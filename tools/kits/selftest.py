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

    # section 4.2 (KITS-TASK-31): the selector's order -- the 95 teams in game
    # order, the ML default kit, then the unworn tags, each tag exactly once.
    all_tags = tuple("%02d" % n for n in range(100)) + tuple("A%d" % n for n in range(5))
    teams = tuple(api.TeamEntry(i, "team %d" % i, api.ORIGIN_TABLE, "%02d" % i)
                  for i in range(95))
    order = api.kit_order(teams, all_tags)
    ok("kit_order lists every tag of the disc once",
       sorted(t for t, _, _ in order) == sorted(all_tags), "%d items" % len(order))
    ok("kit_order puts the 95 teams first, in game order, then the ML default kit",
       [t.index for _, k, t in order[:95] if k == api.KIND_TEAM] == list(range(95))
       and order[95][:2] == (api.ML_DEFAULT_KIT, api.KIND_ML_DEFAULT),
       "%s" % [o[:2] for o in order[93:97]])
    ok("kit_order leaves a team whose tag is not on the disc out",
       len(api.kit_order(teams, all_tags[:10] + ("A4",))) == 11)

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

    # A lone TEX has no disc of its own: the figure's geometry comes from the
    # variable, unless a path is given (CORR-KITS-044).
    os.environ[IMAGE_VARIABLE] = "made-up-geometry.bin"
    try:
        try:
            taken = _figure.geometry_path_for()
        except api.NoGeometry as exc:
            taken = "NoGeometry: %s" % exc
        ok("lone TEX: with no geometry path, the figure takes %s" % IMAGE_VARIABLE,
           taken == "made-up-geometry.bin", "%r" % taken)
        ok("and a path given wins over it",
           _figure.geometry_path_for("given.bin") == "given.bin")
    finally:
        if saved is None:
            del os.environ[IMAGE_VARIABLE]
        else:
            os.environ[IMAGE_VARIABLE] = saved
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

    # The match figure (KITS-TASK-47): the versioned pose, dressed by position.
    pose = _figure.read_match_pose()
    outfield = pose["figures"]["outfield"]["pieces"]
    plain = [p["section"] for p in outfield]
    ok("the versioned match pose has both figures, the outfield one drawing 97",
       sorted(pose["figures"]) == ["captain", "outfield"] and 97 in plain
       and 93 not in plain, "%s" % plain)
    for armband, sleeves, want in ((False, "long", 97), (True, "long", 93),
                                   (False, "short", 4), (True, "short", 90)):
        dressed = _figure.match_order(outfield, armband, sleeves)
        at = plain.index(97)
        ok("match order, %s sleeves, armband %s: section %d where 97 was, with 97's matrix"
           % (sleeves, armband, want),
           dressed[at][0] == want and dressed[at][1] == tuple(outfield[at]["rotation"])
           and dressed[at][2] == tuple(outfield[at]["translation"])
           and len(dressed) == len(outfield), "%s" % [d[0] for d in dressed])
    bare = _figure.match_order(pose["figures"]["captain"]["pieces"], False, "long")
    ok("the captain's pose without the armband draws 97 in its place",
       93 not in [d[0] for d in bare] and 97 in [d[0] for d in bare])
    try:
        _figure.read_match_pose(os.path.join(tempfile.gettempdir(), "no-such-pose.json"))
        told = "no error"
    except api.FigureError as exc:
        told = str(exc)
    ok("a missing match pose says which command measures it",
       "--match-pose 5 --write" in told, told)

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
                       "BACKDROP", "ZONE_PEN", "GAP_PEN", "FONT_FAMILIES", "CORE_TEXT",
                       "TAB_NAMES")
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


def _kit_cli_checks(c) -> None:
    """G1 of KITS-AJUSTES-3D.md on the command line: `figure --kit home|away`
    picks the set `--set 1|2` picks, and the help says which is which."""
    spec = importlib.util.spec_from_file_location("kits_cli", os.path.join(KITS_DIR, "cli.py"))
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    parser = cli.build_parser()

    def sets(*words):
        return cli.chosen_sets(parser.parse_args(["figure", "x.bin"] + list(words)))

    cases = ((("--kit", "home"), (1,)), (("--kit", "away"), (2,)),
             (("--set", "1"), (1,)), (("--set", "2"), (2,)),
             (("--kit", "home", "--kit", "away"), (1, 2)),
             (("--set", "1", "--kit", "away"), (1, 2)), ((), (1, 2)))
    wrong = ["%s gives %s, not %s" % (" ".join(w) or "(none)", sets(*w), want)
             for w, want in cases if sets(*w) != want]
    c.ok("cli.py figure --kit home is --set 1 and --kit away is --set 2",
         not wrong, "; ".join(wrong))
    figure_help = next(a for a in parser._subparsers._group_actions[0].choices.items()
                       if a[0] == "figure")[1].format_help()
    c.ok("cli.py figure --help says 1 is home and 2 is away",
         "1 the home kit, 2 the away kit" in " ".join(figure_help.split()), figure_help[-400:])


def _hole_scene(hole: bool, flat_uv: bool = False):
    """Two quads facing the eye at yaw 180 -- a near one and an opaque one
    behind it -- the near one with a transparent texel block when *hole*, or
    with its UVs on one point when *flat_uv* (a triangle the view cannot map)."""
    from core import figure as _figure

    import scene as looks_scene

    side = 8
    rgba = bytearray(b"\x80\x40\x20\xff" * side * side)
    if hole:
        for y in range(2, 6):
            for x in range(2, 6):
                rgba[(y * side + x) * 4 + 3] = 0
    near = looks_scene.Surface(("near",), side, side, bytes(rgba), 0, 8, 0)
    far = looks_scene.Surface(("far",), side, side, b"\x10\x20\x30\xff" * side * side, 1, 8, 0)
    corners = ((-1.0, 1.0), (1.0, 1.0), (-1.0, -1.0), (1.0, -1.0))
    uvs = ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0))
    parts = []
    for name, surface, z in (("near", near, -1.0), ("far", far, 1.0)):
        quad_uvs = ((0.5, 0.5),) * 4 if (flat_uv and name == "near") else uvs
        parts.append(looks_scene.Part(name, 0, 0, tuple((x, y, z) for x, y in corners),
                                      quad_uvs, surface, "", 0, None))
    return looks_scene.Scene(parts, {("near",): near, ("far",): far}, (), 0, {}), _figure


CROSSING_INK = (b"\xc0\x10\x10", b"\x10\x10\xc0")
"""The colours of the two crossing quads, part 0 and part 1."""


def _crossing_scene():
    """Two quads through each other at yaw 0: part 0 on z = x, part 1 on
    z = -x, so each is nearer on one half.  Both have mean depth 0, and the old
    order by mean depth paints the second over the whole of the first."""
    import scene as looks_scene

    side = 4
    corners = ((-1.0, 1.0), (1.0, 1.0), (-1.0, -1.0), (1.0, -1.0))
    uvs = ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0))
    parts, surfaces = [], {}
    for n, slope in enumerate((1.0, -1.0)):
        key = ("crossing %d" % n,)
        surfaces[key] = looks_scene.Surface(key, side, side,
                                            (CROSSING_INK[n] + b"\xff") * side * side, n, 8, 0)
        parts.append(looks_scene.Part(key[0], 0, 0,
                                      tuple((x, y, slope * x) for x, y in corners), uvs,
                                      surfaces[key], "", 0, None))
    return looks_scene.Scene(parts, surfaces, (), 0, {})


def _hole_checks(c) -> None:
    """K3D-TASK-04: the hole count, on a scene built here.  A transparent block
    in the near surface has to raise the count and name that part; a triangle
    with no UV area is painted by the drawing and skipped only by the old one;
    two crossing quads come out by depth, and out of order by mean depth; and
    the 3D view has no drawing of its own, so the count is of what it shows."""
    whole, _figure = _hole_scene(False)
    holed, _ = _hole_scene(True)
    flat_uv, _ = _hole_scene(False, flat_uv=True)
    yaw = 180.0
    before = _figure.count_holes(whole, yaw, size=64)
    after = _figure.count_holes(holed, yaw, size=64)
    skipped = _figure.count_holes(flat_uv, yaw, size=64)
    print("  ..... whole: missing %d; holed: transparent %d (backdrop %d) from %s; "
          "flat UV: skipped %d" % (before.missing, after.transparent, after.backdrop,
                                   [s[:2] for s in after.sources], skipped.skipped))
    c.ok("hole count: a whole figure misses nothing", before.missing == 0, str(before))
    c.ok("hole count: a transparent texel in the uniform raises the count, from that part",
         after.transparent > before.transparent and after.backdrop == 0
         and any(s[0] == "transparent" and s[1] == "near section 0" for s in after.sources),
         str(after))
    from core import raster as _raster

    old_way = _figure.count_holes(flat_uv, yaw, size=64, order=_raster.MEAN,
                                  skip_degenerate=True)
    picture = _raster.draw(flat_uv, yaw, 0.0, 64, 64, _figure.TRIANGLES)
    near_ink = sum(1 for i in range(0, len(picture.rgba), 4)
                   if bytes(picture.rgba[i:i + 3]) == b"\x80\x40\x20")
    print("  ..... flat UV: the drawing paints %d px of the near quad, skipped %d; the old "
          "drawing skips %d" % (near_ink, skipped.skipped, old_way.skipped))
    c.ok("the drawing paints a triangle with no UV area (G6), and the old drawing's count "
         "still sees it skipped",
         near_ink > 0 and skipped.skipped == 0 and old_way.skipped > 0,
         "painted %d, skipped %d, old %d" % (near_ink, skipped.skipped, old_way.skipped))
    crossing = _crossing_scene()
    by_depth = _figure.count_holes(crossing, 0.0, size=64)
    by_mean = _figure.count_holes(crossing, 0.0, size=64, order=_raster.MEAN)
    picture = _raster.draw(crossing, 0.0, 0.0, 64, 64, _figure.TRIANGLES)
    inks = {}
    wrong = 0
    for at, near in enumerate(picture.nearest):
        if near is None:
            continue
        ink = bytes(picture.rgba[at * 4:at * 4 + 3])
        inks[ink] = inks.get(ink, 0) + 1
        wrong += ink != CROSSING_INK[near[1]]
    print("  ..... crossing quads: by depth misordered %d, %d px off the nearest, inks %s; "
          "by mean depth misordered %d" % (by_depth.misordered, wrong, sorted(inks.values()),
                                           by_mean.misordered))
    c.ok("crossing quads: at every pixel the nearest wins (G6), and the old order by mean "
         "depth is seen misordered",
         by_depth.misordered == 0 and wrong == 0 and len(inks) == 2
         and by_mean.misordered > 0,
         "depth %d, off %d, inks %d, mean %d" % (by_depth.misordered, wrong, len(inks),
                                                by_mean.misordered))
    import ast

    view = os.path.join(KITS_DIR, "ui", "figure_view.py")
    with open(view, encoding="utf-8") as fh:
        source = fh.read()
    tree = ast.parse(source, view)
    own = sorted(node.name for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name in ("rotate", "_affine"))
    c.ok("hole count: the 3D view has no camera or drawing of its own, it shows the "
         "core's (G6), so the count is of the view's picture",
         not own and "self.draw(" in source, "figure_view.py defines %s" % own)


def _dress_checks(c) -> None:
    """K3D-TASK-10 and 11: what dresses each figure, read off the rule of G3
    (`figure.ARM_PIECES`, `LONG_TO_SHORT`, `SLEEVE_LENGTHS`): the long-sleeve
    arms on the four arm pieces, the armband of each length on upper arm b in
    place of the arm it replaces, and nothing for short sleeves alone."""
    from core import figure as _figure

    want = {
        (False, "short"): {},
        (True, "short"): {"upper arm b": 90},
        (False, "long"): {"upper arm a": 95, "forearm a": 96, "upper arm b": 97,
                          "forearm b": 98},
        (True, "long"): {"upper arm a": 95, "forearm a": 96, "upper arm b": 93,
                         "forearm b": 98},
    }
    for (armband, sleeves), expect in sorted(want.items()):
        got = _figure.arm_dress(armband, sleeves)
        c.ok("arm_dress: armband %s, %s sleeves -> %s" % (armband, sleeves, expect or "nothing"),
             got == expect, "%s" % got)
    # K3D-TASK-11: the goalkeeper keeps his own long arms and takes the armband
    # measured in slot 7 on upper arm b; short sleeves he does not wear.
    keeper = {(False, "long"): {}, (True, "long"): {"upper arm b": 92},
              (False, None): {}, (True, None): {"upper arm b": 92}}
    for (armband, sleeves), expect in sorted(keeper.items(), key=repr):
        got = _figure.arm_dress(armband, sleeves, 1)
        c.ok("arm_dress: the goalkeeper, armband %s, %s sleeves -> %s"
             % (armband, sleeves or "his own", expect or "nothing"), got == expect, "%s" % got)
    try:
        _figure.arm_dress(False, "short", 1)
        refused = None
    except _figure.FigureError as exc:
        refused = str(exc)
    c.ok("arm_dress: the goalkeeper in short sleeves is refused", refused is not None,
         "%s" % refused)


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
        hints = {lang: catalog.CATALOG[lang]["figure_hint"] for lang in catalog.LANGUAGES}
        stale = [lang for lang, text in hints.items()
                 if any(w in text for w in ("shows through", "vazad"))]
        c.ok("the 3D hint no longer says the back shows through, in any language (G5)",
             not stale, "%s" % {lang: hints[lang] for lang in stale})
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


def _oracle_checks(c) -> None:
    """oracle.py --expect on a VRAM built here (CORR-KITS-047): the fixture
    kit's set-1 player palette and pages written where the match puts them,
    and the verdict asked for both sets."""
    oracle = c.attempt("import tools/kits/oracle.py", lambda: _kits_module("oracle"))
    if oracle is None:
        return
    body = build_container()
    vram = [bytearray(oracle.VRAM_W * 2) for _ in range(oracle.VRAM_H)]
    records = oracle.records_of(body)
    for index in (0, 1, 2):
        r = records[index]
        words = oracle.payload(body, r)
        for k in range(r.h):
            line = words[k * r.w:(k + 1) * r.w]
            vram[r.y + k][2 * r.x:2 * (r.x + r.w)] = struct.pack(
                "<%dH" % r.w, *(oracle.five(v) for v in line))
    vram = [bytes(row) for row in vram]
    bodies = {"00": body}
    hits = oracle.search(vram, bodies)
    right = oracle.expectation_failures(vram, bodies, hits, {"00": 1})
    wrong = oracle.expectation_failures(vram, bodies, hits, {"00": 2})
    c.ok("oracle --expect: set 1 written, 00=1 holds", right == [], "; ".join(right))
    c.ok("oracle --expect: and 00=2 fails on the palette and both pages", len(wrong) == 3,
         "; ".join(wrong))

    # --back (KITS-TASK-38): a page whose player shirt back, rows 6-29, is
    # copied into the torso gap, as the LOOKS SET was measured doing.
    width, height = 64, 128
    page = [0] * (width * height)

    def put(x, y, value):
        at = y * width + x // 2
        page[at] = (page[at] & 0xFF00) | value if x % 2 == 0 else (page[at] & 0x00FF) | value << 8

    for y in range(30):
        for x in range(20):
            put(44 + x, y, 1 + (3 * x + 5 * y) % 100)
    disc = list(page)
    for y in range(24):
        for x in range(20):
            put(x, 80 + y, oracle.pixel_index(page, width, 44 + x, 6 + y))
    gap = (0, 80, 20, 24)
    count = oracle.back_count(page, disc, width, gap)
    c.ok("oracle --back: a filled gap counts 480 written pixels against a zero disc",
         count == {"pixels": 480, "vram": 480, "disc": 0, "differ": 480}, "%s" % count)
    found = oracle.back_sources(page, width, height, gap)
    count["source"] = oracle.source_zone(found, 20, 24, 0)
    c.ok("oracle --back: the copy is found at (44,6), inside the shirt back",
         (44, 6, "straight") in found and count["source"] == oracle.BACK_SOURCE,
         "%s %s" % (found, count["source"]))
    c.ok("oracle --back: --expect-back written holds",
         oracle.back_judge({"player": count}, 0, "written") == [])
    c.ok("oracle --back: --expect-back untouched fails",
         len(oracle.back_judge({"player": count}, 0, "untouched")) == 1)
    numbers = oracle.numbers_rect()
    planted = oracle.back_count(page, disc, width, numbers[:2] + (20, 12), gap[:2])
    planted["source"] = oracle.source_zone(
        oracle.back_sources(page, width, height, numbers[:2] + (20, 12)), 20, 12, 0)
    c.ok("oracle --back: the numbers zone read in place of the gap is no copy of the shirt back",
         len(oracle.back_judge({"player": planted}, 0, "written")) == 1, "%s" % planted)
    c.ok("oracle --back: a disc page that differs outside the gaps fails",
         len(oracle.back_judge({"player": count}, 7, "written")) == 1)

    # --sleeves (KITS-TASK-39): two flat textured quads on the kit page, one
    # on the uniform image and one on the armband row of the sleeves image.
    kit_page = 9 | 1 << 4 | 1 << 7         # (576,256), 8 bpp

    def quad(u, v, w, h):
        uv = [(u, v), (u + w, v), (u, v + h), (u + w, v + h)]
        words = [0x2C << 24]
        for i, (tu, tv) in enumerate(uv):
            high = (0x7980 if i == 0 else kit_page if i == 1 else 0) << 16
            words += [0, high | tv << 8 | tu]
        return words

    try:
        samples = oracle.textured_samples([quad(4, 10, 8, 8), quad(32, 148, 16, 3)])
    except Exception as exc:  # noqa: BLE001
        samples = []
        c.ok("oracle --sleeves: the quads parse", False, repr(exc))
    tally = oracle.sleeves_tally(samples)
    c.ok("oracle --sleeves: one quad on each image, the second on the armband",
         (tally["uniform"], tally["sleeves"], tally["armband"], tally["long sleeve"])
         == (1, 1, 1, 0), "%s" % tally)
    only_uniform = oracle.sleeves_tally(samples[:1])
    c.ok("oracle --sleeves: --expect-sleeves none holds on a frame with no sleeves primitive",
         oracle.sleeves_judge(only_uniform, "none") == [])
    c.ok("oracle --sleeves: and the plant, every texel on the other image, fails it",
         any("sample the sleeves image" in f for f in oracle.sleeves_judge(
             oracle.sleeves_tally(oracle.planted(samples[:1])), "none")))
    c.ok("oracle --sleeves: a frame with no primitive on the uniform image fails the control",
         len(oracle.sleeves_judge(oracle.sleeves_tally(samples[1:]))) == 1)
    disc = b"junk" + bytes((32, 148, 0x80, 0x79, 48, 148, 0x99, 0, 32, 151, 0, 0, 48, 151, 0, 0))
    import re as _re
    held = bool(_re.search(oracle.texel_pattern(samples[1]["uv"]), disc, _re.DOTALL))
    moved = bool(_re.search(oracle.texel_pattern(oracle.planted(samples)[1]["uv"]), disc,
                            _re.DOTALL))
    c.ok("oracle --sleeves: a quad's texels are found in a model laid out as POLY_FT4, "
         "and not one texel right", held and not moved, "held %s, moved %s" % (held, moved))
    found = {"quads": 1, "files": {"/BIN/MODEL.BIN": [tuple(samples[1]["uv"])]}}
    c.ok("oracle --sleeves: --expect-sleeves drawn needs the armband and the long sleeve",
         len(oracle.sleeves_judge(tally, "drawn", found)) == 1)

    # --back --panels (KITS-TASK-42): a match page with the player shirt back
    # at (44,6), the ten glyphs in the numbers zone, and every panel under the
    # map built by the measured rule -- the "10" panel at (60,104).
    page = [0] * (width * height)
    for y in range(30):
        for x in range(20):
            put(44 + x, y, 1 + (3 * x + 5 * y) % 100)
            put(108 + x, y, 101 + (x + y) % 20)
    zx, zy, zw, zh = oracle.numbers_rect()
    for d in range(10):
        for y in range(zh):
            for x in range(oracle.GLYPH_W):
                ink = x in (1, 4) or (y in (0, 11) and d % 2) or (y == 5 and d % 3) \
                    or (x == 2 and y == d)
                put(zx + d * oracle.GLYPH_W + x, zy + y, 200 if ink else 120)
    numbers = {}
    for n, (figure, cx, cy) in enumerate(oracle.panel_cells()):
        number = 10 if (cx, cy) == (60, 104) else n + 1
        numbers[(cx, cy)] = number
        sx = 44 if figure == 0 else 108
        for y in range(oracle.PANEL_H):
            for x in range(oracle.PANEL_W):
                put(cx + x, cy + y, oracle.pixel_index(page, width, sx + x, 6 + y))
        text = str(number)
        for gx, ch in zip(oracle.digit_xs(len(text)), text):
            for y in range(zh):
                for x in range(oracle.GLYPH_W):
                    v = oracle.pixel_index(page, width, zx + int(ch) * oracle.GLYPH_W + x, zy + y)
                    if v != 120:
                        put(cx + gx + x, cy + oracle.DIGIT_Y + y, v)
    read = oracle.read_panels(page, width)
    c.ok("oracle --back --panels: every panel reads back the number written in it",
         {(r["cell"][1], r["cell"][2]): r["number"] for r in read} == numbers,
         "%s" % [(r["cell"], r["number"], r["digits"]) for r in read][:4])
    c.ok("oracle --back --panels: the measured rule holds, two digits at x 3 and 11",
         oracle.panels_judge(read) == [] and oracle.digit_xs(2) == [3, 11]
         and oracle.digit_xs(1) == [7], "; ".join(oracle.panels_judge(read)[:3]))
    # --attach (KITS-TASK-43): the rule on a report shaped like slot 5's, and
    # a camera fitted to points it projected itself.
    plain = [2, 7, 8, 9, 10, 95, 96, 97, 98]
    captain = [2, 7, 8, 9, 10, 93, 95, 96, 98]
    report = {"origin": {"MODEL.BIN only": 244, "EDT_MOD.BIN only": 0, "both": 0,
                         "neither": 6},
              "sets": [{"sections": plain}, {"sections": captain}]}
    c.ok("oracle --attach: 93 in place of 97 holds", oracle.attach_judge(report) == [])
    c.ok("oracle --attach: section 94 named the armband fails",
         len(oracle.attach_judge(report, oracle.PLANT_ARMBAND)) == 1)
    lone = dict(report, sets=[{"sections": captain}])
    c.ok("oracle --attach: a captain with no armless twin fails",
         len(oracle.attach_judge(lone)) == 1)
    # Short sleeves (CORR-KITS-079), shaped like slot 6: the armband 90 has no
    # quad of its own in the frame, only shared ones, and the captains are the
    # outfield players without 4.
    short = {"origin": report["origin"],
             "sets": [{"sections": [2, 3, 7, 8, 9, 10]}, {"sections": [2, 3, 4, 7, 8, 9, 10]},
                      {"sections": [56, 57, 59, 61]}],
             "shared": {(4, 90): 3, (90, 91): 4}}
    c.ok("oracle --attach: short sleeves, 90 only in shared quads and a captain without 4, holds",
         oracle.attach_judge(short, 90, 4, own_drawn=0) == [],
         "; ".join(oracle.attach_judge(short, 90, 4, own_drawn=0)))
    every = dict(short, sets=[{"sections": [2, 3, 4, 7]}, {"sections": [2, 3, 4, 8]}])
    c.ok("oracle --attach: short sleeves where every outfield player draws 4 fail",
         len(oracle.attach_judge(every, 90, 4, own_drawn=0)) == 1)
    unseen = dict(short, shared={(4, 91): 3})
    c.ok("oracle --attach: short sleeves with 90 nowhere in the frame fail",
         len(oracle.attach_judge(unseen, 90, 4, own_drawn=0)) == 1)
    camera = [2.0, 0.1, 0.3, 160, 0.2, -1.9, 0.4, 120, 0.001, 0.002, 0.004, 1.0]
    model = [(x, y, z) for x in (-40, 0, 37) for y in (-30, 25) for z in (-20, 15)]
    pairs = [(m, oracle.project(camera, m)) for m in model]
    fitted = oracle.fit_camera(pairs)
    c.ok("oracle --attach: a camera fitted to its own projection gives them back",
         fitted is not None and oracle.fit_error(fitted, pairs) < 1e-3,
         "%s" % (fitted and oracle.fit_error(fitted, pairs)))
    # --attach-matrix (KITS-TASK-44): stops laid out the way slot 5 draws, the
    # pointer one stop behind the matrix, one player far from the next.
    plain_order = [24, 2, 95, 96, 97, 98, 7, 9, 11, 8, 10, 12]
    captain_order = [30, 2, 95, 96, 93, 98, 7, 9, 11, 8, 10, 12]
    figures = [captain_order, plain_order, captain_order, plain_order]
    stops, previous = [{"named": [], "rotation": [0] * 9, "translation": [0, 0, 0]}], None
    for f, order in enumerate(figures):
        for k, section in enumerate(order):
            stops[-1]["rotation"] = [f * 100 + k] * 9
            stops[-1]["translation"] = [3000 * f + k, 0, 0]
            stops.append({"named": [["/BIN/MODEL.BIN", section]], "rotation": [0] * 9,
                          "translation": [0, 0, 0]})
    passes = oracle.matrix_passes(oracle.matrix_pieces(stops, 1))
    report = oracle.matrix_report(passes)
    c.ok("oracle --attach-matrix: every figure but the cut-off last comes back whole, in order",
         [[p["section"] for p in f] for f in passes] == figures[:3],
         "%s" % [[p["section"] for p in f] for f in passes])
    c.ok("oracle --attach-matrix: every worn section has its own matrix, and 93 is where 97 is",
         oracle.matrix_judge(report) == [], "; ".join(oracle.matrix_judge(report)))
    c.ok("oracle --attach-matrix: the armband expected where 98 is fails",
         len(oracle.matrix_judge(report, 98)) == 1)
    # The verdict the task exists for (CORR-KITS-076): a worn section given
    # the same rotation and translation as the body piece 7 of its figure has
    # to be reported as sharing it.
    import copy as _copy
    shared = _copy.deepcopy(passes)
    body = next(p["matrix"] for p in shared[1] if p["section"] == 7)
    for p in shared[1]:
        if p["section"] == 97:
            p["matrix"] = _copy.deepcopy(body)
    told = oracle.matrix_judge(oracle.matrix_report(shared))
    c.ok("oracle --attach-matrix: a long sleeve given section 7's matrix shares it",
         any("section 97 shares its matrix with [7]" in f for f in told), "; ".join(told))
    short = oracle.SLEEVE_LENGTHS["short"]
    short_report = {"figures": [], "orders": {(24, 2, 3, 5, 4, 6, 7, 9, 11, 8, 10, 12): 1,
                                              (30, 2, 3, 5, 90, 6, 7, 9, 11, 8, 10, 12): 1}}
    c.ok("oracle --attach-matrix --sleeve-length short: 90 is where 4 is",
         oracle.matrix_judge(short_report, short["replaced"], short["armband"]) == [])
    c.ok("oracle --attach-matrix --sleeve-length short: and not where 6 is",
         len(oracle.matrix_judge(short_report, short["neighbour"], short["armband"])) == 1)
    lagged = oracle.matrix_report(oracle.matrix_passes(oracle.matrix_pieces(stops, 0)))
    c.ok("oracle --attach-matrix: with no pointer lag a figure takes the next player's matrix",
         any("not this figure's" in f for f in oracle.matrix_judge(lagged)),
         "; ".join(oracle.matrix_judge(lagged)))
    # --match-pose (KITS-TASK-45): a quad of a section projected by its piece's
    # matrix lands on the frame's quad, corner for corner by texel; given the
    # neighbour piece's matrix it does not.  The corners are stored v1 v0 v3
    # v2, so pairing by `corners` instead of the stored order would miss.
    from types import SimpleNamespace as _ns
    vertices = [_ns(x=x, y=y, z=0) for x, y in ((-50, -80), (50, -80), (-50, 80), (50, 80))]
    texels = ((0, 0), (31, 0), (0, 63), (31, 63))
    prim = _ns(indices=(0, 1, 2, 3), texcoords=texels,
               corners=(1, 0, 3, 2))
    sec = _ns(vertices=vertices, primitives=[prim])
    view = {"H": 1376, "OFX": 0.0, "OFY": 0.0}
    own = {"matrix": ((4096, 0, 0, 0, 4096, 0, 0, 0, 4096), (-68, 112, 9813))}
    neighbour = {"matrix": ((4096, 0, 0, 0, 4096, 0, 0, 0, 4096), (-68, 52, 9813))}
    drawn = [oracle.pose_project(*own["matrix"], view, (v.x, v.y, v.z)) for v in vertices]
    frame = [{"uv": list(texels), "xy": [(round(x), round(y)) for x, y in drawn]}]
    got, matched = oracle.piece_error(own, view, sec, frame)
    c.ok("oracle --match-pose: a piece's own matrix lands within the limit, paired by texel",
         matched == 1 and got < oracle.POSE_LIMIT, "%s over %d" % (got, matched))
    wrong, _n = oracle.piece_error(neighbour, view, sec, frame)
    c.ok("oracle --match-pose: the neighbour piece's matrix lands over the limit",
         wrong > oracle.POSE_LIMIT, "%s" % wrong)
    flipped, _n = oracle.piece_error(own, view, _ns(vertices=vertices, primitives=[
        _ns(indices=prim.corners, texcoords=texels)]), frame)
    c.ok("oracle --match-pose: texels paired with `corners` instead of the stored order miss",
         flipped > oracle.POSE_LIMIT, "%s" % flipped)
    row = {"section": 2, "error": 0.8, "matched": 3}
    fine = {"captain": {"fit": {"rows": [row]}}, "outfield": {"fit": {"rows": [row]}}}
    c.ok("oracle --match-pose: two figures within the limit pass",
         oracle.pose_judge(fine, oracle.POSE_LIMIT) == [])
    over = {"captain": {"fit": {"rows": [dict(row, error=4.72)]}}}
    told = oracle.pose_judge(over, oracle.POSE_LIMIT)
    c.ok("oracle --match-pose: a piece over the limit and a missing figure both fail",
         len(told) == 2, "; ".join(told))
    # The 3D tab's number (KITS-TASK-40): the core paints a back panel, and the
    # reader that measured the game's panels (KITS-TASK-42) reads it back, at
    # the places measured in slot 5 -- written here, not taken from the core,
    # which the reader now shares.
    MEASURED_DIGIT_ROW = 7
    MEASURED_DIGIT_XS = {1: [7], 2: [3, 11]}
    side = 128
    plain = bytearray([5]) * (side * side)
    for y in range(24):
        for x in range(20):
            plain[(6 + y) * side + 44 + x] = 40 + (x + y) % 3      # the shirt back
    for d in range(10):
        for y in range(12):
            for x in range(6):
                ink = (x + d) % 6 < 2 or y in (d % 12, 11)
                plain[(68 + y) * side + 64 + d * 6 + x] = 20 + d if ink else 3
    from core import figure as _figure

    def as_words(indices):
        return [indices[i] | indices[i + 1] << 8 for i in range(0, len(indices), 2)]

    def read_back(indices, number_cell=(0, 0, 80)):
        words = as_words(indices)
        glyph_set, ground = oracle.glyphs(words, side // 2)
        back = [[v & 0x7F for v in row]
                for row in oracle.back_indices(words, side // 2, (44, 6, 20, 24))]
        return oracle.read_panel(words, side // 2, number_cell, back, glyph_set, ground)

    for number in (7, 10, 23):
        got = read_back(_figure.numbered_indices(bytes(plain), side, 0, number))
        c.ok("the 3D tab's back panel for %d reads %d to the match-panel reader, at the "
             "rule's places, nothing unexplained" % (number, number),
             got["number"] == number and got["unexplained"] == 0
             and [(x, y) for x, y, _d in got["digits"]]
             == [(x, MEASURED_DIGIT_ROW) for x in MEASURED_DIGIT_XS[len(str(number))]],
             "%s" % got)
    flipped = bytearray(_figure.numbered_indices(bytes(plain), side, 0, 10))
    for y in range(80, 104):
        row = flipped[y * side:y * side + 20]
        flipped[y * side:y * side + 20] = row[::-1]
    got = read_back(bytes(flipped))
    c.ok("and the same panel mirrored does not read 10", got["number"] != 10, "%s" % got)
    c.ok("oracle --back --panels: read one row up, every panel fails",
         len({f.split(":")[0] for f in oracle.panels_judge(oracle.read_panels(page, width, -1))})
         == len(read))
    # A quad across the captain's long-sleeve rows and the armband (v 142-151,
    # as the game draws it) and one on the elbow: the armband counts once, the
    # elbow as other, and the three sum to the sleeves image (CORR-KITS-068).
    crossing = oracle.textured_samples([quad(40, 142, 7, 9), quad(32, 213, 6, 6)])
    split = oracle.sleeves_tally(crossing)
    c.ok("oracle --sleeves: a quad across captain and armband is the armband, once; "
         "the elbow is other",
         (split["armband"], split["long sleeve"], split["other sleeves"], split["sleeves"])
         == (1, 0, 1, 2), "%s" % split)
    c.ok("oracle --sleeves: a tally whose parts do not sum to the sleeves image fails",
         any("not the" in f for f in oracle.sleeves_judge(
             dict(split, **{"long sleeve": 1}))), "%s" % split)
    # --keeper-armband (K3D-TASK-08): a goalkeeper opened at 13 drawing 92 and
    # not 15 holds the rule; expecting 103, drawing both, or an armband with
    # other vertices does not.
    keeper = {"figures": [{"figure": 0, "head": 34, "worn": [(92, None), (14, None)],
                           "spread": 150.0}],
              "orders": {(34, 13, 14, 16, 92, 17, 18, 20, 11, 19, 21, 12): 23,
                         (46, 2, 3, 5, 4, 6, 7, 9, 11, 8, 10, 12): 20}}
    c.ok("oracle --keeper-armband: a goalkeeper drawing 92 in place of 15 holds the rule",
         oracle.keeper_armband_judge(keeper, 13, 92, 15, True) == [],
         "; ".join(oracle.keeper_armband_judge(keeper, 13, 92, 15, True)))
    c.ok("oracle --keeper-armband: no goalkeeper drawing the armband fails",
         any("draws section 103" in f
             for f in oracle.keeper_armband_judge(keeper, 13, 103, 15, True)))
    both = dict(keeper, orders={(34, 13, 14, 16, 92, 15, 17): 1})
    c.ok("oracle --keeper-armband: a goalkeeper drawing armband and arm both fails",
         any("both" in f for f in oracle.keeper_armband_judge(both, 13, 92, 15, True)))
    c.ok("oracle --keeper-armband: an armband without the arm's vertices fails",
         len(oracle.keeper_armband_judge(keeper, 13, 92, 15, False)) == 1)
    # --edit-number (K3D-TASK-16): figures cut at a MODEL.BIN head, the torso
    # yaw read off a matrix, a turn counted in frames, and the judge asking for
    # the head, the turn and a panel read by the match's rule.
    edt, model = oracle.layout.EDT_MOD, oracle.layout.MODEL
    still = ([4096, 0, 0, 0, 4096, 0, 0, 0, 4096], [0, 0, 0])
    turned = ([-4096, 0, 0, 0, 4096, 0, 0, 0, -4096], [0, 0, 0])
    stops = [{"named": [[model, 34]], "rotation": still[0], "translation": still[1]},
             {"named": [[edt, 11]], "rotation": still[0], "translation": still[1]},
             {"named": [], "rotation": still[0], "translation": still[1]},
             {"named": [[model, 34]], "rotation": still[0], "translation": still[1]},
             {"named": [[edt, 11]], "rotation": turned[0], "translation": turned[1]},
             {"named": [], "rotation": still[0], "translation": still[1]}]
    stops += stops[3:]       # a third frame, so the second figure has an end
    figures = oracle.edit_figures(oracle.edit_pieces(stops))
    c.ok("oracle --edit-number: the pieces cut into figures at the head, the ends dropped",
         len(figures) == 1 and [p["section"] for p in figures[0]] == [34, 11, None],
         "%s" % [[p["section"] for p in f] for f in figures])
    c.ok("oracle --edit-number: a piece's yaw is 0 still and 180 turned about y",
         (oracle.piece_yaw(still), oracle.piece_yaw(turned)) == (0.0, 180.0))
    turn = oracle.edit_turn([10.0, 10.0, 30.0, 50.0, 70.0, 90.0, 90.0])
    c.ok("oracle --edit-number: a turn of four 20-degree frames is counted as such",
         (turn["frames"], turn["start"], turn["end"]) == (4, 10.0, 90.0), "%s" % turn)
    c.ok("oracle --edit-number: a still torso is no turn",
         oracle.edit_turn([10.0, 10.0, 10.2])["frames"] == 0)
    panel = {"cell": (1, 100, 104), "digits": [(7, oracle.DIGIT_Y, 1)], "unexplained": 0,
             "number": 1}
    report = {"figures": [{"figure": 0, "head": 34, "family": "goalkeeper", "spread": 10.0,
                           "order": "MODEL.BIN:34 EDT_MOD.BIN:11"}],
              "turn": {"frames": 9, "first": 3, "last": 11, "start": 0.0, "end": 180.0},
              "turn_frames": 100}
    c.ok("oracle --edit-number: a figure at the head, a turn and a sound panel hold",
         oracle.edit_number_judge(report, 34, [panel]) == [],
         "; ".join(oracle.edit_number_judge(report, 34, [panel])))
    c.ok("oracle --edit-number: no figure opened at the head fails",
         any("opened at section 103" in f
             for f in oracle.edit_number_judge(report, 103, [panel])))
    c.ok("oracle --edit-number: a torso that never turned fails",
         any("did not turn" in f for f in oracle.edit_number_judge(
             dict(report, turn={"frames": 0, "first": None, "last": None, "start": 0.0,
                                "end": 0.0}), 34, [panel])))
    c.ok("oracle --edit-number: a torso swaying a degree, as the walk does, is no turn",
         not oracle.turned_through(oracle.edit_turn([-11.4, -12.0, -11.2, -10.0, -11.0]))
         and oracle.turned_through(oracle.edit_turn([0.0, 60.0, 120.0, 180.0, 180.0])))
    c.ok("oracle --edit-number: a panel with pixels the rule does not explain fails",
         any("neither" in f for f in oracle.edit_number_judge(
             report, 34, [dict(panel, unexplained=5)])))
    c.ok("oracle --edit-number: no panel after the turn fails",
         any("no panel" in f for f in oracle.edit_number_judge(report, 34, [])))
    # CORR-K3D-020: what G7 measured is asserted, not only printed.
    c.ok("oracle --edit-number: a figure of no family fails",
         any("of no family" in f for f in oracle.edit_number_judge(
             dict(report, figures=[dict(report["figures"][0], family="neither")]),
             34, [panel])))
    expect = dict(oracle.EDIT_EXPECT[(8, 0)], frames=9)
    seen = dict(report, tag=expect["tag"], set=expect["set"])
    c.ok("oracle --edit-number: the measured head, family, number, turn and kit hold",
         oracle.edit_number_judge(seen, 34, [panel], expect) == [],
         "; ".join(oracle.edit_number_judge(seen, 34, [panel], expect)))
    c.ok("oracle --edit-number: the player where the goalkeeper was measured fails",
         any("goalkeeper expected" in f for f in oracle.edit_number_judge(
             dict(seen, figures=[dict(seen["figures"][0], family="player")]),
             34, [panel], expect)))
    c.ok("oracle --edit-number: another number on the measured panel fails",
         any("number 1 expected" in f for f in oracle.edit_number_judge(
             seen, 34, [dict(panel, number=7)], expect)))
    c.ok("oracle --edit-number: a turn of another length fails",
         any("took 9 frame(s), 30 expected" in f for f in oracle.edit_number_judge(
             seen, 34, [panel], dict(expect, frames=30))))
    c.ok("oracle --edit-number: another kit on the screen fails",
         any("TEX_41 set 1 expected" in f for f in oracle.edit_number_judge(
             dict(seen, tag="00"), 34, [panel], expect)))
    # --replay (K3D-TASK-17): the followed figure is the nearest, a still pose
    # differs by nothing, a shaded quad's corner colours and the drawing offset
    # are read off the command list, the GPU's modulation explains a drawn
    # pixel the bare texel does not, the back panel is found by texel, and the
    # judge asks for root, head, armband, stillness, panel, number and frames.
    def _piece(section, z, turn=0):
        return {"section": section, "projection": {"H": 1, "OFX": 0, "OFY": 0},
                "matrix": ((4096, 0, turn, 0, 4096, 0, 0, 0, 4096), (0, 0, z))}

    near = [_piece(34, 4600), _piece(13, 4600), _piece(92, 4600)]
    far = [_piece(46, 9000), _piece(2, 9000), _piece(3, 9000)]
    cut = oracle.replay_figures(far + near)
    c.ok("oracle --replay: the frame is cut at each root, head first",
         [[p["section"] for p in f] for f in cut] == [[46, 2, 3], [34, 13, 92]],
         "%s" % [[p["section"] for p in f] for f in cut])
    c.ok("oracle --replay: the followed figure is the nearest, the plant the next",
         (oracle.replay_focus(cut)[0]["section"], oracle.replay_focus(cut, 1)[0]["section"],
          oracle.replay_focus(cut, 2)) == (34, 46, None))
    c.ok("oracle --replay: one pose twice is still, a moved one is not",
         (oracle.pose_change(near, near),
          oracle.pose_change(near, [_piece(34, 4600), _piece(13, 4601), _piece(92, 4600)]))
         == (0, 1))
    page, clut = 0x99, (488 << 6)
    colour = lambda r, g, b: r | g << 8 | b << 16  # noqa: E731
    quad = [0x3C << 24 | colour(64, 64, 64), 0, (clut << 16) | 100 | 104 << 8,
            colour(128, 128, 128), 4, (page << 16) | 104 | 104 << 8,
            colour(64, 64, 64), 4 << 16, 100 | 108 << 8,
            colour(128, 128, 128), 4 | 4 << 16, 104 | 108 << 8]
    flat = [0x2C << 24 | colour(127, 127, 127), 0, (clut << 16), 1, (page << 16), 1 << 16, 0,
            1 | 1 << 16, 0]
    offset = 0xE5 << 24 | (256 << 11) | 0
    read = oracle.textured_samples([quad, flat])
    c.ok("oracle --replay: a shaded quad keeps its four corner colours, a flat one its one",
         [s["rgb"] for s in read] == [[(64, 64, 64), (128, 128, 128), (64, 64, 64),
                                       (128, 128, 128)], [(127, 127, 127)] * 4]
         and read[0]["page"] == (576, 256) and read[0]["clut"] == (0, 488),
         "%s" % [(s["rgb"], s["page"], s["clut"]) for s in read])
    c.ok("oracle --replay: the drawing offset is read off its command, signed",
         (oracle.draw_offset([[offset], quad]), oracle.draw_offset([[0xE5 << 24 | 0x7FF]]),
          oracle.draw_offset([quad])) == ((0, 256), (-1, 0), None))
    half = (lambda lo, hi: lo | hi << 8)(1, 1)
    texture = {"pages": {"576,256,8": [half] * (oracle.TEXTURE_HALFWORDS * 256)},
               "cluts": {"0,488": [(0, 0, 0), (20, 10, 30)]}}
    drawn = dict(read[0], rgb=[(64, 64, 64)] * 4)
    game = [[(10, 5, 15)] * 6 for _ in range(6)]
    seen = oracle.colour_confront([drawn], {"origin": (0, 0), "rows": game}, texture,
                                  {92: [drawn]})[92]
    c.ok("oracle --replay: a pixel drawn at half colour is the modulated texel, not the bare one",
         seen is not None and seen["shaded_far"] == 0.0 and seen["texel_far"] > 5.0,
         "%s" % seen)
    cells = oracle.panel_samples([read[0]])
    c.ok("oracle --replay: a torso quad inside the goalkeeper's cell names that panel",
         list(cells) == [(1, 100, 104)], "%s" % list(cells))
    expect = {"root": 13, "head": 34, "armband": 92, "replaced": 15,
              "panel": (576, 100, 104), "number": 1}
    good = {"focus": near, "still": 0, "turned": "back", "panel": (576, 100, 104), "number": 1,
            "panel_failures": [], "idle": 390, "front_frames": 9, "back_frames": 60}
    c.ok("oracle --replay: the measured figure holds the judge",
         oracle.replay_judge(good, expect) == [], "; ".join(oracle.replay_judge(good, expect)))
    c.ok("oracle --replay: the plant's root fails",
         any("not at section 103" in f for f in oracle.replay_judge(good, expect, plant=True)))
    c.ok("oracle --replay: a pose that moved, another number and a capture past the idle fail",
         len(oracle.replay_judge(dict(good, still=3, number=5, back_frames=400), expect)) == 3,
         "; ".join(oracle.replay_judge(dict(good, still=3, number=5, back_frames=400), expect)))
    # --replay-field (K3D-TASK-18): the sleeves and armband are read off the
    # sections, and the judge asks for the followed figure clear of the next
    # one, the camera back on the ball, the captain's armband and number, the
    # goalkeeper's armband and every capture under the idle.
    on_axis = [[_piece(46, 3600), dict(_piece(2, 3600), matrix=((4096, 0, 0, 0, 4096, 0, 0, 0, 4096),
                                                                (600, 0, 3600)))],
               [_piece(24, 4700), _piece(2, 4700)]]
    c.ok("oracle --replay-field: the followed figure is on the axis, not the nearest",
         (oracle.field_focus(on_axis)[0]["section"], oracle.field_focus(on_axis, 1)[0]["section"])
         == (24, 46))
    shared_rows = [{"follows": True, "root": 2, "page": 640, "cells": {"0,0,80": 2, "0,60,104": 2}},
                   {"follows": True, "root": 2, "page": 640, "cells": {"0,0,80": 4}},
                   {"follows": True, "root": 13, "page": 640, "cells": {"1,100,104": 4}}]
    oracle.field_panels(shared_rows)
    c.ok("oracle --replay-field: the panel is the cell left once the shared one is taken away",
         [r["panel"] for r in shared_rows] == [(640, 60, 104), (640, 0, 80), (640, 100, 104)],
         "%s" % [r["panel"] for r in shared_rows])
    c.ok("oracle --replay-field: short and long sleeves and the armband are read off the sections",
         (oracle.sleeves_of([46, 2, 3, 5, 90, 6]), oracle.sleeves_of([46, 2, 95, 97, 93, 98]),
          oracle.sleeves_of([34, 13, 14, 16, 92]), oracle.armband_of([46, 2, 3, 5, 90, 6]),
          oracle.armband_of([46, 2, 3, 5, 4, 6])) == ("short", "long", None, 90, None))

    def _row(k, **kw):
        base = {"k": k, "follows": True, "depth": 4695, "off": 1.0, "next": 80.0,
                "next_depth": 4900, "root": 2,
                "armband": None, "number": 7, "frames": 70}
        base.update(kw)
        return base

    field = [_row(0, follows=False, root=13, armband=92, depth=4681, next=None),
             _row(1, follows=False, root=13, armband=92, depth=6059, next=None),
             _row(2), _row(3, armband=90, number=11),
             _row(4, root=13, armband=92, number=1),
             _row(5, follows=False, depth=6100, end="ball")]
    fexpect = {"captain": {"armband": 90, "number": 11}, "keeper": {"k": 0, "root": 13, "armband": 92},
               "sleeves": "short"}
    c.ok("oracle --replay-field: the measured table holds the judge",
         oracle.replay_field_judge(field, fexpect, 390) == [],
         "; ".join(oracle.replay_field_judge(field, fexpect, 390)))
    near_next = [dict(r, next=3.0) if r["k"] == 2 else r for r in field]
    far_behind = [dict(r, next=1.5, next_depth=6802) if r["k"] == 2 else r for r in field]
    c.ok("oracle --replay-field: a second figure on the axis but far behind holds",
         oracle.replay_field_judge(far_behind, fexpect, 390) == [],
         "; ".join(oracle.replay_field_judge(far_behind, fexpect, 390)))
    c.ok("oracle --replay-field: a second figure inside the margin fails",
         any("under the margin" in f for f in oracle.replay_field_judge(near_next, fexpect, 390)),
         "; ".join(oracle.replay_field_judge(near_next, fexpect, 390)))
    wrong = [dict(r, number=12) if r["k"] == 3 else r for r in field]
    c.ok("oracle --replay-field: the captain on another number fails",
         any("holds number 12, not 11" in f
             for f in oracle.replay_field_judge(wrong, fexpect, 390)))
    c.ok("oracle --replay-field: another armband, no ball at the end and a late capture fail",
         len(oracle.replay_field_judge(
             [dict(r, armband=93) if r["k"] == 3 else dict(r, frames=400) if r["k"] == 2 else r
              for r in field[:-1]], fexpect, 390)) == 3,
         "; ".join(oracle.replay_field_judge(
             [dict(r, armband=93) if r["k"] == 3 else dict(r, frames=400) if r["k"] == 2 else r
              for r in field[:-1]], fexpect, 390)))
    # --edt-arms (K3D-TASK-07): an arm laid on four EDT-like pieces -- two
    # cylinders a side, the upper arm over y -40..40 and the forearm over
    # 20..120, side a below z 0 and side b its mirror -- goes on its own piece,
    # in its frame; mirrored it goes on side b; moved out of its frame it fails.
    import math as _math

    def _ring(y0, y1, radius, z0, rows=9, around=12):
        return [(radius * _math.cos(2 * _math.pi * k / around),
                 y0 + (y1 - y0) * r / (rows - 1),
                 z0 + radius * _math.sin(2 * _math.pi * k / around))
                for r in range(rows) for k in range(around)]

    def _mirror(points):
        return [(x, y, -z) for x, y, z in points]

    upper, fore = _ring(-40, 40, 15, -2), _ring(20, 120, 10, -2)
    arms = {(1, "upper arm a"): upper, (2, "upper arm b"): _mirror(upper),
            (3, "forearm a"): fore, (4, "forearm b"): _mirror(fore)}
    sleeve = [(x + 0.5, y + 0.5, z) for x, y, z in _ring(-38, 38, 14, -2, 3, 4)]
    seen = oracle.arms_report({95: sleeve, 97: _mirror(sleeve)}, arms)
    rule = {95: "upper arm a", 97: "upper arm b"}
    c.ok("oracle --edt-arms: a sleeve goes on its own piece, in its frame",
         oracle.arms_judge(seen, rule) == [], "; ".join(oracle.arms_judge(seen, rule)))
    c.ok("oracle --edt-arms: the mirrored sleeve goes on side b",
         seen[97]["piece"] == "upper arm b", "%s" % seen[97]["piece"])
    moved = oracle.arms_report({95: sleeve}, arms, oracle.ARM_PLANT_SHIFT)
    c.ok("oracle --edt-arms: a sleeve moved out of its frame fails",
         any("out of" in f for f in oracle.arms_judge(moved, {95: "upper arm a"})),
         "%s" % moved[95])
    # A judge case: on the disc scene.pose poses by name and cannot report an
    # arm apart (CORR-K3D-012), so only the judge is exercised here.
    c.ok("oracle --edt-arms: the judge refuses an arm reported posed apart",
         len(oracle.arms_judge(seen, rule, {"upper arm a": False})) == 1)


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
        total += harness.run("kit cli", _kit_cli_checks, verbose)
        total += harness.run("holes", _hole_checks, verbose)
        total += harness.run("dressings", _dress_checks, verbose)
        total += harness.run("confront 2", _confront2_checks, verbose)
        total += harness.run("oracle", _oracle_checks, verbose)
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
    _edt_arms_checks(c, image_path)


def _edt_arms_checks(c, image_path) -> None:
    """`oracle.py --edt-arms` on the disc (K3D-TASK-07, CORR-K3D-011): the
    rule ARM_PIECES holds, every arm moved out of its frame fails, and the
    judge refuses a rule with one piece swapped -- the red this check has to
    be seen to give, since controls.py runs without the disc."""
    import contextlib

    oracle = c.attempt("import tools/kits/oracle.py", lambda: _kits_module("oracle"))
    if oracle is None:
        return

    def quiet(plant):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = oracle.run_edt_arms(image_path, plant)
        return code, out.getvalue()

    code, out = c.attempt("oracle --edt-arms on the disc", lambda: quiet(False), default=(None, ""))
    c.ok("oracle --edt-arms: every sleeve and armband section sits where ARM_PIECES says",
         code == 0, "exit %s; %s" % (code, "; ".join(
             ln.strip() for ln in out.splitlines() if "FAIL" in ln)[:300]))
    code, out = c.attempt("oracle --edt-arms --plant-edt-arms", lambda: quiet(True),
                          default=(None, ""))
    c.ok("oracle --edt-arms --plant-edt-arms: every arm out of its frame fails",
         code == 1 and out.count("units out of") == len(oracle.ARM_PIECES),
         "exit %s, %d 'units out of'" % (code, out.count("units out of")))
    swapped = {**oracle.ARM_PIECES, 93: "upper arm a"}
    report = c.attempt("measure the arms for the swapped rule", lambda: _edt_arms_report(
        oracle, image_path), default=None)
    c.ok("oracle --edt-arms: a rule with section 93 on upper arm a is refused",
         report is not None and any("section 93: on upper arm b, the rule says upper arm a" in f
                                    for f in oracle.arms_judge(report, swapped)))


def _edt_arms_report(oracle, image_path) -> dict:
    """`oracle.arms_report` on the disc, as `run_edt_arms` builds it."""
    import iso_source
    import pieces
    import section

    layout = oracle.layout
    with iso_source.open_disc(image_path) as disc:
        files = {n: disc.read(n) for n in (layout.EDT_MOD, layout.MODEL)}
    edt = section.scan(files[layout.EDT_MOD],
                       layout.geometry_start(files[layout.EDT_MOD])).sections
    model = section.scan(files[layout.MODEL], layout.MODEL_GEOMETRY_START).sections
    named, _orders, _paired = pieces.name_pieces(files[layout.EDT_MOD])
    arms = {(i, p.full_name): [(v.x, v.y, v.z) for v in edt[i].vertices]
            for i, p in named.items() if p.full_name in oracle.ARM_NAMES}
    return oracle.arms_report({n: [(v.x, v.y, v.z) for v in model[n].vertices]
                               for n in oracle.ARM_PIECES}, arms)


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
    # The lone TEX: the kit's bytes out of the disc into a file of their own,
    # opened as a TEX, and its figure built with no geometry path -- the
    # variable is the disc (CORR-KITS-044).
    from core import figure as _figure
    with tempfile.TemporaryDirectory() as tmp:
        lone_path = os.path.join(tmp, "TEX_00.BIN")
        with open(lone_path, "wb") as out:
            out.write(src.kit("00").data)
        lone = c.attempt("open the lone TEX_00.BIN", lambda: api.open_source(lone_path))
        drawn = None if lone is None else c.attempt(
            "build the lone TEX's figure", lambda: api.figure(lone.kit(None), 1, 0))
    worn = 0 if drawn is None else sum(1 for key in drawn.surfaces if key[0] == _figure.SLOT)
    c.ok("lone TEX: opened as a TEX, its figure built from %s, %d kit surface(s)"
         % (IMAGE_VARIABLE, worn),
         lone is not None and lone.kind == "tex" and worn > 0,
         "kind %r" % (lone and lone.kind))
    _figure_cli_checks(c, image_path, src.kit("00"), geometry)
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


def _figure_cli_checks(c, image_path, kit, geometry) -> None:
    """Item 5 of section 0 for the 3D tab (CORR-KITS-062): `cli.py figure`
    draws the scene the window draws -- the same `api.figure` call, the same
    digest -- tells set 1 from set 2, and its --negative (set 2 drawn as
    set 1) is seen red."""
    cli = os.path.join(KITS_DIR, "cli.py")
    env = dict(os.environ, **{IMAGE_VARIABLE: image_path})
    proc = subprocess.run([sys.executable, cli, "figure", image_path, "--tag", "00"],
                          capture_output=True, text=True, env=env)
    rows = {}
    for line in proc.stdout.splitlines():
        words = line.split()
        if len(words) > 4 and words[0] == "set" and words[2] == "figure":
            rows[int(words[1]), int(words[3])] = words[-1]
    scene = c.attempt("draw TEX_00 set 1 figure 0 as the window does",
                      lambda: api.figure(kit, 1, 0, frame=api.FIGURE_POSE, geometry=geometry))
    want = None
    if scene is not None:
        import hashlib
        h = hashlib.sha256()
        for part in scene.parts:
            h.update(repr((part.points, part.uvs)).encode())
            h.update(part.surface.rgba if part.surface is not None else b"untextured")
        want = h.hexdigest()
    differ = sum(1 for line in proc.stdout.splitlines()
                 if line.startswith("figure ") and line.endswith("set 1 and set 2 differ"))
    print("  ..... cli.py figure TEX_00: exit %d, %d row(s), %d figure(s) whose sets differ"
          % (proc.returncode, len(rows), differ))
    c.ok("cli.py figure draws the window's scene: TEX_00 set 1 figure 0 digest %s"
         % (want or "?")[:16],
         proc.returncode == 0 and want is not None and rows.get((1, 0)) == want,
         "cli %s, window %s" % (rows.get((1, 0)), want))
    c.ok("cli.py figure tells set 1 from set 2 on TEX_00, for both figures",
         len(rows) == 4 and differ == 2, proc.stdout[-300:])
    proc = subprocess.run([sys.executable, cli, "figure", "--negative", image_path,
                           "--tag", "00"], capture_output=True, text=True, env=env)
    last = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else proc.stderr
    print("  ..... %s" % last)
    c.ok("cli.py figure --negative: the set ignored is seen red", proc.returncode == 0, last)
    proc = subprocess.run([sys.executable, cli, "holes", image_path, "--tag", "00",
                           "--step", "180", "--negative"], capture_output=True, text=True, env=env)
    lines = proc.stdout.splitlines()
    torso = {f: any(line.startswith("figure %d yaw" % f) and "gap torso" in line
                    for line in lines) for f in (0, 1)}
    print("  ..... cli.py holes TEX_00, yaws 0 and 180: exit %d, %s" % (
        proc.returncode, "; ".join(line for line in lines if line.startswith("negative"))))
    c.ok("cli.py holes: from the back the torso gap shows through on neither figure, "
         "the shirt back copied in with Number unticked (G5), and its --negative sees a "
         "planted gap",
         proc.returncode == 0 and not any(torso.values()), proc.stdout[-600:] + proc.stderr)
    by_name = {}
    for words in (("--kit", "home"), ("--set", "1"), ("--kit", "away"), ("--set", "2")):
        proc = subprocess.run([sys.executable, cli, "figure", image_path, "--tag", "00",
                               "--figure", "0"] + list(words),
                              capture_output=True, text=True, env=env)
        found = [line.split()[-1] for line in proc.stdout.splitlines()
                 if line.startswith("set ") and " figure 0 " in line]
        by_name[words] = found[0] if proc.returncode == 0 and len(found) == 1 else None
    print("  ..... cli.py figure TEX_00 figure 0: %s" % ", ".join(
        "%s %s" % (" ".join(w), (d or "?")[:12]) for w, d in by_name.items()))
    c.ok("cli.py figure --kit home draws --set 1's digest and --kit away --set 2's, "
         "and the two differ",
         None not in by_name.values()
         and by_name["--kit", "home"] == by_name["--set", "1"]
         and by_name["--kit", "away"] == by_name["--set", "2"]
         and by_name["--kit", "home"] != by_name["--kit", "away"], str(by_name))


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
