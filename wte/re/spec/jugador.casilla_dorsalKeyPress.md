---
handler: casilla_dorsalKeyPress
formulario: jugador
endereco: 0x00408b50
veredito: aberto
---

# jugador.casilla_dorsalKeyPress

Filtro de tecla do campo de número de camisa da ficha do jogador. 73 bytes.

## Entrada

`Key` (por referência) e, para o encadeamento de foco, a global `0x004335c4`
e a tabela em `0x00433614`.

**Evidência:** disassembly lido

## Saída

```text
se Key = #13:
    se DWORD[0x00433614 + 44 * global_0x004335c4] <> 0:
        casilla_precio.SetFocus          ' VMT slot 0xc0

se Key <> #8 e Key nao e digito:
    Key := #0
```

**A ordem importa**, e é a do original: primeiro o encadeamento de foco, depois
o filtro. Invertida, o `Return` chegaria zerado ao teste do `#13` e o foco
nunca andaria.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.**

**Evidência:** disassembly lido

## Pré-condições

Nenhuma para o filtro. O `SetFocus` é condicionado à tabela — ver as Notas.

**Evidência:** disassembly lido

## Comportamento de erro

Tecla recusada vira `#0`, que é como a VCL e a LCL descartam no `OnKeyPress`.
Não há aviso, não há bipe.

**Evidência:** disassembly lido

## Notas

**O conjunto aceito é dígito e BackSpace, e nada mais.** O teste de dígito é
`isdigit` da RTL da Borland (`0x00419070`, que é a máscara 4 do `_ctype`),
não uma comparação de faixa escrita à mão como no
[`casilla_nombreKeyPress`](jugador.casilla_nombreKeyPress.md) ao lado. O
resultado é o mesmo para ASCII; a diferença só apareceria num *locale* que
classificasse outro byte como dígito, o que não é o caso aqui.

**Não há teto de valor neste handler.** Ele deixa digitar `999`. Quem impõe a
faixa (32 ou 99, conforme a família do time) é o
[`dorsalClick`](MainForm.dorsalClick.md), pela barra de rolagem da janelinha —
que é outro caminho de edição do mesmo dado. Se o campo da ficha aceita o que
a janelinha recusa, isso é comportamento do original e entra na
[WTE-TASK-36](../../../docs/tasks/36-buffers-e-truncamento.md) como borda a
medir, não como defeito a consertar.

**A condição do `SetFocus` está medida, e ela não é sobre foco — é sobre o dado
existir.**

A tabela em `0x00433614` tem passo de 44 bytes, e o passo é o que a identifica:
é a **terceira coluna de offsets do buffer de jogador**, o registro de 44 bytes
que a rotina `0x004046e8` preenche a partir da imagem
([`../auxiliares.md`](../auxiliares.md)). O buffer tem três campos:

| deslocamento | tamanho | offset de origem | o que é |
|---|---|---|---|
| `0x004335ec + 44*i` | 10 B | `DWORD[0x00433608 + 44*i]` | nome |
| `0x004335f6 + 44*i` | 12 B | `DWORD[0x0043360c + 44*i]` | atributos |
| `0x00433604 + 44*i` | 1 B | `DWORD[0x00433614 + 44*i]` | o campo condicional |

E a condição é a mesma nos dois lugares: **se o offset da terceira coluna for
zero, o campo não existe na imagem** — a `0x004046e8` então escreve `50` no
buffer em vez de ler, e este handler não move o foco para o
`casilla_precio`. Ou seja, o `Return` só avança para o preço quando aquele
jogador **tem** o byte; para os outros o campo é um valor sintético e o
original não deixa o cursor chegar lá.

A global `0x004335c4` que indexa a tabela é, portanto, **qual buffer de jogador
está em edição** — 1 e 2 são os dois lados que os handlers de mover usam.

**Veredito `aberto` ainda assim**, e agora por um motivo menor e nomeado: o
port não tem o buffer de 44 bytes, então não tem como avaliar a condição, e
**move o foco sempre**. O buffer entra com o lote de mover jogador — é a
`0x004046e8` que o preenche —, e esta spec fecha junto com ele.

O `50` do ramo sem campo é entrada da
[WTE-TASK-30](../../../docs/tasks/30-preco-do-jogador.md): é o valor que a
ficha mostra quando o jogador não tem o byte, e preço é o assunto dela.

Pascal em
[`../../src/impl/ep2002_jugador.casilla_dorsalKeyPress.inc`](../../src/impl/ep2002_jugador.casilla_dorsalKeyPress.inc).
