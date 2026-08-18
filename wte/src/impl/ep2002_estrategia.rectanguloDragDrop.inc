{ estrategia.rectanguloDragDrop -- 0x00409780, 36 bytes.
  Spec: wte/re/spec/estrategia.rectanguloDragDrop.md

  Soltar dentro do retangulo. Nao move nada: a posicao ja foi escrita a cada
  passagem do `rectanguloDragOver`. Este handler so devolve a bola ao estado
  normal e esconde o retangulo.

  Repare no que ele NAO faz que o `bolaEndDrag` faz: nao torna o rotulo visivel
  de novo. Quem fecha isso e o `bolaEndDrag`, que a VCL dispara depois -- os
  dois sao complementares, e portar um so deixaria o rotulo sumido. }
begin
  REMark('estrategia.rectanguloDragDrop');
  if BolaEmFoco <> nil then
    BolaEmFoco.Enabled := True;
  rectangulo.Visible := False;
end;
