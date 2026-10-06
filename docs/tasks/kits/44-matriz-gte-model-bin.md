---
id: KITS-TASK-44
---

# KITS-TASK-44 — Ler a matriz do GTE por seção do MODEL.BIN na partida

## Goal

Responder com a matriz que o jogo entrega ao GTE o que a KITS-TASK-43 não conseguiu responder pela geometria (CORR-KITS-071): a que peça do corpo se prendem, na partida do slot 5, a seção 93 (braçadeira) e as 95 a 102 (manga longa). Cada uma divide a matriz de uma seção do corpo, ou recebe a sua própria? O ajuste projetivo do `--attach` não decide isso: são 9 ou 10 pontos por seção contra 11 incógnitas (§4.3, "Negativa medida").

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py`: uma opção nova (`--attach-matrix SLOT`, por exemplo) que acha no código da partida as instruções que escrevem a matriz do GTE. É o mesmo gesto do `tools/looks/oracle.py --pose` na `LOOKS SET` (`ctc2` no registrador de controle 0). Ela lê a matriz e a translação carregadas antes de cada seção do `MODEL.BIN`, e agrupa as seções por matriz idêntica
  - `tools/kits/selftest.py`, para a parte pura nova
  - `docs/PLAN-KITS-PY.md`: §4.3, o encaixe medido
- Out: manga curta contra longa. Ela pede um save state de partida com manga curta, que é decisão do usuário (§4.3). Também fica fora desenhar na janela (KITS-TASK-40)

## Done criteria

- [x] `oracle.py --attach-matrix 5` colado no Log, sem elisão: para a seção 93 e as 95 a 102 de cada jogador, a seção do corpo cuja matriz é a mesma, ou "própria"
- [x] Um vermelho visto: a captura deslocada de uma seção (o atraso de ponteiro que o `looks` mediu) ou uma seção do corpo trocada, e a ferramenta acusando
- [x] A §4.3 diz o encaixe medido, com o comando
- [x] `ctest --test-dir build -R kits`: 4/4

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.3).

Aberta em 2026-10-06 pela [CORR-KITS-071](/docs/tasks/kits/CORR-KITS-071.md), por decisão do usuário: reabrir o critério 1 da KITS-TASK-43 (a segunda contagem) com trabalho de seguimento.

As duas armadilhas do `looks` valem aqui até prova em contrário. O ponteiro de modelo numa parada nomeia a peça **anterior**. E a transformação por peça é absoluta: o jogo entrega a câmera já composta. Ver a seção do visualizador de aparência no `CLAUDE.md` e o `tools/looks/oracle.py --pose-lag`.

Recursos: emulador e save-states. O slot 5 tem cópia mestra em `work/kits-states/`.

## Log de Execução

2026-10-06. Ambiente: `DISPLAY=:98`, `XAUTHORITY` vazio,
`WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin`,
`WE2002_LOOKS_DRIVE_IMAGE=work/looks-disc/we2002-english.cue`, fork MCP, slot 5
restaurado de `work/kits-states/`.

**Onde para.** A partida carrega a matriz por peça na mesma instrução da
`LOOKS SET`, `layout.POSE_PIECE_MATRIX` (0x8001229C), lida pelo `v1`.
Os ponteiros vivos nomeiam seções do `MODEL.BIN` pelas `model_maps` do
`looks`. Os 471 bytes que o `MODEL.BIN` difere da RAM não atrapalham a
nomeação; a suspeita, não medida, é o patch de CLUT por time.

**`--attach-matrix 5`**, ao vivo, exit 0, sem elisão:

```
  stops kept at work/kits-oracle/matrix-5.json (--frame-json reads them back)
  /BIN/EDT_MOD.BIN against RAM at its LOOKS SET address: 30937 byte(s) differ
  /BIN/MODEL.BIN against RAM at its LOOKS SET address: 471 byte(s) differ
  600 stop(s); what the pointers name, by count:
    MODEL.BIN:2                    43
    MODEL.BIN:95                   43
    MODEL.BIN:96                   43
    MODEL.BIN:98                   42
    MODEL.BIN:7                    42
    MODEL.BIN:9                    42
    MODEL.BIN:11                   42
    MODEL.BIN:8                    42
    MODEL.BIN:10                   42
    MODEL.BIN:12                   34
    MODEL.BIN:97                   26
    MODEL.BIN:93                   17
    none                           9
    MODEL.BIN:79                   9
    MODEL.BIN:56                   9
    MODEL.BIN:99                   9
    MODEL.BIN:101                  9
    MODEL.BIN:100                  9
    MODEL.BIN:102                  9
    MODEL.BIN:61                   9
    MODEL.BIN:63                   9
    MODEL.BIN:62                   9
    MODEL.BIN:64                   9
    MODEL.BIN:30                   9
    MODEL.BIN:24                   9
    MODEL.BIN:52                   9
    MODEL.BIN:42                   8
    MODEL.BIN:34                   8
  51 whole figure(s), 8 of them with a last piece no stop names; the matrix of a stop goes to the piece named 1 stop(s) later.  The order each figure draws, head first:
    x9   79 56 99 101 100 102 61 63 62 64
    x9   30 2 95 96 93 98 7 9 11 8 10 12
    x9   24 2 95 96 97 98 7 9 11 8 10 12
    x8   52 2 95 96 97 98 7 9 11 8 10 12
    x8   42 2 95 96 97 98 7 9 11 8 10 12
  every figure's translations within 119 to 210 of its median (limit 500)
  the worn sections of every figure, each against every other piece of it:
    figure  0, head 79   99 own, 101 own, 100 own, 102 own
    figure  1, head 30   95 own, 96 own, 93 own, 98 own
    figure  2, head 24   95 own, 96 own, 97 own, 98 own
    figure  3, head 52   95 own, 96 own, 97 own, 98 own
    figure  4, head 42   95 own, 96 own, 97 own, 98 own
    figure  5, head 34   95 own, 96 own, 93 own, 98 own
    figure  6, head 79   99 own, 101 own, 100 own, 102 own
    figure  7, head 30   95 own, 96 own, 93 own, 98 own
    figure  8, head 24   95 own, 96 own, 97 own, 98 own
    figure  9, head 52   95 own, 96 own, 97 own, 98 own
    figure 10, head 42   95 own, 96 own, 97 own, 98 own
    figure 11, head 34   95 own, 96 own, 93 own, 98 own
    figure 12, head 79   99 own, 101 own, 100 own, 102 own
    figure 13, head 30   95 own, 96 own, 93 own, 98 own
    figure 14, head 24   95 own, 96 own, 97 own, 98 own
    figure 15, head 52   95 own, 96 own, 97 own, 98 own
    figure 16, head 42   95 own, 96 own, 97 own, 98 own
    figure 17, head 34   95 own, 96 own, 93 own, 98 own
    figure 18, head 79   99 own, 101 own, 100 own, 102 own
    figure 19, head 30   95 own, 96 own, 93 own, 98 own
    figure 20, head 24   95 own, 96 own, 97 own, 98 own
    figure 21, head 52   95 own, 96 own, 97 own, 98 own
    figure 22, head 42   95 own, 96 own, 97 own, 98 own
    figure 23, head 34   95 own, 96 own, 93 own, 98 own
    figure 24, head 79   99 own, 101 own, 100 own, 102 own
    figure 25, head 30   95 own, 96 own, 93 own, 98 own
    figure 26, head 24   95 own, 96 own, 97 own, 98 own
    figure 27, head 52   95 own, 96 own, 97 own, 98 own
    figure 28, head 42   95 own, 96 own, 97 own, 98 own
    figure 29, head 34   95 own, 96 own, 93 own, 98 own
    figure 30, head 79   99 own, 101 own, 100 own, 102 own
    figure 31, head 30   95 own, 96 own, 93 own, 98 own
    figure 32, head 24   95 own, 96 own, 97 own, 98 own
    figure 33, head 52   95 own, 96 own, 97 own, 98 own
    figure 34, head 42   95 own, 96 own, 97 own, 98 own
    figure 35, head 34   95 own, 96 own, 93 own, 98 own
    figure 36, head 79   99 own, 101 own, 100 own, 102 own
    figure 37, head 30   95 own, 96 own, 93 own, 98 own
    figure 38, head 24   95 own, 96 own, 97 own, 98 own
    figure 39, head 52   95 own, 96 own, 97 own, 98 own
    figure 40, head 42   95 own, 96 own, 97 own, 98 own
    figure 41, head 34   95 own, 96 own, 93 own, 98 own
    figure 42, head 79   99 own, 101 own, 100 own, 102 own
    figure 43, head 30   95 own, 96 own, 93 own, 98 own
    figure 44, head 24   95 own, 96 own, 97 own, 98 own
    figure 45, head 52   95 own, 96 own, 97 own, 98 own
    figure 46, head 42   95 own, 96 own, 97 own, 98 own
    figure 47, head 34   95 own, 96 own, 93 own, 98 own
    figure 48, head 79   99 own, 101 own, 100 own, 102 own
    figure 49, head 30   95 own, 96 own, 93 own, 98 own
    figure 50, head 24   95 own, 96 own, 97 own, 98 own
  ok    every worn section has its own matrix, and section 93 is drawn where 97 is
```

**Vermelhos vistos.** Os dois foram rodados sobre as paradas guardadas,
`--frame-json work/kits-oracle/matrix-5.json`:

- `--plant-matrix lag` sai 1, com 51 linhas `FAIL`, uma por figura. Por
  exemplo: `FAIL  figure 1: a translation 878 from the figure's median, over
  500 -- the matrices are not this figure's`.
- `--plant-matrix slot` sai 1, com `FAIL  a captain draws 2 95 96 93 98 7 9 11
  8 10 12, and no figure draws it with 98 where 93 is`.
- No `selftest.py`, quatro checagens `oracle --attach-matrix`. Plantando a
  matriz da parada errada em `matrix_pieces`, duas falham, com `figure 0: a
  translation 2993 from the figure's median`. O código foi restaurado.

**O limite de 500** do `FIGURE_SPREAD` fica entre o maior espalhamento medido
com o atraso certo (210) e o menor com o atraso errado (878), os dois desta
corrida.
- **Closed** — commit `ddf3d00` (2026-10-06): feat(kits): oracle.py --attach-matrix reads each MODEL.BIN piece's GTE matrix in a match
  - Files (`git show --name-status ddf3d00`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/40-checkboxes-numero-bracadeira.md`
    - `M docs/tasks/kits/44-matriz-gte-model-bin.md`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`
- **Reviewed** (2026-10-06) at `cade713`: CORR-KITS-076, CORR-KITS-077, CORR-KITS-078
