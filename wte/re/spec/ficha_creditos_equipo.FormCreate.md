---
handler: FormCreate
formulario: ficha_creditos_equipo
endereco: 0x0040b034
veredito: trivial
---

# ficha_creditos_equipo.FormCreate

## Entrada

Nada. O corpo não lê estado nenhum — nem da tela, nem da imagem, nem de
global. O único operando é a instância do próprio formulário, carregada do
global `0x0043435c`.

**Evidência:** disassembly lido

## Saída

`Color := $003CDCDC` sobre o próprio formulário — RGB(220, 220, 60).

O DFM declara `Color = clBtnFace`, e **essa cor nunca aparece na tela**: o
`OnCreate` a substitui antes de o formulário ser exibido. É a forma `cor` do
[`../arranque.md`](../arranque.md), medida nos 18 `FormCreate`/`FormShow`.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** O corpo tem 15 bytes e uma única chamada, para
`TControl::SetColor`; não há I/O de arquivo em lugar nenhum dele.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma. Não checa nada.

**Evidência:** disassembly lido

## Comportamento de erro

Não há entrada, então não há entrada inválida.

**Evidência:** disassembly lido

## Notas

`TColor` da VCL é `$00BBGGRR`, **não** `#RRGGBB`. O `TColor` da LCL é o mesmo,
então o literal atravessa sem conversão — mas trocar a ordem por engano daria
um formulário laranja onde o original é azul.

O Pascal está em [`../../src/impl/ep2002_creditos_equipo.FormCreate.inc`](../../src/impl/ep2002_creditos_equipo.FormCreate.inc).
