---
handler: BitBtn1Click
formulario: estrategia
endereco: 0x0040a658
veredito: aberto
---

# estrategia.BitBtn1Click

O ` Default ` da tela de tática. **Seis bytes**, a mesma forma do
[`jugador.BitBtn1Click`](jugador.BitBtn1Click.md): uma chamada e um `ret`.

**Evidência:** disassembly lido

## Entrada

Nada, no corpo.

**Evidência:** disassembly lido

## Saída

```text
preenche_a_tela_de_tatica()     ' 0x0040A0B4
```

A rotina é a mesma que o
[`mostrar_estrategiaClick`](MainForm.mostrar_estrategiaClick.md) chama para
montar a tela — 1.443 bytes, a linha `0x0040a0b4` da
[`auxiliares.md`](../auxiliares.md), que por sua vez chama a
`0x004097D4` e a `0x004099BC`, as duas que o
[`lista_formacionesClick`](estrategia.lista_formacionesClick.md) também usa.

**O rótulo diz ` Default ` e o corpo diz "reconstrói a tela".** As duas
leituras são compatíveis e a spec não escolhe entre elas sem medir: o que está
provado é a chamada.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum** no corpo. A `0x0040A0B4` não alcança a `0x00403400`.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma no corpo.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Justificativa do veredito `aberto`

**A rotina que ele chama não está portada.** O
[`mostrar_estrategiaClick`](MainForm.mostrar_estrategiaClick.md) do port diz
isso no próprio comentário — *"encher a tela de tática (`0x0040a0b4`, 1.443
bytes) é da WTE-TASK-26, dona do formulário `estrategia`"* — e a
[WTE-TASK-26](../../../docs/tasks/26-handlers-de-edicao.md) fechou sem ela. Este
handler é uma chamada só; o que falta é o alvo dela, e o alvo é dívida herdada,
não trabalho de moldura de diálogo.

Portar a `0x0040A0B4` fecha três `aberto` de uma vez — este, o
`mostrar_estrategiaClick` e o [`FormCreate`](estrategia.FormCreate.md) do
mesmo formulário — e é por isso que ela merece ser um lote próprio em vez de
um remendo aqui.

## Notas

O componente se chama `BitBtn1` e o irmão de baixo se chama `BitBtn6` no
`.dfm`, mas o handler dele é `BitBtn3Click`. Nome de componente e nome de
handler são independentes, e é a coluna `componente` do
[`published_methods.tsv`](../published_methods.tsv) que os amarra.
