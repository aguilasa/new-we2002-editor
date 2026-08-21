{ ficha_about.imagen_urlClick -- 0x00402de8, 36 bytes.
  Spec: wte/re/spec/ficha_about.imagen_urlClick.md

  O gemeo do `MainForm.Image3Click`, no banner da janela `Sobre...`. Os dois
  handlers de URL do `.exe` sao exatamente estes dois, identicos ate no
  registrador de trabalho -- so o deslocamento do campo muda. Aqui a acao vem
  do `SpeedButton1` (`+0x2F8`), la do `SpeedButton3` (`+0x4A4`).

  A explicacao do `Trim` e da constante esta no gemeo. }
begin
  REMark('ficha_about.imagen_urlClick');
  OpenURL(Trim(LANZA_URL_URL));
end;
