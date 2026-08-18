{ wte_zonas -- os retangulos em que cada bola do campinho pode ser
  solta.

  GERADO por wte/tools/dump_zonas.py a partir de
  we-team-editor/we-team-editor.exe. NAO EDITAR A MAO: a correcao vai
  no gerador, e depois se regenera.

  E a tabela que o `estrategia.FormCreate` monta em 0x00433e5c e que
  o `bolaMouseDown` le para dimensionar o `rectangulo`. As coordenadas
  sao relativas ao `campo`, e a largura/altura do retangulo desenhado e
  `x2 - x1 + 1` por `y2 - y1 + 1` -- o `+ 1` e do original.

  O indice NAO e o numero da bola: e a zona que a formacao escolhida
  atribuiu aquela bola. O vetor bola->zona e outro, e quem o preenche e
  o `estrategia.lista_formacionesClick`. }
unit wte_zonas;

{$mode objfpc}{$H+}

interface

type
  TZona = record
    x1, y1, x2, y2: Integer;
  end;

const
  ZONAS_TOTAL = 11;

  ZONAS: array[0..ZONAS_TOTAL - 1] of TZona = (
    (x1: 10; y1: 63; x2: 129; y2: 182),
    (x1: 10; y1: 63; x2: 129; y2: 182),
    (x1: 10; y1: 3; x2: 129; y2: 82),
    (x1: 10; y1: 163; x2: 129; y2: 242),
    (x1: 122; y1: 63; x2: 233; y2: 182),
    (x1: 122; y1: 3; x2: 281; y2: 82),
    (x1: 122; y1: 163; x2: 281; y2: 242),
    (x1: 170; y1: 63; x2: 281; y2: 182),
    (x1: 274; y1: 63; x2: 385; y2: 182),
    (x1: 274; y1: 3; x2: 385; y2: 82),
    (x1: 274; y1: 163; x2: 385; y2: 242)
  );

implementation

end.
