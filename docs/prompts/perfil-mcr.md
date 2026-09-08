# Perfil de ciclo — port em Python do editor de `.mcr` do WE2002

**Este arquivo é o perfil do ciclo `port-mcr`**, nomeado pelo campo `perfil:` do
[`docs/tasks/port-mcr/progresso.md`](/docs/tasks/port-mcr/progresso.md) e
carregado pelos prompts de `docs/prompts/`. Os prompts têm o **rito**; o que é
deste ciclo mora aqui.

Fonte: [`PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md). Onde este perfil e o plano
divergirem, **o plano ganha** — aqui só mora o resumo operacional, e o
`fonte_de_verdade` de cada task aponta para a seção que a mede.

**Este ciclo mora numa subpasta**, e é o primeiro que mora. Os comandos o
recebem por argumento: `/executar port-mcr`, `/revisar port-mcr`,
`/corrigir port-mcr`. Sem argumento, os comandos continuam no `docs/tasks/`
raso, que é o ciclo de PES2. A regra está no "Passo 0" de cada prompt.

---

## Contexto essencial — decisões já confirmadas

- **O upstream se porta literalmente, e ele não tem licença.** Decisão do dono
  do repositório, 2026-09-07, com o aviso na mesa. O repo já vive nessa posição
  com `legacy/mfc/`, e por isso não tem `LICENSE`. (§2 do plano)
- **O fonte VB não entra no git.** Clone em `work/easy-mcr/`, SHA
  `30af1fe5` fixado, inventário registrado. O que entra é o port.
- **O núcleo não conhece Qt; a UI não conhece endereço.** Duas guardas
  mecânicas no `selftest`, e a segunda é a que mantém o gate obrigatório
  rodando numa máquina sem Qt. (§3.3, Regra 3)
- **PySide6 em venv, nunca por `apt`.** O Python desta máquina é duplo. (§4)
- **Tática é somente leitura na v1.** O escritor original grava seis destinos e
  o leitor dele nunca lê nenhum. (§1.9)
- **O código do port é en-US, a documentação é português.** Identificadores,
  docstrings, comentários, mensagens de erro, `--help` e rótulo de UI em inglês;
  `docs/**` em português. A fronteira é o arquivo. Decisão do dono do
  repositório, 2026-09-07. O `card.py` era anterior a ela e foi retraduzido pela
  [CORR-MCR-007](/docs/tasks/port-mcr/CORR-MCR-007.md) no mesmo dia; **não há
  exceção aberta**. (§3.5 do plano)
- **Cartão de jogo não se versiona.** A fixture é `work/entrada.mcr`, apontada
  por `WE2002_MCR_CARD`. Mesma regra de `roms/`.
- **Controle negativo se registra pela substituição literal**, nunca pela
  descrição do efeito: a linha de origem, a de destino e a função onde ela mora.
  Duas contagens da MCR-TASK-06 e uma da MCR-TASK-07 não reproduziram da prosa
  ([CORR-MCR-009](/docs/tasks/port-mcr/CORR-MCR-009.md),
  [CORR-MCR-011](/docs/tasks/port-mcr/CORR-MCR-011.md)) — "trocar dois campos no
  encoder" tem mais de uma leitura, e uma linha que aparece duas vezes no
  arquivo precisa da função para ser identificada. A cópia plantada roda com
  `PYTHONPATH=tools/mcr`, senão morre em `ModuleNotFoundError` antes de medir, e
  **confira que a substituição casou**: literal que não bate deixa a cópia
  intacta e a corrida sai verde.
  **E casar não basta — o check que o defeito deveria acender tem de ter
  rodado.** Na MCR-TASK-08 um rótulo inventado passou verde com a substituição
  confirmada: a cópia em `/tmp` não enxergava `work/easy-mcr`, o check contra o
  upstream **pulou**, e "0 failure(s)" foi lido como aprovação. Leve para o
  sandbox o que o módulo precisa (a fixture, o clone) ou confira que a linha de
  `skip` não é justamente a do defeito plantado.

---

## Armadilhas medidas neste ciclo

1. **O Python é duplo.** `python3` do `PATH` é o mise **3.13.13**;
   `/usr/bin/python3` é **3.12.3**; o `build/CMakeCache.txt` fixou o mise. Um
   `apt install python3-pyqt6` instala para o 3.12 e **fica invisível** — o apt
   termina em verde e o `import` continua falhando.
2. **O nome de 10 bytes é cp932**, não ASCII. O `KanjiToAscii` do `we2002_core`
   devolve cinco espaços para o slot 0 da fixture: ele só translitera pares
   `0x82` e manda o resto para espaço. Usá-lo aqui apaga nome japonês em
   silêncio. O upstream tem o mesmo defeito, agravado por um
   `Regex.Replace(texto, "[^a-zA-Z.]", "")`.
3. **Escrever abaixo de `0x800` destrói o cartão.** Os bytes `0..137` são o
   quadro `MC` e o `state`+`size`+`link` da entrada 1 do diretório — medido. O
   upstream grava IDs do banco dele ali. O port **recusa**.
4. **O dorsal está gravado duas vezes**, e é isso que denuncia erro de
   gravação: `1 + ((raw[3]>>2)&0x1f)` tem de bater com a tabela de `0x5404`.
   23/23 na fixture.
5. **A v4.2 do upstream troca Speed e Dribble só na gravação.** Transcrever sem
   conferir herda o defeito, e todo cartão gravado sai com dois atributos
   permutados.
6. **O upstream assume o bloco do save.** Ele trata o cartão como binário plano;
   se o save não estiver no bloco esperado, todo offset se desloca em múltiplos
   de 8192 e o resultado parece plausível.
7. **Os fatores `X*7` e `Y*2` são de tela**, não de formato. Se entrarem no
   núcleo, o round-trip morre.
8. **A tabela de cobradores não é crescente** — `0x614F, 0x6140, 0x6122,
   0x6113, 0x6131`. Aritmética no lugar da tabela grava no campo errado.
9. **A fixture é compartilhada com o ciclo `wte/`, e aquele lado sabe
   regerá-la.** `work/entrada.mcr` é apontada aqui por `WE2002_MCR_CARD` e lá
   por `WTE_MCR_ENTRADA`/`WTE_MCR_FIXTURE` — e por **caminho cravado** em
   `wte/tools/test_dump_mcr.py:341`, que é a razão de o digest ser a régua:
   trocar variável não desvia o lado de lá. Nenhuma das formas escreve nela,
   mas o
   cabeçalho da `golden-13-roundtrip` manda `cp work/saida.mcr
   work/entrada.mcr`, e o `golden_check.sh` produz esse `saida.mcr`. Trocado o
   cartão, os números medidos deste ciclo — 23/23 dorsais, `[7,7,8,7,7]`, o
   cp932 dos slots 0 e 20 — passam a ser sobre outro save, e a divergência
   parece bug do port. O digest que os ancora está na tabela "Estado medido" do
   `progresso.md`: `sha256sum work/entrada.mcr` antes de acusar qualquer coisa.

---

## As fontes de verdade binárias

| pergunta | quem responde |
|---|---|
| onde fica cada campo | [`wte/re/mcr.md`](../../wte/re/mcr.md) — 17 destinos medidos do `we-team-editor.exe` |
| como se empacotam os 12 bytes | [`src/core/Player.cpp`](../../src/core/Player.cpp) — **normativo** |
| o contêiner PSX | spec pública do nocash, já implementada em `wte/tools/dump_mcr.py` |
| o que significam X, Y, papéis e os domínios | o upstream — **rótulo de terceiro, não medição** |
| o `0x6500` | **em aberto** até a MCR-TASK-13 |
| a tática | **sem oráculo** — v1 passa intacta |

---

## Estrutura

```text
tools/mcr/            15 módulos: o núcleo, o harness, os controles, o CLI e os gates
tools/mcr/ui/         a UI PySide6 -- não importa layout/card/io
work/venv-mcr/        o venv com PySide6 6.11.2 (fora do git, 663 MB)
work/entrada.mcr      a fixture (fora do git) -- compartilhada com o ciclo wte/
work/mcr-entrada.mcr  a copia que o `make mcr` edita; a fixture nao se abre
work/easy-mcr/        o clone do upstream (fora do git)
docs/PLAN-MCR-PY.md   a fonte de verdade
docs/tasks/port-mcr/  este ciclo
```

---

## Gates deste ciclo

| gate | a partir de | o que julga |
|---|---|---|
| `ctest -R tasks` | já existe | as convenções de task, inclusive nesta subpasta |
| `mcr_selftest` | MCR-TASK-10 | os 12 `self_check()`, as três regras, a varredura de idioma **e as 14 substituições literais, exigidas vermelhas** — sem fixture e sem Qt, ~13 s. **Obrigatório** |
| `mcr_card` | MCR-TASK-10 | `cli.py check`: round-trip nas duas formas e os cross-checks contra `WE2002_MCR_CARD` (skip 77) |
| `mcr_ui` | MCR-TASK-10 | `ui_check.py`: chama `ui/app.py --smoke` no `:98` com o venv. Registrado já; pula com 77 até a MCR-TASK-11 criar o `app.py` |

Antes da MCR-TASK-10 **não havia gate deste ciclo**, e é por isso que a ordem
mandou: 05 antes de 06/07/08, 09 antes de 11, 10 antes de 12. **Desde
2026-09-08 há**, e o `mcr_selftest` é o obrigatório.

**Controle negativo se roda, não se descreve.** As catorze substituições moram
em `tools/mcr/controls.py` — arquivo, função, linha exata, e o que ela vira —,
e `python3 tools/mcr/controls.py` planta cada uma numa cópia da árvore e exige
o vermelho. Substituição que casa zero ou duas vezes é reportada como
**controle quebrado**, não como vermelho. O `mcr_selftest` as roda a cada
corrida.

---

## Arquivos quentes deste ciclo

- `docs/tasks/port-mcr/progresso.md` — toda task escreve nele; é o recurso mais
  garantido de colidir num lote.
- `docs/PLAN-MCR-PY.md` — as tasks de fechamento escrevem; as demais leem.
- `tools/mcr/layout.py` — fonte única de endereço; três tasks dependem dele.
- `tests/CMakeLists.txt` — a MCR-TASK-10 mexe; ninguém mais.
- `CLAUDE.md`, `NOTICE.md` — MCR-TASK-02 e MCR-TASK-14.

---

## Antecipação

A **MCR-TASK-13 pode ser antecipada** assim que a 09 fechar, e deve: ela precisa
do leitor, não da UI, e o veredito do `0x6500` decide se a tela da MCR-TASK-12
tem um campo "capitão" ou seis cobradores. É o padrão que o `01-executar.md` já
autoriza — tarefa de fase adiante de que uma tarefa da fase corrente precisa.

---

## Verificações específicas por fase

- **Fase 0** — `grep -rn 'port-mcr' docs/prompts/0*.md docs/prompts/geral.md
  .claude/commands` vazio: o **rito** não conhece ciclo pelo nome. As duas
  regras de `.claude/rules/` e este perfil **citam** `port-mcr`, e devem —
  convenção sem caso concreto vira prosa, e elas já nomeiam `PES2` e `WTE` do
  mesmo jeito. `/executar` sem argumento escolhe a mesma task de antes;
  `pip freeze` do venv no Log.
- **Fase 1** — todo módulo novo traz `self_check()` com **caso vermelho**; nenhum
  endereço fora de `layout.py`; round-trip nas duas formas; e **nada em
  português no módulo** — docstring, comentário, literal de prosa, mensagem de
  recusa e identificador local em en-US (§3.5). **Ao traduzir um módulo que já
  tem `self_check`, traduza o trecho esperado junto com a mensagem** — o
  `recusa()` casa substring, e traduzir um lado só deixa o gate verde por
  acidente; foi o que a [CORR-MCR-007](/docs/tasks/port-mcr/CORR-MCR-007.md)
  mediu, replantando os cinco controles negativos.
  **E toda checagem de round-trip precisa de uma companheira que prove que o
  escritor rodou.** Na MCR-TASK-09 o laço de `Save.write` trocado por
  `range(0)` deixou o `model.py` **verde**: escrever ninguém não muda byte
  nenhum, e "não mudou byte" é exatamente o que o round-trip pergunta. Só a
  injeção do `mcrio.py` pegou. O par é: round-trip idêntico **mais** uma
  edição que tem de reaparecer na releitura.
  **O módulo de I/O chama-se `mcrio.py`, não `io.py`** — com `tools/mcr` na
  frente do `sys.path`, `import io` devolve o da stdlib, que o CPython cacheia
  antes de qualquer código nosso rodar; um `io.py` aqui roda como script e não
  é importável por ninguém. Medido na MCR-TASK-09, plano corrigido.
- **Fase 2** — máquina sem venv e sem fixture: `ctest -R mcr` = 1 passed, 2
  skipped. **E o harness não se confere com ele mesmo:** o controle
  `harness-counts-nothing` (o ramo de falha do `Checker.ok` virando `pass`)
  deixou as catorze corridas **verdes**, porque toda asserção do próprio
  harness é um `ok(...)`. O conserto é a única exceção do port a "não use
  `raise` num self-check": o `_checks` do `harness.py` levanta, e o guard
  externo conta por um caminho que o `ok` não percorre.
- **Fase 3** — captura de tela no `:98` no Log; o arquivo gravado pela UI passa
  no `mcr roundtrip`.
- **Fase 4** — os seis itens da definição de pronto, cada um com o comando que o
  reproduz.
