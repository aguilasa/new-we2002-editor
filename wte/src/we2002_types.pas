{ GERADO por wte/tools/port_database_pas.py -- NAO editar a mao.

  Transpilado de src/core/include/we2002/Types.hpp, que ja e byte-identico ao `ed.exe` nas duas ROMs.
  A entrada do transpilador e SEMPRE codigo deste repositorio -- nunca saida de
  decompilador (PLAN-WTE-LAZARUS §8.10).

  Os seeks, os comprimentos de leitura e os limites de laco estao intocados:
  eles codificam o layout MODE2/2352 da imagem, inclusive os saltos manuais
  sobre cabecalho de setor.

  Os trechos marcados PORTE A MAO nao sao transpilacao: sao decisao ja escrita
  em wte/re/tipos.md, com a rota registrada em wte/re/recusas.md.

  Regenerar:  python3 wte/tools/port_database_pas.py
  Conferir:   python3 wte/tools/port_database_pas.py --check }

unit we2002_types;

{$mode objfpc}{$H+}
{$modeswitch advancedrecords}

interface

const
  // Population of the three player pools, in the order they sit on the disc.
  PLAYERS_NC = 462;  // "non-contract" free agents
  PLAYERS_NATIONAL_ALLSTAR = 1449;
  PLAYERS_TOTAL = 1911;
  TEAMS_NATIONAL = 54;
  TEAMS_ALLSTAR = 9;
  TEAMS_ML = 32;
  TEAMS_NATIONAL_ALLSTAR = TEAMS_NATIONAL + TEAMS_ALLSTAR;  // 63
  /// Storage for the national/all-star array: 64 slots, not 63.
  ///
  /// The original declared `squadra squad_nazall[63]` and then looped to 64 in
  /// three places (legacy/mfc/edDlg.cpp:1928, :5821, :7667), reading and writing
  /// 16 bytes past the end of the array every time. On Windows that clobbered
  /// whichever global happened to follow; on Linux it lands somewhere else
  /// entirely, so the overrun could never be reproduced faithfully -- it is
  /// undefined behaviour, not a behaviour.
  ///
  /// The disc genuinely holds 64 squad-number records at
  /// OFS_SQUAD_NUMBERS_NATIONAL, so the fix is to give the array its 64th slot.
  /// Load() then reads all 64 and Save() writes the same 64 back, which makes
  /// that region round-trip unchanged. Only slots 0..62 are ever shown in the
  /// UI, and the golden test against ed.exe pins the 64th down -- it is the one
  /// place where the port deliberately differs from the original.
  TEAMS_NATIONAL_ALLSTAR_SLOTS = 64;

type
  { PORTE A MAO (rota 3) -- wte/re/tipos.md, decisao 2.

    O C++ declara 23 bitfields de 5 bits. O FPC tem `bitpacked record`, mas a
    ordem de bit dele e definida pelo compilador e pelo endianness, e nao e
    obrigada a casar com o que o MSVC fez em 2002. O layout abaixo e o que o
    TestSquadNumbersLayout do newWe2002 fixou: quatro unidades de 32 bits
    little-endian, campos alocados do bit menos significativo para cima, 5 bits
    cada; `numero[k]` mora na unidade `k div 6`, deslocado `5 * (k mod 6)`. }
  TSquadNumbers = packed record
    groups: array[0..3] of LongWord;
  end;


function SquadNumberAt(const n: TSquadNumbers; slot: LongInt): LongWord;
procedure SetSquadNumberAt(var n: TSquadNumbers; slot: LongInt; v: LongWord);

{ Copia com semantica de C -- ver o corpo. }
procedure CStrCopy(var dest; const src);
procedure CStrCat(var dest; const src);
function CStrLen(const s): SizeInt;

implementation

{ PORTE A MAO (rota 3) -- indice fora de 0..22 devolve 0 e ignora escrita, como
  o SquadNumberAt do C++, em vez de alcancar o campo vizinho. }
function SquadNumberAt(const n: TSquadNumbers; slot: LongInt): LongWord;
begin
  if (slot < 0) or (slot > 22) then
  begin
    Result := 0;
    Exit;
  end;
  Result := (n.groups[slot div 6] shr (5 * (slot mod 6))) and $1F;
end;

procedure SetSquadNumberAt(var n: TSquadNumbers; slot: LongInt; v: LongWord);
var
  grupo, deslocamento: LongInt;
begin
  if (slot < 0) or (slot > 22) then
    Exit;
  grupo := slot div 6;
  deslocamento := 5 * (slot mod 6);
  n.groups[grupo] := (n.groups[grupo] and not (LongWord($1F) shl deslocamento))
                     or ((v and $1F) shl deslocamento);
end;

{ PORTE A MAO (rota 3) -- wte/re/tipos.md, decisao 1.

  Semantica de C: copia ATE o #0 inclusive, SEM checar limite. Nao usar
  StrPCopy/StrLCopy, que truncam de outro jeito -- o truncamento do original
  pode ser load-bearing no formato, e o newWe2002 mediu um destes estourando um
  byte em TODA imagem aberta (raw_formation recebendo 30 bytes + terminador). A
  correcao la foi alargar o destino para 31, nao silenciar a copia; o Pascal
  herda os dois. }
procedure CStrCopy(var dest; const src);
var
  d, s: PByte;
begin
  d := @dest;
  s := @src;
  while s^ <> 0 do
  begin
    d^ := s^;
    Inc(d);
    Inc(s);
  end;
  d^ := 0;
end;

procedure CStrCat(var dest; const src);
var
  d, s: PByte;
begin
  d := @dest;
  while d^ <> 0 do
    Inc(d);
  s := @src;
  while s^ <> 0 do
  begin
    d^ := s^;
    Inc(d);
    Inc(s);
  end;
  d^ := 0;
end;

function CStrLen(const s): SizeInt;
var
  p: PByte;
begin
  p := @s;
  Result := 0;
  while p^ <> 0 do
  begin
    Inc(p);
    Inc(Result);
  end;
end;

end.
