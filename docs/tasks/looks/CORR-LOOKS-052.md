---
id: CORR-LOOKS-052
title: "Correção: \"o `modelfile` roda primeiro\" é regra com controle, e a ordem não muda o veredito do `cli.py check`"
type: correção
category: verificação
status: done
depends_on: []
origin: LOOKS-TASK-19
severity: low
done_on: 2026-09-17
done_commit: 44a158e
---

# CORR-LOOKS-052: um controle vermelho por uma propriedade que o gate não tem

## Problema identificado

O `cli.py check` — o que o `looks_image` roda desde a LOOKS-TASK-19 — declara
três regras, cada uma com controle negativo, e a primeira é de **ordem**:

```text
docs/PLAN-LOOKS-PY.md §4.4
- o `modelfile` roda primeiro, porque a primeira leitura dele é um arquivo
  só-japonês pela guarda. Geometria é idêntica nos dois discos, e sem essa
  leitura apontar a variável para o disco inglês passaria em silêncio
```

A mesma razão está no docstring do `cli.py`, na tabela de gates do perfil, no
Log da task ("é a razão medida de o `modelfile` ir primeiro") e no controle
`cli-guard-read-not-first`:

```text
"modelfile's first read is the Japanese-only file through the guard; run
later, geometry checks pass on the English disc before anything notices"
```

**Nada no `cmd_check` depende da ordem.** Ele roda os oito até o fim, sem
parar no primeiro vermelho, e junta os códigos no `combine()`, onde qualquer
falha faz a corrida falhar. O que impede o disco inglês de passar é o
`modelfile` **estar na lista** — e mais seis módulos que também o recusam —,
não estar em primeiro. E estar na lista já é conferido: o self-check compara o
`CHECK_IMAGE` com os fontes que respondem `--check-image`.

O controle fica vermelho porque a asserção é literal (`CHECK_IMAGE[:1] ==
("modelfile",)`), não porque a troca deixaria passar alguma coisa. Ele entra na
contagem de "63 de 63 controles vermelhos" como guarda exercitada, e ensina uma
regra que a ferramenta não cumpre nem precisa cumprir.

A medição que a task cita — "contra o inglês sete falham e o `pieces` passa" —
está certa e é a razão de o `modelfile` precisar **entrar** no `check`. Não é
razão de ordem.

## Evidência

Numa cópia da árvore, com a lista reordenada — `pieces` primeiro, que é o único
que passa no disco inglês, e `modelfile` por **último**:

```text
$ python <cópia>/tools/looks/cli.py check C:/games/ps1/work/we2002-english.bin
  ok    pieces     exit 0   pieces --check-image: ok
  FAIL  texture    exit 1   texture --check-image: 1 failure
  FAIL  atlas      exit 1   atlas --check-image: 1 failure(s)
  FAIL  skin       exit 1   layout.WrongDisc: /BIN/DAT2D.BIN ...
  FAIL  looks      exit 1   layout.WrongDisc: /SELECT.BIN ...
  FAIL  assembly   exit 1   layout.WrongDisc: /BIN/DAT2D.BIN ...
  FAIL  scene      exit 1   layout.WrongDisc: /BIN/DAT2D.BIN ...
  FAIL  modelfile  exit 1   modelfile --check-image: 1 failure(s)
cli check: 8 module(s), 1 ok, 0 skipped, 7 failed -- FAILED
exit=1

$ python <cópia>/tools/looks/cli.py check roms/japanese-shift-jis.bin
cli check: 8 module(s), 8 ok, 0 skipped, 0 failed -- ok
```

O mesmo veredito da ordem commitada, nos dois discos: `1 ok, 7 failed --
FAILED` e `8 ok`.

## Causa raiz

A regra de ordem veio da CORR-LOOKS-012, quando o alvo rodava **só** o
`modelfile`; com oito módulos e um `combine()` que não para no primeiro, a
ordem deixou de ser carga e a regra ficou.

## Correção

### Arquivo: `tools/looks/cli.py` e `tools/looks/controls.py`

Uma das duas, e a escolha é da execução:

1. **Tirar a regra**: a ordem passa a ser só de leitura ("o primeiro vermelho
   impresso é o mais baixo"), o controle `cli-guard-read-not-first` sai, e em
   seu lugar entra o que de fato protege — um controle que **remova** o
   `modelfile` do `CHECK_IMAGE` e exija o vermelho do self-check.
2. **Tornar a regra verdadeira**: o `cmd_check` para no primeiro vermelho da
   guarda, e aí a ordem passa a importar e o controle passa a medir.

A primeira é menor, e não perde nada: nenhuma corrida atual precisa parar cedo.

### Arquivo: `docs/PLAN-LOOKS-PY.md` (§4.4), `docs/prompts/perfil-looks.md` e `docs/tasks/looks/19-alvos-de-ctest-e-cli.md`

A frase de ordem sai (ou passa a dizer o que a opção 2 fizer), e a medição do
`pieces` fica — como razão de o `modelfile` estar no `check`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/cli.py` | modificar |
| `tools/looks/controls.py` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `docs/prompts/perfil-looks.md` | modificar |
| `docs/tasks/looks/19-alvos-de-ctest-e-cli.md` | modificar |

## Verificação

- [x] nenhum controle fica vermelho por uma propriedade que não muda o
      veredito — conferido reordenando a lista e rodando o disco inglês
- [x] tirar o `modelfile` do `CHECK_IMAGE` fica vermelho
- [x] `python tools/looks/cli.py check <inglesa .bin>` continua FAILED, e
      `<japonesa>` continua ok
- [x] `python tools/looks/selftest.py --quiet` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-17

### Resumo do que foi feito

A evidência reproduz em `54dba19`: numa cópia da árvore com `pieces` primeiro e
`modelfile` por último, o disco inglês dá `1 ok, 0 skipped, 7 failed -- FAILED`
e o japonês `8 ok`, iguais à ordem commitada.

**Opção 1 da CORR — tirar a regra.** O `cmd_check` roda os oito até o fim e o
`combine()` falha em qualquer falha; nenhuma corrida precisa parar cedo.

- `cli.py` — o parágrafo "`modelfile` runs FIRST" virou "`modelfile` has to be
  IN the run, and where it runs does not matter", com a medição do `pieces`
  como razão de **estar** e a reordenação como prova de que a posição não muda
  o veredito. O docstring do `CHECK_IMAGE` diz que a ordem é de leitura e que
  quem guarda é a **pertença**. O assert `CHECK_IMAGE[:1] == ("modelfile",)`
  virou `"modelfile" in CHECK_IMAGE`.
- `controls.py` — `cli-guard-read-not-first` saiu; entrou
  `cli-guard-read-left-out`, que **tira** o `modelfile` da lista.
- `tests/CMakeLists.txt` — o comentário do `looks_image` dizia
  "modelfile's check FIRST"; agora diz que os oito rodam até o fim e a ordem é
  de leitura. Arquivo quente de cinco projetos: só o comentário mudou.
- `PLAN-LOOKS-PY.md` §4.4, `perfil-looks.md` (tabela de gates) e
  `19-alvos-de-ctest-e-cli.md` — a frase de ordem trocada no lugar, com a data
  e o que dizia; a medição do `pieces` ficou, como razão de o `modelfile`
  estar no `check`.

### Gates

```text
$ python tools/looks/cli.py check C:/games/ps1/work/we2002-english.bin
cli check: 8 module(s), 1 ok, 0 skipped, 7 failed -- FAILED
$ python tools/looks/cli.py check roms/japanese-shift-jis.bin
cli check: 8 module(s), 8 ok, 0 skipped, 0 failed -- ok

# cópia da árvore, CHECK_IMAGE com o modelfile por ÚLTIMO
['texture', 'atlas', 'skin', 'looks', 'assembly', 'pieces', 'scene', 'modelfile']
  FAIL  texture    exit 1   texture --check-image: 1 failure(s)
  FAIL  atlas      exit 1   atlas --check-image: 1 failure(s)
  FAIL  skin       exit 1   layout.WrongDisc: /BIN/DAT2D.BIN ...
  FAIL  looks      exit 1   layout.WrongDisc: /SELECT.BIN ...
  FAIL  assembly   exit 1   layout.WrongDisc: /BIN/DAT2D.BIN ...
  ok    pieces     exit 0   pieces --check-image: ok
  FAIL  scene      exit 1   layout.WrongDisc: /BIN/DAT2D.BIN ...
  FAIL  modelfile  exit 1   modelfile --check-image: 1 failure(s)
cli check: 8 module(s), 1 ok, 0 skipped, 7 failed -- FAILED
$ python <cópia>/tools/looks/cli.py --check
cli.py: 0 failure(s)            # nenhum controle ficaria vermelho pela ordem

$ python tools/looks/controls.py --only cli-guard-read-left-out
  RED    cli-guard-read-left-out    cli.py :: module constant
$ python tools/looks/selftest.py --quiet
  ..... 64 of 64 controls red
looks_selftest: 0 failure(s)
$ python tools/check_tasks.py
check_tasks: 123 task(s), ok
```

`roms/` intocada (só leitura).

### Problemas encontrados

- O primeiro literal do controle novo saiu com o `\n` expandido pelo shell e
  quebrou o `controls.py` (`SyntaxError`); consertado pelo editor antes de
  qualquer gate.

### Arquivos criados/modificados

- `tools/looks/cli.py`, `tools/looks/controls.py`
- `tests/CMakeLists.txt` — um comentário
- `docs/PLAN-LOOKS-PY.md`, `docs/prompts/perfil-looks.md`,
  `docs/tasks/looks/19-alvos-de-ctest-e-cli.md`
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
