#!/usr/bin/env python3
"""One command line over the viewer's core: sections, pieces, texture, looks, check.

Provenance (plan section 3.4): none of the four columns.  Every number this
prints comes from the module that owns it; this file only chooses which one
to ask, and knows no address and no format of its own.

Subcommands:

    sections [image]        both model files: where the walk starts, what it
                            finds, and that it closes on the file's own end
    pieces [image]          the eleven pieces of each figure, and how each
                            name was known
    texture [image]         DAT2D.BIN: its record tables and the palette list
    looks [tuple]           the twelve rows of LOOKS SET; with a tuple, what it
                            spells, and -- given the image -- its draw list
    check [image]           EVERY `--check-image` of the core, in one run; exits
                            77 with no image.  This is the `looks_image` target
    --check                 this module's own self-check, like every module

The image is the Japanese data track, by argument or by WE2002_LOOKS_IMAGE.
Every read goes through the two-disc guard of layout.py, so pointing either at
the English translation is refused, not answered.

## Why `check` runs eight modules and not one

The `looks_image` target used to run `modelfile.py --check-image` alone, from
CORR-LOOKS-012 on.  By LOOKS-TASK-19 seven more modules had grown a
`--check-image` of their own -- texture, atlas, skin, looks, assembly, pieces
and scene -- and none of them was in any target: a green `looks_image` measured
one eighth of what the disc gate knows.  So `check` runs them all, and the
list is not trusted to stay complete either: the self-check finds every module
that answers `--check-image` by reading the sources, and fails when the two
disagree.

`modelfile` has to be IN the run, and where it runs does not matter.  Its first
read is a Japanese-only file through the guard, and geometry is identical on
both discs, so a run without it pointed at the English image would lean on the
others to notice (CORR-LOOKS-012) -- measured, six of them do and `pieces`
does not.  `check` runs all eight to the end and `combine` fails on any
failure, so the order changes nothing: reordered with `modelfile` LAST, the
English disc still comes out `1 ok, 7 failed -- FAILED`.  This said "runs
FIRST" until CORR-LOOKS-052, and a control guarded the position.

**A partial skip is a failure.**  With the image given, a module that still
answers 77 is missing something the others are not, and eight results with a
skip among them is not the green of eight.  Only all-77 is a skip.

Usage:

    python tools/looks/cli.py sections
    python tools/looks/cli.py looks A-I3-A-C-A
    python tools/looks/cli.py check roms/japanese-shift-jis.bin   # a COPY is
                                                                  # also fine
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tokenize

LOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, LOOKS_DIR)

import harness  # noqa: E402
import layout  # noqa: E402

SKIP = 77

CHECK_IMAGE = (
    "modelfile",
    "texture",
    "sprites",
    "atlas",
    "skin",
    "looks",
    "assembly",
    "pieces",
    "scene",
    "anime",
    "stature",
)
"""Every module with a `--check-image`, in the order `check` runs them.

The order is for reading: dependency order, so the first failure printed is the
lowest one.  It is not a guard -- `check` runs every module to the end.  What
guards is MEMBERSHIP: the self-check compares this with `image_checkers()` and
fails on any difference, and asserts `modelfile` by name (CORR-LOOKS-052).
"""

FLAG = "--check-image"


class Unavailable(RuntimeError):
    """What this run needs is not on this machine.  Reported as 77."""


# --- the pieces `check` is made of -----------------------------------------

def image_checkers(directory: str = LOOKS_DIR) -> set:
    """The modules that answer `--check-image`, read from their sources.

    Tokenised, and only STRING tokens count: this file names the flag too, and
    so does any docstring that mentions it -- a module whose docstring says
    `--check-image` and whose `main()` does not handle it is not a checker,
    but a plain text search could not tell.  What makes a module a checker is
    the flag as a whole string literal, which is how every `main()` compares
    it.
    """
    found = set()
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".py") or name == os.path.basename(__file__):
            continue
        with open(os.path.join(directory, name), encoding="utf-8") as handle:
            try:
                tokens = list(tokenize.generate_tokens(handle.readline))
            except (tokenize.TokenError, SyntaxError):
                continue
        for kind, text, _start, _end, _line in tokens:
            if kind == tokenize.STRING and text in ('"%s"' % FLAG,
                                                    "'%s'" % FLAG):
                found.add(name[:-3])
                break
    return found


def combine(codes: list) -> int:
    """One exit code for many: 0, 77, or 1.

    Nothing run is a failure, not a pass.  All skipped is a skip.  Anything
    else that is not all zeros fails -- including zeros with a skip among
    them, for the reason in the module docstring.
    """
    if not codes:
        return 1
    if all(code == SKIP for code in codes):
        return SKIP
    if all(code == 0 for code in codes):
        return 0
    return 1


def resolve_image(given: str | None, environ=None) -> str:
    """The image by argument, else by environment, else `Unavailable`."""
    if given:
        return given
    environ = os.environ if environ is None else environ
    value = environ.get(layout.ENV_IMAGE)
    if not value:
        raise Unavailable(
            "%s is not set and no image was given: it names the Japanese data "
            "track (.bin) every read comes from.  %s, the English .cue, is not "
            "a substitute" % (layout.ENV_IMAGE, layout.ENV_DRIVE_IMAGE))
    return value


# --- the subcommands --------------------------------------------------------

def cmd_sections(image: str) -> int:
    import iso_source
    import modelfile

    with iso_source.open_disc(image) as disc:
        files = [(path, disc.read(path)) for path in (layout.EDT_MOD,
                                                      layout.MODEL)]
    bad = 0
    for path, data in files:
        scan = modelfile.scan(data, path)
        closes = scan.end == len(data)
        bad += not closes
        print("%-16s %6d B   from %5d: %3d section(s), %4d vertices, "
              "%4d primitives, groups %s, stops at %d%s"
              % (path, len(data), layout.GEOMETRY_START[path],
                 len(scan.sections), scan.vertices, scan.primitives,
                 list(scan.groups), scan.end,
                 "  (the end of the file)" if closes
                 else "  -- NOT THE END OF THE FILE"))
    return 1 if bad else 0


def cmd_pieces(image: str) -> int:
    import iso_source
    import pieces

    with iso_source.open_disc(image) as disc:
        data = disc.read(layout.EDT_MOD)
    pieces.report(data)
    return 0


def cmd_texture(image: str) -> int:
    import iso_source
    import texture

    with iso_source.open_disc(image) as disc:
        data = disc.read(layout.DAT2D)
    texture._report(data, layout.DAT2D)
    return 0


def cmd_looks(text: str | None, image: str | None) -> int:
    import looks

    if text:
        looks.parse_tuple(text)  # refuses a malformed tuple before printing
    looks._report(text)
    if not text:
        return 0
    print()
    if not image:
        print("the draw list needs the image: pass --image, or set %s"
              % layout.ENV_IMAGE)
        return 0
    import assembly

    return assembly._tuple(image, text)


def cmd_check(image: str, verbose: bool = True) -> int:
    env = dict(os.environ)
    env[layout.ENV_IMAGE] = image
    codes = []
    for module in CHECK_IMAGE:
        done = subprocess.run(
            [sys.executable, os.path.join(LOOKS_DIR, module + ".py"), FLAG],
            env=env, capture_output=True, text=True)
        codes.append(done.returncode)
        lines = (done.stdout + done.stderr).rstrip().splitlines()
        last = lines[-1] if lines else "(no output)"
        word = {0: "ok  ", SKIP: "SKIP"}.get(done.returncode, "FAIL")
        print("  %s  %-10s exit %-3d %s" % (word, module, done.returncode,
                                            last))
        if done.returncode != 0 and verbose:
            for line in lines[:-1]:
                print("        %s" % line)
    result = combine(codes)
    passed = codes.count(0)
    skipped = codes.count(SKIP)
    print("cli check: %d module(s), %d ok, %d skipped, %d failed -- %s"
          % (len(codes), passed, skipped, len(codes) - passed - skipped,
             {0: "ok", SKIP: "skipped"}.get(result, "FAILED")))
    return result


# --- the self-check ---------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    return harness.run("cli.py", _checks, verbose)


def _checks(c) -> None:
    ok = c.ok

    found = image_checkers()
    ok("every module that answers --check-image is in CHECK_IMAGE",
       found == set(CHECK_IMAGE),
       "on disc but not listed: %s; listed but not on disc: %s"
       % (sorted(found - set(CHECK_IMAGE)), sorted(set(CHECK_IMAGE) - found)))
    ok("and none is listed twice", len(CHECK_IMAGE) == len(set(CHECK_IMAGE)))
    ok("modelfile is in the run -- its first read is the guard's",
       "modelfile" in CHECK_IMAGE, "%r" % (CHECK_IMAGE,))

    ok("eight passes are a pass", combine([0] * 8) == 0)
    ok("eight skips are a skip", combine([SKIP] * 8) == SKIP)
    ok("a pass with a skip beside it is NOT a pass",
       combine([0, 0, SKIP]) == 1, "%r" % combine([0, 0, SKIP]))
    ok("one failure among passes fails", combine([0, 1, 0]) == 1)
    ok("a failure beside skips is not a skip", combine([SKIP, 2]) == 1)
    ok("nothing run is not a pass", combine([]) == 1)

    ok("an image given by argument wins over the environment",
       resolve_image("given.bin", {layout.ENV_IMAGE: "env.bin"})
       == "given.bin")
    ok("with no argument the environment names it",
       resolve_image(None, {layout.ENV_IMAGE: "env.bin"}) == "env.bin")
    c.refuses("with neither, it is unavailable and names the variable",
              lambda: resolve_image(None, {}), layout.ENV_IMAGE, Unavailable)
    c.refuses("the English .cue's variable is not read in its place",
              lambda: resolve_image(None, {layout.ENV_DRIVE_IMAGE: "en.cue"}),
              layout.ENV_IMAGE, Unavailable)

    parser = build_parser()
    for words in (["sections"], ["pieces"], ["texture"], ["looks"],
                  ["looks", "A-A1-A-A-A"], ["check"], ["check", "x.bin"]):
        ok("the command line takes %s" % " ".join(words),
           parser.parse_args(words).command == words[0])


# --- the command line -------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py", description=__doc__.split("\n", 1)[0])
    sub = parser.add_subparsers(dest="command")
    for name, what in (("sections", "both model files, walked to their end"),
                       ("pieces", "the eleven pieces and how they were named"),
                       ("texture", "DAT2D.BIN's records and palettes"),
                       ("check", "every --check-image; 77 with no image")):
        one = sub.add_parser(name, help=what)
        one.add_argument("image", nargs="?")
    one = sub.add_parser("looks", help="the twelve rows, and a tuple")
    one.add_argument("tuple", nargs="?")
    one.add_argument("--image")
    return parser


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        return 1 if self_check() else 0
    args = build_parser().parse_args(argv[1:])
    if args.command is None:
        print(__doc__.strip())
        return 2
    try:
        if args.command == "looks":
            image = args.image or os.environ.get(layout.ENV_IMAGE)
            return cmd_looks(args.tuple, image)
        image = resolve_image(args.image)
        if args.command == "sections":
            return cmd_sections(image)
        if args.command == "pieces":
            return cmd_pieces(image)
        if args.command == "texture":
            return cmd_texture(image)
        return cmd_check(image)
    except Unavailable as exc:
        print("cli %s: skipped -- %s" % (args.command, exc))
        return SKIP
    except Exception as exc:  # noqa: BLE001 -- a refusal, said in one line
        import looks

        if not isinstance(exc, (looks.BadLooks, layout.WrongDisc)):
            raise
        print("cli %s: refused -- %s" % (args.command, exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
