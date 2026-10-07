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
  - defeito achado no caminho: a vista da aba 3D saía espelhada, e o conserto (`ui/figure_view.py` desenha `cx - x`) entrou aqui, com `core/figure.py`, `core/api.py`, `oracle.py` e `selftest.py` acompanhando (CORR-KITS-089; o Log explica)
- Out: árbitro (§4.5)

## Done criteria

- [x] Para cada checkbox com regra medida: as capturas de costas (`--yaw 0`) ligado e desligado diferem dentro da vista, e a planta que ignora o checkbox fica vermelha no `kits_ui`
- [x] Para cada checkbox sem regra: aparece desligado com a frase, nas duas línguas, e o `kits_ui` afirma que está desligado
- [x] Manga longa: o checkbox está visível com a figura 0 e escondido com a figura 1. O `kits_ui` afirma pelos dois `--figure`, e a planta que o deixa sempre visível fica vermelha
- [x] `ctest --test-dir build -R kits`: 4/4

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.7).

O título no estado diz "número e braçadeira". A manga longa entrou depois, pelo corpo, porque o CLI não renomeia task.

Se as 38 e 39 terminarem as duas blocked, por falta do save state de partida, esta task também espera. Entregar só os checkboxes desligados é decisão do usuário.

Da KITS-TASK-38 (2026-10-05, §4.7): na `LOOKS SET` o jogo **preenche** a lacuna do torso com uma cópia reta da zona "shirt back" — (44,6) 20×24 para (0,80) no jogador, (108,6) para (100,104) no goleiro — e **não desenha número** ali. Duas consequências aqui. As costas têm regra medida, e o 3D pode copiar esse bloco antes de desenhar; a dica da aba (`figure_hint` em `ui/i18n.py`, da KITS-TASK-37) dizia que as costas "not measured yet" — a [CORR-KITS-066](/docs/tasks/concluidos/kits/CORR-KITS-066.md) já a acertou. E o número continua sem regra: o checkbox **Number** fica desligado com a frase, a menos que o usuário dê um save state de partida.

Da KITS-TASK-39 (2026-10-05, §4.3). Na `LOOKS SET` nenhuma primitiva amostra a imagem de mangas. Na partida do slot 5 (`work/kits-states/SLPM-87056_5.sav`, Noruega × Equador de manga longa, o capitão norueguês com a bola) quem a amostra é o `MODEL.BIN`: a **braçadeira é a seção 93** e a **manga longa são as seções 95 a 102** (`oracle.py --sleeves 5 --expect-sleeves drawn`). Os checkboxes **Captain armband** e **Long sleeves** têm, portanto, geometria medida, mas é outra geometria, que não é a do `EDT_MOD.BIN` que a aba desenha hoje. Desenhar exige ler essas seções e pôr cada uma no lugar do braço da figura. O **número** ainda pode ser medido nesse mesmo slot: o `oracle.py --back` lê só (576,256), e numa partida a página do segundo time é a (640,256).

Da KITS-TASK-42 (2026-10-06, §4.7): o **número tem regra medida**. Na partida, cada jogador tem um painel de costas 20×24: a "shirt back" da figura com os glifos 6×12 da zona "numbers 0-9", só a tinta, centrados na linha 7 — um dígito em x 7, dois em x 3 e 11. O checkbox **Number** pode desenhar montando esse painel em (0,80), ou em (100,104) no goleiro, e para isso precisa de um campo de número na janela. Não foi medido como o jogo escolhe o painel de cada jogador.

Da KITS-TASK-43 (2026-10-06, §4.3). A figura de partida é o `MODEL.BIN` inteiro: 244 de 250 primitivas de kit, e 0 do `EDT_MOD.BIN`. O capitão troca a seção 97 pela 93 (`oracle.py --attach 5`). A aba 3D desenha o `EDT_MOD.BIN`, e nele não há braçadeira nem manga longa para ligar. **Captain armband** e **Long sleeves** só desenham se a aba passar a ler a figura do `MODEL.BIN`, com uma pose que ninguém mediu. Antes de destravar esta task, o usuário decide: entregar os dois checkboxes desligados, com a frase, ou abrir esse trabalho.

Da KITS-TASK-44 (2026-10-06, §4.3). Toda peça do `MODEL.BIN` tem matriz própria, e a braçadeira (93) ocupa na ordem de desenho o lugar da manga 97: é a mesma peça do corpo com outra geometria. Desenhar a braçadeira e a manga longa continua pedindo a figura de partida inteira, do `MODEL.BIN`, com uma pose, e essa decisão do usuário não mudou.

## Log de Execução

2026-10-05. Ao começar, nenhum dos três checkboxes tinha regra de desenho medida. O **Number** só tinha a `LOOKS SET`, que não desenha número. A **braçadeira** e a **manga longa** têm as seções do `MODEL.BIN` identificadas, mas não o encaixe na figura. Perguntado, o usuário escolheu "criar tasks para fazer as medições". Saíram a KITS-TASK-42 (o número numa partida) e a KITS-TASK-43 (o encaixe das seções 93 e 95 a 102). Esta task fica **blocked** até as duas fecharem, e a `order` do ciclo as põe antes dela.
- **blocked** (2026-10-05): No drawing rule for any of the three checkboxes: the number was measured only on the LOOKS SET (no digit), and the armband/long sleeves are MODEL.BIN sections 93 and 95-102 with no measured attachment to the figure. The user chose to measure first: KITS-TASK-42 (number in a match) and KITS-TASK-43 (attachment), ordered before this task.
- **pending** (2026-10-06): The cause is gone: KITS-TASK-42 (number rule), 43 and 44 (MODEL.BIN armband/long sleeves) are done.

2026-10-06. Destravada porque as 42, 43 e 44 fecharam. O usuário foi perguntado
o que fazer com a braçadeira e a manga longa, que só existem no `MODEL.BIN`, a
figura de partida que a aba não desenha. Ele escolheu "abrir trabalho de figura
de partida". Saíram as KITS-TASK-45 (pose), 46 (manga curta) e 47 (figura na
aba 3D), e a `order` do ciclo as põe antes desta. A task volta a **blocked**
até a 47 fechar. O **Number** já tem regra (KITS-TASK-42) e entra junto com os
outros dois.
- **blocked** (2026-10-06): The armband and long sleeves exist only in MODEL.BIN, the match figure the 3D tab does not draw. The user chose to open that work (2026-10-06): KITS-TASK-45 (pose), 46 (short sleeves, needs a user's save state) and 47 (match figure in the 3D tab), ordered before this task.
- **pending** (2026-10-06): KITS-TASK-47 closed (c8dfdbe): the match figure is in the 3D tab, so armband and long sleeves have geometry to switch on

### 2026-10-06 — execução

Desbloqueada: a KITS-TASK-47 fechou (`c8dfdbe`), e a aba 3D já tinha a figura de partida.

- **Number** tem regra medida (KITS-TASK-38 e 42). O `api.numbered` (`core/figure.py`) monta o painel de costas na lacuna do torso de uma figura da `LOOKS SET`: as costas copiadas de (44,6)/(108,6), e a tinta dos glifos "numbers 0-9" na linha 7, em x 7, ou em 3 e 11. Ele recolore as superfícies do kit sem regravar o TEX. O campo de número vai de 0 a 99 e abre em 10.
- **Captain armband** e **Long sleeves** desenham a figura de partida (KITS-TASK-47). No jogador da `LOOKS SET`, marcar um dos dois troca a figura. No **match player**, a manga segue o checkbox.
- **Sem regra:** a braçadeira no goleiro (`Captain armband: not measured on the goalkeeper` / `Braçadeira de capitão: não medida no goleiro`) e o número na figura de partida (`Number: not measured on the match figure` / `Número: não medido na figura de partida`). O **Long sleeves** fica escondido com o goleiro.

**Defeito achado e corrigido no caminho: a vista espelhava.** A primeira captura de costas com o número 10 mostrou "01" espelhado. A cena é o espaço do GTE com o y invertido, um referencial de mão esquerda, e o `figure_view.py` desenhava x para a direita. Agora desenha `cx - x`. Depois da troca o "10" lê certo, a braçadeira da figura de partida passa para o braço esquerdo, e o juiz do `kits_ui` da braçadeira mede 291 px numa caixa de 24×17 px (eram 337 px em 25×18 px, espelhado). A prova é o raciocínio no docstring do `figure_view.py` e a leitura do número; nenhuma captura de costas do jogo confronta a vista.

`python tools/kits/ui_check.py` (`:98`, com `WE2002_KITS_ED_IMAGE`):

```
  ok    3D TEX_14 from the back: each measured dressing changes the view (Number 5134 px, Captain armband 332 px, Long sleeves 9104 px)
  ok    the dressing boxes: Long sleeves hidden with the goalkeeper, and the dressings with no rule off with the sentence, in en-US and pt-BR
        plant 'armband drawn as section 97': the armband changes nothing
  ok    plant 'armband drawn as section 97' fails the match judge
        plant 'Number ignored': Number ticked draws the same back as unticked
  ok    plant 'Number ignored' fails the dressing judge
        plant 'Long sleeves ignored': Long sleeves ticked draws the same back as unticked
  ok    plant 'Long sleeves ignored' fails the dressing judge
        plant 'Long sleeves always shown': figure 1 en-US: long sleeves box shown; figure 1 pt-BR: long sleeves box shown
  ok    plant 'Long sleeves always shown' fails the dressing boxes judge
kits_ui: 0 failure(s)
```

`ui/app.py --list-3d` com `--figure 1`:

```
  box number: shown True, enabled True, ticked False, text Number
  box armband: shown True, enabled False, ticked False, text Captain armband: not measured on the goalkeeper
  box long sleeves: shown False, enabled True, ticked False, text Long sleeves
```

**Selftest.** O painel do núcleo é lido pelo `oracle.read_panel`, o leitor da KITS-TASK-42: 7, 10 e 23 saem nas posições medidas, escritas no próprio teste, sem pixel inexplicado, e o painel espelhado não lê 10.

- **Vermelho visto:** com `DIGIT_Y = 6` no núcleo, sai `FAIL  the 3D tab's back panel for 10 reads 10 ...  'digits': [(3, 6, 1), (11, 6, 0)]`. A primeira versão do teste não falhou com essa planta: o `oracle.py` passou a importar a mesma constante e o teste só olhava o x. Restaurado, `kits_selftest: 0 failure(s)`.
- **Controle `figure-swap-noop`:** deixou de ficar vermelho, porque o `numbered_indices` também terminava em `return bytes(out)`, o texto que a planta procura. A variável virou `panel`, e o controle voltou a ficar vermelho.

`ctest --test-dir build -R kits`: `100% tests passed, 0 tests failed out of 4`.
- **Closed** — commit `05d54ec` (2026-10-06): feat(kits): Number, Captain armband and Long sleeves boxes in the 3D tab
  - Files (`git show --name-status 05d54ec`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/40-checkboxes-numero-bracadeira.md`
    - `M docs/tasks/kits/progress.json`
    - `M docs/tasks/kits/progresso.md`
    - `M tools/kits/core/api.py`
    - `M tools/kits/core/figure.py`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui/figure_view.py`
    - `M tools/kits/ui/i18n.py`
    - `M tools/kits/ui_check.py`
- **Reviewed** (2026-10-06) at `aa0b608`: CORR-KITS-089, CORR-KITS-090
