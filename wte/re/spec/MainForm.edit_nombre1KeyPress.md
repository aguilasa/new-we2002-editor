---
handler: edit_nombre1KeyPress
formulario: MainForm
endereco: 0x0040d36c
veredito: implementado
---

# MainForm.edit_nombre1KeyPress

Filtro de tecla do primeiro campo de nome do time. 88 bytes.

## Entrada

`Key`, por referência.

**Evidência:** disassembly lido

## Saída

```text
se Key = #13:  edit_nombre2.SetFocus        ' VMT slot 0xc0
se Key nao esta em { ' ', '.', #8, '0'..'9', 'A'..'Z', 'a'..'z' }:  Key := #0
```

Primeiro o foco, depois o filtro — invertida a ordem, o `Return` chegaria
zerado ao teste do `#13` e o foco nunca andaria.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.**

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Tecla recusada vira `#0`, sem aviso.

**Evidência:** disassembly lido

## Notas

Os três campos de nome formam uma corrente de foco — `nombre1 → nombre2 →
nombre3` — e o terceiro **não** encadeia: ver
[`edit_nombre3KeyPress`](MainForm.edit_nombre3KeyPress.md), que também tem
filtro mais estreito.

O conjunto aceito é o mesmo do filtro de exibição de nome do original
(`0x0040b2d8`, medido na WTE-TASK-25) e o mesmo do
[`casilla_nombreKeyPress`](jugador.casilla_nombreKeyPress.md) da ficha:
letra, dígito, ponto e espaço.

**Não há limite de comprimento aqui.** Ele vem do `MaxLength` que o original
põe no campo ao carregar a imagem, e **o port não põe** — divergência aberta,
registrada na [spec do `iguala_nombresClick`](MainForm.iguala_nombresClick.md)
e entrada da [WTE-TASK-36](../../../docs/tasks/36-buffers-e-truncamento.md).

Pascal em
[`../../src/impl/ep2002_mainform.edit_nombre1KeyPress.inc`](../../src/impl/ep2002_mainform.edit_nombre1KeyPress.inc).
