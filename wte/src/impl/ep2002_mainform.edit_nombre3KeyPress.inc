{ MainForm.edit_nombre3KeyPress -- 0x0040d41c, 32 bytes.
  Spec: wte/re/spec/MainForm.edit_nombre3KeyPress.md

  O TERCEIRO CAMPO NAO E COMO OS OUTROS DOIS, e a diferenca e do original:

    - so **alfanumerico** e BackSpace passam. Sem espaco, sem ponto -- os
      dois irmaos aceitam ambos;
    - **nao encadeia foco**: `Return` nao faz nada aqui.

  Faz sentido no dado: este campo e a abreviatura de tres letras
  (`abbreviations[0]`, `MaxLength = 3` no proprio DFM), nao um nome.

  E o teste e `isalnum` da RTL da Borland (`0x00419018`, mascara `0x104` do
  `_ctype` -- alfa mais digito), enquanto os irmaos comparam faixa a mao. Sem
  consequencia em ASCII; registrado porque a assimetria e do original. }
begin
  REMark('MainForm.edit_nombre3KeyPress');
  if (Key <> #8) and not (Key in ['0'..'9', 'A'..'Z', 'a'..'z']) then
    Key := #0;
end;
