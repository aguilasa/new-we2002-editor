---
id: CORR-KRP-016
---

# CORR-KRP-016 — Filtro de caixa da peça em head_samples sem controle; as CLUTs vizinhas da §3.1 não se reproduzem por ferramenta

Origin: [KRP-TASK-09](/docs/tasks/kits-replay/09-medir-a-regra-da-cabeca-estilo-pele-cabelo-e.md)

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
