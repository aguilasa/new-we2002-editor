{ MainForm.base_teamClick -- 0x00410ff4, 484 bytes.
  Spec: wte/re/spec/MainForm.base_teamClick.md

  ESCOPO: a MOLDURA. Os rotulos `Time Tit.` e `Time Res.` -- os dois com o
  `Hint` `Calcular precos` -- abrem o `ficha_creditos_equipo` e, se a resposta
  nao for cancelar, calculam o preco dos 23 jogadores do time e GRAVAM um byte
  em cada. O calculo e a gravacao sao da WTE-TASK-32, que e a dona de preco; o
  que este corpo faz e abrir e fechar.

  ELE GRAVA NA IMAGEM, e a task de preco precisa saber disso. A WTE-TASK-32 foi
  descrita como "isolada, nao depende de gravacao" -- verdade para o
  `jugador.etiqprecioClick`, que so mostra o numero na tela, e FALSO para este,
  que percorre 23 jogadores e escreve um byte em cada. A regua da 32 tem de ser
  dupla: tela para a formula, byte para este.

  QUEM SEPARA TITULAR DE RESERVA E O PONTEIRO DO `Sender`, e nao o nome --
  diferente do `mostrar_jugadorClick`, que compara nome. Por isso o
  `LadoTitular` do `.aux.inc` nao serve aqui.

  A ESCOLHA DO COMBO NAO ESTA AQUI de proposito. O original a faz no mesmo
  `if` que posiciona a janela, por economia de registrador; ela so alimenta o
  laco, e o laco e da 32. Deixa-la para la e o que impede um local atribuido e
  nunca lido.

  Os dois deslocamentos sao literais do `.text` -- `-65` do lado do titular,
  `Width - 200` do lado do reserva. Sao coordenadas de tempo de projeto e nao
  se derivam de nada. }
begin
  REMark('MainForm.base_teamClick');
  if Sender = TObject(base_team) then
    ficha_creditos_equipo.Left := Left - 65
  else
    ficha_creditos_equipo.Left := Left + Width - 200;

  if ficha_creditos_equipo.ShowModal = mrCancel then
    Exit;

  { Daqui para baixo e a WTE-TASK-32: escolher o combo pelo `Sender`, percorrer
    os 23 slots, calcular o preco de cada um a partir dos doze atributos e
    gravar um byte no offset da terceira coluna -- e so entao mostrar
    `Precos dos jogadores calculados!!!!!!!!!!!` no `ficha_info3`. }
end;
