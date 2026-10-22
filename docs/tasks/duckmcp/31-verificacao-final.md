---
id: DMCP-TASK-31
---

# DMCP-TASK-31 — Verificação final: `duckmcp_live` em dois jogos e a bateria do §5.2

## Goal

A definição de pronto do §0 está medida: `duckmcp_live` passa com dois jogos de digest diferente, e cada linha da tabela do §5.2 tem o mesmo veredito do começo do ciclo.

## Arquivos a criar ou modificar

- In:
  - só corridas e o registro no plano
- Out:
  - código

## Done criteria

- [ ] `duckmcp_live` `Passed` com `DUCKSTATION_TEST_IMAGE` no WE2002 japonês e de novo no PES2 `(EsIt)`, os dois `sha256sum` das trilhas de dados diferentes, colados no Log
- [ ] `ctest --test-dir build -R 'duckmcp|pes2|looks|kits|kit2d|tasks'` com o ambiente inteiro no comando: a linha final colada, e cada *skipped* com a razão
- [ ] o §0 do plano ganha a linha "Feito" com o commit e a data

## Notes

## Log de Execução
