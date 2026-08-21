{ MainForm.SpeedButton1Click -- 0x00410fc0, 14 bytes.
  Spec: wte/re/spec/MainForm.SpeedButton1Click.md

  O `  Sobre...`. Mesma forma do irmao do `ficha_color`, com outro formulario e
  o resultado igualmente descartado.

  ELE E A SEGUNDA PORTA PARA A MESMA JANELA. A primeira e o arranque: a
  `MainForm.FormShow` do original chama `ficha_about.ShowModal()` em
  `0x004117d7`, e e por isso que o lado oraculo do `golden-14-uniforme` tem um
  passo so para dispensar a janela `Sobre...` e o lado port nao tem. Essa
  assimetria e divida da `FormShow`, nao deste handler. }
begin
  REMark('MainForm.SpeedButton1Click');
  ficha_about.ShowModal;
end;
