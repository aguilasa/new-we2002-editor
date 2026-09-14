#!/usr/bin/env python3
"""Count the files and bytes of a directory tree, per top-level entry.

Written for LOOKS-TASK-01, which had to state the size of the Superpack v6 in
NOTICE.md and found the plan's figures described a subfolder rather than the
root.  The repository rule is that every number in a document comes from a
tool that stayed in the tree, so this is that tool rather than a shell
one-liner nobody kept.

It reads nothing but directory metadata and never opens a file, so pointing it
at an unlicensed third-party collection copies none of it.

Usage:
    python tools/looks/superpack_count.py <directory>
    python tools/looks/superpack_count.py --check
"""

from __future__ import annotations

import os
import sys
import tempfile


def walk_count(root: str) -> tuple[int, int]:
    """Return (file count, total bytes) under *root*, recursively.

    Symlinks are not followed and unreadable entries are skipped, so the count
    is of what this machine can actually see.
    """
    files = 0
    total = 0
    for parent, _dirs, names in os.walk(root, followlinks=False):
        for name in names:
            path = os.path.join(parent, name)
            try:
                total += os.path.getsize(path)
            except OSError:
                continue
            files += 1
    return files, total


def breakdown(root: str) -> list[tuple[str, int, int]]:
    """Return [(entry, files, bytes)] for each top-level entry of *root*.

    A top-level file counts as itself, one file.  The rows sum to walk_count().
    """
    rows = []
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        if os.path.isdir(path):
            rows.append((entry,) + walk_count(path))
        else:
            try:
                rows.append((entry, 1, os.path.getsize(path)))
            except OSError:
                pass
    return rows


def self_check() -> None:
    """Build a known tree, count it, and demand the two answers agree.

    The red case is the one that matters: a breakdown whose rows do not sum to
    the recursive total means one of the two walks is wrong, and that is
    exactly the mistake this module exists to have avoided -- the plan's
    figures were a subfolder's, and nothing caught it.
    """
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "a", "deep"))
        os.makedirs(os.path.join(tmp, "b"))
        for path, size in [
            (os.path.join(tmp, "top.txt"), 3),
            (os.path.join(tmp, "a", "one.bin"), 10),
            (os.path.join(tmp, "a", "deep", "two.bin"), 100),
            (os.path.join(tmp, "b", "three.bin"), 1000),
        ]:
            with open(path, "wb") as handle:
                handle.write(b"\0" * size)

        files, total = walk_count(tmp)
        assert (files, total) == (4, 1113), (files, total)

        rows = breakdown(tmp)
        assert [r[0] for r in rows] == ["a", "b", "top.txt"], rows
        assert rows[0][1:] == (2, 110), rows[0]
        assert sum(r[1] for r in rows) == files, rows
        assert sum(r[2] for r in rows) == total, rows

        # Red case: a breakdown that skipped a top-level entry must not sum.
        partial = rows[:1]
        assert sum(r[1] for r in partial) != files
        assert sum(r[2] for r in partial) != total

    print("superpack_count: self_check ok")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip())
        return 2
    if argv[1] == "--check":
        self_check()
        return 0

    root = argv[1]
    if not os.path.isdir(root):
        print("not a directory: %s" % root, file=sys.stderr)
        return 1

    for entry, files, total in breakdown(root):
        print("%-28s %8d files %14d B" % (entry, files, total))
    files, total = walk_count(root)
    print("-" * 62)
    print("%-28s %8d files %14d B  (%.2f GiB)"
          % ("TOTAL", files, total, total / 1024 ** 3))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
