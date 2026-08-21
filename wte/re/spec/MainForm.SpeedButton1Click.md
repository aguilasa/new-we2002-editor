---
handler: SpeedButton1Click
formulario: MainForm
endereco: 0x00410fc0
veredito: trivial
---

# MainForm.SpeedButton1Click

O `  Sobre...` da tela principal. Quatorze bytes, e a mesma forma do
[`ficha_color.SpeedButton1Click`](ficha_color.SpeedButton1Click.md) com outro
formulário.

**Evidência:** disassembly lido

## Entrada

A global `_ficha_about` (`0x00432E44`).

**Evidência:** disassembly lido

## Saída

```text
ficha_about.ShowModal()
```

Resultado descartado.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.**

**Evidência:** disassembly lido

## Pré-condições

Nenhuma. O handler não confere imagem aberta nem estado.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**Este botão é a segunda porta para o mesmo formulário.** A primeira é o
arranque: a [`MainForm.FormShow`](MainForm.FormShow.md) chama
`ficha_about.ShowModal()` em `0x004117d7`, e é por isso que o oráculo abre a
janela `Sobre...` sozinho — o lado oráculo do
[`golden-14-uniforme`](../../tests/roteiros/golden-14-uniforme.txt) tem um
passo só para dispensá-la, e o lado port não tem, porque a `FormShow` do port
ainda não a mostra. Essa assimetria é dívida da `FormShow`, não deste handler.

Três dos quatro `SpeedButton1Click` do binário são este mesmo padrão de
quatorze bytes com outro formulário; o quarto — o do
[`ficha_error`](ficha_error.SpeedButton1Click.md) — também. O que os separa é
só a global carregada, e é por isso que a coluna `formulario` do
[`published_methods.tsv`](../published_methods.tsv) é indispensável aqui: sem
ela os quatro são o mesmo nome.
