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

O laço vai de 0 a 22 (`cmp DWORD PTR [ebp-0x2c],0x17` em `0x00411178`) e grava
22 bytes. Medido em seis times: vão de `CONDICIONAL_BASE + 23·t` até `+ 21`, e o
do slot 22 fica com o valor de fábrica em todos. No time 9 o slot 21 e o 22 têm
a **mesma** soma e a **mesma** posição, e só o 21 é gravado — o que descarta
explicação pelo conteúdo do jogador.

**O `je` da terceira coluna não é a causa**, ao contrário do que esta seção
afirmou até 2026-08-24. A [CORR-WTE-095](../../../docs/tasks/CORR-WTE-095.md)
instrumentou a corrida com `strace` (`diff_dirigido.sh`) e mediu que o oráculo
**lê** o byte condicional do slot 22 em 3067472, com o mesmo número de seeks dos
outros 22 — e a `0x004046e8` só faz essa leitura quando a coluna **não** é zero
(`0x00404748` desvia para `0x0040477e` no caso zero, e ali não há I/O).

O byte se perde na **escrita**: as sequências de syscall do slot 21 e do slot 22
são idênticas até o `fseek` da gravação, e depois dele o 21 emite
`write(fd,"\25",1)` e o 22 não emite nada. Um `0xFF` plantado em 3067472
sobrevive à corrida. É dentro da `0x00403400`, entre o `fseek` de `0x00403410` e
o `fputc` de `0x0040342a`; a `0x00403388` chamada em seguida não é flush, é o
caminhador de setor MODE2/2352.

Duas coisas ficam **fechadas** por isso: a conta de offset do port não está
errada para o slot 22 (a `0x00404374` decide por time, nunca por slot), e o
slot 22 é endereçável — o `io-medido.tsv`, sessão `27-mcr2iso`, mostra o import
de `.mcr` gravando os **23** bytes condicionais do time 3. **Aberto** continua o
mecanismo da perda. O port reproduz o oráculo, porque é contra ele que o gate
mede.

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
