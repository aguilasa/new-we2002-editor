---
id: CORR-WTE-136
title: "Correção: a §8.7 conta seis roteiros onde há oito, e o Log erra o ordinal do item da CORR-WTE-127"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-136: duas contagens da §8.7 que não batem com a árvore

## Problema identificado

**1. "Seis roteiros em `tools/par/8.7-*.sh`".** É a frase de abertura da §8.7
do inventário. O glob tem **nove arquivos**: o prelúdio mais **oito** roteiros.
Os seis que saem `OK` são os seis que o Log da PAR-TASK-06 lista; os outros
dois — `8.7-t2002-exportar.sh` e `8.7-t2002-importar.sh`, os do item 5 — são
citados pelo nome mais abaixo, **na mesma seção**. Quem reler a seção e "rodar
os seis" acredita ter re-medido a §8.7 inteira, e não mediu o item que a
própria task chama de mais valioso (ver
[CORR-WTE-135](/docs/tasks/CORR-WTE-135.md)).

**2. "o 6º da lista já estava fechado pela CORR-WTE-127".** É o Log da
PAR-TASK-06. O item do `Escape` é o **terceiro** da lista, tanto na task quanto
na §8.7; o sexto é o do `.t2002`. O "5 de 5" está certo — cinco itens desta
task, mais um fechado fora dela —, o ordinal é que não.

## Evidência

```text
$ ls tools/par/8.7-*.sh | wc -l
9
$ ls tools/par/8.7-*.sh
tools/par/8.7-clamp-xy.sh
tools/par/8.7-escape-papel-sem-navegar.sh
tools/par/8.7-escape-papel.sh
tools/par/8.7-prelude.sh
tools/par/8.7-preset-renomear.sh
tools/par/8.7-presets-16.sh
tools/par/8.7-t2002-exportar.sh
tools/par/8.7-t2002-importar.sh
tools/par/8.7-troca-papel.sh
```

Contra a §8.7: "Seis roteiros em `tools/par/8.7-*.sh`, os seis saindo `OK`".

E a ordem dos itens, idêntica nos dois documentos: 1 clamp, 2 troca de papel,
**3 `Escape` (CORR-WTE-127)**, 4 os 16 presets, 5 renomear preset, 6 `.t2002`.

## Causa raiz

A frase foi escrita contando as corridas verdes, não os arquivos do diretório;
o ordinal, contando de trás para frente.

## Correção

### Arquivo: `docs/PARIDADE-FUNCIONAL.md`

Trocar a abertura da §8.7 por uma contagem que separe as duas coisas: **oito
roteiros**, dos quais **seis com veredito `OK` de golden** e **dois do item 5**,
cujo veredito é o que a [CORR-WTE-135](/docs/tasks/CORR-WTE-135.md) vai
produzir.

### Arquivo: `docs/tasks/PAR-TASK-06.md`

No Log da quarta passagem, trocar "o 6º da lista" por "o 3º da lista", e dizer
que os dois roteiros do item 5 **não** estão entre os seis re-rodados.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PARIDADE-FUNCIONAL.md` | modificar |
| `docs/tasks/PAR-TASK-06.md` | modificar |

## Verificação

- [x] `ls tools/par/8.7-*.sh | wc -l` bate com o que a §8.7 afirma — **10**,
      e a seção diz "dez arquivos: o prelúdio mais nove roteiros"
- [x] O ordinal do item da CORR-WTE-127 bate com a posição dele nas duas
      listas — **3º** nas duas
- [x] `ctest -R tasks` verde — 51 tasks
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-31

**Resumo do que foi feito:**

A contagem foi escrita depois das outras duas CORRs deste lote, de propósito: a
[134](/docs/tasks/CORR-WTE-134.md) acrescentou o `8.7-escape-papel-preset.sh` ao
glob e a [135](/docs/tasks/CORR-WTE-135.md) deu veredito aos dois do `.t2002`.
Contar antes teria produzido um número que envelheceria na mesma sessão.

O glob tem **10** arquivos — o prelúdio mais nove roteiros. A §8.7 agora separa
o que a frase antiga misturava: sete roteiros com veredito `OK` e dois do item
do `.t2002`, cuja perna de importar **diverge de propósito**, porque quem lê
errado é o oráculo. O "cinco conferidos" da abertura virou "seis", que é o
número de itens da lista; e as "três CORRs" viraram cinco.

O ordinal do item do `Escape` é **3º** nas duas listas, não 6º.

**Problemas encontrados:**

A frase errada não era só imprecisa — ela **dava uma instrução ruim**. "Seis
roteiros, os seis saindo `OK`" convida a re-medir a §8.7 rodando seis coisas, e
os dois que ficam de fora são justamente os do item que a própria task chama de
mais valioso da série. Foi exatamente o que aconteceu na quarta passagem da
PAR-TASK-06, e é o que a CORR-WTE-135 teve de ir medir depois.

**Arquivos criados/modificados:**

| Arquivo | O quê |
|---|---|
| `docs/PARIDADE-FUNCIONAL.md` | a abertura da §8.7: dez arquivos, sete `OK`, dois do item 6, cinco CORRs |
| `docs/tasks/PAR-TASK-06.md` | o ordinal, a ressalva de que os seis re-rodados não são todos, e as cinco CORRs |
