---
id: LOOKS-TASK-07
title: "`oracle.py` — o emulador por MCP e a rota até a tela `LOOKS SET`"
type: implementação
category: oráculo
phase: 2
depends_on: ["LOOKS-TASK-06"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §1.11"
status: pendente
---

# LOOKS-TASK-07: O oráculo, e a rota que falta

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §1.11 e
  §5.2.
- **Há dois save states prontos, e eles substituem a rota.** O usuário gravou
  em 2026-09-14, com o jogo na tela de edição:

  | slot | arquivo | mostra |
  |---|---|---|
  | 1 | `…/duckstation-mcp/savestates/SLPM-87056_1.sav` | **goleiro** |
  | 2 | `…/duckstation-mcp/savestates/SLPM-87056_2.sav` | **jogador de linha** |

  Os dois carregam `C:\games\ps1\work\we2002-english.cue` — conferido por
  dentro do arquivo, no campo `media`. O emulador sobe por
  `.\make.ps1 we2002-play`, que já tem a inglesa como default.
- **O ganho não é economizar cliques, é o baseline.** `load_state` devolve um
  estado **byte a byte idêntico** antes de cada medição, e é isso que faz o
  diff das tasks 08, 09 e 12 medir só o campo que mudou, em vez de medir
  também tudo que o jogo mexeu no caminho.
- Molde pronto: as rotas nomeadas de `tools/pes2/mcp_drive.py` (`route_title`,
  `route_main_menu`, `route_edit`), que esperam pela assinatura do quadro e não
  pelo relógio.
- **Bote o disco inglês** — menus legíveis, geometria idêntica (§1.3).

---

## Objetivo

`tools/looks/oracle.py`: subir o emulador, chegar à tela `LOOKS SET` sozinho, e
oferecer as operações que as tasks 08 e 09 vão usar — ler RAM, capturar quadro,
trocar o valor de um campo.

---

## Critério de conclusão

- [ ] `load_looks(slot)` carrega o state e **confere que chegou** — pela
      assinatura do quadro, não pelo relógio.
- [ ] Os dois slots são usados, e o que cada um mostra fica registrado: 1 é
      goleiro, 2 é jogador de linha.
- [ ] **O `media` de dentro do state é conferido** antes de confiar nele. O
      nome do arquivo usa o serial **japonês** (`SLPM-87056`) mesmo no disco
      inglês, então o nome não diz de que disco o state veio — um state feito
      na japonesa teria exatamente o mesmo nome, e traria os menus ilegíveis.
- [ ] Os dois `.sav` são **copiados para um caminho do projeto** e apontados por
      variável. O diretório de states é compartilhado com o trabalho de PES2, e
      slot nu é sobrescrevível por acidente.
- [ ] Fica registrado que o state amarra **imagem e build do emulador**: se um
      dos dois mudar, ele pode não carregar, e aí a rota manual volta a ser
      necessária.
- [ ] **Círculo confirma e precisa de pelo menos 8 frames.** Com 3 o jogo não
      registra e a tela fica igual, o que parece botão errado. Fica no código,
      não em comentário solto.
- [ ] **Uma tecla de cada vez.** Nada de laço de confirmação — a regra do
      [CLAUDE.md](../../../CLAUDE.md) custou uma corrida no ciclo `wte/`.
- [ ] `verify_load()` reconfere a §5.2: RAM em `0x8011C000` e `0x8016E800` byte
      a byte igual ao disco. É a amarra entre arquivo e tela.
- [ ] **A RAM se lê por MCP vivo, não por arquivo de state.** Medido em
      2026-09-14: o `tools/pes2/savestate.py` lê o cabeçalho e **não alcança a
      RAM nesta máquina** — ele chama o CLI `zstd`, que não está no `PATH`, e o
      módulo `zstandard` também não está instalado. O erro é um
      `FileNotFoundError [WinError 2]` depois de imprimir o cabeçalho, que não
      menciona `zstd` em lugar nenhum.
- [ ] Sem emulador, ou sem os states, **pula** (77) com a mensagem dizendo o
      que falta.

---

## Log de Execução

*(preencher ao executar)*
