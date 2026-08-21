---
handler: BitBtn2Click
formulario: jugador
endereco: 0x00407a68
veredito: trivial
---

# jugador.BitBtn2Click

O `Cancela` da ficha do jogador. Vinte e um bytes, byte a byte a mesma coisa
que o [`ficha_dorsal.BitBtn1Click`](ficha_dorsal.BitBtn1Click.md) — só muda a
global carregada.

**Evidência:** disassembly lido

## Entrada

Nada.

**Evidência:** disassembly lido

## Saída

```text
this.ModalResult := 1        ' mrOk
jugador.Hide()
```

**O botão diz `Cancela` e devolve `mrOk`.** O `.dfm` traz
`ModalResult = 7` (mrCancel) no `BitBtn2`, e a VCL grava esse 7 no formulário
**antes** de chamar o `OnClick`; o handler o sobrescreve com 1. Quem lê o
resultado ganha "Ok" de um botão chamado "Cancela".

Isso não muda nada hoje, e a razão está do outro lado: o
[`mostrar_jugadorClick`](MainForm.mostrar_jugadorClick.md) **descarta** o
retorno do `ShowModal`. O cancelar do formulário não é o resultado modal — é o
[`BitBtn1`](jugador.BitBtn1Click.md), o `Original `, que recarrega a ficha.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** É o [`BitBtn3`](jugador.BitBtn3Click.md), o `Comple.`, que grava.
Fechar por aqui deixa a imagem como estava.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

O port reproduz a sobrescrita — `ModalResult := mrOk` no corpo — em vez de
"corrigir" para `mrCancel`. Corrigir seria inventar uma diferença que o
original não tem e que ninguém observa, e criaria divergência no dia em que
alguém passasse a ler o resultado.
