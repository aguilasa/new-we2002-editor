---
id: WTE-TASK-14
title: "Fechamento da fase 2 — a casca está fiel?"
type: fechamento
category: ui
phase: 2
depends_on: ["WTE-TASK-12", "WTE-TASK-13"]
status: pendente
---

# WTE-TASK-14: Fechamento da fase 2

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 2, critério de pronto.
- A fase 2 entrega ~60% do volume de código do projeto por gerador. Se ela
  fechar com controle faltando ou evento fora de ordem, todo handler da Fase 4
  é implementado contra uma casca errada.

---

## Objetivo

Aceitar a fase, ou listar o que falta.

### Conferências

1. **`--check` do `dfm2lfm.py` verde** e registrado na bateria de testes.
2. **Nenhum `.lfm` ou unidade gerada editado à mão** — provar rodando o
   `--check` sobre a árvore commitada.
3. **Os 96 stubs existem e logam**, um por linha do `published_methods.tsv`.
4. **Os 18 formulários conferidos visualmente**, com veredito escrito.
5. **`eventos.md` sem pergunta em aberto** que a Fase 4 vá precisar.

### Métrica a registrar

Quantas linhas de Pascal existem, e quantas são geradas. Este número é a
verificação da tese da §4.4 — se a fração gerada for muito menor que o esperado,
a tese está errada e o plano precisa dizer isso.

### O que ainda não foi provado

A casca não toca a imagem de CD. Nada nesta fase diz que o app **funciona** —
só que ele **parece** e **reage**. Escrever isso, para o vocabulário não inflar.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/fase-2.md` | criar |
| `docs/PLAN-WTE-LAZARUS.md` | modificar (§4.4, se a fração gerada divergir) |
| `docs/tasks/progresso.md` | modificar |

---

## Critério de conclusão

- [ ] `--check` do gerador verde e na bateria de testes
- [ ] Provado que nenhum arquivo gerado foi editado à mão
- [ ] Os 96 stubs conferidos contra o TSV
- [ ] Os 18 formulários com veredito visual
- [ ] Fração de código gerado medida e comparada com a tese da §4.4
- [ ] Escrito o que a fase **não** prova
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
