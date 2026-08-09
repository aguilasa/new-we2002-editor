---
id: WTE-TASK-10
title: "tools/dfm2lfm.py — gerador dos .lfm e do esqueleto das units"
type: ferramenta
category: ui
phase: 2
depends_on: ["WTE-TASK-03", "WTE-TASK-04", "WTE-TASK-07"]
status: concluído
---

# WTE-TASK-10: Conversor DFM → LFM

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §4.4 e Fase 2 item 1.
- É o gerador que cobre a maior fatia de volume do projeto: ~430 controles em
  18 formulários, mais as assinaturas dos 96 handlers.

O LFM da LCL é sintaticamente quase o DFM textual — a VCL e a LCL
compartilham o formato de propósito. O trabalho está nas exceções.

---

## Objetivo

`wte/tools/dfm2lfm.py`, que lê `wte/re/dfm/*.dfm` e emite, para cada
formulário, um `.lfm` e o esqueleto da unidade Pascal correspondente.

### As quatro exceções a tratar

1. **Blobs binários** — no formato hex que a LCL lê. `Icon.Data`,
   `Picture.Data` dos 45 `TImage`, `Glyph.Data` dos 28 `TSpeedButton`.
2. **`TBrowseURL` → `TLabel`** — componente de terceiro, 2 instâncias, sem par
   na LCL. O comportamento (abrir URL) vira `OpenURL()` de `LCLIntf` no
   handler, e o gerador deixa o `TODO` visível, não silencioso.
3. **Propriedade que a LCL não tem** — vira comentário no `.lfm` com o valor
   original. **Nunca sumir calado**: propriedade descartada em silêncio é
   diferença visual que só aparece na WTE-TASK-12, longe da causa.
4. **`TStaticText`** — 37 instâncias, e a §8.9 avisa que transparência e cor de
   fundo diferem no GTK2. O gerador não resolve isso; só marca as 37 para a
   conferência visual.

### O esqueleto da unidade

Nome fiel ao original (`ep2002_about.pas`, …), com os handlers daquele
formulário como stub que registra o próprio nome:

```pascal
procedure TMainForm.colorearClick(Sender: TObject);
begin
  REStub('colorearClick');
end;
```

**Geometria absoluta, sem layout automático.** Os controles foram posicionados
à mão em 2002 e a fidelidade é o critério — mesma decisão que o `newWe2002`
tomou para os 434 controles do `ed.rc`.

### Contrato de gerador

`--check` comparando com o commitado, saída byte-estável, e falha alta em
construção não reconhecida. Editar `.lfm` à mão tem de quebrar o `--check`.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dfm2lfm.py` | criar |
| `wte/forms/*.lfm` | criar (18, gerado) |
| `wte/src/ep2002_*.pas` | criar (18, gerado) |

---

## Critério de conclusão

- [x] Os 18 `.lfm` gerados e aceitos pelo `lazbuild` — os 19 (18 + o
      `WteMain.lfm` da WTE-TASK-02) passam pelo `LFMtoLRSstream`, que é o
      parser que o `lazbuild` usa, com zero recusa. Medido pelo thread
      principal em 2026-08-06
- [ ] Blobs binários preservados e visíveis na janela — **preservados**: os 118
      (816.880 B) conferidos byte a byte pelos dois `--check`, o do
      `dfm_extract.py` (`.dfm` + `wte/re/dfm/blobs/<form>/*.bin` contra o
      `.exe`) e o do `dfm2lfm.py` (hex do `.lfm` contra o SHA-256 do `.dfm`),
      zero divergentes — remedido em 2026-08-09, com os `blobs/` regerados,
      já que eles são gitignored e só nascem no modo de escrita.
      **Visíveis** é da [WTE-TASK-12](/docs/tasks/12-comparacao-visual.md), que
      já tem "bitmap não aparece" na tabela de achados — não da WTE-TASK-11,
      que nunca teve o item
- [x] `TBrowseURL` substituído com `TODO` visível
- [x] Propriedade descartada vira comentário, nunca some — comentário no
      `.pas`, não no `.lfm`: **LFM não tem sintaxe de comentário** (ver o Log)
- [x] Os 96 stubs gerados na unidade certa (coluna `formulario` da WTE-TASK-04)
- [x] `--check` implementado e verde
- [x] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-06

- **Resumo do que foi feito:**

  `wte/tools/dfm2lfm.py` lê os 18 `.dfm` de `wte/re/dfm/`, os 118 `.bin` de
  `wte/re/dfm/blobs/` e `wte/re/published_methods.tsv`, e emite 18 `.lfm` em
  `wte/forms/`, 18 unidades em `wte/src/` e `wte/forms/conversao.md`. São 441
  componentes, 96 stubs, 118 blobs e 80 propriedades descartadas.

  A tabela de mapeamento não é palpite: saiu das fontes da LCL 3.0 em
  `/usr/lib/lazarus/3.0/lcl`, varrendo as seções `published` de cada classe e
  de todos os ancestrais, cruzado com o que ocorre nos 18 DFM. Propriedade que
  não esteja nem em `ACEITA` nem em `DESCARTA` **aborta** — é o caso "não sei
  em que balde isto cai", diferente de "a LCL não tem".

  Nome das unidades: `ep2002_` + o formulário sem o prefixo `ficha_`. Os 13
  nomes que a §1.3 do plano recuperou dos exports do `.exe` estão numa tabela
  no gerador, e ele aborta se a regra deixar de reproduzi-los — a extrapolação
  para os outros 5 só vale enquanto a regra bater onde há medida.

  Verificado sem `lazbuild` (que é do thread principal), com o que ele usa por
  baixo:

  | Gate | Resultado |
  |---|---|
  | dupla execução byte a byte | `sha256` idêntico |
  | `dfm2lfm.py --check` | verde, com e **sem** `wte/re/dfm/blobs/` |
  | `wte/tools/test_dfm2lfm.py` | 64 testes, sem tocar no `.exe` |
  | `make -C wte check` | 140 testes + 6 geradores, verde |
  | `LFMtoLRSstream` da LCL sobre os 18 `.lfm` | 18/18 aceitos |
  | `fpc` sobre as 18 unidades | 18/18, zero warning |
  | conversão de recurso do FPC (o que o `lazbuild` roda) | 18/18, recursos `TMAINFORM`, `TESTRATEGIA`, `TJUGADOR`, `TFICHA_*` |

- **Arquivos criados/modificados:**
  - `wte/tools/dfm2lfm.py` (criado)
  - `wte/tools/test_dfm2lfm.py` (criado)
  - `wte/forms/ep2002_*.lfm` (criados, 18, gerados)
  - `wte/src/ep2002_*.pas` (criados, 18, gerados)
  - `wte/forms/conversao.md` (criado, gerado)
  - este arquivo (critérios e log)

- **Problemas encontrados:**

  1. **LFM não tem sintaxe de comentário**, e o critério "propriedade
     descartada vira comentário no `.lfm`" não é implementável. O `TParser` da
     FCL — que lê LFM tanto no `LFMtoLRSstream` quanto em tempo de execução —
     só pula espaço, tabulação, CR e LF; e `{` abre bloco binário. Medido:
     `//` e `{ }` num `.lfm` fazem `LFMtoLRSstream` devolver `false`. Pior, o
     `{$R}` só embute bytes: um comentário **compilaria** e explodiria ao abrir
     a janela. O valor descartado vai para um comentário **na unidade Pascal**,
     ao lado do campo do componente, e para `wte/forms/conversao.md`.

  2. **Uma unidade chamada `restub` não pode exportar `REStub`.** Identificador
     em Pascal não distingue maiúsculas: o FPC resolve o nome cru como o da
     unidade e recusa a chamada com
     `Fatal: Syntax error, "." expected but "(" found`. A WTE-TASK-11 planeja
     `wte/src/restub.pas`; os stubs gerados usam **`retrace`**, e o arquivo
     precisa nascer com esse nome. A assinatura que o plano fixa
     (`procedure REStub(const Nome: string)`) não muda.

  3. **`TBrowseURL` é uma `TAction`, não um controle**, e as 2 instâncias vivem
     dentro de um `TActionList`. Como `TLabel`, ficam sem pai
     (`TControl.SetParentComponent` só aceita `TWinControl`) e não aparecem —
     que é o que a ação já fazia. Junto caíram o `Category`, o `URL` (guardado
     na constante `LANZA_URL_URL` de cada unidade) e os 2 `Action = lanza_url`
     dos `TSpeedButton`, cujo valor a LCL recusaria.

  4. **`TUpDown.OnClick` não é `TNotifyEvent`**, é
     `TUDClickEvent(Sender: TObject; Button: TUDBtnType)` — 12 dos 96. O
     gerador deriva a assinatura do par `(classe, evento)` e aborta em par
     desconhecido, justamente porque adivinhar dá um `.pas` que não compila.

  5. **Os `.lfm` versionados somam 1,9 MiB, dos quais ~1,6 MiB são o hex dos
     118 blobs.** Isso tensiona a §2 do plano e a decisão da WTE-TASK-03 (que
     manteve os mesmos bytes fora do versionamento, com o argumento de que
     "hex é só uma codificação"). O `.gitignore` manda o contrário para
     `wte/forms/` — "não acrescente `*.lfm` nem `*.pas` a nenhuma regra daqui"
     —, e sem o hex a janela não mostra bitmap nenhum. Ficou como a tarefa
     pede; **é decisão do usuário confirmar antes do commit**, e reverter é
     mexer num ponto só do gerador.

     *Resolvido:* o usuário confirmou versionar em 2026-08-06, e a exceção
     entrou nos três documentos que declaram a política — §2 do
     [`../PLAN-WTE-LAZARUS.md`](/docs/PLAN-WTE-LAZARUS.md), o bloco
     `wte/re/dfm/blobs/` do `.gitignore` e as "Pendências externas" do
     [`progresso.md`](/docs/tasks/progresso.md) — pela
     [CORR-WTE-019](/docs/tasks/CORR-WTE-019.md). A §2 deixa de tensionar.
