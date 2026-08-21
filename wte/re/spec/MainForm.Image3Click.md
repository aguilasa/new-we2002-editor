---
handler: Image3Click
formulario: MainForm
endereco: 0x00410fd0
veredito: implementado
---

# MainForm.Image3Click

O gêmeo do [`ficha_about.imagen_urlClick`](ficha_about.imagen_urlClick.md), no
banner da tela principal. Trinta e seis bytes, a mesma sequência de três
chamadas, e o mesmo destino.

**Evidência:** disassembly lido

## Entrada

O campo `+0x4A4`, que o [`campos.tsv`](../campos.tsv) nomeia `SpeedButton3`
(`TSpeedButton`). O `Sender` não é olhado — o handler atende só o `Image3`,
mas nem o consulta.

**Evidência:** disassembly lido

## Saída

```text
acao := SpeedButton3.Action          ' TControl::GetAction, VMT +0x3C
metodo := FindDynaInst(acao, -17)    ' TContainedAction::Execute
metodo(acao)
```

O `SpeedButton3` do `MainForm` tem `Action = lanza_url` no `.dfm`, e o
`TBrowseURL` daquele `ActionList` traz a **mesma** URL do `ficha_about`,
espaços à direita inclusive.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.**

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**Por que o clique na imagem não chama o botão, e sim a ação dele.** Um
`TImage` não tem `Action` na VCL de 2002 — `TControl.Action` chegou depois —,
então o autor pendurou a ação no `TSpeedButton` ao lado e fez a imagem
disparar a mesma ação por dentro. O efeito visível é uma faixa clicável de
233 px onde o botão tem 25.

Os dois handlers de URL do `.exe` são exatamente estes dois, e são idênticos
até no registrador de trabalho. Só o deslocamento do campo muda.
