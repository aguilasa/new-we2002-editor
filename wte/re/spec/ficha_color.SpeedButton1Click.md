---
handler: SpeedButton1Click
formulario: ficha_color
endereco: 0x00406f34
veredito: trivial
---

# ficha_color.SpeedButton1Click

O ponto de interrogação do editor de cor: abre o `ficha_info`, que lista os
atalhos de copiar e colar cor. Quatorze bytes, uma chamada.

**Evidência:** disassembly lido

## Entrada

A global `_ficha_info` (`0x00432E50`), que o `.exe` exporta com esse nome. Não
lê campo do formulário nem estado.

**Evidência:** disassembly lido

## Saída

```text
ficha_info.ShowModal()
```

O `+0xE8` do VMT de `TForm` é `@Forms@TCustomForm@ShowModal$qqrv` no
`vcl60.bpl` — o mesmo deslocamento aparece nos outros três handlers de abrir
diálogo, e é assim que eles se reconhecem.

O resultado do modal é **descartado**. O `ficha_info` só tem o botão ` Ok`
(`ModalResult = 1`), e nada depende dele.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.**

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

O `ficha_info` é o texto de ajuda dos atalhos que o
[`colorMouseDown`](ficha_color.colorMouseDown.md) implementa — Ctrl + botão
direito copia uma cor, Ctrl + esquerdo cola, com `Shift` são as dezesseis. É a
única documentação do recurso dentro do app.
