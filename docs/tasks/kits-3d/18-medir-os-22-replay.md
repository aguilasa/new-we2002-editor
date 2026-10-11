---
id: K3D-TASK-18
---

# K3D-TASK-18 — Medir os 22 em campo por L2/R2 nos replays: time, cabeça, manga, braçadeira e painel por jogador

## Goal

Fica medida, nos dois replays, uma tabela dos 22 em campo andada por L2: para cada foco k, o time (página 576 ou 640), a família de seções, a cabeça, a manga (3-6 ou 95-98), a braçadeira (90, 93, 92, 91, 94 ou nenhuma), o painel que o torso amostra e o número. Dela saem o foco do Bokšić (nº 11, 90 no slot 9 e 93 no 10) e o do Marcos, a manga por slot confirmada nos 20 de linha, se a cabeça é por jogador ou por figura, o painel ↔ número dos 22 contra a grade do §4.7, e a ordem do L2/R2. Investigação: a aba não muda.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py` (`--replay-field SLOT`, `--plant-replay-field`; a tabela em `work/kits-oracle/replay-field-<slot>.json`)
  - `tools/kits/selftest.py`, `tools/kits/controls.py`
  - `docs/KITS-AJUSTES-3D.md` (G8: as duas tabelas, coladas da HEAD)
- Out: `tools/kits/core/*`, `tools/kits/ui/*`; o confronto de perto do Bokšić (K3D-TASK-19); andar o replay com Right/Left

## Done criteria

- [x] G8 tem a saída de `oracle.py --replay-field 9` e `--replay-field 10` coladas da HEAD: a tabela dos focos até a volta à bola, com time, família, cabeça, manga, braçadeira, painel e número por foco, e as conclusões escritas uma a uma — o foco do Bokšić e do Marcos nos dois slots, a manga por slot (curta no 9, longa no 10, goleiro sempre longa; divergência por jogador escrita como resultado), cabeça por jogador ou por figura, painel ↔ número contra a grade do §4.7, a ordem do L2/R2 —, toda negativa com comando e saída
- [x] o Bokšić desenha a 90 no slot 9 e a 93 no 10, e o Marcos a seção que a K3D-TASK-17 mediu (controles positivos do relato do usuário); divergência é resultado, escrita
- [x] cada foco recarrega o state e toca L2 k vezes com o `press` exigindo a tela mudar; um toque que não muda a tela é impresso como a volta à bola ou um expulso, e a corrida fica abaixo do timeout da K3D-TASK-17
- [x] `--replay-field 9 --plant-replay-field` sai 1 (foco pela figura seguinte do eixo da câmera — era "pela segunda menor z", e menor z não é o seguido atrás de um jogador; painéis uma linha acima), e cada metade sozinha (`focus`, `panel`) sai 1 com `FAIL` próprio; os controles novos dão `RED` em `python3 tools/kits/controls.py --only <nome>`, e os casos novos do `selftest.py` dão `ok`
- [x] sem uma das cópias mestras (não se aplicou: as duas existem, sha256 no Log): `rite mark K3D-TASK-18 blocked --unblocked-by "test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav"` e o pedido ao usuário
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Recursos: emulador e save-states. Reusa a K3D-TASK-17: a captura do focado (`--replay`), o juiz
de família, cabeça e painel por UV, e a guarda do timeout; o que é novo é o laço por foco e a
tabela. O `press` de L2 pode precisar de um `least` próprio, como `EDIT_ROW_MOVED` precisou para o
`Down` da tela EDIT PL. NUM. De frente basta: o painel pelo UV do torso não depende das costas.

Os 22 podem ser menos, se houver expulso; a volta à bola é o fim do laço. O time de cada foco sai
da página que o torso amostra (576 ou 640), e os números do Brasil e da Croácia se conferem contra
o disco se o juiz precisar de mais do que o painel.

Da K3D-TASK-17: a planta que segue a segunda figura não chega a ler painel nenhum, então "painéis
uma linha acima" não muda a saída dela — a `--plant-replay` largou essa parte. Se a planta desta task
juntar as duas coisas, confira que cada uma derruba um `FAIL` próprio. E o leitor do giro precisou
de mais paradas quando a câmera vê o campo (`REPLAY_YAW_STOPS`): com L2 trocando o foco, o mesmo vale.

Da [CORR-K3D-024](/docs/tasks/kits-3d/CORR-K3D-024.md): o `replay_focus` escolhe a figura de menor z
sem margem nenhuma até a segunda, e a planta da K3D-TASK-17 nunca teve uma figura errada presente para
pegar. Aqui há várias figuras por quadro: meça a distância em z entre a mais próxima e a segunda em cada
foco, ponha a margem no juiz (falha quando as duas estão mais perto que ela), com caso no `selftest.py`
e entrada no `controls.py`, e veja a conferência de raiz ficar vermelha com uma figura real.
E o "De frente basta" acima não vale: de frente nenhuma primitiva do goleiro amostra um painel, e de
costas quatro, os texels do próprio torso 13 no disco — o painel do goleiro é fixo na seção. A medida
são as linhas `front:` e `back:` de `oracle.py --replay 9` (e `10`), coladas no G8
([CORR-K3D-025](/docs/tasks/kits-3d/CORR-K3D-025.md)). Para os 20 de linha, o painel pede as costas (R1) em cada foco, ou um argumento de
que o UV é fixo também no torso 2.

## Log de Execução

### 2026-10-10 — os 22 por L2 nos dois replays

As cópias mestras existem, com os sha256 da K3D-TASK-17 (`sha256sum work/kits-states/SLPM-87056_9.sav
work/kits-states/SLPM-87056_10.sav`: `54c79792…d6d6` e `bdf47644…3b6e`).

**Medido**, com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY=`,
e colado em [G8](/docs/KITS-AJUSTES-3D.md#g8--replays-nos-slots-9-e-10-braçadeira-e-manga-longa-de-perto-o-goleiro-capitão-e-os-22-em-campo)
("Medido (K3D-TASK-18)"), com as oito conclusões:

- `python3 tools/kits/oracle.py --replay-field 9`: saída 0, `ok    22 focus(es) follow a player and the camera comes back to the ball; the outfield captain is focus 3, number 11 with armband 90; the goalkeeper draws 92`;
- `python3 tools/kits/oracle.py --replay-field 10`: saída 0, a mesma linha com `armband 93`;
- `python3 tools/kits/oracle.py --replay-field 9 --field-button R2`: saída 0, o laço do L2 ao contrário, só impresso;
- os toques: todos mexem a tela (de 0,0687 a 0,1416), nenhum recusado — nenhum expulso; o fim é a volta à bola (k = 24 com L2), e cada foco corre de 63 a 65 quadros do último toque, sob os 390 do `--replay-idle`.

O plano dizia "de frente" e "menor z": com L2 a câmera segue **de costas**, e o seguido é a figura **no
eixo** da câmera (no slot 9, k = 21, a figura seguinte está a 2584 de profundidade, à frente do seguido
a 4692). A fonte ganha, e o G8 foi corrigido no mesmo commit.

**Instrumento, no caminho:** a caixa da figura inteira pegava as costas de um vizinho a 19–43 px do eixo
(slot 10, k = 4, 8, 15 e 20 saíam sem painel); o painel passou a ser lido só dos quads dentro da caixa
do próprio torso (`piece_box`). E as costas de todo jogador de linha amostram a célula (0,80) além da
própria: o painel é a célula que sobra (`field_panels`).

**Controle:** `--replay-field 9 --frame-json work/kits-oracle/replay-field-9-capture.json --plant-replay-field`
sai 1 com 42 `FAIL`; `… --plant-replay-field focus` sai 1 com 40 (`FAIL  focus 2: the followed figure lies at depth 7148, not under 5000`, …);
`… --plant-replay-field panel` sai 1 com `FAIL  focus 3, the outfield captain, holds number 4, not 11`.
No catálogo, `controls.py --only` dá `RED` em `oracle-replay-field-margin-unasked`,
`oracle-replay-field-shared-panel` e `oracle-replay-field-nearest-followed`. No `selftest.py`, os oito
casos `oracle --replay-field: …` dão `ok`.

Gates:
- `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:
  `100% tests passed, 0 tests failed out of 4`, nenhum *skipped*.
- `python3 tools/kits/controls.py`: `controls: 46 of 46 red`.
