---
handler: casilla_precioKeyPress
formulario: jugador
endereco: 0x00408b9c
veredito: implementado
---

# jugador.casilla_precioKeyPress

O filtro de tecla do campo de preço. **27 bytes** — treze instruções.

## Entrada

A tecla, por referência (`ecx` aponta para ela, e o original a lê com
`movsx eax,BYTE PTR [ebx]`).

**Evidência:** disassembly lido

## Saída

```text
se tecla <> 8 e não é dígito:  tecla := 0
```

O teste de dígito é a `0x00419070` (o `isdigit` da RTL), e o descarte é
`mov BYTE PTR [ebx],0x0` em `0x00408bb2`.

**Ele é mais curto que o irmão.** O
[`casilla_dorsalKeyPress`](jugador.casilla_dorsalKeyPress.md) encadeia o foco
no `Return` e este **não**: a única comparação além do `isdigit` é contra `8`.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.**

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata — não há o que dar errado.

**Evidência:** disassembly lido

## Notas

O campo nasce desabilitado quando o jogador não tem o campo condicional na
imagem, e aí a ficha mostra o literal `50`. Isso é da `PreencheFicha`, não deste
handler.
