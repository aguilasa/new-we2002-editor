{ MainForm.paderechaClick -- 0x0040e5e8, 312 bytes.
  Spec: wte/re/spec/MainForm.paderechaClick.md

  A seta ">" entre os dois paineis: move UM jogador do lado esquerdo para o
  direito. O corpo inteiro esta na `MoveUmJogador` do `.aux.inc`, que os
  quatro botoes da familia compartilham -- no binario sao quatro copias
  literais que so trocam quais combos entram e qual buffer e qual.

  Origem = o lado esquerdo (`lista_equipos_1`/`lista_jugadores_1`), buffer 1;
  destino = o direito, buffer 2. }
begin
  REMark('MainForm.paderechaClick');
  MoveUmJogador(lista_equipos_1, lista_jugadores_1,
                lista_equipos_2, lista_jugadores_2,
                BUF_ESQUERDA, BUF_DIREITA);
end;
