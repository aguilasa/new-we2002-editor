---
id: CORR-WTE-031
title: "Correção: o `wte/tests/README.md` diz que a pasta está vazia e é só Pascal, e a WTE-TASK-16 pôs dois arquivos lá, um deles C++"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-031: o README de `wte/tests/` descreve uma pasta que não existe mais

## Problema identificado

A [WTE-TASK-16](/docs/tasks/concluidos/16-gerador-de-tabelas.md) criou
`wte/tests/test_offsets.pas` e `wte/tests/test_offsets.cpp` — os dois dumpers da
conferência obrigatória, ambos **gerados** pelo `gen_tables_pas.py`.

O `wte/tests/README.md` continua com o texto da fase 0 e contradiz a pasta em
dois pontos:

1. «**Vazio na fase 0.** O primeiro conteúdo real é da **WTE-TASK-20**
   (round-trip headless contra o `we2002_core`, nas duas ROMs).» — o primeiro
   conteúdo real chegou na WTE-TASK-16, quatro tarefas antes.
2. «Esta pasta é **só Pascal**» — `test_offsets.cpp` é C++, e tem de ser: a
   conferência inteira depende de um lado ser compilado pelo `g++` a partir do
   `Tables.cpp` original. É a própria razão de o arquivo existir, e o README diz
   que ele não pode estar ali.

Falta ainda o que o README de uma pasta gerada precisa dizer: que os dois
arquivos **não se editam à mão**, que quem os produz é o `gen_tables_pas.py`, e
que quem os compila e compara é o `wte/tools/test_gen_tables_pas.py`, por
`make -C wte test`. Sem isso, o próximo a abrir a pasta encontra dois programas
sem dono aparente e sem nenhum alvo que os construa.

Criticidade baixa: nada mede errado por causa disso, e o `--check` do gerador
cobre os dois arquivos. O que se perde é a orientação — e a pergunta "onde ponho
o teste do `dfm_extract.py`?" já ficou sem resposta uma vez neste projeto, e
custou a [CORR-WTE-005](/docs/tasks/concluidos/CORR-WTE-005.md).

## Evidência

```console
$ ls wte/tests
README.md  roteiros  test_offsets.cpp  test_offsets.pas

$ head -4 wte/tests/README.md
# `tests/` — testes do lado Pascal

Vazio na fase 0. O primeiro conteúdo real é da **WTE-TASK-20** (round-trip
headless contra o `we2002_core`, nas duas ROMs).

$ grep -no 'Esta pasta é só Pascal' wte/tests/README.md
13:Esta pasta é só Pascal

$ head -1 wte/tests/test_offsets.cpp
// GERADO por wte/tools/gen_tables_pas.py -- NAO editar a mao.
```

O `roteiros/` também já estava lá (WTE-TASK-13), e o README não o menciona.

## Causa raiz

O README foi escrito na fase 0 descrevendo uma pasta vazia, e a WTE-TASK-16
povoou a pasta sem revisitá-lo.

## Correção

### Arquivo: `wte/tests/README.md`

Reescrever a abertura para o estado corrente, preservando as duas decisões que
o texto atual registra e que continuam valendo — o golden test mora em `tools/`
porque precisa de Wine e do `:99`, e teste de ferramenta Python mora ao lado do
gerador que testa:

- trocar «Vazio na fase 0…» por um inventário do que existe hoje:
  `test_offsets.pas` e `test_offsets.cpp` (WTE-TASK-16, **gerados**, não editar
  à mão) e `roteiros/` (WTE-TASK-13);
- trocar «Esta pasta é só Pascal» pela regra real — a pasta guarda **programas
  de teste compilados**, e o par de dumpers é deliberadamente bilíngue, porque
  a conferência só vale se cada lado vier de um compilador diferente;
- dizer quem constrói: `wte/tools/test_gen_tables_pas.py`, alcançado por
  `make -C wte test` (de que `check` depende), compila os dois e compara as
  saídas — não há alvo do `Makefile` que os construa isoladamente;
- manter a menção à WTE-TASK-20 como o que **ainda** vai chegar (round-trip
  headless nas duas ROMs), em vez de "o primeiro conteúdo real".

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tests/README.md` | modificar |

## Verificação

- [ ] `grep -n 'Vazio na fase 0\|só Pascal' wte/tests/README.md` não devolve nada
- [ ] O README nomeia os três itens que existem hoje: `test_offsets.pas`,
      `test_offsets.cpp` e `roteiros/`
- [ ] O README diz que os dois `test_offsets.*` são gerados pelo
      `gen_tables_pas.py` e conferidos por `make -C wte check`
- [ ] `make -C wte check` continua verde
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

`wte/tests/README.md` reescrito para a pasta que existe: inventário dos três
itens (`test_offsets.pas`, `test_offsets.cpp`, `roteiros/`), a regra real — a
pasta guarda programas de teste **compilados**, e o par de dumpers é
deliberadamente bilíngue porque a conferência só vale com um compilador de
cada lado —, quem os constrói (`wte/tools/test_gen_tables_pas.py`, via
`make -C wte test`, sem alvo isolado), e a WTE-TASK-20 como o que ainda vem.
As duas decisões que o texto antigo guardava foram preservadas.

Executada fora do `/corrigir`: o defeito foi **criado pela própria leva** que
escreveu a WTE-TASK-16, e apareceu na varredura de concorrência pedida logo
depois. Corrigir na hora custa menos que deixar aberto e arriscar que alguém
"conserte" um arquivo já certo.

**Problemas encontrados:** Nenhum.

**Arquivos criados/modificados:** `wte/tests/README.md`
