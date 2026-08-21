{ MainForm.Image3Click -- 0x00410fd0, 36 bytes.
  Spec: wte/re/spec/MainForm.Image3Click.md

  O banner da W11 Online na tela principal. O handler nao sabe a URL: ele
  ENCAMINHA para a acao do botao vizinho -- le `SpeedButton3.Action`
  (`TControl::GetAction`, VMT +0x3C), acha o metodo dinamico -17
  (`TContainedAction::Execute`) e o chama.

  Um `TImage` nao tem `Action` na VCL de 2002, e e por isso que o autor pendurou
  a acao no `TSpeedButton` ao lado e fez a imagem disparar a mesma acao por
  dentro. O efeito visivel e uma faixa clicavel de 233 px onde o botao tem 25.

  A LCL nao tem `TBrowseURL`: o `dfm2lfm.py` converteu a acao num `TLabel`
  inerte e guardou o valor na constante `LANZA_URL_URL` desta unidade, com um
  TODO pedindo `OpenURL()` no handler que dispara. Este e o handler que
  dispara.

  O `Trim` nao e enfeite: a URL do `.dfm` tem NOVE espacos a direita, que o
  `ShellExecute` do Windows ignora e o `xdg-open` leva para dentro do
  argumento. Aparar preserva o efeito -- abrir `http://www.w11.com.br` -- em vez
  da forma do argumento. }
begin
  REMark('MainForm.Image3Click');
  OpenURL(Trim(LANZA_URL_URL));
end;
