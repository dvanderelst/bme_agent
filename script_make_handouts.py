"""
Generate a printable handout of student login slips from the .ods roster.

Reads the same roster as script_configure_students.py (via read_ods_rows, so
the credentials on the handout match exactly what gets synced to the database)
and writes a LibreOffice Calc (.ods) file: a grid of bordered cells, one slip
per student, each showing the student's name, username, and password. The page
is set up for US Letter — open in LibreOffice and print (or export to PDF),
then cut along the cell borders to hand each student their strip.

.ods is used so the sheet can be tweaked in LibreOffice before printing and so
there is no PDF dependency. odfpy (the `odf` package) is already a dependency
of script_configure_students.py.

The output contains plaintext passwords, so it is written into participants26/
(which is gitignored) by default and must never be committed.

Usage:
    python script_make_handouts.py                       # ./students.ods -> participants26/handouts.ods
    python script_make_handouts.py roster.ods out.ods
    python script_make_handouts.py --all                 # include test accounts (teacher/ttest)
    python script_make_handouts.py --url https://chatbme.example.app
    python script_make_handouts.py --cols 3
"""

import argparse
import os
import sys

from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import (
    Style,
    TextProperties,
    ParagraphProperties,
    TableCellProperties,
    TableColumnProperties,
    TableRowProperties,
    PageLayout,
    PageLayoutProperties,
    MasterPage,
)
from odf.table import Table, TableColumn, TableRow, TableCell
from odf.text import P, Span

from script_configure_students import read_ods_rows, DEFAULT_ROSTER

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(_SCRIPT_DIR, "participants26", "handouts.ods")

# Usernames treated as non-student test accounts and skipped unless --all.
TEST_USERNAMES = {"teacher", "ttest"}

# US Letter, portrait, half-inch margins → 7.5in of printable width.
PAGE_WIDTH = "8.5in"
PAGE_HEIGHT = "11in"
PAGE_MARGIN = "0.5in"
PRINTABLE_WIDTH_IN = 7.5
ROW_HEIGHT = "1.25in"


def display_name(full_name: str, username: str) -> str:
    """Turn a roster name into a friendly 'First Last' for the slip.

    The roster stores names as 'Last, First' (e.g. 'Dexheimer, Stephen'); flip
    those to 'First Last'. Names without a comma (e.g. 'Teacher Test') and empty
    names are left as-is, falling back to the username when there's no name."""
    name = (full_name or "").strip()
    if not name:
        return username
    if "," in name:
        last, first = name.split(",", 1)
        first, last = first.strip(), last.strip()
        if first and last:
            return f"{first} {last}"
    return name


def _build_styles(doc, cols: int):
    """Register page layout and cell/paragraph/text styles; return them."""
    # Page: US Letter portrait with half-inch margins. The master page is named
    # "Standard" (the default a Calc table uses) so the layout takes effect.
    page_layout = PageLayout(name="HandoutPL")
    page_layout.addElement(
        PageLayoutProperties(
            pagewidth=PAGE_WIDTH,
            pageheight=PAGE_HEIGHT,
            printorientation="portrait",
            margintop=PAGE_MARGIN,
            marginbottom=PAGE_MARGIN,
            marginleft=PAGE_MARGIN,
            marginright=PAGE_MARGIN,
        )
    )
    doc.automaticstyles.addElement(page_layout)
    doc.masterstyles.addElement(MasterPage(name="Standard", pagelayoutname="HandoutPL"))

    # One bordered cell = one slip. Border doubles as the cut line.
    slip = Style(name="Slip", family="table-cell")
    slip.addElement(
        TableCellProperties(
            border="0.5pt solid #888888",
            verticalalign="middle",
            wrapoption="wrap",
            paddingtop="0.12in",
            paddingbottom="0.12in",
            paddingleft="0.16in",
            paddingright="0.16in",
        )
    )
    doc.styles.addElement(slip)

    name_p = Style(name="SlipName", family="paragraph")
    name_p.addElement(TextProperties(fontsize="14pt", fontweight="bold"))
    name_p.addElement(ParagraphProperties(marginbottom="0.06in"))
    doc.styles.addElement(name_p)

    cred_p = Style(name="SlipCred", family="paragraph")
    cred_p.addElement(TextProperties(fontsize="11pt"))
    doc.styles.addElement(cred_p)

    url_p = Style(name="SlipUrl", family="paragraph")
    url_p.addElement(TextProperties(fontsize="9pt", color="#555555"))
    url_p.addElement(ParagraphProperties(margintop="0.06in"))
    doc.styles.addElement(url_p)

    # Username/password values: monospace + bold so they're easy to read/type.
    val_t = Style(name="SlipVal", family="text")
    val_t.addElement(
        TextProperties(fontsize="12pt", fontweight="bold", fontfamily="Courier New")
    )
    doc.styles.addElement(val_t)

    # Column width so `cols` slips span the printable width.
    col = Style(name="SlipCol", family="table-column")
    col.addElement(
        TableColumnProperties(columnwidth=f"{PRINTABLE_WIDTH_IN / cols:.3f}in")
    )
    doc.automaticstyles.addElement(col)

    row = Style(name="SlipRow", family="table-row")
    row.addElement(TableRowProperties(rowheight=ROW_HEIGHT))
    doc.automaticstyles.addElement(row)

    return slip, name_p, cred_p, url_p, val_t, col, row


def _slip_cell(slip_style, name_p, cred_p, url_p, val_t, name, username, password, url):
    """Build one bordered table cell holding a single student's slip."""
    cell = TableCell(stylename=slip_style, valuetype="string")

    cell.addElement(P(stylename=name_p, text=name))

    p_user = P(stylename=cred_p)
    p_user.addText("Username:  ")
    p_user.addElement(Span(stylename=val_t, text=username))
    cell.addElement(p_user)

    p_pass = P(stylename=cred_p)
    p_pass.addText("Password:  ")
    p_pass.addElement(Span(stylename=val_t, text=password))
    cell.addElement(p_pass)

    if url:
        cell.addElement(P(stylename=url_p, text=url))

    return cell


def build_ods(rows, url: str, cols: int, output: str) -> None:
    """Write the roster rows to an .ods grid of login slips."""
    doc = OpenDocumentSpreadsheet()
    slip, name_p, cred_p, url_p, val_t, col, row = _build_styles(doc, cols)

    table = Table(name="Login slips")
    for _ in range(cols):
        table.addElement(TableColumn(stylename=col))

    for i in range(0, len(rows), cols):
        chunk = rows[i:i + cols]
        tr = TableRow(stylename=row)
        for r in chunk:
            username = (r.get("username") or "").strip().lower()
            password = (r.get("password") or "").strip()
            name = display_name(r.get("full_name", ""), username)
            group = (r.get("group") or "").strip()
            if group:
                name = f"{name}  (Group {group})"
            tr.addElement(
                _slip_cell(slip, name_p, cred_p, url_p, val_t, name, username, password, url)
            )
        # Pad a short final row with empty cells so the table stays rectangular.
        for _ in range(cols - len(chunk)):
            tr.addElement(TableCell())
        table.addElement(tr)

    doc.spreadsheet.addElement(table)
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    doc.save(output)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a printable .ods handout of student login slips (US Letter)."
    )
    parser.add_argument("roster", nargs="?", default=DEFAULT_ROSTER,
                        help=f"Path to the .ods roster (default: {DEFAULT_ROSTER})")
    parser.add_argument("output", nargs="?", default=DEFAULT_OUTPUT,
                        help=f"Output .ods path (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--all", action="store_true",
                        help="Include test accounts (teacher/ttest); they are skipped by default.")
    parser.add_argument("--url", default="",
                        help="Optional app URL printed on every slip.")
    parser.add_argument("--cols", type=int, default=2,
                        help="Number of slip columns across the page (default: 2).")
    args = parser.parse_args()

    if args.cols < 1:
        sys.exit("--cols must be at least 1.")

    rows = read_ods_rows(args.roster)

    if not args.all:
        rows = [r for r in rows
                if (r.get("username") or "").strip().lower() not in TEST_USERNAMES]

    # Sort by group then display name so slips can be handed out group by group.
    rows.sort(key=lambda r: (
        (r.get("group") or "").strip(),
        display_name(r.get("full_name", ""), (r.get("username") or "")).lower(),
    ))

    if not rows:
        sys.exit("No students to print (did everything get filtered out?).")

    build_ods(rows, args.url, args.cols, args.output)

    print(f"Wrote {len(rows)} login slip(s) to {args.output}")
    print("Open it in LibreOffice and print to US Letter (or export to PDF), "
          "then cut along the cell borders.")


if __name__ == "__main__":
    main()
