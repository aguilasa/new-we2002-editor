---
handler: BitBtn1Click
formulario: jugador
endereco: 0x00407a80
veredito: aberto
---

# jugador.BitBtn1Click

O `Original ` da ficha do jogador. **Seis bytes**: uma chamada e um `ret`.

**Evidência:** disassembly lido

## Entrada

Nada, no corpo. Tudo o que importa está na rotina chamada.

**Evidência:** disassembly lido

## Saída

```text
preenche_a_ficha()      ' 0x0040756C
```

É a **mesma** rotina que o
[`mostrar_jugadorClick`](MainForm.mostrar_jugadorClick.md) chama para encher a
ficha antes de mostrá-la — 1.275 bytes, a linha `0x0040756c` da
[`auxiliares.md`](../auxiliares.md). Desfazer, aqui, é reencher a tela a partir
do dado carregado: o que o usuário digitou nos campos some, e o que estava
guardado volta.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** A `0x0040756C` só lê — as quatro internas que ela chama
(`0x00406FB4`, `0x00406FE0`, `0x00407110`, `0x00407338`) não alcançam a
`0x00403400`, que é a única escritora.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma no corpo.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Justificativa do veredito `aberto`

**O port tem a rotina e não a alcança daqui.** A `0x0040756C` está portada como
`PreencheFicha`, e mora em
[`impl/ep2002_mainform.aux.inc`](../../src/impl/ep2002_mainform.aux.inc) porque
quem a estreou foi o `mostrar_jugadorClick`. O `ep2002_mainform` já usa o
`ep2002_jugador` (`jugador.ShowModal`), então `ep2002_jugador` não pode usar o
`ep2002_mainform` na interface — é ciclo de `uses`, e não compila.

É o mesmo problema de estrutura que a
[`wte_render2d`](../../src/wte_render2d.pas) já resolveu uma vez, e com a
solução escrita nas suas próprias palavras: pôr a rotina numa unidade que
**nenhum** dos dois formulários possui, e registrar as dependências nela. A
`PreencheFicha` teria de sair do `.aux.inc` do `MainForm` para uma unidade
neutra, e mover 125 linhas de corpo já verificado é mudança de estrutura, não
de handler — abrir isso dentro de uma task de moldura de diálogo é o oposto de
*"fechar um lote por inteiro"*.

Enquanto isso, o `Original ` fica stub. **Ele não grava nada**, então nenhum
golden fica vermelho por causa dele: o que se perde é o desfazer da ficha.

## Notas

O par `Original `/`Cancela` deste formulário é o mesmo do
[`ficha_color`](ficha_color.BitBtn1Click.md), com os papéis divididos de outro
jeito: lá o `Cancela` desfaz e fecha, aqui ele só
[fecha](jugador.BitBtn2Click.md) — desfazer é exclusivamente deste botão.
