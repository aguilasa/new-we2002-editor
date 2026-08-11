{ ficha_dorsal.FormCreate -- 0x00402bc0. Spec: wte/re/spec/ficha_dorsal.FormCreate.md

  Forma `cor` do `wte/re/arranque.md`: o corpo inteiro e uma chamada a
  `TControl::SetColor` sobre a propria instancia. O DFM diz `Color = clBtnFace`,
  e essa cor NUNCA aparece na tela -- o `OnCreate` a substitui antes de o
  formulario ser exibido.

  `TColor` e `$00BBGGRR`, nao `#RRGGBB`. Este valor e RGB(65, 143, 230). }
begin
  REMark('ficha_dorsal.FormCreate');
  Color := $00E68F41;
end;
