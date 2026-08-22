{ estrategia.BitBtn1Click -- 0x0040a650, 8 bytes.
  Spec: wte/re/spec/estrategia.BitBtn1Click.md
  Dono: CORR-WTE-082.

  O `Original ` da tela de tatica: OITO bytes, uma chamada e um `ret`. Ele
  reenche a tela a partir do que a imagem guarda, jogando fora tudo o que foi
  arrastado desde que o formulario abriu.

  E o irmao exato do `jugador.BitBtn1Click`, e fechou pelo mesmo motivo: nao
  havia o que chamar. A `0x0040a0b4` so ganhou port na CORR-WTE-082, e ate la
  este handler era stub -- como aquele ainda e.

  NAO RELE A IMAGEM, e essa e a unica sutileza. O original chama so a
  `0x0040a0b4`, que trabalha sobre as globais que o
  `MainForm.mostrar_estrategiaClick` encheu ao abrir. Reler aqui daria o mesmo
  resultado hoje e deixaria de dar no dia em que algo gravasse com o formulario
  aberto -- e o ` Accept` faz exatamente isso. }
begin
  REMark('estrategia.BitBtn1Click');
  PreencheTelaDeTatica;
end;
