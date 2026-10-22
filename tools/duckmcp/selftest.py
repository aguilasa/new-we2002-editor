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
6. `audit.self_check()`: the audit of rule (b) over synthetic tools trees
   built in a temporary directory -- a clean one counts 0, one planted
   `import fork` counts 1, and each site category is seen once;
7. the design rules of PLAN-DUCKMCP-PY.md section 3.3, over every `.py` of
   this package:
   - (a) every `import` names the stdlib or this package, and importing
     `duckmcp` and each of its modules, each in a fresh interpreter, loads
     nothing outside the stdlib (`sys.stdlib_module_names`);
   - (c) no game serial, no project name outside a marked `# lineage:`
     comment, no game window title this repository drives (anywhere, lineage
     included), and no address literal outside the PS1 hardware ranges;
   - (d) only `env.py` reads the environment, and only `env.py` mentions
     `XAUTHORITY`.
   `selftest.py` and `controls.py` are exempt from (c) and from the
   `XAUTHORITY` half of (d): they hold the patterns they judge. Rule (b)
   lives outside this package and closes in phase 4.

`controls.py` plants one defect per rule in a sandbox copy and demands
this script goes red on the line that rule prints.

Each failed assertion prints one `FAIL` line naming it. The last line says
how many checks ran and how many failed; the exit is 0 only with none.

Usage:
    python3 tools/duckmcp/selftest.py [--quiet]
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys

DUCKMCP_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(DUCKMCP_DIR)
sys.path.insert(0, TOOLS_DIR)

import duckmcp  # noqa: E402
from duckmcp import audit, cli, client, env, errors, fork  # noqa: E402

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

HARDWARE_RANGES = (
    ("RAM (KUSEG)", 0x00000000, 0x001FFFFF),
    ("RAM (KSEG0)", 0x80000000, 0x801FFFFF),
    ("RAM (KSEG1)", 0xA0000000, 0xA01FFFFF),
    ("scratchpad", 0x1F800000, 0x1F8003FF),
    ("I/O", 0x1F801000, 0x1F802FFF),
    ("BIOS", 0xBFC00000, 0xBFC7FFFF),
)
"""The PS1 hardware ranges an address literal may fall in (rule (c)).

Local until `psx.py` exists; DMCP-TASK-13 moves them there.
"""

ENV_ATTRS = ("environ", "environb", "getenv", "getenvb", "putenv",
             "unsetenv")
"""The `os` names that read or write the environment (rule (d))."""

OS_MODULES = ("os", "posix", "nt")
"""The modules that hold those names: `os` and its two platform halves."""

XAUTH = "XAUTHORITY"
"""The variable only `env.py` may build (rule (d))."""


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
    """True for a literal that is judged and falls in no hardware range."""
    if value < ADDRESS_FLOOR:
        return False
    return not any(lo <= value <= hi for _, lo, hi in HARDWARE_RANGES)


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
    c.module("audit", audit.self_check)
    check_rules(c)

    print("duckmcp_selftest: %d check(s) ran, %d failure(s)" % (c.ran, c.failed))
    return 0 if c.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
