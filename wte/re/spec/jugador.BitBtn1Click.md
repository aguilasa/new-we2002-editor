---
handler: BitBtn1Click
formulario: jugador
endereco: 0x00407a80
veredito: implementado
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

## O veredito passou a `implementado` em 2026-08-24

A [CORR-WTE-091](../../../docs/tasks/concluidos/CORR-WTE-091.md) fez as duas coisas que
faltavam: desceu a `PreencheFicha` para a [`wte_ficha`](../../src/wte_ficha.pas)
— a unidade neutra que nenhum dos dois formulários possui — e escreveu o corpo,
que virou o que o original tem: uma chamada.

### A régua é um PAR de roteiros, e o par é o que dá sentido a ela

Clicar `Original ` sem ter editado nada antes **passaria com o corpo vazio** —
a ficha já mostra o dado carregado, e reencher com o mesmo valor não muda byte
nenhum. Por isso o gate são dois roteiros que diferem por um único clique:

| Roteiro | O que faz | Byte de número de camisa gravado |
|---|---|---|
| [`golden-18-ficha-edicao`](../../tests/roteiros/golden-18-ficha-edicao.txt) | edita o campo para `7` e grava | `0xc0` |
| [`golden-19-ficha-original`](../../tests/roteiros/golden-19-ficha-original.txt) | edita para `7`, clica `Original `, e grava | `0x80` |

**`0x80` é o valor que a ROM já tinha** em `404748` — conferido no
`roms/japanese-shift-jis.bin` intocado. Ou seja: o `Original ` não devolveu *um*
valor, devolveu **o** valor. Com o corpo vazio os dois roteiros gravariam
`0xc0` e o par não distinguiria nada.

Os quatro gates — controle e golden de cada um — deram **byte-idêntico**, e o
disparo está medido em
[`../fase-4-cobertura.tsv`](../fase-4-cobertura.tsv): `golden-19` dispara este
handler uma vez, `golden-18` nenhuma, que é exatamente a diferença entre eles.

### O que segurava o veredito

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

**A unidade neutra existe desde 2026-08-21, e o que falta aqui encolheu.** A
[CORR-WTE-081](../../../docs/tasks/concluidos/CORR-WTE-081.md) criou a
[`wte_ficha`](../../src/wte_ficha.pas) para o
[`BitBtn3`](jugador.BitBtn3Click.md) e desceu para lá o buffer de jogador
inteiro, com `GravaJogador` e `GravaNumeroDaCamisa`; o `ep2002_jugador` já a
usa. Mover a `PreencheFicha` para o mesmo lugar fecha este handler, e é a única
coisa que ainda falta — a `wte_ficha` pode usar o `ep2002_jugador` na
implementação, que é exatamente o que a rotina precisa para alcançar os
controles da ficha.

Enquanto isso, o `Original ` fica stub. **Ele não grava nada**, então nenhum
golden fica vermelho por causa dele: o que se perde é o desfazer da ficha.

## Notas

O par `Original `/`Cancela` deste formulário é o mesmo do
[`ficha_color`](ficha_color.BitBtn1Click.md), com os papéis divididos de outro
jeito: lá o `Cancela` desfaz e fecha, aqui ele só
[fecha](jugador.BitBtn2Click.md) — desfazer é exclusivamente deste botão.
