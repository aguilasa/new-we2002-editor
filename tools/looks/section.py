#!/usr/bin/env python3
"""The section format: a header, its primitives, its vertices, and the gap.

One section of a model file is:

    uint32 numVertex | uint32 numPrimitive
    primitive[numPrimitive]     24 bytes each
    vertex[numVertex]            8 bytes each

This module knows that shape and nothing about where sections live -- offsets
belong to layout.py, and walking a whole file belongs to modelfile.py.  What it
adds over the description in the `we3d` analysis is the gap rule below and the
mode byte, both measured here.

IT IS NOT TMD.  The 24-byte primitive is a *gradation, no-texture* quad: four
colours and four indices, with **no UV**.  Reading it as a TMD packet -- which
carries a 4-byte header and, when textured, UV pairs -- misaligns everything
after the first primitive and the damage looks like a wrong start offset.

Usage:
    python tools/looks/section.py --check
"""

from __future__ import annotations

import struct
import sys

HEADER_SIZE = 8
PRIMITIVE_SIZE = 24
VERTEX_SIZE = 8

COLOURS_PER_PRIMITIVE = 4
INDICES_PER_PRIMITIVE = 4


class BadSection(Exception):
    """Raised when bytes at an offset do not parse as a section."""


class Primitive:
    """One quad: four corner colours and four vertex indices.

    Two things here are easy to get wrong, and both are recorded rather than
    smoothed over.

    **The index order as stored is v1, v0, v3, v2** -- not v0..v3.  That is the
    `we3d` reading and this module preserves the stored order in `indices`,
    offering `corners` for the untangled one.  Nothing here has *verified* the
    untangling: it is third-party opinion until something renders, so the raw
    order stays available and is what round-trips.

    **The fourth byte of each colour is a mode byte, not padding.**  The `we3d`
    description calls it pad.  Measured over all 1,767 primitives of MODEL.BIN
    (2026-09-14): in colour 0 it is never zero -- 120, 121, 122 or 127 -- and
    in colours 1, 2 and 3 it is always zero.  So it is one mode byte per
    primitive, carried in the first colour, and this module keeps it.  It is
    what unknown (d) of the plan turns on in phase 3, and a parser that
    discarded it would have to be rewritten there.
    """

    __slots__ = ("colours", "indices", "mode")

    def __init__(self, colours, indices, mode):
        self.colours = colours
        """4 x (blue, green, red) -- PSX byte order, not RGB."""
        self.indices = indices
        """The four vertex indices exactly as stored: v1, v0, v3, v2."""
        self.mode = mode
        """The fourth byte of colour 0.  See the class docstring."""

    @property
    def corners(self):
        """The indices reordered to v0, v1, v2, v3, per the `we3d` reading."""
        v1, v0, v3, v2 = self.indices
        return (v0, v1, v2, v3)

    def __repr__(self):
        return "Primitive(mode=0x%02x, indices=%r)" % (self.mode, self.indices)


class Vertex:
    """A signed 16-bit point, plus the padding halfword that follows it.

    The padding is kept rather than dropped because rule 2 of the plan says raw
    bytes are normative: a caller that wants to prove it read the file right
    can check it.  Measured over all 2,461 vertices of MODEL.BIN on 2026-09-14,
    it is zero every time -- which is what makes it padding and not a fourth
    coordinate.
    """

    __slots__ = ("x", "y", "z", "pad")

    def __init__(self, x, y, z, pad):
        self.x = x
        self.y = y
        self.z = z
        self.pad = pad

    def __repr__(self):
        return "Vertex(%d, %d, %d)" % (self.x, self.y, self.z)


class Section:
    """A parsed section, and the span of the file it occupied."""

    __slots__ = ("offset", "primitives", "vertices")

    def __init__(self, offset, primitives, vertices):
        self.offset = offset
        self.primitives = primitives
        self.vertices = vertices

    @property
    def size(self):
        return section_size(len(self.vertices), len(self.primitives))

    @property
    def end(self):
        return self.offset + self.size

    def __repr__(self):
        return "Section(at=%d, vertices=%d, primitives=%d)" % (
            self.offset, len(self.vertices), len(self.primitives)
        )


def section_size(vertices: int, primitives: int) -> int:
    """Bytes a section with these counts occupies, header included."""
    return HEADER_SIZE + primitives * PRIMITIVE_SIZE + vertices * VERTEX_SIZE


def read_header(data: bytes, offset: int) -> tuple[int, int]:
    """(numVertex, numPrimitive) at *offset*, as little-endian uint32."""
    if offset + HEADER_SIZE > len(data):
        raise BadSection(
            "offset %d + %d-byte header runs past the %d bytes available"
            % (offset, HEADER_SIZE, len(data))
        )
    return struct.unpack_from("<2I", data, offset)


def is_separator(data: bytes, offset: int) -> bool:
    """Is the header at *offset* the 0/0 pair that ends a group?

    This is the correction the naive reading needs.  A walk that treats 0/0 as
    end-of-file stops at section 55 of MODEL.BIN and looks like a wrong format;
    it is a group boundary, and there are six groups.
    """
    try:
        vertices, primitives = read_header(data, offset)
    except BadSection:
        return False
    return vertices == 0 and primitives == 0


def skip_gap(data: bytes, offset: int) -> int:
    """Advance past a run of zero words, returning the next live offset.

    **The gap is a run of zero WORDS, not a fixed eight bytes**, and that
    distinction is the whole difference between the two model files.  Measured
    2026-09-14: MODEL.BIN separates its six groups with exactly 8 zero bytes,
    so the fixed rule happens to work there; EDT_MOD.BIN has 12 bytes between
    its first three sections and 8 between the rest, so a walker that always
    consumes 8 lands 4 bytes into the next header and reads a vertex count of
    65,563 and a primitive count in the billions.

    With the run rule both files walk to their exact EOF -- which is the test
    that says the rule is right rather than merely tolerated.
    """
    while offset + 4 <= len(data):
        if struct.unpack_from("<I", data, offset)[0] != 0:
            break
        offset += 4
    return offset


def read_primitive(data: bytes, offset: int) -> Primitive:
    """One 24-byte primitive at *offset*."""
    if offset + PRIMITIVE_SIZE > len(data):
        raise BadSection(
            "primitive at %d runs past the %d bytes available" % (offset, len(data))
        )
    colours = []
    for slot in range(COLOURS_PER_PRIMITIVE):
        blue, green, red, fourth = data[offset + slot * 4: offset + slot * 4 + 4]
        colours.append((blue, green, red))
        if slot == 0:
            mode = fourth
    indices = struct.unpack_from("<4H", data, offset + COLOURS_PER_PRIMITIVE * 4)
    return Primitive(tuple(colours), indices, mode)


def read_vertex(data: bytes, offset: int) -> Vertex:
    """One 8-byte vertex at *offset*."""
    if offset + VERTEX_SIZE > len(data):
        raise BadSection(
            "vertex at %d runs past the %d bytes available" % (offset, len(data))
        )
    x, y, z, pad = struct.unpack_from("<3hH", data, offset)
    return Vertex(x, y, z, pad)


def read_section(data: bytes, offset: int) -> Section:
    """Parse the section at *offset*, refusing one that does not fit."""
    vertices, primitives = read_header(data, offset)
    if vertices == 0 and primitives == 0:
        raise BadSection(
            "offset %d is a group separator (0/0), not a section -- see "
            "is_separator()" % offset
        )

    size = section_size(vertices, primitives)
    if offset + size > len(data):
        raise BadSection(
            "section at %d claims %d vertices and %d primitives (%d bytes), "
            "which runs %d bytes past the end of the %d available -- the usual "
            "cause is a start offset landing inside a gap"
            % (offset, vertices, primitives, size,
               offset + size - len(data), len(data))
        )

    first_primitive = offset + HEADER_SIZE
    parsed_primitives = [
        read_primitive(data, first_primitive + i * PRIMITIVE_SIZE)
        for i in range(primitives)
    ]

    first_vertex = first_primitive + primitives * PRIMITIVE_SIZE
    parsed_vertices = [
        read_vertex(data, first_vertex + i * VERTEX_SIZE) for i in range(vertices)
    ]

    return Section(offset, parsed_primitives, parsed_vertices)


def walk(data: bytes, start: int):
    """Yield ``(section, group)`` from *start* to the end of *data*.

    *group* counts from zero and rises at every separator, so a caller learns
    the grouping without a second pass.  The walk stops when fewer than a
    header's worth of bytes remain, which for both model files is the exact
    end of the file.
    """
    offset = start
    group = 0
    while offset + HEADER_SIZE <= len(data):
        if is_separator(data, offset):
            after = skip_gap(data, offset)
            if after == offset:  # pragma: no cover - skip_gap always advances here
                break
            offset = after
            group += 1
            continue
        section = read_section(data, offset)
        yield section, group
        offset = section.end


class Scan:
    """What a full pass over a file found, and where it stopped.

    `end` is not the last section's end.  EDT_MOD.BIN closes with an 8-byte
    gap after its final section, so the last section ends at 36,064 while the
    file is 36,072 bytes; reporting the section end would make an exact-EOF
    assertion fail on a file that parsed perfectly.  MODEL.BIN has no trailing
    gap and the two coincide there -- which is exactly why measuring only that
    file would have hidden the distinction.
    """

    __slots__ = ("sections", "groups", "end")

    def __init__(self, sections, groups, end):
        self.sections = sections
        """Every section, in FILE order."""
        self.groups = groups
        """How many sections each group holds, in order."""
        self.end = end
        """The offset the pass stopped at, trailing gap consumed."""

    @property
    def vertices(self):
        return sum(len(section.vertices) for section in self.sections)

    @property
    def primitives(self):
        return sum(len(section.primitives) for section in self.sections)

    def __repr__(self):
        return "Scan(sections=%d, vertices=%d, primitives=%d, end=%d)" % (
            len(self.sections), self.vertices, self.primitives, self.end
        )


def scan(data: bytes, start: int) -> Scan:
    """Walk from *start* to the end and report what was found and where it ended.

    **The sections come back in FILE order, which is not the order they are
    drawn in.** For EDT_MOD.BIN the pointer list in the header names the same
    eleven offsets in a different sequence -- 19,440 first and 15,704 eighth,
    measured 2026-09-14 -- and that list is the assembly order.  A caller that
    needs the pieces in the right order wants modelfile.py, not this.  Taking
    file order for assembly order shuffles the body silently, which is the
    mistake the PES2 squad tables already paid for once.
    """
    sections = []
    groups = []
    current = 0
    offset = start

    while offset + HEADER_SIZE <= len(data):
        at_separator = is_separator(data, offset)
        if at_separator:
            after = skip_gap(data, offset)
            if after == offset:
                break
            offset = after
            groups.append(current)
            current = 0
            continue
        section = read_section(data, offset)
        sections.append(section)
        current += 1
        offset = section.end

    if current:
        groups.append(current)
    return Scan(sections, groups, offset)


def build_section(vertices, primitives, mode: int = 0x78) -> bytes:  # not-an-address: a primitive mode byte
    """Assemble a section from counts, for tests and for the red case.

    *vertices* and *primitives* are counts; the content is filler with a
    recognisable shape.  It exists so self_check() can assert against bytes it
    constructed rather than against a disc it may not have.
    """
    out = bytearray(struct.pack("<2I", vertices, primitives))
    for index in range(primitives):
        out += bytes((1, 2, 3, mode))
        out += bytes((4, 5, 6, 0)) * 3
        out += struct.pack("<4H", index, index + 1, index + 2, index + 3)
    for index in range(vertices):
        out += struct.pack("<3hH", index, -index, index * 2, 0)
    return bytes(out)


def self_check() -> None:
    """Parse bytes we built, then break the primitive size and demand red."""
    vertices, primitives = 5, 3
    body = build_section(vertices, primitives, mode=0x7A)  # not-an-address: mode byte
    assert len(body) == section_size(vertices, primitives), len(body)

    section = read_section(body, 0)
    assert len(section.vertices) == vertices
    assert len(section.primitives) == primitives
    assert section.end == len(body)

    first = section.primitives[0]
    assert first.mode == 0x7A, first.mode  # not-an-address: mode byte
    assert first.colours[0] == (1, 2, 3), first.colours
    assert first.colours[1] == (4, 5, 6), first.colours

    # Stored order is v1, v0, v3, v2; `corners` is the untangling, and the two
    # have to disagree or the reordering is not being exercised at all.
    assert first.indices == (0, 1, 2, 3), first.indices
    assert first.corners == (1, 0, 3, 2), first.corners
    assert first.corners != first.indices

    third = section.vertices[3]
    assert (third.x, third.y, third.z, third.pad) == (3, -3, 6, 0)

    # -- Red 1: the size the whole format hangs on ------------------------
    #
    # The control the plan names first: change 24 to 20 and the walk has to go
    # red.  Done in process rather than by editing the file, so it runs on
    # every gate rather than only when controls.py plants it.
    # The assertion is about the WALK and not about one section's span.  A
    # shorter primitive still parses -- the section merely looks smaller -- so
    # an exception is the wrong thing to demand.  What breaks is the next
    # offset: the walk resumes 12 bytes early, lands inside the previous
    # section's vertex data, and reads a header out of coordinates.  That is
    # what happens on a real file, so that is what the control has to show.
    pair = build_section(2, 1) + build_section(3, 2)
    assert [section.offset for section, _ in walk(pair, 0)] == [0, len(build_section(2, 1))]

    global PRIMITIVE_SIZE
    saved = PRIMITIVE_SIZE
    try:
        PRIMITIVE_SIZE = 20
        try:
            walked_broken = [section.offset for section, _ in walk(pair, 0)]
        except BadSection:
            walked_broken = "refused"
        assert walked_broken != [0, len(build_section(2, 1))], (
            "primitive size 20 walked the same as 24: the size is not "
            "load-bearing in this parser, so the control proves nothing"
        )
        assert read_section(body, 0).end != len(body)
    finally:
        PRIMITIVE_SIZE = saved

    # And green again once it is put back, so the red above is the size and
    # not some leftover state.
    assert read_section(body, 0).end == len(body)
    assert [section.offset for section, _ in walk(pair, 0)] == [0, len(build_section(2, 1))]

    # -- Red 2: a section that does not fit is refused, and says why -------
    try:
        read_section(body[:-1], 0)
    except BadSection as exc:
        assert "past the end" in str(exc), str(exc)
    else:
        raise AssertionError("a truncated section parsed as whole")

    # -- Red 3: a separator is not a section, and not end-of-file ---------
    separator = struct.pack("<2I", 0, 0)
    assert is_separator(separator, 0)
    try:
        read_section(separator, 0)
    except BadSection as exc:
        assert "separator" in str(exc), str(exc)
    else:
        raise AssertionError("a group separator parsed as a section")

    # -- Red 4: the gap is a run of zero WORDS, not a fixed eight bytes ----
    #
    # The failure this closes was measured on EDT_MOD.BIN, whose first gaps are
    # 12 bytes.  A walker that always consumes 8 starts the next section 4
    # bytes early.  Two sections with a 12-byte gap; a fixed-8 reading finds
    # the second one misaligned, the run reading finds it.
    one = build_section(2, 1)
    two = build_section(3, 2)
    joined = one + b"\x00" * 12 + two
    walked = [section for section, _group in walk(joined, 0)]
    assert len(walked) == 2, walked
    assert walked[1].offset == len(one) + 12, walked[1].offset
    assert walked[1].end == len(joined), walked[1].end
    assert skip_gap(joined, len(one)) == len(one) + 12
    assert len(one) + HEADER_SIZE != len(one) + 12  # the fixed rule would differ

    # -- The group counter rises at the separator, and only there ---------
    groups = [group for _section, group in walk(joined, 0)]
    assert groups == [0, 1], groups
    assert [g for _s, g in walk(one + two, 0)] == [0, 0]

    # -- Red 5: a trailing gap means the last section does NOT end at EOF --
    #
    # The distinction that only EDT_MOD.BIN shows: it closes with 8 zero bytes
    # after its final section.  A scan that reported the last section's end
    # would come up short on a file it parsed perfectly, and someone would go
    # looking for a missing section that is not missing.
    with_tail = one + two + b"\x00" * 8
    tailed = scan(with_tail, 0)
    assert len(tailed.sections) == 2, tailed
    assert tailed.sections[-1].end == len(one) + len(two)
    assert tailed.end == len(with_tail), (tailed.end, len(with_tail))
    assert tailed.sections[-1].end != tailed.end

    # And without a tail the two coincide -- which is why MODEL.BIN alone
    # would not have shown the difference.
    untailed = scan(one + two, 0)
    assert untailed.end == untailed.sections[-1].end == len(one + two)

    # The counts add up the way a caller will ask for them.
    assert untailed.vertices == 2 + 3
    assert untailed.primitives == 1 + 2
    assert scan(joined, 0).groups == [1, 1], scan(joined, 0).groups

    print("section: self_check ok")


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        self_check()
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
