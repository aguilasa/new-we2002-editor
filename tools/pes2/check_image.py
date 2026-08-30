#!/usr/bin/env python3
"""Run every PES2 check that needs a real disc image. Skips without one.

The pattern is the one `WE2002_TEST_IMAGE` already uses in this
repository: the image is ~445 MiB and cannot be committed, so the test
reports itself *skipped* rather than failing on a machine that has no
copy of it.

    Variables it reads, all optional except the first:

    WE2002_PES2_IMAGE    data track (.bin) of one release  -- without it,
                         this exits 77 and ctest records a skip
    WE2002_PES2_IMAGE_B  data track of the other release, for the
                         release diff of plan section 1.12
    WE2002_PES2_CARD     a raw .mcd/.mcr memory card, for the squad
                         alignment of plan section 3.3
    WE2002_PES2_TMPDIR   where the negative control may put its ~450 MiB
                         working copy; without it the negative control is
                         skipped rather than filling /tmp

Nothing here writes to the images it is given: the only write path taken
is the negative control, and that works on a copy.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso                                                   # noqa: E402
import tables                                                # noqa: E402
import faq_check                                             # noqa: E402
import diff_releases                                         # noqa: E402
import memcard                                               # noqa: E402

SKIP = 77


class Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def main():
    image = os.environ.get("WE2002_PES2_IMAGE", "").strip()
    if not image:
        print("WE2002_PES2_IMAGE is not set -- skipping the PES2 image checks.")
        print("Point it at the data track of a Pro Evolution Soccer 2 (Europe)")
        print("dump, e.g. roms/…(EsIt)/…(Track 1).bin")
        return SKIP
    if not os.path.exists(image):
        print(f"WE2002_PES2_IMAGE={image} does not exist", file=sys.stderr)
        return 1

    bad = 0

    print("== anchors (plan 1.13) ==")
    bad += iso.cmd_anchors(Args(image=image))

    print("\n== tables (plan 1.6) ==")
    bad += tables.cmd(Args(image=image, check=True, dump=None, verbose=False))

    print("\n== docs/PES2-NOMES.md against the disc ==")
    bad += faq_check.main(["--image", image])

    other = os.environ.get("WE2002_PES2_IMAGE_B", "").strip()
    if other and os.path.exists(other):
        print("\n== release diff (plan 1.12) ==")
        bad += diff_releases.main([image, other, "--check"])
    else:
        print("\n== release diff: skipped, set WE2002_PES2_IMAGE_B ==")

    card = os.environ.get("WE2002_PES2_CARD", "").strip()
    if card and os.path.exists(card):
        print("\n== memory card alignment (plan 3.3) ==")
        bad += memcard.main([card, image, "--check"])
    else:
        print("\n== memory card: skipped, set WE2002_PES2_CARD ==")

    tmpdir = os.environ.get("WE2002_PES2_TMPDIR", "").strip()
    if tmpdir and os.path.isdir(tmpdir):
        print("\n== negative control (plan 5.1) ==")
        bad += iso.cmd_negative(Args(image=image, tmpdir=tmpdir))
    else:
        print("\n== negative control: skipped, set WE2002_PES2_TMPDIR to a "
              "directory with ~450 MiB free ==")

    print("\nFAILED" if bad else "\nALL OK")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
