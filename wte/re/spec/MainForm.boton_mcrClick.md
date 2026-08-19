---
handler: boton_mcrClick
formulario: MainForm
endereco: 0x0040c2c8
veredito: aberto
---

# MainForm.boton_mcrClick

Abre o diálogo de arquivo do **memory card** (`.mcr`) e carrega o que ele
contém. 418 bytes, mais `0x0040b9ec` (407 B) que faz o trabalho.

## Entrada

- `dialogo_mcr`, o `TOpenDialog` do formulário;
- `lista_equipos.ItemIndex`, para compor o nome sugerido.

**Evidência:** disassembly lido

## Saída

```text
se dialogo_mcr.Execute:
    texto_mcr.Caption := <nome do arquivo>
    0x0040b9ec(...)          ' le o conteudo do .mcr
    boton_mcr2iso.Enabled := verdadeiro
```

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum na imagem de CD** neste corpo. O que `0x0040b9ec` faz com o conteúdo
do `.mcr` não foi lido.

**Evidência:** disassembly lido

## Pré-condições

`Execute` falso sai sem efeito.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata no corpo do handler.

**Evidência:** disassembly lido

## Notas

**Veredito `aberto`, com dono nomeado:** o formato `.mcr` é a
[WTE-TASK-28](../../../docs/tasks/28-import-de-mcr.md), que trata de import e
export de memory card. Este handler é a porta de entrada dela, e implementá-lo
sem a 28 seria abrir um diálogo que não leva a lugar nenhum.
