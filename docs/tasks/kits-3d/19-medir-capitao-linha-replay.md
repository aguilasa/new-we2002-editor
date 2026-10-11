---
id: K3D-TASK-19
---

# K3D-TASK-19 — Medir o capitão de linha (Bokšić) de perto nos replays, manga curta no 9 e longa no 10, contra a aba

## Goal

Fica medido como o jogo desenha o capitão de linha de perto, nas duas mangas: o Bokšić (Croácia, nº 11) no slot 9 com a faixa 90 sobre a manga curta (3-6) e no slot 10 com a 93 e as mangas 95-98 — a faixa e os braços primitiva a primitiva (página, CLUT, zona, cor de vértice, modo), a pose parada com a projeção, o painel e o número nas costas, e o confronto do `match_scene` da família 2 com a pose do jogo e da aba (`--figure 0 --armband`, e `--long-sleeves` no 10) contra o quadro do jogo nas caixas da faixa e das mangas. Um jogador de linha sem braçadeira do slot 10 é o controle da manga longa sozinha. Investigação: a aba não muda; as diferenças listadas, curta e longa separadas, são a entrada do conserto.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py` (`--replay SLOT --focus K`, o confronto da família 2 com `--long-sleeves`)
  - `tools/kits/selftest.py`, `tools/kits/controls.py`
  - `docs/KITS-AJUSTES-3D.md` (G8: o medido nos dois slots, colado da HEAD)
- Out: `tools/kits/core/*`, `tools/kits/ui/*`; andar o replay com Right/Left

## Done criteria

- [ ] G8 tem a saída de `oracle.py --replay 9 --focus <k do Bokšić>`, `--replay 10 --focus <k>`, `--replay-confront` dos dois, e `--replay 10 --focus <k de um jogador sem braçadeira>` coladas da HEAD, com os itens 4 a 7 da K3D-TASK-17 respondidos para a faixa 90 e a manga curta (slot 9) e para a faixa 93 e as mangas 95-98 (slot 10), toda negativa com comando e saída, e a lista das diferenças que o confronto apontou, curta e longa separadas
- [ ] o focado nos dois slots amostra a página da Croácia e tem o 11 no painel das costas; a faixa é a 90 no 9 e a 93 no 10 (controle positivo do relato do usuário); divergência é resultado, escrita
- [ ] `--replay 9 --focus <k> --plant-replay` sai 1 com os `FAIL` da planta; os controles novos dão `RED` em `python3 tools/kits/controls.py --only <nome>`, e os casos novos do `selftest.py` dão `ok`
- [ ] sem uma das cópias mestras: `rite mark K3D-TASK-19 blocked --unblocked-by "test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav"` e o pedido ao usuário
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Recursos: emulador e save-states. Reusa a K3D-TASK-17 inteira (captura, costas por R1, painel,
confronto) com o foco k da tabela da K3D-TASK-18; o `match_scene` da família 2 já aceita
`armband` e `sleeves`, e a aba já desenha `--figure 0 --armband [--long-sleeves] --number 11`. A
tag da Croácia sai da tabela de times (`cli.py teams`) ou da página que o torso amostra.

O controle da manga longa sozinha (um jogador sem braçadeira do slot 10) separa o que é da manga
do que é da faixa nas diferenças listadas.

Da K3D-TASK-18 (G8, "Medido (K3D-TASK-18)"): o Bokšić é o foco **k = 3** do L2 nos dois slots, e o
jogador de linha sem braçadeira para o controle da manga longa pode ser o k = 2 (Balaban, nº 20). Com
L2 a câmera segue **de costas** a ~4700 de profundidade, e não no zoom máximo: as costas e o painel
saem sem girar, e é a frente que pede o giro. O focado atrás de um jogador é a figura **no eixo**
(`field_focus`), não a de menor z (`replay_focus`), que no slot 9 erra quando um vizinho passa entre
ele e a câmera; o `--replay --focus K` tem de usar a regra do eixo, com a margem `REPLAY_FOCUS_MARGIN`.
Cada foco recarrega o state e precisa de `REPLAY_FIELD_SETTLE` quadros depois do último toque.

## Log de Execução
