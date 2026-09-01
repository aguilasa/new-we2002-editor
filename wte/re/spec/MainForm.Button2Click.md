---
handler: Button2Click
formulario: MainForm
endereco: 0x0040c9c4
veredito: nao portado
---

# MainForm.Button2Click

Nove bytes que encerram o processo — e que **nada alcança**.

**Evidência:** disassembly lido

## Entrada

Nada. Nem o `Sender`.

**Evidência:** disassembly lido

## Saída

```text
exit(0)
```

A mesma `0x0041BEAC` que o
[`SpeedButton2Click`](MainForm.SpeedButton2Click.md) chama depois de confirmar
— aqui **sem** perguntar.

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

## Justificativa

**Handler órfão: existe na published method table e nenhum componente o
referencia.** A coluna `componente` do
[`published_methods.tsv`](../published_methods.tsv) está vazia para esta linha
— a única das 96 nessa situação — e a nota diz `sem referencia em DFM`.
Conferido nos dois sentidos: não há `object Button2:` no
[`MainForm.dfm`](../dfm/MainForm.dfm) nem qualquer `OnClick = Button2Click`.

A tabela sobrevive ao `/STRIP` porque o streaming de DFM precisa dela em tempo
de execução (é o mesmo motivo pelo qual a
[WTE-TASK-04](../../../docs/tasks/concluidos/04-mapa-de-handlers.md) conseguiu recuperar os
96 nomes); o que ela **não** garante é que cada método tenha um componente
ligado. Este é o resto de um botão que o autor apagou do formulário e não do
código.

Portar significaria escrever um corpo que nenhum caminho executa nos dois
lados. A razão é de escopo, não de dificuldade: o corpo tem duas instruções e
já está descrito acima — o que falta é alguém para chamá-lo.

O `dfm2lfm.py` gera a declaração do método a partir da mesma tabela, então o
port tem o `Button2Click` como stub `REStub`, sem ligação no `.lfm`. Os dois
lados concordam: o método existe e ninguém o chama.

## Notas

Se um dia aparecer prova de que algo o alcança — um `.dfm` de outra versão do
editor, ou uma ligação feita em código — este veredito cai junto, e o corpo
está aqui pronto para virar uma linha de Pascal.
