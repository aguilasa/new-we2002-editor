{ MainForm.paizquierda2Click -- 0x0040e85c, 316 bytes.
  Spec: wte/re/spec/MainForm.paizquierda2Click.md

  A seta "<<": o espelho do `paderecha2Click`. Move os 23 jogadores do time da
  direita para o da esquerda, com a mesma confirmacao no `ficha_movertodos` e
  o mesmo silencio sobre os codigos de retorno. }
begin
  REMark('MainForm.paizquierda2Click');
  MoveTodosOsJogadores(lista_equipos_2, lista_equipos_1, lista_jugadores_1,
                       BUF_DIREITA, BUF_ESQUERDA);
end;
