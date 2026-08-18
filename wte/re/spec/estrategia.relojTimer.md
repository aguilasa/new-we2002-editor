---
handler: relojTimer
formulario: estrategia
endereco: 0x00409ba4
veredito: aberto
---

# estrategia.relojTimer

A animação de troca de formação. **936 bytes** — o maior handler do grupo de
edição, e o último dos 28 a ganhar spec.

Trocar de formação **não teleporta** os jogadores: o
[`lista_formacionesClick`](estrategia.lista_formacionesClick.md) calcula um
delta por bola, liga o `reloj` e este handler desliza as dez bolas até o
destino. O `.lfm` dá `Interval = 1` e `Enabled = False` — um milissegundo por
quadro, quatro quadros, e o timer se desliga sozinho.

## Entrada

Seis tabelas em `.bss` e um contador, todos contíguos:

| Endereço | O que é |
|---|---|
| `0x00434238` | destino X, já inteiro |
| `0x00434264` | destino Y, já inteiro |
| `0x00434294` | posição corrente X, `Single` |
| `0x004342c0` | posição corrente Y, `Single` |
| `0x004342ec` | passo X por quadro, `Single` |
| `0x00434318` | passo Y por quadro, `Single` |
| `0x0043428c` | o contador de quadros |

**A contiguidade é o que confirma o tamanho.** Entre bases sucessivas há
`0x2c` = 11 entradas, e logo depois da última vem `0x00434340`, a bola em foco.
O laço percorre `1..10`: a entrada extra é da `bola0`, o goleiro, que não anda.

São `Single` e não `Double` — o original lê com `fld DWORD PTR`, quatro bytes.

**Evidência:** disassembly lido

## Saída

**São dois ramos, e o teste está na primeira instrução.**

```text
se [0x43428c] = 4 entao                     ' o encaixe final
    para i := 1 ate 10:
        bola := form.FindComponent('bola' + i)
        [0x434340] := bola
        bola.Left := campo.Left + [0x434238][i-1]
        bola.Top  := campo.Top  + [0x434264][i-1]
        [0x434348] := form.FindComponent('etiqjug' + i)
        etiqueta.Left := bola.Left - 24
        etiqueta.Top  := bola.Top  + 16
    [0x43428c] := 0
    reloj.Enabled := False
    sai

para i := 1 ate 10:                          ' mais um passo
    bola := form.FindComponent('bola' + i)
    [0x434340] := bola
    [0x434294][i-1] += [0x4342ec][i-1]
    [0x4342c0][i-1] += [0x434318][i-1]
    bola.Left := campo.Left + Trunc([0x434294][i-1])
    bola.Top  := campo.Top  + Trunc([0x4342c0][i-1])
    ... o mesmo para o etiqjug
inc [0x43428c]
```

**O ramo do encaixe não é enfeite.** Depois de quatro somas em ponto flutuante
a posição acumulada não é exatamente o destino; sem ele a formação ficaria um
pixel fora, **sempre no mesmo sentido**. Ler só o segundo ramo daria uma
animação que nunca para e nunca chega ao inteiro que a formação pediu.

O arredondamento é `Trunc`, não `Round`: o original chama o auxiliar da RTL que
põe a FPU em arredondar-para-zero (`fstcw` / `or 0xc01` em `0x00419d80`).

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** As chamadas são `FindComponent`, `CurrToStr`, a concatenação e a
destruição de `AnsiString`, `SetLeft`, `SetTop`, o auxiliar de arredondamento e
`TTimer::SetEnabled`.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma checada. Se as tabelas ainda não foram preenchidas, o handler move as
dez bolas para a origem do `campo` — mas ele só dispara depois que alguém
habilita o `reloj`, e quem habilita é o `lista_formacionesClick`.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. `FindComponent` que devolvesse `nil` estouraria na linha seguinte.

**Evidência:** disassembly lido

## Notas

### O nome da bola sai de `Currency`

O original monta `'bola' + n` com `CurrToStr(n * 10000)`. `Currency` na Borland
é inteiro de 64 bits **escalado por 10.000**, então a multiplicação desfaz a
escala e o texto sai `'1'`, não `'10000'` — o mesmo idioma já visto no
[`iguala_nombresClick`](MainForm.iguala_nombresClick.md). O port usa
`IntToStr`, que dá o mesmo texto sem o rodeio.

### Dois ponteiros de rótulo, não um

`0x00434348` — o `etiqjug` que a animação está movendo — é **diferente** de
`0x00434344`, o rótulo destacado pelo mouse. Os dois andam ao mesmo tempo e
escrevem em rótulos diferentes; fundi-los faria o destaque saltar para a última
bola animada.

### Por que o veredito é `aberto`

Não é a régua de bytes — este handler não grava. É que **quem enche as seis
tabelas é o
[`lista_formacionesClick`](estrategia.lista_formacionesClick.md)**, que ainda
não foi portado. Enquanto ele não existir o `reloj` nunca é habilitado, e este
corpo nunca roda: está escrito e correto, e não há como exercitá-lo na tela.

É também ele que **semeia `0x00434340`** — a bola em foco — antes de qualquer
movimento de mouse. Enquanto isso não acontecer, o port precisa da guarda de
`nil` que os handlers de arrastar carregam e o original não tem.
