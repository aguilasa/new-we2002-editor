{ Despeja, em texto estavel e diffavel, todo o estado que a camada de dados
  gerada carrega de uma imagem. Irmao em Pascal do `dump_estado.cpp`.

  Produto da WTE-TASK-20 -- o aceite da fase 3, e o primeiro momento em que o
  projeto afirma algo verificado sobre dados.

  Os dois lados escrevem o MESMO formato e o criterio e `diff` vazio: aqui e
  leitura pura, nao ha comportamento indefinido para preservar, entao zero
  divergencia e o unico resultado aceitavel. (O golden test de imagem do
  newWe2002 aceita uma faixa conhecida de 16 bytes; este nao aceita nada.)

  O par ser bilingue e o ponto, e e a mesma razao dos dois `test_offsets.*`: o
  `fpc` le o Pascal gerado e o `g++` le o C++ original. Dois dumpers na mesma
  linguagem esconderiam erro de leitura de literal -- ele apareceria igual dos
  dois lados.

    dump_estado_pas <imagem.bin>

  Quem compila, roda e compara e o `wte/tools/compare_dumps.py`, alcancado por
  `make -C wte test`. Sem `fpc` ou sem `g++` ele PULA e diz o que deixou de
  medir, em vez de passar em silencio. }

program dump_estado;

{$mode objfpc}{$H+}

uses
  SysUtils,
  we2002_types, we2002_team, we2002_player, we2002_database;

{ --------------------------------------------------------------- formato ---

  `<n>:<hex>` -- n e o tamanho declarado do vetor, e o hex vai ate o ultimo
  byte nao-zero. Tudo depois disso e zero por definicao, entao a forma e SEM
  PERDA e nao gasta 500 caracteres por URL vazia.

  Hex minusculo, decimal com sinal, uma chave por linha, LF. Cada uma dessas
  escolhas tem de valer nos dois lados: divergencia de formatacao viraria
  divergencia de dado no diff, que e o pior tipo de falso positivo. }

const
  DIG: array[0..15] of Char = '0123456789abcdef';

function HexTrim(const dados; n: SizeInt): string;
var
  p: PByte;
  fim, i: SizeInt;
begin
  p := @dados;
  fim := n;
  while (fim > 0) and (p[fim - 1] = 0) do
    Dec(fim);
  Result := IntToStr(n) + ':';
  SetLength(Result, Length(Result) + 2 * fim);
  for i := 0 to fim - 1 do
  begin
    Result[Length(Result) - 2 * (fim - i) + 1] := DIG[p[i] shr 4];
    Result[Length(Result) - 2 * (fim - i) + 2] := DIG[p[i] and 15];
  end;
end;

{ Vetor de ShortInt. O `char` do C++ no x86 e COM sinal, e o lado C++ faz o
  cast explicito; aqui o tipo ja e com sinal. Os dois tem de imprimir -1, nao
  255 -- foi exatamente esse o defeito da CORR-WTE-043. }
function CsvSigned(const dados; n: SizeInt): string;
var
  p: PShortInt;
  i: SizeInt;
begin
  p := @dados;
  Result := '';
  for i := 0 to n - 1 do
  begin
    if i > 0 then
      Result := Result + ',';
    Result := Result + IntToStr(p[i]);
  end;
end;

function CsvUnsigned(const dados; n: SizeInt): string;
var
  p: PByte;
  i: SizeInt;
begin
  p := @dados;
  Result := '';
  for i := 0 to n - 1 do
  begin
    if i > 0 then
      Result := Result + ',';
    Result := Result + IntToStr(p[i]);
  end;
end;

function CsvU16(const dados; n: SizeInt): string;
var
  p: PWord;
  i: SizeInt;
begin
  p := @dados;
  Result := '';
  for i := 0 to n - 1 do
  begin
    if i > 0 then
      Result := Result + ',';
    Result := Result + IntToStr(p[i]);
  end;
end;

procedure Linha(const chave, valor: string);
begin
  WriteLn(chave, ' = ', valor);
end;

procedure LinhaInt(const chave: string; v: LongInt);
begin
  Linha(chave, IntToStr(v));
end;

{ -------------------------------------------------------------- despejos --- }

procedure DespejaJogador(i: LongInt; const p: TPlayer);
var
  k: string;
begin
  k := 'players[' + IntToStr(i) + '].';
  Linha(k + 'url', HexTrim(p.url, SizeOf(p.url)));
  Linha(k + 'name', HexTrim(p.name, SizeOf(p.name)));
  LinhaInt(k + 'position', p.position);
  LinhaInt(k + 'skin_colour', p.skin_colour);
  LinhaInt(k + 'hair_style', p.hair_style);
  LinhaInt(k + 'hair_colour', p.hair_colour);
  LinhaInt(k + 'beard_style', p.beard_style);
  LinhaInt(k + 'beard_colour', p.beard_colour);
  LinhaInt(k + 'height', p.height);
  LinhaInt(k + 'build', p.build);
  LinhaInt(k + 'age', p.age);
  LinhaInt(k + 'boots', p.boots);
  LinhaInt(k + 'foot', p.foot);
  LinhaInt(k + 'attack', p.attack);
  LinhaInt(k + 'defence', p.defence);
  LinhaInt(k + 'strength', p.strength);
  LinhaInt(k + 'stamina', p.stamina);
  LinhaInt(k + 'speed', p.speed);
  LinhaInt(k + 'acceleration', p.acceleration);
  LinhaInt(k + 'passing', p.passing);
  LinhaInt(k + 'shot_power', p.shot_power);
  LinhaInt(k + 'shot_accuracy', p.shot_accuracy);
  LinhaInt(k + 'jump', p.jump);
  LinhaInt(k + 'heading', p.heading);
  LinhaInt(k + 'technique', p.technique);
  LinhaInt(k + 'dribbling', p.dribbling);
  LinhaInt(k + 'swerve', p.swerve);
  LinhaInt(k + 'aggression', p.aggression);
  LinhaInt(k + 'reflexes', p.reflexes);
  LinhaInt(k + 'out_of_position', p.out_of_position);
  LinhaInt(k + 'number', p.number);
  LinhaInt(k + 'cost', p.cost);
  Linha(k + 'raw_attributes', CsvSigned(p.raw_attributes, 12));
end;

{ Team e MlTeam nao tem tipo-base comum no Pascal gerado (o C++ tambem nao --
  sao duas structs irmas), entao os comuns saem em duas copias em vez de um
  generico. A ORDEM das linhas e o que faz o `diff` valer alguma coisa: se
  divergir de `DespejaComuns` do lado C++, todo time vira divergencia. }
procedure DespejaTime(i: LongInt; const t: TTeam);
var
  k, ns, rs: string;
  j: LongInt;
begin
  k := 'teams[' + IntToStr(i) + '].';
  for j := 0 to 5 do
    Linha(k + 'names[' + IntToStr(j) + ']', HexTrim(t.names[j], 20));
  Linha(k + 'mixed_case_name', HexTrim(t.mixed_case_name, 20));
  for j := 0 to 2 do
    Linha(k + 'abbreviations[' + IntToStr(j) + ']',
          HexTrim(t.abbreviations[j], 4));
  Linha(k + 'kanji_name', HexTrim(t.kanji_name, 20));
  Linha(k + 'raw_kanji_name', HexTrim(t.raw_kanji_name, 40));
  LinhaInt(k + 'bar_attack', t.bar_attack);
  LinhaInt(k + 'bar_defence', t.bar_defence);
  LinhaInt(k + 'bar_power', t.bar_power);
  LinhaInt(k + 'bar_speed', t.bar_speed);
  LinhaInt(k + 'bar_technique', t.bar_technique);
  LinhaInt(k + 'kick_long_fk', t.kick_long_fk);
  LinhaInt(k + 'kick_short_fk', t.kick_short_fk);
  LinhaInt(k + 'kick_left_corner', t.kick_left_corner);
  LinhaInt(k + 'kick_right_corner', t.kick_right_corner);
  LinhaInt(k + 'kick_penalty', t.kick_penalty);
  LinhaInt(k + 'captain', t.captain);
  Linha(k + 'raw_formation', HexTrim(t.raw_formation, 31));
  Linha(k + 'slot_role', CsvSigned(t.slot_role, 10));
  Linha(k + 'slot_x', CsvSigned(t.slot_x, 10));
  Linha(k + 'slot_y', CsvSigned(t.slot_y, 10));
  LinhaInt(k + 'flag_shape', t.flag_shape);
  Linha(k + 'flag_colours', CsvU16(t.flag_colours, 16));
  Linha(k + 'home_kit', CsvU16(t.home_kit, 16));
  Linha(k + 'away_kit', CsvU16(t.away_kit, 16));
  Linha(k + 'raw_strategy', CsvSigned(t.raw_strategy, 4));

  { Os 23 numeros DESEMPACOTADOS mais as quatro palavras cruas. As duas formas
    de proposito: o Pascal nao tem o bitfield do C++, tem um layout escrito a
    mao (tipos.md, decisao 2), e despejar so o valor cru deixaria um erro de
    deslocamento passar. Isto e a conferencia do bitfield contra imagem real
    que a fase 3 pede. }
  ns := '';
  for j := 0 to 22 do
  begin
    if j > 0 then
      ns := ns + ',';
    ns := ns + IntToStr(SquadNumberAt(t.squad_numbers, j));
  end;
  Linha(k + 'squad_numbers', ns);
  rs := '';
  for j := 0 to 3 do
  begin
    if j > 0 then
      rs := rs + ',';
    rs := rs + IntToStr(t.squad_numbers.groups[j]);
  end;
  Linha(k + 'squad_numbers.raw', rs);
end;

procedure DespejaMl(const k: string; const t: TMlTeam);
var
  j: LongInt;
begin
  for j := 0 to 7 do
    Linha(k + 'names[' + IntToStr(j) + ']', HexTrim(t.names[j], 20));
  Linha(k + 'mixed_case_name', HexTrim(t.mixed_case_name, 20));
  for j := 0 to 2 do
    Linha(k + 'abbreviations[' + IntToStr(j) + ']',
          HexTrim(t.abbreviations[j], 4));
  Linha(k + 'kanji_name', HexTrim(t.kanji_name, 20));
  Linha(k + 'raw_kanji_name', HexTrim(t.raw_kanji_name, 40));
  LinhaInt(k + 'bar_attack', t.bar_attack);
  LinhaInt(k + 'bar_defence', t.bar_defence);
  LinhaInt(k + 'bar_power', t.bar_power);
  LinhaInt(k + 'bar_speed', t.bar_speed);
  LinhaInt(k + 'bar_technique', t.bar_technique);
  LinhaInt(k + 'kick_long_fk', t.kick_long_fk);
  LinhaInt(k + 'kick_short_fk', t.kick_short_fk);
  LinhaInt(k + 'kick_left_corner', t.kick_left_corner);
  LinhaInt(k + 'kick_right_corner', t.kick_right_corner);
  LinhaInt(k + 'kick_penalty', t.kick_penalty);
  LinhaInt(k + 'captain', t.captain);
  Linha(k + 'raw_formation', HexTrim(t.raw_formation, 31));
  Linha(k + 'slot_role', CsvSigned(t.slot_role, 10));
  Linha(k + 'slot_x', CsvSigned(t.slot_x, 10));
  Linha(k + 'slot_y', CsvSigned(t.slot_y, 10));
  LinhaInt(k + 'flag_shape', t.flag_shape);
  Linha(k + 'flag_colours', CsvU16(t.flag_colours, 16));
  Linha(k + 'home_kit', CsvU16(t.home_kit, 16));
  Linha(k + 'away_kit', CsvU16(t.away_kit, 16));
  Linha(k + 'raw_strategy', CsvSigned(t.raw_strategy, 4));
  Linha(k + 'raw_numbers', CsvSigned(t.raw_numbers, 23));
  Linha(k + 'link', CsvUnsigned(t.link, 46));
end;

procedure DespejaFormacao(i: LongInt; const f: TFormation);
var
  k: string;
begin
  k := 'preset_formations[' + IntToStr(i) + '].';
  Linha(k + 'name', HexTrim(f.name, 7));
  Linha(k + 'roles', CsvSigned(f.roles, 11));
  Linha(k + 'x', CsvSigned(f.x, 10));
  Linha(k + 'y', CsvSigned(f.y, 10));
end;

var
  db: TDatabase;
  i: LongInt;
  imagem: string;
  roundtrip: Boolean;
begin
  { `--roundtrip` e Load+Save sem saida nenhuma: a metade de GRAVACAO do aceite
    da fase 3. Mora aqui, e nao num programa a parte, porque tem de ser
    exatamente o mesmo `TDatabase` que o dump usa -- dois executaveis
    divergiriam no dia em que um fosse recompilado e o outro nao. }
  roundtrip := (ParamCount = 2) and (ParamStr(1) = '--roundtrip');
  if (ParamCount <> 1) and (not roundtrip) then
  begin
    WriteLn(StdErr, 'uso: dump_estado_pas [--roundtrip] <imagem.bin>');
    Halt(2);
  end;
  if roundtrip then
    imagem := ParamStr(2)
  else
    imagem := ParamStr(1);

  db.Init;
  { Reporter nil: a mensagem de tamanho e ruido aqui, e escrever no stdout
    contaminaria o dump. }
  if not db.Load(imagem, nil) then
  begin
    WriteLn(StdErr, 'dump_estado_pas: nao abre ', imagem);
    Halt(1);
  end;
  if roundtrip then
  begin
    if not db.Save(imagem, nil) then
    begin
      WriteLn(StdErr, 'dump_estado_pas: nao grava ', imagem);
      Halt(1);
    end;
    Halt(0);
  end;

  Linha('dump', 'we2002-state v1');
  LinhaInt('counts.players', PLAYERS_TOTAL);
  LinhaInt('counts.teams', TEAMS_NATIONAL_ALLSTAR_SLOTS);
  LinhaInt('counts.ml_teams', TEAMS_ML);
  LinhaInt('counts.formations', 16);

  for i := 0 to PLAYERS_TOTAL - 1 do
    DespejaJogador(i, db.players[i]);
  for i := 0 to TEAMS_NATIONAL_ALLSTAR_SLOTS - 1 do
    DespejaTime(i, db.teams[i]);
  for i := 0 to TEAMS_ML - 1 do
    DespejaMl('ml_teams[' + IntToStr(i) + '].', db.ml_teams[i]);
  DespejaMl('ml_default.', db.ml_default);
  for i := 0 to 15 do
    DespejaFormacao(i, db.preset_formations[i]);
  Linha('link_euro_allstar', CsvUnsigned(db.link_euro_allstar, 46));
  Linha('link_world_allstar', CsvUnsigned(db.link_world_allstar, 46));
end.
