{ ficha_dorsal.BitBtn1Click -- 0x00402b40, 21 bytes.
  Spec: wte/re/spec/ficha_dorsal.BitBtn1Click.md

  O ` Ok` da janelinha de numero de camisa. Duas linhas, e as duas sao do
  original: ele grava 1 no campo de resultado modal (`+0x24C`, o
  `FModalResult` que o `TCustomForm::ShowModal` do `vcl60.bpl` consulta) e
  chama `Hide` na propria janela.

  AS DUAS SAO REDUNDANTES E ESTAO AQUI. O `.dfm` ja da `ModalResult = 1` ao
  botao, e a VCL grava esse valor no formulario ANTES do `OnClick` -- o handler
  regrava o mesmo 1 e ainda esconde a janela a mao. Reproduzir e mais barato do
  que provar que a ordem nao importa nos dois widgetsets. }
begin
  REMark('ficha_dorsal.BitBtn1Click');
  ModalResult := mrOk;
  Hide;
end;
