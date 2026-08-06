---
id: WTE-TASK-03
title: "tools/dfm_extract.py — os 18 formulários, completos"
type: ferramenta
category: engenharia-reversa
phase: 1
depends_on: ["WTE-TASK-02"]
status: concluído
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

- [x] Os 18 formulários decodificam inteiros, os três defeituosos incluídos
- [x] Blobs binários preservados, com o formato escolhido documentado
- [x] `--check` implementado e verde
- [x] Saída byte-estável entre execuções
- [x] Tipo desconhecido aborta com offset, não emite parcial
- [x] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-05

- **Resumo do que foi feito:**

  `wte/tools/dfm_extract.py` lê o `.exe` (leitura pura), varre a árvore de
  recursos do PE em **stdlib pura** — sem `pefile`, são ~60 linhas e o
  `make -C wte check` passa a rodar em qualquer máquina com Python 3 — e
  decodifica os 18 streams `TPF0` de `RT_RCDATA`. Os 21 `TValueType` e as três
  flags de objeto (`ffInherited`, `ffChildPos`, `ffInline`) estão
  implementados; os que não ocorrem nestes 18 foram exercitados contra streams
  sintéticos. *(Esses streams eram código descartável quando esta linha foi
  escrita — a [CORR-WTE-005](/docs/tasks/CORR-WTE-005.md) os transformou em
  `wte/tools/test_dfm_extract.py`, que `make -C wte test` roda.)*

  Os 18 decodificam **até o último byte**: o parser exige `pos == len(stream)`
  ao fim de cada formulário e aborta se sobrar qualquer coisa. Saem 6.848
  linhas de DFM textual padrão (o protótipo dava 6.214).

  **A causa apontada para os três formulários quebrados não se confirma.** Uma
  varredura por bytes de prefixo de objeto nos 18 streams acha **zero** — não
  há um único `0xF0` nessa posição em lugar nenhum do `.rsrc`, então o byte de
  flags não pode ter truncado nada. `ficha_creditos_equipo`, `ficha_movertodos`
  e `ficha_warning_2` também não têm nada de estrutural que os separe dos
  outros 15 (os primeiros seis pares propriedade/tipo de cada um são os mesmos
  de `ficha_enlaza` e `ficha_info4`, que o protótipo decodificou inteiros). A
  falha do protótipo não foi reproduzida — ele não está no repositório —, e o
  que se pode afirmar é que sob um leitor do formato completo os três saem
  inteiros, com 56, 56 e 81 linhas.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/tools/dfm_extract.py` | criar |
  | `wte/re/dfm/*.dfm` | criar (18) |
  | `wte/re/dfm/censo.md` | criar |
  | `wte/re/dfm/README.md` | atualizar — dizia "vazio até a WTE-TASK-03"; agora documenta a convenção de blob |
  | `.gitignore` | acrescentar `wte/re/dfm/blobs/`, depois do `!wte/re/**` |

- **Problemas encontrados:**

  1. **Onde colocar 798 KiB de arte de terceiro.** Os 118 `vaBinary` inline em
     hex dariam ~1,6 MiB de texto versionado — exatamente o que o `.gitignore`
     mantém fora do repositório ao ignorar `we-team-editor/` ("binário sem
     fonte e sem licença não entra"), só que numa codificação diferente.
     Escolhido **arquivo lateral**: `blobs/<form>/<dono>.<prop>.bin`, ignorado
     pelo git e regerado do `.exe`, referenciado no `.dfm` por
     `{blob <arquivo> <tamanho> sha256:<hash>}`. O SHA-256 versionado é o que
     substitui versionar os bytes — o `--check` confere os 798 KiB byte a byte
     contra ele. E `{...}` com texto não-hexadecimal faz um leitor de DFM
     padrão falhar na referência em vez de aceitar lixo em silêncio.
  2. **Censo diverge da §1.6 do plano**: 441 componentes contra 430, com
     `TLabel` 182 (não 177) e `TBitBtn` 32 (não 26). A diferença é exatamente
     os 11 componentes dos três formulários que o protótipo truncou — o censo
     da §1.6 foi tirado da saída incompleta. Reconciliar a §1 é da WTE-TASK-09.
  3. **`--check` sem o `.exe`** sai com código 2 e mensagem própria, distinta
     de "saída desatualizada" (código 1). Não pode sair verde: `make -C wte
     check` verde sem nada medido é o que o Makefile da WTE-TASK-02 diz
     explicitamente que não quer.
