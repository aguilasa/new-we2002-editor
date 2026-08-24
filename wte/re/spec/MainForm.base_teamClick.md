---
handler: base_teamClick
formulario: MainForm
endereco: 0x00410ff4
veredito: implementado
---

# MainForm.base_teamClick

Os rótulos `Time Tit.` e `Time Res.`, os dois com o `Hint`
`Calcular precos           `. Um corpo para os dois, 484 bytes — e é a
**segunda metade da feature de preço**: o preço do time inteiro, num clique.

**Evidência:** disassembly lido

## Entrada

- o `Sender`, comparado com o campo `+0x3AC` (`base_team`, `TStaticText`) para
  decidir de qual combo tirar o time — `+0x390` (`lista_equipos_1`) para o
  titular, `+0x384` (`lista_equipos_2`) para o reserva;
- a posição e a largura do `MainForm` (`+0x40` e `+0x48`), para colocar o
  diálogo;
- a terceira coluna de offset do jogador, em `0x0043366C`;
- os doze atributos do jogador carregado, em `0x0043364E` e `0x0043364F`;
- uma tabela de 16 linhas de 12 bytes em `0x00423648`.

Os três nomes de campo saem do [`campos.tsv`](../campos.tsv).

**Evidência:** disassembly lido

## Saída

```text
se Sender = base_team:
    time := lista_equipos_1.ItemIndex
    ficha_creditos_equipo.Left := MainForm.Left - 65
senao:
    time := lista_equipos_2.ItemIndex
    ficha_creditos_equipo.Left := MainForm.Left + MainForm.Width - 200

se ficha_creditos_equipo.ShowModal() = 7:   ' mrCancel
    sai

para slot := 0 ate 22:
    carrega_jogador(time, slot, buffer := 2)      ' 0x004046E8
    se terceira_coluna_de_offset <> 0:
        soma := 0
        para k := 0 ate 15:
            soma := soma + pesa(atributo_a, atributo_b, tabela[k])   ' 0x00403278
        preco := formula(soma)
        se atributos_a_e_b_derem_zero: preco := preco * 5 div 3
        grava 1 byte de preco no offset da terceira coluna   ' 0x00403400

ficha_info3.etiq1 := 'Precos dos jogadores calculados!!!!!!!!!!!'
ficha_info3.ShowModal()
```

A cadeia sai do `.exe` em `0x00425079`. A `formula(soma)` está no corpo entre
`0x004110E7` e `0x0041112A` e é aritmética inteira pura sobre `soma`, com as
constantes `0x2DC6C0` (3.000.000), `0x9C40` (40.000), `0x2BC` (700), `7` e um
`+5` final; a variante `× 5 div 3` está em `0x00411142`.

**Evidência:** disassembly lido

## Bytes tocados

**Um byte por jogador**, no offset que a terceira coluna da tabela de offsets
dá — o mesmo campo condicional que a
[`auxiliares.md`](../auxiliares.md) descreve na `0x004046E8` (*"1 B que só
existe se a terceira coluna da tabela de offsets não for zero"*). São até 23
bytes por clique, um por slot do time, e nenhum para os times cuja coluna é
zero.

**Evidência:** disassembly lido

## Pré-condições

A confirmação do `ficha_creditos_equipo`: resultado `7` (`mrCancel`) sai sem
gravar nada. E a coluna de offset não nula, por jogador — quem a tem zerada é
pulado dentro do laço.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Não confere imagem aberta nem índice de time válido; `ItemIndex`
igual a `-1` entraria no laço.

**Evidência:** disassembly lido

## O veredito passou a `implementado` em 2026-08-24

A [WTE-TASK-32](../../../docs/tasks/32-preco-do-jogador.md) fechou as duas
metades. A moldura era da WTE-TASK-30; o miolo — a `formula(soma)` e a soma que
a alimenta — está em [`../preco.md`](../preco.md), com a fórmula, as três
armadilhas dela e a tabela de verdade.

**A régua é de byte, e é a que este handler pedia.** O
[`golden-22-precos`](../../tests/roteiros/golden-22-precos.txt) clica o rótulo,
confirma no `ficha_creditos_equipo` e compara a imagem inteira: controle e
golden, byte-idêntico. Mais a tabela de verdade de **132 jogadores em 6 times**,
100% de acerto ([`check_preco.py`](../../tools/check_preco.py)).

**A `0x00403278` não foi portada, e é decisão.** Ela é o decodificador de
atributo do original; este port tem o dele, transpilado do `we2002_core` e
conferido contra as duas ROMs desde a fase 3. Portá-la seria ter dois
decodificadores e duas verdades.

### O achado: ele preça 22 slots, não 23

O laço vai de 0 a 22 (`cmp DWORD PTR [ebp-0x2c],0x17` em `0x00411178`), mas cada
volta pula o slot quando a terceira coluna do buffer é zero — e **para o slot 22
ela sai zero**. Medido em seis times: os bytes gravados vão de
`CONDICIONAL_BASE + 23·t` até `+ 21`, e o do slot 22 fica com o valor de fábrica
em todos. No time 9 o slot 21 e o 22 têm a **mesma** soma e a **mesma** posição,
e só o 21 é gravado — o que descarta explicação pelo conteúdo do jogador.

A causa está aberta na
[CORR-WTE-095](../../../docs/tasks/CORR-WTE-095.md), e ela já mediu duas coisas
em 2026-08-24. O salto **é real**: plantados `0xFF` nos slots 20, 21 e 22 do
time 2, o oráculo devolveu 26 e 21 nos dois primeiros — o `previsto` do
`preco.tsv` — e deixou o terceiro em 255. E a `0x00404374` **não tem ramo por
slot**: ela decide por time (`cmp ecx,0x3f`, `cmp ecx,0x35`, `cmp ecx,0x38`, os
times 54 e 55) e escreve a mesma conta linear em slot para os 23. Logo a conta
de offset do port **não está errada** para o slot 22 — o que sobra em aberto é
o laço observar zero num campo que a rotina anterior sempre preenche.
O port reproduz o oráculo, porque é contra ele que o gate mede.

## Notas

**Este handler grava na imagem, e a task de preço precisa saber disso.** A
[WTE-TASK-32](../../../docs/tasks/32-preco-do-jogador.md) foi descrita como
*"isolada, não depende de gravação"* — verdade para o
`jugador.etiqprecioClick`, que só mostra o número na tela, e **falso** para
este, que percorre 23 jogadores e escreve um byte em cada. A régua da 32 tem de
ser dupla: tela para a fórmula, byte para este.

Os dois rótulos são `TStaticText`, não botão. Quem separa titular de reserva é
o **ponteiro** do `Sender` comparado com o campo, e não o nome — diferente do
[`mostrar_jugadorClick`](MainForm.mostrar_jugadorClick.md), que compara nome.
Vale anotar porque o port tem o `LadoTitular` justamente para o caso do nome, e
ele não serve aqui.
