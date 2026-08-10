{ GERADO por wte/tools/port_database_pas.py -- NAO editar a mao.

  Transpilado de src/core/include/we2002/Team.hpp, src/core/Team.cpp, que ja e byte-identico ao `ed.exe` nas duas ROMs.
  A entrada do transpilador e SEMPRE codigo deste repositorio -- nunca saida de
  decompilador (PLAN-WTE-LAZARUS §8.10).

  Os seeks, os comprimentos de leitura e os limites de laco estao intocados:
  eles codificam o layout MODE2/2352 da imagem, inclusive os saltos manuais
  sobre cabecalho de setor.

  Os trechos marcados PORTE A MAO nao sao transpilacao: sao decisao ja escrita
  em wte/re/tipos.md, com a rota registrada em wte/re/recusas.md.

  Regenerar:  python3 wte/tools/port_database_pas.py
  Conferir:   python3 wte/tools/port_database_pas.py --check }

unit we2002_team;

{$mode objfpc}{$H+}
{$modeswitch advancedrecords}

interface

uses
  we2002_types;

type
  /// A national team or all-star side (63 of them).
  TTeam = record
    /// Six all-caps spellings of the team name, of differing lengths; which
    /// one the game shows depends on the screen. TEAM_NAME_LEN_1..6 give the
    /// byte length of each slot per team.
    names: array[0..5] of array[0..19] of AnsiChar;
    /// The mixed-case spelling -- "Bayern", not "BAYERN". The original's name
    /// for it ended in _m, for *minuscolo*, and phase 2 mis-glossed that as
    /// "long name". It is not longer, it is the same name in mixed case.
    mixed_case_name: array[0..19] of AnsiChar;
    abbreviations: array[0..2] of array[0..3] of AnsiChar;
    /// The Japanese name, decoded to ASCII by KanjiToAscii, and the raw
    /// two-byte-per-character form it was decoded from.
    kanji_name: array[0..19] of AnsiChar;
    raw_kanji_name: array[0..39] of AnsiChar;
    /// The five strength bars shown on the team screen.
    bar_attack: ShortInt;
    bar_defence: ShortInt;
    bar_power: ShortInt;
    bar_speed: ShortInt;
    bar_technique: ShortInt;
    /// Set-piece takers and the captain, each an index into the squad.
    kick_long_fk: ShortInt;
    kick_short_fk: ShortInt;
    kick_left_corner: ShortInt;
    kick_right_corner: ShortInt;
    kick_penalty: ShortInt;
    captain: ShortInt;
    /// The formation, as the 30-byte blob the disc stores, plus the role and
    /// pitch position of each of the ten outfield slots.
    ///
    /// 31 and not 30: Load() reads the 30 bytes and then strcpy()s them here,
    /// so the terminator needs a byte of its own. The original declared 30 and
    /// wrote the NUL one past the end, into slot_role[0]; every -O2 build with
    /// _FORTIFY_SOURCE aborts on that. Save() writes a fixed 30 bytes, so the
    /// extra byte never reaches the disc. See docs/PLAN-LINUX.md phase 6.
    raw_formation: array[0..30] of AnsiChar;
    slot_role: array[0..9] of ShortInt;
    slot_x: array[0..9] of ShortInt;
    slot_y: array[0..9] of ShortInt;
    flag_shape: ShortInt;
    flag_colours: array[0..15] of Word;
    home_kit: array[0..15] of Word;
    away_kit: array[0..15] of Word;
    raw_strategy: array[0..3] of ShortInt;
    squad_numbers: TSquadNumbers;

    procedure Init;
  end;
  /// A Master League club (32 of them). Same shape as Team, but with eight name
  /// slots instead of six, a link table, and squad numbers stored unpacked.
  TMlTeam = record
    names: array[0..7] of array[0..19] of AnsiChar;
    mixed_case_name: array[0..19] of AnsiChar;
    abbreviations: array[0..2] of array[0..3] of AnsiChar;
    kanji_name: array[0..19] of AnsiChar;
    raw_kanji_name: array[0..39] of AnsiChar;
    bar_attack: ShortInt;
    bar_defence: ShortInt;
    bar_power: ShortInt;
    bar_speed: ShortInt;
    bar_technique: ShortInt;
    kick_long_fk: ShortInt;
    kick_short_fk: ShortInt;
    kick_left_corner: ShortInt;
    kick_right_corner: ShortInt;
    kick_penalty: ShortInt;
    captain: ShortInt;
    /// 31 for the same reason as Team::raw_formation.
    raw_formation: array[0..30] of AnsiChar;
    slot_role: array[0..9] of ShortInt;
    slot_x: array[0..9] of ShortInt;
    slot_y: array[0..9] of ShortInt;
    flag_shape: ShortInt;
    flag_colours: array[0..15] of Word;
    home_kit: array[0..15] of Word;
    away_kit: array[0..15] of Word;
    raw_numbers: array[0..22] of ShortInt;
    link: array[0..45] of Byte;
    raw_strategy: array[0..3] of ShortInt;

    procedure Init;
  end;
  /// One of the 16 preset formations.
  TFormation = record
    name: array[0..6] of AnsiChar;
    roles: array[0..10] of ShortInt;
    x: array[0..9] of ShortInt;
    y: array[0..9] of ShortInt;

    procedure Init;
  end;

implementation

{ `Team::Team() = default` mais os
  inicializadores de membro do cabecalho: o objeto sai zerado.
  Registro local NAO e zerado pelo FPC -- dai o Default(). }
procedure TTeam.Init;
begin
  Self := Default(TTeam);
end;

{ `MlTeam::MlTeam() = default` mais os
  inicializadores de membro do cabecalho: o objeto sai zerado.
  Registro local NAO e zerado pelo FPC -- dai o Default(). }
procedure TMlTeam.Init;
begin
  Self := Default(TMlTeam);
end;

{ `Formation::Formation() = default` mais os
  inicializadores de membro do cabecalho: o objeto sai zerado.
  Registro local NAO e zerado pelo FPC -- dai o Default(). }
procedure TFormation.Init;
begin
  Self := Default(TFormation);
end;

end.
