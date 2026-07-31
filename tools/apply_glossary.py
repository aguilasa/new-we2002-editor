#!/usr/bin/env python3
"""Apply tools/glossary.py to the hand-written sources.

The generated files (Database.cpp, Tables.cpp, Offsets.hpp, Tables.hpp) get
the same treatment from their own generators, which is why the map lives in
one place. This covers everything else.

Idempotent: the new names do not match the old patterns, so a second run is a
no-op. Run it after touching the glossary, then rebuild and re-run the golden
test -- a rename that changes behaviour is exactly what that test is for.

    python3 tools/apply_glossary.py            # rewrite the default file list
    python3 tools/apply_glossary.py --check    # report leftovers, change nothing
    python3 tools/apply_glossary.py path...    # rewrite specific files
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import glossary  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Everything under src/, tests/ and tools/ that is not produced by a generator.
DEFAULT_FILES = [
    "src/core/CdImage.cpp",
    "src/core/Player.cpp",
    "src/core/Sofifa.cpp",
    "src/core/Team.cpp",
    "src/core/TextCodec.cpp",
    "src/core/include/we2002/CdImage.hpp",
    "src/core/include/we2002/Database.hpp",
    "src/core/include/we2002/Player.hpp",
    "src/core/include/we2002/Sofifa.hpp",
    "src/core/include/we2002/Team.hpp",
    "src/core/include/we2002/TextCodec.hpp",
    "src/core/include/we2002/Types.hpp",
    "tests/golden_tool.cpp",
    "tests/test_main.cpp",
]

# The Qt application (phase 5.5). Its widget names went through
# glossary.UI_CONTROLS, so it is checked against that map as well as the core
# one -- see APP_FILES below.
APP_FILES = sorted(
    str(p.relative_to(ROOT))
    for p in (ROOT / "src" / "app").glob("*.?pp")
)

# Everything the port compiles, generated or not. --check scans all of it.
CHECKED_FILES = DEFAULT_FILES + APP_FILES + [
    "src/core/Database.cpp",
    "src/core/Tables.cpp",
    "src/core/include/we2002/Offsets.hpp",
    "src/core/include/we2002/Tables.hpp",
]

# The .ui forms and their manifest are generated, so a stale widget name there
# means tools/rc2ui.py was not re-run. Checked as text: the names appear as
# XML attributes and JSON values, neither of which the code scanner would see.
GENERATED_UI = ["src/app/ui/controls.json"] + sorted(
    str(p.relative_to(ROOT)) for p in (ROOT / "src" / "app" / "ui").glob("*.ui")
)


def check() -> int:
    """Report Italian identifiers still present in code.

    Comments, string literals and backticked spans are exempt on purpose.
    Offsets.hpp carries the legacy spelling of every renamed offset in a
    trailing `// was OFS_...` so that grepping a name across this tree and
    legacy/mfc/ still finds both ends; Player.hpp names the two backwards
    legacy methods in the note explaining the rename; Types.hpp quotes the
    legacy array declaration; and the test suite prints Portuguese.
    """
    bad = 0
    for rel in CHECKED_FILES:
        path = ROOT / rel
        if not path.exists():
            continue
        # Widget names only apply to the application; sweeping the core for
        # them would be noise, and the core map must not reach the .ui.
        patterns = [glossary.LEFTOVER]
        if rel in APP_FILES:
            patterns.append(glossary.UI_LEFTOVER)
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            code = glossary.PROTECTED.sub("", line).split("//", 1)[0]
            for pattern in patterns:
                for m in pattern.finditer(code):
                    print(f"{rel}:{n}: {m.group(0)}")
                    bad += 1

    # Whole-file scan, comments included: these have no code to separate out.
    for rel in GENERATED_UI:
        path = ROOT / rel
        if not path.exists():
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            # `id` records the original ed.rc symbol on purpose.
            if '"id":' in line:
                continue
            for m in glossary.UI_LEFTOVER.finditer(line):
                print(f"{rel}:{n}: {m.group(0)} (rode tools/rc2ui.py)")
                bad += 1

    if bad:
        print(f"\n{bad} identificador(es) em italiano restante(s)", file=sys.stderr)
        return 1
    print(f"{len(CHECKED_FILES) + len(GENERATED_UI)} arquivos limpos")
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--check":
        return check()

    targets = argv or DEFAULT_FILES
    for rel in targets:
        path = ROOT / rel
        if not path.exists():
            print(f"aviso: nao existe: {rel}", file=sys.stderr)
            continue
        before = path.read_text(encoding="utf-8")
        after, ids, comments = glossary.rename(before)
        if after == before:
            continue
        path.write_text(after, encoding="utf-8")
        print(f"{rel}: {ids} identificador(es), {comments} comentario(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
