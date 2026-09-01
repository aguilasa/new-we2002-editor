---
handler: FormCreate
formulario: jugador
endereco: 0x00407ce0
veredito: trivial
---

# jugador.FormCreate

## Entrada

Nada da tela e nada da imagem. Os 56 rótulos que ele pinta são achados **por
nome**, com `Classes::TComponent::FindComponent`, e não por campo publicado.

**Evidência:** disassembly lido

## Saída

Uma zebra de duas cores sobre a ficha do jogador:

```text
Color := $00E68F41
para i de 1 a 16:
    se i é ímpar:  hab := $00E68F41 ;  apa := $00D78228
    senão:         hab := $00D78228 ;  apa := $00E68F41
    valorhab<i>.Color := hab
    etiqhab<i>.Color  := hab
    se i <= 12:
        etiqapa<i>.Color  := apa
        valorapa<i>.Color := apa
etiqdorsal.Color := $00D78228     ' campo 0x46c
etiqnombre.Color := $00D78228     ' campo 0x44c
etiqprecio.Color := $00D78228     ' campo 0x3b0
```

As duas cores são RGB(65, 143, 230) e RGB(40, 130, 215) — dois azuis vizinhos,
que é o que faz disso listra e não decoração. A coluna de aparência alterna
**ao contrário** da de habilidade: na linha em que `valorhab` é claro,
`valorapa` é escuro.

Os três campos do fim saem do [`../campos.tsv`](../campos.tsv).

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Os importados chamados são `TControl::SetColor` e
`TComponent::FindComponent`, e nada mais — não há I/O de arquivo.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma checada. O original não confere o resultado de `FindComponent` antes de
usá-lo.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Se um dos 56 rótulos não existisse, `FindComponent` devolveria nulo
e a chamada seguinte cairia — é o mesmo padrão de `FindComponent("dorsal" + N)`
que a [CORR-WTE-044](../../../docs/tasks/concluidos/CORR-WTE-044.md) mediu derrubando o
oráculo. Aqui não cai, porque os 56 existem.

**Evidência:** disassembly lido

## Notas

**O `if i <= 12` não é arbitrário e foi conferido no DFM:** `valorhab`/`etiqhab`
vão de 1 a 16, `etiqapa`/`valorapa` só de 1 a 12. No original isso é um
`cmp ebx,0xc` dentro do laço; se os dois grupos tivessem o mesmo tamanho, o
teste não existiria.

O port **também** acha por nome, em vez de listar os 56 campos: trocaria uma
linha de laço por 56 de repetição. A diferença para o original é que aqui o
`is TLabel` filtra antes de pintar, então rótulo ausente vira nada em vez de
falha de acesso — e os 56 são `TLabel` nos dois lados.

O Pascal está em [`../../src/impl/ep2002_jugador.FormCreate.inc`](../../src/impl/ep2002_jugador.FormCreate.inc).
