---
handler: oscurecerClick
formulario: ficha_color
endereco: 0x004065fc
veredito: implementado
---

# ficha_color.oscurecerClick

Um degrau para baixo em cada canal, em **toda** a faixa selecionada.

**Evidência:** disassembly lido

## Entrada

`0x00433dcc` (`faixa_ini`), `0x00433dd0` (`faixa_fim`), o vetor `0x00433dd4`, e
os dois rádios no fim.

**Evidência:** disassembly lido

## Saída

```text
para i := faixa_ini ate faixa_fim:               ' as duas pontas INCLUSIVE
    canais := decodifica(vetor[i-1])             ' bytes JA expandidos
    se canais[0] > 0:  vetor[i-1] -= 1
    se canais[1] > 0:  vetor[i-1] -= 0x20
    se canais[2] > 0:  vetor[i-1] -= 0x400
    0x00405bc8(i, vetor[i-1])

<poe as tres barras na cor da amostra selecionada>
se boton0.Checked: 0x00405b48(); 0x00405270()
se boton1.Checked: 0x00405b48(); 0x004056c8([0x4335cc], lista_col1.ItemIndex)
```

No original o índice é base zero e começa em `faixa_ini - 1`, com o teste
`< faixa_fim` — o mesmo intervalo fechado, escrito em outra base.

**Evidência:** disassembly lido

## Bytes tocados

Nenhum na imagem.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma além da faixa válida.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata; o piso por canal é a guarda.

**Evidência:** disassembly lido

## Notas

### A faixa é **fechada** aqui e **aberta** no gradiente

Este handler mexe nas duas pontas; o
[`gradienteClick`](ficha_color.gradienteClick.md) não mexe em nenhuma. Os dois
laços se parecem o bastante para alguém escrever um só.

### Não há espaço de cor

A conta é na palavra BGR555 empacotada: `1`, `0x20`, `0x400` — um degrau em cada
campo de cinco bits. A decodificação existe **só para testar o limite**, e o
limite é testado no byte já expandido (`cmp BYTE PTR [ebp+0x0],0x0`). Nem RGB de
oito bits nem HSL entram no caminho.

O piso `> 0` sobre oito bits é o mesmo que `> 0` sobre cinco; o teto do irmão
`clarear` **não** é — ver [`aclararClick`](ficha_color.aclararClick.md).
