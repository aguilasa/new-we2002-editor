---
id: MCR-TASK-10
title: "`selftest.py`, o CLI e os três alvos de `ctest` — fecha a Fase 1"
type: ferramenta
category: ferramental
phase: 2
depends_on: ["MCR-TASK-09"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §5.2"
status: concluído
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

- [x] `tools/mcr/selftest.py` monta um cartão sintético em memória e agrega os
      `self_check()` dos módulos — **sem depender da fixture e sem Qt**.
- [x] As duas guardas da Regra 3: `ui/*.py` não importa `layout`/`card`/`mcrio`,
      e `"PySide6" not in sys.modules` depois de importar o núcleo inteiro.
- [x] **O módulo de I/O chama-se `mcrio.py`, não `io.py`**, e o agregador tem de
      importá-lo por esse nome. A §3.2 do plano dizia `io.py`, e a MCR-TASK-09
      mediu que esse nome é inutilizável: com `tools/mcr` na frente do
      `sys.path`, `import io` devolve o da stdlib — que o CPython cacheia antes
      de qualquer código nosso rodar —, então um `io.py` aqui roda como script e
      **não é importável**. O plano já foi corrigido; a asserção que o prova
      mora no `self_check` do `mcrio.py`.
- [x] **São doze módulos com `self_check()`**: os nove do núcleo (`card`,
      `layout`, `attributes`, `numbers`, `text`, `domains`, `formation`,
      `model`, `mcrio`) mais os três que esta task criou — `harness`,
      `glossary` e `controls`. O `mcrio` é o único que roda o controle negativo
      da §5.2 inteiro (`--negative`, 5/5); o `controls` roda os controles
      negativos — quantos são é o que ele imprime.
- [x] **A guarda da Regra 1 já existe e precisa ser agregada aqui**: a
      MCR-TASK-05 a escreveu como `layout.address_monopoly()`, com CLI
      `python3 tools/mcr/layout.py --rule1`. Ela varre `tools/mcr/**.py` (menos
      o próprio `layout.py`; recursiva desde a
      [CORR-MCR-014](/docs/tasks/port-mcr/CORR-MCR-014.md)) atrás de literal hexadecimal dentro de
      `0x4000..0x8000` **e** dos mesmos endereços em decimal — o upstream
      escreve `22788` e `21508`, que passariam batido por varredura só de hex.
      Hoje devolve **0**; o `selftest` tem de chamá-la, não reimplementá-la.
- [x] **O `attempt()` está em `card.py`, `layout.py` e `attributes.py`**, e o
      `refuses()`/`recusa()` em dois deles. A MCR-TASK-04 mediu por que o
      primeiro existe (sem ele, o defeito que levanta exceção mata a corrida e
      esconde os checks seguintes) e a MCR-TASK-06 mediu por que o segundo
      também: um `try/except ErroEspecífico` escrito à mão deixa passar
      **qualquer outra** exceção, e foi o que aconteceu ao plantar o swap da
      v4.2 — o self-check morreu no meio e três checks não rodaram. A terceira
      cópia já nasceu; **escolha uma casa só para os dois** ao montar o
      `selftest`.
- [x] **`layout.find_upward()` é o resolvedor compartilhado de caminho**, e a
      MCR-TASK-08 o hasteou para lá depois de o mesmo defeito aparecer três
      vezes: `layout.py` (o `mcr.md`), `attributes.py` e `domains.py` (o clone
      do upstream) localizavam o alvo contando saltos de `dirname` a partir de
      `__file__`. Uma cópia do módulo um diretório mais raso — que é o que todo
      controle negativo é — aponta para lugar nenhum, e o check **pula** em vez
      de falhar. Use-o em qualquer módulo novo que precise achar algo fora de
      `tools/mcr/`.
- [x] **A varredura da Regra 1 tokeniza, não greppeia.** Desde a MCR-TASK-08 a
      `address_monopoly()` ignora comentários, literais de string e os tokens
      de f-string (`FSTRING_MIDDLE`, novos no 3.12 — sem eles a prosa dentro de
      um `print` f-string é lida como código). O motivo: um módulo tem de poder
      nomear na própria documentação o endereço sobre o qual ele opera, e o
      `formation.py` nomeia onze. Ao mexer nela, replante uma constante de
      verdade e confira que continua vermelha.
- [x] **O harness precisa de um guard EXTERNO, não só de helpers.** Cinco vezes
      neste ciclo um `ok(...)` cuja expressão levanta matou a corrida e
      escondeu os checks seguintes — MCR-TASK-04 (`find_save`), MCR-TASK-06
      (o `try/except` de recusa), e três vezes na MCR-TASK-07 (`encode_table`,
      `read_all`, `decode_name`). Passar cada chamada por `attempt()` conserta
      **uma de cada vez** e a sexta volta. O conserto durável é envolver o
      corpo inteiro do `self_check` de modo que qualquer exceção que escape
      vire uma falha nomeada e a contagem final ainda saia. Faça isso no
      harness compartilhado, e os cinco módulos herdam.
- [x] **O `selftest` importa `layout` dentro do `attempt()`**, não no escopo do
      módulo: as vistas nomeadas do `layout.py` levantam `LayoutError` no
      import quando um destino some, e o `mcr_selftest` é o gate
      **obrigatório** — uma tabela quebrada tem de virar uma falha nomeada
      entre as demais, não um traceback que derruba a corrida inteira. Medido
      na [CORR-MCR-008](/docs/tasks/port-mcr/CORR-MCR-008.md): nos dois
      controles que tiram um destino, o `layout.py --self-check` sai por
      traceback com **0** das 29 asserções rodadas. É a mesma lição que a
      MCR-TASK-04 pagou e que vale para as tasks 05 a 10.
- [x] `cli.py` com `info`, `dump`, `get`, `set`, `roundtrip`, `negative` e
      `check`, saída determinística.
- [x] **Decidir se o `negative` planta os controles em vez de descrevê-los.**
      Hoje o estímulo de cada controle mora em prosa numa tabela de Log, e a
      [CORR-MCR-009](/docs/tasks/port-mcr/CORR-MCR-009.md) mediu o custo disso:
      duas das cinco contagens da MCR-TASK-06 não reproduziam a partir da
      descrição, porque "trocar dois campos no encoder" tem mais de uma
      leitura. Como subcomando — plantar a substituição, rodar, exigir o
      vermelho e a contagem —, o número passa a ser **medido** em vez de
      anotado à mão. É a mesma regra que o `CLAUDE.md` já aplica aos golden:
      sem o estímulo versionado a corrida não é repetível. A decisão de fazê-lo
      agora é de quem executar esta task; o que não vale é deixá-la implícita.
- [x] `glossary.py` — o mapa `es → en` (§3.5), que até aqui não tinha task
      dona: `jugador→player`, `cancha→pitch`, `formacion→formation`,
      `grabar→write`, `bufersizenum→group_size`.
- [x] A varredura de idioma no `selftest`: **nenhum espanhol remanescente e
      nenhuma prosa portuguesa em `tools/mcr/**.py`**. Todo o código do port é
      **en-US** — docstrings, comentários, mensagens, `--help` e saída do CLI
      (§3.5). **A varredura nasce sem lista de exceção:** o `card.py` era a
      única, e a [CORR-MCR-007](/docs/tasks/port-mcr/CORR-MCR-007.md) a fechou
      em 2026-09-07, antes desta task.
- [x] Três alvos em `tests/CMakeLists.txt`: `mcr_selftest` (obrigatório),
      `mcr_card` (`WE2002_MCR_CARD`, skip 77) e `mcr_ui` (venv + `:98`, skip 77).
- [x] **Numa máquina sem venv e sem fixture**, `ctest -R mcr` reporta
      **1 passed, 2 skipped** — nunca `0 tests`, nunca erro.
- [x] `make test` continua verde.

---

## Log de Execução

**Executado em:** 2026-09-08

### Resumo do que foi feito

Seis módulos novos — `harness.py`, `glossary.py`, `controls.py`, `selftest.py`,
`cli.py` e `ui_check.py`, 1.222 linhas —, os nove do núcleo migrados para o
harness compartilhado, e os **três alvos de `ctest`** registrados. Numa máquina
sem cartão e sem UI, `ctest -R mcr` dá **1 passed, 2 skipped**; `make test` dá
**10 de 10**.

A decisão que a task pedia foi tomada: **o `negative` planta os controles**.
Eles moram em `controls.py` e o `mcr_selftest` os roda a cada corrida. **Na
data desta task eram quinze, 15/15 vermelhos**, com e sem fixture — catorze
até a [CORR-MCR-014](/docs/tasks/port-mcr/CORR-MCR-014.md), e dezesseis desde a
[MCR-TASK-11](/docs/tasks/port-mcr/11-ui-leitura.md). Os números abaixo são os
desta corrida; o de hoje é o que a última linha do comando imprime
([CORR-MCR-017](/docs/tasks/port-mcr/CORR-MCR-017.md)).

E o que a execução ensinou: **um harness não se confere com ele mesmo.**

### O harness, e o guard que os helpers não davam

Os três helpers estavam copiados em nove arquivos e já tinham divergido: o
`card.py` chamava o quarto argumento de `refuses` de `exception` e os outros de
`kind`. Essa é a razão barata.

A cara é o **guard externo**. O `attempt()` pega a exceção da chamada que você
**embrulhou** — um `ok(...)` cuja expressão levanta, um import no topo do corpo,
um helper chamado fora do `attempt` não estão cobertos. Foi o que aconteceu
cinco vezes neste ciclo, e a [CORR-MCR-008](/docs/tasks/port-mcr/CORR-MCR-008.md)
mediu a forma: com um destino removido, o `layout.py --self-check` saía por
traceback com **0 das 29** asserções rodadas. O `harness.run()` fecha isso — o
corpo roda dentro de um `try`, o que escapar vira **uma falha nomeada** com o
último quadro do traceback, e a contagem final ainda sai.

Migração conferida por contagem: os nove módulos têm **exatamente** os mesmos
checks de antes — card 27, layout 29, attributes 22, numbers 17, text 23,
domains 15, formation 25, model 19, mcrio 17 —, e os três novos somam 13, 10 e
**6** (era 5 até a [CORR-MCR-014](/docs/tasks/port-mcr/CORR-MCR-014.md), que
acrescentou ao `controls` a asserção de que o caminho de um controle criador
está livre).

### Um harness não se confere com ele mesmo

O controle `harness-counts-nothing` troca o ramo de falha do `Checker.ok` por
`pass`. Resultado da primeira corrida: **verde**. E não só o `harness.py` —
**as catorze corridas**, porque toda asserção de todo módulo é um `ok(...)`, e
um `ok` cego aprova a própria cegueira.

O conserto é a única exceção do port a "não use `raise` num self-check": o
`_checks` do `harness.py` monta um `Checker` de prova, reprova um check de
propósito, e **levanta** se a contagem não subir. O guard externo conta por um
caminho que o `ok` não percorre. Depois disso o controle fica vermelho.

Vale para quem escrever o próximo agregador: **toda ferramenta de medição
precisa de um caminho de detecção que não passe por ela mesma.**

### Os controles, agora por comando — quinze nesta corrida

```
$ python3 tools/mcr/controls.py
  RED    card-write-guard           card.py :: Card.write
  RED    card-size-guard            card.py :: Card.__init__
  RED    card-link-base             card.py :: DirectoryEntry.next_frame
  RED    attributes-bit-write       attributes.py :: encode_stream
  RED    numbers-bias               numbers.py :: encode_table
  RED    text-interior-nul          text.py :: decode_name
  RED    formation-screen-factor    formation.py :: write
  RED    domains-invented-label     domains.py :: HAIR_STYLE
  RED    layout-stray-address       formation.py :: module scope
  RED    model-write-nobody         model.py :: Save.write
  RED    model-half-number          model.py :: Save.set_number
  RED    mcrio-directory-guard      mcrio.py :: check_card
  RED    mcrio-readonly-guard       mcrio.py :: check_destination
  RED    harness-counts-nothing     harness.py :: Checker.ok
  RED    ui-below-the-sweep         ui/_probe.py :: a new file, one directory down
controls: 15 of 15 red
```

Cada um é **arquivo, função, linha exata e o que ela vira** — a forma que a
[CORR-MCR-009](/docs/tasks/port-mcr/CORR-MCR-009.md) exigiu depois de duas das
cinco contagens da MCR-TASK-06 não reproduzirem da prosa. Substituição que casa
zero ou duas vezes é reportada como **controle quebrado**, não como vermelho:
literal que não bate deixa a cópia intacta e a corrida sai verde pelo motivo
errado.

O sandbox leva `wte/re/mcr.md` e um symlink para `work/easy-mcr`, e o relatório
**conta os `skip`** de cada corrida — as duas metades da lição da MCR-TASK-08.
Sem fixture eles continuam todos vermelhos, e é por isso que o `mcr_selftest`
pode rodá-los sendo o alvo obrigatório.

**Um deles não é substituição — o `ui-below-the-sweep`, e é o único assim.** Ele **cria** um
arquivo — `ui/_probe.py`, uma pasta abaixo —, porque o defeito que ele mede é
uma pasta que a varredura não desce, e nenhuma troca de linha num módulo
existente exprime isso. "Casou uma vez" ali quer dizer que o caminho estava
livre e foi escrito; caminho ocupado é **controle quebrado**, do mesmo jeito
que um literal que casa duas vezes. E o espanhol que ele planta sai do
dicionário do `glossary.py` em tempo de execução, não de literal no
`controls.py` — escrito por extenso, ele faria o próprio catálogo tropeçar na
varredura que o controle existe para exercitar (medido: duas queixas sobre o
`controls.py`), e a saída fácil — pular o `controls.py` como o `glossary.py`
pula a si mesmo — deixaria um vazamento de verdade sem vigilância.

### Os três alvos, medidos

```
$ ctest --test-dir build -R mcr            # sem WE2002_MCR_CARD
100% tests passed, 0 tests failed out of 3
	 10 - mcr_card (Skipped)
	 11 - mcr_ui (Skipped)

$ WE2002_MCR_CARD=$PWD/work/entrada.mcr ctest --test-dir build -R mcr
100% tests passed, 0 tests failed out of 3
	 11 - mcr_ui (Skipped)

$ make test
100% tests passed, 0 tests failed out of 10
```

O `mcr_selftest` leva **~13 s** e não pede nada: cada módulo monta o cartão de
que precisa em memória, e o `selftest.py` **remove `WE2002_MCR_CARD` do
ambiente** antes de chamar qualquer um — o gate obrigatório tem de rodar igual
numa máquina que nunca viu cartão nenhum.

O `mcr_ui` já está registrado e pula com 77 dizendo `app.py does not exist yet
(MCR-TASK-11)`. O contrato que ele chama — `ui/app.py --smoke`, que abre a
janela, deixa o Qt pintar um quadro e sai com 0 — está escrito **no arquivo da
MCR-TASK-11**, não só aqui.

### A varredura de idioma

`glossary.py` tem três regras, e a terceira é a que não precisa de lista:
o espanhol do upstream palavra a palavra, uma lista curta de português de
prosa, e **qualquer letra latina acentuada**. Hoje: `0 complaint(s)`.

A terceira é a rede. Português e espanhol não andam três linhas sem um acento;
os literais japoneses do `text.py` e o sinal de euro estão fora do bloco
`U+00C0..U+024F`, então a rede não toca dado de teste legítimo — **conferido**,
não suposto: o `text.py` tem cinco linhas não-ASCII e a varredura fica muda.

**Duas varreduras sobre a mesma árvore com regras opostas sobre os mesmos
tokens.** A da Regra 1 **tokeniza** para poder ignorar comentário e string,
porque um módulo tem de poder nomear na documentação o endereço sobre o qual
opera. A de idioma **lê justamente** comentário e string, porque é onde a prosa
mora. Está dito nos dois arquivos, porque "unificar as duas" é uma ideia de
aparência natural que quebraria as duas.

### O CLI

`info`, `dump`, `get`, `set`, `roundtrip`, `negative` e `check`. O `set` passa
pelo `mcrio.check_destination` como tudo que grava: recusa a fixture sem
`--force` e recusa `roms/` **com ou sem**. Medido:

```
$ python3 tools/mcr/cli.py set <cópia> 0 technique 12
technique=12 on slot 0: 1 byte(s) moved
  0x0590d
$ python3 tools/mcr/cli.py roundtrip <cópia>
form 1: 0 byte(s) differ
form 2: 0 byte(s) differ
$ python3 tools/mcr/cli.py set work/entrada.mcr 0 technique 12
error: ... is the card named by WE2002_MCR_CARD ...    (rc=2)
```

`cli.py check` **é** o alvo `mcr_card`, e o 77 dele não é erro: é o que diz ao
ctest que o teste pulou. O último check dele relê o arquivo do disco e exige
que nada tenha mudado.

### Os gates da fase

| gate | resultado |
|---|---|
| `ctest -R mcr` sem cartão | **1 passed, 2 skipped** |
| `ctest -R mcr` com cartão | 2 passed, 1 skipped (`mcr_ui`) |
| `make test` | **10 de 10**, 0 falhas |
| `selftest.py` | 0 falhas em 12 módulos + regras de desenho + controles |
| `controls.py` | **15/15 vermelhos** nesta corrida, com e sem fixture |
| `glossary.py` | 0 queixas em `tools/mcr/**.py` |
| `layout.py --rule1` | 0 endereços fora de `layout.py` |
| Regra 3 | `PySide6` ausente; a metade da UI **pula dizendo** que a pasta não existe |
| `check_tasks.py` | 100 task(s), ok |
| fixture | `sha256 e53f4895…c47546`, intacta |

### Arquivos criados/modificados

- `tools/mcr/harness.py` — **novo**, os helpers e o guard externo
- `tools/mcr/glossary.py` — **novo**, o mapa es→en e a varredura de idioma
- `tools/mcr/controls.py` — **novo**, as 15 substituições literais e o motor
- `tools/mcr/selftest.py` — **novo**, o agregador (alvo `mcr_selftest`)
- `tools/mcr/cli.py` — **novo**, os sete subcomandos (alvo `mcr_card`)
- `tools/mcr/ui_check.py` — **novo**, o alvo `mcr_ui`
- os nove do núcleo — `card`, `layout`, `attributes`, `numbers`, `text`,
  `domains`, `formation`, `model`, `mcrio`: helpers locais trocados pelo
  harness, e os dois `try/except` escritos à mão do `layout.py` trocados por
  `refuses`
- `tests/CMakeLists.txt` — os três alvos
- `docs/PLAN-MCR-PY.md` — §3.2 com os três módulos que o esboço não tinha, e
  por que cada um nasceu
- `docs/prompts/perfil-mcr.md` — a tabela de gates, a estrutura, e a lição do
  harness na Fase 2
- `docs/tasks/port-mcr/11-ui-leitura.md` — o contrato `--smoke` e a varredura
  da Regra 3, escritos **na task de destino**
- `docs/tasks/port-mcr/progresso.md` — a linha desta task e o checklist

### Problemas encontrados

**1. O harness cego aprovou a si mesmo.** Detalhado acima. É o achado que vale
carregar: uma ferramenta de medição precisa de um caminho de detecção que não
passe por ela mesma.

**2. O cabeçalho saía duas vezes.** A migração deixou o `print("X.py
self-check")` no corpo, e o `harness.run()` também o imprime. Pego pela
primeira corrida do `selftest`, que mostrou os doze cabeçalhos em dobro.
Barato, mas é o tipo de coisa que sobrevive quando ninguém roda o agregador.

**3. O `card.py` passava a exceção por posição.** `refuses(..., CardError)` como
quarto argumento posicional colide com o `functools.partial(kind=...)` do
`refusing()`, e o `TypeError` que sai é `got multiple values for argument
'kind'`. **Quem o reportou foi o guard externo recém-escrito**, com arquivo,
linha e função — que é exatamente o que ele existe para fazer, na primeira
corrida em que existiu.

**4. A §3.5 do plano diz que `tests/CMakeLists.txt` é português, e ele é
inglês.** Os comentários do arquivo são ingleses desde antes deste ciclo (o
bloco de PES2 inteiro é), enquanto o `Makefile` é português de verdade. Segui o
idioma **de cada arquivo**, que é o que a regra quer dizer; a frase do plano é
que junta os dois indevidamente. Encaminhado para a MCR-TASK-14 pela linha no
quadro dela.
