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

- [ ] G8 tem a saída de `oracle.py --replay-field 9` e `--replay-field 10` coladas da HEAD: a tabela dos focos até a volta à bola, com time, família, cabeça, manga, braçadeira, painel e número por foco, e as conclusões escritas uma a uma — o foco do Bokšić e do Marcos nos dois slots, a manga por slot (curta no 9, longa no 10, goleiro sempre longa; divergência por jogador escrita como resultado), cabeça por jogador ou por figura, painel ↔ número contra a grade do §4.7, a ordem do L2/R2 —, toda negativa com comando e saída
- [ ] o Bokšić desenha a 90 no slot 9 e a 93 no 10, e o Marcos a seção que a K3D-TASK-17 mediu (controles positivos do relato do usuário); divergência é resultado, escrita
- [ ] cada foco recarrega o state e toca L2 k vezes com o `press` exigindo a tela mudar; um toque que não muda a tela é impresso como a volta à bola ou um expulso, e a corrida fica abaixo do timeout da K3D-TASK-17
- [ ] `--replay-field 9 --plant-replay-field` sai 1 (foco pela segunda menor z; painéis uma linha acima); o controle novo dá `RED` em `python3 tools/kits/controls.py --only <nome>`, e os casos novos do `selftest.py` dão `ok`
- [ ] sem uma das cópias mestras: `rite mark K3D-TASK-18 blocked --unblocked-by "test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav"` e o pedido ao usuário
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

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
E o "De frente basta" acima não vale: de frente o torso do goleiro não manda à GPU nenhum quad do
painel; de costas, quatro, e eles são os texels do próprio torso 13 no disco — o painel do goleiro é
fixo na seção. Para os 20 de linha, o painel pede as costas (R1) em cada foco, ou um argumento de
que o UV é fixo também no torso 2.

## Log de Execução
