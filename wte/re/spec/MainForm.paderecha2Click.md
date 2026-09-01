---
handler: paderecha2Click
formulario: MainForm
endereco: 0x0040e720
veredito: implementado
---

# MainForm.paderecha2Click

A seta `>>`: move os **vinte e três** jogadores do time da esquerda para o da
direita, de uma vez. **316 bytes.**

## Entrada

- `lista_equipos_1.ItemIndex` — o time de origem. **O slot de origem não é
  lido de lugar nenhum**: é o contador do laço, 0..22.
- `lista_equipos_2.ItemIndex`, `lista_jugadores_2.ItemIndex` — o destino.
- `_ficha_movertodos`, a global `0x00432e48` — o resultado do modal decide se o
  laço roda.
- O arquivo aberto (`0x00432e58`) e `WORD[0x004335c0]`.

**Evidência:** disassembly lido

## Saída

```text
guarda := lista_jugadores_2.ItemIndex
se ficha_movertodos.ShowModal <> 6: sai            ' VMT +0xe8; 6 = mrYes

para slot := 0 ate 22:
    0x004046e8(lista_equipos_1.ItemIndex, slot, buffer := 1, arquivo)
    0x00404820(buffer := 1, lista_equipos_2.ItemIndex, slot, arquivo)
                                                   ' retorno DESCARTADO

0x0040b2d8(lista_equipos_2, lista_jugadores_2)     ' sempre, sem condicao
lista_jugadores_2.Update
lista_jugadores_2.ItemIndex := guarda
0x004046e8(lista_equipos_2.ItemIndex,
           lista_jugadores_2.ItemIndex, buffer := 2, arquivo)

casilla_xmlibres.Caption := IntToStr(WORD[0x004335c0])
```

**Evidência:** disassembly lido

## Bytes tocados

**Grava vinte e três vezes**, uma por slot, dentro da `0x00404820` — os mesmos
bytes que o [`paderechaClick`](MainForm.paderechaClick.md) grava uma vez.
Offset por ramo é da
[WTE-TASK-27](../../../docs/tasks/concluidos/27-handlers-de-gravacao.md).

**Evidência:** disassembly lido

## Pré-condições

**Uma, e é de tela:** o modal `ficha_movertodos` tem de voltar `6`. Nada mais é
conferido — nem time selecionado, nem imagem aberta.

O `6` é `mrYes`, e ele não é inferido: o `BitBtn1` do
[`ficha_movertodos.dfm`](../dfm/ficha_movertodos.dfm) declara
`ModalResult = 6`, e o corpo compara com `0x6`.

O port acrescenta o teste de `ItemIndex >= 0`.

**Evidência:** disassembly lido

## Comportamento de erro

**Nenhum, e isso é o achado.** Os 23 códigos de retorno são descartados e a
`0x00403e20` **não é chamada**: mover um elenco inteiro para um time que já
tenha um daqueles jogadores não produz mensagem nenhuma. E o repovoamento da
lista de destino acontece **incondicionalmente**, mesmo que as 23 gravações
tenham sido recusadas.

Comparar com o `paderechaClick`, que chama a `0x00403e20` sempre e só repovoa
com código `>= 0`, é o que mostra que este corpo não é aquele num laço.

**Evidência:** disassembly lido

## Notas

**A tela de confirmação é deste botão, e não do `paderechaeizquierdaClick`.** O
enunciado da [WTE-TASK-26](../../../docs/tasks/concluidos/26-handlers-de-edicao.md)
atribuía o `ficha_movertodos` àquele handler ("a novidade da v0.98 — mover todos
os jogadores de cada time com um clique"). Medido, é este par de botões que a
abre: o global `0x00432e48` que os dois corpos carregam é o
`_ficha_movertodos` **exportado pelo próprio `.exe`**, e o
`paderechaeizquierdaClick` (`0x0040e304`) não toca nesse endereço — o corpo dele
chama `0x00403e20` três vezes e nunca `ShowModal` sobre `0x00432e48`.

A leitura do enunciado é compreensível — "mover todos" é o nome do formulário —,
mas o botão que troca os dois elencos de lugar e o botão que copia um elenco
inteiro são coisas diferentes, e é o segundo que pergunta antes.

**A guarda é lida antes do modal.** Ordem do binário, reproduzida: o
`ItemIndex` do destino é salvo antes de a janela subir, não depois. Não é
observável — nada mexe na lista enquanto o modal está aberto —, mas inverter a
ordem seria escolher por gosto onde há medição.

**Veredito `implementado`:** o Pascal
([`../../src/impl/ep2002_mainform.paderecha2Click.inc`](../../src/impl/ep2002_mainform.paderecha2Click.inc))
faz tudo, gravação inclusive.

Fechado em 2026-08-20 pela oitava passagem da
[WTE-TASK-27](../../../docs/tasks/concluidos/27-handlers-de-gravacao.md): o ramo de
**destino de Master League** da `0x00404820` foi portado, com golden verde
([`golden-10-mover-ml`](../../tests/roteiros/golden-10-mover-ml.txt)) e o
contador de blocos livres vindo da
[WTE-TASK-33](../../../docs/tasks/concluidos/33-slots-de-master-league.md). Com ele a
recusa `-1` passou a ser alcançável e o `casilla_xmlibres` mostra o número de
verdade.

O corpo
compartilhado com o `paizquierda2Click` é a `MoveTodosOsJogadores` do
[`.aux.inc`](../../src/impl/ep2002_mainform.aux.inc).
