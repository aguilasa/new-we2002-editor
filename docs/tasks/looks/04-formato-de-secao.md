---
id: LOOKS-TASK-04
title: "`section.py` — primitiva de 24 B, vértice de 8 B e o separador de zeros"
type: implementação
category: formato
phase: 1
depends_on: ["LOOKS-TASK-03"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §1.4"
status: pendente
---

# LOOKS-TASK-04: O formato de seção

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §1.4.
- O formato vem da §2.2 do
  [ANALISE-REPOS-WE3D-DBMANAGER.md](/docs/ANALISE-REPOS-WE3D-DBMANAGER.md), com
  **uma correção medida aqui**: a varredura contígua morre na seção 55 porque
  falta o par de zeros que separa grupos.
- **Não é TMD.** A primitiva de 24 bytes é *gradation, no-texture*: quatro cores
  e quatro índices, **sem UV**. Tratá-la como pacote TMD desalinha tudo.

---

## Objetivo

`tools/looks/section.py`: ler um cabeçalho de seção, suas primitivas e seus
vértices, e saber reconhecer o separador de grupo.

---

## Critério de conclusão

- [ ] `numVertex`/`numPrimitive` lidos como `uint32` LE; tamanho calculado como
      `8 + nPrim*24 + nVert*8`.
- [ ] Primitiva decodificada em **quatro cores (B,G,R,modo) e quatro índices**
      `v1,v0,v3,v2` — atenção à ordem, que não é `v0,v1,v2,v3`.
- [ ] Vértice decodificado como `int16 x,y,z` mais um `uint16` de padding.
- [ ] O par `numVertex == 0 && numPrimitive == 0` é reconhecido como
      **separador de grupo**, e não como fim de arquivo.
- [ ] O byte de modo da primeira cor é **lido e registrado**, não descartado —
      é ele que decide a incógnita (d) na Fase 3.
- [ ] `self_check()` contra seção sintética, com caso vermelho: trocar 24 por
      20 tem de ficar vermelho.

---

## Log de Execução

*(preencher ao executar)*
