#!/usr/bin/env python3
"""The raw MCP sites left outside duckmcp, per project and per file.

The versioned probe of design rule (b) of PLAN-DUCKMCP-PY.md section 3.3.
It walks a tools tree (default: the `tools/` this file lives in), skipping
this package and every `__pycache__`, and reports three kinds of site:

- `import`: an `import mcp` / `from mcp import`, `import fork` /
  `from fork import`, `import savestate` / `from savestate import`,
  at module or function level. The three modules themselves are not
  sites -- they become shims -- but every other file of the project that
  hosts them is;
- `client`: a raw `client.call(` / `<x>.client.call(`, or a `Client(`
  construction, outside the module that defines `Client`;
- `sys.path`: a `sys.path.insert` whose target names another project that
  carries the emulator path -- the one hosting the three modules, or one
  that imports them -- resolved through the names the call uses (a loop
  over `("a", "b")`, a variable built from it).

Which project hosts the modules is **found**, not named: it is the
directory directly under the root holding `mcp.py`, `fork.py` and
`savestate.py`. The tool therefore holds no project name (rule (c)).

A project is the first path segment under the root; files directly under
it belong to `(top)`. Files that do not parse are scanned line by line with
regular expressions instead, and say so in the text output.

It is a probe, not a gate: it exits 0 whatever it counts, and 2 only when
the root is not a directory. The gate of rule (b) comes later.

Usage:
    python3 tools/duckmcp/audit.py [--root DIR] [--json]
"""

import argparse
import ast
import json
import os
import re
import sys
import tempfile

DUCKMCP_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(DUCKMCP_DIR)

MODULES = ("mcp", "fork", "savestate")
"""The emulator modules whose import outside them is a site."""

CLIENT_MODULE = "mcp"
"""The module that defines `Client`, where constructing one is not a site."""

TOP = "(top)"
"""The project name of files directly under the root."""

CATEGORIES = ("import", "client", "sys.path")
"""The kinds of site, in report order."""

SNIPPET = 90
"""How much of the source line a site prints."""

_IMPORT_RE = re.compile(r"^\s*(?:import|from)\s+(%s)\b" % "|".join(MODULES))
_CLIENT_RE = re.compile(r"(?<![\w.])(?:\w+\.)?client\.call\(|(?<![\w])Client\(")
_SYSPATH_RE = re.compile(r"sys\.path\.insert\(")


def project_of(root, path):
    """The first path segment of `path` under `root`, or `(top)`."""
    rel = os.path.relpath(path, root)
    parts = rel.split(os.sep)
    return parts[0] if len(parts) > 1 else TOP


def python_files(root):
    """Every `.py` under `root`, outside this package and `__pycache__`."""
    skip = os.path.normcase(os.path.realpath(os.path.join(root, "duckmcp")))
    out = []
    for here, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__"
                         and os.path.normcase(os.path.realpath(
                             os.path.join(here, d))) != skip)
        for name in sorted(files):
            if name.endswith(".py"):
                out.append(os.path.join(here, name))
    return out


def find_home(root):
    """The project directly under `root` that holds the three modules."""
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if os.path.isdir(d) and all(
                os.path.isfile(os.path.join(d, m + ".py")) for m in MODULES):
            return name
    return None


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _snippet(lines, lineno):
    text = " ".join(lines[lineno - 1].split()) \
        if 0 < lineno <= len(lines) else ""
    return text if len(text) <= SNIPPET else text[:SNIPPET - 3] + "..."


def _imports_module(node):
    """Whether an import statement brings in one of the emulator modules."""
    if isinstance(node, ast.Import):
        return any(a.name.split(".")[0] in MODULES for a in node.names)
    if isinstance(node, ast.ImportFrom):
        return node.level == 0 and bool(node.module) and \
            node.module.split(".")[0] in MODULES
    return False


def _is_client_call(node):
    """`client.call(...)`, `<x>.client.call(...)` or `Client(...)`."""
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr == "call":
        value = func.value
        return (isinstance(value, ast.Name) and value.id == "client") or \
            (isinstance(value, ast.Attribute) and value.attr == "client")
    if isinstance(func, ast.Name):
        return func.id == "Client"
    if isinstance(func, ast.Attribute):
        return func.attr == "Client"
    return False


def _is_syspath_insert(node):
    func = node.func
    return isinstance(func, ast.Attribute) and func.attr == "insert" and \
        isinstance(func.value, ast.Attribute) and func.value.attr == "path" \
        and isinstance(func.value.value, ast.Name) and \
        func.value.value.id == "sys"


def _bindings(tree, source):
    """Name -> the source text of every expression that binds it."""
    out = {}

    def add(target, value):
        # Only names bound as a whole: `os.environ[k] = v` binds nothing.
        if isinstance(target, ast.Name):
            out.setdefault(target.id, []).append(value)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for t in target.elts:
                add(t, value)
        elif isinstance(target, ast.Starred):
            add(target.value, value)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                add(t, node.value)
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)) and node.value:
            add(node.target, node.value)
        elif isinstance(node, (ast.For, ast.comprehension)):
            add(node.target, node.iter)
    return out


def _resolved_text(expr, bindings, source, depth=6):
    """The source of `expr` plus, transitively, what its names are bound to."""
    seen = set()
    texts = []

    def visit(e, d):
        texts.append(ast.get_source_segment(source, e) or "")
        if d == 0:
            return
        for n in ast.walk(e):
            if isinstance(n, ast.Name) and n.id not in seen:
                seen.add(n.id)
                for value in bindings.get(n.id, ()):
                    visit(value, d - 1)

    visit(expr, depth)
    return "\n".join(texts)


def _names_project(text, projects):
    """The projects in `projects` that `text` names as a whole token."""
    return sorted(p for p in projects if re.search(
        r"(?i)(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(p), text))


def _sites_ast(tree, source, lines, project, targets, own_module, is_module):
    sites = []
    bindings = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if not is_module and _imports_module(node):
                sites.append((node.lineno, "import"))
        elif isinstance(node, ast.Call):
            if _is_client_call(node):
                if own_module != CLIENT_MODULE:
                    sites.append((node.lineno, "client"))
            elif _is_syspath_insert(node) and len(node.args) >= 2:
                if bindings is None:
                    bindings = _bindings(tree, source)
                text = _resolved_text(node.args[1], bindings, source)
                if _names_project(text, targets - {project}):
                    sites.append((node.lineno, "sys.path"))
    return sites


def _sites_regex(lines, project, targets, own_module, is_module):
    sites = []
    for i, line in enumerate(lines, 1):
        code = line.split("#", 1)[0]
        if not is_module and _IMPORT_RE.match(code):
            sites.append((i, "import"))
        if own_module != CLIENT_MODULE:
            for _ in _CLIENT_RE.finditer(code):
                sites.append((i, "client"))
        if _SYSPATH_RE.search(code) and \
                _names_project(code, targets - {project}):
            sites.append((i, "sys.path"))
    return sites


def audit(root=None):
    """The audit document: every site, and the totals per project."""
    root = os.path.abspath(root or TOOLS_DIR)
    base = os.path.dirname(root)
    home = find_home(root)
    files = python_files(root)

    parsed = {}
    for path in files:
        source = _read(path)
        try:
            tree = ast.parse(source, filename=path)
        except (SyntaxError, ValueError):
            tree = None
        parsed[path] = (source, tree)

    # A project carries the emulator path if it hosts the modules or imports
    # them; inserting one of those from elsewhere is a sys.path site.
    targets = {home} if home else set()
    for path, (source, tree) in parsed.items():
        project = project_of(root, path)
        if project in targets or project == TOP:
            continue
        if tree is not None:
            hit = any(_imports_module(n) for n in ast.walk(tree))
        else:
            hit = any(_IMPORT_RE.match(l) for l in source.splitlines())
        if hit:
            targets.add(project)

    sites = []
    unparsed = []
    for path in files:
        source, tree = parsed[path]
        lines = source.splitlines()
        project = project_of(root, path)
        in_home = home is not None and project == home and \
            os.path.dirname(path) == os.path.join(root, home)
        stem = os.path.splitext(os.path.basename(path))[0]
        own_module = stem if in_home else None
        is_module = own_module in MODULES
        if tree is not None:
            found = _sites_ast(tree, source, lines, project, targets,
                               own_module, is_module)
        else:
            unparsed.append(os.path.relpath(path, base))
            found = _sites_regex(lines, project, targets, own_module,
                                 is_module)
        for lineno, category in sorted(found):
            sites.append({
                "project": project,
                "file": os.path.relpath(path, base).replace(os.sep, "/"),
                "line": lineno,
                "category": category,
                "snippet": _snippet(lines, lineno),
            })

    per_project = {}
    for s in sites:
        p = per_project.setdefault(s["project"], {
            "sites": 0, "files": set(),
            "by_category": {c: 0 for c in CATEGORIES}})
        p["sites"] += 1
        p["files"].add(s["file"])
        p["by_category"][s["category"]] += 1
    for p in per_project.values():
        p["files"] = len(p["files"])

    return {
        "root": root,
        "home": home,
        "carriers": sorted(targets),
        "files_scanned": len(files),
        "unparsed": unparsed,
        "sites": sites,
        "per_project": dict(sorted(per_project.items())),
        "by_category": {c: sum(1 for s in sites if s["category"] == c)
                        for c in CATEGORIES},
        "files": len({s["file"] for s in sites}),
        "total": len(sites),
    }


def render(doc):
    """The text report; its last line is the fixed-form total."""
    out = ["audit: root %s, %d file(s) scanned, modules hosted by %s"
           % (doc["root"], doc["files_scanned"], doc["home"] or "nobody")]
    for path in doc["unparsed"]:
        out.append("audit: %s did not parse, scanned by regex" % path)
    project = current = None
    for s in doc["sites"]:
        if s["project"] != project:
            project = s["project"]
            out.append("")
            out.append("[%s]" % project)
            current = None
        if s["file"] != current:
            current = s["file"]
        out.append("%s:%d: %s: %s"
                   % (s["file"], s["line"], s["category"], s["snippet"]))
    out.append("")
    for name, p in doc["per_project"].items():
        out.append("%s: %d site(s) in %d file(s) (%s)" % (
            name, p["sites"], p["files"],
            ", ".join("%s %d" % (c, p["by_category"][c])
                      for c in CATEGORIES)))
    out.append("by category: %s" % ", ".join(
        "%s %d" % (c, doc["by_category"][c]) for c in CATEGORIES))
    out.append("audit: %d raw site(s) in %d file(s)"
               % (doc["total"], doc["files"]))
    return "\n".join(out)


def _plant(root, files):
    for rel, text in files.items():
        path = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)


def self_check(root=None) -> list:
    """The audit over synthetic trees: clean counts 0, one `import fork` 1.

    `root` is a scratch directory to build the trees in; without it a
    temporary one is made and removed. Returns one `(name, passed, detail)`
    per assertion.
    """
    results = []

    def expect(what, got, want):
        results.append((what, got == want, "got %r, want %r" % (got, want)))

    with tempfile.TemporaryDirectory(dir=root) as scratch:
        clean = {
            # the modules themselves import each other: not sites
            "emu/mcp.py": "import fork\nclass Client:\n    pass\n"
                          "def f():\n    return Client()\n",
            "emu/fork.py": "from mcp import Client\n",
            "emu/savestate.py": "import os\n",
            # a subscript assignment binds no name: `os` stays unresolved
            "proj/a.py": "import os\nimport sys\nos.environ['K'] = 'emu'\n"
                         "sys.path.insert(0, os.path.dirname(__file__))\n",
            "duckmcp/x.py": "import fork\n",  # this package is skipped
            "proj/__pycache__/b.py": "import fork\n",  # skipped too
        }
        tree = os.path.join(scratch, "clean")
        _plant(tree, clean)
        doc = audit(tree)
        expect("audit finds the module home of a synthetic tree",
               doc["home"], "emu")
        expect("audit counts 0 sites in a clean synthetic tree",
               doc["total"], 0)

        planted = dict(clean)
        planted["proj/a.py"] = clean["proj/a.py"] + "import fork\n"
        tree = os.path.join(scratch, "planted")
        _plant(tree, planted)
        doc = audit(tree)
        expect("audit counts 1 site for one planted `import fork`",
               doc["total"], 1)
        expect("the planted site is an import in proj/a.py line 5",
               [(s["category"], s["file"], s["line"]) for s in doc["sites"]],
               [("import", "planted/proj/a.py", 5)])
        expect("the text report ends in the fixed-form total",
               render(doc).splitlines()[-1],
               "audit: 1 raw site(s) in 1 file(s)")

        each = dict(clean)
        each["other/b.py"] = (
            "import os, sys\n"
            "for _s in ('emu',):\n"
            "    _p = os.path.join('..', _s)\n"
            "    sys.path.insert(0, _p)\n"
            "def g(game, client):\n"
            "    from savestate import read\n"
            "    client.call('pause')\n"
            "    game.client.call('pause')\n"
            "    return Client()\n")
        tree = os.path.join(scratch, "each")
        _plant(tree, each)
        doc = audit(tree)
        expect("one site of every category, inline import and resolved "
               "sys.path target included",
               doc["by_category"], {"import": 1, "client": 3, "sys.path": 1})
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=TOOLS_DIR,
                    help="the tools tree to walk (default: %(default)s)")
    ap.add_argument("--json", action="store_true",
                    help="print the audit document as JSON")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.root):
        print("audit: %s is not a directory" % args.root, file=sys.stderr)
        return 2
    doc = audit(args.root)
    if args.json:
        print(json.dumps(doc, indent=2, sort_keys=False))
    else:
        print(render(doc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
