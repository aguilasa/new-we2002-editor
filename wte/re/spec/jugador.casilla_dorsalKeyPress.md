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

**Veredito `aberto`, e é a condição do `SetFocus` que o segura.** A tabela em
`0x00433614` tem passo de 44 bytes e é indexada pela global `0x004335c4`; o que
ela guarda **não foi medido**. O port move o foco **sempre**, o que é
divergência declarada: na pior das hipóteses ele foca um campo que o original
teria deixado quieto. Medir isso é barato quando a ficha do jogador estiver
sendo preenchida — a mesma global deve aparecer lá — e é o que fecha esta spec.

Pascal em
[`../../src/impl/ep2002_jugador.casilla_dorsalKeyPress.inc`](../../src/impl/ep2002_jugador.casilla_dorsalKeyPress.inc).
