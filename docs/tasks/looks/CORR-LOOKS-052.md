---
id: CORR-LOOKS-052
title: "Correção: \"o `modelfile` roda primeiro\" é regra com controle, e a ordem não muda o veredito do `cli.py check`"
type: correção
category: verificação
status: pendente
depends_on: []
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

- [ ] nenhum controle fica vermelho por uma propriedade que não muda o
      veredito — conferido reordenando a lista e rodando o disco inglês
- [ ] tirar o `modelfile` do `CHECK_IMAGE` fica vermelho
- [ ] `python tools/looks/cli.py check <inglesa .bin>` continua FAILED, e
      `<japonesa>` continua ok
- [ ] `python tools/looks/selftest.py --quiet` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
