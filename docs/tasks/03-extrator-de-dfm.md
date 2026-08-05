---
id: WTE-TASK-03
title: "tools/dfm_extract.py — os 18 formulários, completos"
type: ferramenta
category: engenharia-reversa
phase: 1
depends_on: ["WTE-TASK-02"]
status: pendente
---

# WTE-TASK-03: Extrator de DFM

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §1.6 e Fase 1 item 1.
- Um protótipo **já existe e funcionou**: decodificou 18 blocos `TPF0` do
  `.rsrc` e produziu 6.214 linhas de DFM legível. Esta task o transforma em
  ferramenta.

Dois defeitos medidos no protótipo:

1. **Três dos 18 param cedo** — `ficha_creditos_equipo`, `ficha_movertodos` e
   `ficha_warning_2` saíram com 4, 2 e 3 linhas. O byte de flags de objeto
   (`0xF0` na primeira posição) não está sendo tratado em todos os caminhos.
2. **Blobs binários são descartados** — `Icon.Data`, `Picture.Data` dos 45
   `TImage` e o `Glyph.Data` dos 28 `TSpeedButton` viram `<bin N>`. Sem eles a
   Fase 2 não tem como desenhar nada.

---

## Objetivo

`wte/tools/dfm_extract.py`, determinístico, que lê o `.exe` e escreve os 18
formulários em `wte/re/dfm/`.

### Requisitos

- Os **18** decodificam do começo ao fim, sem exceção engolida.
- **Blobs preservados**, não resumidos. Decidir e escrever o formato: hex
  inline (como o LFM textual usa) ou arquivo lateral referenciado.
- Saída **estável**: rodar duas vezes dá bytes iguais. É o que permite `--check`.
- `--check` compara com o commitado e falha com diferença — mesmo contrato dos
  geradores do `newWe2002`.
- **Falhar alto**: tipo de propriedade desconhecido aborta com o offset, em vez
  de emitir formulário truncado. Um DFM truncado que "parece completo" custaria
  a Fase 2 inteira.

### O que registrar junto

Censo de classes de componente por formulário. O plano tem o total (177
`TLabel`, 45 `TImage`, …, 430 no conjunto); a tabela por formulário é o que
dimensiona a Fase 2.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dfm_extract.py` | criar |
| `wte/re/dfm/*.dfm` | criar (18) |
| `wte/re/dfm/censo.md` | criar |

---

## Critério de conclusão

- [ ] Os 18 formulários decodificam inteiros, os três defeituosos incluídos
- [ ] Blobs binários preservados, com o formato escolhido documentado
- [ ] `--check` implementado e verde
- [ ] Saída byte-estável entre execuções
- [ ] Tipo desconhecido aborta com offset, não emite parcial
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
