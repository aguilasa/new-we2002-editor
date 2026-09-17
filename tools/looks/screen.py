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
    if sorted(table.get("initial", {})) != ["1", "2"]:
        problems.append("the initial values are not those of slots 1 and 2")
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
    else:
        c.skip("screen.json", "not measured yet: oracle.py --screen --write")


def _toy_table() -> dict:
    rows = {}
    for number, name in enumerate(looks.SCREEN):
        field = looks.BY_ROW.get(name)
        rows[name] = {"texts": ["%s %d" % (name, n) for n in range(4)],
                      "left": "locks", "right": "locks",
                      "help": "help %d" % number,
                      "stored": field.name if field else None}
    rows["SKIN"]["texts"] = ["A TYPE", "B TYPE", "C TYPE", "D TYPE"]
    initial = {slot: {"rows": {name: rows[name]["texts"][0]
                               for name in looks.SCREEN},
                      "title": title_drawn("LOOKS SET  "),
                      "title_object": "LOOKS SET  ",
                      "title_skipped": title_skipped("LOOKS SET  ")}
               for slot in ("1", "2")}
    return {"order_of_rows": list(looks.SCREEN), "rows": rows,
            "vertical": {"up": "wraps", "down": "wraps"}, "initial": initial}


def main(argv) -> int:
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
