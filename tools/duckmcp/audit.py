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
the root is not a directory. The gate of rule (b) is `selftest.py`, which
holds every site this finds against its `PENDING` list by `site_keys`: the
file, the category and the printed line, never the line number. `--keys`
prints those keys with their counts, in the shape `PENDING` takes.

Usage:
    python3 tools/duckmcp/audit.py [--root DIR] [--json | --keys]
"""

import argparse
import ast
import collections
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


def _import_re(home):
    """`_IMPORT_RE`, plus the forms qualified by the host project `home`:
    `import <home>.mcp`, `from <home>.mcp import x`, `from <home> import mcp`.

    The host has no `__init__.py`, so with `tools/` on `sys.path` it imports
    as a namespace package and reaches the same modules (CORR-DMCP-024).
    """
    if not home:
        return _IMPORT_RE
    mods, host = "|".join(MODULES), re.escape(home)
    return re.compile(r"^\s*(?:(?:import|from)\s+(?:%s\.)?(?:%s)\b"
                      r"|from\s+%s\s+import\s+.*\b(?:%s)\b)"
                      % (host, mods, host, mods))
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


def _imports_module(node, home=None):
    """Whether an import statement brings in one of the emulator modules,
    bare or qualified by the host project `home` (see `_import_re`)."""
    def names_one(dotted):
        parts = dotted.split(".")
        return parts[0] in MODULES or (
            home is not None and parts[0] == home and len(parts) > 1
            and parts[1] in MODULES)

    if isinstance(node, ast.Import):
        return any(names_one(a.name) for a in node.names)
    if isinstance(node, ast.ImportFrom):
        if node.level != 0 or not node.module:
            return False
        return names_one(node.module) or (
            home is not None and node.module == home
            and any(a.name in MODULES for a in node.names))
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


def _sites_ast(tree, source, lines, project, targets, own_module, is_module,
               home=None):
    sites = []
    bindings = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if not is_module and _imports_module(node, home):
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


def _sites_regex(lines, project, targets, own_module, is_module, home=None):
    sites = []
    import_re = _import_re(home)
    for i, line in enumerate(lines, 1):
        code = line.split("#", 1)[0]
        if not is_module and import_re.match(code):
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
            hit = any(_imports_module(n, home) for n in ast.walk(tree))
        else:
            hit = any(_import_re(home).match(l) for l in source.splitlines())
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
                               own_module, is_module, home)
        else:
            unparsed.append(os.path.relpath(path, base))
            found = _sites_regex(lines, project, targets, own_module,
                                 is_module, home)
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


def site_keys(doc):
    """`Counter` of `(file, category, snippet)` over the sites of `doc`.

    The key rule (b) holds the sites by: stable across edits that only move
    a site to another line.
    """
    return collections.Counter((s["file"], s["category"], s["snippet"])
                               for s in doc["sites"])


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
        expect("site_keys keys the planted site by file, category and line "
               "text, not line number",
               dict(site_keys(doc)),
               {("planted/proj/a.py", "import", "import fork"): 1})
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

        # the host imports as a namespace package: qualified forms count too
        qualified = dict(clean)
        forms = ("import emu.mcp\n"
                 "from emu import fork\n"
                 "from emu.savestate import read\n"
                 "import emu\n")
        qualified["other/q.py"] = forms
        qualified["other/r.py"] = forms + "def (:\n"
        tree = os.path.join(scratch, "qualified")
        _plant(tree, qualified)
        doc = audit(tree)
        expect("imports qualified by the host count, parsed or not "
               "(CORR-DMCP-024)",
               sorted((s["file"].rsplit("/", 1)[-1], s["line"])
                      for s in doc["sites"]),
               [("q.py", 1), ("q.py", 2), ("q.py", 3),
                ("r.py", 1), ("r.py", 2), ("r.py", 3)])

        # a file that does not parse falls back to the line regexes
        broken = dict(clean)
        broken["other/c.py"] = (
            "import fork\n"
            "import sys\n"
            "sys.path.insert(0, '../emu')\n"
            "client.call('pause')\n"
            "def (:\n")
        tree = os.path.join(scratch, "broken")
        _plant(tree, broken)
        doc = audit(tree)
        expect("a file that does not parse is listed as unparsed",
               [p.replace(os.sep, "/") for p in doc["unparsed"]],
               ["broken/other/c.py"])
        expect("the regex fallback counts one site of every category",
               doc["by_category"], {"import": 1, "client": 1, "sys.path": 1})
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=TOOLS_DIR,
                    help="the tools tree to walk (default: %(default)s)")
    out = ap.add_mutually_exclusive_group()
    out.add_argument("--json", action="store_true",
                     help="print the audit document as JSON")
    out.add_argument("--keys", action="store_true",
                     help="print each (file, category, snippet) key and its "
                          "count, as selftest.py's PENDING holds them")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.root):
        print("audit: %s is not a directory" % args.root, file=sys.stderr)
        return 2
    doc = audit(args.root)
    if args.json:
        print(json.dumps(doc, indent=2, sort_keys=False))
    elif args.keys:
        keys = site_keys(doc)
        for (path, category, snippet), count in sorted(keys.items()):
            print("(%r, %r,\n %r, %d)," % (path, category, snippet, count))
        print("audit: %d raw site(s) under %d key(s)"
              % (sum(keys.values()), len(keys)))
    else:
        print(render(doc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
