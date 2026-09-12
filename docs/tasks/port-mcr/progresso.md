# Progresso — port em Python do editor de `.mcr` do WE2002

Rastreamento das tasks de [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md), que é
a fonte de verdade do projeto. Este arquivo registra **andamento**; o plano
registra **objetivo e critério**. Divergência entre os dois se resolve a favor
do plano.

**Pasta deste ciclo:** `docs/tasks/port-mcr/`. Todos os caminhos deste arquivo
e das tasks ao lado dele saem daqui, e é o nome desta pasta que os comandos
recebem como argumento (`/executar port-mcr`). Sem argumento, os comandos
continuam lendo `docs/tasks/` raso — o ciclo de PES2 —, exatamente como antes.

**Perfil deste ciclo:** [`/docs/prompts/perfil-mcr.md`](/docs/prompts/perfil-mcr.md).

**Prefixo dos IDs:** `MCR-TASK-`. O pool de correções é `CORR-MCR-`, declarado
em [`/docs/tasks/port-mcr/correcoes-progresso.md`](/docs/tasks/port-mcr/correcoes-progresso.md).

**Projeto separado do `newWe2002`, do `wte/` e do PES2.** Não compartilha build
nem código: `tools/mcr/` é Python 3 puro, e a UI é PySide6 num venv. O que
compartilha é **conhecimento de formato** — os 17 destinos medidos em
[`../wte/re/mcr.md`](../../../wte/re/mcr.md) e o codec de 12 bytes de
`src/core/Player.cpp`, que a §1.4 do plano mostra ser o mesmo do upstream. A
§0 do plano **proíbe** estender o `we2002_core`; o que for compartilhado é
copiado com atribuição no comentário.

**Este ciclo nasce em 2026-09-07**, a pedido do usuário, a partir do
[`zetaprog/Easy-Mcr-Winning-Eleven-2002-PS1`](https://github.com/zetaprog/Easy-Mcr-Winning-Eleven-2002-PS1)
(VB.NET, sem licença, SHA `30af1fe5`). A decisão de **portar literalmente** é
do dono do repositório, tomada com o aviso de licença na mesa; a §2 do plano
registra a diferença de método para o ciclo `wte/`, onde se recusou transcrição
por princípio.

## Resumo

| ID | Tarefa | Fase | Dependências | Status | Concluída em | Revisado em |
| -- | ------ | ---- | ------------ | ------ | ------------ | ----------- |
| [MCR-TASK-01](/docs/tasks/port-mcr/01-ciclo-em-subpasta.md) | O ciclo em subpasta — o Passo 0 agnóstico nos prompts e wrappers | 0 | — | ✅ Concluído | 2026-09-07 | 2026-09-07 |
| [MCR-TASK-02](/docs/tasks/port-mcr/02-base-legal-e-linhagem.md) | Base legal, linhagem e o SHA fixado do upstream | 0 | 01 | ✅ Concluído | 2026-09-07 | 2026-09-07 |
| [MCR-TASK-03](/docs/tasks/port-mcr/03-ambiente-fixture-e-qt.md) | A fixture nomeada, o venv e o binding Qt | 0 | 01 | ✅ Concluído | 2026-09-07 | 2026-09-07 |
| [MCR-TASK-04](/docs/tasks/port-mcr/04-conteiner-do-cartao.md) | `card.py` — diretório, blocos, quadros, checksum e as recusas | 1 | 03 | ✅ Concluído | 2026-09-07 | 2026-09-07 |
| [MCR-TASK-05](/docs/tasks/port-mcr/05-layout-e-cross-check.md) | `layout.py` e o cross-check dos 17 destinos | 1 | 04 | ✅ Concluído | 2026-09-07 | 2026-09-07 |
| [MCR-TASK-06](/docs/tasks/port-mcr/06-codec-de-atributos.md) | `attributes.py` × `Player::Decode/Encode` | 1 | 05 | ✅ Concluído | 2026-09-07 | 2026-09-07 |
| [MCR-TASK-07](/docs/tasks/port-mcr/07-dorsais-e-nome.md) | `numbers.py` e `text.py` — os 5 bits e o cp932 | 1 | 05 | ✅ Concluído | 2026-09-07 | 2026-09-07 |
| [MCR-TASK-08](/docs/tasks/port-mcr/08-formacao-e-dominios.md) | `formation.py` e `domains.py` — X/Y/papéis, cobradores, presets | 1 | 05 | ✅ Concluído | 2026-09-07 | 2026-09-07 |
| [MCR-TASK-09](/docs/tasks/port-mcr/09-modelo-e-round-trip.md) | `model.py`, `mcrio.py` e o round-trip byte-idêntico | 1 | 06, 07, 08 | ✅ Concluído | 2026-09-08 | 2026-09-08 |
| [MCR-TASK-10](/docs/tasks/port-mcr/10-selftest-cli-e-gate.md) | `selftest.py`, o CLI e os três alvos de `ctest` — **fecha a Fase 1** | 2 | 09 | ✅ Concluído | 2026-09-08 | 2026-09-08 |
| [MCR-TASK-11](/docs/tasks/port-mcr/11-ui-leitura.md) | A casca Qt: janela, elenco, ficha em leitura | 3 | 10 | ✅ Concluído | 2026-09-08 | 2026-09-08 |
| [MCR-TASK-12](/docs/tasks/port-mcr/12-ui-gravacao.md) | Gravação pela UI: ficha, formação, dorsais | 3 | 11 | ✅ Concluído | 2026-09-08 | 2026-09-08 |
| [MCR-TASK-13](/docs/tasks/port-mcr/13-oraculo-e-veredito.md) | O oráculo do Obocaman: o `0x6500`, o nome cheio, o veredito do console | 3 | 09 | ✅ Concluído | 2026-09-08 | 2026-09-08 |
| [MCR-TASK-14](/docs/tasks/port-mcr/14-verificacao-final.md) | Verificação final contra a definição de pronto | 4 | 12, 13 | ✅ Concluído | 2026-09-08 | 2026-09-08 |
| [MCR-TASK-15](/docs/tasks/port-mcr/15-abrir-cartao-pela-tela.md) | Abrir cartão pela tela: a janela sobe primeiro, e o Open é ação visível | 5 | 12 | ✅ Concluído | 2026-09-09 | 2026-09-09 |
| [MCR-TASK-16](/docs/tasks/port-mcr/16-conteiner-gme.md) | Abrir e gravar `.gme`: o contêiner do DexDrive, nos dois sentidos | 5 | 15 | ✅ Concluído | 2026-09-09 | 2026-09-09 |
| [MCR-TASK-17](/docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md) | Onde o option file guarda os times secretos e a Master League no modo exibição | 5 | 09 | ✅ Concluído | 2026-09-10 | 2026-09-10 |

**Legenda:** ⬜ Pendente · 🔄 Em andamento · ✅ Concluído · ❌ Bloqueado · ⏭️ Pulado

**Concluída em** é a data em que a task passou a ✅; **Revisado em** é a data em
que o `/revisar` passou por ela. `⬜ pendente` na segunda coluna significa que a
revisão ainda não aconteceu.

---

## Grafo de dependências

```text
01 (Passo 0)
 ├── 02 base legal
 └── 03 ambiente ── 04 card.py ── 05 layout.py ─┬── 06 attributes ─┐
                                                ├── 07 numbers+text ┼── 09 model + round-trip
                                                └── 08 formation+dom ┘        │
                                                                     10 selftest + gate
                                                        ┌────────────────────┴────────────┐
                                                  11 UI leitura                     13 oráculo
                                                        │                                │
                                                  12 UI gravação                         │
                                                        └────────── 14 fechamento ────────┘
```

**A 13 pode ser antecipada** assim que a 09 fechar: ela precisa do leitor, não
da UI, e o veredito do `0x6500` muda o que a 12 desenha na tela.

**A 15 pendura na 12**, e só nela: ela mexe na porta de leitura da janela e
no estado vazio, e o que precisa estar de pé é a tela que grava.

---

## Checklist por fase

### Fase 0 — o ciclo e o ambiente

- [x] MCR-TASK-01 — o Passo 0 nos 5 prompts e nos 5 wrappers, sem citar o nome
      deste ciclo em nenhum deles
- [x] MCR-TASK-02 — linhagem no `NOTICE.md`, SHA fixado, inventário do upstream
- [x] MCR-TASK-03 — fixture nomeada, venv com PySide6, versões registradas

### Fase 1 — o núcleo

- [x] MCR-TASK-04 — `card.py`, com as recusas
- [x] MCR-TASK-05 — `layout.py`, 17/17
- [x] MCR-TASK-06 — `attributes.py`, 0 divergências
- [x] MCR-TASK-07 — `numbers.py` e `text.py`, 23/23 e cp932
- [x] MCR-TASK-08 — `formation.py` e `domains.py`
- [x] MCR-TASK-09 — `model.py`, `mcrio.py`, round-trip nas duas formas

### Fase 2 — o gate

- [x] MCR-TASK-10 — `selftest`, CLI, `mcr_selftest`/`mcr_card`/`mcr_ui`

### Fase 3 — a UI e o oráculo

- [x] MCR-TASK-11 — leitura na tela
- [x] MCR-TASK-12 — gravação pela tela
- [x] MCR-TASK-13 — o `0x6500` respondido com valor medido

### Fase 4 — fechamento

- [x] MCR-TASK-14 — a definição de pronto do plano, item por item

### Fase 5 — pedidos posteriores ao fechamento

Aberta em **2026-09-09**, a pedido do usuário. A Fase 4 fechou a definição
de pronto do plano e continua fechada; o que entra aqui é **escopo novo**,
não reabertura — e por isso ganha fase própria em vez de uma linha a mais na
Fase 3, que já foi revisada.

- [x] MCR-TASK-15 — a janela sobe sem cartão, e abrir um `.mcr` do
      computador é botão e item de menu, não um diálogo que se antecipa
      à janela
- [x] MCR-TASK-16 — `.gme`, `.mcr` e `.mcd` como três embalagens do mesmo
      cartão: qualquer uma abre, qualquer uma grava, e a conversão entre
      elas não perde byte
- [x] MCR-TASK-17 — `0x02184..0x02185`, dezesseis bits: os nove times, a opção
      de Master League no bit 8 e o World A.S. no bit 10. Mais a verificação
      que precisa ser refeita para o jogo aceitar o cartão. O mapa está em
      [`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md)

---

## Decisões já tomadas

| Decisão | Quando | Onde está registrada |
|---|---|---|
| Portar o upstream **literalmente**, ciente de que ele não tem licença | 2026-09-07, pelo usuário | §2 do plano |
| O fonte VB **não entra no git** — clone em `work/easy-mcr/`, SHA fixado | 2026-09-07 | §2 do plano |
| UI Qt **separada do núcleo**; núcleo não importa Qt | 2026-09-07, pelo usuário | §3.3 do plano, Regra 3 |
| **PySide6 em venv**, não apt — o Python desta máquina é duplo | 2026-09-07 | §4 do plano |
| Tática **somente leitura** na v1 | 2026-09-07 | §1.9 e §5.6 do plano |
| O ciclo vive em subpasta, e os comandos a recebem por argumento | 2026-09-07, pelo usuário | MCR-TASK-01 |

---

## Armadilhas herdadas

As oito da §8 do plano. As três que mordem primeiro:

1. **O Python é duplo** — `apt install python3-pyqt6` instala para o 3.12 e
   fica invisível para o 3.13 do `PATH`. Falha em verde.
2. **O nome de 10 bytes é cp932**, e o `KanjiToAscii` do `we2002_core` o apaga.
3. **Escrever abaixo de `0x800` destrói o cartão** — é o que o upstream faz, e
   o port recusa.

---

## Estado medido, herdado do diagnóstico

Medido em 2026-09-07 contra `work/entrada.mcr` (131.072 B, `BISLPM-86600WEW-OPT`).

| Eixo | Estado |
| --- | --- |
| Cartão | 131.072 B, magic `MC`, entrada 1 do diretório `51 00 00 00 / 00 40 00 00 / 01 00`. SHA-256 `e53f4895affe075bced499a32ba736d10a20f72b010c9c8c05c1269e77c47546` — **é este cartão que os números abaixo medem**; o ciclo `wte/` usa o mesmo arquivo como fixture dele e o cabeçalho da `golden-13-roundtrip` manda regerá-lo de `work/saida.mcr`, então confira o digest antes de tratar uma divergência como bug |
| Cadeia do save | quadros **1 e 2** (`0x51` + `0x53`), 16.384 B declarados, primeiro bloco em `0x2000`. O `link` é **0-based sobre os blocos de dados**: o quadro 1 tem link `1` e aponta para o quadro 2 — lido como número de quadro, aponta para si mesmo. Os 16 checksums XOR batem |
| Dado fora da cadeia | o bloco 3 tem **41 bytes não-zero** e o diretório o marca `0xA0`, livre — é onde ficam formação, cobradores e tática. `tools/mcr/card.py <cartão> --blocks` |
| Registro de jogador | `0x5904`, passo 32, 23 entradas — 12 B de atributo + 10 B de nome + 10 B intocados |
| Dorsais | `0x5404`, 4 grupos de 4 B, 6 × 5 bits, deslocamentos `[0,5,2,7,4,1]`, guardado menos um |
| Dorsal duplo | **23 de 23** concordam entre o bit-field do registro e a tabela |
| Nome | **cp932**, não ASCII; os slots 5 e 20 usam os 10 bytes sem terminador |
| Formação | X `0x62A8`, Y `0x62B2`, papéis `0x63D5` (índice + 2, sobre 20 rótulos) |
| Cobradores | `0x614F, 0x6140, 0x6122, 0x6113, 0x6131` — tabela não-crescente; valem `[7,7,8,7,7]`. Nessa ordem são **SF, LF, RC, LC, PK**, medido na MCR-TASK-13 |
| `0x6500` | vale `8` e é o **capitão** — medido na MCR-TASK-13. Dirigindo as seis colunas da `malla2` do oráculo em seis linhas distintas, os cinco cobradores saem `0,1,2,3,4` e este byte sai `5`; o rótulo do sexto marcador é `Captain` e o local do upstream chama-se `CP`. Domínio `0..10` — o onze inicial, não os 23 slots. `bash wte/tools/golden_run_wte.sh tools/mcr/oracle/13-seis-linhas.txt work/wte-japanese-shift-jis.bin` |
| Tática | `0x64E2 = 1`, `0x6102 = 51`, nibbles `0/14` e `4/9` — escrita e nunca lida pelo original |
| Codec de atributos | o mesmo de `src/core/Player.cpp`, campo por campo |
| Round-trip | **0 bytes** de diferença nas duas formas da §5.1 — ler→gravar e ler→decodificar os 23→re-codificar→gravar. `python3 tools/mcr/mcrio.py <cópia> --roundtrip` |
| Controles negativos | **todos vermelhos**, com e sem fixture. Quantos são, e de que tipo, é a última linha de `python3 tools/mcr/controls.py` — hoje `controls: 25 of 25 red (24 substitutions, 1 new file)`, e o número sobe a cada task que acrescenta um. O `controls.py --self-check` varre este arquivo e o perfil e recusa total copiado que não bate ([CORR-MCR-021](/docs/tasks/port-mcr/CORR-MCR-021.md)) |
| Gravação pela tela | um atributo pelo spin box move **1 byte** (`0x0590d`, dentro dos 12 do registro do jogador 0); o arraste levou o jogador de linha 1 de `[11, 32]` a `[14, 43]` em unidades do cartão; os dois cartões gravados passam nas duas formas do round-trip. `WE2002_MCR_CARD=$PWD/work/entrada.mcr python3 tools/mcr/ui_check.py` |
| Edição de um atributo | move **1 byte** (`0x0590D`, dentro dos 12 do registro do jogador 0); um dorsal move **2** (`0x05404` e `0x05907`), que são as duas cópias da §1.5. `--edit-probe` |
| Abertura pela tela | a janela sobe **sem cartão**, mostrando a página vazia e um botão `Open card...` atrás da mesma ação do `File > Open card...` (`Ctrl+O`); diálogo cancelado não muda nada, arquivo que não é cartão é recusado e a janela continua abrindo no clique seguinte, e edição não gravada só se perde depois de uma pergunta (`asked=0` com o descarte recusado). `WE2002_MCR_CARD=$PWD/work/entrada.mcr python3 tools/mcr/ui_check.py` |
| Contêiner | três embalagens do mesmo cartão: `.mcr` e `.mcd` são o dump cru de 131.072 B, `.gme` põe **3.904** de cabeçalho na frente e o `MC` cai em 3904. A leitura decide **por conteúdo**, a gravação pela extensão do destino. Dos oito `.gme` de `mcr/`, **cinco** trazem `123-456-STD` e três trazem 3.904 zeros; `0x16..0x24` espelham os quinze estados do diretório nos cinco assinados. `.gme` → cartão → `.gme` dá o mesmo arquivo em **8 de 8** preservando o cabeçalho e em **2 de 8** sintetizando — só `0x27..0x34` separa os outros três, e esses bytes não são entendidos. `python3 tools/mcr/gme.py --check` |
| Upstream | SHA `30af1fe5`, sem licença, 5 commits em 2026-05-27 |

---

## Notas de execução

*(preenchido conforme as tasks forem executadas)*
