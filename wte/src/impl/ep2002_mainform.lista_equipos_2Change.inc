{ MainForm.lista_equipos_2Change -- 0x0040e1a8, 346 bytes.
  Spec: wte/re/spec/MainForm.lista_equipos_2Change.md

  O irmao do `lista_equiposChange` para a SEGUNDA lista de times -- o time
  reserva, de onde saem os jogadores que a tela move para o titular. 346 bytes
  contra 1.536: ele faz bem menos.

  Reusa os auxiliares do `.aux.inc`: e a mesma `PreencheJogadores` que o lado
  titular usa, com a outra lista. No original e literalmente a mesma rotina --
  `0x0040b2d8` recebe a lista de times e a de jogadores como argumentos, e e
  por isso que ela tem dois chamadores.

  A BANDEIRA DO RESERVA (`0x00405468`) e desenhada aqui desde a
  WTE-TASK-29. }
var
  indice: Integer;
begin
  REMark('MainForm.lista_equipos_2Change');
  indice := lista_equipos_2.ItemIndex;
  if indice < 0 then
    Exit;

  help_team.Enabled := True;
  PreencheJogadores(lista_jugadores_2, indice);
  lista_jugadores_2.Enabled := True;
  lista_jugadores_2.ItemIndex := 0;
  mostrar_jugador_2.Enabled := True;
  mostrar_estrategia_2.Enabled := True;
  pabajo.Enabled := True;

  { O teste e contra `lista_equipos_1`, e nao contra `lista_equipos`. Os dois
    andam juntos -- o `lista_equiposChange` espelha a selecao num no outro --,
    mas quem o corpo le e o `_1`, e a spec dizia `lista_equipos` ate o mapa de
    campos ser cruzado na oitava passagem da WTE-TASK-25. }
  if lista_equipos_1.ItemIndex >= 0 then
  begin
    paderecha.Enabled := True;
    paderecha2.Enabled := True;
    paizquierda.Enabled := True;
    paizquierda2.Enabled := True;
    paderechaeizquierda.Enabled := True;
  end;

  if indice < IDX_MODELO_ML then
  begin
    { Quando os dois lados sao o MESMO time, o original nao redesenha: copia a
      bandeira ja pronta do titular. E otimizacao, nao comportamento diferente,
      e o port pode fazer os dois caminhos iguais sem divergir na tela -- o que
      falta dos dois lados e o desenho, que e da WTE-TASK-29. }
    if indice = lista_equipos_1.ItemIndex then
      banderita2.Picture := bandera.Picture
    else
      DesenhaBandeira(banderita2, FormaDaBandeira(indice),
                      CoresDaBandeira(indice));
    banderita2.Visible := True;
  end
  else
    banderita2.Visible := False;
end;
