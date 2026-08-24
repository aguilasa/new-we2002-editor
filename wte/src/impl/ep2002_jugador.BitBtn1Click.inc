{ jugador.BitBtn1Click -- 0x00407a80, 6 bytes.
  Spec: wte/re/spec/jugador.BitBtn1Click.md

  O botao `Original ` da ficha. SEIS BYTES no original: uma chamada e um `ret`.
  Desfazer, aqui, e reencher a tela a partir do dado carregado -- o que o
  usuario digitou nos campos some, e o que estava guardado volta.

  NAO GRAVA NADA. A `0x0040756c` so le, e as quatro internas que ela chama
  (`0x00406fb4`, `0x00406fe0`, `0x00407110`, `0x00407338`) nao alcancam a
  `0x00403400`, que e a unica escritora do original.

  ELE ESPEROU UMA MUDANCA DE ESTRUTURA, nao de codigo. A `PreencheFicha` morava
  no `impl/ep2002_mainform.aux.inc`, invisivel de fora, e o `uses` gerado sai na
  INTERFACE -- entao `ep2002_jugador` nao tinha como alcanca-la. A CORR-WTE-091
  desceu a rotina para a `wte_ficha`, que e a unidade neutra que nenhum dos dois
  formularios possui, e com isso o corpo virou o que o original tem: uma
  chamada.

  OS ARGUMENTOS SAO OS DO ESTADO CORRENTE, e nao os do `Sender`: quem escolheu
  time e jogador foi o `mostrar_jugadorClick`, que os deixou em `TimeEmEdicao` e
  `JogadorEmEdicao` antes do `ShowModal`. A ficha e modal, entao nada os move
  enquanto ela esta na tela. A guarda de faixa e a mesma daquele handler, pela
  mesma razao: `IndiceDoJogador` devolve -1 para slot vazio de clube de ML. }
var
  k: Integer;
begin
  REMark('jugador.BitBtn1Click');

  k := IndiceDoJogador(TimeEmEdicao, JogadorEmEdicao);
  if (TimeEmEdicao >= 0) and (JogadorEmEdicao >= 0)
     and (k >= 0) and (k < Length(Jogo.players)) then
    PreencheFicha(Jogo.players[k], TimeEmEdicao, JogadorEmEdicao);
end;
