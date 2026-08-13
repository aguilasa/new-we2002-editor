{ wte_legendas -- as legendas enumeradas da ficha do jogador.

  GERADO por wte/tools/dump_legendas.py a partir de
  we-team-editor/we-team-editor.exe. NAO EDITAR A MAO: a correcao vai
  no gerador, e depois se regenera.

  LEGENDAS e o que o inicializador do original monta em 0x00423798 --
  12 linhas de 8, indexada por (sufixo do `flechasapa` menos um,
  posicao do `TUpDown`). Linha mais curta que a faixa do controle
  preenche o resto com um espaco, como o original.

  CABELO e a tabela propria de flechasapa3, em 0x00423918: a
  forma do cabelo tem faixa maior que uma linha e nao cabe na primeira
  tabela. }
unit wte_legendas;

{$mode objfpc}{$H+}

interface

const
  LEGENDA_LINHAS = 12;
  LEGENDA_COLUNAS = 8;
  LEGENDA_CABELO = 32;

  LEGENDAS: array[0..LEGENDA_LINHAS - 1, 0..LEGENDA_COLUNAS - 1] of string = (
    ('Gl', 'Za', 'Lt', 'Vl', 'Al', 'Me', 'At', 'Po'),
    ('A', 'B', 'C', 'D', ' ', ' ', ' ', ' '),
    (' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '),
    ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'),
    ('A', 'B', 'C', 'D', 'E', 'F', 'G', ' '),
    ('A', 'B', 'C', 'D', 'E', 'F', 'G', ' '),
    (' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '),
    ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'),
    (' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '),
    ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'),
    ('Dire.', 'Esq.', 'Dois', ' ', ' ', ' ', ' ', ' '),
    ('NO', 'YES', ' ', ' ', ' ', ' ', ' ', ' ')
  );

  CABELO: array[0..LEGENDA_CABELO - 1] of string = (
    'A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'B4', 'B5',
    'B6', 'C1', 'C2', 'D1', 'D2', 'E1', 'E2', 'F1',
    'F2', 'F3', 'G1', 'H1', 'I1', 'I2', 'I3', 'J1',
    'K1', 'L1', 'L2', 'L3', 'M1', 'N1', 'O1', 'P1'
  );

{ A legenda de um `flechasapa`, ou cadeia vazia quando o par esta fora
  da tabela. Fora da tabela nao e erro: altura e idade mostram numero,
  e a forma do cabelo tem a LegendaDoCabelo. }
function Legenda(indice, posicao: Integer): string;

{ O nome da forma do cabelo, ou cadeia vazia fora da faixa. }
function LegendaDoCabelo(posicao: Integer): string;

implementation

function Legenda(indice, posicao: Integer): string;
begin
  if (indice < 1) or (indice > LEGENDA_LINHAS) or (posicao < 0)
     or (posicao >= LEGENDA_COLUNAS) then
    Result := ''
  else
    Result := LEGENDAS[indice - 1, posicao];
end;

function LegendaDoCabelo(posicao: Integer): string;
begin
  if (posicao < 0) or (posicao >= LEGENDA_CABELO) then
    Result := ''
  else
    Result := CABELO[posicao];
end;

end.
