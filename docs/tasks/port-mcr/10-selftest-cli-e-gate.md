---
id: MCR-TASK-10
title: "`selftest.py`, o CLI e os três alvos de `ctest` — fecha a Fase 1"
type: ferramenta
category: ferramental
phase: 2
depends_on: ["MCR-TASK-09"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §5.2"
status: pendente
---

# MCR-TASK-10: O gate

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §4.4 e §5.2.
- O padrão do repositório: `self_check()` importável, agregado num `selftest`, e
  registro no `ctest` com `SKIP_RETURN_CODE 77` quando depende de fixture ou de
  ambiente. `tools/pes2/selftest.py` é o modelo; `savestate.py` é o exemplar do
  controle negativo.
- **A partir daqui a regressão fica vermelha sozinha**, e é a partir daqui que a
  UI pode começar sem risco.

---

## Objetivo

Fechar a Fase 1 com gate: um selftest que roda em qualquer máquina, um CLI
utilizável, e três alvos de `ctest` com faixas de custo distintas.

---

## Critério de conclusão

- [ ] `tools/mcr/selftest.py` monta um cartão sintético em memória e agrega os
      `self_check()` dos módulos — **sem depender da fixture e sem Qt**.
- [ ] As duas guardas da Regra 3: `ui/*.py` não importa `layout`/`card`/`mcrio`,
      e `"PySide6" not in sys.modules` depois de importar o núcleo inteiro.
- [ ] **O módulo de I/O chama-se `mcrio.py`, não `io.py`**, e o agregador tem de
      importá-lo por esse nome. A §3.2 do plano dizia `io.py`, e a MCR-TASK-09
      mediu que esse nome é inutilizável: com `tools/mcr` na frente do
      `sys.path`, `import io` devolve o da stdlib — que o CPython cacheia antes
      de qualquer código nosso rodar —, então um `io.py` aqui roda como script e
      **não é importável**. O plano já foi corrigido; a asserção que o prova
      mora no `self_check` do `mcrio.py`.
- [ ] **São nove módulos com `self_check()`, não sete**: `card`, `layout`,
      `attributes`, `numbers`, `text`, `domains`, `formation`, `model` e
      `mcrio`. Os dois últimos nasceram na MCR-TASK-09, e o `mcrio` é o único
      que roda o controle negativo da §5.2 inteiro (`--negative`, 5/5).
- [ ] **A guarda da Regra 1 já existe e precisa ser agregada aqui**: a
      MCR-TASK-05 a escreveu como `layout.address_monopoly()`, com CLI
      `python3 tools/mcr/layout.py --rule1`. Ela varre `tools/mcr/*.py` (menos
      o próprio `layout.py`) atrás de literal hexadecimal dentro de
      `0x4000..0x8000` **e** dos mesmos endereços em decimal — o upstream
      escreve `22788` e `21508`, que passariam batido por varredura só de hex.
      Hoje devolve **0**; o `selftest` tem de chamá-la, não reimplementá-la.
- [ ] **O `attempt()` está em `card.py`, `layout.py` e `attributes.py`**, e o
      `refuses()`/`recusa()` em dois deles. A MCR-TASK-04 mediu por que o
      primeiro existe (sem ele, o defeito que levanta exceção mata a corrida e
      esconde os checks seguintes) e a MCR-TASK-06 mediu por que o segundo
      também: um `try/except ErroEspecífico` escrito à mão deixa passar
      **qualquer outra** exceção, e foi o que aconteceu ao plantar o swap da
      v4.2 — o self-check morreu no meio e três checks não rodaram. A terceira
      cópia já nasceu; **escolha uma casa só para os dois** ao montar o
      `selftest`.
- [ ] **`layout.find_upward()` é o resolvedor compartilhado de caminho**, e a
      MCR-TASK-08 o hasteou para lá depois de o mesmo defeito aparecer três
      vezes: `layout.py` (o `mcr.md`), `attributes.py` e `domains.py` (o clone
      do upstream) localizavam o alvo contando saltos de `dirname` a partir de
      `__file__`. Uma cópia do módulo um diretório mais raso — que é o que todo
      controle negativo é — aponta para lugar nenhum, e o check **pula** em vez
      de falhar. Use-o em qualquer módulo novo que precise achar algo fora de
      `tools/mcr/`.
- [ ] **A varredura da Regra 1 tokeniza, não greppeia.** Desde a MCR-TASK-08 a
      `address_monopoly()` ignora comentários, literais de string e os tokens
      de f-string (`FSTRING_MIDDLE`, novos no 3.12 — sem eles a prosa dentro de
      um `print` f-string é lida como código). O motivo: um módulo tem de poder
      nomear na própria documentação o endereço sobre o qual ele opera, e o
      `formation.py` nomeia onze. Ao mexer nela, replante uma constante de
      verdade e confira que continua vermelha.
- [ ] **O harness precisa de um guard EXTERNO, não só de helpers.** Cinco vezes
      neste ciclo um `ok(...)` cuja expressão levanta matou a corrida e
      escondeu os checks seguintes — MCR-TASK-04 (`find_save`), MCR-TASK-06
      (o `try/except` de recusa), e três vezes na MCR-TASK-07 (`encode_table`,
      `read_all`, `decode_name`). Passar cada chamada por `attempt()` conserta
      **uma de cada vez** e a sexta volta. O conserto durável é envolver o
      corpo inteiro do `self_check` de modo que qualquer exceção que escape
      vire uma falha nomeada e a contagem final ainda saia. Faça isso no
      harness compartilhado, e os cinco módulos herdam.
- [ ] **O `selftest` importa `layout` dentro do `attempt()`**, não no escopo do
      módulo: as vistas nomeadas do `layout.py` levantam `LayoutError` no
      import quando um destino some, e o `mcr_selftest` é o gate
      **obrigatório** — uma tabela quebrada tem de virar uma falha nomeada
      entre as demais, não um traceback que derruba a corrida inteira. Medido
      na [CORR-MCR-008](/docs/tasks/port-mcr/CORR-MCR-008.md): nos dois
      controles que tiram um destino, o `layout.py --self-check` sai por
      traceback com **0** das 29 asserções rodadas. É a mesma lição que a
      MCR-TASK-04 pagou e que vale para as tasks 05 a 10.
- [ ] `cli.py` com `info`, `dump`, `get`, `set`, `roundtrip`, `negative` e
      `check`, saída determinística.
- [ ] **Decidir se o `negative` planta os controles em vez de descrevê-los.**
      Hoje o estímulo de cada controle mora em prosa numa tabela de Log, e a
      [CORR-MCR-009](/docs/tasks/port-mcr/CORR-MCR-009.md) mediu o custo disso:
      duas das cinco contagens da MCR-TASK-06 não reproduziam a partir da
      descrição, porque "trocar dois campos no encoder" tem mais de uma
      leitura. Como subcomando — plantar a substituição, rodar, exigir o
      vermelho e a contagem —, o número passa a ser **medido** em vez de
      anotado à mão. É a mesma regra que o `CLAUDE.md` já aplica aos golden:
      sem o estímulo versionado a corrida não é repetível. A decisão de fazê-lo
      agora é de quem executar esta task; o que não vale é deixá-la implícita.
- [ ] `glossary.py` — o mapa `es → en` (§3.5), que até aqui não tinha task
      dona: `jugador→player`, `cancha→pitch`, `formacion→formation`,
      `grabar→write`, `bufersizenum→group_size`.
- [ ] A varredura de idioma no `selftest`: **nenhum espanhol remanescente e
      nenhuma prosa portuguesa em `tools/mcr/**.py`**. Todo o código do port é
      **en-US** — docstrings, comentários, mensagens, `--help` e saída do CLI
      (§3.5). **A varredura nasce sem lista de exceção:** o `card.py` era a
      única, e a [CORR-MCR-007](/docs/tasks/port-mcr/CORR-MCR-007.md) a fechou
      em 2026-09-07, antes desta task.
- [ ] Três alvos em `tests/CMakeLists.txt`: `mcr_selftest` (obrigatório),
      `mcr_card` (`WE2002_MCR_CARD`, skip 77) e `mcr_ui` (venv + `:98`, skip 77).
- [ ] **Numa máquina sem venv e sem fixture**, `ctest -R mcr` reporta
      **1 passed, 2 skipped** — nunca `0 tests`, nunca erro.
- [ ] `make test` continua verde.

---

## Log de Execução

*(a preencher)*
