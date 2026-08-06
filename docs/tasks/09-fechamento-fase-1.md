---
id: WTE-TASK-09
title: "Fechamento da fase 1 — a extração estática está completa?"
type: fechamento
category: engenharia-reversa
phase: 1
depends_on: ["WTE-TASK-03", "WTE-TASK-04", "WTE-TASK-05", "WTE-TASK-06", "WTE-TASK-07", "WTE-TASK-08"]
status: pendente
---

# WTE-TASK-09: Fechamento da fase 1

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 1, critério de pronto.
- A fase 1 é a única que **não usa decompilador**. Fechá-la mal significa entrar
  na Fase 4 lendo assembly para descobrir coisa que `strings` teria dado.

---

## Objetivo

Conferir que `wte/re/` está completo e que os números batem entre si.

### Conferências cruzadas

1. **DFM × handlers.** Todo `OnClick` citado nos 18 DFM tem entrada em
   `published_methods.tsv`? Todo handler do TSV é referenciado por algum DFM?
   Divergência nas duas direções é achado, não erro de ferramenta.
2. **Strings × handlers.** Quantas strings ficaram sem handler dono? Se for
   muito, a heurística de referência por imediato está perdendo caso.
3. **Offsets × `Offsets.hpp`.** Os 19 continuam batendo depois de a tabela ter
   limite medido? Algum caiu fora do limite?
4. **Assets × formulários.** Os `TImage` dos DFM carregam bitmap embutido ou
   arquivo externo? Se embutido, parte dos 197 pode ser irrelevante.

### Recontagem obrigatória

Todo número que o plano afirma na §1 foi medido em 2026-08-05 por script
descartável. Remedir com as ferramentas versionadas e **reconciliar**:

| Afirmação do plano | Onde remedir |
|---|---|
| 18 formulários, ~430 componentes | `dfm_extract.py` |
| 96 handlers | `dump_published.py` |
| 19 de 69 offsets | `dump_offsets.py` |
| 70 strings com padding | `dump_strings.py` |
| 13 unidades `Tep2002_*` | `objdump -x` |
| 322 imports, sendo 300 de `rtl60.bpl`/`vcl60.bpl` (§1.2) | `dump_units.py` |

Divergência entre o plano e a medição versionada se resolve **a favor da
medição**, e o plano é corrigido.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/fase-1.md` | criar — as quatro conferências e a reconciliação |
| `docs/PLAN-WTE-LAZARUS.md` | modificar (§1, se algum número mudar) |
| `docs/tasks/progresso.md` | modificar |

---

## Critério de conclusão

- [ ] As quatro conferências cruzadas feitas, com o resultado escrito
- [ ] Os seis números do plano remedidos por ferramenta versionada
- [ ] Divergência corrigida no plano, não escondida
- [ ] Nenhum item da Fase 1 em aberto sem justificativa
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
