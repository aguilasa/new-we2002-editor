#!/usr/bin/env python3
"""The fifty renders of the Superpack, against our viewer, with the game's metric.

Plan section 5.4.  The corpus is somebody else's: fifty JPGs under
`We2002\\MCR\\We DB - polipoli\\Faces\\`, named by the tuple they show.  Its value
is exactly that it did not come through our code -- the confrontation of
LOOKS-TASK-17 compares the game with a viewer built from the same table on both
halves of part of the path, and a systematic error on that path agrees with
itself.

**The metric is LOOKS-TASK-17's**, `confront.intersection` over the colours our
side draws, judged by `confront.verdict` -- every render against every one of
ours, the right tuple has to win its own row.  What is NOT the same is the
input, and the difference is measured rather than assumed:

* the emulator's frame carries the palette's 15-bit colours EXACTLY; a JPEG
  does not.  Compression moves a head's pixels off the palette, and a pixel-art
  face more than a flat background, so no threshold measured on one fits both;
* so each JPEG pixel is first SNAPPED to the nearest colour it could have come
  from, and the candidates are not only our palette: the background and the
  shirt are colours too, read off the JPEG's own corner and hem.  A pixel whose
  nearest source is the background or the shirt is not counted.  No distance
  threshold is chosen by hand, which is the point -- a threshold would be a
  number fitted to these fifty pictures.

**And the verdict is per FIELD, and the reason is a control, not the data.**
The 47-way matrix is scored with `confront.verdict` and printed, and most
tuples do not win it.  Before reading that as our render being wrong, the same
47 renders were scored against the emulator's own frames from LOOKS-TASK-17 --
exact colours, a tuple whose truth is known -- and the truth ranked third and
fourth there too.  What a colour histogram resolves is COLOUR: which skin row,
which hair colour, which beard colour.  It does not resolve SHAPE -- which hair
style, which beard -- because the camera and the pose move the proportions of
one colour against another by more than a style does.  So:

* the three colour fields are JUDGED: the best-scoring render must agree with
  the JPEG's name on each, and a disagreement fails;
* the two shape fields are REPORTED, never judged;
* a beard colour is judged only where the name has a beard: with `FACE` at `A`
  the beard's quads sample none of the entries a beard colour moves
  (CORR-LOOKS-038), so the colour is not in the picture to be read.

This split was written after the first run was read, and it says so for the
same reason `confront.verdict` does -- a rule written after the data is the
kind that fits it.  The control is what it leans on, and the control runs every
time the captures of LOOKS-TASK-17 are on disc.

Usage:
    python tools/looks/corpus.py --check
    python tools/looks/corpus.py --run [folder]     # renders ours, then scores
    python tools/looks/corpus.py --score [folder]   # the saved renders only
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import confront  # noqa: E402
import harness  # noqa: E402
import looks  # noqa: E402

SKIP = 77

FIGURE = 0
"""The corpus shows the outfield player: a lavender shirt with a collar, the
same kit slot 2 wears on LOOKS SET, and no goalkeeper's gloves anywhere."""

SLOT = "corpus"
"""The key `confront.verdict` files the judgement under.  Nothing is expected:
a residue here is a finding."""

OUT_DIR = os.path.join("work", "looks-corpus")

BACKGROUND_BOX = (0.02, 0.02, 0.20, 0.16)
"""The top-left corner, as fractions: flat teal in all 49 tuple renders."""

SHIRT_BOX = (0.22, 0.95, 0.77, 1.00)
"""The bottom strip under the neck, as fractions: the shirt's lavender and its
shading, and nothing of the head in any of the 49."""

BLANK = "a blank picture: one colour and no figure"

COLOUR_FIELDS = ("skin_colour", "hair_colour", "beard_colour")
SHAPE_FIELDS = ("hair_style", "beard_style")

CONTROL_DIR = os.path.join("work", "looks-confront")
CONTROL_SLOT = 2
"""The captures LOOKS-TASK-17 leaves: the outfield player, figure 0, the same
figure as the corpus."""

WORST = 6
"""How many of the lowest self-scores are drawn into the strip and printed."""


class CorpusError(Exception):
    """A corpus that could not be measured, or measured wrong."""


class Unavailable(Exception):
    """The machine cannot run this.  Reported as 77."""


# ---- reading --------------------------------------------------------------

def read_jpeg(path: str) -> tuple:
    """(width, height, 3, [row bytes]) -- the shape `confront` reads.

    PIL, lazily: the standard library has no JPEG decoder, and the gate that
    needs no venv must not need PIL to import this module.
    """
    try:
        from PIL import Image
    except ImportError:
        raise Unavailable("PIL is not installed, so the JPGs cannot be "
                          "read") from None
    image = Image.open(path).convert("RGB")
    width, height = image.size
    data = image.tobytes()
    return (width, height, 3,
            [data[y * width * 3:(y + 1) * width * 3] for y in range(height)])


def colours_in(shot, box) -> set:
    width, height, channels, rows = shot
    x0, y0 = int(box[0] * width), int(box[1] * height)
    x1, y1 = int(box[2] * width), int(box[3] * height)
    return {tuple(rows[y][x * channels:x * channels + 3])
            for y in range(y0, y1) for x in range(x0, x1)}


def palette_of(shot) -> set:
    """Every exact colour one of OUR renders draws, background left out."""
    width, height, channels, rows = shot
    back = tuple(rows[0][0:3])
    return {tuple(rows[y][x * channels:x * channels + 3])
            for y in range(height) for x in range(width)} - {back}


def snapped_histogram(shot, palette, sinks) -> dict:
    """{15-bit colour: count} of a JPEG, each pixel given to its nearest source.

    `palette` are the colours our side can draw, `sinks` the JPEG's own
    background and shirt.  Nearest is squared distance in 8-bit RGB, and a tie
    goes to the sink -- a pixel that could as well be background is not
    evidence about the head.
    """
    width, height, channels, rows = shot
    candidates = [(colour, True) for colour in sorted(sinks)] + \
                 [(colour, False) for colour in sorted(palette - sinks)]
    cache: dict = {}
    out: dict = {}
    for y in range(height):
        row = rows[y]
        for x in range(width):
            pixel = row[x * channels:x * channels + 3]
            if pixel not in cache:
                best, sink = None, True
                far = None
                for colour, is_sink in candidates:
                    d = sum((pixel[i] - colour[i]) ** 2 for i in range(3))
                    if far is None or d < far:
                        best, sink, far = colour, is_sink, d
                cache[pixel] = None if sink else confront.quantise(best)
            colour = cache[pixel]
            if colour is not None:
                out[colour] = out.get(colour, 0) + 1
    return out


def is_blank(shot) -> bool:
    width, height, channels, rows = shot
    first = rows[0][0:3]
    return all(rows[y][x * channels:x * channels + 3] == first
               for y in range(height) for x in range(width))


# ---- judging --------------------------------------------------------------

def judge(renders: dict, ours: dict) -> tuple:
    """(scores, alike, judged) for the corpus.

    `renders[name]` is a JPEG's snapped histogram, `ours[name]` our render's
    histogram.  Every render is scored against every one of ours, exactly as a
    game frame is in LOOKS-TASK-17.
    """
    scores = {(name, other): confront.intersection(renders[name], ours[other])
              for name in renders for other in ours}
    alike = {(a, b): (1.0 if ours[a] == ours[b]
                      else confront.intersection(ours[a], ours[b]))
             for a in ours for b in ours if a != b}
    judged = confront.verdict(scores, SLOT, alike, expected={})
    return scores, alike, judged


def visible(field: str, values: dict) -> bool:
    """Is this field in the picture at all, for this tuple?

    Only the beard colour can be absent, and it is absent exactly when there
    is no beard: CORR-LOOKS-038 measured band 0 sampling none of the six
    entries a beard colour moves.
    """
    if field == "beard_colour":
        base = looks.parse_tuple("A-A1-A-A-A")["beard_style"]
        return values["beard_style"] != base
    return True


def fields(histograms: dict, ours: dict) -> dict:
    """{name: {field: 'agree' | 'DISAGREE' | 'invisible'}} plus the best render.

    The best render is the argmax of the intersection over ALL of ours.  Each
    field of the name is compared with the same field of the best render's
    tuple.  Returned as `{name: (best, {field: outcome})}`.
    """
    out = {}
    for name, hist in histograms.items():
        best = max(sorted(ours),
                   key=lambda o: confront.intersection(hist, ours[o]))
        want, got = looks.parse_tuple(name), looks.parse_tuple(best)
        verdicts = {}
        for field in looks.TUPLE_ORDER:
            if not visible(field, want):
                verdicts[field] = "invisible"
            else:
                verdicts[field] = ("agree" if want[field] == got[field]
                                   else "DISAGREE")
        out[name] = (best, verdicts)
    return out


def field_failures(judged_fields: dict) -> list:
    """(name, field, best) for every colour field that disagrees."""
    return [(name, field, best)
            for name, (best, verdicts) in sorted(judged_fields.items())
            for field in COLOUR_FIELDS if verdicts[field] == "DISAGREE"]


def say_fields(label: str, judged_fields: dict) -> None:
    total = len(judged_fields)
    parts = []
    for field in COLOUR_FIELDS + SHAPE_FIELDS:
        seen = [v[field] for _b, v in judged_fields.values()]
        judged = [x for x in seen if x != "invisible"]
        parts.append("%s %d/%d%s" % (field, judged.count("agree"), len(judged),
                                     "" if field in COLOUR_FIELDS
                                     else " (reported)"))
    print("      %s, %d picture(s), the best render agrees on: %s"
          % (label, total, ", ".join(parts)))


def groups(scores: dict, names) -> dict:
    """{(hair style is A1, skin is A): [self-scores]} -- where the corpus is low.

    The head of style A1 is the section every colour row's primitive indices
    were measured on; the other heads use them by borrowing.  Grouping the
    self-score that way is what turned "the I3 renders score badly" into a
    claim about which renders.
    """
    out: dict = {}
    for name in names:
        values = looks.parse_tuple(name)
        base = looks.parse_tuple("A-A1-A-A-A")
        key = (values["hair_style"] == base["hair_style"],
               values["skin_colour"] == base["skin_colour"])
        out.setdefault(key, []).append(scores[(name, name)])
    return out


# ---- the gate -------------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    return harness.run("corpus.py", _checks, verbose)


def _shot(pixels, width):
    rows = [bytes(v for p in pixels[i:i + width] for v in p)
            for i in range(0, len(pixels), width)]
    return (width, len(rows), 3, rows)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt

    skin = (200, 160, 112)
    hair = (16, 16, 16)
    teal = (72, 128, 128)
    shirt = (144, 136, 208)
    # A JPEG pixel moved a few steps from the skin, and one moved from teal.
    noisy_skin = (206, 155, 118)
    noisy_teal = (78, 122, 134)
    jpeg = _shot([noisy_skin, noisy_skin, hair, noisy_teal, teal, shirt], 3)
    hist = attempt("snap a synthetic JPEG",
                   lambda: snapped_histogram(jpeg, {skin, hair}, {teal, shirt}),
                   default={})
    ok("a pixel moved by compression lands on the colour it came from",
       hist.get(confront.quantise(skin)) == 2, "%r" % (hist,))
    ok("and a background pixel counts for nothing, however noisy",
       sum(hist.values()) == 3, "%r" % (hist,))
    ok("a pixel as near a sink as the palette is not evidence",
       snapped_histogram(_shot([(100, 100, 100)], 1), {(90, 100, 100)},
                         {(110, 100, 100)}) == {})

    ours = {"A": {confront.quantise(skin): 8, confront.quantise(hair): 2},
            "B": {confront.quantise((152, 104, 56)): 8,
                  confront.quantise(hair): 2}}
    renders = {"A": {confront.quantise(skin): 5, confront.quantise(hair): 1},
               "B": {confront.quantise((152, 104, 56)): 6,
                     confront.quantise(hair): 1}}
    _scores, _alike, judged = judge(renders, ours)
    ok("the verdict is LOOKS-TASK-17's, with nothing expected",
       judged.get("A", ("",))[0] == "win" and judged.get("B", ("",))[0]
       == "win", "%r" % (judged,))
    crossed = judge({"A": renders["B"], "B": renders["A"]}, ours)[2]
    ok("a render filed under the wrong tuple fails", all(
        outcome == "unexplained" for outcome, _why in crossed.values()),
       "%r" % (crossed,))

    beardless = looks.parse_tuple("A-A1-C-A-A")
    bearded = looks.parse_tuple("A-A1-C-F-C")
    ok("a beard colour is not in a picture with no beard",
       not visible("beard_colour", beardless))
    ok("and is, with one", visible("beard_colour", bearded))
    ok("the other colour fields are always in the picture",
       visible("skin_colour", beardless) and visible("hair_colour", beardless))

    hists = {"A-A1-A-A-A": {1: 5}, "B-A1-A-A-A": {2: 5}}
    mine = {"A-A1-A-A-A": {1: 5}, "B-A1-A-A-A": {2: 5}}
    judged_fields = fields(hists, mine)
    ok("a render that picks its own tuple agrees on every field",
       all(v == "agree" for v in judged_fields["A-A1-A-A-A"][1].values()
           if v != "invisible"), "%r" % (judged_fields,))
    swapped = fields({"A-A1-A-A-A": {2: 5}}, mine)
    ok("a render that picks the other skin disagrees on skin, and fails",
       field_failures(swapped) == [("A-A1-A-A-A", "skin_colour",
                                    "B-A1-A-A-A")], "%r" % (swapped,))
    shape = fields({"A-I3-A-A-A": {1: 5}}, {"A-A1-A-A-A": {1: 5}})
    ok("a shape field that disagrees is reported, not failed",
       shape["A-I3-A-A-A"][1]["hair_style"] == "DISAGREE"
       and field_failures(shape) == [], "%r" % (shape,))
    hidden = fields({"A-A1-C-A-A": {3: 5}}, {"A-A1-C-F-C": {3: 5}})
    ok("a beard colour that cannot be seen does not fail",
       field_failures(hidden) == [], "%r" % (hidden,))

    ok("a one-colour picture is blank", is_blank(_shot([teal] * 4, 2)))
    ok("and a picture with a figure is not", not is_blank(jpeg))
    ok("the palette of a render leaves its background out",
       palette_of(_shot([teal, skin, hair, teal], 2)) == {skin, hair})
    ok("the two sink boxes are inside the picture and do not overlap",
       BACKGROUND_BOX[3] < SHIRT_BOX[1]
       and all(0.0 <= v <= 1.0 for v in BACKGROUND_BOX + SHIRT_BOX))


# ---- the run ---------------------------------------------------------------

def out_dir() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), OUT_DIR)


def names_of(folder: str) -> tuple:
    """(tuples, blanks, not tuples) among the corpus files."""
    import ui_check  # noqa: F401 -- the PNG reader lives there

    tuples, blanks, others = [], [], []
    for name in looks.corpus_names(folder):
        stem = name[:-len(looks.CORPUS_SUFFIX)]
        try:
            looks.parse_tuple(stem)
        except looks.BadLooks as exc:
            shot = read_jpeg(os.path.join(folder, name))
            (blanks if is_blank(shot) else others).append((stem, str(exc)))
        else:
            tuples.append(stem)
    return tuples, blanks, others


def render_all(tuples, where) -> None:
    confront._python_and_app()
    os.makedirs(where, exist_ok=True)
    for text in tuples:
        path = os.path.join(where, "ours-%s.png" % text)
        for stale in (path, path + confront.REFUSED):
            if os.path.exists(stale):
                os.remove(stale)
        picture, why = confront.render(text, FIGURE, path)
        if picture is None:
            with open(path + confront.REFUSED, "w", encoding="utf-8") as out:
                out.write(why + "\n")


def score(folder: str, where: str | None = None, worst: int = 6) -> int:
    import ui_check

    where = where or out_dir()
    tuples, blanks, others = names_of(folder)
    print("  the corpus: %s" % folder)
    print("      %d file(s): %d tuple(s), %d blank, %d other"
          % (len(tuples) + len(blanks) + len(others), len(tuples),
             len(blanks), len(others)))
    for stem, why in blanks:
        print("      %s.jpg -- %s; not a tuple (%s), left out of the score"
              % (stem, BLANK, why.split(":")[0]))
    for stem, why in others:
        print("      %s.jpg -- NOT a tuple and NOT blank: %s" % (stem, why))

    ours, palettes, refused = {}, {}, {}
    for text in tuples:
        kind, found = _side(where, text)
        if kind == "refused":
            refused[text] = found
            continue
        shot = ui_check.picture(found)
        palettes[text] = palette_of(shot)
        ours[text] = confront.histogram(
            shot, drop=confront.quantise(shot[3][0][0:3]))
    palette = set().union(*palettes.values()) if palettes else set()
    print("      our side: %d drawn, %d refused, %d colour(s) drawn in all"
          % (len(ours), len(refused), len(palette)))
    for text, why in sorted(refused.items()):
        print("      refused %s -- %s" % (text, why))

    renders = {}
    for text in ours:
        shot = read_jpeg(os.path.join(folder, text + looks.CORPUS_SUFFIX))
        sinks = colours_in(shot, BACKGROUND_BOX) | colours_in(shot, SHIRT_BOX)
        renders[text] = snapped_histogram(shot, palette, sinks)
    scores, alike, judged = judge(renders, ours)

    counts = {kind: sorted(t for t, (o, _w) in judged.items() if o == kind)
              for kind in ("win", "ranked", "unexplained")}
    print("      the %d-way matrix, confront.verdict: %d win, %d ranked, %d "
          "not first -- shape is beyond the metric, see the control"
          % (len(ours), len(counts["win"]), len(counts["ranked"]),
             len(counts["unexplained"])))

    control = _control(ours, palette)
    corpus_fields = fields(renders, ours)
    say_fields("the corpus", corpus_fields)
    failures = field_failures(corpus_fields)
    for name, field, best in failures:
        print("      COLOUR FIELD MISSED: %s picks %s on %s" % (name, best,
                                                               field))

    print("      self-score, grouped by head and skin:")
    for (a1, skin_a), values in sorted(groups(scores, ours).items(),
                                       reverse=True):
        print("        hair style %-6s skin %-6s %2d picture(s), mean %.3f, "
              "lowest %.3f" % ("A1" if a1 else "not A1",
                               "A" if skin_a else "not A", len(values),
                               sum(values) / len(values), min(values)))

    order = sorted(ours, key=lambda t: scores[(t, t)])
    print("      the %d lowest self-scores -- drawn beside ours in %s:"
          % (WORST, os.path.join(where, "worst.png")))
    for text in order[:WORST]:
        best, verdicts = corpus_fields[text]
        print("        %-12s own %.3f  best %-12s %.3f  shape: %s"
              % (text, scores[(text, text)], best, scores[(text, best)],
                 ", ".join("%s %s" % (f, verdicts[f].lower())
                           for f in SHAPE_FIELDS)))
    _strip(folder, where, order[:WORST])

    bad = len(failures) + control
    print("corpus: %s" % ("ok" if not bad else "%d failure(s)" % bad))
    return bad


def _control(ours: dict, palette: set) -> int:
    """The emulator's frames of LOOKS-TASK-17 through the same 47 renders.

    Exact colours and a known truth, so what fails here is the metric and not
    the corpus.  Absent captures are said, and count as nothing either way.
    """
    import ui_check

    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    where = os.path.join(root, CONTROL_DIR)
    palette15 = {confront.quantise(colour) for colour in palette}
    frames = {}
    for text in confront.TUPLES:
        path = os.path.join(where, "game-%d-%s.png" % (CONTROL_SLOT, text))
        if text in ours and os.path.exists(path):
            frames[text] = confront.restrict(
                confront.histogram(ui_check.picture(path),
                                   box=confront.PANEL), palette15)
    if not frames:
        print("      control: not run -- no captures of LOOKS-TASK-17 under "
              "%s" % where)
        return 0
    judged_fields = fields(frames, ours)
    for text in sorted(frames):
        ranked = sorted(ours, key=lambda o: -confront.intersection(
            frames[text], ours[o]))
        print("      control %-12s the emulator's own frame ranks its tuple "
              "%d of %d" % (text, ranked.index(text) + 1, len(ours)))
    say_fields("the control", judged_fields)
    misses = field_failures(judged_fields)
    for name, field, best in misses:
        print("      CONTROL MISSED A COLOUR FIELD: %s picks %s on %s -- the "
              "premise of judging colour is broken" % (name, best, field))
    return len(misses)


def _strip(folder: str, where: str, names) -> None:
    """The JPEG beside our render, one row per name.  Looked at, not scored."""
    from PIL import Image

    rows = []
    for text in names:
        theirs = Image.open(os.path.join(folder, text + looks.CORPUS_SUFFIX)) \
            .convert("RGB")
        width, height = theirs.size
        ours_image = Image.open(os.path.join(where, "ours-%s.png" % text)) \
            .convert("RGB").resize((height, height))
        side = (height - width) // 2
        rows.append((theirs, ours_image.crop((side, 0, side + width, height))))
    if not rows:
        return
    width, height = rows[0][0].size
    sheet = Image.new("RGB", (2 * width, height * len(rows)))
    for index, (theirs, ours_image) in enumerate(rows):
        sheet.paste(theirs, (0, index * height))
        sheet.paste(ours_image, (width, index * height))
    sheet.save(os.path.join(where, "worst.png"))


def _side(where: str, text: str) -> tuple:
    path = os.path.join(where, "ours-%s.png" % text)
    drawn = os.path.exists(path)
    refused = os.path.exists(path + confront.REFUSED)
    if drawn and refused:
        raise CorpusError("%s has both a render and a refusal -- re-run "
                          "--run" % text)
    if refused:
        with open(path + confront.REFUSED, encoding="utf-8") as handle:
            return ("refused", handle.read().strip())
    if not drawn:
        raise CorpusError("%s has no render under %s -- run --run first"
                          % (text, where))
    return ("drawn", path)


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        return 1 if self_check() else 0
    if len(argv) >= 2 and argv[1] in ("--run", "--score"):
        try:
            folder = looks.corpus_from_env(argv[2] if len(argv) > 2 else None)
        except RuntimeError as exc:
            print("corpus: skipped -- %s" % exc)
            return SKIP
        try:
            if argv[1] == "--run":
                tuples, _blanks, _others = names_of(folder)
                render_all(tuples, out_dir())
            return 1 if score(folder) else 0
        except Unavailable as exc:
            print("corpus: skipped -- %s" % exc)
            return SKIP
        except (CorpusError, confront.ConfrontError) as exc:
            print("corpus FAILED: %s" % exc, file=sys.stderr)
            return 1
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
