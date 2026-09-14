#!/usr/bin/env python3
"""Count the files and bytes of a directory tree, per top-level entry.

Written for LOOKS-TASK-01, which had to state the size of the Superpack v6 in
NOTICE.md and found the plan's figures described a subfolder rather than the
root.  The repository rule is that every number in a document comes from a
tool that stayed in the tree, so this is that tool rather than a shell
one-liner nobody kept.

It reads nothing but directory metadata and never opens a file, so pointing it
at an unlicensed third-party collection copies none of it.

What it cannot do is answer partially and stay quiet about it: a number that
lands in NOTICE.md has to come from a run that saw everything.  Every entry
this machine could not read is counted, named on stderr, reported as
"skipped: N", and makes the exit code non-zero.

Usage:
    python tools/looks/superpack_count.py <directory>
    python tools/looks/superpack_count.py --check
"""

from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile


_ANNOUNCED: set[str] = set()


def _note(notes: list[OSError], error: OSError) -> None:
    """Record one unreadable entry, and say so where it cannot be summed away.

    Counting and announcing are not the same act here: main() walks the tree
    twice on purpose -- once per top-level entry, once whole -- so that the
    rows and the TOTAL are an arithmetic cross-check of each other, and both
    walks meet the same unreadable entry.  Each walk counts it, because each
    walk's own total is short by it; the name is printed once, because the
    reader is being told about an entry and not about a traversal.
    """
    notes.append(error)
    name = error.filename or "<unnamed>"
    if name in _ANNOUNCED:
        return
    _ANNOUNCED.add(name)
    print("skipped (%s): %s" % (error.strerror or error.__class__.__name__,
                                name),
          file=sys.stderr)


def walk_count(root: str, skipped: list[OSError] | None = None
               ) -> tuple[int, int, int]:
    """Return (file count, total bytes, skipped count) under *root*.

    Symlinks are not followed.  Anything unreadable -- a file whose size will
    not come, a directory that will not open -- is counted as a skip instead of
    being dropped: os.walk's default onerror discards a protected subtree
    silently, and the total that comes back still looks plausible.

    *skipped* collects the errors for a caller that is aggregating several
    walks; the third return value is this walk's own count either way.
    """
    notes: list[OSError] = []
    files = 0
    total = 0
    for parent, _dirs, names in os.walk(root, followlinks=False,
                                        onerror=lambda err: _note(notes, err)):
        for name in names:
            path = os.path.join(parent, name)
            try:
                total += os.path.getsize(path)
            except OSError as error:
                _note(notes, error)
                continue
            files += 1
    if skipped is not None:
        skipped.extend(notes)
    return files, total, len(notes)


def breakdown(root: str, skipped: list[OSError] | None = None
              ) -> list[tuple[str, int, int, int]]:
    """Return [(entry, files, bytes, skipped)] for each top-level entry.

    A top-level file counts as itself, one file.  An unreadable one keeps its
    row with zero files and one skip, rather than vanishing from a listing that
    is meant to be exhaustive.  The rows sum to walk_count(), skips included.
    """
    notes: list[OSError] = []
    rows: list[tuple[str, int, int, int]] = []
    try:
        entries = sorted(os.listdir(root))
    except OSError as error:
        _note(notes, error)
        entries = []
    for entry in entries:
        path = os.path.join(root, entry)
        if os.path.isdir(path):
            rows.append((entry,) + walk_count(path, notes))
        else:
            try:
                rows.append((entry, 1, os.path.getsize(path), 0))
            except OSError as error:
                _note(notes, error)
                rows.append((entry, 0, 0, 1))
    if skipped is not None:
        skipped.extend(notes)
    return rows


def self_check() -> None:
    """Build a known tree, count it, and demand the two answers agree.

    Two red cases, and they fail differently.  The first is arithmetic: a
    breakdown whose rows do not sum to the recursive total means one of the two
    walks is wrong, which is the mistake this module exists to have avoided --
    the plan's figures were a subfolder's, and nothing caught it.  The second is
    about silence: a root that cannot be read has to come back as a skip, not as
    an empty tree, because that is the shape a protected subfolder takes inside
    a larger walk -- and there the total still comes out large and believable.
    """
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "a", "deep"))
        os.makedirs(os.path.join(tmp, "b"))
        for path, size in [
            (os.path.join(tmp, "top.txt"), 3),
            (os.path.join(tmp, "a", "one.bin"), 10),
            (os.path.join(tmp, "a", "deep", "two.bin"), 100),
            (os.path.join(tmp, "b", "three.bin"), 1000),  # not-an-address: a test file size
        ]:
            with open(path, "wb") as handle:
                handle.write(b"\0" * size)

        files, total, missed = walk_count(tmp)
        assert (files, total, missed) == (4, 1113, 0), (files, total, missed)  # not-an-address: byte total of the four files above

        rows = breakdown(tmp)
        assert [r[0] for r in rows] == ["a", "b", "top.txt"], rows
        assert rows[0][1:] == (2, 110, 0), rows[0]
        assert sum(r[1] for r in rows) == files, rows
        assert sum(r[2] for r in rows) == total, rows
        assert sum(r[3] for r in rows) == missed, rows

        # Red case 1: a breakdown that skipped a top-level entry must not sum.
        partial = rows[:1]
        assert sum(r[1] for r in partial) != files
        assert sum(r[2] for r in partial) != total

        # Red case 2: an unreadable root is one skip, announced on stderr --
        # never zero files and a clean exit.  The stderr is captured so that
        # two --check runs print the same bytes; the temporary path is in it.
        missing = os.path.join(tmp, "gone")
        _ANNOUNCED.clear()
        noise = io.StringIO()
        with contextlib.redirect_stderr(noise):
            counted = walk_count(missing)
            notes: list[OSError] = []
            empty = breakdown(missing, notes)
        assert counted == (0, 0, 1), counted
        assert empty == [], empty
        assert len(notes) == 1, notes
        assert "skipped" in noise.getvalue(), noise.getvalue()
        # ... and the name is announced once even though two walks met it.
        assert noise.getvalue().count("skipped (") == 1, noise.getvalue()
        _ANNOUNCED.clear()

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

    for entry, files, total, missed in breakdown(root):
        mark = "  skipped %d" % missed if missed else ""
        print("%-28s %8d files %14d B%s" % (entry, files, total, mark))
    files, total, missed = walk_count(root)
    print("-" * 62)
    print("%-28s %8d files %14d B  (%.2f GiB)"
          % ("TOTAL", files, total, total / 1024 ** 3))  # not-an-address: GiB divisor
    print("skipped: %d" % missed)
    if missed:
        print("incomplete: %d %s could not be read, so the totals above are a "
              "lower bound and must not be quoted"
              % (missed, "entry" if missed == 1 else "entries"),
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
