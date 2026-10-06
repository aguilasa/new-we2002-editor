---
id: KITS-TASK-40
---

# KITS-TASK-40 — Checkboxes de número e braçadeira na aba 3D

## Goal

A aba 3D ganha três checkboxes, **Number**, **Captain armband** e **Long sleeves**, que desenham na figura só o que as KITS-TASK-38 e 39 mediram. O de manga longa, pedido do usuário em 2026-10-05, só aparece com a figura de jogador de linha: com o goleiro ele fica escondido, e não apenas desligado. O que não foi medido fica com o checkbox desligado e a frase "not measured" no catálogo. Remapear UV à mão não vale (§0).

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/app.py`, `tools/kits/ui/i18n.py`
  - `tools/kits/core/figure.py` e `tools/kits/core/api.py`, se a regra medida pedir composição de texels ou geometria a mais
  - `tools/kits/ui_check.py`: a verificação e a planta
  - `docs/PLAN-KITS-PY.md`: §3.4
- Out: árbitro (§4.5)

## Done criteria

- [ ] Para cada checkbox com regra medida: as capturas de costas (`--yaw 0`) ligado e desligado diferem dentro da vista, e a planta que ignora o checkbox fica vermelha no `kits_ui`
- [ ] Para cada checkbox sem regra: aparece desligado com a frase, nas duas línguas, e o `kits_ui` afirma que está desligado
- [ ] Manga longa: o checkbox está visível com a figura 0 e escondido com a figura 1. O `kits_ui` afirma pelos dois `--figure`, e a planta que o deixa sempre visível fica vermelha
- [ ] `ctest --test-dir build -R kits`: 4/4

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.7).

O título no estado diz "número e braçadeira". A manga longa entrou depois, pelo corpo, porque o CLI não renomeia task.

Se as 38 e 39 terminarem as duas blocked, por falta do save state de partida, esta task também espera. Entregar só os checkboxes desligados é decisão do usuário.

Da KITS-TASK-38 (2026-10-05, §4.7): na `LOOKS SET` o jogo **preenche** a lacuna do torso com uma cópia reta da zona "shirt back" — (44,6) 20×24 para (0,80) no jogador, (108,6) para (100,104) no goleiro — e **não desenha número** ali. Duas consequências aqui. As costas têm regra medida, e o 3D pode copiar esse bloco antes de desenhar; a dica da aba (`figure_hint` em `ui/i18n.py`, da KITS-TASK-37) dizia que as costas "not measured yet" — a [CORR-KITS-066](/docs/tasks/kits/CORR-KITS-066.md) já a acertou. E o número continua sem regra: o checkbox **Number** fica desligado com a frase, a menos que o usuário dê um save state de partida.

Da KITS-TASK-39 (2026-10-05, §4.3). Na `LOOKS SET` nenhuma primitiva amostra a imagem de mangas. Na partida do slot 5 (`work/kits-states/SLPM-87056_5.sav`, Noruega × Equador de manga longa, o capitão norueguês com a bola) quem a amostra é o `MODEL.BIN`: a **braçadeira é a seção 93** e a **manga longa são as seções 95 a 102** (`oracle.py --sleeves 5 --expect-sleeves drawn`). Os checkboxes **Captain armband** e **Long sleeves** têm, portanto, geometria medida, mas é outra geometria, que não é a do `EDT_MOD.BIN` que a aba desenha hoje. Desenhar exige ler essas seções e pôr cada uma no lugar do braço da figura. O **número** ainda pode ser medido nesse mesmo slot: o `oracle.py --back` lê só (576,256), e numa partida a página do segundo time é a (640,256).

Da KITS-TASK-42 (2026-10-06, §4.7): o **número tem regra medida**. Na partida, cada jogador tem um painel de costas 20×24: a "shirt back" da figura com os glifos 6×12 da zona "numbers 0-9", só a tinta, centrados na linha 7 — um dígito em x 7, dois em x 3 e 11. O checkbox **Number** pode desenhar montando esse painel em (0,80), ou em (100,104) no goleiro, e para isso precisa de um campo de número na janela. Não foi medido como o jogo escolhe o painel de cada jogador.

Da KITS-TASK-43 (2026-10-06, §4.3). A figura de partida é o `MODEL.BIN` inteiro: 244 de 250 primitivas de kit, e 0 do `EDT_MOD.BIN`. O capitão troca a seção 97 pela 93 (`oracle.py --attach 5`). A aba 3D desenha o `EDT_MOD.BIN`, e nele não há braçadeira nem manga longa para ligar. **Captain armband** e **Long sleeves** só desenham se a aba passar a ler a figura do `MODEL.BIN`, com uma pose que ninguém mediu. Antes de destravar esta task, o usuário decide: entregar os dois checkboxes desligados, com a frase, ou abrir esse trabalho.

## Log de Execução

2026-10-05. Ao começar, nenhum dos três checkboxes tinha regra de desenho medida. O **Number** só tinha a `LOOKS SET`, que não desenha número. A **braçadeira** e a **manga longa** têm as seções do `MODEL.BIN` identificadas, mas não o encaixe na figura. Perguntado, o usuário escolheu "criar tasks para fazer as medições". Saíram a KITS-TASK-42 (o número numa partida) e a KITS-TASK-43 (o encaixe das seções 93 e 95 a 102). Esta task fica **blocked** até as duas fecharem, e a `order` do ciclo as põe antes dela.
- **blocked** (2026-10-05): No drawing rule for any of the three checkboxes: the number was measured only on the LOOKS SET (no digit), and the armband/long sleeves are MODEL.BIN sections 93 and 95-102 with no measured attachment to the figure. The user chose to measure first: KITS-TASK-42 (number in a match) and KITS-TASK-43 (attachment), ordered before this task.
