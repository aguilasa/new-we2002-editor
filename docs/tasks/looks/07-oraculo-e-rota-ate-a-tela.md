---
id: LOOKS-TASK-07
title: "`oracle.py` — o emulador por MCP e a rota até a tela `LOOKS SET`"
type: implementação
category: oráculo
phase: 2
depends_on: ["LOOKS-TASK-06"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §1.11"
status: concluído
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

- [x] `load_looks(slot)` carrega o state e **confere que chegou** — pela
      assinatura do quadro, não pelo relógio.
- [x] Os dois slots são usados, e o que cada um mostra fica registrado: 1 é
      goleiro, 2 é jogador de linha.
- [x] **O `media` de dentro do state é conferido** antes de confiar nele. O
      nome do arquivo usa o serial **japonês** (`SLPM-87056`) mesmo no disco
      inglês, então o nome não diz de que disco o state veio — um state feito
      na japonesa teria exatamente o mesmo nome, e traria os menus ilegíveis.
- [x] Os dois `.sav` são **copiados para um caminho do projeto** e apontados por
      variável. O diretório de states é compartilhado com o trabalho de PES2, e
      slot nu é sobrescrevível por acidente.
- [x] Fica registrado que o state amarra **imagem e build do emulador**: se um
      dos dois mudar, ele pode não carregar, e aí a rota manual volta a ser
      necessária.
- [x] **Círculo confirma e precisa de pelo menos 8 frames.** Com 3 o jogo não
      registra e a tela fica igual, o que parece botão errado. Fica no código,
      não em comentário solto.
- [x] **Uma tecla de cada vez.** Nada de laço de confirmação — a regra do
      [CLAUDE.md](../../../CLAUDE.md) custou uma corrida no ciclo `wte/`.
- [x] `verify_load()` reconfere a §5.2: RAM em `0x8011C000` e `0x8016E800`
      contra o disco. É a amarra entre arquivo e tela.

      **E a §5.2 estava errada: não é byte a byte.** Medido em 2026-09-14 com o
      jogo na tela, 203 bytes do `EDT_MOD.BIN` e 20 do `MODEL.BIN` diferem — o
      jogo reescreve a geometria carregada. O que `verify_load()` **exige** é o
      que se sustenta e é o que distingue endereço certo de endereço errado: o
      cabeçalho e as listas de ponteiro idênticos, e **todo** byte divergente
      dentro de uma seção. A §5.2 foi corrigida no lugar, e o achado foi
      encaminhado para a
      [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md).
- [x] **A RAM se lê por MCP vivo, não por arquivo de state.** Medido em
      2026-09-14: o `tools/pes2/savestate.py` lê o cabeçalho e **não alcança a
      RAM nesta máquina** — ele chama o CLI `zstd`, que não está no `PATH`, e o
      módulo `zstandard` também não está instalado. O erro é um
      `FileNotFoundError [WinError 2]` depois de imprimir o cabeçalho, que não
      menciona `zstd` em lugar nenhum.
- [x] Sem emulador, ou sem os states, **pula** (77) com a mensagem dizendo o
      que falta.

---

## Log de Execução

**Executado em:** 2026-09-14

### Resumo do que foi feito

`tools/looks/oracle.py`: sobe o fork com MCP sobre o `.cue` inglês, **põe a
janela em −32000** antes de qualquer outra coisa, restaura um dos dois save
states, prova pelo quadro que chegou à tela `LOOKS SET` **e que é o state
certo**, compara a RAM dos dois arquivos de modelo contra o disco, e move um
campo com uma tecla. Sem emulador, sem os `.sav` ou sem a variável de disco,
**pula com 77** dizendo o que falta.

O que a task aprendeu, em ordem de importância:

### 1. A §5.2 do plano estava errada, e o erro é o achado

Ela prometia RAM **byte a byte** igual ao disco. Medido pela primeira vez, com
o jogo parado na tela:

```text
/BIN/EDT_MOD.BIN at 0x8011c000: 203 of 36072 byte(s) differ (99.44% equal), in section(s) 0, 3, 4, 5, 6, 7, 8, 9, 10
    every one of them at byte [2] of a 24-byte primitive
/BIN/MODEL.BIN at 0x8016e800: 20 of 64800 byte(s) differ (99.97% equal), in section(s) 24, 32
    every one of them at byte [1, 2, 5, 9] of a 24-byte primitive
```

**O jogo reescreve a geometria carregada**, e reescreve exatamente onde a
aparência moraria: cor de primitiva, nunca cabeçalho de seção, nunca a folga
entre duas. Três consequências:

- **`verify_load()` exige o que se sustenta**, e o que exige é o que separa
  endereço certo de endereço errado: cabeçalho e listas de ponteiro idênticos,
  e **todo** byte divergente dentro de uma seção varrida. Uma diferença no
  cabeçalho, ou na folga entre seções, é recusa — e as duas têm caso vermelho.
- **O `EDT_MOD.BIN` difere entre os dois states e o `MODEL.BIN` não**: 162
  corridas de diferença entre goleiro e jogador de linha no primeiro, **zero**
  no segundo. É evidência direta sobre a incógnita (a), e por isso está escrita
  **na** [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md), com a
  ressalva que a fase exige: isso diz quem é **reescrito**, ainda não quem é
  **desenhado**.
- A §5.2 foi **corrigida no lugar**, com o número medido e o comando que o
  remede.

E a §5.1, na mesma página, ainda dizia "`EDT_MOD.BIN` **11** terminando em
36.072" — o número que a [`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md)
derrubou na §1.5 três seções acima, e que sobreviveu ali porque ninguém releu a
§5. Corrigida também, e com o offset de partida junto dos dois números, que é o
que a faz voltar a ser medição.

### 2. A média do quadro inteiro **não** distingue os dois states

Os dois slots mostram a mesma tela com jogadores diferentes: 0,182425 contra
0,183158 sobre a imagem inteira — e a própria animação do boneco balança a
média entre 0,182309 e 0,183844. Ou seja, a diferença entre os dois states é
**menor que o ruído da tela**, e uma assinatura de média teria aceitado
qualquer um dos dois como o outro, calada.

A placa de posição embaixo do nome da camisa (`GK` num, `CB` no outro) resolve:
os dois diferem ali em **0,119963**. É por ela que o `load_looks()` recusa o
state errado, e a recusa tem caso vermelho vivo no `--check-live`:

```text
ok    slot 2's picture is refused as slot 1
      the position plate reads 0.299999 and slot 1 (the goalkeeper) reads 0.291686 (+-0.004000)
```

**E o baseline que o plano prometia está medido:** dois `load_state` do mesmo
slot devolvem quadros que diferem em **0,000000** — igualdade exata, não
tolerância. É isso que autoriza a Fase 2 a ler um diff como "só o campo que eu
troquei".

### 3. As caixas são fração do quadro, não pixel

A resolução de captura é a que a configuração do próprio DuckStation disser, e
este ciclo **não configura o emulador** (decisão de 2026-09-02, herdada de
PES2). Uma caixa em pixel para de significar alguma coisa no dia em que alguém
mexer no multiplicador de resolução — e como o `stats()` de uma caixa errada
devolve um número perfeitamente plausível, isso não teria sintoma. As caixas são
fração, e o `self_check()` exige que resolvam para a mesma parcela de um quadro
de 320×240 e de um de 960×720.

### 4. O bug que eu mesmo plantei, e a guarda que ele virou

O `restore_state()` criava o diretório de save states quando ele não existia.
Rodando o caso de skip com um `PES2_FORK` apontando para lugar nenhum, ele
**copiou as duas fixtures para `C:\nowhere\savestates`** e imprimiu que tinha
restaurado. Cópia numa pasta que nada lê é a forma que mais parece sucesso.

Agora recusa: o diretório é da DuckStation e esta ferramenta **não cria** — e o
caso vermelho confere as duas coisas, que recusou e que **não deixou pasta para
trás**. Na mesma passagem o restore saiu de antes da subida do emulador para
dentro dela: quem prova que o fork está onde se pensa é o `launch`.

(A pasta foi removida; as duas fixtures continuam no diretório do emulador e em
`work/looks-states/`.)

### 5. Duas armadilhas de plataforma

- **O console do Windows é cp1252 e o título do jogo é japonês.** Imprimir a
  resposta crua de `get_status` mata o script com `UnicodeEncodeError` num
  traceback que fala de `charmap` e não do emulador. O `oracle.py` não imprime
  o título; script de sondagem que imprimir precisa de `PYTHONIOENCODING=utf-8`.
- **`mcp_drive.py` traz PIL no import**, então perguntar a ele onde mora um save
  state custa uma biblioteca de imagem. O diretório sai de `fork.FORK_HOME`, e
  lido do ambiente a cada chamada — `PES2_FORK` posto depois do import seria
  ignorado em silêncio, que é como o caso vermelho acima não teria como existir.

### Gates medidos

```text
python tools/looks/selftest.py --quiet
  modules:  0 failure(s)
  rules:    0 failure(s)      ..... rule 1 swept 8 file(s), 3110 line(s)
  controls: 0 failure(s)      ..... 9 of 9 controls red
  looks_selftest: 0 failure(s)
```

Visto **vermelho**, com `PLANTED = 0x8011C000` acrescentado ao `oracle.py` numa
cópia da árvore (nada commitado):

```text
FAIL  Rule 1: no address outside layout.py  [('oracle.py', 896, 'PLANTED = 0x8011C000')]
..... rule 1 swept 8 file(s), 3112 line(s)
looks_selftest: 1 failure(s)                                            (exit 1)
```

O nono controle é novo e é deste módulo — `oracle-any-screen` abre o
`BADGE_TOL` de 0,004 para 0,5, e com ele aberto o `load_looks()` aceita um state
como o outro.

```text
python tools/looks/modelfile.py --check-image      ->  ok
python tools/looks/oracle.py --check               ->  oracle.py: 0 failure(s)
python tools/looks/oracle.py --check-states        ->  os dois .sav, media conferido
python tools/looks/oracle.py --check-live          ->  oracle --check-live: 0 failure(s)
python tools/check_tasks.py                        ->  123 task(s), ok
```

Os três caminhos de skip, conferidos um a um e todos saindo **77**: sem
`WE2002_LOOKS_DRIVE_IMAGE`, sem a cópia de projeto dos states, e com o fork
apontado para um caminho que não existe.

`roms/` só foi lida, nunca escrita; o disco inglês é o que o emulador boota e
dele não se leu textura nenhuma.

### Arquivos criados/modificados

- `tools/looks/oracle.py` — **novo**. `Oracle` (launch/pause/step/press/
  capture/read_ram), `load_looks()`, `require_looks()`, `verify_load()`,
  `_compare()`, o par `adopt_states()`/`restore_state()`, `require_media()`,
  `hide_window()`, `self_check()` com os casos vermelhos, e `--check`,
  `--check-states`, `--adopt-states`, `--check-live`
- `tools/looks/controls.py` — o nono controle, `oracle-any-screen`
- `tools/looks/selftest.py` — `oracle` no `MODULES`
- `docs/PLAN-LOOKS-PY.md` — §1.11 com o que o oráculo mediu, §5.1 com o offset
  de partida e §5.2 reescrita sobre a medição
- `docs/tasks/looks/08-de-onde-vem-o-boneco.md` — a linha da RAM reescrita
- `docs/tasks/looks/19-alvos-de-ctest-e-cli.md` — a decisão sobre o
  `--check-live` virar ou não um quarto alvo
- `docs/tasks/looks/progresso.md` — tabela e checklist da Fase 2
- `docs/tasks/looks/07-oraculo-e-rota-ate-a-tela.md` — este arquivo

### Problemas encontrados

- **A rota por botões continua não escrita**, e isso é decisão, não pendência
  escondida: os dois states chegam à tela e dão um baseline que a navegação não
  daria. O critério desta task não a pede; a §1.11 continua guardando a receita
  manual, agora com a razão pela qual ela não pode ser descartada — o state
  amarra imagem **e** build do emulador.
- **O `--check-live` não é alvo de `ctest` nenhum**, e por isso só roda quem se
  lembra dele. Encaminhado **na**
  [`LOOKS-TASK-19`](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md), que é quem
  registra os alvos: ou vira o quarto, ou fica escrito que é comando de mão.
- E o de sempre, que não é desta task: **`ctest -R looks` neste worktree
  responde `No tests were found!!!` e sai 0**
  ([`CORR-LOOKS-015`](/docs/tasks/looks/CORR-LOOKS-015.md)). Os gates acima
  saíram dos comandos da coluna do meio da tabela do
  [`perfil-looks.md`](/docs/prompts/perfil-looks.md).
