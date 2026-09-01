---
handler: FormShow
formulario: ficha_enlaza
endereco: 0x00402c44
veredito: trivial
---

# ficha_enlaza.FormShow

## Entrada

Um campo publicado do próprio formulário: o de deslocamento `0x304`, que o
[`../campos.tsv`](../campos.tsv) resolve em `BitBtn2` (`TBitBtn`).

**Evidência:** disassembly lido

## Saída

`BitBtn2.SetFocus`. É a forma `campo` do [`../arranque.md`](../arranque.md):
uma chamada virtual sobre um campo publicado, slot `0xC0` do VMT — que nos
packages é `Controls::TWinControl::SetFocus`, resolvido pelo próprio
`dump_arranque.py` contra o `vcl60.bpl`.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Três instruções e uma chamada; não há I/O de arquivo.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma checada. `SetFocus` sobre controle de formulário não visível levantaria
exceção na VCL, mas isto roda no `OnShow`, quando o formulário já é visível.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**Quem abre este formulário** é o
[`MainForm.mostrar_jugadorClick`](MainForm.mostrar_jugadorClick.md), quando o
jogador escolhido é de clube de Master League. Aquele handler continua
`aberto`, e com ele continuam sem medir a condição exata do desvio e o que o
chamador faz com o `mrYes` que este modal devolve — ver a
[CORR-WTE-086](../../../docs/tasks/concluidos/CORR-WTE-086.md), que corrigiu a atribuição
anterior ao `pabajoClick`.

O `ficha_enlaza` pergunta *"o jogador selecionado é linkado do jogador N do
time M; você deseja deslinkar o jogador?"*, com `BitBtn1` = " Sim" e `BitBtn2`
= "Nao" (os `Caption` estão no DFM). Focar o botão **negativo** ao abrir é o
que impede que um `Return` distraído deslinke o jogador.

Isso já é o critério de fase 6 *"nenhuma ação destrutiva alcançável por
`Return`"* — e aqui ele vem do original, não do port. No `newWe2002` o mesmo
problema apareceu pelo lado avesso: `PUSHBUTTON` do `.rc` teve de sair com
`autoDefault=false` porque o Qt torna todo botão auto-default (ver o
`CLAUDE.md`).

O Pascal está em [`../../src/impl/ep2002_enlaza.FormShow.inc`](../../src/impl/ep2002_enlaza.FormShow.inc).
