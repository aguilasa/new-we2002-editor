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
| [MCR-TASK-02](/docs/tasks/port-mcr/02-base-legal-e-linhagem.md) | Base legal, linhagem e o SHA fixado do upstream | 0 | 01 | ✅ Concluído | 2026-09-07 | ⬜ pendente |
| [MCR-TASK-03](/docs/tasks/port-mcr/03-ambiente-fixture-e-qt.md) | A fixture nomeada, o venv e o binding Qt | 0 | 01 | ⬜ Pendente | — | — |
| [MCR-TASK-04](/docs/tasks/port-mcr/04-conteiner-do-cartao.md) | `card.py` — diretório, blocos, quadros, checksum e as recusas | 1 | 03 | ⬜ Pendente | — | — |
| [MCR-TASK-05](/docs/tasks/port-mcr/05-layout-e-cross-check.md) | `layout.py` e o cross-check dos 17 destinos | 1 | 04 | ⬜ Pendente | — | — |
| [MCR-TASK-06](/docs/tasks/port-mcr/06-codec-de-atributos.md) | `attributes.py` × `Player::Decode/Encode` | 1 | 05 | ⬜ Pendente | — | — |
| [MCR-TASK-07](/docs/tasks/port-mcr/07-dorsais-e-nome.md) | `numbers.py` e `text.py` — os 5 bits e o cp932 | 1 | 05 | ⬜ Pendente | — | — |
| [MCR-TASK-08](/docs/tasks/port-mcr/08-formacao-e-dominios.md) | `formation.py` e `domains.py` — X/Y/papéis, cobradores, presets | 1 | 05 | ⬜ Pendente | — | — |
| [MCR-TASK-09](/docs/tasks/port-mcr/09-modelo-e-round-trip.md) | `model.py`, `io.py` e o round-trip byte-idêntico | 1 | 06, 07, 08 | ⬜ Pendente | — | — |
| [MCR-TASK-10](/docs/tasks/port-mcr/10-selftest-cli-e-gate.md) | `selftest.py`, o CLI e os três alvos de `ctest` — **fecha a Fase 1** | 2 | 09 | ⬜ Pendente | — | — |
| [MCR-TASK-11](/docs/tasks/port-mcr/11-ui-leitura.md) | A casca Qt: janela, elenco, ficha em leitura | 3 | 10 | ⬜ Pendente | — | — |
| [MCR-TASK-12](/docs/tasks/port-mcr/12-ui-gravacao.md) | Gravação pela UI: ficha, formação, dorsais | 3 | 11 | ⬜ Pendente | — | — |
| [MCR-TASK-13](/docs/tasks/port-mcr/13-oraculo-e-veredito.md) | O oráculo do Obocaman: o `0x6500`, o nome cheio, o veredito do console | 3 | 09 | ⬜ Pendente | — | — |
| [MCR-TASK-14](/docs/tasks/port-mcr/14-verificacao-final.md) | Verificação final contra a definição de pronto | 4 | 12, 13 | ⬜ Pendente | — | — |

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

---

## Checklist por fase

### Fase 0 — o ciclo e o ambiente

- [x] MCR-TASK-01 — o Passo 0 nos 5 prompts e nos 5 wrappers, sem citar o nome
      deste ciclo em nenhum deles
- [x] MCR-TASK-02 — linhagem no `NOTICE.md`, SHA fixado, inventário do upstream
- [ ] MCR-TASK-03 — fixture nomeada, venv com PySide6, versões registradas

### Fase 1 — o núcleo

- [ ] MCR-TASK-04 — `card.py`, com as recusas
- [ ] MCR-TASK-05 — `layout.py`, 17/17
- [ ] MCR-TASK-06 — `attributes.py`, 0 divergências
- [ ] MCR-TASK-07 — `numbers.py` e `text.py`, 23/23 e cp932
- [ ] MCR-TASK-08 — `formation.py` e `domains.py`
- [ ] MCR-TASK-09 — `model.py`, `io.py`, round-trip nas duas formas

### Fase 2 — o gate

- [ ] MCR-TASK-10 — `selftest`, CLI, `mcr_selftest`/`mcr_card`/`mcr_ui`

### Fase 3 — a UI e o oráculo

- [ ] MCR-TASK-11 — leitura na tela
- [ ] MCR-TASK-12 — gravação pela tela
- [ ] MCR-TASK-13 — o `0x6500` respondido com valor medido

### Fase 4 — fechamento

- [ ] MCR-TASK-14 — a definição de pronto do plano, item por item

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
| Cartão | 131.072 B, magic `MC`, entrada 1 do diretório `51 00 00 00 / 00 40 00 00 / 01 00` |
| Registro de jogador | `0x5904`, passo 32, 23 entradas — 12 B de atributo + 10 B de nome + 10 B intocados |
| Dorsais | `0x5404`, 4 grupos de 4 B, 6 × 5 bits, deslocamentos `[0,5,2,7,4,1]`, guardado menos um |
| Dorsal duplo | **23 de 23** concordam entre o bit-field do registro e a tabela |
| Nome | **cp932**, não ASCII; o slot 20 usa os 10 bytes sem terminador |
| Formação | X `0x62A8`, Y `0x62B2`, papéis `0x63D5` (índice + 2, sobre 20 rótulos) |
| Cobradores | `0x614F, 0x6140, 0x6122, 0x6113, 0x6131` — tabela não-crescente; valem `[7,7,8,7,7]` |
| `0x6500` | vale `8` — **capitão** pela nossa RE, "sexto cobrador" pelo upstream. Em aberto |
| Tática | `0x64E2 = 1`, `0x6102 = 51`, nibbles `0/14` e `4/9` — escrita e nunca lida pelo original |
| Codec de atributos | o mesmo de `src/core/Player.cpp`, campo por campo |
| Upstream | SHA `30af1fe5`, sem licença, 5 commits em 2026-05-27 |

---

## Notas de execução

*(preenchido conforme as tasks forem executadas)*
