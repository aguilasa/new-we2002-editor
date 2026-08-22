{ estrategia.BitBtn3Click -- 0x0040a660, 1.931 bytes.
  Spec: wte/re/spec/estrategia.BitBtn3Click.md
  Dono: CORR-WTE-081, terceira e ultima das gravacoes orfas.

  O ` Accept` da tela de tatica -- no componente chamado `BitBtn6` --, e a
  OITAVA rota de escrita na imagem. Ele le a tela e devolve 45 bytes por time:
  30 de formacao, 6 de cobrador, 5 de tatica e 2 + 2 de cor de radar.

  ELE SO PODE EXISTIR PORQUE A TELA E ENCHIDA. Ate a CORR-WTE-082 a
  `0x0040A0B4` nao estava portada, e as posicoes que este corpo converte em
  celula seriam as coordenadas de tempo de projeto do `.lfm`. A gravacao sairia
  PLAUSIVEL -- formato e offset certos, conteudo do formulario --, que e o pior
  jeito de errar.

  TRES BLOCOS, na ordem do original:

  1. a validacao das cores de radar, que so existe para selecao;
  2. as duas cores gravadas, uma chamada de dois bytes cada;
  3. a leitura da tela, convertida de pixel para celula, e as tres gravacoes
     que sobram.

  AS CONVERSOES SAO O INVERSO EXATO DO QUE A TELA RECEBEU, e vale ler os dois
  lados juntos:

      DestinoX := x * 8 - 2          ->   x := (Left - campo.Left + 2) div 8
      DestinoY := ((y - 3) div 2) * 5 - 7
                                     ->   y := ((Top - campo.Top + 7) div 5) * 2 + 3
      Top := malla2.Top + 16 * v + 3 ->   v := (Top - malla2.Top - 3) div 16

  As divisoes truncam para ZERO nos dois lados -- o `sar` do original vem com
  o `+7` ou o `+15` de correcao de sinal, que e o que o `div` do Pascal faz.

  O QUINTO BYTE DA TATICA E O PRIMEIRO DO COBRADOR, e isso nao e escolha
  nossa. O buffer de tatica do original tem QUATRO bytes na pilha
  (`[ebp-0x58]`) e o de cobrador comeca logo depois (`[ebp-0x54]`); a gravacao
  pede CINCO. O quinto byte lido, portanto, e `cobrador[0]`. Reproduzido como
  esta: e deterministico, e a carga nunca le esse byte de volta -- ela le
  quatro.

  O PAPEL NAO SAI DA TELA. Os dez bytes de papel sao os da tatica VIVA,
  devolvidos como vieram; a tela nao tem onde edita-los. E por isso que o
  original grava `[0x00434224][1..10]` e nao um buffer local. }
var
  papel, x, y: array[0 .. TATICA_JOGADORES_EM_CAMPO - 1] of Byte;
  cobrador: array[0 .. TATICA_COBRADORES - 1] of Byte;
  tatica: array[0 .. TATICA_TATICA_PASSO - 1] of Byte;
  i, casa, visitante, valor: Integer;
  c: TComponent;

  { `(Top - referencia.Top - 3) div 16`, o inverso do `PoeNaMalha`. }
  function CelulaDaMalha(alvo: TControl): Integer;
  begin
    Result := (alvo.Top - malla2.Top - MALHA_FOLGA) div MALHA_PASSO_Y;
  end;

begin
  REMark('estrategia.BitBtn3Click');
  if not TaticaViva.valida then
    Exit;

  casa := ComboBox1.ItemIndex;
  visitante := ComboBox2.ItemIndex;

  { 1. A VALIDACAO, e ela so roda para selecao -- o `cmp DWORD ds:0x4335cc,0x5f`
       do prologo pula os blocos 1 e 2 inteiros para clube de Master League. }
  if TimeEmEdicao < TATICA_TIMES_COM_TABELA then
  begin
    { Os dez pares que ele AVISA. Casar com um deles nao impede: pergunta, e
      so desiste se a resposta nao for `Sim`. }
    for i := 0 to PARES_DE_RADAR_TOTAL - 1 do
      if (casa = PARES_DE_RADAR[i][0]) and (visitante = PARES_DE_RADAR[i][1]) then
        if ficha_warning_2.ShowModal <> mrYes then
          Exit;

    { E a recusa dura: duas cores iguais. O foco volta para o primeiro combo. }
    if casa = visitante then
    begin
      ficha_error2.etiq1.Caption :=
        'You should use different Home && Away radar colours...';
      ficha_error2.ShowModal;
      ComboBox1.SetFocus;
      Exit;
    end;

    { 2. AS DUAS CORES. }
    GravaCorDeRadar(TimeEmEdicao, 0, casa);
    GravaCorDeRadar(TimeEmEdicao, 1, visitante);
  end;

  { 3. A TELA, convertida. As onze bolas sao `bola1`..`bola10` -- o goleiro
       (`bola0`) nao entra, aqui como no laco da animacao. }
  for i := 0 to TATICA_JOGADORES_EM_CAMPO - 1 do
  begin
    papel[i] := TaticaViva.formacao.papel[i + 1];
    x[i] := 0;
    y[i] := 0;
    c := FindComponent('bola' + IntToStr(i + 1));
    if not (c is TControl) then
      Continue;
    x[i] := Byte((TControl(c).Left - campo.Left + TATICA_X_FOLGA)
                 div TATICA_X_PASSO);
    y[i] := Byte(((TControl(c).Top - campo.Top + TATICA_Y_FOLGA)
                  div TATICA_Y_PASSO) * 2 + 3);
  end;

  for i := 0 to TATICA_COBRADORES - 1 do
  begin
    cobrador[i] := 0;
    c := FindComponent('tirador' + IntToStr(i + 1));
    if c is TControl then
      cobrador[i] := Byte(CelulaDaMalha(TControl(c)));
  end;

  { O byte 0 da tatica sai do item da lista, e e o inverso exato da escolha do
    registro de zona que a carga faz: `STOCK` vira 16, `DEFAULT` devolve o
    codigo que a imagem trouxe, e o resto perde os dois itens de cabeca. }
  FillChar(tatica, SizeOf(tatica), 0);
  if lista_formaciones.ItemIndex = TATICA_ITEM_DEFAULT then
    tatica[0] := TaticaViva.tatica[0]
  else if lista_formaciones.ItemIndex = 0 then
    tatica[0] := TATICA_CODIGO_STOCK
  else
    tatica[0] := Byte(lista_formaciones.ItemIndex - TATICA_ZONA_DESLOCAMENTO);

  { Os quatro marcadores, cada um em quatro bits, a partir do bit 8. }
  for i := 1 to TATICA_MARCADORES do
  begin
    c := FindComponent('simbolo' + IntToStr(i));
    if not (c is TControl) then
      Continue;
    valor := CelulaDaMalha(TControl(c)) and $0F;
    tatica[(TATICA_MARCADOR_BITS * i + TATICA_MARCADOR_BITS) div 8] :=
      tatica[(TATICA_MARCADOR_BITS * i + TATICA_MARCADOR_BITS) div 8]
      or Byte(valor shl ((TATICA_MARCADOR_BITS * i + TATICA_MARCADOR_BITS) mod 8));
  end;

  { O transbordo: o quinto byte gravado e o primeiro do cobrador. }
  tatica[TATICA_TATICA_PASSO - 1] := cobrador[0];

  GravaTaticaNaImagem(TimeEmEdicao, papel[0], x[0], y[0], cobrador[0],
                      tatica[0]);

  ModalResult := mrOk;
end;
