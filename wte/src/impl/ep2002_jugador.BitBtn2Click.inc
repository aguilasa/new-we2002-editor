{ jugador.BitBtn2Click -- 0x00407a68, 21 bytes.
  Spec: wte/re/spec/jugador.BitBtn2Click.md

  O `Cancela` da ficha do jogador, byte a byte igual ao ` Ok` do
  `ficha_dorsal` -- so muda a global carregada.

  O BOTAO DIZ `Cancela` E DEVOLVE `mrOk`. O `.dfm` traz `ModalResult = 7`
  (mrCancel) no `BitBtn2`, a VCL grava esse 7 antes do `OnClick`, e o handler o
  sobrescreve com 1. Isso nao muda nada hoje: o `mostrar_jugadorClick` DESCARTA
  o retorno do `ShowModal`. O port reproduz a sobrescrita em vez de "corrigir"
  para `mrCancel` -- corrigir inventaria uma diferenca que ninguem observa e
  que morderia no dia em que alguem passasse a ler o resultado.

  Quem desfaz a edicao da ficha nao e este botao, e o `Original ` -- ver
  `wte/re/spec/jugador.BitBtn1Click.md`. }
begin
  REMark('jugador.BitBtn2Click');
  ModalResult := mrOk;
  Hide;
end;
