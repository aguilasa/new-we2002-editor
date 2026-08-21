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
  { O BUFFER DE JOGADOR, e ele so passou a importar quando o `Comple.` ganhou
    dono (CORR-WTE-081): o `BitBtn3Click` grava A PARTIR do buffer, entao ele
    tem de estar carregado antes de a ficha aparecer.

    O original faz os quatro em fila, em `0x0040f955`..`0x0040fa22`: o indice
    do buffer (1 para o lado esquerdo, 2 para o direito), o par (time, slot), o
    numero de camisa pela `0x00403f00` e a carga pela `0x004046e8`. }
  if titular then
    BufferDaFicha := BUF_ESQUERDA
  else
    BufferDaFicha := BUF_DIREITA;
  NumeroNaFicha := NumeroDaCamisa(TimeEmEdicao, JogadorEmEdicao);
  CarregaJogador(TimeEmEdicao, JogadorEmEdicao, BufferDaFicha);

  { O NOME QUE A FICHA MOSTRA sai do ITEM DA LISTA, nao do disco -- o
    `0x0040fa8c` faz `0x004335d4 := Copy(<item>, i, 14)`. A diferenca nao e
    academica: o item ja passou pelo filtro do `0x0040b2d8`, e e ele que o
    `Comple.` grava de volta. Aqui `NomeDoJogador` e a mesma coisa, porque a
    lista e enchida com ele. }
  NomeNaFicha := NomeDoJogador(TimeEmEdicao, JogadorEmEdicao);

  k := IndiceDoJogador(TimeEmEdicao, JogadorEmEdicao);
  if (TimeEmEdicao >= 0) and (JogadorEmEdicao >= 0)
     and (k >= 0) and (k < Length(Jogo.players)) then
    PreencheFicha(Jogo.players[k], TimeEmEdicao, JogadorEmEdicao);

  { A VALVULA DA RECUSA `-2`, ligada SO enquanto a ficha esta na tela --
    `mov BYTE ds:0x423168,1` em `0x0040ffb3`, `ShowModal` em `0x0040ffc6`,
    `mov ..,0` em `0x0040ffcc`.

    Sem ela o `Comple.` nao gravaria nada: o destino da `GravaJogador` e o
    MESMO par (time, slot) da origem, a identidade bate e a rotina sai com
    `COD_MESMO_JOGADOR` sem tocar na imagem. }
  IgnoraJogadorRepetido := True;
  try
    jugador.ShowModal;
  finally
    IgnoraJogadorRepetido := False;
  end;
end;
