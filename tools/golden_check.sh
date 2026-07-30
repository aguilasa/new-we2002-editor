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

IMAGE="${1:-${WE2002_GOLDEN_IMAGE:-}}"
TOOL="${2:-${WE2002_GOLDEN_TOOL:-$REPO/build/tests/we2002_golden_tool}}"

if [ -z "$IMAGE" ]; then
    echo "golden_check: WE2002_GOLDEN_IMAGE nao definida -- pulando" >&2
    exit 77
fi
[ -f "$IMAGE" ] || { echo "golden_check: nao existe: $IMAGE" >&2; exit 1; }
[ -x "$TOOL" ] || { echo "golden_check: falta $TOOL (compile primeiro)" >&2; exit 1; }
[ -f "$REPO/Debug/ed.exe" ] || {
    echo "golden_check: Debug/ed.exe ausente -- sem oraculo, sem teste" >&2
    exit 1
}

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

echo "golden_check: rodando o port"
"$TOOL" roundtrip "$WORK/port.bin"

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
