---
handler: base_teamClick
formulario: MainForm
endereco: 0x00410ff4
veredito: aberto
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

## Justificativa do veredito `aberto`

**É preço, e preço é da
[WTE-TASK-32](../../../docs/tasks/32-preco-do-jogador.md).** A tabela *"o que
fica de fora"* da [WTE-TASK-30](../../../docs/tasks/30-handlers-auxiliares.md)
já manda os dois handlers de preço do formulário `jugador` para lá, com o
critério certo — *"são fórmula, não diálogo"* —, e não lista este porque a task
foi escrita antes de alguém ler o corpo dele. Medido, ele é o mesmo assunto: a
mensagem que ele mostra é `Precos dos jogadores calculados!!!!!!!!!!!`.

O `CLAUDE.md` do repositório sempre soube que a feature tem duas metades —
*"preço derivado dos atributos (do jogador ou do time inteiro)"*. A metade do
time inteiro é este handler.

**A moldura fica pronta aqui e o miolo não**, que é exatamente a divisão que o
enunciado da 30 pede: o `ficha_creditos_equipo` é um dos 13 diálogos
auxiliares, e o que falta é a `formula(soma)` e a `0x00403278`.

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
