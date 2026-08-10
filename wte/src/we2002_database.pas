{ GERADO por wte/tools/port_database_pas.py -- NAO editar a mao.

  Transpilado de src/core/include/we2002/Database.hpp, src/core/Database.cpp, que ja e byte-identico ao `ed.exe` nas duas ROMs.
  A entrada do transpilador e SEMPRE codigo deste repositorio -- nunca saida de
  decompilador (PLAN-WTE-LAZARUS §8.10).

  Os seeks, os comprimentos de leitura e os limites de laco estao intocados:
  eles codificam o layout MODE2/2352 da imagem, inclusive os saltos manuais
  sobre cabecalho de setor.

  Os trechos marcados PORTE A MAO nao sao transpilacao: sao decisao ja escrita
  em wte/re/tipos.md, com a rota registrada em wte/re/recusas.md.

  Regenerar:  python3 wte/tools/port_database_pas.py
  Conferir:   python3 wte/tools/port_database_pas.py --check }

unit we2002_database;

{$mode objfpc}{$H+}
{$modeswitch advancedrecords}
{$POINTERMATH ON}  { `lk[0]` sobre PByte, como no C++ }

interface

uses
  we2002_types, we2002_team, we2002_player, we2002_cdimage, we2002_offsets, we2002_tables;

type
  { `using Reporter = std::function<void(const std::string&)>` do Database.hpp.
    PORTE A MAO (rota 3): pode ser nil, como o std::function vazio. }
  TReporter = procedure(const msg: string) of object;
  /// Everything the editor holds in memory about one CD image.
  ///
  /// In the original these were file-scope globals in edDlg.cpp, shared by the
  /// dialog and every handler. They are gathered here so that loading two images
  /// in one process is possible and, more immediately, so the golden tests can
  /// build an instance without standing up a GUI.
  TDatabase = record
    /// Non-contract players first, then the national and all-star squads.
    players: array[0..PLAYERS_TOTAL - 1] of TPlayer;
    /// National teams then all-stars. 64 slots, of which only 0..62 are real
    /// teams -- see TEAMS_NATIONAL_ALLSTAR_SLOTS for why the 64th exists.
    teams: array[0..TEAMS_NATIONAL_ALLSTAR_SLOTS - 1] of TTeam;
    ml_teams: array[0..TEAMS_ML - 1] of TMlTeam;  ///< Master League clubs
    ml_default: TMlTeam;  ///< the default-ML template
    preset_formations: array[0..15] of TFormation;  ///< the 16 preset formations
    link_euro_allstar: array[0..45] of Byte;
    link_world_allstar: array[0..45] of Byte;

    procedure Init;
    /// Read the whole database out of a raw MODE2/2352 image.
    /// Returns false only if the file cannot be opened.
    function Load(const image: string; const report: TReporter): Boolean;
    /// Write the in-memory state back into the image, in place.
    ///
    /// Does NOT recalculate EDC/ECC -- see CdImage.hpp. Returns false only if
    /// the file cannot be opened for writing.
    function Save(const image: string; const report: TReporter): Boolean;
    /// Copy the all-star squads' player names in from whoever their link
    /// tables point at. Called at the end of Load().
    procedure CopyAllStarNames;
    // PORTE A MAO (rota 3) -- tipos.md decisao 5; substitui o bloco
    // de std::ofstream do OnWriteCD.
    procedure WriteUrlSidecar(const image: string);
  end;

procedure Reportar(const report: TReporter; const msg: string);
function UrlSidecarPath(const image: string): string;

/// Resolve a two-byte Master League link into an index into Database::players.
function ResolveMlLink(lk: PByte): LongInt;
/// Transfer value for players[i], derived from the player's attributes.
function ComputePlayerCost(const db: TDatabase; i: LongInt): LongInt;

implementation

uses
  Classes, SysUtils, StrUtils, Math, we2002_textcodec;

{ PORTE A MAO (rota 3) -- o `if (report)` do C++ testa um std::function vazio. }
procedure Reportar(const report: TReporter; const msg: string);
begin
  if Assigned(report) then
    report(msg);
end;

{ PORTE A MAO (rota 3) -- caminho do sidecar "<imagem>_url.txt".

  O original montava isto com CString::Replace(".bin", "_url.txt"), que troca
  TODA ocorrencia e nao so a extensao. Reproduzido como e: um diretorio chamado
  "foo.bin" tambem seria reescrito, e mudar isso mudaria qual arquivo o editor
  le de volta. }
function UrlSidecarPath(const image: string): string;
const
  DE = '.bin';
  PARA = '_url.txt';
var
  at_: SizeInt;
begin
  Result := image;
  at_ := Pos(DE, Result);
  while at_ > 0 do
  begin
    Delete(Result, at_, Length(DE));
    Insert(PARA, Result, at_);
    at_ := PosEx(DE, Result, at_ + Length(PARA));
  end;
end;

{ PORTE A MAO (rota 3) -- wte/re/tipos.md, decisao 5.

  Byte a byte, e por isso NAO e TStringList: o SaveToFile dele usa o LineEnding
  da plataforma e tem WriteBOM, e este arquivo e do usuario. Uma linha por
  jogador, terminador #10, sem #13 e sem BOM. }
procedure TDatabase.WriteUrlSidecar(const image: string);
var
  arquivo: TFileStream;
  i: LongInt;
  linha: string;
  lf: Byte;
begin
  lf := 10;
  arquivo := TFileStream.Create(UrlSidecarPath(image), fmCreate);
  try
    for i := 0 to PLAYERS_TOTAL - 1 do
    begin
      linha := PAnsiChar(@players[i].url[0]);
      if linha <> '' then
        arquivo.WriteBuffer(linha[1], Length(linha));
      arquivo.WriteBuffer(lf, 1);
    end;
  finally
    arquivo.Free;
  end;
end;

{ `Database::Database() = default` mais os
  inicializadores de membro do cabecalho: o objeto sai zerado.
  Registro local NAO e zerado pelo FPC -- dai o Default(). }
procedure TDatabase.Init;
begin
  Self := Default(TDatabase);
end;

function ResolveMlLink(lk: PByte): LongInt;
var
  team: LongWord;
  slot: LongWord;
  r: LongInt;
begin
  // From legacy/mfc/edDlg.cpp:3430, minus one dead expression statement that
  // read a player name and threw it away, and plus two bounds checks the
  // original did not have.
  //
  // A link is (team code, position). On a real image the team code is 0..119
  // and the result lands inside players[], so neither check ever fires --
  // which is what the golden tests demonstrate. On anything else, which is to
  // say on whatever file a user opens by mistake, the original read past the
  // end of START_LINK's 120 entries and then indexed players[] with the
  // garbage that came out. The first symptom was a crash before the window
  // even appeared, with nothing on stderr.
  //
  // Out of range resolves to player 0 rather than to nothing, because every
  // caller uses the result as an index immediately and none of them has an
  // error path to take.
  team := lk[0];
  slot := lk[1];
  r := 0;
  if slot > 22 then
  begin
    if team >= LongWord(START_LINK_COUNT) then
    begin
      Result := 0;
      Exit;
    end;
    r := LongInt(slot) + START_LINK[team] - 23;
  end
  else
  begin
    r := LongInt((team * 23) + slot) + PLAYERS_NC;
  end;
  if (r < 0)  or  (r >= PLAYERS_TOTAL) then
  begin
    Result := 0;
    Exit;
  end;
  Result := r;
  Exit;
end;

procedure TDatabase.CopyAllStarNames;
var
  i: LongInt;
begin
  // Verbatim from legacy/mfc/edDlg.cpp:8418.
  for i := 0 to 22 do
  begin
    // euro
    CStrCopy(players[462 + (54 * 23) + i].name, players[ResolveMlLink(@link_euro_allstar[i * 2])].name);
    // world
    CStrCopy(players[462 + (55 * 23) + i].name, players[ResolveMlLink(@link_world_allstar[i * 2])].name);
  end;
end;

function TDatabase.Load(const image: string; const report: TReporter): Boolean;
var
  i: LongInt;
  j: LongInt;
  colour_buf: array[0..15] of Word;
  buf: array[0..49] of AnsiChar;
  buf1: array[0..49] of AnsiChar;
  name_buf: array[0..10] of AnsiChar;
  image_file: TCdImage;
begin
  image_file.Init;
  if not image_file.OpenRead(image) then
  begin
    Reportar(report, 'Error ! Impossible to open CD image !');
    Result := false;
    Exit;
  end;
  // teams
  //load names 
  // kanji batch, ml clubs
  image_file.Seek(OFS_TEAM_NAME_KANJI, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Read(ml_teams[31-i].raw_kanji_name,TEAM_NAME_KANJI_LEN[94-i]*2);
    KanjiToAscii(@ml_teams[31-i].raw_kanji_name, @ml_teams[31-i].kanji_name, TEAM_NAME_KANJI_LEN[94-i]);
  end;
  for i := 0 to 62 do
  begin
    if i = 58 then
    begin
      image_file.Read(teams[62-i].raw_kanji_name,4);
      image_file.Seek(OFS_TEAM_NAME_KANJI_A, soBeginning);
      image_file.Read(buf,8);
      for j := 0 to 7 do
      begin
        teams[62-i].raw_kanji_name[4+j] := buf[j];
      end;
    end
    else
    begin
      image_file.Read(teams[62-i].raw_kanji_name,TEAM_NAME_KANJI_LEN[62-i]*2);
    end;
    KanjiToAscii(@teams[62-i].raw_kanji_name, @teams[62-i].kanji_name, TEAM_NAME_KANJI_LEN[62-i]);
  end;
  //1st batch - ml
  image_file.Seek(OFS_TEAM_NAME_1, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Read(buf,TEAM_NAME_LEN_1[94-i]);
    CStrCopy(ml_teams[31-i].names[0],buf);
  end;
  //1st batch - national and all-star - jump - yugoslavia (24th)
  for i := 0 to 62 do
  begin
    if i = 40 then
    begin
      image_file.Seek(OFS_TEAM_NAME_1_A, soBeginning);
    end;
    image_file.Read(buf,TEAM_NAME_LEN_1[62-i]);
    CStrCopy(teams[62-i].names[0],buf);
  end;
  //2nd batch - ml
  image_file.Seek(OFS_TEAM_NAME_2, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Read(buf,TEAM_NAME_LEN_2[94-i]);
    CStrCopy(ml_teams[31-i].names[1],buf);
  end;
  //2nd batch - national and all-star 
  for i := 0 to 62 do
  begin
    image_file.Read(buf,TEAM_NAME_LEN_2[62-i]);
    CStrCopy(teams[62-i].names[1],buf);
  end;
  //3rd batch - ml
  image_file.Seek(OFS_TEAM_NAME_3, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Read(buf,TEAM_NAME_LEN_3[94-i]);
    CStrCopy(ml_teams[31-i].names[2],buf);
  end;
  //3rd batch - national and all-star 
  for i := 0 to 62 do
  begin
    image_file.Read(buf,TEAM_NAME_LEN_3[62-i]);
    CStrCopy(teams[62-i].names[2],buf);
  end;
  //4th batch - ml
  image_file.Seek(OFS_TEAM_NAME_4, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Read(buf,TEAM_NAME_LEN_4[94-i]);
    CStrCopy(ml_teams[31-i].names[3],buf);
  end;
  //4th batch - national and all-star 
  for i := 0 to 62 do
  begin
    image_file.Read(buf,TEAM_NAME_LEN_4[62-i]);
    CStrCopy(teams[62-i].names[3],buf);
  end;
  //5th batch - ml
  image_file.Seek(OFS_TEAM_NAME_5, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Read(buf,TEAM_NAME_LEN_5[94-i]);
    CStrCopy(ml_teams[31-i].names[4],buf);
  end;
  //5th batch - national and all-star - jump - france (7th)
  for i := 0 to 62 do
  begin
    if i = 57 then
    begin
      image_file.Read(buf1, 4);
      buf1[4] := AnsiChar(0);
      CStrCopy(buf, buf1);
      image_file.Seek(OFS_TEAM_NAME_5_A, soBeginning);
      image_file.Read(buf1, 4);
      CStrCat(buf, buf1);
    end
    else
    begin
      image_file.Read(buf,TEAM_NAME_LEN_5[62-i]);
    end;
    CStrCopy(teams[62-i].names[4],buf);
  end;
  //6th batch - ml
  image_file.Seek(OFS_TEAM_NAME_6, soBeginning);
  for i := 0 to 31 do
  begin
    if i = 15 then
    begin
      image_file.Seek(OFS_TEAM_NAME_6_A, soBeginning);
    end;
    image_file.Read(buf,TEAM_NAME_LEN_6[94-i]);
    CStrCopy(ml_teams[31-i].names[5],buf);
  end;
  //6th batch - national and all-star 
  image_file.Seek(OFS_TEAM_NAME_6_B, soBeginning);
  for i := 0 to 62 do
  begin
    image_file.Read(buf,TEAM_NAME_LEN_6[62-i]);
    CStrCopy(teams[62-i].names[5],buf);
  end;
  //mixed case, ml clubs
  image_file.Seek(OFS_TEAM_MIXED_CASE_NAME, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Read(buf,TEAM_MIXED_CASE_NAME_LEN[94-i]);
    CStrCopy(ml_teams[31-i].mixed_case_name,buf);
  end;
  //mixed case, national and all-star 
  for i := 0 to 62 do
  begin
    image_file.Read(buf,TEAM_MIXED_CASE_NAME_LEN[62-i]);
    CStrCopy(teams[62-i].mixed_case_name,buf);
  end;
  //abbrev.1 - ml
  buf1[4] := AnsiChar(0);
  image_file.Seek(OFS_TEAM_ABBREV_1, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Read(buf1,4);
    CStrCopy(ml_teams[31-i].abbreviations[0],buf1);
  end;
  //abbrev.1 - national and all-star 
  for i := 0 to 62 do
  begin
    image_file.Read(buf1,4);
    CStrCopy(teams[62-i].abbreviations[0],buf1);
  end;
  //abbrev.2 - ml
  image_file.Seek(OFS_TEAM_ABBREV_2, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Read(buf1,4);
    CStrCopy(ml_teams[31-i].abbreviations[1],buf1);
  end;
  //abbrev.2 - national and all-star 
  for i := 0 to 62 do
  begin
    image_file.Read(buf1,4);
    CStrCopy(teams[62-i].abbreviations[1],buf1);
  end;
  //abbrev.3 - ml
  image_file.Seek(OFS_TEAM_ABBREV_3, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Read(buf1,4);
    CStrCopy(ml_teams[31-i].abbreviations[2],buf1);
  end;
  //abbrev.3 - national and all-star 
  for i := 0 to 62 do
  begin
    image_file.Read(buf1,4);
    CStrCopy(teams[62-i].abbreviations[2],buf1);
  end;
  // ml clubs, 7th name slot
  image_file.Seek(OFS_ML_TEAM_NAME_7, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Read(buf,ML_TEAM_NAME_LEN_7[31-i]);
    CStrCopy(ml_teams[31-i].names[6],buf);
  end;
  // ml clubs, 8th name slot
  image_file.Seek(OFS_ML_TEAM_NAME_8, soBeginning);
  for i := 0 to 31 do
  begin
    if i = 30 then
    begin
      image_file.Read(buf1, 4);
      buf1[4] := AnsiChar(0);
      CStrCopy(buf, buf1);
      image_file.Seek(OFS_ML_TEAM_NAME_8_A, soBeginning);
      image_file.Read(buf1, 4);
      CStrCat(buf, buf1);
    end
    else
    begin
      image_file.Read(buf,ML_TEAM_NAME_LEN_8[31-i]);
    end;
    CStrCopy(ml_teams[31-i].names[7],buf);
  end;
  for i := 0 to 9 do
  begin
    buf[i] := AnsiChar(0);
  end;
  //load strength bars
  //national and all-star
  image_file.Seek(OFS_TEAM_BARS, soBeginning);
  for i := 0 to 62 do
  begin
    image_file.Read(buf,1);
    teams[i].bar_attack := Ord(buf[0]);
    if i = 3 then
    begin
      image_file.Seek(OFS_TEAM_BARS_A, soBeginning);
    end;
    image_file.Read(buf,4);
    teams[i].bar_defence := Ord(buf[0]);
    teams[i].bar_power := Ord(buf[1]);
    teams[i].bar_speed := Ord(buf[2]);
    teams[i].bar_technique := Ord(buf[3]);
  end;
  //ml
  for i := 0 to 31 do
  begin
    image_file.Read(buf,5);
    ml_teams[i].bar_attack := Ord(buf[0]);
    ml_teams[i].bar_defence := Ord(buf[1]);
    ml_teams[i].bar_power := Ord(buf[2]);
    ml_teams[i].bar_speed := Ord(buf[3]);
    ml_teams[i].bar_technique := Ord(buf[4]);
  end;
  //load set-piece takers
  //national and all-star
  image_file.Seek(OFS_KICKER, soBeginning);
  for i := 0 to 62 do
  begin
    image_file.Read(buf,6);
    teams[i].kick_long_fk := Ord(buf[0]);
    teams[i].kick_short_fk := Ord(buf[1]);
    teams[i].kick_right_corner := Ord(buf[2]);
    teams[i].kick_left_corner := Ord(buf[3]);
    teams[i].kick_penalty := Ord(buf[4]);
    teams[i].captain := Ord(buf[5]);
  end;
  //ml
  for i := 0 to 31 do
  begin
    image_file.Read(buf,6);
    ml_teams[i].kick_long_fk := Ord(buf[1]);
    ml_teams[i].kick_short_fk := Ord(buf[0]);
    ml_teams[i].kick_right_corner := Ord(buf[3]);
    ml_teams[i].kick_left_corner := Ord(buf[2]);
    ml_teams[i].kick_penalty := Ord(buf[4]);
    ml_teams[i].captain := Ord(buf[5]);
  end;
  //ml default
  image_file.Read(buf,2);
  image_file.Read(buf,6);
  ml_default.kick_long_fk := Ord(buf[1]);
  ml_default.kick_short_fk := Ord(buf[0]);
  ml_default.kick_right_corner := Ord(buf[3]);
  ml_default.kick_left_corner := Ord(buf[2]);
  ml_default.kick_penalty := Ord(buf[4]);
  ml_default.captain := Ord(buf[5]);
  //load formations 
  //national and all-star
  buf[30] := AnsiChar(0);
  image_file.Seek(OFS_FORMATIONS, soBeginning);
  for i := 0 to 62 do
  begin
    if i = 32 then
    begin
      image_file.Read(buf1,20);
      for j := 0 to 19 do
      begin
        buf[j] := buf1[j];
      end;
      image_file.Seek(OFS_FORMATIONS_A, soBeginning);
      image_file.Read(buf1, 10);
      for j := 0 to 9 do
      begin
        buf[j+20] := buf1[j];
      end;
      buf[30] := AnsiChar(0);
    end
    else
    begin
      image_file.Read(buf,30);
    end;
    CStrCopy(teams[i].raw_formation, buf);
  end;
  //ml
  for i := 0 to 31 do
  begin
    image_file.Read(buf,30);
    CStrCopy(ml_teams[i].raw_formation, buf);
  end;
  //ml default
  image_file.Read(buf,2);
  image_file.Read(buf,30);
  buf[30] := AnsiChar(0);
  CStrCopy(ml_default.raw_formation, buf);
  //load the squad-number blob
  //for ml clubs
  image_file.Seek(OFS_SQUAD_NUMBERS_ML, soBeginning);
  image_file.Read(ml_default.raw_numbers,23);
  image_file.Read(buf,1);
  for i := 0 to TEAMS_ML - 1 do
  begin
    image_file.Read(ml_teams[i].raw_numbers,23);
  end;
  //for national and all-star teams
  image_file.Seek(OFS_SQUAD_NUMBERS_NATIONAL, soBeginning);
  for i := 0 to 63 do
  begin
    image_file.Read(teams[i].squad_numbers,16);
  end;
  //load flags
  //shape, 1st copy (all five copies agree)
  //national and all-star
  image_file.Seek(OFS_FLAG_SHAPE_COPY_1, soBeginning);
  for i := 0 to 62 do
  begin
    image_file.Read(teams[i].flag_shape,1);
  end;
  //ml
  for i := 0 to TEAMS_ML - 1 do
  begin
    image_file.Read(ml_teams[i].flag_shape,1);
  end;
  //colours  
  //national and all-star 
  image_file.Seek(OFS_FLAG_COLOURS, soBeginning);
  for i := 0 to 55 do
  begin
    case i of
      13:
      begin
        image_file.Read(teams[i].flag_colours,26);
        image_file.Seek(OFS_FLAG_COLOURS_A, soBeginning);
        image_file.Read(colour_buf,6);
        for j := 0 to 2 do
        begin
          teams[i].flag_colours[j+13] := colour_buf[j];
        end;
      end;
      // the new national sides are elsewhere
      36, 39, 47:
        ;
      // the retired national sides -- northern ireland, jamaica, uae -- sit in between
      1, 40, 52:
      begin
        image_file.Seek(32, soCurrent);
        // PORTE A MAO (rota 1): o ramo seguinte foi DUPLICADO aqui porque o
        // `case` do Pascal nao cai para o proximo. Ver wte/re/recusas.md.
        image_file.Read(teams[i].flag_colours,32);
      end;
    else
      begin
        image_file.Read(teams[i].flag_colours,32);
      end;
    end;
  end;
  image_file.Seek(64, soCurrent);
  for i := 0 to 4 do
  begin
    image_file.Read(ml_teams[i].flag_colours,32);
  end;
  image_file.Read(ml_teams[10].flag_colours,32);
  for i := 0 to 2 do
  begin
    image_file.Read(ml_teams[i+7].flag_colours,32);
  end;
  for i := 0 to 1 do
  begin
    image_file.Read(ml_teams[i+11].flag_colours,32);
  end;
  image_file.Read(ml_teams[15].flag_colours,32);
  for i := 0 to 3 do
  begin
    image_file.Read(ml_teams[i+18].flag_colours,32);
  end;
  image_file.Seek(32, soCurrent);
  image_file.Read(ml_teams[14].flag_colours,32);
  image_file.Read(ml_teams[24].flag_colours,32);
  image_file.Read(ml_teams[25].flag_colours,32);
  //bayern munich
  image_file.Read(ml_teams[26].flag_colours,26);
  image_file.Seek(OFS_FLAG_COLOURS_B, soBeginning);
  image_file.Read(colour_buf,6);
  for j := 0 to 2 do
  begin
    ml_teams[26].flag_colours[j+13] := colour_buf[j];
  end;
  image_file.Read(ml_teams[27].flag_colours,32);
  for i := 0 to 1 do
  begin
    image_file.Read(ml_teams[i+16].flag_colours,32);
  end;
  image_file.Seek(64, soCurrent);
  image_file.Read(ml_teams[13].flag_colours,32);
  image_file.Seek(288, soCurrent);
  image_file.Read(teams[39].flag_colours,32);
  image_file.Seek(64, soCurrent);
  image_file.Read(teams[47].flag_colours,32);
  image_file.Read(ml_teams[6].flag_colours,32);
  image_file.Read(ml_teams[23].flag_colours,32);
  image_file.Read(ml_teams[28].flag_colours,32);
  image_file.Read(ml_teams[29].flag_colours,32);
  image_file.Read(ml_teams[30].flag_colours,32);
  image_file.Read(ml_teams[31].flag_colours,32);
  //senegal
  image_file.Seek(OFS_FLAG_COLOURS_SENEGAL, soBeginning);
  image_file.Read(teams[36].flag_colours,32);
  //kit preview !!!!!!!!!!!!!!!!
  image_file.Seek(OFS_KIT_PREVIEW, soBeginning);
  for i := 0 to 62 do
  begin
    case i of
      30:
      begin
        image_file.Read(teams[i].home_kit,32);
        image_file.Read(teams[i].away_kit,32);
        image_file.Seek(OFS_KIT_PREVIEW_A, soBeginning);
      end;
    else
      begin
        image_file.Read(teams[i].home_kit,32);
        image_file.Read(teams[i].away_kit,32);
      end;
    end;
  end;
  //ml
  image_file.Seek(OFS_KIT_PREVIEW_B, soBeginning);
  for i := 0 to TEAMS_ML - 1 do
  begin
    image_file.Read(ml_teams[i].home_kit,32);
    image_file.Read(ml_teams[i].away_kit,32);
  end;
  // players
  //load names
  //national and all-star players
  image_file.Seek(OFS_PLAYER_NAME, soBeginning);
  image_file.Read(buf, 8);
  buf[8] := AnsiChar(0);
  CStrCopy(name_buf,buf);
  image_file.Seek(OFS_PLAYER_NAME+312, soBeginning);
  image_file.Read(buf, 2);
  buf[2] := AnsiChar(0);
  CStrCat(name_buf,buf);
  CStrCopy(players[PLAYERS_NC].name,name_buf);
  for i := 1+PLAYERS_NC to PLAYERS_TOTAL - 1 do
  begin
    case i of
      205+PLAYERS_NC:
      begin
        image_file.Read(buf, 6);
        buf[6] := AnsiChar(0);
        CStrCopy(name_buf,buf);
        image_file.Seek(OFS_PLAYER_NAME_2, soBeginning);
        image_file.Read(buf, 4);
        buf[4] := AnsiChar(0);
        CStrCat(name_buf,buf);
      end;
      410+PLAYERS_NC:
      begin
        image_file.Read(buf, 4);
        buf[4] := AnsiChar(0);
        CStrCopy(name_buf,buf);
        image_file.Seek(OFS_PLAYER_NAME_3, soBeginning);
        image_file.Read(buf, 6);
        buf[6] := AnsiChar(0);
        CStrCat(name_buf,buf);
      end;
      615+PLAYERS_NC:
      begin
        image_file.Read(buf, 2);
        buf[2] := AnsiChar(0);
        CStrCopy(name_buf,buf);
        image_file.Seek(OFS_PLAYER_NAME_4, soBeginning);
        image_file.Read(buf, 8);
        buf[8] := AnsiChar(0);
        CStrCat(name_buf,buf);
      end;
      820+PLAYERS_NC:
      begin
        image_file.Seek(OFS_PLAYER_NAME_5, soBeginning);
        image_file.Read(name_buf, 10);
      end;
      1024+PLAYERS_NC:
      begin
        image_file.Read(buf, 8);
        buf[8] := AnsiChar(0);
        CStrCopy(name_buf,buf);
        image_file.Seek(OFS_PLAYER_NAME_6, soBeginning);
        image_file.Read(buf, 2);
        buf[2] := AnsiChar(0);
        CStrCat(name_buf,buf);
      end;
      1229+PLAYERS_NC:
      begin
        image_file.Read(buf, 6);
        buf[6] := AnsiChar(0);
        CStrCopy(name_buf,buf);
        image_file.Seek(OFS_PLAYER_NAME_7, soBeginning);
        image_file.Read(buf, 4);
        buf[4] := AnsiChar(0);
        CStrCat(name_buf,buf);
      end;
      1434+PLAYERS_NC:
      begin
        image_file.Read(buf, 4);
        buf[4] := AnsiChar(0);
        CStrCopy(name_buf,buf);
        image_file.Seek(OFS_PLAYER_NAME_8, soBeginning);
        image_file.Read(buf, 6);
        buf[6] := AnsiChar(0);
        CStrCat(name_buf,buf);
      end;
    else
      begin
        image_file.Read(name_buf, 10);
      end;
    end;
    name_buf[10] := AnsiChar(0);
    CStrCopy(players[i].name,name_buf);
  end;
  //non-contract ml players
  image_file.Seek(OFS_ML_PLAYER_NAME, soBeginning);
  for i := 0 to PLAYERS_NC - 1 do
  begin
    case i of
      203:
      begin
        image_file.Read(name_buf, 10);
        image_file.Seek(OFS_ML_PLAYER_NAME_2, soBeginning);
      end;
      408:
      begin
        image_file.Read(buf, 8);
        buf[8] := AnsiChar(0);
        CStrCopy(name_buf,buf);
        image_file.Seek(OFS_ML_PLAYER_NAME_3, soBeginning);
        image_file.Read(buf, 2);
        buf[2] := AnsiChar(0);
        CStrCat(name_buf,buf);
      end;
    else
      begin
        image_file.Read(name_buf, 10);
      end;
    end;
    name_buf[10] := AnsiChar(0);
    CStrCopy(players[i].name, name_buf);
  end;
  //load attributes
  //national and all-star
  image_file.Seek(OFS_PLAYER_ATTR, soBeginning);
  for i := PLAYERS_NC to PLAYERS_TOTAL - 1 do
  begin
    case i of
      44+PLAYERS_NC:
      begin
        image_file.Read(buf1, 4);
        image_file.Seek(OFS_PLAYER_ATTR_1, soBeginning);
        image_file.Read(buf, 8);
        for j := 0 to 7 do
        begin
          buf1[j+4] := buf[j];
        end;
      end;
      215+PLAYERS_NC:
      begin
        image_file.Seek(OFS_PLAYER_ATTR_2, soBeginning);
        image_file.Read(buf1, 12);
      end;
      385+PLAYERS_NC:
      begin
        image_file.Read(buf1, 8);
        image_file.Seek(OFS_PLAYER_ATTR_3, soBeginning);
        image_file.Read(buf, 4);
        for j := 0 to 3 do
        begin
          buf1[j+8] := buf[j];
        end;
      end;
      556+PLAYERS_NC:
      begin
        image_file.Read(buf1, 4);
        image_file.Seek(OFS_PLAYER_ATTR_4, soBeginning);
        image_file.Read(buf, 8);
        for j := 0 to 7 do
        begin
          buf1[j+4] := buf[j];
        end;
      end;
      727+PLAYERS_NC:
      begin
        image_file.Seek(OFS_PLAYER_ATTR_5, soBeginning);
        image_file.Read(buf1, 12);
      end;
      897+PLAYERS_NC:
      begin
        image_file.Read(buf1, 8);
        image_file.Seek(OFS_PLAYER_ATTR_6, soBeginning);
        image_file.Read(buf, 4);
        for j := 0 to 3 do
        begin
          buf1[j+8] := buf[j];
        end;
      end;
      1068+PLAYERS_NC:
      begin
        image_file.Read(buf1, 4);
        image_file.Seek(OFS_PLAYER_ATTR_7, soBeginning);
        image_file.Read(buf, 8);
        for j := 0 to 7 do
        begin
          buf1[j+4] := buf[j];
        end;
      end;
      1239+PLAYERS_NC:
      begin
        image_file.Seek(OFS_PLAYER_ATTR_8, soBeginning);
        image_file.Read(buf1, 12);
      end;
      1409+PLAYERS_NC:
      begin
        image_file.Read(buf1, 8);
        image_file.Seek(OFS_PLAYER_ATTR_9, soBeginning);
        image_file.Read(buf, 4);
        for j := 0 to 3 do
        begin
          buf1[j+8] := buf[j];
        end;
      end;
    else
      begin
        image_file.Read(buf1, 12);
      end;
    end;
    for j := 0 to 11 do
    begin
      players[i].raw_attributes[j] := Ord(buf1[j]);
    end;
    players[i].Decode;
  end;
  //non-contract ml players
  image_file.Seek(OFS_ML_PLAYER_ATTR, soBeginning);
  for i := 0 to PLAYERS_NC - 1 do
  begin
    case i of
      148:
      begin
        image_file.Read(buf1, 8);
        image_file.Seek(OFS_ML_PLAYER_ATTR_1, soBeginning);
        image_file.Read(buf, 4);
        for j := 0 to 3 do
        begin
          buf1[j+8] := buf[j];
        end;
      end;
      319:
      begin
        image_file.Read(buf1, 4);
        image_file.Seek(OFS_ML_PLAYER_ATTR_2, soBeginning);
        image_file.Read(buf, 8);
        for j := 0 to 7 do
        begin
          buf1[j+4] := buf[j];
        end;
      end;
    else
      begin
        image_file.Read(buf1, 12);
      end;
    end;
    for j := 0 to 11 do
    begin
      players[i].raw_attributes[j] := Ord(buf1[j]);
    end;
    players[i].Decode;
  end;
  //assign ml links
  //default
  image_file.Seek(OFS_LINK_ML, soBeginning);
  image_file.Read(buf, 46);
  for j := 0 to 45 do
  begin
    ml_default.link[j] := Ord(buf[j]);
  end;
  // all ml clubs
  image_file.Seek(OFS_LINK_ML1, soBeginning);
  for i := 0 to TEAMS_ML - 1 do
  begin
    if i = 6 then
    begin
      image_file.Read(buf, 28);
      for j := 0 to 27 do
      begin
        ml_teams[i].link[j] := Ord(buf[j]);
      end;
      image_file.Seek(OFS_LINK_ML2, soBeginning);
      image_file.Read(buf, 18);
      for j := 0 to 17 do
      begin
        ml_teams[i].link[j+28] := Ord(buf[j]);
      end;
    end
    else
    begin
      image_file.Read(buf, 46);
      for j := 0 to 45 do
      begin
        ml_teams[i].link[j] := Ord(buf[j]);
      end;
    end;
  end;
  //load ml costs
  image_file.Seek(OFS_COST_NATIONAL, soBeginning);
  i := PLAYERS_NC;
  while i < PLAYERS_TOTAL do
  begin
    if i = 1704 then
    begin
      image_file.Seek(2, soCurrent);
      i := 1750;
    end;
    image_file.Read(players[i].cost, 1);
    Inc(i);
  end;
  image_file.Seek(OFS_COST_NC, soBeginning);
  for i := 0 to PLAYERS_NC - 1 do
  begin
    image_file.Read(buf1, 1);
    players[i].cost := Ord(buf1[0]);
  end;
  // all-star name links
  image_file.Seek(2328964, soBeginning);
  image_file.Read(link_euro_allstar, 46);
  image_file.Seek(2329010, soBeginning);
  image_file.Read(link_world_allstar, 46);
  CopyAllStarNames;
  //preset formations
  image_file.Seek(4822152, soBeginning);
  for i := 0 to 15 do
  begin
    image_file.Read(preset_formations[15-i].name, 6);
    preset_formations[15-i].name[6] := AnsiChar(0);
    image_file.Read(buf, 2);
  end;
  image_file.Seek(374188, soBeginning);
  for i := 0 to 15 do
  begin
    image_file.Read(preset_formations[i].roles, 11);
  end;
  image_file.Seek(374780, soBeginning);
  for i := 0 to 15 do
  begin
    image_file.Read(preset_formations[i].x, 10);
    image_file.Read(preset_formations[i].y, 10);
  end;
  image_file.Close;
  Result := true;
  Exit;
end;

function TDatabase.Save(const image: string; const report: TReporter): Boolean;
var
  i: LongInt;
  j: LongInt;
  p: LongInt;
  buf: array[0..49] of AnsiChar;
  buf1: array[0..49] of AnsiChar;
  colour_buf: array[0..15] of Word;
  image_file: TCdImage;
begin
  image_file.Init;
  if not image_file.OpenReadWrite(image) then
  begin
    Reportar(report, 'Error ! Impossible to write into CD image !');
    Result := false;
    Exit;
  end;
  // teams
  //save names
  // kanji batch, ml clubs
  image_file.Seek(OFS_TEAM_NAME_KANJI, soBeginning);
  for i := 0 to 31 do
  begin
    AsciiToKanji(@ml_teams[31-i].kanji_name, @ml_teams[31-i].raw_kanji_name, TEAM_NAME_KANJI_LEN[94-i]);
    image_file.Write(ml_teams[31-i].raw_kanji_name,TEAM_NAME_KANJI_LEN[94-i]*2);
  end;
  for i := 0 to 62 do
  begin
    AsciiToKanji(@teams[62-i].kanji_name, @teams[62-i].raw_kanji_name, TEAM_NAME_KANJI_LEN[62-i]);
    if i = 58 then
    begin
      image_file.Write(teams[62-i].raw_kanji_name,4);
      image_file.Seek(OFS_TEAM_NAME_KANJI_A, soBeginning);
      for j := 0 to 7 do
      begin
        buf[j] := teams[62-i].raw_kanji_name[4+j];
      end;
      image_file.Write(buf,8);
    end
    else
    begin
      image_file.Write(teams[62-i].raw_kanji_name,TEAM_NAME_KANJI_LEN[62-i]*2);
    end;
  end;
  //1st batch - ml
  image_file.Seek(OFS_TEAM_NAME_1, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Write(ml_teams[31-i].names[0], TEAM_NAME_LEN_1[94-i]);
  end;
  //1st batch - national and all-star - jump - yugoslavia (24th)
  for i := 0 to 62 do
  begin
    if i = 40 then
    begin
      image_file.Seek(OFS_TEAM_NAME_1_A, soBeginning);
    end;
    image_file.Write(teams[62-i].names[0], TEAM_NAME_LEN_1[62-i]);
  end;
  //2nd batch - ml
  image_file.Seek(OFS_TEAM_NAME_2, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Write(ml_teams[31-i].names[1],TEAM_NAME_LEN_2[94-i]);
  end;
  //2nd batch - national and all-star 
  for i := 0 to 62 do
  begin
    image_file.Write(teams[62-i].names[1],TEAM_NAME_LEN_2[62-i]);
  end;
  //3rd batch - ml
  image_file.Seek(OFS_TEAM_NAME_3, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Write(ml_teams[31-i].names[2],TEAM_NAME_LEN_3[94-i]);
  end;
  //3rd batch - national and all-star 
  for i := 0 to 62 do
  begin
    image_file.Write(teams[62-i].names[2],TEAM_NAME_LEN_3[62-i]);
  end;
  //4th batch - ml
  image_file.Seek(OFS_TEAM_NAME_4, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Write(ml_teams[31-i].names[3],TEAM_NAME_LEN_4[94-i]);
  end;
  //4th batch - national and all-star 
  for i := 0 to 62 do
  begin
    image_file.Write(teams[62-i].names[3],TEAM_NAME_LEN_4[62-i]);
  end;
  //5th batch - ml
  image_file.Seek(OFS_TEAM_NAME_5, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Write(ml_teams[31-i].names[4],TEAM_NAME_LEN_5[94-i]);
  end;
  //5th batch - national and all-star - jump - france (7th)
  for i := 0 to 62 do
  begin
    if i = 57 then
    begin
      image_file.Write(teams[62-i].names[4], 4);
      image_file.Seek(OFS_TEAM_NAME_5_A, soBeginning);
      for j := 0 to 3 do
      begin
        buf[j] := teams[62-i].names[4][j+4];
      end;
      image_file.Write(buf, 4);
    end
    else
    begin
      image_file.Write(teams[62-i].names[4],TEAM_NAME_LEN_5[62-i]);
    end;
  end;
  //6th batch - ml
  image_file.Seek(OFS_TEAM_NAME_6, soBeginning);
  for i := 0 to 31 do
  begin
    if i = 15 then
    begin
      image_file.Seek(OFS_TEAM_NAME_6_A, soBeginning);
    end;
    image_file.Write(ml_teams[31-i].names[5],TEAM_NAME_LEN_6[94-i]);
  end;
  //6th batch - national and all-star 
  image_file.Seek(OFS_TEAM_NAME_6_B, soBeginning);
  for i := 0 to 62 do
  begin
    image_file.Write(teams[62-i].names[5],TEAM_NAME_LEN_6[62-i]);
  end;
  //mixed case, ml clubs
  image_file.Seek(OFS_TEAM_MIXED_CASE_NAME, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Write(ml_teams[31-i].mixed_case_name,TEAM_MIXED_CASE_NAME_LEN[94-i]);
  end;
  //mixed case, national and all-star 
  for i := 0 to 62 do
  begin
    image_file.Write(teams[62-i].mixed_case_name,TEAM_MIXED_CASE_NAME_LEN[62-i]);
  end;
  //abbrev.1 - ml
  image_file.Seek(OFS_TEAM_ABBREV_1, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Write(ml_teams[31-i].abbreviations[0],4);
  end;
  //abbrev.1 - national and all-star 
  for i := 0 to 62 do
  begin
    image_file.Write(teams[62-i].abbreviations[0],4);
  end;
  //abbrev.2 - ml
  image_file.Seek(OFS_TEAM_ABBREV_2, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Write(ml_teams[31-i].abbreviations[1],4);
  end;
  //abbrev.2 - national and all-star 
  for i := 0 to 62 do
  begin
    image_file.Write(teams[62-i].abbreviations[1],4);
  end;
  //abbrev.3 - ml
  image_file.Seek(OFS_TEAM_ABBREV_3, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Write(ml_teams[31-i].abbreviations[2],4);
  end;
  //abbrev.3 - national and all-star 
  for i := 0 to 62 do
  begin
    image_file.Write(teams[62-i].abbreviations[2],4);
  end;
  // ml clubs, 7th name slot
  image_file.Seek(OFS_ML_TEAM_NAME_7, soBeginning);
  for i := 0 to 31 do
  begin
    image_file.Write(ml_teams[31-i].names[6],ML_TEAM_NAME_LEN_7[31-i]);
  end;
  // ml clubs, 8th name slot
  image_file.Seek(OFS_ML_TEAM_NAME_8, soBeginning);
  for i := 0 to 31 do
  begin
    if i = 30 then
    begin
      image_file.Write(ml_teams[31-i].names[7], 4);
      image_file.Seek(OFS_ML_TEAM_NAME_8_A, soBeginning);
      for j := 0 to 3 do
      begin
        buf[j] := ml_teams[31-i].names[7][j+4];
      end;
      image_file.Write(buf, 4);
    end
    else
    begin
      image_file.Write(ml_teams[31-i].names[7],ML_TEAM_NAME_LEN_8[31-i]);
    end;
  end;
  //save strength bars
  //national and all-star
  image_file.Seek(OFS_TEAM_BARS, soBeginning);
  for i := 0 to 62 do
  begin
    image_file.Write(teams[i].bar_attack,1);
    if i = 3 then
    begin
      image_file.Seek(OFS_TEAM_BARS_A, soBeginning);
    end;
    image_file.Write(teams[i].bar_defence,1);
    image_file.Write(teams[i].bar_power,1);
    image_file.Write(teams[i].bar_speed,1);
    image_file.Write(teams[i].bar_technique,1);
  end;
  //ml
  for i := 0 to 31 do
  begin
    image_file.Write(ml_teams[i].bar_attack,1);
    image_file.Write(ml_teams[i].bar_defence,1);
    image_file.Write(ml_teams[i].bar_power,1);
    image_file.Write(ml_teams[i].bar_speed,1);
    image_file.Write(ml_teams[i].bar_technique,1);
  end;
  //save set-piece takers
  //national and all-star
  image_file.Seek(OFS_KICKER, soBeginning);
  for i := 0 to 62 do
  begin
    image_file.Write(teams[i].kick_long_fk, 1);
    image_file.Write(teams[i].kick_short_fk, 1);
    image_file.Write(teams[i].kick_right_corner, 1);
    image_file.Write(teams[i].kick_left_corner, 1);
    image_file.Write(teams[i].kick_penalty, 1);
    image_file.Write(teams[i].captain, 1);
  end;
  //ml
  for i := 0 to 31 do
  begin
    image_file.Write(ml_teams[i].kick_long_fk, 1);
    image_file.Write(ml_teams[i].kick_short_fk, 1);
    image_file.Write(ml_teams[i].kick_right_corner, 1);
    image_file.Write(ml_teams[i].kick_left_corner, 1);
    image_file.Write(ml_teams[i].kick_penalty, 1);
    image_file.Write(ml_teams[i].captain, 1);
  end;
  //ml default
  image_file.Seek(2, soCurrent);
  image_file.Write(ml_default.kick_long_fk, 1);
  image_file.Write(ml_default.kick_short_fk, 1);
  image_file.Write(ml_default.kick_right_corner, 1);
  image_file.Write(ml_default.kick_left_corner, 1);
  image_file.Write(ml_default.kick_penalty, 1);
  image_file.Write(ml_default.captain, 1);
  //save formations -- mind the jump
  //national and all-star
  image_file.Seek(OFS_FORMATIONS, soBeginning);
  for i := 0 to 62 do
  begin
    if i = 32 then
    begin
      image_file.Write(teams[i].raw_formation,20);
      for j := 0 to 9 do
      begin
        buf[j] := teams[i].raw_formation[j+20];
      end;
      image_file.Seek(OFS_FORMATIONS_A, soBeginning);
      image_file.Write(buf, 10);
    end
    else
    begin
      image_file.Write(teams[i].raw_formation,30);
    end;
  end;
  //ml
  for i := 0 to 31 do
  begin
    image_file.Write(ml_teams[i].raw_formation,30);
  end;
  //ml default
  image_file.Seek(2, soCurrent);
  image_file.Write(ml_default.raw_formation,30);
  //save the squad-number blob
  //for ml clubs
  image_file.Seek(OFS_SQUAD_NUMBERS_ML, soBeginning);
  image_file.Write(ml_default.raw_numbers,23);
  image_file.Seek(1, soCurrent);
  for i := 0 to TEAMS_ML - 1 do
  begin
    image_file.Write(ml_teams[i].raw_numbers,23);
  end;
  //for national and all-star teams
  image_file.Seek(OFS_SQUAD_NUMBERS_NATIONAL, soBeginning);
  for i := 0 to 63 do
  begin
    image_file.Write(teams[i].squad_numbers,16);
  end;
  //kit preview !!!!!!!!!!!!!!!!
  image_file.Seek(OFS_KIT_PREVIEW, soBeginning);
  for i := 0 to 62 do
  begin
    case i of
      30:
      begin
        image_file.Write(teams[i].home_kit,32);
        image_file.Write(teams[i].away_kit,32);
        image_file.Seek(OFS_KIT_PREVIEW_A, soBeginning);
      end;
    else
      begin
        image_file.Write(teams[i].home_kit,32);
        image_file.Write(teams[i].away_kit,32);
      end;
    end;
  end;
  image_file.Seek(OFS_KIT_PREVIEW_B, soBeginning);
  for i := 0 to TEAMS_ML - 1 do
  begin
    image_file.Write(ml_teams[i].home_kit,32);
    image_file.Write(ml_teams[i].away_kit,32);
  end;
  // players
  //save names
  //national and all-star players
  image_file.Seek(OFS_PLAYER_NAME, soBeginning);
  image_file.Write(players[PLAYERS_NC].name, 8);
  image_file.Seek(OFS_PLAYER_NAME+312, soBeginning);
  for j := 0 to 1 do
  begin
    buf[j] := players[PLAYERS_NC].name[j+8];
  end;
  image_file.Write(buf, 2);
  for i := 1+PLAYERS_NC to PLAYERS_TOTAL - 1 do
  begin
    case i of
      205+PLAYERS_NC:
      begin
        image_file.Write(players[i].name, 6);
        image_file.Seek(OFS_PLAYER_NAME_2, soBeginning);
        for j := 0 to 3 do
        begin
          buf[j] := players[i].name[j+6];
        end;
        image_file.Write(buf, 4);
      end;
      410+PLAYERS_NC:
      begin
        image_file.Write(players[i].name, 4);
        image_file.Seek(OFS_PLAYER_NAME_3, soBeginning);
        for j := 0 to 5 do
        begin
          buf[j] := players[i].name[j+4];
        end;
        image_file.Write(buf, 6);
      end;
      615+PLAYERS_NC:
      begin
        image_file.Write(players[i].name, 2);
        image_file.Seek(OFS_PLAYER_NAME_4, soBeginning);
        for j := 0 to 7 do
        begin
          buf[j] := players[i].name[j+2];
        end;
        image_file.Write(buf, 8);
      end;
      820+PLAYERS_NC:
      begin
        image_file.Seek(OFS_PLAYER_NAME_5, soBeginning);
        image_file.Write(players[i].name, 10);
      end;
      1024+PLAYERS_NC:
      begin
        image_file.Write(players[i].name, 8);
        image_file.Seek(OFS_PLAYER_NAME_6, soBeginning);
        for j := 0 to 1 do
        begin
          buf[j] := players[i].name[j+8];
        end;
        image_file.Write(buf, 2);
      end;
      1229+PLAYERS_NC:
      begin
        image_file.Write(players[i].name, 6);
        image_file.Seek(OFS_PLAYER_NAME_7, soBeginning);
        for j := 0 to 3 do
        begin
          buf[j] := players[i].name[j+6];
        end;
        image_file.Write(buf, 4);
      end;
      1434+PLAYERS_NC:
      begin
        image_file.Write(players[i].name, 4);
        image_file.Seek(OFS_PLAYER_NAME_8, soBeginning);
        for j := 0 to 5 do
        begin
          buf[j] := players[i].name[j+4];
        end;
        image_file.Write(buf, 6);
      end;
    else
      begin
        image_file.Write(players[i].name, 10);
      end;
    end;
  end;
  //non-contract ml players
  image_file.Seek(OFS_ML_PLAYER_NAME, soBeginning);
  for i := 0 to PLAYERS_NC - 1 do
  begin
    case i of
      203:
      begin
        image_file.Write(players[i].name, 10);
        image_file.Seek(OFS_ML_PLAYER_NAME_2, soBeginning);
      end;
      408:
      begin
        image_file.Write(players[i].name, 8);
        image_file.Seek(OFS_ML_PLAYER_NAME_3, soBeginning);
        for j := 0 to 1 do
        begin
          buf[j] := players[i].name[j+8];
        end;
        image_file.Write(buf, 2);
      end;
    else
      begin
        image_file.Write(players[i].name, 10);
      end;
    end;
  end;
  //assign ml links
  //default
  image_file.Seek(OFS_LINK_ML, soBeginning);
  image_file.Write(ml_default.link, 46);
  // all ml clubs
  image_file.Seek(OFS_LINK_ML1, soBeginning);
  for i := 0 to TEAMS_ML - 1 do
  begin
    if i = 6 then
    begin
      image_file.Write(ml_teams[i].link, 28);
      image_file.Seek(OFS_LINK_ML2, soBeginning);
      for j := 0 to 17 do
      begin
        buf[j] := AnsiChar(ml_teams[i].link[j+28]);
      end;
      image_file.Write(buf, 18);
    end
    else
    begin
      image_file.Write(ml_teams[i].link, 46);
    end;
  end;
  //save flags: the shape table five times over
  //national and all-star
  image_file.Seek(OFS_FLAG_SHAPE_COPY_1, soBeginning);
  for i := 0 to 62 do
  begin
    image_file.Write(teams[i].flag_shape,1);
  end;
  //ml
  for i := 0 to TEAMS_ML - 1 do
  begin
    image_file.Write(ml_teams[i].flag_shape,1);
  end;
  image_file.Seek(OFS_FLAG_SHAPE_COPY_2, soBeginning);
  for i := 0 to 62 do
  begin
    image_file.Write(teams[i].flag_shape,1);
  end;
  //ml
  for i := 0 to TEAMS_ML - 1 do
  begin
    image_file.Write(ml_teams[i].flag_shape,1);
  end;
  image_file.Seek(OFS_FLAG_SHAPE_COPY_3, soBeginning);
  for i := 0 to 62 do
  begin
    image_file.Write(teams[i].flag_shape,1);
  end;
  //ml
  for i := 0 to TEAMS_ML - 1 do
  begin
    image_file.Write(ml_teams[i].flag_shape,1);
  end;
  image_file.Seek(OFS_FLAG_SHAPE_COPY_4, soBeginning);
  for i := 0 to 62 do
  begin
    image_file.Write(teams[i].flag_shape,1);
  end;
  //ml
  for i := 0 to TEAMS_ML - 1 do
  begin
    image_file.Write(ml_teams[i].flag_shape,1);
  end;
  image_file.Seek(OFS_FLAG_SHAPE_COPY_5, soBeginning);
  for i := 0 to 62 do
  begin
    image_file.Write(teams[i].flag_shape,1);
  end;
  //ml
  for i := 0 to TEAMS_ML - 1 do
  begin
    image_file.Write(ml_teams[i].flag_shape,1);
  end;
  //colours  !!!!!!!!!!!!!!!!
  //national and all-star 
  image_file.Seek(OFS_FLAG_COLOURS, soBeginning);
  for i := 0 to 55 do
  begin
    case i of
      13:
      begin
        image_file.Write(teams[i].flag_colours,26);
        image_file.Seek(OFS_FLAG_COLOURS_A, soBeginning);
        for j := 0 to 2 do
        begin
          colour_buf[j] := teams[i].flag_colours[j+13];
        end;
        image_file.Write(colour_buf,6);
      end;
      // the new national sides are elsewhere
      36, 39, 47:
        ;
      // the retired national sides -- northern ireland, jamaica, uae -- sit in between
      1, 40, 52:
      begin
        image_file.Seek(32, soCurrent);
        // PORTE A MAO (rota 1): o ramo seguinte foi DUPLICADO aqui porque o
        // `case` do Pascal nao cai para o proximo. Ver wte/re/recusas.md.
        image_file.Write(teams[i].flag_colours,32);
      end;
    else
      begin
        image_file.Write(teams[i].flag_colours,32);
      end;
    end;
  end;
  image_file.Seek(64, soCurrent);
  for i := 0 to 4 do
  begin
    image_file.Write(ml_teams[i].flag_colours,32);
  end;
  image_file.Write(ml_teams[10].flag_colours,32);
  for i := 0 to 2 do
  begin
    image_file.Write(ml_teams[i+7].flag_colours,32);
  end;
  for i := 0 to 1 do
  begin
    image_file.Write(ml_teams[i+11].flag_colours,32);
  end;
  image_file.Write(ml_teams[15].flag_colours,32);
  for i := 0 to 3 do
  begin
    image_file.Write(ml_teams[i+18].flag_colours,32);
  end;
  image_file.Seek(32, soCurrent);
  image_file.Write(ml_teams[14].flag_colours,32);
  image_file.Write(ml_teams[24].flag_colours,32);
  image_file.Write(ml_teams[25].flag_colours,32);
  //bayern munich
  image_file.Write(ml_teams[26].flag_colours,26);
  image_file.Seek(OFS_FLAG_COLOURS_B, soBeginning);
  for j := 0 to 2 do
  begin
    colour_buf[j] := ml_teams[26].flag_colours[j+13];
  end;
  image_file.Write(colour_buf,6);
  image_file.Write(ml_teams[27].flag_colours,32);
  i := 0;
  while i < 2 do
  begin
    image_file.Write(ml_teams[i+16].flag_colours,32);
    Inc(i);
  end;
  image_file.Seek(64, soCurrent);
  image_file.Write(ml_teams[13].flag_colours,32);
  image_file.Seek(288, soCurrent);
  image_file.Write(teams[39].flag_colours,32);
  image_file.Seek(64, soCurrent);
  image_file.Write(teams[47].flag_colours,32);
  image_file.Write(ml_teams[6].flag_colours,32);
  image_file.Write(ml_teams[23].flag_colours,32);
  image_file.Write(ml_teams[28].flag_colours,32);
  image_file.Write(ml_teams[29].flag_colours,32);
  image_file.Write(ml_teams[30].flag_colours,32);
  image_file.Write(ml_teams[31].flag_colours,32);
  //senegal
  image_file.Seek(OFS_FLAG_COLOURS_SENEGAL, soBeginning);
  image_file.Write(teams[36].flag_colours,32);
  //save attributes -- repacked into the raw blob
  //national and all-star
  image_file.Seek(OFS_PLAYER_ATTR, soBeginning);
  for p := PLAYERS_NC to PLAYERS_TOTAL - 1 do
  begin
    if (p >= 1704)  and  (p <= 1749) then
    begin
      if p < 1727 then
      begin
        i := ResolveMlLink(@link_euro_allstar[(p-1704)*2]);
      end
      else
      begin
        i := ResolveMlLink(@link_world_allstar[(p-1727)*2]);
      end;
    end
    else
    begin
      i := p;
    end;
    players[i].Encode;
    case p of
      44+PLAYERS_NC:
      begin
        image_file.Write(players[i].raw_attributes, 4);
        image_file.Seek(OFS_PLAYER_ATTR_1, soBeginning);
        for j := 0 to 7 do
        begin
          buf1[j] := AnsiChar(players[i].raw_attributes[j+4]);
        end;
        image_file.Write(buf1, 8);
      end;
      215+PLAYERS_NC:
      begin
        image_file.Seek(OFS_PLAYER_ATTR_2, soBeginning);
        image_file.Write(players[i].raw_attributes, 12);
      end;
      385+PLAYERS_NC:
      begin
        image_file.Write(players[i].raw_attributes, 8);
        image_file.Seek(OFS_PLAYER_ATTR_3, soBeginning);
        for j := 0 to 3 do
        begin
          buf1[j] := AnsiChar(players[i].raw_attributes[j+8]);
        end;
        image_file.Write(buf1, 4);
      end;
      556+PLAYERS_NC:
      begin
        image_file.Write(players[i].raw_attributes, 4);
        image_file.Seek(OFS_PLAYER_ATTR_4, soBeginning);
        for j := 0 to 7 do
        begin
          buf1[j] := AnsiChar(players[i].raw_attributes[j+4]);
        end;
        image_file.Write(buf1, 8);
      end;
      727+PLAYERS_NC:
      begin
        image_file.Seek(OFS_PLAYER_ATTR_5, soBeginning);
        image_file.Write(players[i].raw_attributes, 12);
      end;
      897+PLAYERS_NC:
      begin
        image_file.Write(players[i].raw_attributes, 8);
        image_file.Seek(OFS_PLAYER_ATTR_6, soBeginning);
        for j := 0 to 3 do
        begin
          buf1[j] := AnsiChar(players[i].raw_attributes[j+8]);
        end;
        image_file.Write(buf1, 4);
      end;
      1068+PLAYERS_NC:
      begin
        image_file.Write(players[i].raw_attributes, 4);
        image_file.Seek(OFS_PLAYER_ATTR_7, soBeginning);
        for j := 0 to 7 do
        begin
          buf1[j] := AnsiChar(players[i].raw_attributes[j+4]);
        end;
        image_file.Write(buf1, 8);
      end;
      1239+PLAYERS_NC:
      begin
        image_file.Seek(OFS_PLAYER_ATTR_8, soBeginning);
        image_file.Write(players[i].raw_attributes, 12);
      end;
      1409+PLAYERS_NC:
      begin
        image_file.Write(players[i].raw_attributes, 8);
        image_file.Seek(OFS_PLAYER_ATTR_9, soBeginning);
        for j := 0 to 3 do
        begin
          buf1[j] := AnsiChar(players[i].raw_attributes[j+8]);
        end;
        image_file.Write(buf1, 4);
      end;
    else
      begin
        image_file.Write(players[i].raw_attributes, 12);
      end;
    end;
  end;
  //non-contract ml players
  image_file.Seek(OFS_ML_PLAYER_ATTR, soBeginning);
  for i := 0 to PLAYERS_NC - 1 do
  begin
    players[i].Encode;
    case i of
      148:
      begin
        image_file.Write(players[i].raw_attributes, 8);
        image_file.Seek(OFS_ML_PLAYER_ATTR_1, soBeginning);
        for j := 0 to 3 do
        begin
          buf1[j] := AnsiChar(players[i].raw_attributes[j+8]);
        end;
        image_file.Write(buf1, 4);
      end;
      319:
      begin
        image_file.Write(players[i].raw_attributes, 4);
        image_file.Seek(OFS_ML_PLAYER_ATTR_2, soBeginning);
        for j := 0 to 7 do
        begin
          buf1[j] := AnsiChar(players[i].raw_attributes[j+4]);
        end;
        image_file.Write(buf1, 8);
      end;
    else
      begin
        image_file.Write(players[i].raw_attributes, 12);
      end;
    end;
  end;
  //save ml costs
  image_file.Seek(OFS_COST_NATIONAL, soBeginning);
  buf[1] := AnsiChar(0);
  buf[0] := buf[1];
  i := PLAYERS_NC;
  while i < PLAYERS_TOTAL do
  begin
    if i=1704 then
    begin
      image_file.Write(buf,2);
      i := 1750;
    end;
    image_file.Write(players[i].cost, 1);
    Inc(i);
  end;
  image_file.Seek(OFS_COST_NC, soBeginning);
  for i := 0 to PLAYERS_NC - 1 do
  begin
    image_file.Write(players[i].cost, 1);
  end;
  //all-star links
  image_file.Seek(2328964, soBeginning);
  image_file.Write(link_euro_allstar, 46);
  image_file.Seek(2329010, soBeginning);
  image_file.Write(link_world_allstar, 46);
  //preset formations
  image_file.Seek(4822152, soBeginning);
  buf[2] := AnsiChar(0);
  buf[1] := buf[2];
  buf[0] := buf[1];
  for i := 0 to 15 do
  begin
    image_file.Write(preset_formations[15-i].name, 6);
    image_file.Write(buf, 2);
  end;
  image_file.Seek(374188, soBeginning);
  for i := 0 to 15 do
  begin
    image_file.Write(preset_formations[i].roles, 11);
  end;
  image_file.Seek(374780, soBeginning);
  for i := 0 to 15 do
  begin
    image_file.Write(preset_formations[i].x, 10);
    image_file.Write(preset_formations[i].y, 10);
  end;
  image_file.Close;
  WriteUrlSidecar(image);
  Reportar(report, 'CD image edited !');
  Result := true;
  Exit;
end;

function ComputePlayerCost(const db: TDatabase; i: LongInt): LongInt;
var
  k: Double;
begin
  //{"GK", "CB", "SB", "DH", "SH", "OH", "CF", "WG"};
  k := 16;
  case db.players[i].position of
    //goalkeeper
    0:
    begin
      k := k + ((db.players[i].acceleration-15) * 0.45);
      k := k + ((db.players[i].speed-15) * 0.45);
      k := k + ((db.players[i].aggression-12) * 0.05);
      k := k + ((db.players[i].reflexes-16) * 0.7);
      k := k + ((db.players[i].height-180) * 0.07);
      k := k + (db.players[i].out_of_position * 0.5);
      k := k + ((db.players[i].strength-16) * 0.7);
      k := k + ((db.players[i].stamina-14) * 0.15);
      k := k + ((db.players[i].technique-13) * 0.15);
      k := k + ((db.players[i].attack-12) * 0.05);
      k := k + ((db.players[i].defence-16) * 0.8);
      k := k + ((db.players[i].dribbling-14) * 0.08);
      k := k + ((db.players[i].swerve-14) * 0.08);
      k := k + ((db.players[i].passing-14) * 0.08);
      k := k + ((db.players[i].shot_power-15) * 0.3);
      k := k + ((db.players[i].shot_accuracy-14) * 0.2);
      k := k + ((db.players[i].jump-15) * 0.8);
      k := k + ((db.players[i].heading-13) * 0.15);
      // i 9!!
      if db.players[i].acceleration = 19 then
      begin
        k := k + (0.4);
      end;
      if db.players[i].speed = 19 then
      begin
        k := k + (0.4);
      end;
      if db.players[i].reflexes = 19 then
      begin
        k := k + (0.8);
      end;
      if db.players[i].strength = 19 then
      begin
        k := k + (0.8);
      end;
      if db.players[i].stamina = 19 then
      begin
        k := k + (0.3);
      end;
      if db.players[i].technique = 19 then
      begin
        k := k + (0.4);
      end;
      if db.players[i].attack = 19 then
      begin
        k := k + (0.2);
      end;
      if db.players[i].defence = 19 then
      begin
        k := k + (0.9);
      end;
      if db.players[i].swerve = 19 then
      begin
        k := k + (0.15);
      end;
      if db.players[i].passing = 19 then
      begin
        k := k + (0.25);
      end;
      if db.players[i].shot_power = 19 then
      begin
        k := k + (0.2);
      end;
      if db.players[i].shot_accuracy = 19 then
      begin
        k := k + (0.2);
      end;
      if db.players[i].jump = 19 then
      begin
        k := k + (0.8);
      end;
      if db.players[i].heading = 19 then
      begin
        k := k + (0.2);
      end;
    end;
    //defender
    1, 2:
    begin
      k := k + (1);
      if db.players[i].foot = 2 then
      begin
        k := k + (1);
      end;
      k := k + ((db.players[i].acceleration-16) * 0.55);
      k := k + ((db.players[i].speed-16) * 0.55);
      k := k + ((db.players[i].aggression-13) * 0.2);
      k := k + ((db.players[i].reflexes-15) * 0.35);
      k := k + ((db.players[i].height-170) * 0.045);
      k := k + (db.players[i].out_of_position * 1);
      k := k + ((db.players[i].strength-16) * 0.6);
      k := k + ((db.players[i].stamina-16) * 0.4);
      k := k + ((db.players[i].technique-15) * 0.4);
      k := k + ((db.players[i].attack-14) * 0.3);
      k := k + ((db.players[i].defence-16) * 0.85);
      k := k + ((db.players[i].dribbling-14) * 0.25);
      k := k + ((db.players[i].swerve-14) * 0.25);
      k := k + ((db.players[i].passing-15) * 0.35);
      k := k + ((db.players[i].shot_power-16) * 0.35);
      k := k + ((db.players[i].shot_accuracy-14) * 0.3);
      k := k + ((db.players[i].jump-16) * 0.5);
      k := k + ((db.players[i].heading-15) * 0.5);
      // i 9!!
      if db.players[i].acceleration = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].speed = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].reflexes = 19 then
      begin
        k := k + (0.35);
      end;
      if db.players[i].aggression = 19 then
      begin
        k := k + (0.25);
      end;
      if db.players[i].strength = 19 then
      begin
        k := k + (0.8);
      end;
      if db.players[i].stamina = 19 then
      begin
        k := k + (0.45);
      end;
      if db.players[i].technique = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].attack = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].defence = 19 then
      begin
        k := k + (0.9);
      end;
      if db.players[i].dribbling = 19 then
      begin
        k := k + (0.4);
      end;
      if db.players[i].swerve = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].passing = 19 then
      begin
        k := k + (0.4);
      end;
      if db.players[i].shot_power = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].shot_accuracy = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].jump = 19 then
      begin
        k := k + (0.7);
      end;
      if db.players[i].heading = 19 then
      begin
        k := k + (0.7);
      end;
    end;
    //midfielder
    3, 4, 5:
    begin
      k := k + (3);
      if db.players[i].foot = 2 then
      begin
        k := k + (1.5);
      end;
      k := k + ((db.players[i].acceleration-16) * 0.4);
      k := k + ((db.players[i].speed-16) * 0.4);
      k := k + ((db.players[i].aggression-12) * 0.1);
      k := k + ((db.players[i].reflexes-14) * 0.3);
      k := k + ((db.players[i].height-170) * 0.04);
      k := k + (db.players[i].out_of_position * 1);
      k := k + ((db.players[i].strength-16) * 0.3);
      k := k + ((db.players[i].stamina-16) * 0.45);
      k := k + ((db.players[i].technique-16) * 0.6);
      k := k + ((db.players[i].attack-15) * 0.4);
      k := k + ((db.players[i].defence-15) * 0.3);
      k := k + ((db.players[i].dribbling-14) * 0.4);
      k := k + ((db.players[i].swerve-14) * 0.5);
      k := k + ((db.players[i].passing-16) * 0.6);
      k := k + ((db.players[i].shot_power-16) * 0.5);
      k := k + ((db.players[i].shot_accuracy-16) * 0.6);
      k := k + ((db.players[i].jump-16) * 0.5);
      k := k + ((db.players[i].heading-15) * 0.55);
      // i 9!!
      if db.players[i].acceleration = 19 then
      begin
        k := k + (0.4);
      end;
      if db.players[i].speed = 19 then
      begin
        k := k + (0.4);
      end;
      if db.players[i].reflexes = 19 then
      begin
        k := k + (0.3);
      end;
      if db.players[i].aggression = 19 then
      begin
        k := k + (0.2);
      end;
      if db.players[i].strength = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].stamina = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].technique = 19 then
      begin
        k := k + (0.8);
      end;
      if db.players[i].attack = 19 then
      begin
        k := k + (0.7);
      end;
      if db.players[i].defence = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].dribbling = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].swerve = 19 then
      begin
        k := k + (0.8);
      end;
      if db.players[i].passing = 19 then
      begin
        k := k + (0.7);
      end;
      if db.players[i].shot_power = 19 then
      begin
        k := k + (0.7);
      end;
      if db.players[i].shot_accuracy = 19 then
      begin
        k := k + (0.8);
      end;
      if db.players[i].jump = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].heading = 19 then
      begin
        k := k + (0.6);
      end;
    end;
    //forward
    6, 7:
    begin
      k := k + (7);
      if db.players[i].foot = 2 then
      begin
        k := k + (2);
      end;
      k := k + ((db.players[i].acceleration-16) * 0.6);
      k := k + ((db.players[i].speed-16) * 0.6);
      k := k + ((db.players[i].aggression-14) * 0.4);
      k := k + ((db.players[i].reflexes-16) * 0.4);
      k := k + ((db.players[i].height-170) * 0.04);
      k := k + (db.players[i].out_of_position * 1.5);
      k := k + ((db.players[i].strength-16) * 0.45);
      k := k + ((db.players[i].stamina-16) * 0.45);
      k := k + ((db.players[i].technique-16) * 0.9);
      k := k + ((db.players[i].attack-16) * 0.9);
      k := k + ((db.players[i].defence-13) * 0.3);
      k := k + ((db.players[i].dribbling-16) * 0.8);
      k := k + ((db.players[i].swerve-16) * 0.8);
      k := k + ((db.players[i].passing-16) * 0.7);
      k := k + ((db.players[i].shot_power-16) * 0.9);
      k := k + ((db.players[i].shot_accuracy-16) * 0.9);
      k := k + ((db.players[i].jump-16) * 0.6);
      k := k + ((db.players[i].heading-16) * 0.7);
      // i 9!!
      if db.players[i].acceleration = 19 then
      begin
        k := k + (0.6);
      end;
      if db.players[i].speed = 19 then
      begin
        k := k + (0.6);
      end;
      if db.players[i].reflexes = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].aggression = 19 then
      begin
        k := k + (0.4);
      end;
      if db.players[i].strength = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].stamina = 19 then
      begin
        k := k + (0.5);
      end;
      if db.players[i].technique = 19 then
      begin
        k := k + (0.9);
      end;
      if db.players[i].attack = 19 then
      begin
        k := k + (0.9);
      end;
      if db.players[i].defence = 19 then
      begin
        k := k + (0.3);
      end;
      if db.players[i].dribbling = 19 then
      begin
        k := k + (0.9);
      end;
      if db.players[i].swerve = 19 then
      begin
        k := k + (0.9);
      end;
      if db.players[i].passing = 19 then
      begin
        k := k + (0.9);
      end;
      if db.players[i].shot_power = 19 then
      begin
        k := k + (0.9);
      end;
      if db.players[i].shot_accuracy = 19 then
      begin
        k := k + (0.9);
      end;
      if db.players[i].jump = 19 then
      begin
        k := k + (0.7);
      end;
      if db.players[i].heading = 19 then
      begin
        k := k + (0.8);
      end;
    end;
  end;
  if k<1 then
  begin
    k := 1;
  end;
  Result := Ceil(k);
  Exit;
end;

end.
