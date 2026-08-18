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

### De onde saem as seis tabelas, e quem liga o timer

**Da auxiliar `0x004097d4`**, não do handler que a chama — a CORR-WTE-062 mediu
isto em 2026-08-18. As fórmulas:

```text
DestinoX[i] := x[i]*8 - 2
DestinoY[i] := ((y[i] - 3) div 2)*5 - 7
DeltaX[i]   := (DestinoX[i] - AtualX[i]) * 0.2
```

O `x` e o `y` vêm da tabela de formações de `0x00433f0c`
([`../formacoes.md`](../formacoes.md)); o `0.2` é um `long double` de 80 bits
em `0x004099b0`, decodificado e não escrito à mão.

**O `0.2` muda a leitura do ramo de encaixe.** Quatro quadros a 0.2 cobrem
**80%** do trajeto, e o encaixe dá o último quinto de uma vez. Esta spec dizia
que ele corrigia "um pixel fora, sempre no mesmo sentido"; é um quinto do
caminho, não um pixel. O texto do `.inc` foi corrigido junto.

`0x004097d4` também é quem faz `reloj.Enabled := True` e quem **semeia
`0x00434340`**, a bola em foco, antes de qualquer movimento de mouse.

### Por que o veredito continua `aberto`

Não é a régua de bytes — este handler não grava. E não é mais o
`lista_formacionesClick`, que está portado. É que `0x004097d4` é chamada
**também** por `0x0040a0b4`, a rotina que enche a tela de tática ao abrir o
formulário: no original a animação roda **na abertura**, deslizando as bolas
das posições de projeto até a formação do time. `0x0040a0b4` não está portada —
é do grupo de carga, pelo `MainForm.mostrar_estrategiaClick` —, então no port
este corpo só roda depois de um clique em `lista_formaciones`.

Isso é exercitável na tela, ao contrário do que esta spec afirmava: basta abrir
a tática e clicar num item. O que não é exercitável é o caminho de abertura.
