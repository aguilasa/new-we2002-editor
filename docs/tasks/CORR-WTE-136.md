---
id: CORR-WTE-136
title: "Correção: a §8.7 conta seis roteiros onde há oito, e o Log erra o ordinal do item da CORR-WTE-127"
type: correção
category: processo
status: pendente
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

- [ ] `ls tools/par/8.7-*.sh | wc -l` bate com o que a §8.7 afirma
- [ ] O ordinal do item da CORR-WTE-127 bate com a posição dele nas duas listas
- [ ] `ctest -R tasks` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
