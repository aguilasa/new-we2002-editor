#!/usr/bin/env python3
"""The negative controls of duckmcp's design rules, planted by command.

A rule that has never been seen red is decoration. Each control here is ONE
literal substitution in one file of this package: the engine copies
`tools/duckmcp/` into a sandbox (`<tmp>/tools/duckmcp/`), substitutes, runs
the sandbox `selftest.py --quiet`, and demands two things -- a non-zero exit,
and a `FAIL` line carrying the text of the assertion the control claims to
cover. Red through another assertion does not count.

A substitution whose old text matches zero times or more than once is a
BROKEN control, not a red one: a literal that does not match leaves the copy
intact, and the run would come out green for the wrong reason. Before any
control the untouched sandbox must come out green, or no red means anything.

The rules are those of PLAN-DUCKMCP-PY.md section 3.3: (a) nothing outside
the stdlib on import, (c) nothing of a game inside the package, (d) only
`env.py` reads the environment. Rule (b) closes in phase 4.

The last line says how many controls ran, how many went red as required,
and the count per rule; the exit is 0 only when every one did.

Usage:
    python3 tools/duckmcp/controls.py [--list] [--only ID]
"""

import argparse
import collections
import os
import shutil
import subprocess
import sys
import tempfile

DUCKMCP_DIR = os.path.dirname(os.path.abspath(__file__))

ANCHOR = "\nSKIP = 77\n"
"""The line of `errors.py` most controls plant next to."""

Control = collections.namedtuple(
    "Control", "id rule file old new expect extra why")
Control.__doc__ = """One planted defect and the FAIL text it must cause.

`extra` is `(path under the sandbox tools/, content)` or None: a file the
control needs beside the package, never a substitution.
"""

CONTROLS = (
    Control(
        "a-import-pil", "a", "errors.py", ANCHOR,
        "\nimport PIL  # noqa: F401\nSKIP = 77\n",
        "FAIL  rule (a) static: errors.py imports only the stdlib", None,
        "the import the rule names first; the static half sees it whether "
        "or not PIL is installed"),
    Control(
        "a-hidden-import", "a", "errors.py", ANCHOR,
        "\n__import__(\"dmcp_probe_dep\")\nSKIP = 77\n",
        "FAIL  rule (a) loaded: import duckmcp.errors loads only the stdlib",
        ("dmcp_probe_dep.py", "\"\"\"A non-stdlib module planted.\"\"\"\n"),
        "an import no `import` statement shows: only the fresh interpreter "
        "that diffs sys.modules sees it"),
    Control(
        "c-serial-in-comment", "c", "errors.py", ANCHOR,
        "\n# measured on SLES-03957\nSKIP = 77\n",
        "FAIL  rule (c): errors.py holds no game serial", None,
        "a serial in a comment that is not lineage"),
    Control(
        "c-address-outside", "c", "errors.py", ANCHOR,
        "\nBASE = 0x12345678\nSKIP = 77\n",
        "FAIL  rule (c): errors.py has no address outside the hardware "
        "ranges", None,
        "a literal in no PS1 hardware range: a game's address, not the "
        "console's"),
    Control(
        "c-sixth-legacy-name", "c", "env.py",
        '    "DUCKSTATION_DISPLAY": "PES2_DISPLAY",\n',
        '    "DUCKSTATION_DISPLAY": "PES2_DISPLAY",\n'
        '    "DUCKSTATION_SERIAL": "PES2_SERIAL",\n',
        "FAIL  rule (c): env.py names no project outside a lineage comment",
        None,
        "the allow-list is exactly five names: a sixth PES2_ in env.py fails"),
    Control(
        "c-legacy-name-elsewhere", "c", "errors.py", ANCHOR,
        "\nPORT_VAR = \"PES2_MCP_PORT\"\nSKIP = 77\n",
        "FAIL  rule (c): errors.py names no project outside a lineage "
        "comment", None,
        "an allow-listed name outside env.py: the allow-list is env.py's "
        "only"),
    Control(
        "c-project-in-comment", "c", "errors.py", ANCHOR,
        "\n# as tools/pes2/fork.py did it\nSKIP = 77\n",
        "FAIL  rule (c): errors.py names no project outside a lineage "
        "comment", None,
        "a project name in a comment not opened by `# lineage:`"),
    Control(
        "c-code-before-lineage", "c", "errors.py", ANCHOR,
        "\nWHO = \"looks\"  # lineage: a trailing lineage comment\nSKIP = 77\n",
        "FAIL  rule (c): errors.py names no project outside a lineage "
        "comment", None,
        "a trailing `# lineage:` exempts the comment, not the code before it"),
    Control(
        "d-os-environ", "d", "errors.py", ANCHOR,
        "\nimport os\nSKIP = int(os.environ.get(\"SKIP\", \"77\"))\n",
        "FAIL  rule (d): errors.py does not read the environment", None,
        "the environment read outside env.py"),
    Control(
        "d-from-os-getenv", "d", "audit.py", "\nimport tempfile\n",
        "\nimport tempfile\nfrom os import getenv  # noqa: F401\n",
        "FAIL  rule (d): audit.py does not read the environment", None,
        "the same read spelled without `os.`"),
    Control(
        "d-xauthority", "d", "errors.py", ANCHOR,
        "\n# the cookie goes in XAUTHORITY\nSKIP = 77\n",
        "FAIL  rule (d): errors.py does not mention XAUTHORITY", None,
        "only env.py builds the X cookie variable"),
)
"""Every control, in report order."""


def sandbox(tmp):
    """Copy the package to `<tmp>/tools/duckmcp`; return that folder."""
    dest = os.path.join(tmp, "tools", "duckmcp")
    shutil.copytree(DUCKMCP_DIR, dest,
                    ignore=shutil.ignore_patterns("__pycache__"))
    return dest


def run_selftest(pkg):
    """`(exit code, output)` of the sandbox selftest in quiet mode."""
    proc = subprocess.run(
        [sys.executable, os.path.join(pkg, "selftest.py"), "--quiet"],
        capture_output=True, text=True, timeout=300)
    return proc.returncode, proc.stdout + proc.stderr


def plant(pkg, control):
    """Apply the one substitution; return None or why it is broken."""
    path = os.path.join(pkg, control.file)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    count = text.count(control.old)
    if count != 1:
        return "old text matches %d time(s) in %s, not 1" % (count,
                                                              control.file)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace(control.old, control.new))
    if control.extra:
        extra, content = control.extra
        with open(os.path.join(os.path.dirname(pkg), extra), "w",
                  encoding="utf-8") as f:
            f.write(content)
    return None


def run_control(control):
    """`(red as required, report lines)` for one control in a fresh copy."""
    with tempfile.TemporaryDirectory(prefix="duckmcp-ctl-") as tmp:
        pkg = sandbox(tmp)
        broken = plant(pkg, control)
        if broken:
            return False, ["BROKEN %s: %s" % (control.id, broken)]
        code, out = run_selftest(pkg)
    fails = [line.strip() for line in out.splitlines()
             if line.strip().startswith("FAIL")]
    hit = [line for line in fails if line.startswith(control.expect)]
    if code != 0 and hit:
        return True, ["red    %s (rule %s): %s" % (control.id, control.rule,
                                                   hit[0])]
    why = ("exit 0" if code == 0
           else "red, but not on %r" % control.expect)
    return False, ["GREEN  %s (rule %s): %s" % (control.id, control.rule,
                                                why)] + \
        ["         %s" % line for line in fails]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true",
                    help="list the controls and exit")
    ap.add_argument("--only", metavar="ID", help="run one control")
    args = ap.parse_args(argv)
    if args.list:
        for c in CONTROLS:
            print("%-26s rule (%s)  %s:  %s" % (c.id, c.rule, c.file, c.why))
        return 0
    chosen = [c for c in CONTROLS if args.only in (None, c.id)]
    if not chosen:
        print("no control named %r; see --list" % args.only)
        return 2

    with tempfile.TemporaryDirectory(prefix="duckmcp-ctl-") as tmp:
        code, out = run_selftest(sandbox(tmp))
    if code != 0:
        print("the untouched sandbox is not green, so no red means anything:")
        print(out.rstrip())
        print("duckmcp_controls: 0 control(s) run, baseline red")
        return 1
    print("baseline: the untouched sandbox is green")

    red = 0
    per_rule = collections.Counter()
    for control in chosen:
        ok, lines = run_control(control)
        for line in lines:
            print(line)
        if ok:
            red += 1
            per_rule[control.rule] += 1
    rules = ", ".join("(%s) %d/%d" % (r, per_rule[r],
                                      sum(c.rule == r for c in chosen))
                      for r in sorted({c.rule for c in chosen}))
    print("duckmcp_controls: %d control(s), %d red as required; per rule %s"
          % (len(chosen), red, rules))
    return 0 if red == len(chosen) else 1


if __name__ == "__main__":
    sys.exit(main())
