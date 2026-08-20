{ MainForm.boton_mcrClick -- 0x0040c2c8, 418 bytes.
  Spec: wte/re/spec/MainForm.boton_mcrClick.md

  Abre o `dialogo_mcr` (`TOpenDialog` do formulario) e carrega o memory card
  que ele apontar. 418 bytes de corpo, mais os 407 da `0x0040b9ec`, que e quem
  le -- e o mapa do que ela le esta em `wte/re/mcr.md`.

  ELE NAO GRAVA NADA. O que grava e o `boton_mcr2iso`, que este corpo HABILITA
  ao terminar: o botao nasce `Enabled = False` no DFM, e sem cartao carregado
  nao ha o que importar.

  A imagem vem por variavel de ambiente pelo mesmo motivo da textura e do
  destino do `.mcr`: o `TOpenDialog` do gtk2 nao se dirige por coordenada fixa
  no `:99`, entao o lado port do gate nunca chegaria ao `Execute`. Ver
  `TexturaEscolhida` e `CartaoDestino` no `we2002_estado`. }
begin
  REMark('MainForm.boton_mcrClick');
  if not dialogo_mcr.Execute then
    Exit;
  if not LeCartaoDeMemoria(dialogo_mcr.FileName, CartaoCarregado) then
  begin
    { O original nao confere nada: chama a `0x0040b9ec` sobre o que vier e
      habilita o botao. Aqui um arquivo que nao e cartao para aqui, porque o
      lixo iria PARA A IMAGEM no clique seguinte. Divergencia deliberada,
      WTE-TASK-35. }
    texto_mcr.Caption := 'nao e um memory card: '
                       + ExtractFileName(dialogo_mcr.FileName);
    Exit;
  end;
  CartaoCaminho := dialogo_mcr.FileName;
  texto_mcr.Caption := ExtractFileName(dialogo_mcr.FileName);
  boton_mcr2iso.Enabled := True;
end;
