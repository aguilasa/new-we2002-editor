---
id: KITS-TASK-42
---

# KITS-TASK-42 — Medir o número de camisa numa partida

## Goal

Responder ao passo 2 da §4.7 na partida do slot 5. A pergunta é se a lacuna do torso, ou outro lugar da página de kit, recebe o número de camisa. Se recebe, a task diz de onde vêm os texels de cada dígito e onde cada um cai. Na `LOOKS SET` o jogo copia as costas e não desenha número (KITS-TASK-38). Nada se sabe ainda da partida, e é essa regra que o checkbox **Number** da KITS-TASK-40 espera.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py`: o `--back` passa a aceitar slot de partida (`load_slot`) e uma página de kit escolhida (`--page 576|640`), com o TEX de cada página dado pelo `--slot` (Noruega `TEX_14` em (576,256), Equador `TEX_47` em (640,256)). Se o número não estiver na lacuna, ele procura na página inteira os pixels que diferem do disco
  - `tools/kits/selftest.py`, para a parte pura nova
  - `docs/PLAN-KITS-PY.md`: §4.7 com o resultado
- Out: desenhar o número na janela (KITS-TASK-40)

## Done criteria

- [x] `oracle.py --back 5 --page 576` e `--page 640` colados no Log: os pixels que diferem do disco na lacuna e no resto da página, e a origem de cada bloco escrito
- [x] Se há número: a regra na §4.7, com a zona de origem de cada dígito, o retângulo onde ele cai e o comando que mede isso. O camisa 10 da Noruega dá dois dígitos, "1" e "0", e a regra tem que dizer onde cai cada um
- [x] Se não há número na página de kit: a negativa medida na §4.7. Se o número estiver em outra página, a task diz qual, pela lista do GPU (`--sleeves` já anda essa lista)
- [x] Um vermelho visto: o TEX trocado entre as duas páginas, ou a zona errada, e a ferramenta acusando

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.7).

Criada em 2026-10-05, a pedido do usuário, quando a KITS-TASK-40 chegou sem regra para nenhum dos três checkboxes.

State: `work/kits-states/SLPM-87056_5.sav`, salvo pelo usuário em 2026-10-05. É Noruega × Equador, os dois de manga longa, e o state abre com o camisa 10 da Noruega, que é o capitão, com a bola. O `--slot 5` acha a Noruega (`TEX_14`) em (576,256) e o Equador (`TEX_47`) em (640,256). As páginas da partida batem só em parte com o disco: o uniforme diferiu em 2.640 de 8.192 halfwords contra o conjunto 1. Então a partida reescreve a página, e o número é o primeiro suspeito.

Um caso medido não é a regra: um número (10) e um time. Outro número, se for preciso, pede outro state, e isso é decisão do usuário.

## Log de Execução

2026-10-06. Ambiente: `DISPLAY=:98`, `XAUTHORITY` vazio,
`WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin`,
`WE2002_LOOKS_DRIVE_IMAGE=work/looks-disc/we2002-english.cue`, fork MCP, slot 5
restaurado de `work/kits-states/`.

**Como chegou à regra.** O `--back 5 --page 576 --tag 14 --blocks` deu um
bloco só diferente do disco, `(0,80)-(119,127) 5280 pixel(s)`, e as lacunas
não eram mais cópia das costas. O `--picture`, que pinta a página da VRAM com
a paleta do kit, mostrou uma grade de painéis de costas com números. O Equador
deu um segundo bloco na metade do goleiro, e o `--blocks` contou
`goalkeeper half, rows 0-79: 4064 pixel(s) differ from set 1, 0 from set 2`. A
mistura é por zona, e por isso entrou o `--keeper-set`.

**`--back 5 --page 576 --tag 14 --panels`**, exit 0:

```
  disc side TEX_14: 0 halfword(s) of 8192 differ from VRAM outside the panels
    player     panel (  0, 80): number 3    digits 3 at (7,7); 0 pixel(s) the rule does not explain
    ...
    player     panel ( 60,104): number 10   digits 1 at (3,7) 0 at (11,7); 0 pixel(s) the rule does not explain
    player     panel ( 80,104): number 11   digits 1 at (3,7) 1 at (11,7); 0 pixel(s) the rule does not explain
    goalkeeper panel (100,104): number 1    digits 1 at (7,7); 0 pixel(s) the rule does not explain
  ok    every panel holds the shirt back and its centred number
```

Os números na ordem da grade são `3 4 2 5 8 / 6 9 7 10 11 / 1`.

**`--back 5 --page 640 --tag 47 --keeper-set 2 --panels`**, exit 0, com
`disc side TEX_47: 0 halfword(s) of 8192 differ from VRAM outside the panels`
e os números `17 2 3 4 5 / 16 19 10 11 9 / 1`. Os 11 painéis dão `0 pixel(s)
the rule does not explain`.

**Há número.** A regra está na §4.7. O fundo é a "shirt back" da figura; os
dígitos são glifos 6×12 da zona "numbers 0-9", só a tinta, centrados na linha
7: um dígito em x 7, dois em x 3 e 11. O camisa 10 da Noruega tem o "1" em
(3,7) e o "0" em (11,7) do painel (60,104). O critério de outra página não se
aplica, porque o número está na página de kit.

**Vermelhos vistos:**

- `--back 5 --page 576 --tag 47 --keeper-set 2 --panels` (o TEX do Equador na
  página da Noruega) sai 1, com `FAIL  the disc page differs from VRAM in 4557
  halfword(s) outside the rewritten rectangles`.
- `--back 5 --page 576 --tag 14 --panels --plant-back panels` sai 1, com 22
  linhas `FAIL` (11 painéis × 2), por exemplo `FAIL  panel (0,79): digits at
  [(7, 8)], the rule puts them at [(7, 7)]`.
- No `selftest.py`, três checagens `oracle --back --panels`. Plantando o fundo
  da zona errado (`ground = min`), duas falham com `panel (0,80) holds no
  digit`; o código foi restaurado.

Regressão da `LOOKS SET`: `--back 2 --expect-back written` sai 0, com `disc
side TEX_A4: 0 halfword(s) of 8192 differ from VRAM outside the gaps`.
- **Closed** — commit `e1d38dc` (2026-10-06): feat(kits): oracle.py --back --panels measures the shirt number in a match
  - Files (`git show --name-status e1d38dc`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/40-checkboxes-numero-bracadeira.md`
    - `M docs/tasks/kits/42-medir-numero-partida.md`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`
