{ MainForm.pabajoClick -- 0x0040ecc0, 447 bytes.
  Spec: wte/re/spec/MainForm.pabajoClick.md

  A seta para baixo: devolve o jogador guardado na linha selecionada da lista
  de descarte para o slot selecionado no lado DIREITO.

  A PRE-CONDICAO E A UNICA DO LOTE QUE VIRA MENSAGEM PROPRIA: linha vazia
  abre o `ficha_error2` com "Selecione um jogador para mover!!!" e sai. Repare
  que e o `ficha_error2`, nao o `ficha_error` que a `MostraCodigo` usa -- sao
  dois formularios de erro distintos no original, e cada um tem o seu.

  E ELE REPOVOA O LADO ESQUERDO TAMBEM, mas so quando os dois combos de time
  mostram o MESMO time: sem isso a lista da esquerda continuaria exibindo o
  nome antigo do jogador que acabou de ser substituido. }
var
  linha, guarda1, guarda2, codigo: Integer;
begin
  REMark('MainForm.pabajoClick');
  linha := lista_descarte.ItemIndex;
  if (linha < 0) or (linha >= JOGADORES_POR_TIME) then
    Exit;
  if not DescarteOcupado[linha] then
  begin
    ficha_error2.etiq1.Caption := 'Selecione um jogador para mover!!!';
    ficha_error2.ShowModal;
    Exit;
  end;
  if (lista_equipos_2.ItemIndex < 0) or (lista_jugadores_2.ItemIndex < 0) then
    Exit;

  guarda1 := lista_jugadores_1.ItemIndex;
  guarda2 := lista_jugadores_2.ItemIndex;

  codigo := GravaJogador(linha + BUF_DESCARTE_BASE,
                         lista_equipos_2.ItemIndex, guarda2);
  if codigo >= 0 then
  begin
    PreencheJogadores(lista_jugadores_2, lista_equipos_2.ItemIndex);
    lista_jugadores_2.Update;
    lista_jugadores_2.ItemIndex := guarda2;
    if lista_equipos_1.ItemIndex = lista_equipos_2.ItemIndex then
    begin
      PreencheJogadores(lista_jugadores_1, lista_equipos_1.ItemIndex);
      lista_jugadores_1.Update;
      lista_jugadores_1.ItemIndex := guarda1;
    end;
  end;
  casilla_xmlibres.Caption := IntToStr(BlocosLivresDeMl);
  MostraCodigo(codigo);
end;
