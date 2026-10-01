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
from core import source, tex  # noqa: E402  (internals under test; tex puts pes2/looks on the path)

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


FACADE_CLIENTS = ("cli.py",)
"""Files of tools/kits that may import nothing of the core but `core.api`
(section 3.1); the window's `ui/` joins them when it exists."""


def facade_breaks() -> list:
    """(file, line, module) for every import in FACADE_CLIENTS that is
    neither the standard library nor `core.api`."""
    import ast

    out = []
    for name in FACADE_CLIENTS:
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
                if (mod == "core.api" or top == "__future__"
                        or (top and top in sys.stdlib_module_names)):
                    continue
                out.append((name, node.lineno, mod))
    return out


def _rule_checks(c) -> None:
    breaks = c.attempt("sweep tools/kits/core", core_rule_breaks, default=None)
    c.ok("core/ has no print, exit, input or Qt (section 3.1)", breaks == [],
         "%s" % breaks)
    breaks = c.attempt("sweep the facade clients", facade_breaks, default=None)
    c.ok("cli.py imports only core.api and the standard library (section 3.1)",
         breaks == [], "%s" % breaks)


# -- 4. the negative controls ----------------------------------------------

def _kits_controls():
    """tools/kits/controls.py, by path: `import controls` finds the looks one,
    which `tex` put first on sys.path."""
    spec = importlib.util.spec_from_file_location("kits_controls",
                                                  os.path.join(KITS_DIR, "controls.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module           # dataclasses look the module up
    spec.loader.exec_module(module)
    return module


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
            c.ok("confront 1 control: one pixel changed on our side makes one tag differ",
                 proc.returncode == 0 and got == (n_kits - 1, n_kits)
                 and "red, held" in proc.stdout,
                 "exit %d, %s" % (proc.returncode, got))


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
