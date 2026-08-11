{ ficha_movertodos.FormCreate -- 0x00402e84. Spec: wte/re/spec/ficha_movertodos.FormCreate.md

  Forma `cor` do `wte/re/arranque.md`: o corpo inteiro e uma chamada a
  `TControl::SetColor` sobre a propria instancia. O DFM diz `Color = clBtnFace`,
  e essa cor NUNCA aparece na tela -- o `OnCreate` a substitui antes de o
  formulario ser exibido.

  `TColor` e `$00BBGGRR`, nao `#RRGGBB`. Este valor e RGB(220, 220, 60). }
begin
  REMark('ficha_movertodos.FormCreate');
  Color := $003CDCDC;
end;
