---
id: CORR-KRP-016
---

# CORR-KRP-016 — Filtro de caixa da peça em head_samples sem controle; as CLUTs vizinhas da §3.1 não se reproduzem por ferramenta

Origin: [KRP-TASK-09](/docs/tasks/concluidos/kits-replay/09-medir-a-regra-da-cabeca-estilo-pele-cabelo-e.md)

## Problem

A §3.1 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#3.1) diz que ler a cabeça dentro da caixa
da figura inteira pegaria a cabeça de um vizinho: "(16,482) no 4 da Croácia e (32,480) no 10 do
Brasil". O Log da task e a docstring de `head_samples` repetem isso.

Esse número só se reproduz remendando `head_samples` à mão. Nenhuma opção versionada o imprime, e o
`controls.py` não tem defeito plantado para o filtro de caixa da peça. Ficam de fora duas regras: a
do projeto ("sonda que produziu um número vira opção de uma ferramenta versionada") e a da §9 do
plano ("um controle por leitor ou asserção nova").

A afirmação é verdadeira, e o gate `kits_replay` fica vermelho sem o filtro, mas nenhuma corrida
registrada mostra isso.

## Evidência

```text
$ grep -n 'head_samples\|piece_box' tools/kits/controls.py
(sem saída)
```

Medição ad hoc, remontável a partir da HEAD:

1. `T=$(mktemp -d); git archive HEAD tools src/core/include | tar -x -C $T`.
2. Em `$T/tools/kits/core/replay.py`, dentro de `head_samples`, trocar a linha
   `            if all(box[0] <= x <= box[2] and box[1] <= y <= box[3] for x, y in one["xy"])]`
   por `            ]`.
3. Rodar:

```text
$ cd $T && WE2002_LOOKS_IMAGE=<repo>/roms/japanese-shift-jis.bin python3 tools/kits/replay.py head <repo>/work/kits-oracle/replay-field-10-capture.json --player all
  focus 8  page 640  team 22   number 4    section 34  I, 13 prim(s), CLUT (16,482) (32,480): skin A/C hair A/B beard -
  focus 15 page 576  team 41   number 10   section 34  I, 20 prim(s), CLUT (16,482) (32,480): skin A/C hair A/B beard -
  20 of 22 distinct player(s) match their disc record
$ cd $T && WE2002_LOOKS_IMAGE=... python3 tools/kits/replay.py check <repo>/work/kits-oracle
  FAIL  replay-field-10-capture.json: head of focus 8, team 22 number 4: skin A/C, not A
  kits_replay: 4 failure(s)
```

## Root cause

(Hipótese.) A restrição de caixa foi achada com uma sonda descartável enquanto `head_samples` era
escrita, e os plants só entraram para a coluna de cabelo, o gêmeo e o viés de elenco.

## Fix

- Em `tools/kits/controls.py`, acrescentar um `Control` (por exemplo `replay-head-piece-box`, alvo
  `kits/core/replay.py :: head_samples`) cujo plant tire a condição de caixa da peça, esperando o
  vermelho no slot 10, foco 8.
- Na §3.1 do `docs/PLAN-KITS-REPLAY.md`, apontar a frase "(16,482) … (32,480)" para a saída desse
  controle, em vez de uma corrida não registrada.

## Arquivos a criar ou modificar

- `tools/kits/controls.py`
- `docs/PLAN-KITS-REPLAY.md`

## Verificação

```sh
python3 tools/kits/controls.py | grep replay-head-piece-box
```

Hoje não imprime nada. Depois do conserto tem de imprimir `RED    replay-head-piece-box`, e a última
linha tem de dizer `controls: 74 of 74 red`.

## Log de Execução

**2026-10-15.** A medição ad hoc da Evidência, remontada como um script só, sobre a HEAD
`7a085569`, com caminhos absolutos. As duas primeiras linhas da saída são o `grep -c` da condição
antes (1) e depois (0) da remoção; da corrida do `head` ficam os dois focos que mudam e o total.

```sh
#!/bin/bash
# CORR-KRP-016: head_samples without the piece-box condition, on the HEAD tree.
R=/home/ingmar/desenvolvimento/github/new-we2002-editor
S=/tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad
T=$(mktemp -d -p "$S")
git -C "$R" archive HEAD tools src/core/include | tar -x -C "$T"
F="$T/tools/kits/core/replay.py"
OLD='            if all(box[0] <= x <= box[2] and box[1] <= y <= box[3] for x, y in one["xy"])]'
grep -cF "$OLD" "$F"
python3 - "$F" "$OLD" <<'PY'
import sys
p, old = sys.argv[1], sys.argv[2]
s = open(p).read()
assert s.count(old + "\n") == 1
open(p, "w").write(s.replace(old + "\n", "            ]\n"))
PY
grep -cF "$OLD" "$F"
cd "$T"
export WE2002_LOOKS_IMAGE=$R/roms/japanese-shift-jis.bin
echo "== head --player all"
python3 tools/kits/replay.py head $R/work/kits-oracle/replay-field-10-capture.json --player all; echo "exit $?"
echo "== check"
python3 tools/kits/replay.py check $R/work/kits-oracle; echo "exit $?"
```

```text
1
0
== head --player all
  focus 8  page 640  team 22   number 4    section 34  I, 13 prim(s), CLUT (16,482) (32,480): skin A/C hair A/B beard -
           record 510 (slot 4) A-I2-B-A-B: section 34 skin A hair B beard B -- skin A/C, not A; hair colour A/B, not B
  focus 15 page 576  team 41   number 10   section 34  I, 20 prim(s), CLUT (16,482) (32,480): skin A/C hair A/B beard -
           record 951 (slot 8) C-I1-A-A-A: section 34 skin C hair A beard A -- skin A/C, not C; hair colour A/B, not A
20 of 22 distinct player(s) match their disc record
exit 1
== check
  ok    HEAD_EXPECT: the disc records the 22 players' looks it says
  ok    replay-9.json: root 13 head 34 armband 92 for 15, still 0, panel [576, 100, 104] number 1; every head reads its player's HEAD_EXPECT
  ok    replay-9-3.json: root 2 head 46 armband 90 for 4, still 0, panel [640, 60, 104] number 11; every head reads its player's HEAD_EXPECT
  ok    replay-10.json: root 13 head 34 armband 92 for 15, still 0, panel [576, 100, 104] number 1; every head reads its player's HEAD_EXPECT
  ok    replay-10-2.json: root 2 head 46 armband None for None, still 0, panel [640, 80, 104] number 20; every head reads its player's HEAD_EXPECT
  ok    replay-10-3.json: root 2 head 46 armband 93 for 97, still 0, panel [640, 60, 104] number 11; every head reads its player's HEAD_EXPECT
  ok    replay-field-9-capture.json: 25 foci, 20 outfield, 2 goalkeeper(s) followed; every head reads its player's HEAD_EXPECT
  FAIL  replay-field-10-capture.json: head of focus 8, team 22 number 4: skin A/C, not A
  FAIL  replay-field-10-capture.json: head of focus 8, team 22 number 4: hair colour A/B, not B
  FAIL  replay-field-10-capture.json: head of focus 15, team 41 number 10: skin A/C, not C
  FAIL  replay-field-10-capture.json: head of focus 15, team 41 number 10: hair colour A/B, not A
kits_replay: 4 failure(s)
exit 1
```

Sem a condição, o 4 da Croácia (foco 8) e o 10 do Brasil (foco 15) leem as duas CLUTs, (16,482) e
(32,480), e o `kits_replay` cai em 4 falhas. Com a condição, na mesma HEAD, os dois leem uma CLUT
só, e o total é `22 of 22`.

O conserto acrescenta o controle `replay-head-piece-box` ao `tools/kits/controls.py`. O sandbox dos
controles roda o selftest sem `WE2002_LOOKS_IMAGE` e sem as capturas de `work/kits-oracle`, então o
vermelho tem de vir de uma asserção sintética. Por isso o `tools/kits/selftest.py` ganhou uma, em
`_replay_head_checks`: uma figura de frente, cabeça 34 e raiz 2, e dois quads com os texels da 34.
O quad da própria cabeça tem CLUT (32,480). O do vizinho tem CLUT (16,482) e cai dentro do box da
figura e fora do box da peça. A asserção exige que `head_samples` devolva só (32,480).

O controle prova o filtro pelo caso sintético. As CLUTs reais da §3.1 vêm da corrida acima, e a
§3.1 do plano agora remete a esta CORR e ao controle.
- **Closed** — commit `c5b4a783` (2026-10-15): test(kits): plant the head piece-box filter of head_samples as a control
  - Files (`git show --name-status c5b4a783`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/CORR-KRP-016.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/selftest.py`
