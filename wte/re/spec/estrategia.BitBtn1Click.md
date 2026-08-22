---
handler: BitBtn1Click
formulario: estrategia
endereco: 0x0040a658
veredito: implementado
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

## Como o veredito fechou

**O alvo chegou.** A `0x0040A0B4` está portada como `PreencheTelaDeTatica`, na
[`wte_tatica`](../../src/wte_tatica.pas), pela
[CORR-WTE-082](../../../docs/tasks/CORR-WTE-082.md); este handler voltou a ser
o que sempre foi, uma chamada só.

**Ele não relê a imagem, e isso é a única sutileza.** O original chama apenas a
`0x0040A0B4`, que trabalha sobre as globais que o `mostrar_estrategiaClick`
encheu ao abrir. Reler aqui daria o mesmo resultado hoje e deixaria de dar no
dia em que algo gravasse com o formulário aberto — e o
[` Accept`](estrategia.BitBtn3Click.md) faz exatamente isso.

A conferência é a do grupo de leitura: `compara_tela.sh --malha` nos três times
`0`, `2` e `63`, com as quatro posições de marcador batendo com o oráculo antes
e depois do clique.

## Notas

O componente se chama `BitBtn1` e o irmão de baixo se chama `BitBtn6` no
`.dfm`, mas o handler dele é `BitBtn3Click`. Nome de componente e nome de
handler são independentes, e é a coluna `componente` do
[`published_methods.tsv`](../published_methods.tsv) que os amarra.
