---
id: CORR-KRP-006
---

# CORR-KRP-006 — Selftest do show não pega desenho espelhado nem sem rotação

Origin: [KRP-TASK-05](/docs/tasks/kits-replay/05-show-png-e-confront-puro-sobre-a-captura.md)

## Problem

A asserção nova do selftest ("show draws the figure in its captured pose, on the frame buffer's
pixels") usa um quadrado 20×20 centrado e simétrico, com rotação identidade. Dois defeitos plantados
em `pose_picture` passam por ela:

- tirar a negação de x/y, o que espelha o desenho;
- trocar a rotação capturada pela identidade.

Numa captura real os dois mudam muito o desenho: `drawn` vai de 2349 para 136 no espelhado e para
2636 sem rotação. Então o gate prova só que "algo é desenhado no centro da caixa", não que é
desenhado "na pose capturada".

A armadilha K2 (§9) pede um plant que derrube a asserção com dado real. O único plant existente
(matriz identidade mais translação zero, o que dá z=0 e nada projeta) só a derruba pela fixture
sintética.

## Evidência

```text
$ S=$(mktemp -d); for v in head mirror norot; do mkdir -p $S/t-$v; git archive HEAD tools | tar -x -C $S/t-$v; done
$ sed -i 's/points.append((-at\[0\], -at\[1\], -cz))/points.append((at[0], at[1], -cz))/' $S/t-mirror/tools/kits/core/replay.py
$ sed -i 's/        rotation, translation = piece\["matrix"\]/        rotation, translation = (4096, 0, 0, 0, 4096, 0, 0, 0, 4096), piece["matrix"][1]/' $S/t-norot/tools/kits/core/replay.py
$ cat > $S/probe.py <<'EOF'
import sys
sys.path.insert(0, sys.argv[1] + "/tools/kits")
from types import SimpleNamespace as _ns2
from core import replay
square = _ns2(vertices=[_ns2(x=x, y=y, z=0) for x, y in ((-10, -10), (10, -10), (-10, 10), (10, 10))],
              primitives=[_ns2(indices=(0, 1, 2, 3), texcoords=((0, 0), (8, 0), (0, 8), (8, 8)))])
posed = replay.Figure([{"section": 5, "projection": {"H": 1000, "OFX": 0, "OFY": 0},
                        "matrix": ((4096, 0, 0, 0, 4096, 0, 0, 0, 4096), (0, 0, 1000))}])
posed.samples = []
pw, ph, picture = replay.pose_picture(posed, {"sections": {(replay.layout.MODEL, 5): square}}, None, (-20, -20, 20, 20))
painted = [(x, y) for y in range(ph) for x in range(pw) if picture[(y * pw + x) * 4 + 3]]
ok = (pw, ph) == (41, 41) and (20, 20) in painted and (1, 1) not in painted and 400 <= len(painted) <= 484
print("PASS" if ok else "FAIL", "%dx%d, %d px painted" % (pw, ph, len(painted)))
EOF
$ for v in head mirror norot; do echo "== $v"; (cd $S && python3 -I probe.py $S/t-$v); done
== head
PASS 41x41, 400 px painted
== mirror
PASS 41x41, 400 px painted
== norot
PASS 41x41, 400 px painted
$ for v in head mirror norot; do WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 $S/t-$v/tools/kits/replay.py show work/kits-oracle/replay-9-3.json --png $S/$v.png --json | grep '"drawn"'; done
 "drawn": 2349,
 "drawn": 136,
 "drawn": 2636,
```

## Root cause

(Inferido da fixture.) Ela é simétrica em x e y e tem rotação identidade, então a asserção não
distingue um espelhamento ou uma rotação perdida do desenho certo. O correspondente dela com dado real
é o PNG, sobre o qual nada afirma.

## Fix

- Em `tools/kits/selftest.py` (`_replay_reader_checks`), usar uma fixture assimétrica: quadrado fora
  do centro (translação x≠0) e rotação que não seja identidade (por exemplo 90° em z). Afirmar pixels
  pintados num quadrante e nenhum no quadrante espelhado.
- Melhor ainda: acrescentar ao `replay.py check`/`kits_replay` uma asserção com dado real, por
  exemplo que a máscara desenhada pelo `show` se sobreponha aos pixels da figura do jogo dentro do
  `piece_box` acima de uma constante por (slot, foco), como a K1 exige.
- Acrescentar a `tools/kits/controls.py` os plants de espelho e de rotação identidade, e mostrá-los
  `RED` no Log.

## Arquivos a criar ou modificar

- `tools/kits/selftest.py`
- `tools/kits/controls.py`
- `tools/kits/replay.py` (só no caminho com dado real)

## Verificação

Com a asserção corrigida, a sonda acima tem de imprimir `FAIL` para `mirror` e `norot`. E
`python3 tools/kits/controls.py --only <ids dos controles novos>` tem de mostrá-los `RED`.

## Log de Execução
