"""A PNG reader (and a small writer) in the standard library: `zlib`, `struct`.

What it is for is the emulator: `read_vram_region`, `dump_vram` and the
screenshot tools answer with a PNG file, and the package keeps no imaging
dependency (rule (a)), so the one way to compare what the GPU holds with
what a disc holds is to decode it here.

Eight bits per channel, non-interlaced, colour types 0 (grey), 2 (RGB),
3 (palette, with `tRNS`), 4 (grey + alpha) and 6 (RGBA): every shape the
emulator writes and every shape a user's editor saves an 8-bit image in.
All five row filters. Anything else -- 16-bit, 1/2/4-bit, Adam7 -- raises
`PngError` rather than guessing, because a misread PNG comes out as
plausible colours. So does a chunk whose CRC does not match.

Three readings of one decoded `Png`, each the shape a caller already has:

- `read_png(path)` -> `(width, height, rows)`, rows of `(r, g, b)` tuples,
  alpha dropped, palette and grey expanded;
- `read_rgba(path)` -> the same with `(r, g, b, a)`;
- `read_indexed(path)` -> `(width, height, indices, palette)`, the raw
  bytes of an 8-bit palette image and its `(r, g, b, a)` entries.

`write_png` writes any of the five colour types with a chosen row filter;
it exists so the self check can produce what it decodes.
"""

# lineage: read_png of tools/looks/atlas.py (the (width, height, rows of
# (r, g, b)) shape) and read_png of tools/pes2/asset_write.py (the
# (width, height, indices, palette) shape), merged; write_png after
# atlas.write_png, generalised to every colour type and filter.

import collections
import struct
import zlib

SIGNATURE = b"\x89PNG\r\n\x1a\n"

CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
"""Bytes per pixel at eight bits, by colour type."""

FILTERS = (0, 1, 2, 3, 4)
"""None, Sub, Up, Average, Paeth."""

Png = collections.namedtuple("Png", "width height colour lines palette")
Png.__doc__ = """One decoded image, before any reading of it.

`lines` is one `bytes` per row, unfiltered, `CHANNELS[colour]` bytes a
pixel; `palette` is a list of `(r, g, b, a)` (empty unless colour type 3).
"""


class PngError(ValueError):
    """A file this reader will not decode, with the reason."""


def _paeth(left, up, upleft):
    guess = left + up - upleft
    pa, pb, pc = abs(guess - left), abs(guess - up), abs(guess - upleft)
    if pa <= pb and pa <= pc:
        return left
    return up if pb <= pc else upleft


def _unfilter(kind, line, previous, bpp, where):
    for i in range(len(line)):
        left = line[i - bpp] if i >= bpp else 0
        up = previous[i]
        if kind == 1:
            line[i] = (line[i] + left) & 255
        elif kind == 2:
            line[i] = (line[i] + up) & 255
        elif kind == 3:
            line[i] = (line[i] + (left + up) // 2) & 255
        elif kind == 4:
            upleft = previous[i - bpp] if i >= bpp else 0
            line[i] = (line[i] + _paeth(left, up, upleft)) & 255
        elif kind:
            raise PngError("%s uses filter %d on a row" % (where, kind))
    return line


def decode(blob, where="the PNG"):
    """The `Png` in `blob`, the bytes of a PNG file."""
    if blob[:8] != SIGNATURE:
        raise PngError("%s does not open with a PNG signature" % where)
    at = 8
    header, palette, trns, data = None, [], b"", bytearray()
    while True:
        if at + 12 > len(blob):
            raise PngError("%s ends before its IEND chunk" % where)
        length, tag = struct.unpack_from(">I4s", blob, at)
        body = blob[at + 8:at + 8 + length]
        if len(body) != length or at + 12 + length > len(blob):
            raise PngError("%s: chunk %r runs past the end" % (where, tag))
        crc = struct.unpack_from(">I", blob, at + 8 + length)[0]
        if zlib.crc32(tag + body) != crc:
            raise PngError("%s: chunk %r fails its CRC" % (where, tag))
        at += 12 + length
        if tag == b"IHDR":
            header = struct.unpack(">IIBBBBB", body)
        elif tag == b"PLTE":
            palette = [tuple(body[i:i + 3]) for i in range(0, len(body), 3)]
        elif tag == b"tRNS":
            trns = body
        elif tag == b"IDAT":
            data += body
        elif tag == b"IEND":
            break
    if header is None:
        raise PngError("%s has no IHDR" % where)
    width, height, depth, colour, _comp, _filt, interlace = header
    if depth != 8 or interlace or colour not in CHANNELS:
        raise PngError("%s is depth %d colour type %d interlace %d, and this "
                       "reader does 8-bit non-interlaced 0/2/3/4/6"
                       % (where, depth, colour, interlace))
    if colour == 3 and not palette:
        raise PngError("%s is a palette image with no PLTE" % where)
    bpp = CHANNELS[colour]
    stride = width * bpp
    try:
        raw = zlib.decompress(bytes(data))
    except zlib.error as exc:
        raise PngError("%s: IDAT does not inflate: %s" % (where, exc))
    if len(raw) < height * (1 + stride):
        raise PngError("%s: IDAT holds %d byte(s), %dx%d needs %d"
                       % (where, len(raw), width, height,
                          height * (1 + stride)))
    lines, previous = [], bytearray(stride)
    for row in range(height):
        start = row * (1 + stride)
        line = _unfilter(raw[start], bytearray(raw[start + 1:start + 1
                                                   + stride]),
                         previous, bpp, "%s row %d" % (where, row))
        lines.append(bytes(line))
        previous = line
    alpha = list(trns[:len(palette)]) + [255] * (len(palette) - len(trns))
    return Png(width, height, colour, lines,
               [c + (a,) for c, a in zip(palette, alpha)])


def read(path):
    """The `Png` of the file at `path`."""
    with open(path, "rb") as handle:
        return decode(handle.read(), path)


def pixels(image, alpha=False):
    """Rows of `(r, g, b)` -- or `(r, g, b, a)` -- tuples of a `Png`."""
    out = []
    for line in image.lines:
        if image.colour == 3:
            try:
                row = [image.palette[v] for v in line]
            except IndexError:
                raise PngError("an index past the %d-entry palette"
                               % len(image.palette))
        elif image.colour == 0:
            row = [(v, v, v, 255) for v in line]
        elif image.colour == 4:
            row = [(line[i], line[i], line[i], line[i + 1])
                   for i in range(0, len(line), 2)]
        elif image.colour == 2:
            row = [tuple(line[i:i + 3]) + (255,)
                   for i in range(0, len(line), 3)]
        else:
            row = [tuple(line[i:i + 4]) for i in range(0, len(line), 4)]
        out.append(row if alpha else [p[:3] for p in row])
    return out


def read_png(path):
    """`(width, height, rows of (r, g, b))`: the shape the callers had."""
    image = read(path)
    return image.width, image.height, pixels(image)


def read_rgba(path):
    """`(width, height, rows of (r, g, b, a))`."""
    image = read(path)
    return image.width, image.height, pixels(image, alpha=True)


def read_indexed(path):
    """`(width, height, indices, palette)` of an 8-bit palette PNG.

    `indices` is `width * height` bytes, row by row; `palette` the
    `(r, g, b, a)` entries, alpha from `tRNS` and 255 past it. Any other
    colour type raises `PngError`: there are no indices to give.
    """
    image = read(path)
    if image.colour != 3:
        raise PngError("%s is colour type %d, not an 8-bit palette image"
                       % (path, image.colour))
    return image.width, image.height, b"".join(image.lines), image.palette


def _filter(kind, line, previous, bpp):
    out = bytearray(len(line))
    for i in range(len(line)):
        left = line[i - bpp] if i >= bpp else 0
        up = previous[i]
        upleft = previous[i - bpp] if i >= bpp else 0
        guess = (0, left, up, (left + up) // 2,
                 _paeth(left, up, upleft))[kind]
        out[i] = (line[i] - guess) & 255
    return out


def encode(width, height, lines, colour=2, palette=None, filters=0):
    """The bytes of a PNG of `lines` (one `bytes` per row, raw samples).

    `palette`: `(r, g, b[, a])` entries for colour type 3. `filters`: one
    filter type for every row, or a sequence giving each row its own.
    """
    if colour not in CHANNELS:
        raise PngError("colour type %r is not one this writes" % (colour,))
    bpp = CHANNELS[colour]
    if len(lines) != height or any(len(l) != width * bpp for l in lines):
        raise PngError("%d line(s) do not make %dx%d at %d byte(s) a pixel"
                       % (len(lines), width, height, bpp))
    kinds = [filters] * height if isinstance(filters, int) else list(filters)

    def chunk(tag, body):
        return (struct.pack(">I", len(body)) + tag + body
                + struct.pack(">I", zlib.crc32(tag + body)))

    raw, previous = bytearray(), bytes(width * bpp)
    for kind, line in zip(kinds, lines):
        if kind not in FILTERS:
            raise PngError("filter %r is not one of %s" % (kind, FILTERS))
        raw.append(kind)
        raw += _filter(kind, line, previous, bpp)
        previous = line
    body = SIGNATURE + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height,
                                                  8, colour, 0, 0, 0))
    if colour == 3:
        entries = list(palette or ())
        body += chunk(b"PLTE", b"".join(bytes(c[:3]) for c in entries))
        if any(len(c) > 3 and c[3] != 255 for c in entries):
            body += chunk(b"tRNS", bytes(c[3] if len(c) > 3 else 255
                                         for c in entries))
    return (body + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def write_png(path, width, height, lines, colour=2, palette=None, filters=0):
    """`encode` to the file at `path`; returns how many bytes it wrote."""
    blob = encode(width, height, lines, colour, palette, filters)
    with open(path, "wb") as handle:
        handle.write(blob)
    return len(blob)


# ---- self check ----------------------------------------------------------

VECTOR_STREAM = ("01003b76252525252525026565656666666767670398b5d347c74747c747"
                 "0465656528282867282804656565292929292929")
"""Five filtered rows of a 3x5 RGB image, filter byte first in each."""

VECTOR_PIXELS = [(0, 59, 118), (37, 96, 155), (74, 133, 192),
                 (101, 160, 219), (139, 198, 1), (177, 236, 39),
                 (202, 5, 64), (241, 44, 103), (24, 83, 142),
                 (47, 106, 165), (87, 146, 205), (127, 186, 245),
                 (148, 207, 10), (189, 248, 51), (230, 33, 92)]
"""What Pillow decoded `VECTOR_STREAM` to."""

TIE_STREAM = "040a0208fc04fc22ee22"
"""Two Paeth-filtered rows of a 4x2 grey image built to tie the predictor:
at (1, 1) the left and the upper-left distances tie, at (3, 1) the upper and
the upper-left. The order of the tie-break decides what decodes."""

TIE_PIXELS = [10, 12, 20, 16, 6, 40, 22, 50]
"""What Pillow decoded `TIE_STREAM` to."""

def _sample(width, height, bpp):
    """Rows of samples that make every filter predict something non-trivial."""
    return [bytes((x * 37 + y * 101 + c * 59 + (x * y) % 13) & 255
                  for x in range(width) for c in range(bpp))
            for y in range(height)]


def self_check():
    """Decode what `encode` wrote, pixel by pixel, for each filter and each
    colour type, and the refusals.

    Returns one `(name, passed, detail)` per assertion.
    """
    out = []
    width, height = 7, 5
    rgb = _sample(width, height, 3)
    want = [[tuple(line[i:i + 3]) for i in range(0, len(line), 3)]
            for line in rgb]
    for kind in FILTERS:
        image = decode(encode(width, height, rgb, 2, filters=kind))
        got = pixels(image)
        bad = [(x, y) for y in range(height) for x in range(width)
               if got[y][x] != want[y][x]]
        out.append(("filter %d: an RGB image decodes pixel for pixel" % kind,
                    not bad and (image.width, image.height) == (width, height),
                    bad[:4]))
    mixed = decode(encode(width, height, rgb, 2, filters=[0, 1, 2, 3, 4]))
    out.append(("one image with all five filters, one per row, decodes",
                pixels(mixed) == want, ""))

    # Two fixed vectors, so a bug shared by `_filter` and `_unfilter` cannot
    # pass as a round trip: these filtered rows decode to the pixels kept
    # beside them under Pillow 12.3.0, checked once on 2026-10-22 and kept as
    # constants (this module never imports Pillow).
    stream = bytes.fromhex(VECTOR_STREAM)
    lines = [stream[r * 10 + 1:r * 10 + 10] for r in range(5)]
    kinds = [stream[r * 10] for r in range(5)]
    previous, decoded = bytearray(9), []
    for kind, line in zip(kinds, lines):
        previous = _unfilter(kind, bytearray(line), previous, 3, "vector")
        decoded.append([tuple(previous[i:i + 3]) for i in range(0, 9, 3)])
    out.append(("a fixed vector of all five filters decodes as Pillow did",
                kinds == [1, 2, 3, 4, 4]
                and [p for row in decoded for p in row] == VECTOR_PIXELS,
                decoded[:1]))

    stream = bytes.fromhex(TIE_STREAM)
    previous, decoded = bytearray(4), []
    for row in range(2):
        previous = _unfilter(stream[row * 5], bytearray(stream[row * 5 + 1:
                                                               row * 5 + 5]),
                             previous, 1, "tie vector")
        decoded += list(previous)
    out.append(("Paeth breaks its ties left, then up, then upper-left, as "
                "Pillow did", decoded == TIE_PIXELS, decoded))

    rgba = _sample(width, height, 4)
    got = pixels(decode(encode(width, height, rgba, 6, filters=4)), alpha=True)
    out.append(("an RGBA image keeps its alpha in read_rgba's shape",
                got == [[tuple(l[i:i + 4]) for i in range(0, len(l), 4)]
                        for l in rgba], ""))
    grey = _sample(width, height, 1)
    out.append(("a grey image reads as (v, v, v)",
                pixels(decode(encode(width, height, grey, 0, filters=3)))
                == [[(v, v, v) for v in l] for l in grey], ""))
    grey_alpha = _sample(width, height, 2)
    out.append(("a grey + alpha image reads as (v, v, v, a)",
                pixels(decode(encode(width, height, grey_alpha, 4,
                                     filters=1)), alpha=True)
                == [[(l[i], l[i], l[i], l[i + 1]) for i in range(0, len(l), 2)]
                    for l in grey_alpha], ""))

    palette = [(i * 9 & 255, i * 5 & 255, 255 - i, 128 if i < 4 else 255)
               for i in range(20)]
    indices = [bytes((x + 3 * y) % 20 for x in range(width))
               for y in range(height)]
    image = decode(encode(width, height, indices, 3, palette, filters=2))
    out.append(("a palette image keeps its indices and its tRNS alpha",
                b"".join(image.lines) == b"".join(indices)
                and image.palette == palette, ""))
    out.append(("a palette image reads as its colours, alpha dropped",
                pixels(image) == [[palette[v][:3] for v in l]
                                  for l in indices], ""))

    good = encode(width, height, rgb, 2, filters=1)
    ihdr = struct.pack(">IIBBBBB", width, height, 16, 2, 0, 0, 0)
    deep = (good[:8] + struct.pack(">I", 13) + b"IHDR" + ihdr
            + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr)) + good[33:])
    refusals = (
        ("a missing signature", b"GIF89a" + good[6:], "signature"),
        ("a flipped CRC", good[:30] + bytes([good[30] ^ 1]) + good[31:],
         "fails its CRC"),
        ("a 16-bit image with a good CRC", deep, "depth 16"),
        ("a truncated file", good[:len(good) // 2], "past the end"),
    )
    for name, blob, reason in refusals:
        try:
            decode(blob)
            out.append(("decode refuses %s" % name, False, "decoded"))
        except PngError as exc:
            out.append(("decode refuses %s" % name, reason in str(exc), exc))
    raw = bytearray(b"".join(b"\x00" + line for line in rgb))
    raw[0] = 5
    idat = zlib.compress(bytes(raw))
    head = good[:33]
    bad_filter = (head + struct.pack(">I", len(idat)) + b"IDAT" + idat
                  + struct.pack(">I", zlib.crc32(b"IDAT" + idat))
                  + good[-12:])
    try:
        decode(bad_filter)
        out.append(("decode refuses an unknown filter type", False, ""))
    except PngError as exc:
        out.append(("decode refuses an unknown filter type",
                    "filter 5" in str(exc), exc))
    return out
