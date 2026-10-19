---
id: CORR-KRP-007
---

# CORR-KRP-007 — Comentário do selftest do show diz 21x21; o quadrado pinta 20x20

Origin: [KRP-TASK-05](/docs/tasks/concluidos/kits-replay/05-show-png-e-confront-puro-sobre-a-captura.md)

## Problem

O comentário acima da asserção nova do `show` em `tools/kits/selftest.py` diz que o quadrado "covers
the middle 21x21 of a 41x41 box". Medido, ele pinta 400 pixels, de (10,10) a (29,29): 20×20. Essa
contagem cai exatamente no limite inferior da asserção, 400.

## Evidência

```text
$ grep -n '21x21' tools/kits/selftest.py
1689:    # square of side 20 at z 1000 seen with H 1000 covers the middle 21x21 of
$ S=$(mktemp -d); git archive HEAD tools | tar -x -C $S
$ cd $S && python3 -I - <<'EOF'
import sys; sys.path.insert(0,"tools/kits")
from types import SimpleNamespace as n
from core import replay
sq=n(vertices=[n(x=x,y=y,z=0) for x,y in ((-10,-10),(10,-10),(-10,10),(10,10))],primitives=[n(indices=(0,1,2,3),texcoords=((0,0),(8,0),(0,8),(8,8)))])
f=replay.Figure([{"section":5,"projection":{"H":1000,"OFX":0,"OFY":0},"matrix":((4096,0,0,0,4096,0,0,0,4096),(0,0,1000))}]); f.samples=[]
w,h,p=replay.pose_picture(f,{"sections":{(replay.layout.MODEL,5):sq}},None,(-20,-20,20,20))
pt=[(x,y) for y in range(h) for x in range(w) if p[(y*w+x)*4+3]]
print(len(pt), min(pt), max(pt))
EOF
400 (10, 10) (29, 29)
```

## Root cause

O comentário foi escrito a partir da geometria esperada (lado 20 dá 21 pontos de amostra), não da
saída medida do raster, que preenche 20 pixels por lado.

## Fix

Em `tools/kits/selftest.py`, escrever no comentário o medido (20×20, 400 px) e centrar o limite da
asserção nesse valor, em vez de deixá-lo na borda. Pode entrar na mesma reescrita da
[CORR-KRP-006](/docs/tasks/concluidos/kits-replay/CORR-KRP-006.md).

## Arquivos a criar ou modificar

- `tools/kits/selftest.py`

## Verificação

```sh
grep -n '21x21' tools/kits/selftest.py
```

Não pode imprimir nada. A sonda acima continua dando 400, agora dentro dos limites novos.

## Log de Execução

- **Stale** (2026-10-13) at `3d92791b`: grep -n '21x21' tools/kits/selftest.py now prints nothing (rc=1): CORR-KRP-006 (64ff1d2d) replaced the symmetric-square fixture and its comment
