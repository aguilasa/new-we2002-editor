---
handler: lista_col2Change
formulario: ficha_color
endereco: 0x004068ec
veredito: divergencia deliberada
---

# ficha_color.lista_col2Change

O combo de **chuteira**, `BOOTS TYPE`. Estruturalmente é o
[`lista_col1change`](ficha_color.lista_col1change.md) sem o redesenho.

**Evidência:** disassembly lido

## Entrada

`lista_col2.ItemIndex`, pelo `Sender`.

**Evidência:** disassembly lido

## Saída

```text
0x00405b48()                          ' grava o vetor na fonte anterior
0x00433dc8 (conjunto) := Sender.ItemIndex
0x00405d6c()                          ' recarrega e pinta as 16
```

**Evidência:** disassembly lido

## Bytes tocados

Nenhum na imagem.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

### Ele escreve o **mesmo** global que o `lista_col1change`

`0x00433dc8` é "qual conjunto dentro da família", e quem decide de qual combo
ele veio é a família corrente. É o que o
[`botonClick`](ficha_color.botonClick.md) formaliza ao ler o `ItemIndex` de
`lista_col1` ou de `lista_col2` conforme a família seja 1 ou 2.

### A divergência: a família 2 não tem fonte neste port

As cores de chuteira estão em `0x00433096 + conjunto * 32`, e o `we2002_core`
— o oráculo de formato deste projeto — não tem campo de chuteira em `TTeam` nem
em `TMlTeam`. Descobrir onde elas moram na imagem é trabalho que ninguém pediu,
e a família ficou de fora com endereço escrito (ver
[`wte_cor.pas`](../../src/wte_cor.pas)).

O `conjunto` é escrito assim mesmo, porque é **estado do editor** e não dado.
O que não acontece é o preenchimento achar fonte: ele devolve `False` e não
pinta. **O original pinta**, com o ponteiro de fonte não inicializado — o mesmo
comportamento indefinido que o `botonClick` já descreve.

Na prática o combo está `Enabled = False` no `.dfm`: só o `botonClick` o
alcança, e ele o alcança para ler, não para disparar este handler. Entrada para
a [WTE-TASK-35](../../../docs/tasks/concluidos/35-divergencias-deliberadas.md).
