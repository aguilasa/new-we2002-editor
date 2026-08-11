{ MainForm.lista_equiposChange -- 0x0040cd6c, 1.536 bytes.
  Spec: wte/re/spec/MainForm.lista_equiposChange.md

  O handler central do editor: quase toda operacao comeca por escolher um time
  nesta lista. Tres blocos, na ordem do original -- estado de controle, as
  cinco barras, o resto da tela.

  NAO LE A IMAGEM, e isso e decisao medida, nao atalho. O original reabre o
  arquivo e calcula endereco a cada troca de time; as contas dele caem nos
  mesmos bytes que a camada de dados ja carregou -- `OFS_TEAM_BARS` para as
  barras (conferido byte a byte, e remedido a cada build pelo
  `wte/tools/check_barras.py`), a tabela de offsets em `0x004231a0` para os
  nomes (a mesma que a WTE-TASK-06 registrou), e o mesmo elenco para os nomes
  de jogador. Ver `wte/re/auxiliares.md`.

  O `95` NAO e o numero de times: e o indice do item `95 Master L. `, o
  time-modelo que a Master League usa ao criar clube. E por isso que ele
  desliga barra, bandeira, uniforme e nome. Os times de verdade sao 0..94.

  NAO ESTA AQUI, e o dono esta nomeado: a bandeira e o uniforme 2D
  (`0x00405270` e `0x004056c8`) sao da
  WTE-TASK-32 (wte/re/spec/MainForm.lista_equiposChange.md, secao Notas). O
  handler deixa os controles com a visibilidade certa; quem os desenha e a 32. }
var
  indice: Integer;
  nacional: Boolean;
  i: Integer;
  barra, radio: TComponent;
begin
  REMark('MainForm.lista_equiposChange');
  indice := lista_equipos.ItemIndex;
  if indice < 0 then
    Exit;
  nacional := indice < IDX_MODELO_ML;

  { --- 1. estado de controle ------------------------------------------- }
  base_team.Enabled := True;
  if lista_equipos_2.ItemIndex >= 0 then
  begin
    paderecha.Enabled := True;
    paderecha2.Enabled := True;
    paizquierda.Enabled := True;
    paizquierda2.Enabled := True;
    paderechaeizquierda.Enabled := True;
  end;
  edit_nombre1.Enabled := nacional;
  edit_nombre2.Enabled := nacional;
  edit_nombre3.Enabled := nacional;
  iguala_nombres.Enabled := nacional;
  { Os rotulos ficam habilitados SEMPRE -- nao seguem `nacional`. E assimetria
    do original, medida, nao descuido de leitura. }
  etiq_nombre1.Enabled := True;
  etiq_nombre2.Enabled := True;
  etiq_nombre3.Enabled := True;
  boton_nombres2iso.Enabled := nacional;
  boton_mcr.Enabled := True;
  boton_dialogo_tex.Enabled := True;
  bandera.Visible := nacional;
  home1.Visible := nacional;
  home2.Visible := nacional;
  punto.Visible := nacional;
  banderita1.Visible := nacional;
  colorear.Enabled := nacional;

  edit_nombre1.Text := NomeDoTime(indice, 0);
  edit_nombre2.Text := NomeDoTime(indice, 1);
  edit_nombre3.Text := NomeDoTime(indice, 2);

  { --- 2. as cinco barras ---------------------------------------------- }
  { A largura e `11*v + 9`, aritmetica literal do disassembly e nao proporcao
    sobre um maximo: `v = 0` da 9 px, que e a barra vazia desenhada no DFM. }
  for i := 0 to 4 do
  begin
    barra := FindComponent('barra' + IntToStr(i));
    radio := FindComponent('sel_barra' + IntToStr(i));
    if barra is TControl then
      if nacional then
        TControl(barra).Width := 11 * BarraDoTime(indice, i) + 9
      else
        TControl(barra).Width := 9;
    if radio is TControl then
      TControl(radio).Enabled := nacional;
  end;
  track_barra.Enabled := nacional;
  if nacional then
    track_barra.Position := BarraDoTime(indice, BarraMarcada);
  boton_barras2iso.Enabled := nacional;

  { --- 3. o resto da tela ---------------------------------------------- }
  lista_descarte.ItemIndex := -1;
  lista_descarte.Enabled := True;
  parriba.Enabled := True;

  { `ItemIndex :=` nao dispara `OnChange` na LCL -- medido pelo
    `wte/tools/check_lcl_combo.py`, como no Win32 do original e ao contrario do
    Qt do newWe2002. Sem isso esta linha reentraria neste handler. }
  lista_equipos_1.ItemIndex := indice;
  PreencheJogadores(lista_jugadores_1, indice);
  PreencheCamisas(indice);
  lista_jugadores_1.Enabled := True;
  lista_jugadores_1.ItemIndex := 0;
  MarcaCamisa(1);

  grabar_memory.Enabled := True;
  grabar_camiseta.Enabled := True;
  mostrar_jugador_1.Enabled := True;
  mostrar_estrategia_1.Enabled := True;

  { Acima de 62 -- as selecoes classicas e os clubes de ML -- o `home1` e
    reposicionado e o `punto` some. }
  if indice > 62 then
  begin
    home1.Left := 7;
    home1.Width := 100;
    punto.Visible := False;
  end
  else
  begin
    home1.Left := 16;
    home1.Width := 80;
  end;
end;
