#!/usr/bin/env python3
"""Generate tools/kits/core/generated/ from the C++ core and the measured kit rule.

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

Second output, `team_kits.py` (PLAN-KITS-PY.md section 4.2): which TEX each
team wears.  Its source is EDITOR_RULE below -- what Obocaman's
`we-team-editor.exe` computes from its team combobox, read out of the exe's
code by `--editor` -- checked row by row against EMULATOR_ROWS, the teams
measured in VRAM by `oracle.py`.  The exe is not in the repository (no
licence); the rule read from it is.

Usage:
    python tools/kits/gen_tables.py            # write the generated files
    python tools/kits/gen_tables.py --check    # regenerate in memory; exit 1 on a diff
    python tools/kits/gen_tables.py --check --src <dir>   # read the C++ from another tree
    python tools/kits/gen_tables.py --negative   # one TEAM_NAMES row changed in a copy: --check must fail
    python tools/kits/gen_tables.py --report     # the team -> TEX table, counted
    python tools/kits/gen_tables.py --editor [EXE]   # read the rule from the exe; exit 1 if it differs
    python tools/kits/gen_tables.py --negative-editor  # the divisor changed in a copy: --editor must fail
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

KITS_OUTPUT = os.path.join(KITS_DIR, "core", "generated", "team_kits.py")
EDITOR_EXE = os.path.join("we-team-editor", "we-team-editor.exe")

EDITOR_RULE = {"divisor": 95, "skip": 9, "base": 0x12D7718, "stride": 47040}
"""What `we-team-editor.exe` does with the item index of its team combobox
to reach that team's TEX, read out of its code by `--editor` (2026-10-04):

    n = index + skip * (index div divisor)
    TEX number n starts at raw byte base + n * stride

`base` is TEX_00's first data byte (LBA 8400, plus the 24-byte sector
header) and `stride` is 20 sectors of 2352 bytes, so TEX number n is the
n-th of the 105 in disc order: 00..99, then A0..A4.  The combobox lists the
95 teams and then a 96th item, "95 Master L." / "95 Default ML", which the
rule sends to n = 104, TEX_A4."""

RULE_CODE = re.compile(
    rb"\xb9(.{4})\x99\xf7\xf9"                 # mov ecx, divisor; cdq; idiv ecx
    rb"\x8d\x04\xc0\x03[\xf8\xd8]"            # lea eax, [eax+eax*8]; add index, eax
    rb"\x8d\x04[\x7f\x5b]\xc1\xe0(.)\x2b[\xc7\xc3]"  # lea eax, [n+n*2]; shl; sub n
    rb"\xc1\xe0(.)\x2b[\xc7\xc3]\xc1\xe0(.)"    # shl; sub n; shl
    rb"\x05(.{4})", re.S)                        # add eax, base
"""The instructions of the rule, with the numbers left as groups.  The
multiplier of the quotient is the `lea [eax+eax*8]`, 9, fixed by the bytes."""

EMULATOR_ROWS = (
    (0, "00", "Ireland, home, set 1: oracle.py --slot 4 --expect 00=1 --expect 41=1 "
              "(work/kits-states/SLPM-87056_4.sav, sha256 40bcf3d6...)"),
    (1, "01", "Scotland, home, set 1: oracle.py --slot 3 --expect 01=1 --expect 13=2 "
              "(work/kits-states/SLPM-87056_3.sav, sha256 5f392a12...)"),
    (13, "13", "Denmark, away, set 2: oracle.py --slot 3 --expect 01=1 --expect 13=2 "
               "(work/kits-states/SLPM-87056_3.sav, sha256 5f392a12...)"),
    (41, "41", "Brazil, away, set 1: oracle.py --slot 4 --expect 00=1 --expect 41=1 "
               "(work/kits-states/SLPM-87056_4.sav, sha256 40bcf3d6...)"),
)
"""(team index, tag, how it was measured): the rows the game itself confirmed,
by the flag and the exact player palette it uploaded to VRAM (section 4.1)."""
KIT_COUNT = 105
SKIP = 77


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


def kit_tag(n: int) -> str:
    """The tag of the n-th TEX in disc order: 00..99, then A0..A4."""
    if not 0 <= n < KIT_COUNT:
        raise GenError("TEX number %d is outside the %d on the disc" % (n, KIT_COUNT))
    return "%02d" % n if n < 100 else "A%d" % (n - 100)


def kit_number(index: int, rule: dict = EDITOR_RULE) -> int:
    return index + rule["skip"] * (index // rule["divisor"])


def read_editor_rule(data: bytes) -> dict:
    """EDITOR_RULE as the exe's code says it; GenError when the code is not
    there or its sites disagree."""
    import struct

    found = []
    for m in RULE_CODE.finditer(data):
        divisor, = struct.unpack("<i", m.group(1))
        a, b, c = (ord(m.group(i)) for i in (2, 3, 4))
        base, = struct.unpack("<I", m.group(5))
        found.append((m.start(), {"divisor": divisor, "skip": 9, "base": base,
                                  "stride": ((3 << a) - 1 << b) - 1 << c}))
    if not found:
        raise GenError("the rule's instructions are not in the exe")
    rules = {tuple(sorted(r.items())) for _, r in found}
    if len(rules) != 1:
        raise GenError("the %d sites of the rule disagree: %s"
                       % (len(found), ", ".join("0x%x %s" % (at, r) for at, r in found)))
    return dict(found[0][1], sites=tuple(at for at, _ in found))


def render_kits(src: str = REPO_DIR) -> str:
    counts = read_counts(src)
    teams = counts["TEAMS_NATIONAL"] + counts["TEAMS_ALLSTAR"] + counts["TEAMS_ML"]
    tags = tuple(kit_tag(kit_number(i)) for i in range(teams))
    ml_default = kit_tag(kit_number(teams))
    for index, tag, how in EMULATOR_ROWS:
        if tags[index] != tag:
            raise GenError("the rule gives team %d TEX_%s, and the game wore TEX_%s (%s)"
                           % (index, tags[index], tag, how))
    used = set(tags) | {ml_default}
    unreached = tuple(kit_tag(n) for n in range(KIT_COUNT) if kit_tag(n) not in used)
    lines = [
        '"""Which TEX each team wears, by team index (PLAN-KITS-PY.md section 4.2).',
        "",
        "GENERATED by tools/kits/gen_tables.py from its EDITOR_RULE and EMULATOR_ROWS.",
        "Do not edit by hand: change the generator and rerun.",
        "",
        "Every row comes from the rule of Obocaman's we-team-editor.exe (index + %d * (index"
        % EDITOR_RULE["skip"],
        "div %d) is the TEX number in disc order), read out of the exe by `gen_tables.py"
        % EDITOR_RULE["divisor"],
        "--editor`; the rows in TEAM_KIT_EMULATOR were also measured in the game's VRAM.",
        '"""',
        "",
        "# -- the TEX of team 0..%d, in the order of TEAM_NAMES --" % (teams - 1),
        "",
        "TEAM_KIT = %s" % _tuple(tags),
        "",
        "# -- the editor's item after the teams (\"95 Master L.\" / \"95 Default ML\") --",
        "",
        "ML_DEFAULT_KIT = %r" % ml_default,
        "",
        "# -- tags no team and no item of the editor reaches --",
        "",
        "UNREACHED_KITS = %s" % _tuple(unreached),
        "",
        "# -- the rows the game confirmed: team index -> how it was measured --",
        "",
        "TEAM_KIT_EMULATOR = {",
    ]
    lines += ["    %d: %r," % (index, how) for index, _, how in EMULATOR_ROWS]
    lines.append("}")
    return "\n".join(lines) + "\n"


OUTPUTS = ((OUTPUT, render), (KITS_OUTPUT, render_kits))


def report(src: str = REPO_DIR) -> int:
    """`--report`: how much of the team -> TEX table there is, counted."""
    import importlib.util

    spec = importlib.util.spec_from_loader("team_kits", loader=None)
    table = importlib.util.module_from_spec(spec)
    exec(render_kits(src), table.__dict__)
    print("team_kits: %d teams with a TEX, from the editor's rule; %d of them confirmed "
          "in the game (%s); the editor's ML default item -> TEX_%s; %d tags no item "
          "reaches (%s)"
          % (len(table.TEAM_KIT), len(table.TEAM_KIT_EMULATOR),
             ", ".join("%d -> TEX_%s" % (i, table.TEAM_KIT[i])
                       for i in sorted(table.TEAM_KIT_EMULATOR)),
             table.ML_DEFAULT_KIT, len(table.UNREACHED_KITS),
             " ".join(table.UNREACHED_KITS)))
    return 0


def editor(path: str) -> int:
    """`--editor`: the rule read from the exe has to be EDITOR_RULE."""
    if not os.path.isfile(path):
        print("gen_tables --editor: skipped -- no exe at %s (it is not in git)" % path)
        return SKIP
    with open(path, "rb") as fh:
        data = fh.read()
    try:
        rule = read_editor_rule(data)
    except GenError as exc:
        print("gen_tables --editor: %s" % exc)
        return 1
    sites = rule.pop("sites")
    print("gen_tables --editor: %d site(s) at %s give %s"
          % (len(sites), ", ".join("0x%x" % at for at in sites), rule))
    if rule != EDITOR_RULE:
        print("gen_tables --editor: FAIL -- EDITOR_RULE says %s" % EDITOR_RULE)
        return 1
    print("gen_tables --editor: the exe computes EDITOR_RULE")
    return 0


def negative_editor(path: str) -> int:
    """A copy of the exe with the divisor of every site changed by one:
    `--editor` on it has to fail."""
    import shutil
    import tempfile

    if not os.path.isfile(path):
        print("gen_tables --negative-editor: skipped -- no exe at %s" % path)
        return SKIP
    with tempfile.TemporaryDirectory(prefix="kits-gen-") as tmp:
        copy = os.path.join(tmp, "editor.exe")
        shutil.copyfile(path, copy)
        with open(copy, "rb") as fh:
            data = bytearray(fh.read())
        sites = [m.start() for m in RULE_CODE.finditer(bytes(data))]
        for at in sites:
            data[at + 1] += 1
        with open(copy, "wb") as fh:
            fh.write(bytes(data))
        print("control: divisor + 1 at %d site(s) of a copy" % len(sites))
        code = editor(copy)
    held = code == 1 and bool(sites)
    print("control: --editor <copy> exit %d -- %s" % (code, "red, held" if held else "FAILED"))
    return 0 if held else 1


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
    """0 when every committed file is what *src* generates, 1 (with the diff)
    otherwise."""
    bad = 0
    for output, make in OUTPUTS:
        try:
            text = make(src)
        except (GenError, OSError) as exc:
            print("gen_tables: %s" % exc, file=sys.stderr)
            return 1
        try:
            with open(output, encoding="utf-8") as fh:
                have = fh.read()
        except OSError as exc:
            print("gen_tables: %s cannot be read: %s" % (output, exc), file=sys.stderr)
            return 1
        if have == text:
            print("gen_tables: %s is up to date" % os.path.relpath(output, REPO_DIR))
            continue
        bad = 1
        diff = difflib.unified_diff(have.splitlines(), text.splitlines(),
                                    "committed", "regenerated", lineterm="", n=1)
        print("gen_tables: %s is stale -- rerun python tools/kits/gen_tables.py"
              % os.path.relpath(output, REPO_DIR))
        for line in list(diff)[:20]:
            print("  " + line)
    return bad


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="regenerate in memory and compare with the committed file")
    parser.add_argument("--negative", action="store_true",
                        help="change one TEAM_NAMES row in a copy of the C++ and require a diff")
    parser.add_argument("--src", default=REPO_DIR,
                        help="the tree to read the C++ from (default: this repository)")
    parser.add_argument("--editor", nargs="?", const=EDITOR_EXE, metavar="EXE",
                        help="read the kit rule out of we-team-editor.exe and compare "
                             "it with EDITOR_RULE")
    parser.add_argument("--negative-editor", nargs="?", const=EDITOR_EXE, metavar="EXE",
                        help="change the divisor in a copy of the exe: --editor must fail")
    parser.add_argument("--report", action="store_true",
                        help="count the team -> TEX table: rows, confirmed rows, unreached tags")
    args = parser.parse_args(argv)
    if args.report:
        return report(args.src)
    if args.editor:
        return editor(args.editor)
    if args.negative_editor:
        return negative_editor(args.negative_editor)
    if args.negative:
        return negative()
    if args.check:
        return check(args.src)
    for output, make in OUTPUTS:
        try:
            text = make(args.src)
        except (GenError, OSError) as exc:
            print("gen_tables: %s" % exc, file=sys.stderr)
            return 1
        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("gen_tables: wrote %s" % os.path.relpath(output, REPO_DIR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
