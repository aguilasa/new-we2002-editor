---
handler: lista_formacionesClick
formulario: estrategia
endereco: 0x00409aa0
veredito: aberto
---

# estrategia.lista_formacionesClick

Aplica uma das 16 formações predefinidas sobre o time selecionado. 259 bytes,
e o corpo é quase só encaminhamento: lê `lista_formaciones` e chama duas
rotinas.

## Entrada

`lista_formaciones.ItemIndex` — a formação escolhida. É o único campo que o
corpo toca; ele o lê cinco vezes.

**Evidência:** disassembly lido

## Saída

```text
0x004097d4(indice)      ' 474 bytes -- nao lida
0x004099bc(indice)      ' 227 bytes -- nao lida
```

As duas são de uso exclusivo deste handler e do `mostrar_estrategiaClick`
(`0x0040a0b4` também as chama), pelo
[`../auxiliares.md`](../auxiliares.md).

**Evidência:** disassembly lido

## Bytes tocados

**Não medido.** O handler em si não abre arquivo; se a formação vai para a
imagem, vai dentro de `0x004097d4` ou `0x004099bc`. A
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md) é quem responde
isso, porque é ela que trata de gravação.

**Evidência:** nao medido

## Pré-condições

Não confere `ItemIndex = -1` no corpo.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**Este é o handler destrutivo que o enunciado da WTE-TASK-25 manda vigiar:**
aplicar formação predefinida sobre o time selecionado é ação que sobrescreve
estado, disparada por clique em lista. A vigilância pedida — "conferir que ela
não roda durante a carga" — está satisfeita por construção no port: o
`estrategia` só é criado no arranque e só fica alcançável pelo
`mostrar_estrategiaClick`, e nenhum handler de carga toca `lista_formaciones`.

**Veredito `aberto`, com dono nomeado:** o efeito está nas duas rotinas não
lidas, e o que elas fazem é editar tática — que é a
[WTE-TASK-26](../../../docs/tasks/26-handlers-de-edicao.md).
