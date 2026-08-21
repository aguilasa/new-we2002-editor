{ ficha_error.SpeedButton1Click -- 0x00420f08, 14 bytes.
  Spec: wte/re/spec/ficha_error.SpeedButton1Click.md

  O ponto de interrogacao da janela de erro: abre o `ficha_info2`, que explica
  por que os blocos livres de Master League acabam. Quem mostra o `ficha_error`
  e o `MostraCodigo` do `ep2002_mainform.aux.inc`.

  O texto do `ficha_info2` esta em ingles e o resto do app em portugues -- e a
  traducao PT-BR que nao chegou nesse formulario. O port copia os rotulos como
  estao. }
begin
  REMark('ficha_error.SpeedButton1Click');
  ficha_info2.ShowModal;
end;
