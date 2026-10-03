#!/usr/bin/env python3
"""The kits gates: `kits_selftest` (needs nothing) and `kits_image` (needs a disc).

`kits_selftest` runs with no image, no venv and no display, and never skips
its way to green.  In this order:

1. the self-check of every `tools/looks/` module the kits code imports
   (PLAN-KITS-PY.md section 6, coupling) -- the list is derived from the
   imports, so a new import is covered without anyone remembering it;
2. the core read on a container built here, in memory: the guard of form,
   each of its refusals, the header extent, the Form 2 tail and the ISO
   size, and control 4 of section 5 (one byte of an LZSS stream);
3. the rules of section 3.1 on `tools/kits/core/`: no print, no exit, no Qt;
4. the negative controls of `controls.py`, each planted in a copy of the
   tree and each required to turn this gate red (skipped by --no-plant,
   which is how `controls.py` itself runs it).

`kits_image` (--image) reads the disc in WE2002_LOOKS_IMAGE through the
facade and exits 77 without it: every kit passes the guard, the stream
control holds on a real kit, and the recognition fixtures of `cli.py open
--negative` give what they have to.

Usage:
    python tools/kits/selftest.py [--quiet] [--no-plant]
    python tools/kits/selftest.py --image [--quiet]
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import io
import os
import re
import subprocess
import struct
import sys
import tempfile
import tokenize

KITS_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(KITS_DIR)
LOOKS_DIR = os.path.join(TOOLS_DIR, "looks")
CORE_DIR = os.path.join(KITS_DIR, "core")
sys.path.insert(0, KITS_DIR)

from core import api  # noqa: E402
from core import source, tex, zones  # noqa: E402  (internals under test; tex puts pes2/looks on the path)

import harness  # noqa: E402  (tools/looks)
import iso  # noqa: E402  (tools/pes2)
import lzss  # noqa: E402

SKIP = 77
IMAGE_VARIABLE = "WE2002_LOOKS_IMAGE"

# -- 1. the looks modules the kits code imports ----------------------------

_IMPORT = re.compile(r"^\s*(?:import\s+(\w+)|from\s+(\w+)\s+import\b)", re.MULTILINE)


def _kits_sources() -> list:
    out = []
    for root, dirs, files in os.walk(KITS_DIR):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        out += [os.path.join(root, f) for f in files if f.endswith(".py")]
    return sorted(out)


def _imported_names(path: str) -> set:
    """Every module name an `import`/`from ... import` line of *path* names,
    indented ones (imports inside a function) included."""
    with open(path, encoding="utf-8") as fh:
        return {m.group(1) or m.group(2) for m in _IMPORT.finditer(fh.read())}


def _looks_path(name: str) -> str:
    return os.path.join(LOOKS_DIR, name + ".py")


def looks_modules_reached() -> list:
    """Names of every `tools/looks/*.py` the kits code reaches: imported by
    kits code, or by a looks module so reached -- the transitive closure,
    since a break two imports away breaks the kits all the same."""
    names = set()
    for path in _kits_sources():
        names |= _imported_names(path)
    # A kits module of the same name as a looks one (cli) is the kits one.
    names -= {os.path.splitext(os.path.basename(p))[0] for p in _kits_sources()}
    todo = sorted(n for n in names if os.path.isfile(_looks_path(n)))
    seen = set()
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        todo += [n for n in _imported_names(_looks_path(name))
                 if n not in seen and os.path.isfile(_looks_path(n))]
    return sorted(seen)


def looks_modules_imported() -> list:
    """Names of the reached `tools/looks/*.py` (`looks_modules_reached`) that
    have a self_check."""
    out = []
    for name in looks_modules_reached():
        with open(_looks_path(name), encoding="utf-8") as fh:
            if "def self_check(" in fh.read():
                out.append(name)
    return out


def _looks_checks(c) -> None:
    names = c.attempt("derive the looks modules from the imports", looks_modules_imported,
                      default=[])
    c.ok("the kits code imports at least one looks module", bool(names))
    c.ok("layout is among them (the kit file names live there)", "layout" in names,
         "found %s" % names)
    for name in names:
        module = c.attempt("import %s" % name, lambda n=name: importlib.import_module(n))
        if module is None:
            continue
        fn = module.self_check
        call = (lambda: fn(verbose=False)) if "verbose" in fn.__code__.co_varnames else fn
        outcome = c.attempt("looks %s.self_check()" % name, call, default="raised")
        if outcome != "raised":
            c.ok("looks %s.self_check() reports no failure" % name, not outcome,
                 "failures=%s" % outcome)
    print("  ..... %d looks self-check(s): %s" % (len(names), ", ".join(names)))


# -- 2. the core on a container built here ---------------------------------
#
# The rectangles are written out again on purpose, not taken from
# tex.EXPECTED_SHAPE: a fixture built from the table under test agrees with
# it whatever the table says.

KIND_IMAGE, KIND_CLUT = 0x0A, 0x09
FIXTURE_RECORDS = (
    (KIND_IMAGE, 576, 256, 64, 128), (KIND_IMAGE, 576, 384, 64, 128),
    (KIND_CLUT, 0, 486, 256, 1), (KIND_CLUT, 0, 488, 256, 1),
    (KIND_IMAGE, 576, 256, 64, 128), (KIND_IMAGE, 576, 384, 64, 128),
    (KIND_CLUT, 0, 486, 256, 1), (KIND_CLUT, 0, 488, 256, 1),
    (KIND_IMAGE, 704, 256, 64, 64), (KIND_CLUT, 256, 480, 256, 1),
    (KIND_IMAGE, 768, 384, 64, 128),
)
FIXTURE_PLAIN = {0: 16384, 1: 16384, 4: 16384, 5: 16384, 8: 16384, 10: 16384}
"""Bytes each image decompresses to; the flag (8) holds twice its 64x64."""

HEADER_WORDS = 12
TAG = 0x800F
END = 0x00FF


def _plain(record: int, size: int) -> bytes:
    return bytes((i * (record + 3) + (i >> 7)) & 0xFF for i in range(size))


def build_container(records=FIXTURE_RECORDS, sizes=None, short_by=None) -> bytes:
    """A kit container: header, the streams and palettes, one record list.

    *sizes* overrides how many bytes an image stream decompresses to;
    *short_by* drops that many records from the end of the list."""
    sizes = {**FIXTURE_PLAIN, **(sizes or {})}
    body = bytearray(HEADER_WORDS * 4)
    offsets = []
    for i, (kind, _x, _y, w, _h) in enumerate(records):
        offsets.append(len(body))
        if kind == KIND_IMAGE:
            body += lzss.compress(_plain(i, sizes[i]))
        else:
            body += bytes((i + j) & 0x7F for j in range(w * 2))
        body += bytes(-len(body) % 4)
    listed = records[:len(records) - (short_by or 0)]
    list_at = len(body)
    for (kind, x, y, w, h), off in zip(listed, offsets):
        body += struct.pack("<8H", kind, x, y, w, h, 0, off, TAG)
    body += struct.pack("<H", END)
    struct.pack_into("<HH", body, 0, list_at, TAG)
    return bytes(body)


def _fake_disc(data: bytes, form2_at=(), tail_byte=None, iso_size=None, next_lba=None):
    """An `iso.Image` over sectors built here: the kit at LBA 0.

    *form2_at* are kit sectors whose subheader says Form 2; *tail_byte*
    puts a non-zero byte in their Form 2 tail; *iso_size* is the size the
    directory declares; *next_lba* places another file."""
    sectors = -(-len(data) // iso.FORM1_DATA)
    raw = bytearray()
    for i in range(sectors + 4):
        sector = bytearray(iso.RAW_SECTOR)
        if i in form2_at:
            sector[18] = iso.SUBMODE_FORM2
            if tail_byte is not None:
                sector[2100] = tail_byte
        chunk = data[i * iso.FORM1_DATA:(i + 1) * iso.FORM1_DATA]
        sector[iso.HEADER:iso.HEADER + len(chunk)] = chunk
        raw += sector
    image = iso.Image.__new__(iso.Image)
    image.path = "<fixture disc>"
    image.f = io.BytesIO(bytes(raw))
    image.sector_count = sectors + 4
    image.files = {"/BIN/TEX_00.BIN": iso.Entry("/BIN/TEX_00.BIN", 0,
                                                iso_size if iso_size else len(data))}
    image.files["/NEXT.BIN"] = iso.Entry("/NEXT.BIN", next_lba or sectors + 4, 1)
    return image


def _core_checks(c) -> None:
    ok = c.ok
    data = build_container()

    kit = tex.read_kit(data, "fixture")
    ok("a well-formed container passes the guard", kit.ok, "; ".join(kit.problems))
    ok("it gives 6 images and 5 palettes", (len(kit.images), len(kit.palettes)) == (6, 5),
       "%d images, %d palettes" % (len(kit.images), len(kit.palettes)))
    ok("the images are named, in file order",
       [i.name for i in kit.images] == [tex.RECORD_NAMES[r] for r in (0, 1, 4, 5, 8, 10)])
    flag = [i for i in kit.images if i.record == 8]
    ok("the flag is 128x64, its filler half dropped",
       bool(flag) and (flag[0].width, flag[0].height, len(flag[0].indices)) == (128, 64, 8192))
    ok("the uniform is the bytes that went in",
       bool(kit.images) and kit.images[0].indices == _plain(0, 16384))
    ok("the header extent is the end of the record list",
       tex.declared_extent(data) == len(data),
       "%s for %d bytes" % (tex.declared_extent(data), len(data)))

    def problems(d):
        return tex.read_kit(d, "fixture").problems

    # api.figure (KITS-TASK-24): no geometry is a sentence, not a traceback, and
    # the 486/488 swap of control 4 moves exactly the two palettes of the set.
    saved = os.environ.pop(IMAGE_VARIABLE, None)
    try:
        c.refuses("with no geometry disc, api.figure says why",
                  lambda: api.figure(kit, 1, 0), "needs the Japanese disc", kind=api.NoGeometry)
    finally:
        if saved is not None:
            os.environ[IMAGE_VARIABLE] = saved
    from core import figure as _figure
    import texture as _texture
    for kit_set in (1, 2):
        held = _texture.in_set_order(_texture.palettes(data), kit_set)
        player = next(r for r in held if r.y == _figure.PLAYER_ROW)
        keeper = next(r for r in held if r.y == _figure.KEEPER_ROW)
        size = player.colours * 2
        swapped = _figure.swapped_palettes(data, kit_set)
        moved = [i for i in range(len(data)) if data[i] != swapped[i]]
        ok("set %d: the swap puts 488 where 486 was and 486 where 488 was, and touches "
           "nothing else" % kit_set,
           swapped[player.offset:player.offset + size] == data[keeper.offset:keeper.offset + size]
           and swapped[keeper.offset:keeper.offset + size] == data[player.offset:player.offset + size]
           and all(player.offset <= i < player.offset + size
                   or keeper.offset <= i < keeper.offset + size for i in moved)
           and bool(moved), "%d byte(s) moved" % len(moved))

    p = problems(build_container(short_by=1))
    ok("a missing record is refused by count",
       len(p) == 1 and "has 10 image/palette records" in p[0], p)
    moved = list(FIXTURE_RECORDS)
    moved[10] = (KIND_IMAGE, 768, 385, 64, 128)
    p = problems(build_container(records=tuple(moved)))
    ok("a moved rectangle is refused by record",
       len(p) == 1 and p[0].startswith("record 10 is image at (768,385)"), p)
    p = problems(build_container(sizes={1: 16383}))
    ok("a stream one byte short is refused on its record",
       len(p) == 1 and p[0].startswith("record 1 (sleeves, first set) decompresses to 16383"), p)
    p = problems(build_container(sizes={8: 8192}))
    ok("a flag stream of only its rectangle is refused (it holds twice that)",
       len(p) == 1 and p[0].startswith("record 8 (flag) decompresses to 8192"), p)
    cut = data[:len(data) - 600]          # the record list is in the last 600 bytes
    p = problems(cut)
    ok("a cut container is refused, not read short", bool(p), "no problem for %d bytes" % len(cut))

    sc = tex.stream_control(data, "fixture")
    ok("section 5 control 4: one byte of record 0's stream changed is refused on record 0",
       sc.ok, "clean=%s planted=%s" % (sc.clean.problems, sc.planted.problems))

    # The disc rules of source.read_disc_file, on sectors built here.
    last = -(-len(data) // iso.FORM1_DATA) - 1
    got, notes = source.read_disc_file(_fake_disc(data, form2_at=(last,)), "/BIN/TEX_00.BIN")
    kinds = [n.kind for n in notes]
    ok("a sector marked Form 2 with a zero tail is read as Form 1, and noted",
       got == data and kinds == [tex.NOTE_FORM2_TAIL], kinds)
    c.refuses("a sector marked Form 2 with data in its tail is refused",
              lambda: source.read_disc_file(_fake_disc(data, form2_at=(last,), tail_byte=0x55),
                                            "/BIN/TEX_00.BIN"),
              "is Form 2 with data past byte 2048", kind=api.KitUnreadable)
    short = (last - 1) * iso.FORM1_DATA
    got, notes = source.read_disc_file(_fake_disc(data, iso_size=short), "/BIN/TEX_00.BIN")
    ok("an ISO size short of the header's end is read past, and noted",
       got == data and [n.kind for n in notes] == [tex.NOTE_PAST_ISO_SIZE],
       [n.kind for n in notes])
    got, notes = source.read_disc_file(_fake_disc(data, iso_size=short), "/BIN/TEX_00.BIN",
                                       trust_iso_size=True)
    ok("--iso-size reads only the ISO size", len(got) == short and not notes)
    got, notes = source.read_disc_file(_fake_disc(data, iso_size=short, next_lba=last - 1),
                                       "/BIN/TEX_00.BIN")
    ok("a file starting at the ISO end stops the read there",
       len(got) == short and not notes, "%d bytes, %s" % (len(got), notes))

    # The zone map (section 4.6): its invariants, and where built rects fall.
    bad = zones.self_check()
    ok("zones.self_check() reports no failure", not bad, "; ".join(bad))
    front = api.zone_at(15, 10)
    ok("zone_at names the shirt front at (15,10) and nothing at (50,60)",
       front is not None and front.name == "shirt front" and api.zone_at(50, 60) is None)
    m = api.measure

    def placed(rect):
        r = m.UvRect(file="f", section=0, primitive=0, role="uniform", rect=rect, outside="")
        rep = m.UvReport(source="", kit="", tuple_text="",
                         figures=(m.FigureUv(figure=0, rects=(r,)),))
        return api.confront_zones(rep).placed[0].klass

    got = (placed((13, 9, 14, 10)), placed((10, 9, 13, 10)), placed((2, 81, 4, 83)),
           placed((48, 57, 49, 58)))
    ok("a rect falls in one zone, across two, in a gap, or outside the map",
       got == zones.CLASSES, got)

    # The other three ways section 4.6 fails (CORR-KITS-031), on a map of
    # four rows built here: a quiet zone with no reason, an excused zone that
    # is sampled, and a gap nobody samples.
    quiet = zones.Zone("quiet", 0, 10, 0, 4, 4, "selftest")
    excused = zones.Zone("excused", 0, 20, 0, 4, 4, "selftest", "planted reason")
    mini = (zones.Zone("sampled", 0, 0, 0, 4, 4, "selftest"), quiet, excused)
    gap = zones.Gap("unused", 0, 30, 0, 2, 2, "planted")
    rects = tuple(m.UvRect(file="f", section=0, primitive=i, role="uniform", rect=r, outside="")
                  for i, r in enumerate(((0, 0, 1, 1), (20, 0, 21, 1))))
    con = zones.confront(m.UvReport(source="", kit="", tuple_text="",
                                    figures=(m.FigureUv(figure=0, rects=rects),)),
                         mini, (gap,))
    ok("a zone nobody samples, with no reason, fails section 4.6",
       con.unsampled_unexplained == (quiet,), con.unsampled_unexplained)
    ok("a zone excused from sampling, and sampled, fails section 4.6",
       con.sampled_but_excused == (excused,), con.sampled_but_excused)
    ok("a declared gap nobody samples fails section 4.6",
       con.gaps_unused == (gap,), con.gaps_unused)
    ok("and the verdict says so", not con.ok)


# -- 3. the rules of section 3.1 on the core -------------------------------

FORBIDDEN_CALLS = ("print", "exit", "input")
FORBIDDEN_IMPORTS = ("PySide6", "PySide2", "PyQt5", "PyQt6")


def core_rule_breaks() -> list:
    """(file, line, what) for every print/exit/input call and Qt import in core/."""
    out = []
    for name in sorted(os.listdir(CORE_DIR)):
        if not name.endswith(".py"):
            continue
        path = os.path.join(CORE_DIR, name)
        with open(path, "rb") as fh:
            tokens = list(tokenize.tokenize(fh.readline))
        for a, b in zip(tokens, tokens[1:]):
            if a.type == tokenize.NAME and a.string in FORBIDDEN_CALLS and b.string == "(":
                out.append((name, a.start[0], a.string + "()"))
            if a.type == tokenize.NAME and a.string in FORBIDDEN_IMPORTS:
                out.append((name, a.start[0], a.string))
    return out


FACADE_CLIENTS = ("cli.py", "confront.py")
"""Files of tools/kits that may import nothing of the core but `core.api`
(section 3.1)."""
UI_DIR = "ui"
UI_TOOLKIT = "PySide6"
"""The window's files are facade clients too, and the only ones that may
import the toolkit."""


def ui_clients() -> tuple:
    folder = os.path.join(KITS_DIR, UI_DIR)
    if not os.path.isdir(folder):
        return ()
    return tuple(UI_DIR + "/" + n for n in sorted(os.listdir(folder)) if n.endswith(".py"))


def facade_breaks(clients=FACADE_CLIENTS, allowed=()) -> list:
    """(file, line, module) for every import in *clients* that is neither
    the standard library, `core.api` nor a top-level module in *allowed*."""
    import ast

    out = []
    for name in clients:
        path = os.path.join(KITS_DIR, name)
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level or node.module is None:
                    mods = ["." * node.level + (node.module or "")]
                elif node.module == "core":
                    mods = ["core." + a.name for a in node.names]
                else:
                    mods = [node.module]
            else:
                continue
            for mod in mods:
                top = mod.split(".")[0]
                if (mod == "core.api" or top == "__future__" or top in allowed
                        or (top and top in sys.stdlib_module_names)):
                    continue
                out.append((name, node.lineno, mod))
    return out


UI_APP = UI_DIR + "/app.py"
UI_CATALOG = UI_DIR + "/i18n.py"
NOT_SHOWN_CALLS = ("tr", "print", "add_argument", "ArgumentParser", "ArgumentTypeError",
                   "RuntimeError", "setStyle", "save", "getattr", "QColor")
"""Calls whose string arguments are not window text: the catalog lookup itself,
the headless stdout and argparse messages, the style's name, the PNG format,
QPalette role names and colours (section 3.4, KITS-TASK-36)."""
NOT_SHOWN_CONSTANTS = ("WORK", "COLOURS", "DISABLED_TEXT", "DISABLED_ROLES", "CHECKER",
                       "BACKDROP", "ZONE_PEN", "GAP_PEN", "FONT_FAMILIES", "CORE_TEXT")
"""Module constants of ui/app.py that hold keys, colours and font families."""
_FORMAT_SPEC = re.compile(r"%[-#0 +]*\d*(?:\.\d+)?[a-zA-Z%]|\{[^{}]*\}")


def _shows_words(text: str) -> bool:
    return any(ch.isalpha() for ch in _FORMAT_SPEC.sub("", text))


def visible_literals(source: str, name: str = UI_APP) -> list:
    """(line, text) of every string literal in *source* that reaches the screen
    without passing through `tr(...)`.  Not window text: a bare string statement
    (a docstring), a dunder name, a dict key (a field name), the catalog key a
    `say(...)` names, the arguments of `NOT_SHOWN_CALLS`, and the module
    constants in `NOT_SHOWN_CONSTANTS`.  Anything else with a letter in it,
    format specifiers aside, is."""
    import ast

    tree = ast.parse(source, name)
    skip = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            skip.add(id(node.value))
        if isinstance(node, ast.Dict):
            skip.update(id(k) for k in node.keys if k is not None)
        if isinstance(node, ast.Call):
            func = node.func
            called = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if called in NOT_SHOWN_CALLS:
                for arg in list(node.args) + [k.value for k in node.keywords]:
                    skip.update(id(n) for n in ast.walk(arg))
            if called == "say" and node.args:
                skip.update(id(n) for n in ast.walk(node.args[0]))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if all(isinstance(t, ast.Name) and t.id in NOT_SHOWN_CONSTANTS for t in targets):
                skip.update(id(n) for n in ast.walk(node))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                and id(node) not in skip and _shows_words(node.value) \
                and not re.fullmatch(r"__\w+__", node.value):
            out.append((node.lineno, node.value))
    return sorted(out)


def catalog_keys_used(source: str) -> set:
    """The literal keys `tr(...)` and `say(...)` are called with, and the keys
    of the `labels` dict the window fills its selector labels from."""
    import ast

    out = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and node.args:
            func = node.func
            called = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if called in ("tr", "say"):
                out.update(n.value for n in ast.walk(node.args[0])
                           if isinstance(n, ast.Constant) and isinstance(n.value, str))
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Attribute) and t.attr == "labels"
                                                for t in node.targets) \
                and isinstance(node.value, ast.Dict):
            out.update(k.value for k in node.value.keys if isinstance(k, ast.Constant))
    return out


def _catalog():
    """ui/i18n.py, by path: standard library only, so no venv is needed."""
    spec = importlib.util.spec_from_file_location("kits_ui_i18n",
                                                  os.path.join(KITS_DIR, UI_CATALOG))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _language_checks(c) -> None:
    catalog = c.attempt("import ui/i18n.py", _catalog)
    if catalog is not None:
        c.ok("the window speaks %s by default" % catalog.DEFAULT, catalog.DEFAULT == "en-US")
        bad = catalog.problems()
        c.ok("en-US and pt-BR have the same keys and the same fields", bad == [], "%s" % bad)
        print("  ..... %d language(s), %d key(s) each: %s"
              % (len(catalog.LANGUAGES), len(catalog.CATALOG[catalog.DEFAULT]),
                 ", ".join(catalog.LANGUAGES)))
        bad = catalog.self_check()
        c.ok("ui/i18n.py's own self-check", bad == [], "%s" % bad)
    with open(os.path.join(KITS_DIR, UI_APP), encoding="utf-8") as fh:
        found = c.attempt("sweep ui/app.py for window text", lambda: visible_literals(fh.read()),
                          default=None)
    c.ok("ui/app.py shows no text outside tr()", found == [], "%s" % found)
    if catalog is not None:
        with open(os.path.join(KITS_DIR, UI_APP), encoding="utf-8") as fh:
            keys = catalog_keys_used(fh.read())
        missing = sorted(k for k in keys if k not in catalog.CATALOG[catalog.DEFAULT])
        c.ok("every key ui/app.py asks for is in the catalog (%d used)" % len(keys),
             bool(keys) and missing == [], "%s" % missing)
    planted = visible_literals(
        'def f(w):\n    """A docstring."""\n    w.setText("Abrir")\n'
        '    w.setText(tr("open"))\n    print("headless")\n    w.setText("%d×" % 3)\n')
    c.ok("and the sweep finds a planted literal, and only it", planted == [(3, "Abrir")],
         "%s" % planted)


SCENE_BRIDGE = "figure.py"
SCENE_MODULES = ("scene",)
"""The looks modules that draw the figure.  Only `core/figure.py` may import
them (section 3.1): the rest of the core reaches `layout` for addresses and
`survey.py` runs the phase-0 probes, but none of them asks for a scene."""


def scene_importers(folder: str = CORE_DIR) -> list:
    """Files of *folder* that import a module of `SCENE_MODULES`."""
    out = []
    for name in sorted(os.listdir(folder)):
        if name.endswith(".py") and _imported_names(os.path.join(folder, name)) & set(SCENE_MODULES):
            out.append(name)
    return out


def _rule_checks(c) -> None:
    importers = c.attempt("sweep core/ for the scene", scene_importers, default=None)
    c.ok("only core/figure.py imports the looks scene (section 3.1)",
         importers == [SCENE_BRIDGE], "%s" % importers)
    breaks = c.attempt("sweep tools/kits/core", core_rule_breaks, default=None)
    c.ok("core/ has no print, exit, input or Qt (section 3.1)", breaks == [],
         "%s" % breaks)
    breaks = c.attempt("sweep the facade clients", facade_breaks, default=None)
    c.ok("cli.py and confront.py import only core.api and the standard library "
         "(section 3.1)",
         breaks == [], "%s" % breaks)
    clients = ui_clients()
    own = tuple(n.split("/")[-1][:-3] for n in clients)
    breaks = c.attempt("sweep the window",
                       lambda: facade_breaks(clients, (UI_TOOLKIT,) + own), default=None)
    c.ok("ui/ imports only PySide6, core.api, its own modules and the standard library "
         "(section 3.1)",
         bool(clients) and breaks == [], "%s in %s" % (breaks, clients))


# -- 4. the negative controls ----------------------------------------------

def _kits_module(name: str):
    """tools/kits/<name>.py, by path: `import controls` or `import confront`
    finds the looks one, which `tex` put first on sys.path."""
    spec = importlib.util.spec_from_file_location("kits_" + name,
                                                  os.path.join(KITS_DIR, name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module           # dataclasses look the module up
    spec.loader.exec_module(module)
    return module


def _kits_controls():
    return _kits_module("controls")


# -- confront 2's reader, on a pair built here -----------------------------

def build_tim(pixels: bytes, w: int, h: int, x: int = 960, y: int = 0) -> bytes:
    """An 8-bit TIM with a 256-colour CLUT block, written out here."""
    clut = struct.pack("<IHHHH", 12 + 512, 0, 480, 256, 1) + bytes(512)
    image = struct.pack("<IHHHH", 12 + len(pixels), x, y, w, h) + pixels
    return struct.pack("<II", 0x10, 0x09) + clut + image


def _confront2_checks(c) -> None:
    confront = c.attempt("import tools/kits/confront.py", lambda: _kits_module("confront"))
    if confront is None:
        return
    pixels = _plain(0, 64 * 128 * 2)
    tim = build_tim(pixels, 64, 128)
    stream = lzss.compress(pixels)
    r = confront.compare_pair(stream, tim, "fixture")
    c.ok("confront 2: a .bin compressed from the .tim's pixels matches", r.ok,
         "%s %s" % (r.status, r.detail))
    flipped = bytearray(tim)
    flipped[len(tim) - len(pixels) + 1000] ^= 1
    r = confront.compare_pair(stream, bytes(flipped), "fixture")
    c.ok("confront 2: one pixel changed in the .tim is a mismatch at that pixel",
         r.status == "differ" and "first at 1000" in r.detail, "%s %s" % (r.status, r.detail))
    r = confront.compare_pair(stream, tim[:len(tim) - 1], "fixture")
    c.ok("confront 2: a cut .tim is refused as a TIM, not compared", r.status == "tim",
         "%s %s" % (r.status, r.detail))
    r = confront.compare_pair(b"\x01\x00", tim, "fixture")
    c.ok("confront 2: a .bin that does not decode is said so", r.status == "bin",
         "%s %s" % (r.status, r.detail))


def _negative(c) -> None:
    controls = c.attempt("import tools/kits/controls.py", _kits_controls)
    if controls is None:
        return
    results = c.attempt("plant every control", lambda: controls.run_all(verbose=False),
                        default=[])
    c.ok("there is at least one control", bool(results))
    c.ok("every planted control turns the gate red",
         bool(results) and all(r.good for r in results),
         "%s" % [r.control.id for r in results if not r.good])
    print("  ..... %d of %d controls red" % (sum(r.good for r in results), len(results)))


def run(verbose: bool = True, plant: bool = True) -> int:
    """`kits_selftest`.  Returns the failure count."""
    image = os.environ.pop(IMAGE_VARIABLE, None)
    try:
        total = harness.run("looks modules", _looks_checks, verbose)
        total += harness.run("core", _core_checks, verbose)
        total += harness.run("rules", _rule_checks, verbose)
        total += harness.run("language", _language_checks, verbose)
        total += harness.run("confront 2", _confront2_checks, verbose)
        if plant:
            total += harness.run("controls", _negative, verbose)
        else:
            print("controls: not planted (--no-plant)")
    finally:
        if image is not None:
            os.environ[IMAGE_VARIABLE] = image
    print("kits_selftest: %d failure(s)" % total)
    return total


# -- kits_image ------------------------------------------------------------

def _image_checks(c, image_path) -> None:
    src = c.attempt("open %s" % image_path, lambda: api.open_source(image_path))
    if src is None:
        return
    c.ok("it opens as a disc", src.kind == api.KIND_ROM, src.kind)
    tags = src.kit_tags()
    c.ok("it has kit containers", bool(tags))
    kits = c.attempt("read every kit", lambda: src.kits(), default=())
    bad = [k.label for k in kits if not k.ok]
    c.ok("every kit passes the guard of form", kits and not bad, "%s" % bad)
    print("  ..... %d of %d kits pass the guard" % (len(kits) - len(bad), len(kits)))
    sound = next((k for k in kits if k.ok), None)
    if sound is not None:
        sc = api.stream_control(sound)
        c.ok("section 5 control 4 on %s" % sound.label, sc.ok, "%s" % (sc.planted.problems,))
    with tempfile.TemporaryDirectory(prefix="kits-image-") as folder:
        opened = c.attempt("build the recognition fixtures",
                           lambda: api.open_controls(image_path, folder), default=())
        c.ok("every recognition fixture gives what it has to",
             opened and all(o.ok for o in opened),
             "%s" % [o.name for o in opened if not o.ok])
    _confront_checks(c, image_path, len(kits))
    _zones_checks(c, image_path)


def _zones_checks(c, image_path) -> None:
    """Section 4.6 through `cli.py zones`, and section 5 control 4: the map
    moved 1 px has to fail."""
    cli = os.path.join(KITS_DIR, "cli.py")
    proc = subprocess.run([sys.executable, cli, "zones", image_path],
                          capture_output=True, text=True)
    c.ok("section 4.6: every UV rect in a zone or a declared gap, every quiet zone explained",
         proc.returncode == 0 and "verdict: section 4.6 holds" in proc.stdout,
         "exit %d" % proc.returncode)
    proc = subprocess.run([sys.executable, cli, "zones", "--negative", image_path],
                          capture_output=True, text=True)
    c.ok("section 5 control 4: the zone map moved 1 px fails section 4.6",
         proc.returncode == 0 and "red, held" in proc.stdout, "exit %d" % proc.returncode)
    _zones_map_checks(c, cli)


ZONES_PNG_VARIABLE = "WE2002_KITS_ZONES_PNG"
"""polipoli's `Zonas We2002.png`, a file of the user's (never in the repo).
Unset: the --map half is not run, and says so; set to no file: a failure."""


def _zones_map_checks(c, cli) -> None:
    """`cli.py zones --map`: every row of ZONES is polipoli's picture, and the
    map moved 1 px against the same picture has to fail (CORR-KITS-028)."""
    png = os.environ.get(ZONES_PNG_VARIABLE)
    if not png:
        print("  ..... zones --map: not run, %s is not set (polipoli's Zonas We2002.png)"
              % ZONES_PNG_VARIABLE)
        return
    c.ok("%s points at a file" % ZONES_PNG_VARIABLE, os.path.isfile(png), png)
    if not os.path.isfile(png):
        return
    proc = subprocess.run([sys.executable, cli, "zones", "--map", png],
                          capture_output=True, text=True)
    c.ok("zones --map: every row of the map is polipoli's picture",
         proc.returncode == 0 and "verdict: every row of the map is the picture" in proc.stdout,
         "exit %d" % proc.returncode)
    proc = subprocess.run([sys.executable, cli, "zones", "--map", png, "--negative"],
                          capture_output=True, text=True)
    c.ok("zones --map --negative: the map moved 1 px fails against the picture",
         proc.returncode == 0 and "control red, held" in proc.stdout,
         "exit %d" % proc.returncode)


CONFRONT_LINE = re.compile(r"^confront 1: (\d+) of (\d+) tags equal", re.MULTILINE)


def _confront_checks(c, image_path, n_kits) -> None:
    """Confront 1 of section 5 through `cli.py export --confront`, and its
    control: one pixel changed on our side has to make exactly that tag differ."""
    cli = os.path.join(KITS_DIR, "cli.py")
    for negative in (False, True):
        argv = [sys.executable, cli, "export", "--confront", image_path]
        if negative:
            argv.insert(4, "--negative")
        proc = subprocess.run(argv, capture_output=True, text=True)
        m = CONFRONT_LINE.search(proc.stdout)
        got = (int(m.group(1)), int(m.group(2))) if m else None
        if not negative:
            c.ok("confront 1: every kit equal to bin_archive.py export",
                 proc.returncode == 0 and got == (n_kits, n_kits),
                 "exit %d, %s" % (proc.returncode, got))
            print("  ..... confront 1: %s of %s tags equal" % (got or ("?", "?")))
        else:
            c.ok("confront 1 control: one pixel and one palette colour changed on our "
                 "side make two tags differ, the second by its palette",
                 proc.returncode == 0 and got == (n_kits - 2, n_kits)
                 and "red, held" in proc.stdout and "palettes differ" in proc.stdout,
                 "exit %d, %s" % (proc.returncode, got))


def _figure_checks(c, image_path) -> None:
    """Section 5, control 4, on the disc: swapping 486 and 488 swaps the
    player's and the goalkeeper's colours on the figure, every kit surface."""
    src = c.attempt("open %s" % image_path, lambda: api.open_source(image_path))
    geometry = c.attempt("read the figure's geometry", lambda: api.read_geometry(image_path))
    if src is None or geometry is None:
        return
    for tag in ("A4", "00"):
        kit = src.kit(tag)
        for figure in (0, 1):
            for kit_set in (1, 2):
                swap = c.attempt("swap TEX_%s set %d figure %d" % (tag, kit_set, figure),
                                 lambda: api.palette_swap(kit, kit_set, figure, geometry))
                if swap is None:
                    continue
                print("  ..... TEX_%s set %d figure %d: rows %s, %d kit surface(s), %d wrong"
                      % (tag, kit_set, figure, swap.rows, swap.surfaces, len(swap.wrong)))
                c.ok("TEX_%s set %d figure %d: 486/488 swapped draws the other figure's colours"
                     % (tag, kit_set, figure), swap.ok, "; ".join(swap.wrong[:3]))


def run_image(verbose: bool = True) -> int:
    """`kits_image`: 77 when the variable is not set, else the failure count
    (as 0 or 1).  Set and pointing at no file is a failure, not a skip: the
    run asked for the disc gate, and a typo must not turn it grey."""
    image_path = os.environ.get(IMAGE_VARIABLE)
    if not image_path:
        print("kits_image: skipped -- %s is not set (the Japanese data track .bin)"
              % IMAGE_VARIABLE)
        return SKIP
    if not os.path.isfile(image_path):
        print("  FAIL  %s points at a file  %s is not one" % (IMAGE_VARIABLE, image_path))
        print("kits_image: 1 failure(s)")
        return 1
    total = harness.run("kits_image", _image_checks, verbose, image_path=image_path)
    total += harness.run("figure", _figure_checks, verbose, image_path=image_path)
    return 1 if total else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", action="store_true", help="run kits_image instead")
    parser.add_argument("--no-plant", action="store_true",
                        help="skip the negative controls (controls.py runs it this way)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    if args.image:
        return run_image(verbose=not args.quiet)
    return 1 if run(verbose=not args.quiet, plant=not args.no_plant) else 0


if __name__ == "__main__":
    raise SystemExit(main())
