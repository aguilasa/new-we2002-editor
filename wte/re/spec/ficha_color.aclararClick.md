---
handler: aclararClick
formulario: ficha_color
endereco: 0x00406744
veredito: implementado
---

# ficha_color.aclararClick

Espelho exato do [`oscurecerClick`](ficha_color.oscurecerClick.md): um degrau
para **cima** em cada canal, na faixa fechada.

**Evidência:** disassembly lido

## Entrada

A mesma do irmão.

**Evidência:** disassembly lido

## Saída

```text
para i := faixa_ini ate faixa_fim:
    canais := decodifica(vetor[i-1])
    se canais[0] < 0xF8:  vetor[i-1] += 1
    se canais[1] < 0xF8:  vetor[i-1] += 0x20
    se canais[2] < 0xF8:  vetor[i-1] += 0x400
    0x00405bc8(i, vetor[i-1])

<poe as tres barras na cor da amostra selecionada>
se boton0.Checked: 0x00405b48(); 0x00405270()
se boton1.Checked: 0x00405b48(); 0x004056c8([0x4335cc], lista_col1.ItemIndex)
```

**Evidência:** disassembly lido

## Bytes tocados

Nenhum na imagem.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma além da faixa válida.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata; o teto por canal é a guarda.

**Evidência:** disassembly lido

## Notas

### `0xF8` prova que a expansão é deslocamento

`0xF8` é `31 shl 3` = **248**, não 255. Se a expansão de cinco para oito bits
fosse a regra de três `v * 255 / 31`, o teto seria `0xFF`. Um port que
expandisse assim teria branco diferente do original em toda camisa clara — e
teria o teto errado junto, porque os dois números são o mesmo número.

O `cmp BYTE PTR [ebp+0x0],0xf8` está entre os padrões que o
[`dump_render2d.py`](../../tools/dump_render2d.py) **exige** encontrar; o
operando dele é de onde sai a constante `RENDER_MAXIMO` do Pascal.
