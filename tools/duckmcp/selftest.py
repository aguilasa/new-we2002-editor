#!/usr/bin/env python3
"""The duckmcp gate `duckmcp_selftest`: needs nothing, never skips.

In this order:

1. the package imports as `import duckmcp` with `tools/` on `sys.path`, and
   re-exports the errors;
2. `errors.self_check()`: `SKIP == 77` and the exception hierarchy;
3. `env.self_check()`: the new variable beats its legacy fallback, the
   legacy one alone beats the default, neither gives the default; the `:98`
   rule of `x_env`; `is_roms` on both separators; the `state_path` shape;
4. `client.self_check()`: JSON and SSE replies decode the same, error
   replies raise, a refused port says whether the process is alive, dead or
   unknown, and against a loopback stand-in of the fork's one-session rule a
   stolen session is recovered once, a second loss is an error, and another
   `ToolError` passes without a new handshake;
4b. `fork.self_check()`: the kill list, a missing install is `Skip` naming
   the recipe, `roms/` refused by `launch` on both separators, a joystick
   node refused, `running_pids` never our own pid, the window choice with
   and without a title, and the client's default liveness probe over
   `fork.running_pids()` stubbed (`[]` dead, `[4242]` alive, raising
   unknown); then, here, `fork.child_env`'s `:98` rule, which spells the
   variable only this file and `env.py` may;
5. `cli.self_check()`: `call TOOL a=1 b="x"` decodes into the arguments it
   sends, the old flags become subcommand lines; and `cli.py list` against
   a refused port (port 1), run as a script, exits 77 with the
   `NotRunning` sentence on stderr;
5b. `buttons.self_check()`: the sixteen names round-trip in any
   capitalisation, junk is refused with the list, and `canonical()` agrees
   with the `capitalize()` rule it replaces; `session.self_check()`, against
   a fake client that records calls: `press` always sends `duration_frames`
   (pitfall 36) and steps `frames + after`, `Session(fake)` takes any object
   with `initialize`, `call`, `session`, `server`, `capture` returns a path,
   `read_ram` checks the length, `game()` reads `game_serial`/`game_title`,
   `save_state` waits for the file, and the fork is killed on exit only when
   the session launched it; then, here, importing `duckmcp.session` in a
   fresh interpreter loads no imaging library;
5c. `debug.self_check()`, against a fake client: addresses, stores,
   registers and the `wait_for_pause` reply shapes; a breakpoint that never
   fires is a `Fail`, and so is the process dying mid-wait, citing pitfall
   35; the poll interval is slept (0 allowed) and a nudge carries its
   release; an exception inside `breakpoints` (and `vram_watch`) still
   leaves `breakpoint clear` and `pause` as the last calls; `who_writes`
   returns `pc`, `registers`, `rows`, `store`, `caller`; `stops` closes on
   repetition; `watch_reads` reads `breakpoint list`;
6. `audit.self_check()`: the audit of rule (b) over synthetic tools trees
   built in a temporary directory -- a clean one counts 0, one planted
   `import fork` counts 1, and each site category is seen once;
6b. `psx.self_check()`: the ranges against the sizes they are built from,
   the three segments folding onto one physical address, KSEG2 refused;
   `gpu.self_check()`: every GP0 opcode shape gets its hardware size, a
   synthetic list with one packet of each is walked to the end marker, and
   a list looping to its head, to its middle or through two mirrors is
   refused; `png.self_check()`: images `png.encode` wrote are decoded pixel
   for pixel under each of the five filters and each colour type, a fixed
   vector decodes as Pillow did, and bad files are refused with the reason;
   `vram.self_check()`: all 32768 fifteen-bit values round-trip;
   `savestate.self_check()`: synthetic stored states read back, `diff` and
   `scan` find what was planted, and a missing kernel mark, one shifted by
   45 bytes, a truncated file, a wrong RAM size and a missing file are
   refused;
7. the design rules of PLAN-DUCKMCP-PY.md section 3.3, over every `.py` of
   this package:
   - (a) every `import` names the stdlib or this package, and importing
     `duckmcp` and each of its modules, each in a fresh interpreter, loads
     nothing outside the stdlib (`sys.stdlib_module_names`);
   - (c) no game serial, no project name outside a marked `# lineage:`
     comment, no game window title this repository drives (anywhere, lineage
     included), and no address literal outside the PS1 hardware ranges,
     which are `psx.HARDWARE_RANGES`, read through the module;
   - (d) only `env.py` reads the environment, and only `env.py` mentions
     `XAUTHORITY`.
   `selftest.py` and `controls.py` are exempt from (c) and from the
   `XAUTHORITY` half of (d): they hold the patterns they judge.
8. rule (b), over the rest of the tools tree (`tools/` minus this package):
   every raw site `audit.py` finds is held against `PENDING` by its
   `audit.site_keys` key -- file, category, printed line, never the line
   number. A site beyond the list is red, an entry the audit no longer
   finds is red, an entry naming a task outside `MIGRATIONS` is red, and the
   size of the list (the sum of its counts) must equal the audit total.

`controls.py` plants one defect per rule in a sandbox copy and demands
this script goes red on the line that rule prints.

Each failed assertion prints one `FAIL` line naming it. The last line says
how many checks ran and how many failed; the exit is 0 only with none.

Usage:
    python3 tools/duckmcp/selftest.py [--quiet]
"""

import argparse
import ast
import collections
import json
import os
import re
import subprocess
import sys

DUCKMCP_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(DUCKMCP_DIR)
sys.path.insert(0, TOOLS_DIR)

import duckmcp  # noqa: E402
from duckmcp import (audit, buttons, cli, client, debug, env,  # noqa: E402
                     errors, fork, gpu, live, png, psx, savestate,
                     session, vram)

JUDGES = ("selftest.py", "controls.py")
"""The files that hold the patterns of rule (c), and so are exempt from it."""

ENV_MODULE = "env.py"
"""The one module allowed to read the environment (rule (d))."""

LEGACY_ENV_NAMES = ("PES2_MCP_HOST", "PES2_MCP_PORT", "PES2_FORK",
                    "PES2_DUCKSTATION", "PES2_DISPLAY")
"""The five legacy variable names `env.py` may spell, and only `env.py`.

Decision 3 of PLAN-DUCKMCP-PY.md section 2: the old `PES2_*` names are read
as fallback while the callers migrate, so `env.py` must hold them as string
literals. Exactly these five, and only in `env.py`: any other `PES2`/`pes2`
there, or one of these five anywhere else, still breaks rule (c).
"""

SERIAL_RE = re.compile(r"S[LC][EPU][SM]-\d{5}")
"""A PlayStation disc serial (rule (c))."""

PROJECT_RE = re.compile(r"(?<![A-Za-z0-9])(pes2|looks|kits|kit2d|we2002)"
                        r"(?![A-Za-z0-9])", re.IGNORECASE)
"""A project name of this repository (rule (c)).

The boundary is any non-alphanumeric, not `\\b`: `_` is a word character,
and `\\bpes2\\b` would let `PES2_SERIAL` through.
"""

TITLE_RE = re.compile(r"Pro Evolution Soccer|Winning Eleven|World Soccer",
                      re.IGNORECASE)
"""A game window title this repository drives (rule (c), section 2.1).

A deny-list, so a title not on it passes: the structural half is
`fork.self_check`'s "launch() has no default title (match=None)".
"""

LINEAGE = "# lineage:"
"""What opens a lineage comment, the one place a project name may appear."""

HEX_RE = re.compile(r"(?<![0-9A-Za-z_])0[xX][0-9A-Fa-f_]+")
"""A hexadecimal literal, in code or in prose."""

ADDRESS_FLOOR = 0x10000
"""Below this a literal is a constant, not an address, and is not judged."""

ENV_ATTRS = ("environ", "environb", "getenv", "getenvb", "putenv",
             "unsetenv")
"""The `os` names that read or write the environment (rule (d))."""

OS_MODULES = ("os", "posix", "nt")
"""The modules that hold those names: `os` and its two platform halves."""

XAUTH = "XAUTHORITY"
"""The variable only `env.py` may build (rule (d))."""


MIGRATIONS = ("DMCP-TASK-19", "DMCP-TASK-20", "DMCP-TASK-22", "DMCP-TASK-23",
              "DMCP-TASK-25", "DMCP-TASK-26", "DMCP-TASK-30")
"""The tasks of phases 5 to 7 and 9 that remove raw sites (rule (b))."""

PENDING = (
    # DMCP-TASK-30
    ('DMCP-TASK-30', 'tools/kit2d/selftest.py', 'sys.path',
     'sys.path.insert(0, os.path.join(TOOLS_DIR, "pes2"))', 1),
    ('DMCP-TASK-30', 'tools/kits/core/tex.py', 'sys.path',
     'sys.path.insert(0, _path)', 1),
    ('DMCP-TASK-30', 'tools/kits/oracle.py', 'sys.path',
     'sys.path.insert(0, _path)', 1),
    ('DMCP-TASK-30', 'tools/looks/atlas.py', 'sys.path',
     'sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),', 1),
    ('DMCP-TASK-30', 'tools/looks/iso_source.py', 'sys.path',
     'sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pes2"))', 1),
    ('DMCP-TASK-30', 'tools/looks/oracle.py', 'sys.path',
     'sys.path.insert(0, PES2)', 1),
    ('DMCP-TASK-30', 'tools/looks/sprites.py', 'sys.path',
     'sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pes2"))', 1),
)
"""The raw sites rule (b) still tolerates outside this package.

Each entry is `(task, file, category, snippet, count)`: the task that
removes the site, then the key `audit.py` gives it -- the file under the
repository root, the category, and the source line as the audit prints it
(whitespace folded, cut at `audit.SNIPPET`) -- and how many sites share
that key. The line number is left out on purpose: an unrelated edit above a
site moves it, and the list must not churn for that. Equal lines in one
file are one entry with their count.

The check is a multiset equality both ways: a site the audit finds beyond
an entry's count is red (a new raw site), and an entry whose count exceeds
what the audit finds is red too (stale), so a migration that removes sites
shrinks this list in the same commit. The size is the sum of the counts,
and it equals the audit total; task 30 leaves it empty.

The task is the planned remover, by file per the phases of
PLAN-DUCKMCP-PY.md section 6; inside the one file split across two tasks
the breakpoint-family calls go to the later one. A `sys.path` site stays
until the module home is gone, so all of them are task 30's. A migrating
task may move an entry to a later task, saying so in its Log.
"""


class Checker:
    """Counts the checks that ran and the ones that failed."""

    def __init__(self, verbose):
        self.verbose = verbose
        self.ran = 0
        self.failed = 0

    def ok(self, name, cond, detail=""):
        self.ran += 1
        if cond:
            if self.verbose:
                print("  ok    %s" % name)
        else:
            self.failed += 1
            print("  FAIL  %s%s" % (name, "  " + str(detail) if detail else ""))

    def module(self, name, self_check):
        """Each `(name, passed, detail)` a module's self_check returns."""
        try:
            results = self_check()
        except Exception as exc:  # noqa: BLE001
            self.ok("%s.self_check() raised %s: %s"
                    % (name, type(exc).__name__, exc), False)
            return
        self.ok("%s.self_check() asserted something" % name, bool(results))
        for what, passed, detail in results:
            self.ok("%s: %s" % (name, what), passed, "" if passed else detail)


def package_files():
    """Every `.py` of this package, as `(relative path, source)`."""
    out = []
    for here, dirs, files in os.walk(DUCKMCP_DIR):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for name in sorted(files):
            if name.endswith(".py"):
                path = os.path.join(here, name)
                with open(path, encoding="utf-8") as f:
                    out.append((os.path.relpath(path, DUCKMCP_DIR)
                                .replace(os.sep, "/"), f.read()))
    return out


def module_name(rel):
    """`errors.py` -> `duckmcp.errors`, `__init__.py` -> `duckmcp`."""
    parts = rel[:-3].split("/")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(["duckmcp"] + parts)


def stdlib_names():
    """The top-level stdlib module names, or None before Python 3.10."""
    return getattr(sys, "stdlib_module_names", None)


def foreign_imports(tree, stdlib):
    """`(line, name)` of each absolute import outside the stdlib and us."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            names = [node.module or ""]
        else:
            continue
        for name in names:
            top = name.split(".")[0]
            if top != "duckmcp" and top not in stdlib:
                out.append((node.lineno, name))
    return out


_PROBE = """
import importlib, json, sys
sys.path.insert(0, %r)
before = set(sys.modules)
importlib.import_module(%r)
new = set(sys.modules) - before
print(json.dumps(sorted(m for m in new
      if m.split(".")[0] not in sys.stdlib_module_names
      and m.split(".")[0] != "duckmcp")))
"""


def loaded_foreign(module):
    """The non-stdlib modules importing `module` loads, in a fresh `-I` run.

    Returns `(names, error)`: `error` is the stderr tail when the import
    itself failed.
    """
    proc = subprocess.run([sys.executable, "-I", "-c",
                           _PROBE % (TOOLS_DIR, module)],
                          capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        return None, (proc.stderr.strip().splitlines() or ["exit %d"
                                                           % proc.returncode])[-1]
    return json.loads(proc.stdout.strip().splitlines()[-1]), None


def lineage_lines(source):
    """Indices of the lines inside a full-line `# lineage:` comment block.

    The block opens with a comment line starting `# lineage:` and runs over
    the comment-only lines right after it.
    """
    out = set()
    inside = False
    for i, line in enumerate(source.splitlines()):
        text = line.strip()
        if text.startswith(LINEAGE):
            inside = True
        elif not text.startswith("#"):
            inside = False
        if inside:
            out.add(i)
    return out


def judged_for_names(rel, source):
    """`(line number, text)` rule (c) judges for project names.

    Lineage comments are dropped (a trailing `# lineage:` drops only the
    comment), and in `env.py` the five legacy names are blanked first.
    """
    lineage = lineage_lines(source)
    out = []
    for i, line in enumerate(source.splitlines()):
        if i in lineage:
            continue
        at = line.find(LINEAGE)
        text = line if at < 0 else line[:at]
        if rel == ENV_MODULE:
            for name in LEGACY_ENV_NAMES:
                text = re.sub(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % name,
                              " ", text)
        out.append((i + 1, text))
    return out


def outside_hardware(value):
    """True for a literal that is judged and falls in no `psx.py` range."""
    if value < ADDRESS_FLOOR:
        return False
    # read through the module on every call, never bound here: the ranges
    # are psx.py's, and a constant of the same name in this file is not them
    return not any(lo <= value <= hi for _, lo, hi in psx.HARDWARE_RANGES)


def env_reads(tree):
    """`(line, what)` of each environment access in a parsed module."""
    # the names `os` (or `posix`/`nt`, which hold the same reads) is bound
    # to: `import os as _os` reads through `_os.environ`
    modules = {"os"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(a.asname or a.name for a in node.names
                           if a.name in OS_MODULES)
    out = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Attribute) and node.attr in ENV_ATTRS
                and isinstance(node.value, ast.Name)
                and node.value.id in modules):
            out.append((node.lineno, "%s.%s" % (node.value.id, node.attr)))
        elif (isinstance(node, ast.ImportFrom) and node.module in OS_MODULES
              and any(a.name in ENV_ATTRS for a in node.names)):
            out.append((node.lineno, "from %s import %s"
                        % (node.module, ", ".join(a.name for a in node.names))))
        elif (isinstance(node, ast.Name) and node.id in ("environ", "getenv")
              and isinstance(node.ctx, ast.Load)):
            out.append((node.lineno, node.id))
    return out


def where(hits):
    """`line 3: x; line 9: y` for a FAIL detail."""
    return "; ".join("line %d: %s" % hit for hit in hits)


def check_rules(c):
    """Rules (a), (c) and (d) of section 3.3 over every file of the package."""
    files = package_files()
    c.ok("rules: the package has files to judge", len(files) >= 4,
         [rel for rel, _ in files])
    c.ok("rule (c): the address judge accepts RAM, scratchpad, I/O, BIOS",
         not any(outside_hardware(v) for v in
                 (0x80010000, 0x801FFFFF, 0x00100000, 0xA0000000,
                  0x1F800200, 0x1F801810, 0xBFC00000, 0x0010, 0xFFFF)))
    c.ok("rule (c): the address judge refuses the gaps between ranges",
         all(outside_hardware(v) for v in
             (0x12345678, 0x80200000, 0x1F800400, 0x1F803000, 0xBFC80000,
              0x00200000)))
    c.ok("rule (c): PROJECT_RE sees PES2_X and tools/pes2/, not pes20",
         bool(PROJECT_RE.search("PES2_X")) and bool(
             PROJECT_RE.search("tools/pes2/")) and not
         PROJECT_RE.search("pes20"))

    stdlib = stdlib_names()
    c.ok("rule (a): sys.stdlib_module_names exists (Python 3.10+)",
         stdlib is not None, sys.version.split()[0])
    for rel, source in files:
        try:
            tree = ast.parse(source, rel)
        except SyntaxError as exc:
            c.ok("rules: %s parses" % rel, False, exc)
            continue
        if stdlib is not None:
            c.ok("rule (a) static: %s imports only the stdlib" % rel,
                 not foreign_imports(tree, stdlib),
                 where(foreign_imports(tree, stdlib)))
            names, error = loaded_foreign(module_name(rel))
            c.ok("rule (a) loaded: import %s loads only the stdlib"
                 % module_name(rel), error is None and not names,
                 error or ", ".join(names or ()))

        reads = env_reads(tree)
        if rel == ENV_MODULE:
            c.ok("rule (d): env.py does read the environment", bool(reads))
        else:
            c.ok("rule (d): %s does not read the environment" % rel,
                 not reads, where(reads))

        if rel in JUDGES:
            continue
        lines = source.splitlines()
        if rel != ENV_MODULE:
            hits = [(i + 1, XAUTH) for i, line in enumerate(lines)
                    if XAUTH in line]
            c.ok("rule (d): %s does not mention %s" % (rel, XAUTH),
                 not hits, where(hits))

        serials = [(i + 1, m.group(0)) for i, line in enumerate(lines)
                   for m in SERIAL_RE.finditer(line)]
        c.ok("rule (c): %s holds no game serial" % rel, not serials,
             where(serials))
        names = [(n, m.group(0)) for n, text in judged_for_names(rel, source)
                 for m in PROJECT_RE.finditer(text)]
        c.ok("rule (c): %s names no project outside a lineage comment" % rel,
             not names, where(names))
        titles = [(i + 1, m.group(0)) for i, line in enumerate(lines)
                  for m in TITLE_RE.finditer(line)]
        c.ok("rule (c): %s names no game window title" % rel, not titles,
             where(titles))
        addresses = [(i + 1, m.group(0)) for i, line in enumerate(lines)
                     for m in HEX_RE.finditer(line)
                     if outside_hardware(int(m.group(0).replace("_", ""), 16))]
        c.ok("rule (c): %s has no address outside the hardware ranges" % rel,
             not addresses, where(addresses))

    env_text = dict(files).get(ENV_MODULE, "")
    missing = [n for n in LEGACY_ENV_NAMES if n not in env_text]
    c.ok("rule (c): every allow-listed legacy name is still in env.py",
         not missing, missing)


def pending_keys():
    """`Counter` of `(file, category, snippet)` over `PENDING`."""
    out = collections.Counter()
    for _, path, category, snippet, count in PENDING:
        out[path, category, snippet] += count
    return out


def check_rule_b(c):
    """Rule (b): the raw sites outside the package are exactly `PENDING`.

    The multiset comparison (no new site, no stale entry) is the rule. The
    other lines keep the list honest as a document: every entry names a
    migration task, counts at least 1, and has a key of its own -- a key
    split over two entries sums to the same multiset, so only that line
    sees it. The size line ties the list to `audit.py`'s printed total, the
    number migration Logs paste: it goes red when `doc["total"]` drifts from
    the sites `site_keys` counts, which the multiset lines cannot see.
    """
    doc = audit.audit(TOOLS_DIR)
    found = audit.site_keys(doc)
    listed = pending_keys()
    size = sum(listed.values())

    def show(diff):
        return "; ".join("%s: %s: %s (x%d)" % (k + (n,))
                         for k, n in sorted(diff.items()))

    new = found - listed
    stale = listed - found
    c.ok("rule (b): no raw site outside PENDING", not new, show(new))
    c.ok("rule (b): no stale PENDING entry (listed, no longer found)",
         not stale, show(stale))
    bad = sorted({entry[0] for entry in PENDING} - set(MIGRATIONS))
    c.ok("rule (b): every PENDING entry names a migration task", not bad,
         bad)
    zero = [entry[1:4] for entry in PENDING if entry[4] < 1]
    c.ok("rule (b): every PENDING count is at least 1", not zero, zero)
    keys = [entry[1:4] for entry in PENDING]
    c.ok("rule (b): no key appears twice in PENDING",
         len(keys) == len(set(keys)),
         sorted(k for k in set(keys) if keys.count(k) > 1))
    c.ok("rule (b): PENDING lists %d site(s) in %d entries, audit.py counts "
         "%d" % (size, len(PENDING), doc["total"]), size == doc["total"])


def check_child_env(c):
    """`fork.child_env`: the `:98` rule comes from `env.x_env`, and a missing
    install adds no library path."""
    on98 = fork.child_env(":98", home="/nowhere")
    c.ok("fork: child_env(':98') blanks XAUTHORITY",
         on98.get("XAUTHORITY") == "", repr(on98.get("XAUTHORITY")))
    on1 = fork.child_env(":1", home="/nowhere")
    c.ok("fork: child_env(':1') leaves XAUTHORITY as env.x_env does",
         on1.get("XAUTHORITY") == env.x_env(":1").get("XAUTHORITY"),
         repr(on1.get("XAUTHORITY")))
    c.ok("fork: child_env sets DISPLAY", on98.get("DISPLAY") == ":98")
    c.ok("fork: a missing install adds no library path",
         on98.get("LD_LIBRARY_PATH") == env.x_env(":98").get("LD_LIBRARY_PATH")
         and on98.get("QT_PLUGIN_PATH") == env.x_env(":98").get(
             "QT_PLUGIN_PATH"))


def check_cli_refused(c):
    """`cli.py list` as a script, against port 1 where nothing listens."""
    script = os.path.join(DUCKMCP_DIR, "cli.py")
    try:
        proc = subprocess.run([sys.executable, script, "--port", "1",
                               "--timeout", "5", "list"],
                              capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired as exc:
        c.ok("cli: list against a refused port exits 77", False, exc)
        return
    c.ok("cli: list against a refused port exits 77 (errors.SKIP)",
         proc.returncode == errors.SKIP,
         "exit %d; stderr %r" % (proc.returncode, proc.stderr[-300:]))
    c.ok("cli: the refused port prints the NotRunning sentence on stderr",
         "skipping: no MCP server at http://" in proc.stderr
         and ":1/mcp" in proc.stderr and "Traceback" not in proc.stderr,
         repr(proc.stderr[-300:]))


def check_live_kill(c):
    """`live.run` stops the fork only when it launched one (CORR-DMCP-011).

    `fork.launch`, `kill` and `running_pids` are stubbed: a launch that skips
    with an emulator of somebody else's running must not kill it, a launch
    that fails after its Popen (a new pid) must, and so must a launch that
    returned.
    """
    saved = fork.launch, fork.kill, fork.running_pids
    cases = (
        ("a skipped launch leaves another session's emulator alive",
         errors.Skip("no X server on :97"), [[4242], [4242]], 0),
        ("a launch that fails after its Popen stops the new pid",
         errors.Fail("the game window never appeared"), [[], [5150]], 1),
    )
    try:
        for name, raised, answers, want in cases:
            kills = []
            answers = list(answers)

            def launch(image, display=None, exc=raised):
                raise exc

            fork.launch = launch
            fork.kill = lambda verbose=True: kills.append(1) or 0
            fork.running_pids = lambda: answers.pop(0) if answers else []
            try:
                live.run("/x/a.cue", 1)
            except (errors.Skip, errors.Fail):
                pass
            c.ok("live: %s" % name, len(kills) == want,
                 "kill() called %d time(s), want %d" % (len(kills), want))
    finally:
        fork.launch, fork.kill, fork.running_pids = saved


def check_live_read_back(c):
    """`live.run` and `live.main` offline, over `session._FakeClient`
    (CORR-DMCP-017, -018, -019): each of the four conditions can fail and is
    named in the FAIL line, and a read that raises ends in a FAIL line, not a
    traceback. The fake's `dump_vram` writes a real PNG of the given size."""
    import contextlib
    import io

    blobs = {}

    def vram_png(width, height):
        if (width, height) not in blobs:
            blobs[width, height] = png.encode(width, height,
                                              [bytes(width * 3)] * height)
        return blobs[width, height]

    class Fake(session._FakeClient):
        def __init__(self, vram=(psx.VRAM_WIDTH, psx.VRAM_HEIGHT), **kw):
            super().__init__(**kw)
            self.vram = vram

        def tools(self):
            return ["get_status", "frame_step"]

        def call(self, name, **arguments):
            out = super().call(name, **arguments)
            if name == "dump_vram" and self.vram:
                self._touch(arguments["path"], vram_png(*self.vram))
            return out

    saved = fork.launch, fork.kill, fork.running_pids

    def main_with(client):
        fork.launch = lambda image, display=None: (1, 2, client)
        fork.kill = lambda verbose=True: 0
        fork.running_pids = lambda: []
        text = io.StringIO()
        try:
            with contextlib.redirect_stdout(text):
                rc = live.main(["--image", "/x/a.cue", "--steps", "3"])
        except Exception as exc:                             # noqa: BLE001
            rc = "escaped %s: %s" % (type(exc).__name__, exc)
        lines = text.getvalue().splitlines()
        return rc, lines[-1] if lines else ""

    try:
        rc, last = main_with(Fake())
        c.ok("live: the read-back passes on RAM, a 1024x512 VRAM and a serial",
             rc == 0 and last.startswith("duckmcp_live: ok --"), (rc, last))
        rc, last = main_with(Fake(serial=""))
        c.ok("live: an empty serial fails, named serial",
             rc == 1 and last.startswith("duckmcp_live: FAIL (serial) --"),
             (rc, last))
        rc, last = main_with(Fake(vram=(psx.VRAM_WIDTH, psx.VRAM_HEIGHT + 1)))
        c.ok("live: a 1024x513 VRAM fails, named vram",
             rc == 1 and last.startswith("duckmcp_live: FAIL (vram) --"),
             (rc, last))
        rc, last = main_with(Fake(vram=None))
        c.ok("live: a VRAM file that does not decode ends in a FAIL line",
             rc == 1 and last.startswith("duckmcp_live: FAIL -- PngError:"),
             (rc, last))
        rc, last = main_with(Fake(short_read=True))
        c.ok("live: a short RAM read ends in a FAIL line",
             rc == 1 and last.startswith("duckmcp_live: FAIL -- ToolError:"),
             (rc, last))
    finally:
        fork.launch, fork.kill, fork.running_pids = saved

    # RAM and frames cannot go wrong through the fake (read_ram refuses a
    # short read; the fake steps one frame a call), so failures() is judged
    # directly for them.
    ok = {"ram": psx.RAM_SIZE, "vram": (psx.VRAM_WIDTH, psx.VRAM_HEIGHT),
          "game": session.Game("X-1", "t")}
    c.ok("live: failures() is empty when all four hold",
         live.failures(3, 0, 3, ok) == [], live.failures(3, 0, 3, ok))
    c.ok("live: failures() names frames when frame_number moves wrong",
         live.failures(3, 0, 2, ok) == ["frames"], live.failures(3, 0, 2, ok))
    short = dict(ok, ram=psx.RAM_SIZE - 1)
    c.ok("live: failures() names ram when RAM is short",
         live.failures(3, 0, 3, short) == ["ram"],
         live.failures(3, 0, 3, short))


def check_session_imports(c):
    """`capture` hands back a path, so the module needs no imaging library:
    a fresh `-I` interpreter importing `duckmcp.session` loads none."""
    names, error = loaded_foreign("duckmcp.session")
    imaging = [n for n in names or () if n.split(".")[0] in ("PIL", "PySide6",
                                                             "numpy")]
    c.ok("session: importing duckmcp.session loads no PIL, PySide6 or numpy",
         error is None and not imaging, error or imaging)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quiet", action="store_true",
                    help="print only failures and the last line")
    args = ap.parse_args(argv)
    c = Checker(verbose=not args.quiet)

    c.ok("duckmcp is imported from tools/duckmcp/",
         os.path.dirname(os.path.abspath(duckmcp.__file__)) == DUCKMCP_DIR,
         duckmcp.__file__)
    c.ok("duckmcp has a __version__", bool(getattr(duckmcp, "__version__", "")))
    c.ok("duckmcp re-exports Client", getattr(duckmcp, "Client", None)
         is client.Client)
    c.ok("duckmcp re-exports Session", getattr(duckmcp, "Session", None)
         is session.Session)
    c.ok("duckmcp re-exports the errors",
         all(getattr(duckmcp, n, None) is getattr(errors, n)
             for n in ("SKIP", "Fail", "Skip", "NotRunning", "ToolError",
                       "SessionLost")))
    c.module("errors", errors.self_check)
    c.module("env", env.self_check)
    c.module("client", client.self_check)
    c.module("fork", fork.self_check)
    check_child_env(c)
    c.module("cli", cli.self_check)
    check_cli_refused(c)
    check_live_kill(c)
    check_live_read_back(c)
    c.module("buttons", buttons.self_check)
    c.module("session", session.self_check)
    check_session_imports(c)
    c.module("debug", debug.self_check)
    c.module("audit", audit.self_check)
    c.module("psx", psx.self_check)
    c.module("gpu", gpu.self_check)
    c.module("png", png.self_check)
    c.module("vram", vram.self_check)
    c.module("savestate", savestate.self_check)
    check_rules(c)
    check_rule_b(c)

    print("duckmcp_selftest: %d check(s) ran, %d failure(s)" % (c.ran, c.failed))
    return 0 if c.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
