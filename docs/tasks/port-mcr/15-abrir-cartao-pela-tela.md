---
id: MCR-TASK-15
title: "Abrir cartão pela tela: a janela sobe primeiro, e o Open é ação visível"
type: implementação
category: ui
phase: 5
depends_on: ["MCR-TASK-12"]
fonte_de_verdade: "/docs/tasks/port-mcr/15-abrir-cartao-pela-tela.md §Critério de conclusão"
status: concluído
---

# MCR-TASK-15: abrir um cartão pela janela, sem diálogo que se antecipa a ela

## Contexto

- **Pedido do usuário em 2026-09-09**, depois do fechamento do ciclo: a UI tem
  de ter sempre uma forma de **escolher um `.mcr` do computador**, por botão ou
  por menu, e **não** deve cair direto na tela de escolher arquivo.
- **Fonte de verdade:** este arquivo. A §0 do plano descreve o escopo da v1 e a
  §3 a arquitetura, e nenhuma das duas diz como se abre um cartão — o critério
  é o daqui, como a regra de `.claude/rules/tasks.md` autoriza quando a fonte
  ainda não existe.
- **O menu já existe, e é onde tem de continuar.** `tools/mcr/ui/main_window.py`
  linhas 67-69: `&File > &Open card...`, com o atalho padrão de abrir (Ctrl+O),
  ligado a `MainWindow.choose()`, que abre um `QFileDialog` e chama `open()`.
  Esta task **não** cria uma segunda porta de leitura.

O que está medido como faltando, hoje:

| Medido | Onde |
|---|---|
| o diálogo abre **antes** da janela: `if not path: window.choose()` vem antes de `window.show()` | `tools/mcr/ui/app.py:286-288` |
| não há botão nenhum na árvore da UI — `grep -rn "QToolBar\|QPushButton" tools/mcr/ui/` dá **0** | `tools/mcr/ui/` |
| o caminho suportado nunca chega lá: `make mcr` **aborta** sem `WE2002_MCR_CARD` (`test -s`) e sempre passa a cópia como `argv[1]` | `Makefile`, alvos `$(MCR_COPY)` e `mcr` |
| trocar de cartão descarta edição não gravada sem perguntar: `open()` sobrescreve `_save` e zera `_dirty` | `tools/mcr/ui/main_window.py:123` |
| nenhum gate exercita `choose()`, e o README não cita Ctrl+O nem o item de menu | `tools/mcr/ui_check.py`, `tools/mcr/README.md` |

Três armadilhas que já foram pagas neste ciclo e valem aqui:

1. **Modal em gate é travamento, não falha** (lição 2 da MCR-TASK-12). O
   `QFileDialog` é pior que o `QMessageBox`: roda laço próprio e pode ser
   nativo. **O gate não abre o diálogo** — ele mede a ligação, não a caixa.
2. **A Regra 3 continua valendo**: nada em `tools/mcr/ui/**.py` importa
   `layout`, `card` ou `mcrio`; o estado vazio e o botão novo não são exceção,
   e o `selftest` varre.
3. **Cópia, sempre.** Abrir um cartão qualquer do disco pela tela põe o
   `mcrio.copy_target()` no caminho de gravação — o Save padrão continua indo
   para `<nome>-edited.mcr`. A recusa que protege a fixture, essa, só está
   armada enquanto `WE2002_MCR_CARD` está exportado; a recusa de `roms/` e a de
   escrita abaixo de `0x800` valem sempre.

---

## Objetivo

A janela do editor sobe **primeiro**, com ou sem cartão, e abrir um `.mcr` do
computador é uma ação visível dela — botão no estado vazio e item de menu —,
nunca um diálogo que aparece antes da janela existir.

---

## Critério de conclusão

- [x] **A janela sobe antes de qualquer diálogo.** `python3 tools/mcr/ui/app.py`
      sem argumento mostra a janela vazia e **não** abre o `QFileDialog`
      sozinho. O `if not path: window.choose()` do `app.py` sai.
- [x] **O estado vazio diz o que fazer e traz o botão.** Sem cartão, a área
      central mostra uma linha em en-US e um botão `Open card...` ligado à
      **mesma** `MainWindow.choose()` do menu — uma porta, dois gatilhos, nunca
      duas implementações de abrir.
- [x] **O item de menu fica onde está** (`&File > &Open card...`, Ctrl+O), e
      continua alcançável **com cartão aberto**, para trocar de cartão sem
      fechar a janela.
- [x] **Trocar de cartão com edição pendente pergunta antes.** Com
      `window.dirty`, `choose()` confirma o descarte; com `headless` ligado a
      confirmação **levanta** em vez de abrir modal, como as recusas da
      MCR-TASK-12.
- [x] **Cancelar o diálogo não deixa a janela sem saída**: nada fecha, nada
      trava, e o botão/menu continuam lá.
- [x] **Arquivo que não é cartão continua recusado** pelo aviso que já existe,
      e a janela segue utilizável depois da recusa.
- [x] **`make mcr` abre a janela sem cartão em vez de abortar.** Sem
      `WE2002_MCR_CARD`, ou com um caminho que não existe, o alvo sobe a UI
      vazia e diz por quê; com a variável apontada, o comportamento de hoje não
      muda — cópia em `work/` e cartão aberto. O mesmo para `make -C tools/mcr ui`.
- [x] **Gate, sem abrir o diálogo.** `ui/app.py` ganha um `--open-probe` que
      sobe sem cartão e relata em JSON: `path is None`, as três ações de
      gravação **desabilitadas**, o botão do estado vazio presente, e o botão e
      o item de menu chegando à **mesma** ação. Quem julga é o `ui_check.py`,
      como na CORR-MCR-018 — a tela relata, não afirma. **Ganhou um passo a
      mais na execução**: um arquivo que não é cartão, para medir que a janela
      **sobrevive** à recusa e continua abrindo no clique seguinte.
- [x] **Caso vermelho plantado**, com a disciplina do `controls.py`: **dois**,
      os dois em `ui/main_window.py` — a ligação do botão e a guarda de edição
      não gravada —, plantados a cada corrida do gate. Casar zero ou duas vezes
      é controle quebrado, não vermelho.
- [x] **Capturas no `:98`** — janela vazia com o botão, e a mesma janela depois
      de abrir um cartão pelo menu — anexadas ao Log.
- [x] **README e os dois `Makefile` atualizados**: como subir a UI sem cartão,
      o Ctrl+O e o item de menu, e o que muda no alvo `mcr`.
- [x] Strings da UI em **en-US** (§3.5); esta task e o Log, em português.
- [x] `python3 tools/mcr/selftest.py`, `python3 tools/mcr/controls.py` e
      `ctest -R mcr` com `WE2002_MCR_CARD` apontado — os três verdes, com o
      número medido de cada um no Log.

---

## Log de Execução

**Executado em:** 2026-09-09

### Resumo do que foi feito

O pedido era "ter uma opção de abrir", e **ela já existia**: o item
`File > Open card...` com `Ctrl+O` está no `main_window.py` desde a
MCR-TASK-11. O que faltava era o contrário do que o nome sugere — não uma porta
a mais, e sim **tirar a porta que se abria sozinha**. O `app.py` chamava
`choose()` antes de `show()`, então a primeira coisa na tela era um
`QFileDialog` modal sobre nada; cancelado, sobrava uma janela em branco em que
o único caminho de volta era um menu que ninguém tinha motivo para procurar. E
o caminho suportado nunca chegava lá: `make mcr` **abortava** sem
`WE2002_MCR_CARD` e sempre passava a cópia em `argv[1]`.

Três coisas mudaram, e a que decide as outras duas é a primeira:

1. **A janela sobe primeiro, com ou sem cartão.** O centro virou um
   `QStackedWidget` de duas páginas: a vazia, com a frase e o botão
   `Open card...`, e as abas. Abrir um cartão troca a página; nada mais no
   arquivo sabe disso.
2. **Duas maneiras de entrar, um caminho só.** O botão não chama `choose` — ele
   dispara `act_open`, a **mesma** `QAction` que o menu carrega. É a diferença
   entre uma porta com duas maçanetas e duas portas que envelhecem separadas, e
   é o que o primeiro controle negativo mede: com a ligação trocada por
   `lambda: None`, o clique deixa de alcançar o caminho e o gate fica vermelho.
3. **`make mcr` deixou de abortar.** Sem cartão — variável vazia, ou apontando
   para arquivo que não existe — ele sobe a janela vazia e diz que é o editor
   quem abre um. Quem decide isso é um `$(wildcard)` em tempo de parse, que
   torna a cópia prerequisito **só quando há o que copiar**; o `tools/mcr` ganhou
   `ui-vazia`, que delega com a variável vazia.

### O modal é o inimigo do gate, e agora tem seam

A lição 2 da MCR-TASK-12 — *"modal em gate é travamento, não falha"* — vale
mais forte aqui: um `QFileDialog` roda laço próprio e pode ser **nativo**, então
um gate que clicasse no botão ficaria parado até o timeout de 120 s e relataria
"não saiu" em vez do motivo. A saída foi pôr as duas caixas atrás de métodos,
`_ask_for_card()` e `_confirm_discard()`, que o probe **substitui**. O caminho
inteiro continua sendo exercitado — botão, ação, `choose`, `open` —, só a caixa
é que não sobe; e alcançar a caixa de verdade numa corrida `headless`
**levanta**, para que o dia em que o seam sumir seja um vermelho e não um
travamento.

A guarda de descarte fica **antes** do diálogo de propósito: perguntar qual
arquivo abrir e só depois avisar que as edições se perdem obriga a responder
duas perguntas para desfazer um engano.

### O que o gate mede agora

`ui_check.py` ganhou `open_probe`, e ele roda **com ou sem fixture** — o que
mede primeiro é justamente a máquina que não tem cartão:

```
open: the window came up with no card, showing the empty page and a
      'Open card...' button behind Open card... (Ctrl+O); cancelling changed nothing
open: a file that is not a card was refused (...) and the window stayed empty
      and still opened on the next click
open: the dialog named a card and the window opened it, and an unsaved edit
      survived a refused discard (asked=0, confirmed=1)
negative: breaking the button's wiring reddens the gate -- clicking the empty
      page's button reached the open path 0 time(s), not once
negative: breaking the dirty guard reddens the gate -- opening another card with
      unsaved edits asked for confirmation 0 time(s), not once
```

`asked=0` é a asserção que mais vale ali: com o descarte recusado, o diálogo
**não chega a abrir**. Sem fixture, o passo imprime `note: no WE2002_MCR_CARD,
so the open probe stopped after the empty window` e o alvo continua passando —
mesma convenção da linha irmã do write probe, e mesma advertência: leia a linha,
não o `Passed`.

### As capturas, no `:98`

```
$ export DISPLAY=:98 XAUTHORITY=
$ work/venv-mcr/bin/python tools/mcr/ui/app.py --screenshot work/mcr-ui-vazia.png
wrote work/mcr-ui-vazia.png (no card)
$ work/venv-mcr/bin/python tools/mcr/ui/app.py work/mcr-entrada.mcr --tab 0 \
    --screenshot work/mcr-ui-players.png
wrote work/mcr-ui-players.png with mcr-entrada.mcr
```

As duas em `work/`, que é gitignored. A vazia mostra o menu `File`, a frase
("No card open" mais o que fazer e para onde a gravação vai) e o botão
`Open card...` centrado, com `No card open` na barra de estado.

### Os gates da fase

| gate | resultado medido |
|---|---|
| `python3 tools/mcr/selftest.py` | `0 failure(s) over 12 modules plus the design rules` |
| `python3 tools/mcr/controls.py` | `controls: 20 of 20 red (19 substitutions, 1 new file)` |
| `python3 tools/mcr/glossary.py` | `0 complaint(s)` |
| `ui_check.py` com fixture | `rc=0`, com os **seis** plantios vermelhos (2 do arraste, 2 do domínio, 2 novos) |
| `ctest -R mcr` com `WE2002_MCR_CARD` | **3 de 3** |
| `ctest -R mcr` sem fixture | 3 de 3, com `mcr_card` *skipped* e o `mcr_ui` medindo a janela vazia |
| `make test` | **10 de 10** |
| `check_tasks.py` / `ctest -R tasks` | 101 tasks ok / 1 de 1 |
| fixture | `e53f4895affe075bced499a32ba736d10a20f72b010c9c8c05c1269e77c47546`, intocada; `roms/` idem |

E os três lançamentos, medidos de verdade e não só com `make -n`:
`make mcr WE2002_MCR_CARD= ARGS=--smoke` e
`make -C tools/mcr ui-vazia ARGS=--smoke` imprimem
`smoke: window up, card not loaded`; `make mcr ARGS=--smoke`, com a fixture,
continua imprimindo `card loaded` sobre `work/mcr-entrada.mcr`.

### Arquivos criados/modificados

- `tools/mcr/ui/main_window.py` — a página vazia, o `QStackedWidget`, o botão
  ligado à ação do menu, os dois seams e a guarda de descarte
- `tools/mcr/ui/app.py` — `--open-probe`/`--open-with`, a saída do
  `choose()` de antes do `show()`, e o `--screenshot` mirando `window.tabs`
  (o centro deixou de ser o `QTabWidget`)
- `tools/mcr/ui_check.py` — `_run_open`, `_judge_open`, `_plant_open`,
  `open_probe`, os dois `OPEN_BREAKS` e o `_sandbox` com o arquivo a quebrar
- `Makefile` — `MCR_CARD_THERE`, a cópia como prerequisito condicional, o alvo
  `mcr` sem cartão e a linha de ajuda
- `tools/mcr/Makefile` — o alvo `ui-vazia`, o `.PHONY` e a ajuda
- `tools/mcr/README.md` — a seção "Escolher o cartão pela janela", a linha do
  `ui-vazia` na tabela e a bandeira nova
- `CLAUDE.md` — a linha do `make mcr` na tabela do projeto `mcr`
- `docs/prompts/perfil-mcr.md` — a linha do `mcr_ui` (quatro plantios viraram
  seis, e o passo novo)
- `docs/PLAN-MCR-PY.md` — a Fase 5 na §7, com o motivo de ela não ser reabertura
- `docs/tasks/port-mcr/progresso.md` — a linha, a Fase 5, o grafo e a tabela
  "Estado medido"
- `docs/tasks/port-mcr/15-abrir-cartao-pela-tela.md` — esta task, criada nesta
  mesma leva

### Problemas encontrados

- **A primeira versão do juiz contava totais, não deltas.** O passo da recusa
  entrou depois e acrescentou um clique; `asked_from_menu != 2` passou a acusar
  o que estava certo (`the menu item did not open the card the dialog named:
  /tmp/…/open.mcr for /tmp/…/open.mcr` — o mesmo caminho dos dois lados, e a
  falha era a contagem). Todo contador do probe virou **delta**, e o comentário
  diz por quê: total absoluto obriga quem acrescentar um passo no meio a
  atualizar uma asserção que não é sobre ele.
- **O `--screenshot` mirava `window.centralWidget()`**, que era o `QTabWidget`.
  Com o `QStackedWidget` no centro, `--tab 1` teria trocado de **página** em vez
  de aba — a captura da formação sairia sendo a tela vazia. Corrigido para
  `window.tabs`, que é o nome que a janela agora expõe.
- Nada mais. A recusa de arquivo que não é cartão, a gravação e o arraste
  continuam medidos pelos passos que já existiam.
