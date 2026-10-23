#!/usr/bin/env python3
"""The negative controls of duckmcp's design rules, planted by command.

A rule that has never been seen red is decoration. Each control here is ONE
literal substitution in one file of this package, or ONE new file planted
beside it: the engine copies `tools/duckmcp/` into a sandbox
(`<tmp>/tools/duckmcp/`), with every other `.py` of `tools/` beside it so the
audit of rule (b) sees the same tree, plants, runs the sandbox
`selftest.py --quiet`, and demands two things -- a non-zero exit, and a
`FAIL` line carrying the text of the assertion the control claims to cover.
Red through another assertion does not count.

A substitution whose old text matches zero times or more than once is a
BROKEN control, not a red one: a literal that does not match leaves the copy
intact, and the run would come out green for the wrong reason. So is a
planted file whose directory is missing from the sandbox or that is already
there. Before any control the untouched sandbox must come out green, or no
red means anything.

The rules are those of PLAN-DUCKMCP-PY.md section 3.3: (a) nothing outside
the stdlib on import, (c) nothing of a game inside the package, (d) only
`env.py` reads the environment, and (b) outside the package no raw site
beyond the `PENDING` list of `selftest.py` -- a new file in another project
with `import fork` or a raw `client.call(`, an entry counted past what the
audit finds, an entry naming no migration task. Beside them,
the controls of rule `client` break the transport itself and its liveness
seam, and demand the assertion of `client.self_check()` or
`fork.self_check()` that covers the broken behaviour; the control of rule
`session` drops `duration_frames` from `Session.press` (pitfall 36) and
demands the fake-client assertion of `session.self_check()`, and the controls
of rule `debug` drop the clear from the `finally` of `debug.breakpoints` and
the liveness check from `debug.wait_for_pause` (pitfall 35), each demanding
its assertion of `debug.self_check()`.

The last line says how many controls ran, how many went red as required,
how many of those cover the design rules (a) to (d), and the count per rule;
the exit is 0 only when every one did.

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
control needs beside the package, never a substitution. A control with
`file` None plants only that file.
"""

DESIGN_RULES = ("a", "b", "c", "d")
"""The rules of PLAN-DUCKMCP-PY.md section 3.3, counted apart on the last
line."""

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
        "c-game-window-title", "c", "fork.py", "\nDIALOGS = (",
        "\nGAME_WINDOW = \"^Pro Evolution Soccer 2$\"\nDIALOGS = (",
        "FAIL  rule (c): fork.py names no game window title", None,
        "the title default the launcher had before it moved (section 2.1): "
        "a game's window title is the caller's"),
    Control(
        "c-launch-default-title", "c", "fork.py",
        "def launch(image, match=None,",
        "def launch(image, match=\"^Any Game$\",",
        "FAIL  fork: launch() has no default title (match=None)", None,
        "a default title the deny-list does not know: the structural half "
        "of the same rule"),
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
        "d-aliased-os", "d", "errors.py", ANCHOR,
        "\nimport os as _os\nSKIP = int(_os.environ.get('SKIP', '77'))\n",
        "FAIL  rule (d): errors.py does not read the environment", None,
        "the same read through `os` bound to another name"),
    Control(
        "d-xauthority", "d", "errors.py", ANCHOR,
        "\n# the cookie goes in XAUTHORITY\nSKIP = 77\n",
        "FAIL  rule (d): errors.py does not mention XAUTHORITY", None,
        "only env.py builds the X cookie variable"),
    Control(
        "b-import-fork-kit2d", "b", None, None, None,
        "FAIL  rule (b): no raw site outside PENDING",
        ("kit2d/dmcp_probe_b.py", "import fork  # planted\n"),
        "a project that never talked to the emulator starts importing the "
        "launcher shim, in a file the list does not know"),
    Control(
        "b-import-qualified-kit2d", "b", None, None, None,
        "FAIL  rule (b): no raw site outside PENDING",
        ("kit2d/dmcp_probe_b.py",
         "import pes2.mcp  # planted\nfrom pes2 import fork  # planted\n"),
        "the same modules reached through the host as a namespace package: "
        "the bare-name pattern alone would miss them (CORR-DMCP-024)"),
    Control(
        "b-client-call-kit2d", "b", None, None, None,
        "FAIL  rule (b): no raw site outside PENDING",
        ("kit2d/dmcp_probe_b.py",
         "def poke(client):\n    return client.call(\"pause\")\n"),
        "a raw client.call( outside the lib instead of Session or debug"),
    Control(
        "b-stale-entry", "b", "selftest.py",
        "     'from mcp import Client, NotRunning # noqa: E402', 1),\n",
        "     'from mcp import Client, NotRunning # noqa: E402', 2),\n",
        "FAIL  rule (b): no stale PENDING entry (listed, no longer found)",
        None,
        "an entry counting a site the audit no longer finds: a migration "
        "that removed sites without shrinking the list"),
    Control(
        "b-unknown-task", "b", "selftest.py",
        "    ('DMCP-TASK-30', 'tools/kit2d/selftest.py', 'sys.path',\n",
        "    ('DMCP-TASK-99', 'tools/kit2d/selftest.py', 'sys.path',\n",
        "FAIL  rule (b): every PENDING entry names a migration task", None,
        "an entry no task of phases 5 to 9 removes: it would never leave"),
    Control(
        "b-duplicate-key", "b", "selftest.py",
        "    ('DMCP-TASK-20', 'tools/pes2/who_writes.py', 'client',\n"
        "     'client.call(\"breakpoint\", action=\"clear\")', 2),\n",
        "    ('DMCP-TASK-20', 'tools/pes2/who_writes.py', 'client',\n"
        "     'client.call(\"breakpoint\", action=\"clear\")', 1),\n"
        "    ('DMCP-TASK-20', 'tools/pes2/who_writes.py', 'client',\n"
        "     'client.call(\"breakpoint\", action=\"clear\")', 1),\n",
        "FAIL  rule (b): no key appears twice in PENDING", None,
        "one key split over two entries: the multiset is unchanged, so only "
        "the duplicate check sees it"),
    Control(
        "b-zero-count", "b", "selftest.py",
        "    ('DMCP-TASK-30', 'tools/kit2d/selftest.py', 'sys.path',\n"
        "     'sys.path.insert(0, os.path.join(TOOLS_DIR, \"pes2\"))', 1),\n",
        "    ('DMCP-TASK-30', 'tools/kit2d/selftest.py', 'sys.path',\n"
        "     'sys.path.insert(0, os.path.join(TOOLS_DIR, \"pes2\"))', 0),\n",
        "FAIL  rule (b): every PENDING count is at least 1", None,
        "an entry counting nothing: it lists a site it does not hold"),
    Control(
        "b-total-drifts", "b", "audit.py",
        "        \"total\": len(sites),\n",
        "        \"total\": len(sites) + 1,\n",
        "FAIL  rule (b): PENDING lists", None,
        "the audit's printed total off its own sites: the number migration "
        "Logs paste would no longer be the list's size"),
    Control(
        "client-session-never-reclaimed", "client", "client.py",
        "            if not self.reclaim:\n                raise\n",
        "            raise\n",
        "FAIL  client: a stolen session is recovered once and the call goes "
        "through", None,
        "a stolen session (pitfall 46) re-raised instead of taken back: the "
        "loopback stand-in of the one-session rule must catch it"),
    Control(
        "client-liveness-unwired", "client", "client.py",
        "        return bool(fork.running_pids())\n",
        "        return None\n",
        "FAIL  fork: process_alive() is False when running_pids() == []",
        None,
        "the seam left at its old unknown answer: a refused port could no "
        "longer tell a dead fork from a mute server"),
    Control(
        "fork-kills-foreign-apprun", "fork", "fork.py",
        "        if \"duckstation\" not in cmdline(pid).lower():\n"
        "            continue\n",
        "",
        "FAIL  fork: an AppRun whose command line is not DuckStation's is "
        "spared", None,
        "the command-line filter dropped: kill() SIGKILLs every type-2 "
        "AppImage, since all of them run as AppRun"),
    Control(
        "fork-first-window-wins", "fork", "fork.py",
        "return max(kept, key=lambda pair: pair[0])[1]",
        "return kept[0][1]",
        "FAIL  fork: with no match the widest non-dialog window wins", None,
        "the pes2 rule the move replaced: the first window, not the widest"),
    Control(
        "fork-own-pid-kept", "fork", "fork.py",
        "        if pid == own or pid in pids:\n",
        "        if pid in pids:\n",
        "FAIL  fork: select_pids drops our own pid even when pgrep lists it",
        None,
        "the own-pid filter dropped: kill() would SIGKILL its caller"),
    Control(
        "press-without-duration", "session", "session.py",
        "        self.call(\"press_button\", button=name, duration_frames=frames,\n"
        "                  **extra)\n",
        "        self.call(\"press_button\", button=name,\n"
        "                  **extra)\n",
        "FAIL  session: press always sends duration_frames (pitfall 36)", None,
        "the press without its release: the server holds the button until "
        "something else lets it go (pitfall 36)"),
    Control(
        "live-kills-on-skip", "live", "live.py",
        "        if set(fork.running_pids()) - running:\n",
        "        if True:\n",
        "FAIL  live: a skipped launch leaves another session's emulator "
        "alive", None,
        "the old order: kill in a finally around launch, so a skipped run "
        "stops an emulator it never opened"),
    Control(
        "gpu-loop-as-too-long", "gpu", "gpu.py",
        "            raise GpuListLoop(\n",
        "            raise GpuListTooLong(\n",
        "FAIL  gpu: walk refuses a list looping back to its head as a loop",
        None,
        "a loop reported as a long list: the caller can no longer tell a "
        "corrupt list from a big one"),
    Control(
        "gpu-end-marker-ignored", "gpu", "gpu.py",
        "        if nxt == END_MARKER:\n",
        "        if nxt == END_MARKER and False:\n",
        "FAIL  gpu.self_check() raised ValueError", None,
        "the walk runs past the end marker into memory that is not the list"),
    Control(
        "png-paeth-tie-upleft-first", "png", "png.py",
        "    if pa <= pb and pa <= pc:\n"
        "        return left\n"
        "    return up if pb <= pc else upleft\n",
        "    if pc <= pa and pc <= pb:\n"
        "        return upleft\n"
        "    if pa <= pb:\n"
        "        return left\n"
        "    return up\n",
        "FAIL  png: Paeth breaks its ties left, then up, then upper-left, as "
        "Pillow did", None,
        "the tie-break order swapped on both sides: a round trip passes, "
        "only the fixed tie vector sees it"),
    Control(
        "vram-blue-shift", "vram", "vram.py",
        "    return (r << 3, g << 3, b << 3)\n",
        "    return (r << 3, g << 3, b << 2)\n",
        "FAIL  vram: to_halfword(to_rgb(h)) == h for all 32768 values", None,
        "one channel scaled by the wrong shift"),
    Control(
        "psx-range-planted", "psx", "psx.py",
        "    (\"BIOS\", 0xBFC00000, 0xBFC7FFFF),\n",
        "    (\"BIOS\", 0xBFC00000, 0xBFC7FFFF),\n"
        "    (\"planted\", 0x12340000, 0x1234FFFF),\n",
        "FAIL  rule (c): the address judge refuses the gaps between ranges",
        None,
        "a range that is not the console's: rule (c) reads psx.py, so its "
        "sentinel has to go red"),
    Control(
        "live-frames-unchecked", "live", "live.py",
        '    if after - before != steps:\n',
        '    if False:\n',
        'FAIL  live: failures() names frames when frame_number moves wrong', None,
        'frame_step no longer judged: a server that steps nothing would pass'),
    Control(
        "live-ram-unchecked", "live", "live.py",
        '    if reads["ram"] != psx.RAM_SIZE:\n',
        '    if False:\n',
        'FAIL  live: failures() names ram when RAM is short', None,
        'the RAM length no longer judged'),
    Control(
        "live-vram-unchecked", "live", "live.py",
        '    if reads["vram"] != (psx.VRAM_WIDTH, psx.VRAM_HEIGHT):\n',
        '    if False:\n',
        'FAIL  live: a 1024x513 VRAM fails, named vram', None,
        'the VRAM size no longer judged'),
    Control(
        "live-serial-unchecked", "live", "live.py",
        '    if reads["game"].serial is None:\n',
        '    if False:\n',
        'FAIL  live: an empty serial fails, named serial', None,
        'game() no longer has to name a disc'),
    Control(
        "live-png-error-escapes", "live", "live.py",
        '    except (Fail, NotRunning, ToolError, ValueError) as exc:\n',
        '    except (Fail, NotRunning, ToolError) as exc:\n',
        'FAIL  live: a VRAM file that does not decode ends in a FAIL line', None,
        'a PngError escapes main as a traceback: the last line is no verdict'),
    Control(
        "breakpoint-not-cleared", "debug", "debug.py",
        '        _quietly(client, "breakpoint", action="clear")\n',
        '',
        "FAIL  debug: an exception inside breakpoints still clears and pauses",
        None,
        "the finally of breakpoints without its clear: a failed run leaves a "
        "breakpoint armed in the emulator the next run inherits"),
    Control(
        "wait-without-liveness", "debug", "debug.py",
        "        if probe() is False:\n",
        "        if False:\n",
        "FAIL  debug: a death mid-wait is a Fail citing pitfall 35", None,
        "the wait without its liveness check: a fork that died mid-wait "
        "(pitfall 35) reads as a breakpoint that never fired"),
)
"""Every control, in report order."""


def sandbox(tmp):
    """Copy the package to `<tmp>/tools/duckmcp`, and every other `.py` of
    `tools/` beside it (what the audit of rule (b) reads); return the
    package folder."""
    tools = os.path.dirname(DUCKMCP_DIR)
    dest = os.path.join(tmp, "tools", "duckmcp")
    shutil.copytree(DUCKMCP_DIR, dest,
                    ignore=shutil.ignore_patterns("__pycache__"))
    for here, dirs, files in os.walk(tools):
        dirs[:] = [d for d in dirs if d != "__pycache__" and
                   os.path.join(here, d) != DUCKMCP_DIR]
        for name in files:
            if name.endswith(".py"):
                rel = os.path.relpath(os.path.join(here, name), tools)
                target = os.path.join(tmp, "tools", rel)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copy2(os.path.join(here, name), target)
    return dest


def run_selftest(pkg):
    """`(exit code, output)` of the sandbox selftest in quiet mode."""
    proc = subprocess.run(
        [sys.executable, os.path.join(pkg, "selftest.py"), "--quiet"],
        capture_output=True, text=True, timeout=300)
    return proc.returncode, proc.stdout + proc.stderr


def plant(pkg, control):
    """Apply the one substitution; return None or why it is broken."""
    if control.file is not None:
        path = os.path.join(pkg, control.file)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        count = text.count(control.old)
        if count != 1:
            return "old text matches %d time(s) in %s, not 1" % (
                count, control.file)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.replace(control.old, control.new))
    elif not control.extra:
        return "no substitution and no planted file"
    if control.extra:
        extra, content = control.extra
        target = os.path.join(os.path.dirname(pkg), *extra.split("/"))
        if not os.path.isdir(os.path.dirname(target)):
            return "the sandbox has no %s" % os.path.dirname(extra)
        if os.path.exists(target):
            return "the planted %s is already in the sandbox" % extra
        with open(target, "w", encoding="utf-8") as f:
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
            print("%-26s rule (%s)  %s:  %s" % (
                c.id, c.rule, c.file or c.extra[0], c.why))
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
    design = sum(per_rule[r] for r in DESIGN_RULES)
    print("duckmcp_controls: %d control(s), %d red as required; "
          "%d/%d cover rules (a) to (d); per rule %s"
          % (len(chosen), red, design,
             sum(c.rule in DESIGN_RULES for c in chosen), rules))
    return 0 if red == len(chosen) else 1


if __name__ == "__main__":
    sys.exit(main())
