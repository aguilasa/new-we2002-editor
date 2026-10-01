#!/usr/bin/env python3
"""Generate tools/kits/core/generated/team_names.py from the C++ core.

PLAN-KITS-PY.md section 3.3: the Python core does not retype the team-name
reader of `we2002_core`.  The offsets of the name batches, the length of
each name in each batch, the team counts and the English `TEAM_NAMES`
table come from the C++ sources by this generator, and `--check` fails when
the C++ changed and the generated file did not.

Sources (read, never written):

    src/core/include/we2002/Offsets.hpp   OFS_TEAM_NAME_*, OFS_TEAM_MIXED_CASE_NAME,
                                          OFS_ML_TEAM_NAME_*
    src/core/include/we2002/Types.hpp     TEAMS_NATIONAL, TEAMS_ALLSTAR, TEAMS_ML
    src/core/Tables.cpp                   TEAM_NAME_LEN_1..6, TEAM_NAME_KANJI_LEN,
                                          TEAM_MIXED_CASE_NAME_LEN, ML_TEAM_NAME_LEN_7/8,
                                          TEAM_NAMES

Those two C++ files are themselves generated from `legacy/mfc/edDlg.cpp` by
`tools/extract_legacy_data.py`; this one reads the C++ the port compiles,
so the Python and the C++ cannot drift apart.

Usage:
    python tools/kits/gen_tables.py            # write the generated file
    python tools/kits/gen_tables.py --check    # regenerate in memory; exit 1 on a diff
    python tools/kits/gen_tables.py --check --src <dir>   # read the C++ from another tree
    python tools/kits/gen_tables.py --negative   # one TEAM_NAMES row changed in a copy: --check must fail
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import sys

KITS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(os.path.dirname(KITS_DIR))
OUTPUT = os.path.join(KITS_DIR, "core", "generated", "team_names.py")

OFFSETS = "src/core/include/we2002/Offsets.hpp"
TYPES = "src/core/include/we2002/Types.hpp"
TABLES = "src/core/Tables.cpp"

OFFSET_NAMES = re.compile(r"^(OFS_TEAM_NAME\w*|OFS_TEAM_MIXED_CASE_NAME|OFS_ML_TEAM_NAME\w*)$")
COUNT_NAMES = ("TEAMS_NATIONAL", "TEAMS_ALLSTAR", "TEAMS_ML")
LENGTH_TABLES = ("TEAM_NAME_LEN_1", "TEAM_NAME_LEN_2", "TEAM_NAME_LEN_3", "TEAM_NAME_LEN_4",
                 "TEAM_NAME_LEN_5", "TEAM_NAME_LEN_6", "TEAM_NAME_KANJI_LEN",
                 "TEAM_MIXED_CASE_NAME_LEN", "ML_TEAM_NAME_LEN_7", "ML_TEAM_NAME_LEN_8")
NAME_TABLE = "TEAM_NAMES"


class GenError(Exception):
    """A source does not say what the generator expects; the message says what."""


def _read(src: str, rel: str) -> str:
    with open(os.path.join(src, rel), encoding="latin-1") as fh:
        return fh.read()


def _strip_comments(text: str) -> str:
    """Drop // and /* */ comments outside string literals."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i = j + 1
        elif text.startswith("//", i):
            i = text.find("\n", i)
            i = n if i < 0 else i
        elif text.startswith("/*", i):
            i = text.find("*/", i) + 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def read_offsets(src: str) -> dict:
    out = {}
    for m in re.finditer(r"inline constexpr Offset (\w+)\s*=\s*(\d+);", _read(src, OFFSETS)):
        if OFFSET_NAMES.match(m.group(1)):
            out[m.group(1)] = int(m.group(2))
    if "OFS_TEAM_NAME_1" not in out:
        raise GenError("%s: no OFS_TEAM_NAME_1" % OFFSETS)
    return out


def read_counts(src: str) -> dict:
    text = _read(src, TYPES)
    out = {}
    for name in COUNT_NAMES:
        m = re.search(r"inline constexpr int %s\s*=\s*(\d+);" % name, text)
        if not m:
            raise GenError("%s: no %s" % (TYPES, name))
        out[name] = int(m.group(1))
    return out


def _array_body(text: str, name: str) -> tuple:
    m = re.search(r"const char %s((?:\[\w+\])+)\s*=\s*\{(.*?)\};" % name, text, re.S)
    if not m:
        raise GenError("%s: no array %s" % (TABLES, name))
    dims = [int(d) for d in re.findall(r"\[(\d+)\]", m.group(1))]
    return dims, m.group(2)


def read_lengths(text: str, name: str) -> tuple:
    dims, body = _array_body(text, name)
    values = tuple(int(v) for v in re.findall(r"-?\d+", body))
    if len(values) != dims[0]:
        raise GenError("%s: %s[%d] holds %d values" % (TABLES, name, dims[0], len(values)))
    return values


def read_names(text: str) -> tuple:
    dims, body = _array_body(text, NAME_TABLE)
    names = tuple(bytes(s, "latin-1").decode("unicode_escape").encode("latin-1").decode("latin-1")
                  for s in re.findall(r'"((?:[^"\\]|\\.)*)"', body))
    if len(names) != dims[0]:
        raise GenError("%s: %s[%d] holds %d strings" % (TABLES, NAME_TABLE, dims[0], len(names)))
    long = [n for n in names if len(n) >= dims[1]]
    if long:
        raise GenError("%s: %s entries do not fit %d bytes: %s" % (TABLES, NAME_TABLE, dims[1], long))
    return names


def _tuple(values, per_line: int = 16) -> str:
    rows = [", ".join(repr(v) for v in values[i:i + per_line])
            for i in range(0, len(values), per_line)]
    return "(\n" + "".join("    %s,\n" % r for r in rows) + ")"


def render(src: str = REPO_DIR) -> str:
    tables = _strip_comments(_read(src, TABLES))
    offsets = read_offsets(src)
    counts = read_counts(src)
    lengths = {name: read_lengths(tables, name) for name in LENGTH_TABLES}
    names = read_names(tables)
    lines = [
        '"""Team-name constants of the C++ core, for the kits core.',
        "",
        "GENERATED by tools/kits/gen_tables.py from %s, %s and %s." % (OFFSETS, TYPES, TABLES),
        "Do not edit by hand: change the C++ (or its own generator) and rerun.",
        '"""',
        "",
        "# -- the team counts and the index ranges of TEAM_NAMES (ed.exe's team combobox:",
        "#    nations 0..53, all-stars 54..62, Master League clubs 63..94) --",
        "",
    ]
    for name in COUNT_NAMES:
        lines.append("%s = %d" % (name, counts[name]))
    lines += ["", "# -- offsets into the raw MODE2/2352 image (not ISO file offsets) --", ""]
    for name in sorted(offsets, key=lambda k: (offsets[k], k)):
        lines.append("%s = %d" % (name, offsets[name]))
    lines += ["", "# -- byte length of each team's name in each batch, by team index --", ""]
    for name in LENGTH_TABLES:
        lines.append("%s = %s" % (name, _tuple(lengths[name])))
        lines.append("")
    lines.append("# -- the English names the original editor shows, by team index (%d rows;" % len(names))
    lines.append("#    rows %d.. are names no team of the combobox uses) --"
                 % (counts["TEAMS_NATIONAL"] + counts["TEAMS_ALLSTAR"] + counts["TEAMS_ML"]))
    lines.append("")
    lines.append("%s = %s" % (NAME_TABLE, _tuple(names, per_line=4)))
    return "\n".join(lines) + "\n"


NEGATIVE_INDEX = 1
"""The TEAM_NAMES row --negative changes in its copy ("Scotland")."""


def negative() -> int:
    """Copy the three C++ sources into a temporary tree, change one name of
    TEAM_NAMES (and nothing else), and require the check to see it."""
    import shutil
    import tempfile

    with tempfile.TemporaryDirectory(prefix="kits-gen-") as tmp:
        for rel in (OFFSETS, TYPES, TABLES):
            os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
            shutil.copyfile(os.path.join(REPO_DIR, rel), os.path.join(tmp, rel))
        path = os.path.join(tmp, TABLES)
        with open(path, encoding="latin-1") as fh:
            text = fh.read()
        start = text.index("const char %s[" % NAME_TABLE)
        body = text.index("{", start)
        old = render(REPO_DIR)  # the clean output, for the before/after line
        name = read_names(_strip_comments(text))[NEGATIVE_INDEX]
        at = text.index('"%s"' % name, body)
        text = text[:at] + '"%s"' % (name + "X") + text[at + len(name) + 2:]
        with open(path, "w", encoding="latin-1", newline="") as fh:
            fh.write(text)
        new = render(tmp)
        changed = [(a, b) for a, b in zip(old.splitlines(), new.splitlines()) if a != b]
        print("control: %s row %d %r -> %r in a copy of %s"
              % (NAME_TABLE, NEGATIVE_INDEX, name, name + "X", TABLES))
        code = check(tmp)
        held = code != 0 and len(changed) == 1
        print("control: --check --src <copy> exit %d, %d generated line(s) differ -- %s"
              % (code, len(changed), "red, held" if held else "FAILED"))
        return 0 if held else 1


def check(src: str) -> int:
    """0 when the committed file is what *src*'s C++ generates, 1 (with the
    diff) otherwise."""
    try:
        text = render(src)
    except (GenError, OSError) as exc:
        print("gen_tables: %s" % exc, file=sys.stderr)
        return 1
    try:
        with open(OUTPUT, encoding="utf-8") as fh:
            have = fh.read()
    except OSError as exc:
        print("gen_tables: %s cannot be read: %s" % (OUTPUT, exc), file=sys.stderr)
        return 1
    if have == text:
        print("gen_tables: %s is up to date" % os.path.relpath(OUTPUT, REPO_DIR))
        return 0
    diff = difflib.unified_diff(have.splitlines(), text.splitlines(),
                                "committed", "regenerated", lineterm="", n=1)
    print("gen_tables: %s is stale -- rerun python tools/kits/gen_tables.py"
          % os.path.relpath(OUTPUT, REPO_DIR))
    for line in list(diff)[:20]:
        print("  " + line)
    return 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="regenerate in memory and compare with the committed file")
    parser.add_argument("--negative", action="store_true",
                        help="change one TEAM_NAMES row in a copy of the C++ and require a diff")
    parser.add_argument("--src", default=REPO_DIR,
                        help="the tree to read the C++ from (default: this repository)")
    args = parser.parse_args(argv)
    if args.negative:
        return negative()
    if args.check:
        return check(args.src)
    try:
        text = render(args.src)
    except (GenError, OSError) as exc:
        print("gen_tables: %s" % exc, file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("gen_tables: wrote %s" % os.path.relpath(OUTPUT, REPO_DIR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
