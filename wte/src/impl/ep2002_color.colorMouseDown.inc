{ ficha_color.colorMouseDown -- 0x00406a0c, 1320 bytes.
  Um corpo para as 16 amostras `color1`..`color16`.
  Spec: wte/re/spec/ficha_color.colorMouseDown.md

  **E O COLA-CORES DO TITULO DA TASK**, e o readme do original o vende como
  "an improvement over WE2002 Painter features". Tres modos, escolhidos pelas
  teclas modificadoras e pelo botao:

      sem Ctrl,  esquerdo   seleciona a amostra (a unica coisa visivel)
      Ctrl,      direito    copia UMA cor        -> `CorCopiada`
      Ctrl,      esquerdo   cola UMA cor
      Ctrl+Shift direito    copia AS 16          -> `PaletaCopiada`
      Ctrl+Shift esquerdo   cola AS 16

  O botao do meio nao faz nada em modo nenhum: os testes do original sao
  `= mbRight` e `= mbLeft`, e nao um `if/else`.

  ### O `Ctrl` sem `Shift` LE O NOME, e nao a `entrada`

  A cor copiada ou colada e a da amostra CLICADA, que nao precisa ser a
  selecionada. O original recorta `Copy(Name, 6, 2)` do `Sender`; aqui e o
  mesmo recorte. Usar `CorEmEdicao.entrada` daria a cor errada sempre que o
  usuario copiasse sem selecionar antes.

  ### O `Ctrl+Shift` para copiar tambem pinta as 16 `colcop`

  A fileira `colcop1`..`colcop16` e o mostruario do que esta na area de
  transferencia, e `colcop0` e o mostruario da cor unica. Elas nao sao
  editaveis: so recebem tinta.

  ### O `if` repetido no fim e do original

  Depois dos modos com Ctrl o original testa `boton0.Checked` DUAS vezes -- e
  no segundo teste redesenha o UNIFORME. E defeito: com a bandeira marcada ele
  redesenha os dois, e com o uniforme marcado nao redesenha nenhum. A cauda
  esta reproduzida como esta, porque o efeito e visivel e o gate compara tela;
  "corrigir" aqui produziria divergencia de pixel contra o oraculo.

  ### A selecao move controle, e as coordenadas sao literais

  A amostra que sai encolhe para 33x25 na linha de baixo, a que entra cresce
  para 47x39, e a moldura `recuadro2` a acompanha. Os `32` sao a largura de uma
  amostra; o resto e coordenada de tempo de projeto. }
var
  clicada, alvo: TComponent;
  i: Integer;
begin
  REMark('ficha_color.colorMouseDown');
  if not (Sender is TControl) then
    Exit;
  clicada := TComponent(Sender);

  if ssCtrl in Shift then
  begin
    if ssShift in Shift then
    begin
      if Button = mbRight then
      begin
        for i := 1 to COR_AMOSTRAS do
        begin
          PaletaCopiada[i - 1] := CorEmEdicao.cores[i - 1];
          alvo := FindComponent('colcop' + IntToStr(i));
          if alvo is TLabel then
          begin
            TLabel(alvo).Transparent := False;
            TLabel(alvo).Color :=
              TControl(FindComponent('color' + IntToStr(i))).Color;
          end;
        end;
      end;
      if Button = mbLeft then
      begin
        for i := 1 to COR_AMOSTRAS do
          PintaUmaAmostra(Self, i, PaletaCopiada[i - 1]);
        SalvaPaleta(TimeEmCor);
        if boton0.Checked then
          RedesenhaBandeiraEmVigor;
        if boton1.Checked then
          RedesenhaUniformeEmVigor(lista_col1.ItemIndex);
      end;
    end
    else
    begin
      i := StrToIntDef(Copy(clicada.Name, 6, 2), -1);
      if (i >= 1) and (i <= COR_AMOSTRAS) then
      begin
        if Button = mbRight then
        begin
          CorCopiada := CorEmEdicao.cores[i - 1];
          colcop0.Transparent := False;
          colcop0.Color := TControl(clicada).Color;
        end;
        if Button = mbLeft then
        begin
          PintaUmaAmostra(Self, i, CorCopiada);
          SalvaPaleta(TimeEmCor);
          if boton0.Checked then
            RedesenhaBandeiraEmVigor;
          if boton1.Checked then
            RedesenhaUniformeEmVigor(lista_col1.ItemIndex);
        end;
      end;
    end;

    { A cauda com o `boton0` testado duas vezes -- ver o cabecalho. }
    if boton0.Checked then
    begin
      SalvaPaleta(TimeEmCor);
      RedesenhaBandeiraEmVigor;
    end;
    if boton0.Checked then
    begin
      SalvaPaleta(TimeEmCor);
      RedesenhaUniformeEmVigor(lista_col1.ItemIndex);
    end;
    Exit;
  end;

  { Sem Ctrl: so o botao esquerdo faz alguma coisa, e ela e selecionar. }
  if Button <> mbLeft then
    Exit;
  alvo := FindComponent('color' + IntToStr(CorEmEdicao.entrada + 1));
  if alvo is TControl then
  begin
    TControl(alvo).Left := CorEmEdicao.entrada * 32 + $10;
    TControl(alvo).Top := $56;
    TControl(alvo).Width := $21;
    TControl(alvo).Height := $19;
    TControl(alvo).SendToBack;
  end;

  i := StrToIntDef(Copy(clicada.Name, 6, 2), -1);
  if (i < 1) or (i > COR_AMOSTRAS) then
    Exit;
  CorEmEdicao.entrada := i - 1;

  TControl(clicada).BringToFront;
  TControl(clicada).Left := CorEmEdicao.entrada * 32 + 9;
  recuadro2.Left := CorEmEdicao.entrada * 32 + 8;
  TControl(clicada).Top := $4F;
  TControl(clicada).Width := $2F;
  TControl(clicada).Height := $27;

  MostraCorSelecionada(Self);
end;
