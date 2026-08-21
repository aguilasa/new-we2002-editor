{ ficha_color.barraChange -- 0x00405e40, 568 bytes.
  Um corpo para as tres barras `barra_rojo`, `barra_verde` e `barra_azul`.
  Spec: wte/re/spec/ficha_color.barraChange.md

  E o handler que de fato MUDA a cor: monta a palavra BGR555 com os cinco bits
  de cada barra, pinta a amostra selecionada e grava direto na fonte.

  ELE NAO PASSA PELA `PintaUmaAmostra`, e a diferenca nao e de estilo: aquela
  poria as barras na posicao da cor, e as barras sao a ENTRADA aqui -- seria
  realimentacao. O original tambem nao a chama; ele acha o `TLabel` por nome e
  escreve a cor, que e o que este corpo repete.

  E ELE GRAVA NA FONTE UM SO PAR DE BYTES, e nao as 16 palavras. O
  `SalvaPaleta` escreveria todas, e o resultado seria o mesmo -- as outras 15
  nao mudaram --, mas escrever uma entrada e o que o original faz e e o que
  mantem o custo do arrasto de barra constante.

  A cor da amostra e montada com os canais NAO EXPANDIDOS deslocados de tres:
  `(v shl 3) and $FF`. Com `Max = 31` no `.dfm` o `and` nunca corta nada, e ele
  esta aqui porque esta no original. }
var
  alvo: TComponent;
  r5, g5, b5: Integer;
begin
  REMark('ficha_color.barraChange');
  if (CorEmEdicao.entrada < 0) or (CorEmEdicao.entrada >= COR_AMOSTRAS) then
    Exit;
  r5 := barra_rojo.Position;
  g5 := barra_verde.Position;
  b5 := barra_azul.Position;

  alvo := FindComponent('color' + IntToStr(CorEmEdicao.entrada + 1));
  if alvo is TControl then
  begin
    if alvo is TLabel then
      TLabel(alvo).Transparent := False;
    TControl(alvo).Color :=
      TColor(((r5 shl RENDER_EXPANSAO) and $FF)
             or (((g5 shl RENDER_EXPANSAO) and $FF) shl 8)
             or (((b5 shl RENDER_EXPANSAO) and $FF) shl 16));
  end;

  CorEmEdicao.cores[CorEmEdicao.entrada] := CodificaCor(r5, g5, b5);

  { Os dois `if` sao independentes, como no `AplicaAosDesenhos` -- so que aqui
    a gravacao e de uma entrada so, entao o corpo nao pode ser compartilhado. }
  if boton0.Checked then
  begin
    SalvaPaleta(TimeEmCor);
    RedesenhaBandeiraEmVigor;
  end;
  if boton1.Checked then
  begin
    SalvaPaleta(TimeEmCor);
    RedesenhaUniformeEmVigor(lista_col1.ItemIndex);
  end;
end;
