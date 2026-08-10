{ GERADO por wte/tools/port_database_pas.py -- NAO editar a mao.

  Transpilado de src/core/include/we2002/Player.hpp, src/core/Player.cpp, que ja e byte-identico ao `ed.exe` nas duas ROMs.
  A entrada do transpilador e SEMPRE codigo deste repositorio -- nunca saida de
  decompilador (PLAN-WTE-LAZARUS §8.10).

  Os seeks, os comprimentos de leitura e os limites de laco estao intocados:
  eles codificam o layout MODE2/2352 da imagem, inclusive os saltos manuais
  sobre cabecalho de setor.

  Os trechos marcados PORTE A MAO nao sao transpilacao: sao decisao ja escrita
  em wte/re/tipos.md, com a rota registrada em wte/re/recusas.md.

  Regenerar:  python3 wte/tools/port_database_pas.py
  Conferir:   python3 wte/tools/port_database_pas.py --check }

unit we2002_player;

{$mode objfpc}{$H+}
{$modeswitch advancedrecords}

interface

type
  /// A player as stored on the CD image.
  TPlayer = record
    url: array[0..499] of AnsiChar;
    name: array[0..10] of AnsiChar;
    position: LongInt;
    skin_colour: LongInt;
    hair_style: LongInt;
    hair_colour: LongInt;
    beard_style: LongInt;
    beard_colour: LongInt;
    height: LongInt;
    build: LongInt;
    age: LongInt;
    boots: LongInt;
    foot: LongInt;
    attack: LongInt;
    defence: LongInt;
    strength: LongInt;
    stamina: LongInt;
    speed: LongInt;
    acceleration: LongInt;
    passing: LongInt;
    shot_power: LongInt;
    shot_accuracy: LongInt;
    jump: LongInt;
    heading: LongInt;
    technique: LongInt;
    dribbling: LongInt;
    swerve: LongInt;
    aggression: LongInt;
    reflexes: LongInt;
    out_of_position: LongInt;
    number: LongInt;
    cost: LongInt;
    /// The 12 raw bytes as they appear on the disc.
    raw_attributes: array[0..11] of ShortInt;

    procedure Init;
    /// Unpack `raw_attributes` (12 packed bytes off the disc) into the members.
    ///
    /// The original spelled this pair backwards: its decoder was called
    /// "codifica_carat" and its encoder "decodifica". Decode/Encode here,
    /// matching the direction of travel.
    procedure Decode;
    /// Repack the members back into `raw_attributes`.
    procedure Encode;
  end;

implementation

{ `Player::Player() = default` mais os
  inicializadores de membro do cabecalho: o objeto sai zerado.
  Registro local NAO e zerado pelo FPC -- dai o Default(). }
procedure TPlayer.Init;
begin
  Self := Default(TPlayer);
end;

procedure TPlayer.Decode;
begin
  // blob -> members
  position := raw_attributes[0] and $07;
  skin_colour := raw_attributes[4] and $03;
  hair_style := ((raw_attributes[0] shr 4) and $0f) + ((raw_attributes[1] shl 4) and $10);
  hair_colour := (raw_attributes[1] shr 1) and $07;
  beard_style := (raw_attributes[1] shr 5) and $07;
  beard_colour := (raw_attributes[2] shr 1) and $07;
  height := 148 + ((raw_attributes[2] shr 4) and $0f) + ((raw_attributes[3] shl 4) and $30);
  build := (raw_attributes[4] shr 2) and $07;
  age := 15 + ((raw_attributes[4] shr 5) and $07) + ((raw_attributes[5] shl 3) and $18);
  boots := (raw_attributes[11] shr 3) and $07;
  foot := (raw_attributes[11] shr 6) and $03;
  attack := 12 + ((raw_attributes[7] shr 5) and $07);
  defence := 12 + (raw_attributes[8] and $07);
  strength := 12 + ((raw_attributes[5] shr 6) and $03) + ((raw_attributes[6] shl 2) and $04);
  stamina := 12 + ((raw_attributes[6] shr 1) and $07);
  speed := 12 + ((raw_attributes[6] shr 7) and $01) + ((raw_attributes[7] shl 1) and $06);
  acceleration := 12 + ((raw_attributes[7] shr 2) and $07);
  passing := 12 + ((raw_attributes[9] shr 1) and $07);
  shot_power := 12 + ((raw_attributes[8] shr 3) and $07);
  shot_accuracy := 12 + ((raw_attributes[8] shr 6) and $03) + ((raw_attributes[9] shl 2) and $04);
  jump := 12 + ((raw_attributes[10] shr 2) and $07);
  heading := 12 + ((raw_attributes[9] shr 7) and $01) + ((raw_attributes[10] shl 1) and $06);
  technique := 12 + ((raw_attributes[9] shr 4) and $07);
  dribbling := 12 + ((raw_attributes[6] shr 4) and $07);
  swerve := 12 + ((raw_attributes[10] shr 5) and $07);
  aggression := 12 + (raw_attributes[11] and $07);
  reflexes := 12 + ((raw_attributes[5] shr 2) and $07);
  out_of_position := (raw_attributes[3] shr 7) and $01;
  number := 1 + ((raw_attributes[3] shr 2) and $1f);
end;

procedure TPlayer.Encode;
begin
  // members -> blob
  raw_attributes[3] := raw_attributes[3] and ($01);
  raw_attributes[3] := raw_attributes[3] or ((number-1) shl 2);
  raw_attributes[3] := raw_attributes[3] and ($7f);
  raw_attributes[3] := raw_attributes[3] or (out_of_position shl 7);
  raw_attributes[0] := raw_attributes[0] and ($f8);
  raw_attributes[0] := raw_attributes[0] or (position);
  raw_attributes[4] := raw_attributes[4] and ($fc);
  raw_attributes[4] := raw_attributes[4] or (skin_colour);
  raw_attributes[0] := raw_attributes[0] and ($0f);
  raw_attributes[0] := raw_attributes[0] or (hair_style shl 4);
  raw_attributes[1] := raw_attributes[1] and ($fe);
  raw_attributes[1] := raw_attributes[1] or (hair_style shr 4);
  raw_attributes[1] := raw_attributes[1] and ($f1);
  raw_attributes[1] := raw_attributes[1] or (hair_colour shl 1);
  raw_attributes[1] := raw_attributes[1] and ($1f);
  raw_attributes[1] := raw_attributes[1] or (beard_style shl 5);
  raw_attributes[2] := raw_attributes[2] and ($f1);
  raw_attributes[2] := raw_attributes[2] or (beard_colour shl 1);
  raw_attributes[2] := raw_attributes[2] and ($0f);
  raw_attributes[2] := raw_attributes[2] or ((height-148) shl 4);
  raw_attributes[3] := raw_attributes[3] and ($fc);
  raw_attributes[3] := raw_attributes[3] or ((height-148) shr 4);
  raw_attributes[4] := raw_attributes[4] and ($e3);
  raw_attributes[4] := raw_attributes[4] or (build shl 2);
  raw_attributes[4] := raw_attributes[4] and ($1f);
  raw_attributes[4] := raw_attributes[4] or ((age-15) shl 5);
  raw_attributes[5] := raw_attributes[5] and ($fc);
  raw_attributes[5] := raw_attributes[5] or ((age-15) shr 3);
  raw_attributes[11] := raw_attributes[11] and ($c7);
  raw_attributes[11] := raw_attributes[11] or (boots shl 3);
  raw_attributes[11] := raw_attributes[11] and ($3f);
  raw_attributes[11] := raw_attributes[11] or (foot shl 6);
  raw_attributes[7] := raw_attributes[7] and ($1f);
  raw_attributes[7] := raw_attributes[7] or ((attack-12) shl 5);
  raw_attributes[8] := raw_attributes[8] and ($f8);
  raw_attributes[8] := raw_attributes[8] or (defence-12);
  raw_attributes[5] := raw_attributes[5] and ($3f);
  raw_attributes[5] := raw_attributes[5] or ((strength-12) shl 6);
  raw_attributes[6] := raw_attributes[6] and ($fe);
  raw_attributes[6] := raw_attributes[6] or ((strength-12) shr 2);
  raw_attributes[6] := raw_attributes[6] and ($f1);
  raw_attributes[6] := raw_attributes[6] or ((stamina-12) shl 1);
  raw_attributes[6] := raw_attributes[6] and ($7f);
  raw_attributes[6] := raw_attributes[6] or ((speed-12) shl 7);
  raw_attributes[7] := raw_attributes[7] and ($fc);
  raw_attributes[7] := raw_attributes[7] or ((speed-12) shr 1);
  raw_attributes[7] := raw_attributes[7] and ($e3);
  raw_attributes[7] := raw_attributes[7] or ((acceleration-12) shl 2);
  raw_attributes[9] := raw_attributes[9] and ($f1);
  raw_attributes[9] := raw_attributes[9] or ((passing-12) shl 1);
  raw_attributes[8] := raw_attributes[8] and ($c7);
  raw_attributes[8] := raw_attributes[8] or ((shot_power-12) shl 3);
  raw_attributes[8] := raw_attributes[8] and ($3f);
  raw_attributes[8] := raw_attributes[8] or ((shot_accuracy-12) shl 6);
  raw_attributes[9] := raw_attributes[9] and ($fe);
  raw_attributes[9] := raw_attributes[9] or ((shot_accuracy-12) shr 2);
  raw_attributes[10] := raw_attributes[10] and ($e3);
  raw_attributes[10] := raw_attributes[10] or ((jump-12) shl 2);
  raw_attributes[9] := raw_attributes[9] and ($7f);
  raw_attributes[9] := raw_attributes[9] or ((heading-12) shl 7);
  raw_attributes[10] := raw_attributes[10] and ($fc);
  raw_attributes[10] := raw_attributes[10] or ((heading-12) shr 1);
  raw_attributes[9] := raw_attributes[9] and ($8f);
  raw_attributes[9] := raw_attributes[9] or ((technique-12) shl 4);
  raw_attributes[6] := raw_attributes[6] and ($8f);
  raw_attributes[6] := raw_attributes[6] or ((dribbling-12) shl 4);
  raw_attributes[10] := raw_attributes[10] and ($1f);
  raw_attributes[10] := raw_attributes[10] or ((swerve-12) shl 5);
  raw_attributes[11] := raw_attributes[11] and ($f8);
  raw_attributes[11] := raw_attributes[11] or (aggression-12);
  raw_attributes[5] := raw_attributes[5] and ($e3);
  raw_attributes[5] := raw_attributes[5] or ((reflexes-12) shl 2);
end;

end.
