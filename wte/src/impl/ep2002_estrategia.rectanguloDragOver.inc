{ estrategia.rectanguloDragOver -- 0x00409644, 316 bytes.
  Spec: wte/re/spec/estrategia.rectanguloDragOver.md

  O movimento durante o arrasto. Aceita sempre, ajusta a posicao a grade e
  arrasta o rotulo junto.

  A COORDENADA CHEGA RELATIVA AO `rectangulo`, nao ao `campo`: o alvo do
  arrasto e o retangulo, e por isso a conversao comeca somando a diferenca
  entre as duas origens. Tratar `X`/`Y` como se ja fossem do campo desloca a
  bola pela posicao da zona -- erro que cresce com a zona e some na zona 0. }
begin
  REMark('estrategia.rectanguloDragOver');
  Accept := True;
  if (BolaEmFoco = nil) then
    Exit;
  GradeX := AjustaX(rectangulo.Left - campo.Left + X);
  GradeY := AjustaY(rectangulo.Top - campo.Top + Y);
  BolaEmFoco.Left := campo.Left + GradeX - RAIO_DA_BOLA;
  BolaEmFoco.Top := campo.Top + GradeY - RAIO_DA_BOLA;
  if EtiquetaEmFoco <> nil then
  begin
    EtiquetaEmFoco.Left := BolaEmFoco.Left + ETIQUETA_DX;
    EtiquetaEmFoco.Top := BolaEmFoco.Top + ETIQUETA_DY;
  end;
end;
