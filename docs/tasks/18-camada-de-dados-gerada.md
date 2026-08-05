---
id: WTE-TASK-18
title: "Gerar a camada de dados e fazê-la compilar"
type: implementação
category: dados
phase: 3
depends_on: ["WTE-TASK-17"]
status: pendente
---

# WTE-TASK-18: Camada de dados gerada

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 3 item 3.
- Executar o transpilador da WTE-TASK-17 sobre as ~2.150 linhas e resolver o que
  o `FORBIDDEN` recusar.

**O que o `FORBIDDEN` recusa não é falha do gerador — é trabalho identificado.**
Cada recusa tem três saídas, e a decisão vai escrita:

1. **Estender a tabela** — a construção tem tradução mecânica, faltava a regra.
2. **Ajustar a entrada** — o C++ do `we2002_core` pode ser reescrito num estilo
   que o transpilador digere, **sem mudar comportamento**, e isso melhora os
   dois lados. Exige rodar o golden test do `newWe2002` depois.
3. **Porte manual daquele trecho** — último recurso, e o trecho fica marcado.

A opção 2 tem custo escondido: mexer em `src/core/` afeta o `newWe2002`, que
está com escopo fechado e verificado. **Não fazer sem rodar `ctest` e o golden.**

---

## Objetivo

Unidades Pascal geradas, compilando, com o registro do que foi recusado.

### Escopo

| Entrada | Saída |
|---|---|
| `Database.cpp` + `.hpp` | `we2002_database.pas` |
| `Player.cpp` + `.hpp` | `we2002_player.pas` |
| `CdImage.cpp` + `.hpp` | `we2002_cdimage.pas` |
| `TextCodec.cpp` + `.hpp` | `we2002_textcodec.pas` |
| `Types.hpp` | `we2002_types.pas` |

**`Sofifa.cpp` fica de fora.** O import do SoFIFA está desligado no `newWe2002`
desde 2026-08-05, o editor do Obocaman não tem nada equivalente, e trazer 805
linhas sem consumidor é peso morto.

### Regras que a camada tem de preservar

Vindas do `newWe2002`, todas com custo pago:

- **Nunca recalcular EDC/ECC.** O editor original não recalcula; um port deve
  **preservar**, não "corrigir".
- **Setores MODE2/2352.** Os offsets pulam cabeçalho de setor manualmente; se um
  round-trip falhar, a primeira suspeita é fronteira de setor.
- **Leitura curta não é erro.**
- **`Load`+`Save` sem editar nada não devolve a imagem intacta**, e não deveria:
  o `Save` reconstrói as all-star a partir dos links. O oráculo faz o mesmo.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/src/we2002_*.pas` | criar (5, gerado) |
| `wte/re/recusas.md` | criar — cada recusa, a rota escolhida, a razão |
| `src/core/*` | modificar **só** se a rota 2 for escolhida, e com golden rodado |

---

## Critério de conclusão

- [ ] As cinco unidades geradas e compilando
- [ ] Toda recusa do `FORBIDDEN` com rota escolhida e razão escrita
- [ ] Se houve rota 2: `ctest` e o golden do `newWe2002` verdes depois
- [ ] Trechos de porte manual marcados no código gerado
- [ ] `Sofifa.cpp` fora, e a razão registrada
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
