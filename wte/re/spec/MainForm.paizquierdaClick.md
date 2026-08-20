---
handler: paizquierdaClick
formulario: MainForm
endereco: 0x0040e4b0
veredito: implementado
---

# MainForm.paizquierdaClick

A seta `<`: move **um** jogador do time da direita para o da esquerda.
**312 bytes**, e é uma cópia literal do
[`paderechaClick`](MainForm.paderechaClick.md) com os quatro campos de combo
trocados e o `1`/`2` invertido. A medição inteira — buffer de 44 bytes,
identidade, códigos de recusa, slots de VMT — está naquela spec; aqui fica o
que é próprio deste corpo.

## Entrada

- `lista_equipos_2.ItemIndex`, `lista_jugadores_2.ItemIndex` — a origem.
- `lista_equipos_1.ItemIndex`, `lista_jugadores_1.ItemIndex` — o destino.
- O arquivo aberto (`0x00432e58`) e `WORD[0x004335c0]`.

**Evidência:** disassembly lido

## Saída

```text
guarda := lista_jugadores_1.ItemIndex          ' o DESTINO

0x004046e8(lista_equipos_2.ItemIndex,
           lista_jugadores_2.ItemIndex, buffer := 2, arquivo)
codigo := 0x00404820(buffer := 2,
                     lista_equipos_1.ItemIndex,
                     lista_jugadores_1.ItemIndex, arquivo)

se codigo >= 0:
    0x0040b2d8(lista_equipos_1, lista_jugadores_1)
    lista_jugadores_1.Update
    lista_jugadores_1.ItemIndex := guarda
    0x004046e8(lista_equipos_1.ItemIndex,
               lista_jugadores_1.ItemIndex, buffer := 1, arquivo)

casilla_xmlibres.Caption := IntToStr(WORD[0x004335c0])
0x00403e20(codigo)
```

**O buffer acompanha o lado da tela, não o papel na operação.** Este handler lê
para o buffer 2 (o direito) e recarrega o 1 (o esquerdo) no fim; o
`paderechaClick` faz o contrário. É a mesma numeração nos dois, e é por isso que
ela não pode ser lida como "origem/destino".

**Evidência:** disassembly lido

## Bytes tocados

**Grava**, dentro da `0x00404820`, como o `paderechaClick`. Offset por ramo é da
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md).

**Evidência:** disassembly lido

## Pré-condições

**Nenhuma**, como o irmão. O port acrescenta o teste de `ItemIndex >= 0`.

**Evidência:** disassembly lido

## Comportamento de erro

As mesmas duas recusas (`-2` jogador repetido, `-1` sem bloco de ML livre),
pela mesma `0x00403e20`. Ver
[`MainForm.paderechaClick.md`](MainForm.paderechaClick.md).

**Evidência:** disassembly lido

## Notas

**Veredito `implementado`, pela mesma razão que o irmão:** o Pascal
([`../../src/impl/ep2002_mainform.paizquierdaClick.inc`](../../src/impl/ep2002_mainform.paizquierdaClick.inc))
faz tudo, gravação inclusive.

Fechado em 2026-08-20 pela oitava passagem da
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md): o ramo de
**destino de Master League** da `0x00404820` foi portado, com golden verde
([`golden-10-mover-ml`](../../tests/roteiros/golden-10-mover-ml.txt)) e o
contador de blocos livres vindo da
[WTE-TASK-33](../../../docs/tasks/33-slots-de-master-league.md). Com ele a
recusa `-1` passou a ser alcançável e o `casilla_xmlibres` mostra o número de
verdade.

O corpo compartilhado dos quatro botões da família mora em
[`../../src/impl/ep2002_mainform.aux.inc`](../../src/impl/ep2002_mainform.aux.inc)
(`MoveUmJogador`), porque no binário eles são quatro cópias que só trocam
argumento — duplicar o corpo no port copiaria a repetição sem copiar nada que
ela signifique.
