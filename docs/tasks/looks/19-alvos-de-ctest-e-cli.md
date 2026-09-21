---
id: LOOKS-TASK-19
title: "`cli.py` e os quatro alvos de `ctest`"
type: implementação
category: verificação
phase: 7
depends_on: [LOOKS-TASK-18]
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#4.4"
reviewed_on: 2026-09-17
review_commit: null
done_on: 2026-09-17
done_commit: 66eeb6e
---

# LOOKS-TASK-19: A linha de comando e os gates

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §4.4 e §9.
- A convenção do repositório é **um alvo por faixa de custo**: um obrigatório
  que não precisa de nada e nunca pula; os dependentes de fixture com
  `SKIP_RETURN_CODE 77` e a variável nomeada na mensagem; os de display/venv
  sob `if(UNIX AND Python3_FOUND)` — **no repositório**, onde o `mcr_ui` está
  assim. **Neste ciclo não:** os quatro de `looks` ficam no `if(Python3_FOUND)`,
  porque sob `if(UNIX …)` o `looks_ui` sumiria da máquina Windows onde roda e
  `ctest -R looks_ui` sairia zero — medido no critério do `looks_ui` abaixo. *(Até
  2026-09-17 esta linha trazia só a convenção, e lida de cima era instrução —
  [`CORR-LOOKS-053`](/docs/tasks/looks/CORR-LOOKS-053.md).)*

---

- **Existe um segundo gate de disco desde 2026-09-15**, e ele não está em
  `ctest` nenhum: `python tools/looks/texture.py --check-image`, da
  [`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md). Ele pula
  com 77 sem `WE2002_LOOKS_IMAGE`, como o `looks_image` já faz. **Decidir se o
  `looks_image` passa a rodar os dois `--check-image`** — o do `modelfile.py` e
  o do `texture.py` — ou se nasce um alvo terceiro é desta task; deixá-lo fora é
  um alvo verde que não roda metade do que existe.

---

## Objetivo

`tools/looks/cli.py` responde pelas perguntas do projeto, e o `ctest` registra
os quatro alvos. *(Dizia "três" até 2026-09-17, contra o título —
[`CORR-LOOKS-053`](/docs/tasks/looks/CORR-LOOKS-053.md).)*

---

## Critério de conclusão

- [x] `cli.py` com `sections`, `pieces`, `texture`, `looks` e `check` — e
      `--check`, o self-check, que é por onde o `controls.py` o planta.
- [x] `looks_selftest` **já registrado**, pela
      [`LOOKS-TASK-06`](/docs/tasks/looks/06-harness-controles-e-selftest.md).
      Esta task **confere**: sem dependência nenhuma e **nunca pula**.
- [x] `looks_image` **já registrado** — entrou na
      [`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md) em 2026-09-14,
      porque o perfil o prometia desde a LOOKS-TASK-05 e `ctest -R looks`
      respondia `No tests were found!!!` **saindo zero**, que se lê como
      verde. Esta task **confere**, não cria: `SKIP_RETURN_CODE 77`,
      `WE2002_LOOKS_IMAGE` nomeada na mensagem de skip, e o disco inglês
      recusado em vez de aceito em silêncio.
- [x] `looks_ui` **já registrado**, pela
      [`LOOKS-TASK-16`](/docs/tasks/looks/16-contratos-da-ui.md) em 2026-09-16,
      com `SKIP_RETURN_CODE 77`. Esta task **confere**, não cria — e confere
      uma coisa a mais, porque o enunciado deste item dizia
      `if(UNIX AND Python3_FOUND)` e isso está **medido como errado**: a janela
      sobe nativa nesta máquina Windows, estacionada em −32000, sem Xvfb
      nenhum. Sob `if(UNIX …)` o alvo desapareceria justamente de onde ele
      roda, e `ctest -R looks_ui` responderia `No tests were found!!!`
      **saindo zero** — a armadilha 12 outra vez. Ele entrou no mesmo
      `if(Python3_FOUND)` dos outros dois.
- [x] **Decidido: virou o quarto alvo, `looks_live`.** Título desta task,
      §4.4 do plano e tabela de gates do perfil passaram a dizer quatro.
      O enunciado original deste item segue abaixo.
      **Decidir o que fazer com o `oracle.py --check-live`, que existe desde a
      [`LOOKS-TASK-07`](/docs/tasks/looks/07-oraculo-e-rota-ate-a-tela.md)** e
      hoje não é alvo nenhum. Ele sobe o emulador, carrega os dois save states,
      confere a chegada pelo quadro e compara a RAM com o disco; **pula com 77**
      sem `WE2002_LOOKS_DRIVE_IMAGE`, sem `WE2002_LOOKS_IMAGE`, sem os `.sav`
      de `work/looks-states/` ou sem o fork — os quatro conferidos antes de o
      emulador subir, desde a
      [`CORR-LOOKS-017`](/docs/tasks/looks/CORR-LOOKS-017.md). Ou vira um
      quarto alvo — e aí o título desta task e a tabela
      de gates do [`perfil-looks.md`](/docs/prompts/perfil-looks.md) passam a
      dizer quatro —, ou fica como comando de mão, e **isso fica escrito**. O
      que não pode é continuar sendo um gate que só roda quem se lembra dele,
      que é exatamente o que a
      [`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md) abriu.
- [x] **Com o quarto alvo, o número passou a 1 passed, 3 skipped**, copiado
      da corrida no Log. O enunciado original segue.
      Numa máquina limpa, `ctest -R looks` dá **1 passed, 2 skipped** — e o
      número aparece no Log, **copiado da saída de uma corrida de verdade**.
      Até esta task são **1 passed, 1 skipped**: o `looks_selftest` passa e o
      `looks_image` pula sem a variável.
- [x] **O número sai de uma corrida que listou os alvos pelo nome.**
      `ctest -R looks` que responde `No tests were found!!!` **sai 0**, e já
      passou por verde duas vezes neste ciclo
      ([`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md),
      [`CORR-LOOKS-015`](/docs/tasks/looks/CORR-LOOKS-015.md)). Nenhum
      diretório de build do worktree lista os alvos; nesta máquina a corrida
      sai de um build **fora da árvore**, configurado com o toolchain do
      vcpkg — a receita está na tabela de gates do
      [`perfil-looks.md`](/docs/prompts/perfil-looks.md).
- [x] Os alvos dos outros projetos continuam verdes: `ctest -R "pes2|mcr|tasks"`
      sem regressão, especialmente se a LOOKS-TASK-10 mexeu no
      `bin_archive.py`.

---

## Log de Execução

**Executado em:** 2026-09-17 — **CONCLUÍDA**.

### O que se aprendeu

**O `looks_image` media um oitavo do gate de disco.** Desde a
[`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md) ele rodava o
`modelfile.py --check-image`, e sete módulos ganharam o seu depois disso sem
entrar em alvo nenhum. A decisão que esta task pedia — os dois
`--check-image` ou um alvo terceiro — tinha envelhecido para oito. O
`cli.py check` roda os oito, até o fim, e a lista **se confere
contra os fontes** no self-check, porque a lista escrita à mão é exatamente o
que deixou sete de fora. Pulo parcial falha; nada rodado não é verde.

**Contra o disco inglês, sete falham e o `pieces` passa** — e está certo: ele
só lê geometria, que é igual nos dois. É a razão medida de o `modelfile`
**estar** no `check`. *(Até 2026-09-17 esta frase dizia "de o `modelfile` ir
primeiro", e a ordem não muda o veredito —
[`CORR-LOOKS-052`](/docs/tasks/looks/CORR-LOOKS-052.md).)*

**O `--check-live` virou alvo porque é barato e se recusa cedo.** Os quatro
pré-requisitos são conferidos antes de subir processo; com tudo no lugar, 8,9 s.
`RESOURCE_LOCK duckstation` nele e no `pes2_boot`.

**E a primeira corrida pelo `ctest` achou dois defeitos.** A sessão MCP caiu no
primeiro `pause` — um vermelho em catorze corridas, não reproduzido, aberto como
[`CORR-LOOKS-051`](/docs/tasks/looks/CORR-LOOKS-051.md). E o emulador **ficou
de pé** depois do teste: exceção dentro do `__enter__` não passa pelo
`__exit__`. Este segundo foi consertado aqui — um alvo que roda sem ninguém
olhando não pode deixar o recurso serializado do repositório ocupado —, e
conferido plantando uma falha no `pause`: zero processos DuckStation depois.
Virou a armadilha 31 do perfil.

### Gates medidos

Na árvore de `417c711`, build fora da árvore com o toolchain do vcpkg:

```text
$ ctest --test-dir <build> -R looks          # sem as três variáveis
1/4 Test #10: looks_selftest ...................   Passed   19.18 sec
2/4 Test #11: looks_image ......................***Skipped   0.09 sec
3/4 Test #12: looks_ui .........................***Skipped   0.78 sec
4/4 Test #13: looks_live .......................***Skipped   0.11 sec
100% tests passed out of 4

$ WE2002_LOOKS_IMAGE=<japonesa> WE2002_LOOKS_DRIVE_IMAGE=<inglesa .cue>     ctest --test-dir <build> -R looks
1/4 Test #10: looks_selftest ...................   Passed   18.87 sec
2/4 Test #11: looks_image ......................   Passed    2.09 sec
3/4 Test #12: looks_ui .........................   Passed   45.17 sec
4/4 Test #13: looks_live .......................   Passed    8.89 sec
100% tests passed out of 4
# e nenhum processo DuckStation depois

$ ctest --test-dir <build> -R "pes2|mcr|tasks"
1/6 Test #4: tasks ............................   Passed
2/6 Test #5: pes2_selftest ....................***Failed
3/6 Test #6: pes2_image .......................***Skipped
4/6 Test #7: mcr_selftest .....................   Passed
5/6 Test #8: mcr_card .........................***Skipped
6/6 Test #9: mcr_container ....................   Passed

$ python tools/looks/selftest.py --quiet
  ..... rule 1 swept 21 file(s), 15800 line(s)
  ..... 63 of 63 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check <japonesa>
cli check: 8 module(s), 8 ok, 0 skipped, 0 failed -- ok
$ python tools/looks/cli.py check                 # sem a variável
cli check: skipped -- WE2002_LOOKS_IMAGE is not set and no image was given: ...
exit 77
$ python tools/looks/cli.py check <inglesa .bin>
cli check: 8 module(s), 1 ok, 0 skipped, 7 failed -- FAILED

$ python tools/looks/oracle.py --check      oracle.py: 0 failure(s)
$ python tools/check_tasks.py               check_tasks: 123 task(s), ok
```

**O `pes2_selftest` vermelho não é regressão**: ele lista `/proc/self/fd`, que
não existe no Windows, e já estava assim na
[`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md) e na
[`LOOKS-TASK-16`](/docs/tasks/looks/16-contratos-da-ui.md); `git diff a82f922
417c711 -- tools/pes2` é vazio, e o registro dele no `CMakeLists.txt` não mudou.
O `pes2_boot` ganhou `RESOURCE_LOCK` e é `if(UNIX)`: não existe neste build.

Controles de 60 para 63, cada um conferido vermelho pela **própria** causa:
`cli-check-forgets-a-module` (*on disc but not listed: ['scene']*),
`cli-guard-read-not-first` (*modelfile runs first* — trocado pela
[`CORR-LOOKS-052`](/docs/tasks/looks/CORR-LOOKS-052.md) por
`cli-guard-read-left-out`, que tira o `modelfile` da lista) e `cli-partial-skip-passes`
(*a pass with a skip beside it is NOT a pass*).

### Problemas encontrados, e para onde foram

- **A sessão MCP perdida no primeiro `pause`** —
  [`CORR-LOOKS-051`](/docs/tasks/looks/CORR-LOOKS-051.md), Média, aberta.
- **O emulador deixado de pé pela exceção no `__enter__`** — consertado aqui.
- **As falhas por disco errado de `skin`, `looks`, `assembly` e `scene` saem
  como traceback**, não como recusa de uma linha. O vermelho é o certo; a forma
  é só ruído, e não abri correção.

### Arquivos criados/modificados

Commit `417c711`:

- `tools/looks/cli.py` — novo
- `tools/looks/controls.py` — três controles
- `tools/looks/selftest.py` — `cli` na lista de módulos
- `tools/looks/oracle.py` — o `__enter__` derruba o emulador quando falha
- `tests/CMakeLists.txt` — `looks_image` por `cli.py check`, `looks_live`
  novo, `RESOURCE_LOCK` também no `pes2_boot`
- `docs/PLAN-LOOKS-PY.md` — §0 item 4, §3.2, §4.4 e §9
- `docs/prompts/perfil-looks.md` — tabela de gates, a contagem, arquivos
  quentes e a armadilha 31
- `docs/tasks/looks/progresso.md` — o título desta task, a linha da Fase 7 e a
  estrutura sem o `check_image.py` que nunca existiu
- `docs/tasks/looks/CORR-LOOKS-051.md` e
  `docs/tasks/looks/correcoes-progresso.md` — a correção aberta
- este arquivo — o título

Commit seguinte: este Log, os critérios e `docs/tasks/looks/progresso.md`.
