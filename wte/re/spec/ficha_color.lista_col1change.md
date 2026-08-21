---
handler: lista_col1change
formulario: ficha_color
endereco: 0x004068b0
veredito: implementado
---

# ficha_color.lista_col1change

Troca o **jogo de uniforme** — `Primeiro` ou `Segundo`. O nome tem `c`
minúsculo, como o `.dfm` o escreve; o gerador não o corrige, porque nome de
handler é chave de busca contra o binário.

**Evidência:** disassembly lido

## Entrada

`lista_col1.ItemIndex` (`[this+0x398]`, e também pelo `Sender`) e
`0x004335cc` (o time em edição).

**Evidência:** disassembly lido

## Saída

```text
0x00405b48()                          ' grava o vetor no jogo ANTERIOR
0x00433dc8 (conjunto) := Sender.ItemIndex
0x00405d6c()                          ' recarrega e pinta as 16
0x004056c8([0x004335cc], lista_col1.ItemIndex)
```

**Evidência:** disassembly lido

## Bytes tocados

Nenhum na imagem.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

### A ordem dos três primeiros passos não comuta

Gravar **antes** de trocar o `conjunto` é o que preserva a edição: sem isso, o
que o usuário mexeu no `Primeiro` some ao ir para o `Segundo`, e o sintoma só
aparece quando ele volta.

### O `ItemIndex` é lido duas vezes

Uma pelo `Sender` (para o `conjunto`) e outra pelo campo `[this+0x398]` (para o
redesenho). São o mesmo combo e o mesmo valor; o original faz as duas leituras
e o port faz o mesmo, porque a diferença é zero e a fidelidade é o critério.
