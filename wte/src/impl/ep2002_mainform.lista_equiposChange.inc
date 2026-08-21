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

  A BANDEIRA E O UNIFORME sao desenhados aqui desde a WTE-TASK-29 -- o
  `0x00405270` e o `0x004056c8`, na secao 4. Ate ela este comentario dizia que
  o desenho era de outra task; hoje ele so nao acontece quando o time nao tem
  bandeira, que e o caso do modelo de ML. }
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
  { Os dois de emitir arquivo nascem `Enabled = False` no DFM e e AQUI que o
    original os liga -- `0x0040d31a` e `0x0040d327`. Sem time escolhido nao
    ha o que emitir. }
  grabar_memory.Enabled := True;
  grabar_camiseta.Enabled := True;
  bandera.Visible := nacional;
  home1.Visible := nacional;
  home2.Visible := nacional;
  punto.Visible := nacional;
  banderita1.Visible := nacional;
  colorear.Enabled := nacional;

  { --- 4. a bandeira e o uniforme ---------------------------------------- }
  { A ORDEM E A DO ORIGINAL, e as tres partes sao tres chamadas separadas:

      0x0040d21d   copia a forma lida da imagem e chama 0x00405270  (bandeira)
      0x0040d2ab   `xor edx,edx` e chama 0x004056c8                 (uniforme)
      0x0040d2c2   TPicture::Assign de `bandera` para `banderita1`

    O `xor edx,edx` nao e detalhe: ao TROCAR DE TIME o original desenha sempre
    o Primeiro uniforme, e nao o que estivesse escolhido. Quem escolhe o
    Segundo e o combo do `ficha_color`, que redesenha por conta propria.

    `banderita1` nao e desenhada -- ela COPIA a bandeira ja pronta. Redesenhar
    daria o mesmo pixel e leria o arquivo de novo. }
  if nacional then
  begin
    DesenhaBandeira(bandera, FormaDaBandeira(indice), CoresDaBandeira(indice));
    DesenhaUniforme(home1, home2, indice, 0, CoresDoUniforme(indice, 0));
    banderita1.Picture.Assign(bandera.Picture);
  end;

  { Os tres campos NAO sao names[0..2], e as duas correcoes vieram de comparar
    tela com tela, nao de leitura:

      Nome1  names[1]           o slot com bytes fora de `A-Za-z0-9. `, que o
                                filtro do original mostra como `?????`
      Nome2  names[0]           o nome legivel
      Nome3  abbreviations[0]   a sigla de tres letras

    A do Nome3 so apareceu no clube de Master League: para Gales `names[2]`
    truncado e a abreviatura dao os dois `WAL`, e para o Manchester `names[2]`
    e `ARAGON` (cortado em `ARA` pelo campo) contra `AGN` na tela do original.
    Time de uma familia so nao teria pego. }
  edit_nombre1.Text := NomeDoTime(indice, 1);
  edit_nombre2.Text := NomeDoTime(indice, 0);
  edit_nombre3.Text := AbreviaturaDoTime(indice);

  { Os dois limites sao postos AQUI, e nao no `FormShow` -- `0x0040cc43` e
    `0x0040cc5b`, logo depois do laco que mede os lotes, dentro do
    `0x0040cbc8` que este handler chama. O port os punha uma vez so, na carga
    da imagem, com numero fixo; o do `edit_nombre2` estava errado por isso.

    Os DOIS sao por time e estao medidos nas duas pontas -- derivados dos
    lotes de `0x004231a0` e conferidos na tela do oraculo. O do `edit_nombre1`
    leva um `- 1` que nao e chute: e um `dec` que o original aplica so ao lote
    kanji (`0x00403d95`), e esta no `LimiteDoNome1`.

    O lote de onde sai cada limite NAO e o lote de onde sai o texto do campo:
    `edit_nombre1` mostra `names[1]` e recebe o limite do lote kanji, e
    `edit_nombre2` mostra `names[0]` e recebe o do lote `OFS_TEAM_NAME_3`. As
    duas pontas estao medidas -- o texto por comparacao de tela na WTE-TASK-25,
    o limite pelo disassembly aqui -- e a assimetria e do original. Quem grava
    e o `boton_nombres2isoClick`, da WTE-TASK-27, e e la que ela importa. }
  edit_nombre1.MaxLength := LimiteDoNome1(indice);
  edit_nombre2.MaxLength := LimiteDoNome2(indice);

  { --- 2. as cinco barras ---------------------------------------------- }
  { A largura e `11*v + 9`, aritmetica literal do disassembly e nao proporcao
    sobre um maximo: `v = 0` da 9 px, que e a barra vazia desenhada no DFM. }
  for i := 0 to 4 do
  begin
    barra := FindComponent('barra' + IntToStr(i));
    radio := FindComponent('sel_barra' + IntToStr(i));
    { Os cinco bytes vao para `BarrasEmEdicao` ANTES de virarem largura, e e
      dali que a largura sai. O original faz o mesmo -- le da imagem para
      `0x00434592` e desenha a partir do buffer --, e a diferenca so aparece
      depois: quem edita e grava e o buffer, nao `Jogo.teams[].bar_*`.
      Sem `nacional` o original nem chega no laco de leitura. }
    if nacional then
      BarrasEmEdicao[i] := Byte(BarraDoTime(indice, i));
    if barra is TControl then
      if nacional then
        TControl(barra).Width := 11 * BarrasEmEdicao[i] + 9
      else
        TControl(barra).Width := 9;
    if radio is TControl then
      TControl(radio).Enabled := nacional;
  end;
  track_barra.Enabled := nacional;
  if nacional then
    track_barra.Position := BarrasEmEdicao[BarraMarcada];
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
