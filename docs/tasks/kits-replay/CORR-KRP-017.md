---
id: CORR-KRP-017
---

# CORR-KRP-017 — Log da KRP-TASK-10 explica a frente de Marcos e as colunas de barba com o que a medição desmente

Origin: [KRP-TASK-10](/docs/tasks/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md)

## Problem

Duas explicações do Log da KRP-TASK-10 são falsas quando medidas. Os números do Log se reproduzem;
o erro está só na explicação.

- O Log explica a interseção de frente de Marcos, que fica parada (0,501 → 0,500), dizendo que "a
  cabeça dele já era a 34 com a mesma CLUT do jogo". Não era: a figura de referência desenha a seção
  24 com as CLUTs (16,480)/(144,480). Com `--player` a figura desenha a seção 34 com (32,480)/(160,480),
  que é o que o jogo usa.
- O mesmo Log diz que as colunas de barba (144,480) e (160,480) são "não amostrada por uma vista de
  frente". A captura 10-2 amostra (160,480).

## Evidência

```text
$ cd tools/kits && WE2002_LOOKS_IMAGE=$PWD/../../roms/japanese-shift-jis.bin python3 - <<'PY'
import os
from core import figure as F, api
geo=F.read_geometry(os.environ['WE2002_LOOKS_IMAGE'])
kit=api.open_source(os.environ['WE2002_LOOKS_IMAGE']).kit("41")
for fig in (0,1):
    for pl in (None,"A-I1-B-A-B"):
        s=api.figure(kit,1,fig,frame=api.FIGURE_POSE,geometry=geo,player=pl)
        c={}
        for p in s.parts:
            if p.file==F.layout.MODEL: k=(p.section,F.skin.grid(p.clut)); c[k]=c.get(k,0)+1
        print(fig, pl, c)
PY
0 None {(24, (480, 1)): 16, (24, (480, 9)): 2}
0 A-I1-B-A-B {(34, (480, 2)): 20, (34, (480, 10)): 3}
```

A figura 1, que a aba desenha para 9-R1, dá o mesmo.

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-10-2.json --section 46 --json
"section": {"cluts": [[32, 480], [160, 480]], ... "n": 18, ...}
$ grep -n "já era a 34" docs/tasks/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md
(imprime uma linha)
```

## Root cause

(Hipótese.) As explicações foram escritas a partir do esperado, não de uma corrida da ferramenta.

## Fix

Reescrever as duas frases no Log da KRP-TASK-10:

- a cabeça de referência é a 24, nas colunas 1/9, e a aba desenha a 34 com as CLUTs do jogo, então a
  interseção de frente parada ainda precisa de explicação;
- (144,480) não aparece na captura 9-3, e (160,480) aparece na 10-2.

Colar os comandos acima como evidência.

## Arquivos a criar ou modificar

- `docs/tasks/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md`

## Verificação

```sh
grep -n "já era a 34" docs/tasks/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md
```

Hoje imprime uma linha. Depois do conserto não pode imprimir nada.

## Log de Execução

- 2026-10-16: as duas frases do Log da KRP-TASK-10 foram reescritas. A frente parada do Marcos fica registrada como **sem explicação** (a cabeça de referência é a 24, nas colunas 1/9; com `--player` a aba desenha a 34 com as CLUTs do jogo), e a coluna da barba passou a dizer o que as capturas amostram: a (144,480) não aparece na 9-3 e a (160,480) aparece na 10-2. As medições foram coladas numa nota datada no fim do Log da task, com o script inteiro em heredoc e, do `replay.py figure` sem `--json`, só a linha da seção 46. A causa raiz continua hipótese: nada aqui mede como o texto anterior foi escrito.
