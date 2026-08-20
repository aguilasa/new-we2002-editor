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

**Nenhum na imagem de CD** neste corpo — nem no `0x0040b9ec`, que só lê.

`0x0040b9ec` (407 B) enche cinco globais a partir do `.mcr`, e o mapa completo,
com o lado escritor ao lado, está em [`../mcr.md`](../mcr.md):

| origem no `.mcr` | passo | total | o quê |
|---|---:|---:|---|
| `0x5910` | 32 | 23 × 10 B | nomes |
| `0x5904` | 32 | 23 × 12 B | atributos |
| `0x5404` | — | 16 B | números de camisa, 5 bits cada |
| `0x63D5` então `0x62A8` | — | 10 B + 20 B | formação, **partida** e remontada contígua |
| tabela `0x00423F84`, 5 entradas | — | 5 × 1 B | cobradores 0..4 |
| `0x6500` | — | 1 B | cobrador 5, o capitão |

**A tática não volta.** O escritor grava seis campos de tática (`0x64E2`,
`0x6102`, `0x6488`, `0x6479`, `0x6497`, `0x64A6`) e este leitor não lê nenhum
deles. Quem lê tática de um `.mcr` é o `boton_mcr2isoClick`, direto do arquivo.

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

*(2026-08-20)* A 28 mapeou o formato — contêiner e conteúdo, em
[`../mcr.md`](../mcr.md) —, e a seção *Bytes tocados* acima já traz o que o
`0x0040b9ec` faz. **O que falta é o Pascal**, e ele depende da unidade
`we2002_mcr` que a mesma task cria.
