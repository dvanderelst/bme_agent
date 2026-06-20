#!/usr/bin/env python3
"""
End-of-program data export for the BmE study.

Downloads every table in the Postgres database into collected_data/database/
in three parts:

  raw/          Faithful, full-fidelity copy WITH names and password hashes,
                plus the actual attachment image files. This is the master
                copy. It stays inside the TrueCrypt-encrypted folder and is
                NEVER shared.

  anonymized/   Shareable copies for colleagues. Every login/username is
                replaced by a stable pseudonym (S01, S02, ...) so the same
                person carries the same pseudonym ACROSS ALL TABLES (cross-
                table linkage preserved), but no names appear. Password hashes
                dropped; student_settings.full_name dropped (group kept);
                free-text fields scrubbed of known student names; attachment
                image bytes withheld (metadata kept for linkage).

  identity_key/ pseudonym_map.csv — the pseudonym <-> username <-> full_name
                lookup. This is the ONE file that re-links the anonymized data
                to real identities. Per the consent commitment made to
                students it is kept (not destroyed, so deletion-on-request
                stays honourable) but NEVER leaves the encrypted folder unless
                IRB approval is granted.

This is pseudonymization, not anonymization. Read-only against the DB.
Re-runnable: it overwrites collected_data/database/ on each run.
"""

from __future__ import annotations

import base64
import csv
import datetime as dt
import json
import re
import tomllib
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

REPO = Path(__file__).resolve().parent
SECRETS = REPO / "agent" / ".streamlit" / "secrets.toml"
OUT = REPO / "collected_data" / "database"

# Tables to export, in dependency order (attachments references interactions).
TABLES = [
    "students",
    "interactions",
    "feedback",
    "attachments",
    "rubric_responses",
    "rubric_attempts",
    "login_failures",
]

# Columns whose value is a username/login string and must be pseudonymized.
USERNAME_COLUMNS = {
    "students": ["username"],
    "interactions": ["user_id"],
    "feedback": ["user_id"],
    "rubric_responses": ["username"],
    "rubric_attempts": ["username"],
    "login_failures": ["username"],
    "attachments": [],
}

# Free-text columns to scrub for stray name mentions in the anonymized copy.
FREETEXT_COLUMNS = {
    "interactions": ["user_message", "agent_response"],
    "feedback": ["note"],
    "rubric_responses": ["answer_text", "note"],
    "rubric_attempts": ["note"],
}

# Columns dropped entirely from the anonymized copy.
DROP_IN_ANON = {
    "students": ["password_hash", "full_name"],
    "attachments": ["bytes"],  # image bytes withheld; metadata kept for linkage
}

# Surnames that are also common English words — skip in free-text redaction so
# we don't mangle ordinary prose ("a strong signal"). The username/user_id
# columns are still fully pseudonymized; this only affects free-text scrubbing.
COMMON_WORD_NAMES = {"strong", "test", "teacher"}

TEST_ACCOUNTS = {"teacher", "ttest"}


def load_db_url() -> str:
    return tomllib.load(SECRETS.open("rb"))["DATABASE_URL"]


def json_default(o):
    if isinstance(o, (dt.datetime, dt.date)):
        return o.isoformat()
    if isinstance(o, (bytes, bytearray, memoryview)):
        return base64.b64encode(bytes(o)).decode("ascii")
    raise TypeError(f"not serializable: {type(o)}")


def fetch_all(url):
    data = {}
    with psycopg2.connect(url, connect_timeout=20) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for t in TABLES:
                cur.execute(f"SELECT * FROM {t} ORDER BY 1")
                data[t] = [dict(r) for r in cur.fetchall()]
    return data


# --------------------------------------------------------------------------
# Pseudonym map
# --------------------------------------------------------------------------
def build_pseudonym_map(data):
    """Collect every distinct username string across all tables and assign a
    stable pseudonym. Sorted alphabetically for determinism."""
    seen = set()
    for table, cols in USERNAME_COLUMNS.items():
        for row in data.get(table, []):
            for c in cols:
                v = row.get(c)
                if v:
                    seen.add(v)

    roster = {r["username"]: r.get("full_name") for r in data.get("students", [])}

    mapping = {}  # username -> {pseudonym, full_name, account_type}
    for i, username in enumerate(sorted(seen), start=1):
        pseudonym = f"S{i:02d}"
        if username in roster and username not in TEST_ACCOUNTS:
            acct = "student"
        elif username in TEST_ACCOUNTS:
            acct = "test"
        else:
            acct = "unmatched_login_string"
        mapping[username] = {
            "pseudonym": pseudonym,
            "full_name": roster.get(username, ""),
            "account_type": acct,
        }
    return mapping


# --------------------------------------------------------------------------
# Free-text name redaction
# --------------------------------------------------------------------------
def build_name_regex(data):
    """Build a regex matching known student names (first, last, full) for
    free-text scrubbing. Returns (compiled_regex, token_set)."""
    tokens = set()
    full_phrases = set()
    for r in data.get("students", []):
        # Test accounts are not real people; their names ("Test Test",
        # "Teacher Test") are common words that would over-redact prose.
        if (r.get("username") or "").lower() in TEST_ACCOUNTS:
            continue
        full = (r.get("full_name") or "").strip()
        if not full:
            continue
        # Stored as "Last, First".
        if "," in full:
            last, first = (p.strip() for p in full.split(",", 1))
        else:
            parts = full.split()
            first, last = (parts[0], parts[-1]) if len(parts) > 1 else (parts[0], "")
        for part in (first, last):
            if part and part.lower() not in COMMON_WORD_NAMES:
                tokens.add(part.lower())
        # full-name phrases in both orders
        if first and last:
            full_phrases.add(f"{first} {last}".lower())
            full_phrases.add(f"{last}, {first}".lower())
            full_phrases.add(f"{last} {first}".lower())
        # the login handle itself (e.g. "breanna", "benjaminm")
        u = (r.get("username") or "").lower()
        if u and u not in COMMON_WORD_NAMES and u not in TEST_ACCOUNTS:
            tokens.add(u)

    # Longest first so full names win over single tokens.
    alternatives = sorted(full_phrases | tokens, key=len, reverse=True)
    if not alternatives:
        return None, set()
    pattern = r"\b(" + "|".join(re.escape(a) for a in alternatives) + r")\b"
    return re.compile(pattern, re.IGNORECASE), (full_phrases | tokens)


def redact_text(text, regex, counter):
    if not isinstance(text, str) or not text or regex is None:
        return text

    def repl(m):
        counter[m.group(0).lower()] = counter.get(m.group(0).lower(), 0) + 1
        return "[NAME]"

    return regex.sub(repl, text)


def redact_json(value, regex, counter):
    """Recursively redact string values inside answer_json structures."""
    if isinstance(value, str):
        return redact_text(value, regex, counter)
    if isinstance(value, list):
        return [redact_json(v, regex, counter) for v in value]
    if isinstance(value, dict):
        return {k: redact_json(v, regex, counter) for k, v in value.items()}
    return value


# --------------------------------------------------------------------------
# Anonymization
# --------------------------------------------------------------------------
def anonymize(data, pmap, regex, counter):
    out = {}
    for table in TABLES:
        ucols = USERNAME_COLUMNS.get(table, [])
        ftcols = FREETEXT_COLUMNS.get(table, [])
        drop = DROP_IN_ANON.get(table, [])
        rows = []
        for row in data[table]:
            r = dict(row)
            for c in drop:
                r.pop(c, None)
            # pseudonymize usernames
            for c in ucols:
                if r.get(c):
                    r[c] = pmap.get(r[c], {}).get("pseudonym", "S??")
            # scrub student_settings.full_name (keep group/backend/etc.)
            if "student_settings" in r and isinstance(r["student_settings"], dict):
                ss = dict(r["student_settings"])
                ss.pop("full_name", None)
                r["student_settings"] = ss
            # redact free text
            for c in ftcols:
                r[c] = redact_text(r.get(c), regex, counter)
            if table == "rubric_responses" and r.get("answer_json") is not None:
                r["answer_json"] = redact_json(r["answer_json"], regex, counter)
            # scrub student-chosen attachment filenames
            if table == "attachments" and r.get("filename"):
                r["filename"] = redact_text(r["filename"], regex, counter)
            rows.append(r)
        out[table] = rows
    return out


# --------------------------------------------------------------------------
# Writers
# --------------------------------------------------------------------------
def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, default=json_default, ensure_ascii=False, indent=1)


def sanitize_filename(name):
    return re.sub(r"[^\w.\- ]", "_", name or "file")


def write_raw(data, stamp):
    raw = OUT / "raw"
    img_dir = raw / "attachments"
    img_dir.mkdir(parents=True, exist_ok=True)

    # attachments: write image bytes to files, keep metadata (with bytes -> path)
    att_meta = []
    for r in data["attachments"]:
        meta = {k: v for k, v in r.items() if k != "bytes"}
        blob = r.get("bytes")
        if blob:
            fn = f"{r['id']:04d}_{sanitize_filename(r.get('filename'))}"
            (img_dir / fn).write_bytes(bytes(blob))
            meta["file"] = f"attachments/{fn}"
        att_meta.append(meta)

    for t in TABLES:
        if t == "attachments":
            write_json(raw / "attachments.json", att_meta)
        else:
            write_json(raw / f"{t}.json", data[t])

    write_json(raw / "export_manifest.json", {
        "exported_at": stamp,
        "kind": "raw_with_identities",
        "row_counts": {t: len(data[t]) for t in TABLES},
        "attachment_images_written": sum(1 for r in data["attachments"] if r.get("bytes")),
        "warning": "Contains names + password hashes. Keep inside encrypted folder. Do not share.",
    })


def write_anon(anon, pmap, stamp):
    a = OUT / "anonymized"
    for t in TABLES:
        write_json(a / f"{t}.json", anon[t])
    write_json(a / "export_manifest.json", {
        "exported_at": stamp,
        "kind": "anonymized_shareable",
        "row_counts": {t: len(anon[t]) for t in TABLES},
        "pseudonymization": "usernames -> stable pseudonyms, same person same id across all tables",
        "dropped": DROP_IN_ANON,
        "notes": [
            "student_settings.full_name removed; group/backend/enabled retained.",
            "attachment image bytes withheld; metadata kept (interaction_id links to interactions).",
            "free-text fields scrubbed of known student names -> [NAME] (heuristic; spot-check before sharing).",
            f"surnames skipped as common words: {sorted(COMMON_WORD_NAMES)}",
        ],
    })
    # README for colleagues
    (a / "README.md").write_text(
        "# Anonymized BmE study data\n\n"
        "These are pseudonymized copies of the study database. Each participant is\n"
        "identified only by a stable pseudonym (e.g. `S01`) that is the SAME across\n"
        "every table, so you can link a person's chatbot interactions, feedback,\n"
        "rubric responses, etc. — without any names.\n\n"
        "## Tables\n"
        + "".join(f"- `{t}.json`\n" for t in TABLES)
        + "\n## What was removed\n"
        "- Real names / usernames (replaced by pseudonyms).\n"
        "- Password hashes.\n"
        "- `student_settings.full_name` (the `group` A/B assignment is kept).\n"
        "- Uploaded screenshot image bytes (metadata kept; ask the PI if you need images).\n"
        "- Known student names appearing in free text are replaced with `[NAME]`.\n\n"
        "## Linkage key\n"
        "The pseudonym -> name mapping is held only by the PI and is not part of this\n"
        "share. It is released only under IRB approval.\n",
        encoding="utf-8",
    )


def write_identity_key(pmap, stamp, redaction_counter):
    k = OUT / "identity_key"
    k.mkdir(parents=True, exist_ok=True)
    # The redaction report lists matched name tokens (real first names), so it
    # lives with the identity key — never in the shareable anonymized set.
    write_json(k / "redaction_report.json", {
        "exported_at": stamp,
        "description": "Per-token counts of free-text replacements with [NAME]. Review for false positives.",
        "total_replacements": sum(redaction_counter.values()),
        "by_matched_text": dict(sorted(redaction_counter.items(), key=lambda kv: -kv[1])),
    })
    rows = sorted(pmap.items(), key=lambda kv: kv[1]["pseudonym"])
    with (k / "pseudonym_map.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pseudonym", "username", "full_name", "account_type"])
        for username, info in rows:
            w.writerow([info["pseudonym"], username, info["full_name"], info["account_type"]])
    (k / "README.md").write_text(
        "# IDENTITY KEY — DO NOT SHARE\n\n"
        "`pseudonym_map.csv` re-links the anonymized data to real identities.\n\n"
        "Per the data-handling commitment made to students:\n"
        "- This file is KEPT (not destroyed) so a student's deletion-on-request can\n"
        "  still be honoured by finding their pseudonym and removing matching rows.\n"
        "- It is stored ONLY inside the encrypted (TrueCrypt) folder.\n"
        "- It is NEVER shared with colleagues unless/until IRB approval is granted.\n\n"
        f"Generated {stamp}.\n",
        encoding="utf-8",
    )


def main():
    url = load_db_url()
    stamp = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    print(f"[{stamp}] connecting and downloading {len(TABLES)} tables...")
    data = fetch_all(url)
    for t in TABLES:
        print(f"  {t:18s} {len(data[t])} rows")

    pmap = build_pseudonym_map(data)
    print(f"\npseudonyms assigned: {len(pmap)} distinct login strings")

    regex, _ = build_name_regex(data)
    counter = {}
    anon = anonymize(data, pmap, regex, counter)

    write_raw(data, stamp)
    write_anon(anon, pmap, stamp)
    write_identity_key(pmap, stamp, counter)

    print(f"\nfree-text redactions: {sum(counter.values())} replacements")
    print("\nwritten to:")
    print(f"  {OUT/'raw'}/          (master, with names — keep encrypted)")
    print(f"  {OUT/'anonymized'}/   (shareable, pseudonymized)")
    print(f"  {OUT/'identity_key'}/ (pseudonym map — never share unless IRB)")


if __name__ == "__main__":
    main()
