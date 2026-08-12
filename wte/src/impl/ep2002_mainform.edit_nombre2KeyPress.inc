{ MainForm.edit_nombre2KeyPress -- 0x0040d3c4, 88 bytes.
  Spec: wte/re/spec/MainForm.edit_nombre2KeyPress.md

  Filtro de tecla do segundo campo de nome do time. Letra, digito, ponto,
  espaco e BackSpace passam; o resto vira #0.

  `Return` leva o foco ao campo seguinte -- e os tres campos formam uma
  corrente, `nombre1 -> nombre2 -> (nada)`. O terceiro nao encadeia.

  Primeiro o foco, depois o filtro. Ordem do original, e ela importa:
  invertida, o `Return` chegaria zerado ao teste e o foco nunca andaria. }
begin
  REMark('MainForm.edit_nombre2KeyPress');
  if Key = #13 then
    edit_nombre3.SetFocus;
  if not ((Key = ' ') or (Key = '.') or (Key = #8)
          or (Key in ['0'..'9']) or (Key in ['A'..'Z']) or (Key in ['a'..'z'])) then
    Key := #0;
end;
