---
id: WTE-TASK-10
title: "tools/dfm2lfm.py — gerador dos .lfm e do esqueleto das units"
type: ferramenta
category: ui
phase: 2
depends_on: ["WTE-TASK-03", "WTE-TASK-04", "WTE-TASK-07"]
status: pendente
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

- [ ] Os 18 `.lfm` gerados e aceitos pelo `lazbuild`
- [ ] Blobs binários preservados e visíveis na janela
- [ ] `TBrowseURL` substituído com `TODO` visível
- [ ] Propriedade descartada vira comentário, nunca some
- [ ] Os 96 stubs gerados na unidade certa (coluna `formulario` da WTE-TASK-04)
- [ ] `--check` implementado e verde
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
