{ MainForm.track_barraChange -- 0x0040ca10, 166 bytes.
  Spec: wte/re/spec/MainForm.track_barraChange.md

  O unico handler de edicao das barras. Duas saidas, nesta ordem:

    barra<marcada>.Width   := 11 * Position + 9    (a mesma aritmetica da carga)
    BarrasEmEdicao[marcada] := Position            (o `0x00434592` do original)

  A barra e achada por NOME (`'barra' + IntToStr(marcada)`, cadeia `'barra'`
  em 0x00424d69), nao por campo -- o original monta a cadeia com `IntToStr` e
  chama `FindComponent`. Reproduzido como esta.

  NAO grava na imagem. Quem leva `BarrasEmEdicao` para o disco e o
  `boton_barras2isoClick` (`0x0040cab8`), que e da WTE-TASK-27; ate ela
  existir, este handler nao tem como ser julgado por byte -- so por pixel. }
var
  barra: TComponent;
  valor: Integer;
begin
  REMark('MainForm.track_barraChange');
  if (BarraMarcada < Low(BarrasEmEdicao))
     or (BarraMarcada > High(BarrasEmEdicao)) then
    Exit;
  valor := track_barra.Position;
  barra := FindComponent('barra' + IntToStr(BarraMarcada));
  if barra is TControl then
    TControl(barra).Width := 11 * valor + 9;
  BarrasEmEdicao[BarraMarcada] := Byte(valor);
end;
