{ ficha_info4.FormCreate -- 0x0040422c. Spec: wte/re/spec/ficha_info4.FormCreate.md

  Forma `cor` do `wte/re/arranque.md`: o corpo inteiro e uma chamada a
  `TControl::SetColor` sobre a propria instancia. O DFM diz `Color = clBtnFace`,
  e essa cor NUNCA aparece na tela -- o `OnCreate` a substitui antes de o
  formulario ser exibido.

  `TColor` e `$00BBGGRR`, nao `#RRGGBB`. Este valor e RGB(60, 220, 220). }
begin
  REMark('ficha_info4.FormCreate');
  Color := $00DCDC3C;
end;
