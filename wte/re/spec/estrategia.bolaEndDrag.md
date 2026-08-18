---
handler: bolaEndDrag
formulario: estrategia
endereco: 0x004097a4
veredito: implementado
---

# estrategia.bolaEndDrag

Fim do arrasto, **por qualquer caminho** — inclusive soltar fora do retângulo,
que é o caso que o [`rectanguloDragDrop`](estrategia.rectanguloDragDrop.md) não
vê. **48 bytes**.

## Entrada

Os globais `0x00434340` e `0x00434344`.

**Evidência:** disassembly lido

## Saída

```text
[0x434340].Enabled := True        ' VMT[0x64]
[0x434344].Visible := True
rectangulo.Visible := False
```

Exatamente o `rectanguloDragDrop` mais a linha do rótulo.

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

Soltar **fora** do retângulo não desfaz o movimento: a bola fica onde o último
`rectanguloDragOver` a deixou, que é dentro da zona, porque só há `DragOver`
enquanto o ponteiro está sobre o retângulo. A restrição de zona, portanto, não
é um teste — é uma consequência geométrica de o alvo do arrasto ser o próprio
retângulo.
