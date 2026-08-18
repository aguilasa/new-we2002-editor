---
handler: rectanguloDragDrop
formulario: estrategia
endereco: 0x00409780
veredito: implementado
---

# estrategia.rectanguloDragDrop

Soltar a bola dentro do retângulo. **36 bytes** — o menor handler do grupo.

## Entrada

Só o global `0x00434340`.

**Evidência:** disassembly lido

## Saída

```text
[0x434340].Enabled := True        ' VMT[0x64]
rectangulo.Visible := False
```

**Ele não move a bola.** A posição já foi escrita a cada passagem do
[`rectanguloDragOver`](estrategia.rectanguloDragOver.md); soltar só encerra o
estado visual.

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

**Repare no que ele não faz que o irmão faz:** não devolve o rótulo à
visibilidade. Quem fecha isso é o [`bolaEndDrag`](estrategia.bolaEndDrag.md),
que a VCL dispara em seguida. Os dois são complementares e portar só um
deixaria o `etiqjug` sumido depois do primeiro arrasto — sintoma que pareceria
bug de desenho, não de handler faltando.
