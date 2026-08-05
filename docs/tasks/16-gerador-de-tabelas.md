---
id: WTE-TASK-16
title: "tools/gen_tables_pas.py — offsets e tabelas estáticas"
type: ferramenta
category: dados
phase: 3
depends_on: ["WTE-TASK-15"]
status: pendente
---

# WTE-TASK-16: Gerador de tabelas

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §4.4 e Fase 3 item 3.
- O gerador **mais simples** dos quatro, e por isso o primeiro a rodar: a
  entrada é dado puro, sem fluxo de controle para traduzir. Serve de piloto do
  contrato de gerador antes do transpilador de verdade (WTE-TASK-17).

Entrada, tudo deste repositório:

| Arquivo | Conteúdo |
|---|---|
| `src/core/include/we2002/Offsets.hpp` | 69 `OFS_*` |
| `src/core/Tables.cpp` | 704 linhas, 16 tabelas |
| `src/core/include/we2002/Tables.hpp` | as declarações |

---

## Objetivo

`wte/tools/gen_tables_pas.py` emitindo uma unidade Pascal com os offsets como
`const` e as 16 tabelas como array constante.

### Requisitos

- **Nomes preservados.** `OFS_TEAM_NAME_1` continua `OFS_TEAM_NAME_1`. O
  glossário do `newWe2002` já traduziu tudo do italiano; não retraduzir, não
  "melhorar". Grepar um nome nas duas árvores tem de continuar funcionando.
- **Rastreabilidade herdada.** Os offsets carregam comentário com o nome antigo
  (`// was OFS_NOMI_SQ1`); preservar como comentário Pascal.
- **Tipo conforme a WTE-TASK-15.**
- `--check`, saída byte-estável, falha alta em construção não reconhecida.

### Conferência obrigatória

O valor de cada offset no Pascal gerado tem de ser **numericamente igual** ao do
`Offsets.hpp`. Gerar um teste que compara os 69, não confiar na inspeção.

Isso parece redundante — é o mesmo arquivo de entrada. Não é: erro de parsing de
literal (hex, sufixo, expressão) produz número plausível e errado, e o offset
errado só aparece quando a gravação corromper a imagem.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/gen_tables_pas.py` | criar |
| `wte/src/we2002_offsets.pas` | criar (gerado) |
| `wte/src/we2002_tables.pas` | criar (gerado) |
| `wte/tests/test_offsets.pas` | criar |

---

## Critério de conclusão

- [ ] Os 69 offsets e as 16 tabelas emitidos
- [ ] Nomes idênticos aos do `newWe2002`
- [ ] Comentários `was OFS_*` preservados
- [ ] Teste comparando os 69 valores contra o `Offsets.hpp`, verde
- [ ] `--check` implementado e verde
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
