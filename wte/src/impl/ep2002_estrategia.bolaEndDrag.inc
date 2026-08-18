{ estrategia.bolaEndDrag -- 0x004097a4, 48 bytes.
  Spec: wte/re/spec/estrategia.bolaEndDrag.md

  Fim do arrasto, por qualquer caminho -- inclusive soltar FORA do retangulo,
  que e o caso que o `rectanguloDragDrop` nao ve. Restaura os tres estados. }
begin
  REMark('estrategia.bolaEndDrag');
  if BolaEmFoco <> nil then
    BolaEmFoco.Enabled := True;
  if EtiquetaEmFoco <> nil then
    EtiquetaEmFoco.Visible := True;
  rectangulo.Visible := False;
end;
