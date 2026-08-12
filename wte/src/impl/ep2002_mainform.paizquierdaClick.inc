{ MainForm.paizquierdaClick -- 0x0040e4b0, 312 bytes.
  Spec: wte/re/spec/MainForm.paizquierdaClick.md

  A seta "<": move UM jogador do lado direito para o esquerdo. E o espelho do
  `paderechaClick`, e no binario e uma copia literal dele com os quatro campos
  de combo trocados e o `1`/`2` invertido.

  Origem = o lado direito (`lista_equipos_2`/`lista_jugadores_2`), buffer 2;
  destino = o esquerdo, buffer 1. }
begin
  REMark('MainForm.paizquierdaClick');
  MoveUmJogador(lista_equipos_2, lista_jugadores_2,
                lista_equipos_1, lista_jugadores_1,
                BUF_DIREITA, BUF_ESQUERDA);
end;
