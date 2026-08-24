---
id: CORR-WTE-097
title: "Correção: o comentário do base_teamClick diz \"medido em dois times\" e a medida final tem seis"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-WTE-097: o `.inc` do `base_teamClick` ainda diz "dois times"

## Problema identificado

O achado de que **o original preça 22 slots, não 23** está escrito em quatro
lugares, e três deles dizem **seis times**. O quarto — o cabeçalho do
[`ep2002_mainform.base_teamClick.inc`](../../wte/src/impl/ep2002_mainform.base_teamClick.inc),
que é onde mora a constante `ULTIMO_SLOT_PRECADO = 21` que depende do achado —
ainda diz **dois**, com a lista `(2 e 9)` de quando só duas corridas existiam.

Não é afirmação falsa: os times 2 e 9 estão entre os seis. É a evidência mais
fraca, no arquivo onde ela mais pesa — quem for questionar o `21` lê este
cabeçalho antes de qualquer outro.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -rn "dois times\|seis times" wte/src/impl/ep2002_mainform.base_teamClick.inc \
     wte/re/preco.md wte/re/spec/MainForm.base_teamClick.md \
     wte/tools/check_preco.py docs/tasks/CORR-WTE-095.md
```

```text
wte/src/impl/…base_teamClick.inc:48:  e para o slot 22 a coluna sai ZERO. Medido em dois times da ROM japonesa
wte/re/preco.md:133:… Medido em seis times: os bytes gravados
wte/re/spec/MainForm.base_teamClick.md:113:ela sai zero**. Medido em seis times: os bytes gravados vão de
wte/tools/check_preco.py:122:# o limite do laco lido no `.text` e a FAIXA de bytes que mudou, medida em seis
docs/tasks/CORR-WTE-095.md:35:**Medido em seis times da ROM japonesa** (0, 2, 9, 17, 30, 48): os bytes
```

E a amostra que sustenta o seis:

```bash
awk -F'\t' '$7!="-" && NR>1{print $1"/"$2}' wte/re/preco.tsv | sort -u
awk -F'\t' '$3==22 && $7!="-"' wte/re/preco.tsv | wc -l
```

```text
japanese-shift-jis/0
japanese-shift-jis/17
japanese-shift-jis/2
japanese-shift-jis/30
japanese-shift-jis/48
japanese-shift-jis/9
0
```

Seis times medidos, e **nenhuma** linha de slot 22 marcada como medida em
nenhum deles.

## Causa raiz

O cabeçalho foi escrito depois das duas primeiras corridas do oráculo e não
reescrito quando a amostra cresceu para seis.

## Correção

### Arquivo: `wte/src/impl/ep2002_mainform.base_teamClick.inc`

No bloco do `ULTIMO_SLOT_PRECADO`: `Medido em dois times da ROM japonesa (2 e
9)` → `Medido em seis times da ROM japonesa (0, 2, 9, 17, 30, 48)`, mantendo a
observação do time 9 — slots 21 e 22 com a mesma soma e a mesma posição, e só o
21 gravado —, que continua sendo o argumento que descarta explicação pelo
conteúdo.

Vale acrescentar a linha de **como se remede**, que é uma linha:

```bash
awk -F'\t' '$3==22 && $7!="-"' wte/re/preco.tsv | wc -l   # tem de dar 0
```

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/src/impl/ep2002_mainform.base_teamClick.inc` | modificar |

## Verificação

- [ ] `grep -n "dois times" wte/src/impl/ep2002_mainform.base_teamClick.inc` sai vazio
- [ ] `lazbuild wte/wte.lpi` compila (o `.inc` entra por `{$I}`)
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
