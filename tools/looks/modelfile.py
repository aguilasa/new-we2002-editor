#!/usr/bin/env python3
"""The two model files: every section, and the order the game assembles them in.

section.py knows the shape of one section.  This module walks a whole file and
answers the two questions a caller actually has:

* **what is in the file** -- every section, in file order, with the counts
  adding up and the walk ending exactly at EOF;
* **what the game draws** -- the sections a header list names, in the order it
  names them, which is NOT file order.

Those are different answers and conflating them is the mistake this module is
shaped to prevent.  EDT_MOD.BIN holds twenty sections and two lists of eleven;
each list is one model, the two share two sections, and the first section in
the file is the eighth record of the second list.  Taking file order for
assembly order shuffles a body silently -- the failure the PES2 squad tables
paid for once already.

Usage:
    python tools/looks/modelfile.py --check
    python tools/looks/modelfile.py --check-image <japanese.bin>
    python tools/looks/modelfile.py --check-image      # takes WE2002_LOOKS_IMAGE
"""

from __future__ import annotations

import sys

import layout
import section


class Model:
    """The sections one header list names, in the order it names them."""

    __slots__ = ("index", "targets", "sections")

    def __init__(self, index, targets, sections):
        self.index = index
        """Which header list this came from, counting from zero."""
        self.targets = targets
        """The offsets the list names, in LIST order."""
        self.sections = sections
        """The parsed sections, in the same order as `targets`."""

    @property
    def vertices(self):
        return sum(len(one.vertices) for one in self.sections)

    @property
    def primitives(self):
        return sum(len(one.primitives) for one in self.sections)

    @property
    def shape(self):
        """(vertices, primitives) per section, in list order."""
        return [(len(one.vertices), len(one.primitives)) for one in self.sections]

    def pairs(self):
        """(paired, alone): counts that appear twice, and counts that appear once.

        A body is limbs plus a trunk, so a model of mirrored parts shows up as
        several repeated counts and one that stands alone.  Both EDT_MOD.BIN
        lists have exactly that shape -- five repeated counts and a single
        84/71 -- which is evidence that each list is one figure rather than an
        arbitrary grouping.  It says nothing about WHICH part is which; that is
        phase 2, decided at the emulator and not from a vertex count.
        """
        seen = {}
        for counts in self.shape:
            seen[counts] = seen.get(counts, 0) + 1
        paired = sorted(k for k, n in seen.items() if n == 2)
        alone = sorted(k for k, n in seen.items() if n == 1)
        return paired, alone

    def __repr__(self):
        return "Model(%d, sections=%d, vertices=%d, primitives=%d)" % (
            self.index, len(self.sections), self.vertices, self.primitives
        )


def scan(data: bytes, disc_path: str) -> section.Scan:
    """Walk *data* from its recorded start of geometry.

    The start comes from layout, never from the caller.  That is the whole
    lesson of CORR-LOOKS-010: a scan handed 15,704 by hand reported eleven
    sections closing on an exact EOF, which reads as a complete file and was
    43% of one.  A caller that cannot choose the start cannot make that
    mistake, and a start that is wrong is wrong in one place.
    """
    return section.scan(data, layout.GEOMETRY_START[disc_path])


def read_models(data: bytes) -> list:
    """One Model per header list, sections parsed and kept in list order.

    Refuses a file whose lists name something that is not a section --
    MODEL.BIN, whose every list opens with a 0x80-tagged entry aiming at its
    flat pointer array.  Returning models for it would mean parsing offset 104
    as a section header and reporting a vertex count in the billions.
    """
    if not layout.is_derivable(data):
        raise layout.BadPointerList(
            "this file's header lists name a target that is not a section, so "
            "they cannot be read as models yet -- see layout.geometry_start()"
        )
    models = []
    for index, targets in enumerate(layout.record_lists(data)):
        sections = [section.read_section(data, offset) for offset in targets]
        models.append(Model(index, list(targets), sections))
    return models


def verify(data: bytes, disc_path: str) -> str:
    """Assert the recorded geometry of *disc_path* and return a one-line report.

    The counts live in layout.GEOMETRY_EXPECTED, beside the offset the walk
    starts at, because a count without its start offset is not checkable.
    """
    expected = layout.GEOMETRY_EXPECTED.get(disc_path)
    if expected is None:
        raise KeyError("no expected geometry recorded for %s" % disc_path)

    start = layout.GEOMETRY_START[disc_path]
    found = scan(data, disc_path)
    got = (len(found.sections), found.vertices, found.primitives, found.end)

    if got != expected:
        raise AssertionError(
            "%s scanned from %d: got %d sections, %d vertices, %d primitives, "
            "ending at %d; expected %d, %d, %d, ending at %d"
            % ((disc_path, start) + got + expected)
        )
    if found.end != len(data):
        raise AssertionError(
            "%s scanned from %d ended at %d, but the file is %d bytes"
            % (disc_path, start, found.end, len(data))
        )
    return "%s from %d: %d sections, %d vertices, %d primitives, end %d = EOF" % (
        (disc_path, start) + got
    )


def _build_file(groups, base_pointer, start_pad):
    """A synthetic model file: a header, one list per group, then the sections.

    Built rather than fixtured so self_check() runs with no disc image.  The
    layout mirrors EDT_MOD.BIN: header pointers to record lists, lists of
    (tag, pointer) pairs closed by the terminator, then the geometry.
    """
    import struct

    header_words = len(groups)
    # Each list: [count][pad] then two words per entry, then the terminator.
    list_offsets = []
    cursor = header_words * 4
    for members in groups:
        list_offsets.append(cursor)
        cursor += 8 + len(members) * 8 + 8

    geometry_at = cursor + start_pad
    bodies = []
    offset = geometry_at
    placed = {}
    for members in groups:
        for name, (vertices, primitives) in members:
            if name in placed:
                continue
            body = section.build_section(vertices, primitives)
            placed[name] = offset
            bodies.append(body)
            offset += len(body)

    out = bytearray()
    for start in list_offsets:
        out += struct.pack("<I", base_pointer + start)
    for members, start in zip(groups, list_offsets):
        assert len(out) == start, (len(out), start)
        out += struct.pack("<2I", len(members), 0)
        for name, _counts in members:
            out += struct.pack("<2I", 2, base_pointer + placed[name])
        out += struct.pack("<2I", layout.LIST_TERMINATOR, 0)
    out += b"\x00" * start_pad
    for body in bodies:
        out += body
    return bytes(out), placed


def self_check() -> None:
    """Build a two-list file, read it back, and demand the order survive."""
    base_pointer = 0x80010000  # not-an-address: a synthetic KSEG0 base
    groups = [
        [("trunk", (7, 5)), ("left", (3, 2)), ("right", (3, 2))],
        [("trunk", (7, 5)), ("boot", (4, 3)), ("other", (4, 3))],
    ]
    data, placed = _build_file(groups, base_pointer, start_pad=12)

    saved_start = layout.GEOMETRY_START.get("/SYNTH")
    saved_expected = layout.GEOMETRY_EXPECTED.get("/SYNTH")
    try:
        header, derived_base = layout.derive_base(data)
        assert header == len(groups), header
        assert derived_base == base_pointer, hex(derived_base)

        # The start is derived, and it is the lowest target of any list.
        start = layout.geometry_start(data)
        assert start == min(placed.values()), (start, placed)

        models = read_models(data)
        assert len(models) == len(groups), models
        assert [len(one.sections) for one in models] == [3, 3]

        # Shared sections are shared: "trunk" is in both lists, once in the file.
        assert models[0].targets[0] == models[1].targets[0]
        total = section.scan(data, start)
        assert len(total.sections) == 5, total  # 3 + 3, one of them shared
        assert total.end == len(data), (total.end, len(data))

        # -- the pair shape, which is what says a list is one figure ------
        paired, alone = models[0].pairs()
        assert paired == [(3, 2)], paired
        assert alone == [(7, 5)], alone

        # -- Red 1: list order is not file order, and the model keeps the list's
        #
        # The control the task names: reverse the order and it must show.  The
        # SET is unchanged, so anything comparing sets stays green -- which is
        # exactly why the assertion is about the sequence.
        forward = models[0].targets
        backward = list(reversed(forward))
        assert sorted(forward) == sorted(backward)
        assert forward != backward, "the synthetic list is symmetric, so this proves nothing"
        shuffled = Model(0, backward, [section.read_section(data, o) for o in backward])
        assert shuffled.shape != models[0].shape, (
            "reversing the list did not change the shape: the order is not "
            "being carried, so the control proves nothing"
        )
        assert shuffled.vertices == models[0].vertices  # totals cannot catch it

        # -- Red 2: verify() fails loudly when a count is off -------------
        layout.GEOMETRY_START["/SYNTH"] = start
        layout.GEOMETRY_EXPECTED["/SYNTH"] = (
            len(total.sections), total.vertices, total.primitives, total.end
        )
        assert verify(data, "/SYNTH")

        layout.GEOMETRY_EXPECTED["/SYNTH"] = (
            len(total.sections) + 1, total.vertices, total.primitives, total.end
        )
        try:
            verify(data, "/SYNTH")
        except AssertionError as exc:
            assert "expected" in str(exc), str(exc)
            assert str(start) in str(exc), (
                "the failure message omits the start offset, which is the "
                "half that was missing when a partial scan looked complete"
            )
        else:
            raise AssertionError("verify() accepted the wrong section count")

        # -- Red 3: a file whose lists are not section lists is refused ----
        #
        # Stands in for MODEL.BIN: tag the first entry 0x80 and read_models
        # must decline rather than parse the pointer table as geometry.
        tagged = bytearray(data)
        first_list = len(groups) * 4
        tagged[first_list + 8:first_list + 12] = layout.SUBLIST_TAG.to_bytes(4, "little")
        assert not layout.is_derivable(bytes(tagged))
        try:
            read_models(bytes(tagged))
        except layout.BadPointerList as exc:
            assert "not a section" in str(exc), str(exc)
        else:
            raise AssertionError("read_models parsed a non-section list as models")
    finally:
        for store, was in ((layout.GEOMETRY_START, saved_start),
                           (layout.GEOMETRY_EXPECTED, saved_expected)):
            if was is None:
                store.pop("/SYNTH", None)
            else:
                store["/SYNTH"] = was

    print("modelfile: self_check ok")


def _check_image(image_path: str) -> int:
    """Assert the recorded geometry of both model files on a real disc."""
    import iso_source

    failures = 0
    with iso_source.open_disc(image_path) as disc:
        # First: is this the disc the variable claims?  Geometry is identical
        # on both, so reading only geometry would accept the English disc
        # without a word -- and WE2002_LOOKS_IMAGE names the Japanese track,
        # which is where every read in this project comes from.  One read of a
        # Japanese-only file through the guard settles it, and the refusal
        # names the problem.
        try:
            disc.read(layout.DAT2D)
            print("  disc is the Japanese one (%s accepted)" % layout.DAT2D)
        except layout.WrongDisc as exc:
            print("  FAILED %s" % exc)
            print("modelfile --check-image: 1 failure(s)")
            return 1

        for disc_path in (layout.MODEL, layout.EDT_MOD):
            data = disc.read(disc_path)
            try:
                print("  %s" % verify(data, disc_path))
            except AssertionError as exc:
                failures += 1
                print("  FAILED %s" % exc)

        edt = disc.read(layout.EDT_MOD)
        models = read_models(edt)
        print("  %s: %d models" % (layout.EDT_MOD, len(models)))
        for model in models:
            paired, alone = model.pairs()
            print("    list %d: %d sections, %d vertices, %d primitives"
                  % (model.index, len(model.sections), model.vertices,
                     model.primitives))
            print("      pairs %s  alone %s" % (paired, alone))
            if len(alone) != 1:
                failures += 1
                print("      FAILED expected exactly one unpaired section")

        shared = sorted(set(models[0].targets) & set(models[1].targets))
        print("    shared by both lists: %s" % shared)

        # File order is not list order, and this is where it is checked against
        # the real thing rather than against a synthetic.
        for model in models:
            if model.targets == sorted(model.targets):
                failures += 1
                print("    FAILED list %d is in file order -- the distinction "
                      "this module exists for would be untested" % model.index)

        model_data = disc.read(layout.MODEL)
        if layout.is_derivable(model_data):
            failures += 1
            print("  FAILED %s became derivable: geometry_start() would now "
                  "answer for it, and its lists still name a non-section"
                  % layout.MODEL)

    if failures:
        print("modelfile --check-image: %d failure(s)" % failures)
        return 1
    print("modelfile --check-image: ok")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        self_check()
        return 0
    if len(argv) == 3 and argv[1] == "--check-image":
        return _check_image(argv[2])
    if len(argv) == 2 and argv[1] == "--check-image":
        # No path: take it from the environment, and SKIP rather than pass when
        # it is not there.  77 is this repository's skip code across all five
        # projects, and the reason it is here and not in the ctest line is the
        # message -- a bare skip that does not name the variable is a skip
        # nobody acts on.
        import iso_source  # late, like _check_image: see its comment

        try:
            image = iso_source.image_from_env()
        except RuntimeError as exc:
            print("modelfile --check-image: skipped -- %s" % exc)
            return 77
        return _check_image(image)
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
