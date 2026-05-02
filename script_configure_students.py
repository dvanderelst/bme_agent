"""
Sync the students table on the Railway Postgres database from a local
LibreOffice/OpenOffice Calc (.ods) roster.

The ODS file is the source of truth. The first row holds column headers
matching the desired table schema; each subsequent row is one student.

Required headers: username, password
Any additional headers (e.g. full_name, challenge, cohort, ...) become
TEXT columns on the students table. Columns present in the table but
absent from the spreadsheet are dropped (except the reserved system
columns: username, password_hash, created_at).

Passwords in the spreadsheet are plaintext — the script bcrypt-hashes
them on insert.

Usage:
    python script_configure_students.py                   # syncs ./students.ods
    python script_configure_students.py sync other.ods
    python script_configure_students.py list
"""

import argparse
import os
import sys
from typing import Any, Dict, List

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values

from odf.opendocument import load as load_ods
from odf.table import Table, TableRow, TableCell
from odf.text import P

from shared_lib.auth import ensure_students_table, hash_password
from shared_lib.config_manager import config


RESERVED_COLUMNS = {"username", "password_hash", "enabled", "backend", "created_at"}

TRUE_VALUES = {"true", "yes", "1", "y", "t"}
FALSE_VALUES = {"false", "no", "0", "n", "f"}
VALID_BACKENDS = {"mistral", "anthropic"}


def parse_enabled(value: str, username: str) -> bool:
    """Convert a spreadsheet 'enabled' cell to a boolean. Empty → True."""
    v = (value or "").strip().lower()
    if v == "":
        return True
    if v in TRUE_VALUES:
        return True
    if v in FALSE_VALUES:
        return False
    sys.exit(
        f"Invalid 'enabled' value for {username}: {value!r}. "
        f"Use one of: {sorted(TRUE_VALUES | FALSE_VALUES)} (or leave blank for true)."
    )


def parse_backend(value: str, username: str) -> str:
    """Validate a 'backend' cell. Must be one of VALID_BACKENDS (non-empty)."""
    v = (value or "").strip().lower()
    if v == "":
        sys.exit(
            f"Empty 'backend' for {username}. "
            f"Set it to one of: {sorted(VALID_BACKENDS)}."
        )
    if v in VALID_BACKENDS:
        return v
    sys.exit(
        f"Invalid 'backend' value for {username}: {value!r}. "
        f"Use one of: {sorted(VALID_BACKENDS)}."
    )

# Default roster lives next to this script so PyCharm's run config works
# regardless of the configured working directory.
DEFAULT_ROSTER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.ods")


def get_database_url() -> str:
    url = config.get("database_url")
    if not url:
        sys.exit("DATABASE_URL not found in .streamlit/secrets.toml or environment.")
    return url


def _cell_text(cell: TableCell) -> str:
    """Concatenate all <text:p> children of a cell into a single string."""
    parts = []
    for p in cell.getElementsByType(P):
        parts.append("".join(node.data for node in p.childNodes if hasattr(node, "data")))
    return "\n".join(parts)


def read_ods_rows(path: str) -> List[Dict[str, str]]:
    """
    Read the first sheet of an .ods file into a list of {header: value} dicts.

    Empty trailing cells (which ODS encodes as repeated empty cells) are
    trimmed. Empty rows are skipped.
    """
    doc = load_ods(path)
    tables = doc.spreadsheet.getElementsByType(Table)
    if not tables:
        sys.exit(f"No sheets found in {path}")
    sheet = tables[0]

    parsed_rows: List[List[str]] = []
    for tr in sheet.getElementsByType(TableRow):
        cells: List[str] = []
        for tc in tr.getElementsByType(TableCell):
            value = _cell_text(tc)
            repeat = int(tc.getAttribute("numbercolumnsrepeated") or 1)
            cells.extend([value] * repeat)
        # Trim trailing blanks
        while cells and cells[-1] == "":
            cells.pop()
        parsed_rows.append(cells)

    # Drop fully empty rows
    parsed_rows = [r for r in parsed_rows if any(c.strip() for c in r)]

    if not parsed_rows:
        sys.exit(f"{path} is empty")

    headers = [h.strip() for h in parsed_rows[0]]
    if not all(headers):
        sys.exit("Header row contains an empty cell")

    rows: List[Dict[str, str]] = []
    for raw in parsed_rows[1:]:
        # Pad short rows with empty strings so zip works
        padded = raw + [""] * (len(headers) - len(raw))
        rows.append({h: padded[i].strip() for i, h in enumerate(headers)})
    return rows


def get_existing_columns(cur) -> List[str]:
    cur.execute(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'students'
        ORDER BY ordinal_position
        """
    )
    return [r[0] for r in cur.fetchall()]


def _quote_ident(name: str) -> str:
    """Validate and quote a SQL identifier. Rejects anything that isn't
    a plain alphanumeric/underscore name to keep DDL safe."""
    if not name or not all(c.isalnum() or c == "_" for c in name) or name[0].isdigit():
        sys.exit(f"Invalid column name: {name!r}")
    return f'"{name}"'


def cmd_sync(args, database_url: str) -> None:
    rows = read_ods_rows(args.path)
    headers = list(rows[0].keys()) if rows else []

    for required in ("username", "password", "enabled", "backend"):
        if required not in headers:
            sys.exit(f"Spreadsheet must have a '{required}' column")
    if "password_hash" in headers:
        sys.exit("'password_hash' is reserved — use a 'password' column instead")
    if "created_at" in headers:
        sys.exit("'created_at' is reserved (auto-managed by the database)")

    # Columns that should exist in the table beyond the reserved ones.
    desired_extras = [
        h for h in headers if h not in ("username", "password", "enabled", "backend")
    ]

    # Validate rows and parse special-column values before touching the DB.
    seen = set()
    enabled_flags: List[bool] = []
    backend_values: List[Any] = []
    for r in rows:
        u = r["username"].strip().lower()
        if not u:
            sys.exit("Found a row with an empty username")
        if u in seen:
            sys.exit(f"Duplicate username in spreadsheet: {u}")
        if not r["password"]:
            sys.exit(f"Empty password for {u}")
        seen.add(u)
        enabled_flags.append(parse_enabled(r["enabled"], u))
        backend_values.append(parse_backend(r["backend"], u))

    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            existing = get_existing_columns(cur)
            existing_extras = [c for c in existing if c not in RESERVED_COLUMNS]

            to_add = [h for h in desired_extras if h not in existing_extras]
            to_drop = [c for c in existing_extras if c not in desired_extras]

            for col in to_add:
                cur.execute(
                    f"ALTER TABLE students ADD COLUMN {_quote_ident(col)} TEXT"
                )
            for col in to_drop:
                cur.execute(
                    f"ALTER TABLE students DROP COLUMN {_quote_ident(col)}"
                )

            cur.execute("TRUNCATE TABLE students")

            insert_cols = ["username", "password_hash", "enabled", "backend"] + desired_extras
            col_sql = ", ".join(_quote_ident(c) for c in insert_cols)
            values = [
                (
                    r["username"].strip().lower(),
                    hash_password(r["password"]),
                    enabled_flags[i],
                    backend_values[i],
                    *(r[c] or None for c in desired_extras),
                )
                for i, r in enumerate(rows)
            ]
            execute_values(
                cur,
                f"INSERT INTO students ({col_sql}) VALUES %s",
                values,
            )

    print(f"Synced {len(rows)} student(s) from {args.path}.")
    if to_add:
        print(f"  Added columns: {', '.join(to_add)}")
    if to_drop:
        print(f"  Dropped columns: {', '.join(to_drop)}")


def cmd_list(args, database_url: str) -> None:
    with psycopg2.connect(database_url) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            columns = [c for c in get_existing_columns(cur) if c != "password_hash"]
            cur.execute(
                f"SELECT {', '.join(_quote_ident(c) for c in columns)} "
                "FROM students ORDER BY username"
            )
            rows = cur.fetchall()

    if not rows:
        print("No students registered.")
        return

    widths = {c: max(len(c), max(len(str(r.get(c) or "")) for r in rows)) for c in columns}
    header = "  ".join(c.ljust(widths[c]) for c in columns)
    print(header)
    print("-" * len(header))
    for r in rows:
        print("  ".join(str(r.get(c) or "").ljust(widths[c]) for c in columns))


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync the students table from a .ods roster.")
    sub = parser.add_subparsers(dest="cmd")

    p_sync = sub.add_parser("sync", help="Replace the students table with the contents of an .ods file")
    p_sync.add_argument("path", nargs="?", default=DEFAULT_ROSTER,
                        help=f"Path to the .ods roster (default: {DEFAULT_ROSTER})")
    p_sync.set_defaults(func=cmd_sync)

    p_list = sub.add_parser("list", help="List currently registered students")
    p_list.set_defaults(func=cmd_list)

    # No subcommand → default to `sync` against the bundled roster so the
    # script can be run from PyCharm with no arguments.
    args = parser.parse_args()
    if args.cmd is None:
        args = parser.parse_args(["sync"])

    database_url = get_database_url()
    ensure_students_table(database_url)
    args.func(args, database_url)


if __name__ == "__main__":
    main()
