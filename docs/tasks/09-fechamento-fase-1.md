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
| 197 bitmaps + `dat.bin` (§1.2 e §1.8) | `find -iname '*.bmp'` — ver [`assets.md`](../../wte/re/assets.md) |

A última linha não tem gerador: a WTE-TASK-08 decidiu rota inline para os
assets, com o comando ao lado de cada número. A coluna "onde remedir" aponta o
comando e o documento que o executa.

Divergência entre o plano e a medição versionada se resolve **a favor da
medição**, e o plano é corrigido.

### Varrer os sítios, não só a §1

Corrigir a §1 do plano não fecha um número errado — ele se espalha. O "197
bitmaps" está em **nove** lugares, dois deles no plano e dois em tarefas da fase
7 ainda por executar (a 38 vai pedir mensagem de erro sobre essa contagem, a 39
uma regra de empacotamento). Para cada número reconciliado:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -rn "<o número velho>" docs/ wte/re/
```

O alvo é zerar a saída fora dos documentos que **narram** a correção
(`correcoes-progresso.md`, os `CORR-WTE-*.md`, os Logs de Execução), onde o
número velho é citação histórica e fica. Registrar em `wte/re/fase-1.md` o
`grep -rn "197" docs/ | wc -l` de antes e de depois.

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
- [ ] Os sete números do plano remedidos por ferramenta versionada
- [ ] Divergência corrigida no plano, não escondida
- [ ] Cada número reconciliado varrido com `grep -rn` em `docs/` e `wte/re/`, e
      o `wc -l` de antes e de depois registrado em `wte/re/fase-1.md`
- [ ] Nenhum item da Fase 1 em aberto sem justificativa
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
