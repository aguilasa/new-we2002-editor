---
id: WTE-TASK-29
title: "Fechamento da fase 4 — os 96 têm veredito?"
type: fechamento
category: comportamento
phase: 4
depends_on: ["WTE-TASK-25", "WTE-TASK-26", "WTE-TASK-27", "WTE-TASK-28"]
status: pendente
---

# WTE-TASK-29: Fechamento da fase 4

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 4, critério de pronto.

> **Pronto quando:** os 96 têm veredito e nenhum é "não portado" sem
> justificativa escrita.

---

## Objetivo

Provar o critério, ou listar o que falta.

### Conferências

1. **Cobertura.** `spec_index.py` sobre `re/spec/` tem de listar 96 entradas.
   Nenhuma `aberto`.
2. **Justificativa.** Todo `não portado` com razão escrita, e a razão tem de
   ser de escopo, não de dificuldade. "Não deu tempo" não é veredito.
3. **Evidência.** Quantas specs se apoiam só em "observação de tela"? Essas são
   hipóteses vestidas de spec. Listar, e decidir quais precisam de disassembly
   antes da Fase 6.
4. **Golden.** Toda operação de gravação verde nas duas ROMs.
5. **Nenhum decompilado colado.** Varredura por trecho de C nas specs — a §2
   depende disso e ninguém confere sozinho.

### Métrica a registrar

Distribuição dos vereditos: quantos `implementado`, `trivial`, `divergência
deliberada`, `não portado`. E a comparação com o que a Fase 4 previa.

Se `trivial` for a maioria esmagadora, provavelmente foi atribuído sem olhar —
a WTE-TASK-28 avisa disso. Amostrar cinco `trivial` ao acaso e reconferir.

### O que ainda não foi provado

As quatro features da Fase 5. O app já edita e grava como o original nas
operações comuns, mas o **motivo do projeto** — preço, `.mcr`, camisa 2D, slots
de ML — ainda não está feito.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/fase-4.md` | criar |
| `wte/re/spec/INDICE.md` | regenerar |
| `docs/tasks/progresso.md` | modificar |

---

## Critério de conclusão

- [ ] 96 entradas no índice, nenhuma `aberto`
- [ ] Todo `não portado` com justificativa de escopo
- [ ] Specs de evidência fraca listadas, com decisão sobre cada
- [ ] Golden verde nas duas ROMs para toda gravação
- [ ] Varredura por decompilado colado, limpa
- [ ] Cinco `trivial` reamostrados e reconferidos
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
