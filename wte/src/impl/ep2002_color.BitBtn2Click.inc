{ ficha_color.BitBtn2Click -- 0x004069c8, 30 bytes.
  Spec: wte/re/spec/ficha_color.BitBtn2Click.md

  O `Cancela`: desfaz e deixa a janela fechar.

  QUEM FECHA A JANELA NAO E O HANDLER. O `BitBtn2` traz `Cancel = True` e
  `ModalResult = 7` no `.dfm`, e o widgetset grava o 7 antes de chamar o
  `OnClick`. Nao ha `Hide` nem escrita em `ModalResult` aqui -- ao contrario do
  `jugador.BitBtn2Click`, que sobrescreve o resultado.

  SAO DUAS DIFERENCAS CONTRA O `BitBtn1`, e as duas sao "a janela vai sumir":
  nao repinta as 16 amostras, porque ninguem vai ve-las; e redesenha o uniforme
  com o jogo 0 em vez do jogo do `lista_col1`. O `xor edx,edx` antes da chamada
  e literal no original, e faz sentido -- o `MainForm` mostra o primeiro
  uniforme, e e para ele que a tela volta.

  Este e o unico dos tres `Cancela` do binario que cancela de verdade: os
  outros dois so fecham. }
begin
  REMark('ficha_color.BitBtn2Click');
  RestauraOriginal(TimeEmCor);
  RedesenhaBandeiraEmVigor;
  RedesenhaUniformeEmVigor(0);
end;
