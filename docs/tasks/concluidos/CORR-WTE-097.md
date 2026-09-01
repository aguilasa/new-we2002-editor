---
id: CORR-WTE-097
title: "Correção: o comentário do base_teamClick diz \"medido em dois times\" e a medida final tem seis"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-097: o `.inc` do `base_teamClick` ainda diz "dois times"

## Problema identificado

O achado de que **o original preça 22 slots, não 23** está escrito em quatro
lugares, e três deles dizem **seis times**. O quarto — o cabeçalho do
[`ep2002_mainform.base_teamClick.inc`](../../../wte/src/impl/ep2002_mainform.base_teamClick.inc),
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

- [x] `grep -n "dois times" wte/src/impl/ep2002_mainform.base_teamClick.inc` sai vazio
- [x] `lazbuild wte/wte.lpi` compila, e **sem warning novo**: `-B` antes e
      depois dá o **mesmo** único warning, o
      `we2002_preco.pas(138,27) Comment level 2 found`, que é anterior
      (commit `c566455`) e num arquivo que esta correção não toca
- [x] `make -C wte check` verde — 764 testes, `OK (skipped=1)`
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-24

**Resumo do que foi feito:**

O cabeçalho passou a dizer **seis times (0, 2, 9, 17, 30, 48)**, mantida a
observação do time 9 — slots 21 e 22 com a mesma soma e a mesma posição, só o 21
gravado —, que continua sendo o argumento que descarta explicação pelo conteúdo.
Entrou também a linha de como se remede a amostra, que a correção pedia:

```bash
awk -F'\t' '$3==22 && $7!="-"' wte/re/preco.tsv | wc -l   # tem de dar 0
```

**E entrou uma segunda régua, que a correção não previa e a
[CORR-WTE-095](/docs/tasks/concluidos/CORR-WTE-095.md) produziu horas antes neste mesmo
lote:** como se remede o **salto**, que é outra pergunta que a da amostra.
Plantar `0xFF` no slot 22 e rodar o oráculo separa "não grava" de "grava o valor
que já estava lá" — sem isso, as seis corridas provam só que o byte não mudou.

**Problemas encontrados:**

1. **A correção *k+1* tornou falso o que a *k* deixou escrito, dentro do mesmo
   lote.** O cabeçalho dizia *"o `ed.exe` e o editor do Obocaman discordam sobre
   o último slot"*, e isso já não é o que está medido: a CORR-WTE-095 leu a
   `0x00404374` do próprio oráculo e ela **não** tem ramo por slot — calcula
   `0x2ece0c + 23*time + 2*(time div 56) + slot` para os 23, igual ao port. O
   parágrafo foi reescrito: a conta de offset do port não está errada, e o que
   sobra aberto é o `cmp` de `0x004110a6` ler zero num campo que a rotina
   anterior acabou de preencher. *(A CORR-WTE-095 fechou isso em 2026-08-24: o
   `cmp` **não** lê zero — a coluna é não nula nas 23 voltas, e o byte se perde
   abaixo do `fputc`. O que este Log registra é o estado daquele dia.)*
2. **O `.inc` cresceu 13 linhas e derrubou o `check_fase2.py`.** A §4.4 do plano
   cita a fração medida, e ela caiu de **52,1%** para **52,0%** — 9.453 geradas
   contra 8.719 à mão (eram 8.706). O número novo veio do próprio gate, que
   imprime o literal esperado; o `fase-2.md` foi regerado e sai byte-idêntico em
   duas escritas.
3. **Um warning anterior apareceu ao medir a linha de base**, e fica registrado
   porque ninguém o tinha notado: `we2002_preco.pas:138` tem `` `{$Q-}` `` dentro
   de um comentário `{ }`, e a crase não protege — o `{` abre nível 2. É de
   `c566455`, é inofensivo (o FPC avisa e segue), e está **fora** do escopo desta
   correção.

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `wte/src/impl/ep2002_mainform.base_teamClick.inc` | modificado — a amostra, as duas réguas e o parágrafo da causa |
| `docs/PLAN-WTE-LAZARUS.md` | modificado — a fração da §4.4, 52,1% → 52,0% |
| `wte/re/fase-2.md` | regerado |
