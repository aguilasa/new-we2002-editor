{ MainForm.mostrar_jugadorClick -- 0x0040f8d4, 2.378 bytes.
  Spec: wte/re/spec/MainForm.mostrar_jugadorClick.md

  ESCOPO: navegacao. Das 2.378 instrucoes do original, o que a WTE-TASK-25 deve
  e escolher o par de listas certo, guardar a selecao e mostrar o formulario.
  Encher a ficha -- `0x00404820` e `0x0040756c`, 2.734 bytes -- e editar
  jogador, e isso e da WTE-TASK-26, dona do formulario `jugador`. A divisao
  esta escrita no enunciado da task.

  Um corpo serve dois botoes, e quem decide qual e o `Sender.Name`, nao o
  ponteiro -- ver `LadoTitular` no `.aux.inc`. }
var
  titular: Boolean;
  k: LongInt;
begin
  REMark('MainForm.mostrar_jugadorClick');
  titular := LadoTitular(Sender, 'mostrar_jugador_1');
  if titular then
  begin
    TimeEmEdicao := lista_equipos_1.ItemIndex;
    JogadorEmEdicao := lista_jugadores_1.ItemIndex;
  end
  else
  begin
    TimeEmEdicao := lista_equipos_2.ItemIndex;
    JogadorEmEdicao := lista_jugadores_2.ItemIndex;
  end;
  { A ficha deixou de abrir vazia na decima segunda passagem da WTE-TASK-26: o
    `PreencheFicha` e o `0x0040756c` do original, que este handler chama antes
    de mostrar o formulario. O indice do jogador dentro de `Jogo.players` sai
    do mesmo `IndiceDoJogador` que a lista usou para escrever o nome. }
  k := IndiceDoJogador(TimeEmEdicao, JogadorEmEdicao);
  if (TimeEmEdicao >= 0) and (JogadorEmEdicao >= 0)
     and (k >= 0) and (k < Length(Jogo.players)) then
    PreencheFicha(Jogo.players[k], TimeEmEdicao, JogadorEmEdicao);
  jugador.ShowModal;
end;
