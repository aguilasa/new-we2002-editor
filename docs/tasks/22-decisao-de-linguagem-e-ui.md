---
id: PES2-TASK-22
title: "Decisão de linguagem e UI do editor"
type: decisão
category: projeto
phase: 6
depends_on: ["PES2-TASK-21", "PES2-TASK-30"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §5 (Fase 6)"
status: pendente
---

# PES2-TASK-22: Linguagem e UI do editor

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §5, Fase 6, e o não-objetivo da §0:
  *"Não decidir agora a linguagem nem a UI do editor. O mapa vem antes; sem
  ele não há o que a UI mostre."*
- **Esta task é o "agora" que a §0 adiava.** Ela só abre depois da
  PES2-TASK-21, e é a primeira do projeto que decide sobre o editor.
- **E depois da PES2-TASK-30**, pelo mesmo argumento uma camada adiante: a
  Fase 7 acrescentou assets — grade de imagem × paleta, import/export de PNG,
  cópias por idioma. Decidir a UI sem a lista que a 30 entrega é desenhar uma
  janela sem lugar para metade do que o editor vai mostrar.

---

## Objetivo

Escolher linguagem, toolkit e forma da interface, com a razão escrita.

### O que o repositório já ensinou sobre cada opção

| Opção | Precedente aqui | O que custou |
|---|---|---|
| **C++ + Qt6** | `newWe2002` | build pesado; mas o core portável e headless é o que tornou os golden possíveis |
| **Lazarus/FPC** | `wte/` | nativo no Linux, VCL-like; projeto separado que não compartilha build |
| **Python + Qt/Tk** | as onze ferramentas de `tools/pes2/` | já é a linguagem de todo o ferramental deste projeto; sem compilação, sem gerador de UI |

### O peso que este projeto tem e os outros não

1. **Não há oráculo** (§4.1). O que sustenta a verificação aqui é o emulador,
   não uma comparação byte a byte contra outro binário. Isso **reduz** o
   valor de um core headless separado — que no `newWe2002` existia
   justamente para os golden — e aumenta o de iterar rápido.
2. **O ferramental inteiro já é Python** e não depende do `we2002_core` nem
   do Qt (§3.1). Trocar de linguagem para o editor significa reimplementar
   `iso.py`, `tables.py` e a aritmética de setor, ou fazer ponte.
3. **A §6.9 proíbe estender o `we2002_core`.** Se algo tiver de ser
   compartilhado, é **copiado com atribuição no comentário** — não linkado.

### E a forma da UI

O `ed.exe` tem 434 controles num diálogo de 1077 px, posicionados à mão em
2002. Não é modelo a copiar; é aviso do que acontece quando a UI cresce sem
layout. Decidir aqui se o alvo é GUI, TUI ou linha de comando com o mapa
como interface — as três são respostas legítimas, e a terceira é a mais
barata para um primeiro editor.

---

## Critério de conclusão

- [ ] Decisão escrita na §5 do plano, Fase 6, com a razão em um parágrafo.
- [ ] O que ela custa, dito: o que vai precisar ser reimplementado ou feito
      ponte, e quanto.
- [ ] A regra da §6.9 respeitada na escolha — nada de estender o
      `we2002_core`.
- [ ] Se a escolha implicar build novo, o esqueleto dele é a primeira coisa
      da PES2-TASK-23, não desta.

---

## Log de Execução

*(a preencher)*
