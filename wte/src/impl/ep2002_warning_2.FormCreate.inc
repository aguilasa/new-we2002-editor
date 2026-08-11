{ ficha_warning_2.FormCreate -- 0x00408d88. Spec: wte/re/spec/ficha_warning_2.FormCreate.md

  Forma `cor` do `wte/re/arranque.md`: o corpo inteiro e uma chamada a
  `TControl::SetColor` sobre a propria instancia. O DFM diz `Color = clBtnFace`,
  e essa cor NUNCA aparece na tela -- o `OnCreate` a substitui antes de o
  formulario ser exibido.

  `TColor` e `$00BBGGRR`, nao `#RRGGBB`. Este valor e RGB(220, 60, 60). }
begin
  REMark('ficha_warning_2.FormCreate');
  Color := $003C3CDC;
end;
