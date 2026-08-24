---
handler: casilla_dorsalKeyPress
formulario: jugador
endereco: 0x00408b50
veredito: implementado
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

**A divergência do `SetFocus` fechou na décima segunda passagem da
WTE-TASK-26.** Durante três passagens o port moveu o foco **sempre**, porque
não tinha como avaliar a condição. Agora tem, e não foi pelo caminho que esta
spec previa: em vez de consultar o buffer de 44 bytes, ele faz a mesma
pergunta ao dado — `JogadorTemCampoCondicional`, no
[`we2002_estado`](../../src/we2002_estado.pas), decide pela regra que os dois
oráculos confirmaram, a de que só os times **54 e 55** não têm o campo. O
resultado é o mesmo byte a byte e não obriga a ficha a conhecer o buffer de um
handler de outro formulário, que seria referência circular de unidade.

## O veredito passou a `implementado` em 2026-08-24

Esta seção dizia *"a régua de tela do grupo de edição
(`compara_tela.sh --edicao`) não alcança a ficha do jogador"*, e continua
verdadeira — mas era a régua errada para julgar este handler. Ele filtra tecla
num campo cujo valor **vira byte na imagem**, então quem o julga é o gate de
byte, e a [CORR-WTE-091](../../../docs/tasks/CORR-WTE-091.md) o construiu.

O [`golden-18-ficha-edicao`](../../tests/roteiros/golden-18-ficha-edicao.txt)
limpa o campo com `End`/`shift+Home`/`BackSpace` — nunca `Ctrl+A`, que num
`TEdit` do Win32 não seleciona tudo —, digita `7` e grava pelo `Comple.`. O byte
de número de camisa em `404748` sai `0xc0` contra os `0x80` da ROM intocada:
**a tecla chegou, o filtro a aceitou e o valor chegou ao disco**, dos dois
lados, byte-idêntico ao oráculo em controle e golden.

Medido em [`../fase-4-cobertura.tsv`](../fase-4-cobertura.tsv): **2** disparos
em cada um dos dois roteiros do par — o `KeyPress` do dígito e o do `Return`
implícito na sequência de limpeza.

O ramo que continua sem exercício é o do `50`, e ele tem dono: é o valor que a
ficha mostra quando o jogador não tem o byte condicional, e preço é assunto da
[WTE-TASK-32](../../../docs/tasks/32-preco-do-jogador.md).

### O registro de quando o veredito era `aberto`

O `50` do ramo sem campo é entrada da
[WTE-TASK-32](../../../docs/tasks/32-preco-do-jogador.md): é o valor que a
ficha mostra quando o jogador não tem o byte, e preço é o assunto dela.

Pascal em
[`../../src/impl/ep2002_jugador.casilla_dorsalKeyPress.inc`](../../src/impl/ep2002_jugador.casilla_dorsalKeyPress.inc).
