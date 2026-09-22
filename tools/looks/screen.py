#!/usr/bin/env python3
"""The LOOKS SET screen as the game draws it: every text, the help, the cursor, the boxes.

Provenance (plan section 3.4):

    container   --
    address     layout.py, as always -- this module holds none
    codec       IN HOUSE, and checked against the game's own glyph routine:
                the strings the screen prints carry control bytes, and what
                `decode()` makes of them is compared, on every run of the
                measurement, with the glyphs the game actually draws
    semantics   MEASURED.  Nothing in the table is transcribed: it is written
                by `oracle.py --screen --write`, walking every row of both
                save states, and re-measured by `oracle.py --screen`

## Why the table is a file and not a literal

Trap 17 of the cycle profile: a screen text invented from a label is the error
the whole screen phase exists not to make.  So the texts -- `A1 TYPE`, `175 cm`,
`RIGHT`, the nations, the help of each row -- live in `screen.json`, which ONE
tool writes and the same tool re-checks, and this module only reads it.  A hand
edit of the JSON is a generated file edited by hand, and `--screen` goes red on
the next run.

## What a row's text is

The screen prints its rows through five text objects, not twelve: the labels
are one multi-line string, the units (`O.K.`, `TYPE`, `cm`) another, the
values of SKIN to BOOTS a third, and NAT and FOOT one each.  A row's text is
every piece that lands on its line, left to right, joined by one space --
`A1` and `TYPE` make `A1 TYPE`.  Left to right is the order the glyph routine
draws them in, and the measurement learns it from there rather than from the
objects, whose own order says nothing about where they land.

Usage:
    python tools/looks/screen.py --check
    python tools/looks/screen.py --report
"""

from __future__ import annotations

import io
import json
import os
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import harness  # noqa: E402
import looks  # noqa: E402

TABLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screen.json")

NEWLINE = 0x0A  # not-an-address: a control byte
TAB = 0x09  # not-an-address: a control byte
COLOUR = 0x0D  # not-an-address: a control byte
"""The three control bytes the ASCII strings of this screen carry.

Read off the strings the game passes to its print routine and checked against
the glyphs it draws: `\\n` opens the next line, `\\t` and ONE byte after it
move the pen (`\\t\\x12A\\t\\x1e1` draws `A1`), `\\r` and THREE bytes after it
set a colour (`\\r\\x80\\x80\\x80O.K.` draws `O.K.`).  Any other byte below the
printable range is refused rather than skipped: skipping an unknown code is how
a decoder draws `A` where the game draws `A1`.
"""

TAB_ARGUMENTS = 1
COLOUR_ARGUMENTS = 3
PRINTABLE = (0x20, 0x7E)  # not-an-address: the ASCII range

GREY_FLOOR = 150
EDGE_ACROSS = 24
EDGE_DOWN = 12
"""A box edge: a run of neutral grey at least this long.

The three boxes of the screen -- the player's panel, the twelve rows, the help
-- are drawn with a one-pixel border in exact grey (173,173,173 or
189,189,189 on the native frame).  The letters are not neutral, and no stroke
of the 8 px font is 12 px tall or 24 px wide, so these floors keep text out.
"""

TITLE_FONT = "-12AEJSTW"
"""The characters the title's font has a glyph for.

The title is printed with the second of the two ASCII fonts (`kind` 33), and
that one does NOT go through the glyph routine the rows are checked against --
measured, nothing at all is drawn on the title's line by it.  What its font
draws was measured instead on 2026-09-17, by writing an eleven-byte marker over
the string the title object points at, in the RAM of the running game, and
reading the band back off VRAM (the state was reloaded afterwards, and the
string read `LOOKS SET  ` again):

    AAAAAAAAAAA   draws eleven As
    ABCDEFGHIJK   draws AEJ
    0123456789A   draws 12A

Of the seventy-one printable characters swept one at a time, these nine draw;
the other sixty-two draw NOTHING AND DO NOT MOVE THE PEN.  A space moves it
without drawing: five of them push the next glyph 42 px right.

So the screen's own title is `S SET` -- `LOOK` has no glyph and is skipped --
and that is the game drawing, not a capture cut short: the band holds the same
four letters over 600 frames.  Whoever draws this screen writes what the screen
writes, and `screen.json` keeps both (CORR-LOOKS-054).
"""

TITLE_BAND = 14
"""Rows of the title's own band, from its object's y down.  Measured: its
letters fill rows 21 to 30 of the native frame for an object at y=20, and the
next text below starts at 41."""

INK_FLOOR = 200
"""The title's letters are neutral white -- (239,239,239) on the native frame.
The teal banner behind them, the grey borders (173 and 189) and the lavender of
the rows are not."""

INK_GAP = 4
"""Empty columns between two letters of the title's font.

Measured on the eleven-A marker: exactly four between each pair, and no gap of
two inside a glyph.  The space of `S SET` leaves sixteen, which is the same
separation read wider -- counting runs counts letters either way."""

CURSOR_FLOOR = 64
"""The cursor box is yellow -- red equal to green, blue under half of them.

It pulses, and the phases measured on the native frame are (132,132,8),
(181,181,57) and (189,189,66).  This said "blue under a quarter" until the
brighter two were met, which it refused, and the walk lost the cursor.  The
background teal (0,49,49), the grey borders and the lavender letters
(115,115,247) do not match the shape."""


class BadScreen(Exception):
    """A string, an image or a table that does not say what this expects."""


# ---- the strings ------------------------------------------------------------

def decode(raw: bytes) -> list:
    """The lines a string of this screen draws, control bytes taken out."""
    lines, current, at = [], [], 0
    while at < len(raw):
        byte = raw[at]
        if byte == NEWLINE:
            lines.append("".join(current))
            current = []
            at += 1
        elif byte == TAB:
            at += 1 + TAB_ARGUMENTS
        elif byte == COLOUR:
            at += 1 + COLOUR_ARGUMENTS
        elif PRINTABLE[0] <= byte <= PRINTABLE[1]:
            current.append(chr(byte))
            at += 1
        else:
            raise BadScreen("byte %#04x at %d of %r is not a character and not "
                            "one of the three control codes this screen uses"
                            % (byte, at, raw))
    if at != len(raw):
        raise BadScreen("%r ends inside the arguments of a control code" % raw)
    lines.append("".join(current))
    return lines


def line_tokens(raw: bytes) -> list:
    """Each line of a string as the tokens its pen follows.

    `[["tab", column] | ["colour", [r, g, b]] | ["text", characters], ...]`
    per line: a tab puts the pen at `column` pixels from the object's x, a
    colour is what every glyph after it is modulated by -- and it holds into
    the lines below, since the game writes it into the object --, and text is
    laid from wherever the pen is.  Read off the print routine's jump table
    (0x800FC048 in /SELECTC.BIN): code 9 goes to 0x8010C690, which sets the
    pen to the object's x plus the byte, and code 13 to 0x8010C730, which
    stores the three bytes as the object's colour.  This is what
    `glyphs.Font.place` lays out (LOOKS-TASK-38).
    """
    decode(raw)  # refuses a byte that is none of the three codes
    lines, current, at = [[]], None, 0
    while at < len(raw):
        byte = raw[at]
        if byte == NEWLINE:
            lines.append([])
            current = None
            at += 1
        elif byte == TAB:
            lines[-1].append(["tab", raw[at + 1]])
            current = None
            at += 1 + TAB_ARGUMENTS
        elif byte == COLOUR:
            lines[-1].append(["colour",
                              list(raw[at + 1:at + 1 + COLOUR_ARGUMENTS])])
            current = None
            at += 1 + COLOUR_ARGUMENTS
        else:
            if current is None:
                current = ["text", ""]
                lines[-1].append(current)
            current[1] += chr(byte)
            at += 1
    return lines


def colour_at(lines, number: int, colour) -> list:
    """The colour in force as line *number* of an object starts: the object's
    own, changed by every colour code of the lines above it."""
    for line in lines[:number]:
        for kind, value in line:
            if kind == "colour":
                colour = value
    return list(colour)


def tokens_text(tokens) -> str:
    """The characters of a line's tokens, tabs left out."""
    return "".join(value for kind, value in tokens if kind == "text")


def make_printable(stream) -> bool:
    """Let *stream* carry the text the game draws, whatever the console is.

    The help of a row holds the button glyph `■` (U+25A0), and this machine's
    standard output is cp1252, which has no such character.  Printing it there
    raises `UnicodeEncodeError` -- `--report` died on the third of the twelve
    rows, and the message `oracle._walk_row` raises when the cursor missed a
    row would have died in the same place, in the print of its own failure
    (CORR-LOOKS-055).

    So the stream is asked for UTF-8, and for `replace` on top of it: a console
    that cannot carry a character prints a substitute, and nothing anywhere
    stops to complain.  What is NOT done is taking the `■` out of the
    measurement -- it is what the screen draws.
    """
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is None:  # a stream someone replaced with their own object
        return False
    reconfigure(encoding="utf-8", errors="replace")
    return True


def printable_output() -> None:
    """Both standard streams, for the main() of a tool that prints this text."""
    make_printable(sys.stdout)
    make_printable(sys.stderr)


def help_text(raw: bytes) -> str:
    """The help box's Shift-JIS full-width string, as the letters a person reads.

    NFKC folds the full-width forms (`Ｓｋｉｎ`) into ASCII and keeps the button
    glyph `■` as it is; trailing blanks are layout, not text.
    """
    try:
        text = raw.decode("cp932")
    except UnicodeDecodeError as exc:
        raise BadScreen("the help string %r is not Shift-JIS: %s"
                        % (raw, exc)) from None
    return unicodedata.normalize("NFKC", text).rstrip()


def title_drawn(text: str) -> str:
    """What the title band SHOWS of the string the title object holds.

    A character the font has no glyph for is skipped, pen and all; a space
    moves the pen and draws nothing.  Trailing spaces move it past the last
    letter, so they are not part of what anyone reads.
    """
    return "".join(character for character in text
                   if character == " " or character in TITLE_FONT).rstrip()


def title_skipped(text: str) -> str:
    """The characters of *text* the title's font has no glyph for, in order.

    `LOOK` of `LOOKS SET`.  Kept beside the title in the table because it is
    the difference itself: if the font, the string or the screen changes, this
    is what changes with them.
    """
    return "".join(character for character in text
                   if character != " " and character not in TITLE_FONT)


def glyph_strings(calls) -> list:
    """(x, y, text) of every string the glyph routine DREW, in drawing order.

    *calls* are `(code, x, y, pass)` in call order.  Pass 1 measures the width
    with every glyph at one x and is not what the screen shows; pass 0 draws.
    A string ends where the line changes, the pen moves left, or a measuring
    pass begins -- the next object's.
    """
    out, current = [], None
    for code, x, y, measuring in calls:
        if measuring:
            current = None
            continue
        if current is None or y != current[1] or x < current[3]:
            current = [x, y, [], x]
            out.append(current)
        if not PRINTABLE[0] <= code <= PRINTABLE[1]:
            raise BadScreen("glyph %#x at (%d, %d) is outside the ASCII font"
                            % (code, x, y))
        current[2].append(chr(code))
        current[3] = x
    return [(x, y, "".join(chars)) for x, y, chars, _ in out]


# ---- rows ---------------------------------------------------------------------

def row_of(y: int, row0_y: int, pitch: int):
    """Which row a line at *y* lands on, or None off the grid."""
    offset = y - row0_y
    if offset % pitch:
        return None
    index = offset // pitch
    return index if 0 <= index < len(looks.SCREEN) else None


def in_rows(obj, left: int, top: int) -> bool:
    """Does a text object print inside the rows box?

    By the box it is laid out in, not by where it starts: NAT's object sits at
    x=-80 while it prints `Unknown` and at x=-104 once it prints a nation,
    both times 296 wide, and a test on x alone threw every nation away.  What
    is left out is what the box does not reach -- the plate and the shirt name,
    whose boxes end before the rows box begins -- and what sits above its top,
    the title.
    """
    return obj["x"] + obj["width"] > left and obj["y"] >= top


def pieces(objects, row0_y: int, pitch: int, left: int, top: int) -> dict:
    """{row name: {object key: piece}} for the objects inside the rows box.

    An object is `{"at", "x", "y", "width", "lines"}`; its key is `at`, where
    the object itself lives.  Not its position: NAT's object moves 24 pixels
    left when `Unknown` becomes a nation, and a key of `(x, y)` turned the same
    object into one the measured order had never seen.
    """
    out = {name: {} for name in looks.SCREEN}
    for obj in objects:
        if not in_rows(obj, left, top):
            continue
        stripped = [line.strip() for line in obj["lines"]]
        if stripped == list(looks.SCREEN):
            continue
        for number, text in enumerate(stripped):
            index = row_of(obj["y"] + number * pitch, row0_y, pitch)
            if index is None or not text:
                continue
            out[looks.SCREEN[index]][obj["at"]] = text
    return out


def labels_object(objects):
    """The object that prints the twelve row names, or a refusal."""
    found = [obj for obj in objects
             if [line.strip() for line in obj["lines"]] == list(looks.SCREEN)]
    if len(found) != 1:
        raise BadScreen("%d object(s) print the twelve row names, and the "
                        "screen has one" % len(found))
    return found[0]


def compose(row_pieces: dict, order: list) -> str:
    """One row's text: its pieces in the left-to-right *order*, one space apart.

    *order* is a list of object keys.  A piece whose object is not in it is a
    refusal: it would land somewhere the measurement never saw it land.
    """
    unknown = [key for key in row_pieces if key not in order]
    if unknown:
        raise BadScreen("pieces from %s, and the measured order is %s"
                        % (unknown, order))
    return " ".join(row_pieces[key] for key in order if key in row_pieces)


# ---- the native frame ------------------------------------------------------

def _grey(pixel) -> bool:
    red, green, blue = pixel[:3]
    return red == green == blue and red >= GREY_FLOOR


def boxes(rows, width: int, height: int) -> list:
    """Every rectangle with a closed one-pixel grey border, as (x0, y0, x1, y1).

    *rows* is a list of rows of pixels, the frame at native resolution.
    Inclusive corners.  Only a box whose four edges are all there counts -- an
    open shape is not a box of this screen.
    """
    runs = []
    for y in range(height):
        row, x = rows[y], 0
        while x < width:
            if _grey(row[x]):
                start = x
                while x < width and _grey(row[x]):
                    x += 1
                if x - start >= EDGE_ACROSS:
                    runs.append((start, x - 1, y))
            else:
                x += 1
    found = []
    for x0, x1, top in runs:
        for other_x0, other_x1, bottom in runs:
            if (other_x0, other_x1) != (x0, x1) or bottom - top < EDGE_DOWN:
                continue
            if all(_grey(rows[y][x0]) and _grey(rows[y][x1])
                   for y in range(top, bottom + 1)):
                found.append((x0, top, x1, bottom))
                break
    return sorted(set(found))


def cursor(rows, box) -> tuple | None:
    """The bounding box of the yellow cursor inside *box*, or None."""
    x0, y0, x1, y1 = box
    seen = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
            if _yellow(rows[y][x])]
    if not seen:
        return None
    xs, ys = [x for x, _ in seen], [y for _, y in seen]
    return (min(xs), min(ys), max(xs), max(ys))


def _yellow(pixel) -> bool:
    red, green, blue = pixel[:3]
    return red == green and red >= CURSOR_FLOOR and blue * 2 < red


def _white(pixel) -> bool:
    red, green, blue = pixel[:3]
    return red == green == blue and red >= INK_FLOOR


def title_band(anchor, width: int, origin) -> tuple:
    """The title's band on the native frame, from its object's own anchor.

    *anchor* and *width* are the object's, in coordinates of the display's
    centre; *origin* is that centre.  Inclusive corners, like `boxes`.
    """
    x = anchor[0] + origin[0]
    y = anchor[1] + origin[1]
    return (x, y, x + width - 1, y + TITLE_BAND - 1)


def ink_runs(rows, box) -> list:
    """The white letters inside *box*, as (first column, last column).

    The title is the one text of this screen drawn by a font the glyph routine
    never reports, so what it drew is counted off the finished frame instead of
    read off a call -- one run per letter, `TITLE_FONT` says which.
    """
    x0, y0, x1, y1 = box
    columns = sorted({x for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
                      if _white(rows[y][x])})
    out, start = [], None
    for index, x in enumerate(columns):
        if start is None:
            start = x
        if index + 1 == len(columns) or columns[index + 1] - x >= INK_GAP:
            out.append((start, x))
            start = None
    return out


def fraction(box, display) -> list:
    """A native box as fractions of the display, for a window of any size."""
    width, height = display
    x0, y0, x1, y1 = box
    return [round(x0 / width, 6), round(y0 / height, 6),
            round((x1 + 1) / width, 6), round((y1 + 1) / height, 6)]


# ---- the table ---------------------------------------------------------------

def load(path: str = TABLE) -> dict:
    with open(path, encoding="utf-8") as handle:
        table = json.load(handle)
    problems = validate(table)
    if problems:
        raise BadScreen("%s does not hold together: %s"
                        % (path, "; ".join(problems)))
    return table


def write(table: dict, path: str = TABLE) -> None:
    """Only the measurement calls this.  It refuses a table that does not
    validate, so a broken walk cannot become the reference."""
    problems = validate(table)
    if problems:
        raise BadScreen("refusing to write a table that does not hold "
                        "together: %s" % "; ".join(problems))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(table, handle, ensure_ascii=False, indent=1, sort_keys=True)
        handle.write("\n")


def validate(table: dict) -> list:
    """What makes a table usable, each a sentence.  Empty is good."""
    problems = []
    rows = table.get("rows", {})
    if list(table.get("order_of_rows", [])) != list(looks.SCREEN):
        problems.append("the rows are not the twelve of looks.SCREEN in order")
    helps = []
    for name in looks.SCREEN:
        row = rows.get(name)
        if row is None:
            problems.append("row %s is missing" % name)
            continue
        texts = row.get("texts", [])
        if not texts:
            problems.append("row %s has no text" % name)
        if len(set(texts)) != len(texts):
            problems.append("row %s repeats a text, so a value could not be "
                            "told from its neighbour" % name)
        for end in ("left", "right"):
            if row.get(end) not in ("locks", "wraps"):
                problems.append("row %s: the %s end is %r"
                                % (name, end, row.get(end)))
        helps.append(row.get("help"))
        problems += _arrow_problems(name, row)
        problems += _layout_problems(name, row)
        problems += _cursor_problems(name, row, table)
        label = row.get("label", "missing")
        if label == "missing":
            problems.append("row %s does not say whether Left takes the "
                            "cursor to its label" % name)
        elif label is not None:
            problems += _label_problems(name, label)
            helps.append(label.get("help"))
        field = looks.BY_ROW.get(name)
        if field is not None:
            if row.get("stored") != field.name:
                problems.append("row %s is stored as %r and looks.py says %r"
                                % (name, row.get("stored"), field.name))
            if len(texts) > field.values:
                problems.append("row %s walks %d values and the field holds %d"
                                % (name, len(texts), field.values))
        elif row.get("stored") is not None:
            problems.append("row %s is not a stored field and says %r"
                            % (name, row.get("stored")))
    if len(set(helps)) != len(helps):
        problems.append("two rows share a help text, and the help is what "
                        "says where the cursor is")
    for slot, state in sorted(table.get("initial", {}).items()):
        for name in looks.SCREEN:
            shown = state.get("rows", {}).get(name)
            if name in rows and shown not in rows[name].get("texts", []):
                problems.append("slot %s shows %r on %s, which the walk never "
                                "reached" % (slot, shown, name))
        problems += _title_problems(slot, state)
        problems += _style_problems(slot, state)
    if sorted(table.get("initial", {})) != ["1", "2"]:
        problems.append("the initial values are not those of slots 1 and 2")
    return problems


def _cursor_problems(name: str, row: dict, table: dict) -> list:
    """The cursor box on a row's value, as the walk read it off VRAM.

    Per row, because the game sizes it per row: measured on 2026-09-22 on
    every row of both slots, at arrival, both ends and the middle value, it
    starts at x 314 on NAT, 436 on AGE, 428 on FOOT and 396 on the other
    nine, and no row moves it from value to value (CORR-LOOKS-070).  A table
    that carried NAT's box down by the pitch drew eleven rows wrong.
    """
    box = row.get("cursor")
    if (not isinstance(box, list) or len(box) != 4
            or not all(isinstance(v, int) for v in box)
            or not box[0] <= box[2] or not box[1] <= box[3]):
        return ["row %s: the cursor box on its value is %r, and the walk "
                "reads one on every row" % (name, box)]
    if "row0_y" in table and "display" in table:
        line = (table["row0_y"] + table["pitch"] * looks.SCREEN.index(name)
                + table["display"][1] // 2)
        if not box[1] <= line <= box[3]:
            return ["row %s: the cursor box %r does not cover the row's line "
                    "at y %d" % (name, box, line)]
    return []


LABEL_MOVES = {"enter": "Left", "leave": "Right", "left": "locks",
               "up": "locks", "down": "locks"}
"""What a row's label position does with each press -- the only shape the
walk has measured (DEFAUL, CORR-LOOKS-067): Left from the row's first value
enters it, Right leaves it for that value, and Left, Up and Down move nothing.
A walk that measured anything else refuses rather than write it here."""


def _label_problems(name: str, label: dict) -> list:
    """The label position of a row has to be the shape `State` reads."""
    if not isinstance(label, dict):
        return ["row %s: the label position is %r" % (name, label)]
    problems = []
    if not isinstance(label.get("help"), str) or not label.get("help"):
        problems.append("row %s: the label position has no help" % name)
    arrows = label.get("arrows")
    if not isinstance(arrows, list):
        problems.append("row %s: the label position does not say where its "
                        "arrows show" % name)
    else:
        for one in arrows:
            if (not isinstance(one, dict)
                    or one.get("side") not in ARROW_SIDES
                    or len(one.get("point", [])) != 2):
                problems.append("row %s: an arrow on the label is %r"
                                % (name, one))
    cursor = label.get("cursor")
    if (not isinstance(cursor, list) or len(cursor) != 4
            or not cursor[0] <= cursor[2] or not cursor[1] <= cursor[3]):
        problems.append("row %s: the cursor box on the label is %r"
                        % (name, cursor))
    for key, want in LABEL_MOVES.items():
        if label.get(key) != want:
            problems.append("row %s: on the label, %s is %r and the only one "
                            "modelled is %r"
                            % (name, key, label.get(key), want))
    return problems


ARROW_WHERE = ("arrival", "left_end", "between", "right_end")
"""Where the walk reads the arrows of a row: when the cursor arrives on it,
at each end, and on every value between -- which it asserts are all the same.
"""

ARROW_SIDES = ("left", "right")


def _arrow_problems(name: str, row: dict) -> list:
    """The arrows a row stores have to be the shape `State.arrows` reads.

    `between` is None exactly when the row has no value between its two ends:
    a table that says otherwise was written by a walk that did not look.
    """
    arrows = row.get("arrows")
    if not isinstance(arrows, dict):
        return ["row %s does not say where its arrows show" % name]
    problems = []
    for where in ARROW_WHERE:
        if where not in arrows:
            problems.append("row %s: no arrows %s" % (name, where))
            continue
        found = arrows[where]
        if found is None:
            if where != "between" or len(row.get("texts", [])) > 2:
                problems.append("row %s: the arrows %s were not read"
                                % (name, where))
            continue
        for one in found:
            if (one.get("side") not in ARROW_SIDES
                    or len(one.get("point", [])) != 2):
                problems.append("row %s: an arrow %s is %r" % (name, where,
                                                               one))
    if (arrows.get("between") is not None
            and len(row.get("texts", [])) <= 2):
        problems.append("row %s has no value between its ends and stores "
                        "arrows there" % name)
    return problems


TEXT_ROLES = ("labels", "plate", "shirt")
SPACING_MAX = 8
"""A spacing past this would be a byte read from the wrong offset: the
measured ones are 0, 1 and 2 (LOOKS-TASK-37)."""


ALIGNMENTS = (0, 2, 3)
"""The alignment bytes a text object of this screen carries (LOOKS-TASK-38)."""


def _piece_problems(what: str, piece) -> list:
    """One piece of text -- a box, how it is written and its tokens."""
    if not isinstance(piece, dict):
        return ["%s is %r" % (what, piece)]
    problems = []
    box = piece.get("box")
    if not (isinstance(box, list) and len(box) == 3
            and all(isinstance(one, int) for one in box)):
        problems.append("%s has the box %r" % (what, box))
    if piece.get("align") not in ALIGNMENTS:
        problems.append("%s is aligned %r" % (what, piece.get("align")))
    if not 0 <= piece.get("spacing", -1) <= SPACING_MAX:
        problems.append("%s is spaced %r" % (what, piece.get("spacing")))
    tokens = piece.get("tokens")
    if not (isinstance(tokens, list) and all(
            isinstance(one, list) and len(one) == 2
            and one[0] in ("tab", "colour", "text") for one in tokens)):
        problems.append("%s has the tokens %r" % (what, tokens))
    return problems


def _layout_problems(name: str, row: dict) -> list:
    """Every value of a row says how it is laid out, and spells its text.

    `layouts[i]` is how the game writes `texts[i]`: its pieces, each a box,
    an alignment, a spacing and the line's tokens.  Joined the way the rows
    are composed -- stripped, a space apart -- they have to spell the text,
    or the walk paired a layout with the wrong value.
    """
    layouts = row.get("layouts")
    texts = row.get("texts", [])
    if not isinstance(layouts, list) or len(layouts) != len(texts):
        return ["row %s says how %s of its %d value(s) are laid out"
                % (name, len(layouts) if isinstance(layouts, list) else "none",
                   len(texts))]
    problems = []
    for text, pieces in zip(texts, layouts):
        for number, piece in enumerate(pieces):
            problems += _piece_problems("row %s, %r, piece %d"
                                        % (name, text, number), piece)
        if problems:
            continue
        spelled = " ".join(tokens_text(piece["tokens"]).strip()
                           for piece in pieces)
        if spelled != text:
            problems.append("row %s: the pieces of %r spell %r"
                            % (name, text, spelled))
    return problems


def _style_problems(slot, state: dict) -> list:
    """Every text the window writes has to say how the game writes it.

    `{spacing, colour, align}` for the labels, the plate, the shirt and each
    row's value -- off the text objects' own bytes (`oracle.text_style`).
    """
    styles = state.get("styles")
    if not isinstance(styles, dict):
        return ["slot %s does not say how its text is written" % slot]
    problems = []
    found = [(role, styles.get(role)) for role in TEXT_ROLES]
    found += [("value of %s" % name, styles.get("values", {}).get(name))
              for name in looks.SCREEN]
    for what, style in found:
        if not isinstance(style, dict):
            problems.append("slot %s: no style for the %s" % (slot, what))
            continue
        if not 0 <= style.get("spacing", -1) <= SPACING_MAX:
            problems.append("slot %s: the %s is spaced %r"
                            % (slot, what, style.get("spacing")))
        colour = style.get("colour")
        if (not isinstance(colour, list) or len(colour) != 3
                or not all(0 <= one <= 255 for one in colour)):
            problems.append("slot %s: the %s is coloured %r"
                            % (slot, what, colour))
    for role in ("plate", "shirt"):
        problems += _piece_problems("slot %s's %s" % (slot, role),
                                    styles.get(role))
    return problems


def _title_problems(slot, state: dict) -> list:
    """The title a state stores has to be what its object's string draws.

    Three fields say one thing three ways -- the string the object holds, the
    letters the band shows, and the ones the font skips -- and a table that
    stores the object's string as the title (`LOOKS SET`, which no frame of
    this screen has ever shown) is refused here.  It is the check the measured
    table went without until CORR-LOOKS-054.
    """
    held = state.get("title_object")
    if not isinstance(held, str):
        return ["slot %s does not say what string the title object holds"
                % slot]
    problems = []
    if state.get("title") != title_drawn(held):
        problems.append("slot %s stores the title %r, and the object holds "
                        "%r, which draws %r"
                        % (slot, state.get("title"), held, title_drawn(held)))
    if state.get("title_skipped") != title_skipped(held):
        problems.append("slot %s says the title skips %r and this font skips "
                        "%r of %r" % (slot, state.get("title_skipped"),
                                      title_skipped(held), held))
    return problems


def label_disagreements(table: dict) -> list:
    """Where a label of looks.py is not what the game writes for that value.

    looks.py's labels are third-party opinion -- four editors agreeing -- and
    the walk is the first witness that is the game: for every value a row
    reaches, the first word of the screen's text has to be the label (`A1` of
    `A1 TYPE`), its initial (`R` of `RIGHT`), or, for a row without labels,
    the number itself (`175` of `175 cm`).
    """
    out = []
    for name, field in looks.BY_ROW.items():
        row = table["rows"][name]
        for text, value in zip(row["texts"], row["values"]):
            word = text.split(" ")[0]
            label = field.label(value)
            if field.labels:
                agrees = word == label or (len(label) == 1 and word.isalpha()
                                           and word.startswith(label))
            else:
                agrees = word == str(value)
            if not agrees:
                out.append("%s=%d is %r in looks.py and %r on the screen"
                           % (name, value, label, text))
    return out


def index_of(table: dict, row: str, text: str) -> int:
    texts = table["rows"][row]["texts"]
    if text not in texts:
        raise BadScreen("%r is not a value of %s: %s" % (text, row, texts))
    return texts.index(text)


def step(table: dict, row: str, index: int, button: str) -> int:
    """Where one press of Left or Right takes *row* from *index*, as measured."""
    texts = table["rows"][row]["texts"]
    if not 0 <= index < len(texts):
        raise BadScreen("%s has %d values and %d is not one"
                        % (row, len(texts), index))
    if button == "Right":
        if index + 1 < len(texts):
            return index + 1
        return 0 if table["rows"][row]["right"] == "wraps" else index
    if button == "Left":
        if index > 0:
            return index - 1
        return (len(texts) - 1 if table["rows"][row]["left"] == "wraps"
                else index)
    raise BadScreen("%r moves no value; Left and Right do" % button)


def move(table: dict, cursor_row: int, button: str) -> int:
    """Where one press of Up or Down takes the cursor, as measured."""
    last = len(looks.SCREEN) - 1
    if button == "Down":
        if cursor_row < last:
            return cursor_row + 1
        return 0 if table["vertical"]["down"] == "wraps" else cursor_row
    if button == "Up":
        if cursor_row > 0:
            return cursor_row - 1
        return last if table["vertical"]["up"] == "wraps" else cursor_row
    raise BadScreen("%r moves no cursor; Up and Down do" % button)


# ---- the screen as a thing that is walked --------------------------------

BUTTONS = ("Up", "Down", "Left", "Right")
"""The four the screen answers to.  A fifth is refused, not ignored: a gate
that sends `Cross` and gets silence would report a screen that never moved."""


class State:
    """Where the screen is, after N presses from a save state's own start.

    **The window owns none of this.**  Rule 3 keeps address and disc out of
    `ui/`, and this keeps the SCREEN out of it too: what a press does is
    measured (`step`, `move`, the locks and the wrap), so the widget that
    draws the screen must not be the thing that decides where a press lands.
    It reads `text_of`, `help_text` and `tuple_text`, and sends `press`.

    That split is what makes the gate's judgement mean anything: `ui_check.py`
    compares what the window PRINTS against what this class says, and the two
    would agree by construction if the window did its own arithmetic.
    """

    __slots__ = ("table", "slot", "cursor", "indices", "pressed", "on_label")

    def __init__(self, table: dict, slot: int | str = 2):
        slot = str(slot)
        if slot not in table.get("initial", {}):
            raise BadScreen("slot %s was not measured; the states are %s"
                            % (slot, ", ".join(sorted(table["initial"]))))
        self.table = table
        self.slot = slot
        start = table["initial"][slot]
        self.cursor = list(looks.SCREEN).index(table["cursor_on_load"])
        self.indices = {name: index_of(table, name, start["rows"][name])
                        for name in looks.SCREEN}
        self.pressed = 0
        # On the row's LABEL rather than its value: DEFAUL has two positions,
        # and Left from its value takes the cursor box to the name, the help
        # to "Undo" and the arrow to the other side (CORR-LOOKS-067).
        self.on_label = False

    # -- what the screen shows --------------------------------------------

    @property
    def row(self) -> str:
        """The row the cursor is on."""
        return looks.SCREEN[self.cursor]

    @property
    def order(self) -> list:
        """The rows, top to bottom.  The window draws them in this order and
        may not know where it comes from (rule 3)."""
        return list(looks.SCREEN)

    def text_of(self, row: str) -> str:
        return self.table["rows"][row]["texts"][self.indices[row]]

    def texts(self) -> dict:
        return {name: self.text_of(name) for name in looks.SCREEN}

    def help_text(self) -> str:
        """The help box, INCLUDING the lie it tells before the first press.

        Trap 35: after `load_state` the box still shows the menu's `Visual`,
        and only the first press makes it say the row.  Reproducing that is
        fidelity -- a window that shows `Nation` from the start disagrees with
        the game on frame one, which is exactly what the key-against-key
        comparison would catch and be right to.
        """
        if not self.pressed:
            return self.table["help_on_load"]
        if self.on_label:
            return self.table["rows"][self.row]["label"]["help"]
        return self.table["rows"][self.row]["help"]

    def arrows(self) -> list:
        """The arrows beside the cursor's value, as the walk read them.

        `[{"side", "point"}]` in native pixels.  Where the row is -- arriving,
        at an end, or between -- picks which of the walk's four readings
        applies.  A row with one value has no end to reach, and shows what
        it showed when the cursor arrived (DEFAUL: the left arrow alone).
        On the row's label the label's own arrows apply (DEFAUL: the right
        arrow beside the name, CORR-LOOKS-067).
        """
        row = self.table["rows"][self.row]
        arrows = row["arrows"]
        count = len(row["texts"])
        index = self.indices[self.row]
        if self.on_label:
            found = row["label"]["arrows"]
        elif count == 1:
            found = arrows["arrival"]
        elif index == 0:
            found = arrows["left_end"]
        elif index == count - 1:
            found = arrows["right_end"]
        else:
            found = arrows["between"]
        return [dict(one, point=list(one["point"])) for one in found]

    def cursor_box(self) -> list:
        """The yellow box, in native pixels, where the walk measured it: over
        the row's value, a box per row -- or over the row's name when the
        cursor is on the label.

        Not carried down by the pitch from the row the state loads on: that
        row is NAT, whose box starts at x 314, and nine of the other eleven
        start at 396 (CORR-LOOKS-070)."""
        row = self.table["rows"][self.row]
        if self.on_label:
            return list(row["label"]["cursor"])
        return list(row["cursor"])

    def value_box(self, row: str) -> list:
        """The box the walk measured over *row*'s value, in native pixels."""
        return list(self.table["rows"][row]["cursor"])

    def style(self, role: str) -> dict:
        """How the game writes the labels, the plate or the shirt:
        `{spacing, colour, align}` off the text object's own bytes."""
        return dict(self.table["initial"][self.slot]["styles"][role])

    def value_layout(self, row: str) -> list:
        """The pieces *row*'s value is written in now, as the walk read them:
        `[{box, align, spacing, colour, tokens}]` (LOOKS-TASK-38)."""
        found = self.table["rows"][row]["layouts"][self.indices[row]]
        return [dict(piece, box=list(piece["box"])) for piece in found]

    def plate(self) -> str:
        return self.table["initial"][self.slot]["plate"]

    def shirt(self) -> str:
        return self.table["initial"][self.slot]["shirt"]

    def title(self) -> str:
        """What the title band DRAWS -- `S SET`, not the `LOOKS SET` the object
        holds (CORR-LOOKS-054)."""
        return self.table["initial"][self.slot]["title"]

    def figure(self) -> int:
        """0 is the outfield player and 1 the goalkeeper, as `scene` counts
        them; slot 1 is the goalkeeper's state and slot 2 the other one."""
        return 1 if self.slot == "1" else 0

    def layout(self) -> dict:
        """Where everything sits, in the display's own 512x240 pixels.

        The table keeps text in the coordinates the game prints them in --
        from the centre of the display -- and the boxes in native pixels.  A
        widget wants one system, so the conversion happens here, once, where
        the origin is known: `x + width/2`, `y + height/2`.

        **Native pixels, not fractions of a capture.**  The emulator's picture
        crops overscan by however it is configured, so a fraction of it is not
        the game's arrangement; that is why the walk stored both and why this
        reads the native half (LOOKS-TASK-21).
        """
        width, height = self.table["display"]
        origin = (width // 2, height // 2)
        anchors = self.table["initial"][self.slot]["anchors"]

        def native(point):
            return [point[0] + origin[0], point[1] + origin[1]]

        cursor = list(self.table["regions"]["cursor"]["native"])
        first = self.table["regions"]["cursor"]["row"]
        step_down = self.table["pitch"] * list(looks.SCREEN).index(first)
        return {
            "display": list(self.table["display"]),
            "pitch": self.table["pitch"],
            "rows_y": native([0, self.table["row0_y"]])[1],
            "labels_x": native(anchors["labels"])[0],
            "values_x": cursor[0],
            # The cursor rectangle of the FIRST row: the walk measured it on
            # the row the state loads on, and the pitch carries it from there.
            "cursor": [cursor[0], cursor[1] - step_down,
                       cursor[2], cursor[3] - step_down],
            "title": native(anchors["title"]),
            "plate": native(anchors["plate"]),
            "shirt": native(anchors["shirt"]),
            "panel": list(self.table["regions"]["panel"]["native"]),
            "rows": list(self.table["regions"]["rows"]["native"]),
            "help": list(self.table["regions"]["help"]["native"]),
        }

    # -- what a press does -------------------------------------------------

    def value_of(self, row: str):
        """What the row stores at its current text, or None for the two that
        store nothing (trap 17: DEFAUL and NAT are not fields)."""
        values = self.table["rows"][row].get("values")
        return None if values is None else values[self.indices[row]]

    def values(self) -> dict:
        """The stored fields, by their `looks.py` names."""
        out = {}
        for name in looks.SCREEN:
            field = looks.BY_ROW.get(name)
            value = self.value_of(name)
            if field is not None and value is not None:
                out[field.name] = value
        return out

    def tuple_text(self) -> str:
        """The five fields the scene is built from, as `A-A1-A-A-A`."""
        return looks.format_tuple(self.values())

    def press(self, button: str) -> bool:
        """One press.  True if anything moved -- False at a lock."""
        if button not in BUTTONS:
            raise BadScreen("%r is not one of the four this screen answers "
                            "to: %s" % (button, ", ".join(BUTTONS)))
        self.pressed += 1
        row = self.row
        label = self.table["rows"][row].get("label")
        if self.on_label:
            if button == label["leave"]:
                self.on_label = False
                return True
            return False  # Left, Up and Down lock there (LABEL_MOVES)
        if (label is not None and button == label["enter"]
                and self.indices[row] == 0):
            self.on_label = True
            return True
        if button in ("Up", "Down"):
            where = move(self.table, self.cursor, button)
            moved = where != self.cursor
            self.cursor = where
            return moved
        where = step(self.table, row, self.indices[row], button)
        moved = where != self.indices[row]
        self.indices[row] = where
        return moved

    def press_all(self, buttons) -> list:
        """A sequence, and what each press did.  The order is the measurement."""
        return [self.press(button) for button in buttons]


def parse_keys(text: str) -> list:
    """`Down,Down,Right` to the three presses it names, refusing the rest."""
    buttons = [part.strip() for part in text.split(",") if part.strip()]
    for button in buttons:
        if button not in BUTTONS:
            raise BadScreen("%r is not one of the four this screen answers "
                            "to: %s" % (button, ", ".join(BUTTONS)))
    return buttons


def walk_to_end(table: dict, row: str, button: str) -> list:
    """The presses that take *row* from one end to the other, plus one more.

    The extra press is the point: it is what tells a lock from a wrap, and it
    is the press the gate judges.  Length is `len(texts)`, so it reaches the
    far end from ANY starting index and then tries to go past it.
    """
    return [button] * len(table["rows"][row]["texts"])


def report(table: dict) -> None:
    print("display %dx%d, rows from y=%d every %d"
          % (tuple(table["display"]) + (table["row0_y"], table["pitch"])))
    print("vertical: Up %s, Down %s; help on load %r; cursor starts on %s"
          % (table["vertical"]["up"], table["vertical"]["down"],
             table["help_on_load"], table["cursor_on_load"]))
    for name in looks.SCREEN:
        row = table["rows"][name]
        texts = row["texts"]
        shown = texts if len(texts) <= 8 else texts[:4] + ["..."] + texts[-3:]
        print("  %-9s %3d value(s)  left %-5s right %-5s help %r"
              % (name, len(texts), row["left"], row["right"], row["help"]))
        print("            %s" % " | ".join(shown))
    for slot, state in sorted(table["initial"].items()):
        print("  slot %s: plate %s, shirt %r, title %r (the object holds %r, "
              "and this font has no %r)"
              % (slot, state["plate"], state["shirt"], state["title"],
                 state["title_object"], state["title_skipped"]))
    for name, box in sorted(table["regions"].items()):
        print("  region %-8s native %s  fraction %s"
              % (name, box["native"], box["fraction"]))


# ---- self-check ----------------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    return harness.run("screen.py", _checks, verbose)


def _frame(width, height, background=(0, 49, 49)):
    return [[background] * width for _ in range(height)]


def _draw_box(rows, box, colour=(173, 173, 173)):
    x0, y0, x1, y1 = box
    for x in range(x0, x1 + 1):
        rows[y0][x] = rows[y1][x] = colour
    for y in range(y0, y1 + 1):
        rows[y][x0] = rows[y][x1] = colour


def _checks(c) -> None:
    ok = c.ok
    refuses = c.refusing(BadScreen)

    # The strings, as the game passed them on 2026-09-17 -- the value block of
    # slot 2 and the unit block, each checked there against the drawn glyphs.
    values = (b"A\n\t\x12A\t\x1e1\nA\nA\nA\n175\nA\n\t>\rpp\xf023\n"
              b"\rpp\xf0A")
    ok("the value block decodes to the nine values the screen drew",
       decode(values) == ["A", "A1", "A", "A", "A", "175", "A", "23", "A"],
       "%r" % decode(values))
    units = (b"\r\x80\x80\x80O.K.  \n\rpp\xf0\nTYPE\nTYPE\nTYPE\nTYPE\n"
             b"TYPE\ncm\nTYPE\n\nTYPE")
    ok("the unit block keeps its blank lines, so the rows stay aligned",
       decode(units) == ["O.K.  ", "", "TYPE", "TYPE", "TYPE", "TYPE", "TYPE",
                         "cm", "TYPE", "", "TYPE"], "%r" % decode(units))
    refuses("an unknown control byte is refused, not skipped",
            lambda: decode(b"OUTSIDE\x0b\x08"), "not a character")
    refuses("a string cut inside a colour code is refused",
            lambda: decode(b"A\r\x80"), "ends inside")
    ok("full-width help folds to the letters",
       help_text("Ｓｋｉｎ　Ｃｏｌｏｕｒ　■　Ｔｕｒｎ　　".encode("cp932"))
       == "Skin Colour ■ Turn")

    # A console of this machine's default encoding, which the help does not fit.
    console = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", newline="\n")
    c.refuses("a console that cannot carry the help's glyph says so",
              lambda: console.write("Skin Colour ■ Turn"),
              "charmap", UnicodeEncodeError)
    ok("and after make_printable the same write goes through",
       make_printable(console) and console.write("Skin Colour ■ Turn") > 0)
    ok("a stream that cannot be reconfigured is left alone, not broken",
       make_printable(object()) is False)

    # The title, against the three markers written into the running game's RAM
    # on 2026-09-17 and read back off the band (TITLE_FONT).
    ok("the title the screen shows is not the string the object holds",
       title_drawn("LOOKS SET  ") == "S SET"
       and title_skipped("LOOKS SET  ") == "LOOK",
       "%r / %r" % (title_drawn("LOOKS SET  "),
                    title_skipped("LOOKS SET  ")))
    ok("a marker of eleven As draws eleven, and one of A to K draws three",
       title_drawn("AAAAAAAAAAA") == "AAAAAAAAAAA"
       and title_drawn("ABCDEFGHIJK") == "AEJ",
       "%r" % title_drawn("ABCDEFGHIJK"))
    ok("the digits that have a glyph are the two the marker drew",
       title_drawn("0123456789A") == "12A", "%r" % title_drawn("0123456789A"))
    ok("a space moves the pen where a letter without a glyph does not",
       title_drawn("01234     A") == "12     A",
       "%r" % title_drawn("01234     A"))

    calls = [(ord("A"), 5, 7, 1), (ord("1"), 5, 7, 1),
             (ord("A"), 5, 7, 0), (ord("1"), 13, 7, 0),
             (ord("T"), 30, 7, 1), (ord("T"), 30, 7, 0),
             (ord("Y"), 38, 7, 0), (ord("B"), 0, 19, 0)]
    ok("the glyph pass keeps the drawing pass and splits strings",
       glyph_strings(calls) == [(5, 7, "A1"), (30, 7, "TY"), (0, 19, "B")],
       "%r" % glyph_strings(calls))

    labels = {"at": 0, "x": -56, "y": -79, "width": 320,
              "lines": [name + " " for name in looks.SCREEN]}
    unit = {"at": 20, "x": -80, "y": -79, "width": 296, "lines": decode(units)}
    value = {"at": 40, "x": 130, "y": -55, "width": 64, "lines": decode(values)}
    plate = {"at": 60, "x": -240, "y": -67, "width": 48, "lines": ["CB"]}
    shirt = {"at": 80, "x": -213, "y": -82, "width": 120, "lines": ["SHIRT N"]}
    title = {"at": 100, "x": -224, "y": -100, "width": 256, "lines": ["LOOKS SET"]}
    nation = {"at": 120, "x": -104, "y": -67, "width": 296, "lines": ["Wales"]}
    found = pieces([labels, unit, value, plate, shirt, title, nation],
                   -79, 12, -80, -83)
    ok("pieces land on their rows; labels, plate, shirt and title kept out",
       found["HAIR"] == {20: "TYPE", 40: "A1"}
       and found["NAT"] == {120: "Wales"}
       and found["DEFAUL"] == {20: "O.K."}, "%r" % found)
    ok("a row composes left to right in the measured order",
       compose(found["HAIR"], [40, 20]) == "A1 TYPE")
    refuses("a piece from an object the order never saw is refused",
            lambda: compose(found["HAIR"], [20]), "measured order")
    ok("the label object is the one printing the row names",
       labels_object([unit, labels, value]) is labels)
    refuses("no label object is a refusal",
            lambda: labels_object([unit, value]), "0 object(s)")

    frame = _frame(64, 40)
    _draw_box(frame, (2, 3, 40, 30))
    ok("a closed grey border is a box", boxes(frame, 64, 40) == [(2, 3, 40, 30)],
       "%r" % boxes(frame, 64, 40))
    frame[10][40] = (0, 49, 49)
    ok("and one missing pixel of an edge makes it no box",
       boxes(frame, 64, 40) == [], "%r" % boxes(frame, 64, 40))
    text = _frame(64, 40)
    for x in range(4, 12):
        text[5][x] = (200, 200, 200)
    ok("a short grey stroke is text, not an edge", boxes(text, 64, 40) == [])
    lit = _frame(64, 40)
    for x in range(10, 20):
        lit[8][x] = (132, 132, 8)
        lit[14][x] = (189, 189, 66)
    lit[11][10] = (181, 181, 57)
    lit[20][30] = (115, 115, 247)
    lit[25][30] = (173, 173, 173)
    ok("every measured phase of the cursor is found, letter and border not",
       cursor(lit, (0, 0, 63, 39)) == (10, 8, 19, 14),
       "%r" % (cursor(lit, (0, 0, 63, 39)),))
    ok("fractions close on the far edge",
       fraction((0, 0, 511, 239), (512, 240)) == [0.0, 0.0, 1.0, 1.0])

    ok("the title's band comes off its object's own anchor",
       title_band((-224, -100), 256, (256, 120)) == (32, 20, 287, 33),
       "%r" % (title_band((-224, -100), 256, (256, 120)),))
    band = _frame(64, 40)
    for x in list(range(10, 17)) + list(range(21, 26)):
        band[5][x] = (239, 239, 239)  # two letters, the measured four apart
    band[6][30] = (173, 173, 173)  # a border
    band[6][34] = (115, 115, 247)  # a letter of the rows
    band[20][12] = (239, 239, 239)  # white below the band
    ok("one run per letter, and neither border nor lavender counts",
       ink_runs(band, (0, 0, 63, 10)) == [(10, 16), (21, 25)],
       "%r" % ink_runs(band, (0, 0, 63, 10)))

    table = _toy_table()
    ok("a whole toy table validates", validate(table) == [],
       "%r" % validate(table))
    broken = json.loads(json.dumps(table))
    broken["rows"]["SKIN"]["layouts"][1][0]["tokens"] = [["text", "C TYPE"]]
    ok("a layout that spells another value is refused",
       any("spell" in p for p in validate(broken)))
    broken = json.loads(json.dumps(table))
    broken["rows"]["SKIN"]["layouts"][0][0]["align"] = 1
    ok("an alignment no object carries is refused",
       any("aligned" in p for p in validate(broken)))
    broken = json.loads(json.dumps(table))
    del broken["rows"]["NAT"]["layouts"][-1]
    ok("a row with a value and no layout is refused",
       any("laid out" in p for p in validate(broken)))
    ok("line_tokens keeps a tab's column and a colour code's three bytes",
       line_tokens(b"\t\x12A\t\x1e1\n\rpp\xf023")
       == [[["tab", 18], ["text", "A"], ["tab", 30], ["text", "1"]],
           [["colour", [112, 112, 240]], ["text", "23"]]],
       "%r" % (line_tokens(b"\t\x12A\t\x1e1\n\rpp\xf023"),))
    ok("a colour code holds into the lines below it",
       colour_at(line_tokens(b"\r\x80\x80\x80O.K.\nA\n\rpp\xf0\nB"), 1,
                 [1, 2, 3]) == [128, 128, 128]
       and colour_at(line_tokens(b"\r\x80\x80\x80O.K.\nA\n\rpp\xf0\nB"),
                     3, [1, 2, 3]) == [112, 112, 240])
    broken = json.loads(json.dumps(table))
    del broken["initial"]["1"]["styles"]["values"]["AGE"]
    ok("a row whose value says nothing of how it is written is refused",
       any("value of AGE" in p for p in validate(broken)))
    broken = json.loads(json.dumps(table))
    broken["initial"]["2"]["styles"]["labels"]["spacing"] = 200
    ok("a spacing no object carries is refused",
       any("spaced" in p for p in validate(broken)))
    walked = State(table, 2)
    ok("on arrival at the left end the right arrow shows alone",
       [one["side"] for one in walked.arrows()] == ["right"],
       "%r" % walked.arrows())
    walked.press("Right")
    ok("between the ends both arrows show",
       [one["side"] for one in walked.arrows()] == ["left", "right"])
    walked.press_all(["Right", "Right"])
    ok("at the right end the left arrow shows alone",
       [one["side"] for one in walked.arrows()] == ["left"])
    broken = json.loads(json.dumps(table))
    broken["rows"]["SKIN"]["arrows"]["between"] = None
    ok("a row with values between its ends and no arrows there is refused",
       any("were not read" in p for p in validate(broken)))
    broken = json.loads(json.dumps(table))
    broken["rows"]["SKIN"]["arrows"]["left_end"] = [{"side": "up",
                                                     "point": [0, 0]}]
    ok("an arrow that is neither side is refused",
       any("an arrow" in p for p in validate(broken)))
    labelled = json.loads(json.dumps(table))
    labelled["rows"]["SKIN"]["label"] = dict(
        LABEL_MOVES, help="label help",
        arrows=[{"side": "right", "point": [276, 67]}],
        cursor=[188, 65, 272, 76])
    ok("a row with a label position validates", validate(labelled) == [],
       "%r" % validate(labelled))
    on = State(labelled, 2)
    on.press("Down")
    on.press("Up")
    entered = on.press("Left")
    ok("Left from the row's first value takes the cursor to the label: the "
       "text stays, the help, the arrows and the box move (CORR-LOOKS-067)",
       entered and on.on_label and on.text_of("SKIN") == "A TYPE"
       and on.help_text() == "label help"
       and on.arrows() == [{"side": "right", "point": [276, 67]}]
       and on.cursor_box() == [188, 65, 272, 76],
       "%r %r %r" % (on.help_text(), on.arrows(), on.on_label))
    ok("and on the label Left, Up and Down move nothing",
       on.press_all(["Left", "Up", "Down"]) == [False, False, False]
       and on.on_label and on.row == "SKIN")
    ok("Right leaves the label for the value, with the row's own help back",
       on.press("Right") and not on.on_label
       and on.help_text() == "help %d" % looks.SCREEN.index("SKIN"))
    plain = State(table, 2)
    plain.press("Down")
    plain.press("Up")
    ok("without a label position Left at the first value locks, as before",
       plain.press("Left") is False and not plain.on_label)
    broken = json.loads(json.dumps(labelled))
    broken["rows"]["SKIN"]["label"]["up"] = "wraps"
    ok("a label position that moves where the walk measured a lock is "
       "refused", any("the only one modelled" in p for p in validate(broken)),
       "%r" % validate(broken))
    broken = json.loads(json.dumps(labelled))
    broken["rows"]["SKIN"]["label"]["help"] = broken["rows"]["NAT"]["help"]
    ok("a label whose help is another row's is refused -- the help is what "
       "says where the cursor is", any("share a help" in p
                                       for p in validate(broken)))
    broken = json.loads(json.dumps(labelled))
    del broken["rows"]["SKIN"]["label"]["cursor"]
    ok("a label position with no cursor box is refused",
       any("cursor box on the label" in p for p in validate(broken)))
    boxed = json.loads(json.dumps(table))
    boxed["rows"]["NAT"]["cursor"] = [314, 53, 476, 64]
    walked = State(boxed, 2)
    walked.press("Up")
    at_nat = walked.cursor_box()
    walked.press("Up")
    ok("the cursor box is the row's own, not the box of another row carried "
       "down by the pitch: NAT at x 314 and DEFAUL above it at 396 "
       "(CORR-LOOKS-070)", at_nat == [314, 53, 476, 64]
       and walked.row == "DEFAUL"
       and walked.cursor_box() == [396, 41, 476, 52],
       "%r then %r on %s" % (at_nat, walked.cursor_box(), walked.row))
    broken = json.loads(json.dumps(table))
    del broken["rows"]["DEFAUL"]["cursor"]
    ok("a row with no cursor box on its value is refused, which is the table "
       "the walk wrote before CORR-LOOKS-070",
       any("cursor box on its value" in p for p in validate(broken)),
       "%r" % validate(broken))
    broken = json.loads(json.dumps(table))
    broken.update(row0_y=-79, pitch=12, display=[512, 240])
    ok("with the row grid known, a toy table whose boxes sit on their lines "
       "validates", validate(broken) == [], "%r" % validate(broken))
    broken["rows"]["SKIN"]["cursor"] = [396, 41, 476, 52]
    ok("and a cursor box that does not cover its row's line is refused",
       any("does not cover the row's line" in p for p in validate(broken)),
       "%r" % validate(broken))
    broken = json.loads(json.dumps(table))
    del broken["rows"]["DEFAUL"]["label"]
    ok("a row that does not say whether it has a label is refused, which is "
       "the table the walk wrote before CORR-LOOKS-067",
       any("to its label" in p for p in validate(broken)))
    ok("Right locks at the right end", step(table, "SKIN", 3, "Right") == 3)
    ok("Left locks at the left end", step(table, "SKIN", 0, "Left") == 0)
    ok("Down wraps past FOOT when the walk said so",
       move(table, 11, "Down") == 0)
    broken = json.loads(json.dumps(table))
    broken["rows"]["NAT"]["help"] = broken["rows"]["SKIN"]["help"]
    ok("two rows with one help are refused",
       any("share a help" in p for p in validate(broken)))
    broken = json.loads(json.dumps(table))
    broken["rows"]["SKIN"]["texts"] = ["A TYPE"] * 5
    ok("a stored row walking more values than the field holds is refused",
       any("the field holds" in p for p in validate(broken)))
    broken = json.loads(json.dumps(table))
    broken["initial"]["1"]["rows"]["AGE"] = "99"
    ok("an initial value the walk never reached is refused",
       any("never reached" in p for p in validate(broken)))
    broken = json.loads(json.dumps(table))
    broken["initial"]["1"]["title"] = broken["initial"]["1"]["title_object"]
    ok("a table storing the title the OBJECT holds is refused, which is the "
       "table this cycle wrote before CORR-LOOKS-054",
       any("which draws" in p for p in validate(broken)),
       "%r" % validate(broken))
    broken = json.loads(json.dumps(table))
    del broken["initial"]["2"]["title_object"]
    ok("and a title with no string beside it is refused",
       any("what string the title object holds" in p
           for p in validate(broken)))
    refuses("writing a broken table is refused before the file is touched",
            lambda: write(broken, os.devnull), "refusing to write")

    if os.path.exists(TABLE):
        measured = c.attempt("load screen.json", load)
        ok("screen.json, as the measurement wrote it, validates",
           measured is not None)
        if measured is not None:
            ok("every label of looks.py is what the game writes, on every "
               "value the screen reaches", label_disagreements(measured) == [],
               "%r" % label_disagreements(measured)[:4])
            wrong = json.loads(json.dumps(measured))
            wrong["rows"]["HAIR"]["texts"][19] = "I1 TYPE"
            ok("and a hair style the game spells differently is caught",
               any("HAIR=19" in p for p in label_disagreements(wrong)))
            _state_checks(c, measured)
    else:
        c.skip("screen.json", "not measured yet: oracle.py --screen --write")


def _state_checks(c, table: dict) -> None:
    """The walking of the screen, on the measured table -- what the window
    drives and what `ui_check.py` judges the window against."""
    ok = c.ok
    refuses = c.refusing(BadScreen)

    state = State(table, 2)
    ok("a state starts where the save state starts",
       state.row == table["cursor_on_load"]
       and state.texts() == table["initial"]["2"]["rows"],
       "%s, %r" % (state.row, state.texts()))
    ok("and the help box lies about the cursor until the first press, as the "
       "game does", state.help_text() == table["help_on_load"])
    state.press("Down")
    ok("after one press the help names the row the cursor is on",
       state.help_text() == table["rows"][state.row]["help"],
       "%r on %s" % (state.help_text(), state.row))

    top = State(table, 2)
    while top.row != looks.SCREEN[0]:
        top.press("Up")
    ok("one more Up leaves the top row for the last one -- the cursor wraps, "
       "which the rows do not", top.press("Up")
       and top.row == looks.SCREEN[-1], top.row)

    # The two ends of a row, the way the gate walks them.  The cursor goes to
    # the row FIRST: pressing Left with the cursor elsewhere leaves SKIN where
    # it was for a reason that has nothing to do with SKIN's ends, and a check
    # written that way would pass on a screen whose rows did not lock at all.
    walker = State(table, 2)
    while walker.row != "SKIN":
        walker.press("Down")
    moved = walker.press_all(walk_to_end(table, "SKIN", "Right"))
    ok("Right walks SKIN to its last value and the last press moves nothing",
       walker.text_of("SKIN") == table["rows"]["SKIN"]["texts"][-1]
       and moved[-1] is False, "%r, %r" % (walker.text_of("SKIN"), moved))
    ok("and walking SKIN left no other row where it was not",
       all(walker.text_of(name) == table["initial"]["2"]["rows"][name]
           for name in looks.SCREEN if name != "SKIN"))

    ok("the tuple the scene is built from follows the rows",
       walker.tuple_text().split("-")[0]
       == looks.BY_NAME["skin_colour"].label(walker.value_of("SKIN")),
       walker.tuple_text())
    ok("and the two rows that store nothing have no value",
       State(table, 2).value_of("NAT") is None
       and State(table, 2).value_of("DEFAUL") is None)

    ok("slot 1 is the goalkeeper, plate and figure together",
       State(table, 1).plate() == table["initial"]["1"]["plate"]
       and State(table, 1).figure() == 1 and State(table, 2).figure() == 0)
    ok("the title a state reports is what the band draws, not what the "
       "object holds (CORR-LOOKS-054)",
       State(table, 1).title() == table["initial"]["1"]["title"]
       and State(table, 1).title() != table["initial"]["1"]["title_object"])

    label = table["rows"]["DEFAUL"]["label"]
    ok("DEFAUL has a label position, and its help is not the row's",
       label is not None and label["help"] != table["rows"]["DEFAUL"]["help"],
       "%r" % (label,))
    if label is not None:
        on = State(table, 2)
        while on.row != "DEFAUL":
            on.press("Up")
        on.press("Left")
        ok("Up, Left from the load puts the cursor on DEFAUL's name, with its "
           "help, arrows and box (CORR-LOOKS-067)",
           on.on_label and on.help_text() == label["help"]
           and on.arrows() == label["arrows"]
           and on.cursor_box() == label["cursor"]
           and on.text_of("DEFAUL") == table["rows"]["DEFAUL"]["texts"][0])
        on.press("Right")
        ok("and Right brings it back to the value",
           not on.on_label
           and on.help_text() == table["rows"]["DEFAUL"]["help"]
           and on.arrows() == table["rows"]["DEFAUL"]["arrows"]["arrival"])
        ok("and the box back on the value is DEFAUL's own, not NAT's carried "
           "up by the pitch (CORR-LOOKS-070)",
           on.cursor_box() == table["rows"]["DEFAUL"]["cursor"]
           and on.cursor_box()[0] != table["rows"]["NAT"]["cursor"][0],
           "%r against NAT's %r" % (on.cursor_box(),
                                    table["rows"]["NAT"]["cursor"]))

    refuses("a button this screen does not answer to is refused, not ignored",
            lambda: State(table, 2).press("Cross"), "is not one of the four")
    refuses("and a slot nobody measured is refused",
            lambda: State(table, 3), "was not measured")
    refuses("a key sequence with a stranger in it is refused whole",
            lambda: parse_keys("Down,Cross,Up"), "is not one of the four")
    ok("a key sequence parses to the presses it names",
       parse_keys("Down, Right ,Up") == ["Down", "Right", "Up"])


def _toy_table() -> dict:
    rows = {}
    for number, name in enumerate(looks.SCREEN):
        field = looks.BY_ROW.get(name)
        rows[name] = {"texts": ["%s %d" % (name, n) for n in range(4)],
                      "left": "locks", "right": "locks",
                      "help": "help %d" % number,
                      "stored": field.name if field else None,
                      "label": None,
                      "cursor": [396, 41 + 12 * number, 476, 52 + 12 * number],
                      "arrows": {
                          "arrival": [{"side": "right", "point": [480, 43]}],
                          "left_end": [{"side": "right", "point": [480, 43]}],
                          "between": [{"side": "left", "point": [300, 43]},
                                      {"side": "right", "point": [480, 43]}],
                          "right_end": [{"side": "left", "point": [300, 43]}]}}
    rows["SKIN"]["texts"] = ["A TYPE", "B TYPE", "C TYPE", "D TYPE"]
    style = {"spacing": 2, "colour": [128, 128, 128], "align": 0}
    placed = dict(style, box=[16, 53, 48], tokens=[["text", "CB"]])
    for name in looks.SCREEN:
        rows[name]["layouts"] = [
            [dict(style, box=[176, 41, 296], align=2,
                  tokens=[["text", text]])]
            for text in rows[name]["texts"]]
    initial = {slot: {"rows": {name: rows[name]["texts"][0]
                               for name in looks.SCREEN},
                      "styles": {"labels": style, "plate": placed,
                                 "shirt": placed,
                                 "values": {name: style
                                            for name in looks.SCREEN}},
                      "title": title_drawn("LOOKS SET  "),
                      "title_object": "LOOKS SET  ",
                      "title_skipped": title_skipped("LOOKS SET  ")}
               for slot in ("1", "2")}
    return {"order_of_rows": list(looks.SCREEN), "rows": rows,
            "vertical": {"up": "wraps", "down": "wraps"}, "initial": initial,
            "cursor_on_load": "SKIN"}


def main(argv) -> int:
    printable_output()
    if len(argv) == 2 and argv[1] == "--check":
        return 1 if self_check() else 0
    if len(argv) == 2 and argv[1] == "--report":
        try:
            report(load())
        except (OSError, BadScreen) as exc:
            print("screen: %s" % exc, file=sys.stderr)
            return 1
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
