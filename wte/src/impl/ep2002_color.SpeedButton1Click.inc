{ ficha_color.SpeedButton1Click -- 0x00406f34, 14 bytes.
  Spec: wte/re/spec/ficha_color.SpeedButton1Click.md

  O ponto de interrogacao do editor de cor: abre o `ficha_info`, que lista os
  atalhos de copiar e colar cor que o `colorMouseDown` implementa.

  O resultado do modal e descartado, como no original -- o `ficha_info` so tem
  o botao ` Ok`. }
begin
  REMark('ficha_color.SpeedButton1Click');
  ficha_info.ShowModal;
end;
