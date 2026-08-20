#!/usr/bin/env bash
# End-to-end phase 3 golden test: does this port write the same bytes the
# original ed.exe writes?
#
#   tools/golden_check.sh /path/to/image.bin [/path/to/golden_tool]
#
# Two copies of the image are made in a temp directory; one is put through
# ed.exe under Wine, the other through we2002_golden_tool. They must come out
# identical apart from one documented 16-byte run -- see KNOWN_DIFF below.
#
# The source image is never touched. Two ~474 MB copies are made and deleted.
#
# ctest runs this only when WE2002_GOLDEN_IMAGE points at an image; otherwise
# it exits 77, which CMake is told to read as "skipped".

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Pinned here and not just in golden_run.sh / golden_gui.sh, which set the same
# thing: the stray-window check below inspects a display, and ctest passes
# whatever DISPLAY the developer's shell had -- :1, the real session, whose
# ordinary windows are big enough to trip the check. Never :1 (see CLAUDE.md).
export DISPLAY="${GOLDEN_DISPLAY:-:98}"

IMAGE="${1:-${WE2002_GOLDEN_IMAGE:-}}"
TOOL="${2:-${WE2002_GOLDEN_TOOL:-$REPO/build/tests/we2002_golden_tool}}"

# WE2002_GOLDEN_MODE=gui puts the Qt window on the port side instead of the
# headless tool, so the same comparison also covers the widget layer added in
# phase 5. It needs a built src/app and an X display; "core" is the default.
MODE="${WE2002_GOLDEN_MODE:-core}"

if [ -z "$IMAGE" ]; then
    echo "golden_check: WE2002_GOLDEN_IMAGE nao definida -- pulando" >&2
    exit 77
fi
[ -f "$IMAGE" ] || { echo "golden_check: nao existe: $IMAGE" >&2; exit 1; }
if [ "$MODE" = gui ]; then
    TOOL="${WE2002_GOLDEN_APP:-$REPO/build/src/app/newWe2002}"
    [ -x "$TOOL" ] || {
        echo "golden_check: falta $TOOL -- o app Qt nao foi compilado" >&2
        exit 77
    }
else
    [ -x "$TOOL" ] || { echo "golden_check: falta $TOOL (compile primeiro)" >&2; exit 1; }
fi
[ -f "$REPO/Debug/ed.exe" ] || {
    echo "golden_check: Debug/ed.exe ausente -- sem oraculo, sem teste" >&2
    exit 1
}

# Both halves find the main dialog by its size, because it has no title. So an
# editor already open on this display -- a leftover from poking at the GUI by
# hand -- gets driven instead of the one under test, and the run fails with
# byte differences that look like a port bug. Refuse to start instead.
# Anything this big is an editor: the dialog is 1077x547, and Wine clips it to
# the width of the screen, so the test is a floor and not an exact size.
if command -v xwininfo >/dev/null 2>&1; then
    while read -r line; do
        [[ "$line" =~ ([0-9]+)x([0-9]+)\+ ]] || continue
        if [ "${BASH_REMATCH[1]}" -ge 900 ] && [ "${BASH_REMATCH[2]}" -ge 450 ]; then
            echo "golden_check: ja existe uma janela de editor em $DISPLAY:" >&2
            echo "  $line" >&2
            echo "  Feche-a antes (o ed.exe pede 'wineserver -k'). Os dois lados" >&2
            echo "  acham o dialogo pelo tamanho e dirigiriam a janela errada." >&2
            exit 1
        fi
    done < <(xwininfo -root -children 2>/dev/null | grep -F '": (')
fi

# The one place ed.exe and the port are allowed to disagree.
#
# squadra squad_nazall[63] is indexed to 64 in three loops of the original
# (edDlg.cpp:1928, :5821, :7667). The 64th element does not exist, so the
# original reads and writes 16 bytes of whatever follows in memory -- which is
# squad_ml[0], hence the Shift-JIS club-name bytes that land here. It is
# deterministic on Windows only by accident of the linker's layout.
#
# The port gives the array the 64 slots the disc actually has, so it reads
# those 16 bytes off the image and writes them back unchanged. That is a
# deliberate deviation: reproducing the overrun would mean reproducing
# undefined behaviour whose value depends on the compiler.
KNOWN_START=405724
KNOWN_END=405739

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "golden_check: copiando $IMAGE"
cp "$IMAGE" "$WORK/oracle.bin"
cp "$IMAGE" "$WORK/port.bin"

echo "golden_check: rodando o oraculo (ed.exe sob Wine)"
"$REPO/tools/golden_run.sh" "$WORK/oracle.bin"

if [ "$MODE" = gui ]; then
    echo "golden_check: rodando o port (janela Qt)"
    "$REPO/tools/golden_gui.sh" "$WORK/port.bin" "$TOOL"
else
    echo "golden_check: rodando o port"
    "$TOOL" roundtrip "$WORK/port.bin"
fi

echo "golden_check: comparando"
python3 "$REPO/tools/golden_compare.py" --json "$WORK/oracle.bin" "$WORK/port.bin" \
    > "$WORK/diff.json" || true

python3 - "$WORK/diff.json" "$KNOWN_START" "$KNOWN_END" <<'PY'
import json, sys
report = json.load(open(sys.argv[1]))
known_start, known_end = int(sys.argv[2]), int(sys.argv[3])

unexpected = [
    r for r in report["runs"]
    if not (r["start"] == known_start and r["end"] == known_end)
]

if unexpected:
    print(f"FALHOU: {len(unexpected)} divergencia(s) nao esperada(s):")
    for r in unexpected:
        print(f"  {r['start']}..{r['end']}  {r['bytes']} byte(s)  "
              f"{r['kind']}  {r['region']}+{r['region_delta']}")
    sys.exit(1)

if not report["runs"]:
    print("OK: byte-identico ao oraculo (nem a divergencia conhecida apareceu)")
else:
    print("OK: identico ao oraculo, exceto o slot 64 conhecido "
          f"({known_start}..{known_end})")
PY
