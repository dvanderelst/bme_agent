"""
Generate a printable handout sheet of student login slips from the .ods roster.

Reads the same roster as script_configure_students.py (via read_ods_rows, so
the credentials on the handout match exactly what gets synced to the database)
and writes an A4 HTML page: a grid of bordered slips with dashed cut lines, one
per student, each showing the student's name, username, and password. Open the
HTML in a browser and print (or Save as PDF), then cut along the dashed lines
to hand each student their strip.

HTML is used deliberately so the script has no PDF dependency — printing to A4
or PDF is the browser's job.

The output contains plaintext passwords, so it is written into participants26/
(which is gitignored) by default and must never be committed.

Usage:
    python script_make_handouts.py                       # ./students.ods -> participants26/handouts.html
    python script_make_handouts.py roster.ods out.html
    python script_make_handouts.py --all                 # include test accounts (teacher/ttest)
    python script_make_handouts.py --url https://chatbme.example.app
    python script_make_handouts.py --cols 3
"""

import argparse
import html
import os
import sys

from script_configure_students import read_ods_rows, DEFAULT_ROSTER

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(_SCRIPT_DIR, "participants26", "handouts.html")

# Usernames treated as non-student test accounts and skipped unless --all.
TEST_USERNAMES = {"teacher", "ttest"}


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


def build_html(rows, url: str, cols: int) -> str:
    """Render the roster rows into a self-contained printable HTML string."""
    # Page geometry: A4 minus 10mm margins ≈ 190mm wide. Slip height chosen so
    # a 2-column layout yields whole rows that fit the printable page height
    # without splitting a slip across pages (break-inside: avoid backs this up).
    css = f"""
    @page {{ size: A4; margin: 10mm; }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; }}
    .grid {{ display: grid; grid-template-columns: repeat({cols}, 1fr); }}
    .slip {{
        border: 1px dashed #888;
        padding: 7mm 6mm;
        min-height: 42mm;
        break-inside: avoid;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    .name {{ font-size: 15pt; font-weight: 700; margin-bottom: 4mm; }}
    .group {{ font-size: 10pt; font-weight: 400; color: #555; }}
    .cred {{ font-size: 12pt; margin: 1mm 0; }}
    .label {{ display: inline-block; width: 24mm; color: #555; }}
    .val {{ font-family: "Courier New", monospace; font-weight: 700; font-size: 13pt; }}
    .url {{ margin-top: 4mm; font-size: 10pt; color: #333; }}
    @media screen {{ body {{ background: #eee; }} .grid {{ max-width: 190mm; margin: 8mm auto; background: #fff; }} }}
    """

    slips = []
    for r in rows:
        username = (r.get("username") or "").strip().lower()
        password = (r.get("password") or "").strip()
        name = display_name(r.get("full_name", ""), username)
        group = (r.get("group") or "").strip()
        group_html = (
            f' <span class="group">(Group {html.escape(group)})</span>' if group else ""
        )
        url_html = (
            f'<div class="url">{html.escape(url)}</div>' if url else ""
        )
        slips.append(
            f'''  <div class="slip">
    <div class="name">{html.escape(name)}{group_html}</div>
    <div class="cred"><span class="label">Username</span><span class="val">{html.escape(username)}</span></div>
    <div class="cred"><span class="label">Password</span><span class="val">{html.escape(password)}</span></div>
    {url_html}
  </div>'''
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>BmE student login slips</title>
<style>{css}</style>
</head>
<body>
<div class="grid">
{os.linesep.join(slips)}
</div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a printable HTML handout of student login slips."
    )
    parser.add_argument("roster", nargs="?", default=DEFAULT_ROSTER,
                        help=f"Path to the .ods roster (default: {DEFAULT_ROSTER})")
    parser.add_argument("output", nargs="?", default=DEFAULT_OUTPUT,
                        help=f"Output HTML path (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--all", action="store_true",
                        help="Include test accounts (teacher/ttest); they are skipped by default.")
    parser.add_argument("--url", default="",
                        help="Optional app URL printed on every slip.")
    parser.add_argument("--cols", type=int, default=2,
                        help="Number of columns in the grid (default: 2).")
    args = parser.parse_args()

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

    html_text = build_html(rows, args.url, args.cols)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html_text)

    print(f"Wrote {len(rows)} login slip(s) to {args.output}")
    print("Open it in a browser and print to A4 (or Save as PDF), then cut along the dashed lines.")


if __name__ == "__main__":
    main()
