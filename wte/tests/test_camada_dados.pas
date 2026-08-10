{ Prova, contra a camada de dados GERADA, as cinco decisoes de wte/re/tipos.md.

  Nao e teste de leitura de imagem -- isso e a WTE-TASK-20, com o round-trip
  contra o we2002_core. Aqui se mede o que a decisao de TIPO promete, que e o
  que erra em silencio: layout de bit, sinal de `char`, semantica da copia,
  leitura curta e o terminador do sidecar.

  Cada linha de saida e `OK<TAB>nome` ou `FALHA<TAB>nome<TAB>detalhe`. Quem le
  e wte/tools/test_port_database_pas.py, que reprova em qualquer FALHA e
  tambem se a contagem de casos mudar sem o teste mudar junto.

  Rodado por: wte/tools/test_port_database_pas.py
}

program test_camada_dados;

{$mode objfpc}{$H+}

uses
  Classes, SysUtils,
  we2002_types, we2002_team, we2002_player, we2002_cdimage, we2002_textcodec,
  we2002_database, we2002_offsets;

var
  falhas: LongInt = 0;
  { 1,2 MB -- variavel global de proposito: registro deste tamanho como local
    estoura a pilha, e o consumidor da camada tem a mesma restricao. }
  db: TDatabase;

procedure Checa(const nome: string; ok: Boolean; const detalhe: string = '');
begin
  if ok then
    WriteLn('OK'#9, nome)
  else
  begin
    WriteLn('FALHA'#9, nome, #9, detalhe);
    Inc(falhas);
  end;
end;

{ ---- decisao 2: bitfield por mascara e deslocamento -------------------- }
procedure NumerosDeCamisa;
var
  n: TSquadNumbers;
  i: LongInt;
  esperado: LongWord;
begin
  Checa('squad_numbers/tamanho', SizeOf(TSquadNumbers) = 16,
        Format('SizeOf = %d', [SizeOf(TSquadNumbers)]));

  n := Default(TSquadNumbers);
  for i := 0 to 5 do
    SetSquadNumberAt(n, i, i + 1);
  { O mesmo vetor do TestSquadNumbersLayout do newWe2002. }
  esperado := 1 or (2 shl 5) or (3 shl 10) or (4 shl 15) or (5 shl 20)
              or (6 shl 25);
  Checa('squad_numbers/layout', n.groups[0] = esperado,
        Format('%x <> %x', [n.groups[0], esperado]));

  SetSquadNumberAt(n, 6, 31);
  Checa('squad_numbers/segunda_unidade', n.groups[1] = 31,
        Format('%x', [n.groups[1]]));

  for i := 0 to 22 do
    SetSquadNumberAt(n, i, LongWord(i mod 32));
  for i := 0 to 22 do
    if SquadNumberAt(n, i) <> LongWord(i mod 32) then
    begin
      Checa('squad_numbers/ida_e_volta', False, Format('slot %d', [i]));
      Exit;
    end;
  Checa('squad_numbers/ida_e_volta', True);

  { Indice fora de 0..22 devolve 0 e IGNORA escrita, em vez de alcancar o
    campo vizinho. }
  SetSquadNumberAt(n, 23, 31);
  SetSquadNumberAt(n, -1, 31);
  Checa('squad_numbers/fora_da_faixa',
        (SquadNumberAt(n, 23) = 0) and (SquadNumberAt(n, -1) = 0)
        and (SquadNumberAt(n, 22) = LongWord(22 mod 32)));
end;

{ ---- decisao 1: copia com semantica de C, sem checar limite ------------ }
procedure CopiaComSemanticaDeC;
var
  t: TTeam;
  origem: array[0..31] of AnsiChar;
  i: LongInt;
  destino, cauda: array[0..15] of AnsiChar;
begin
  t := Default(TTeam);
  { 30 bytes SEM #0, como o Load le da imagem. A copia escreve 31 -- e o
    31o byte tem de caber em raw_formation, nao vazar para slot_role. Foi este
    estouro que o newWe2002 mediu em TODA imagem aberta. }
  for i := 0 to 29 do
    origem[i] := AnsiChar(Ord('A') + (i mod 26));
  origem[30] := #0;
  CStrCopy(t.raw_formation, origem);
  Checa('cstrcopy/formacao_de_31',
        (t.raw_formation[29] = origem[29]) and (t.raw_formation[30] = #0)
        and (t.slot_role[0] = 0), 'o terminador vazou para slot_role');

  destino := 'abc'#0'zzzzzzzzzzz';
  cauda := 'de'#0'zzzzzzzzzzzz';
  CStrCat(destino, cauda);
  Checa('cstrcat/concatena',
        (destino[0] = 'a') and (destino[3] = 'd') and (destino[4] = 'e')
        and (destino[5] = #0));
  Checa('cstrlen/conta_ate_o_nul', CStrLen(destino) = 5,
        Format('%d', [CStrLen(destino)]));
end;

{ ---- decisao 4: `char` numerico tem SINAL ------------------------------ }
procedure CharNumericoTemSinal;
var
  t: TTeam;
  b: Byte;
begin
  t := Default(TTeam);
  b := $C8;                        { 200 }
  Move(b, t.flag_shape, 1);
  { A UI alarga com static_cast<int>: 200 tem de chegar como -56, igual ao
    we2002_core. Mapear para Byte mostraria 200 na tela. }
  Checa('char_numerico/sinal', t.flag_shape = -56,
        Format('%d', [t.flag_shape]));
  Checa('char_numerico/tamanho', SizeOf(t.flag_shape) = 1);
end;

{ ---- decisao 4, um nivel acima: a CONVERSAO local->campo (CORR-WTE-043) --- }
procedure CustoNcEntraComSinal;
var
  caminho: string;
  f: TFileStream;
  zeros: array[0..65535] of Byte;
  b: Byte;
  restam: Int64;
  bloco: LongInt;
begin
  { Imagem esparsa: zeros ate OFS_COST_NC, depois 0xC8 no custo do jogador 0
    e 0x24 no do jogador 1. O resto do Load le curto, que a decisao 3 diz nao
    ser erro. }
  caminho := GetTempFileName;
  f := TFileStream.Create(caminho, fmCreate);
  try
    FillChar(zeros, SizeOf(zeros), 0);
    restam := OFS_COST_NC;
    while restam > 0 do
    begin
      bloco := SizeOf(zeros);
      if restam < bloco then
        bloco := restam;
      f.WriteBuffer(zeros, bloco);
      Dec(restam, bloco);
    end;
    b := $C8;                      { 200 sem sinal, -56 com }
    f.WriteBuffer(b, 1);
    b := $24;                      { 36: o maximo que as duas ROMs tem }
    f.WriteBuffer(b, 1);
  finally
    f.Free;
  end;

  Checa('custo_nc/carrega', db.Load(caminho, nil));
  { `players[i].cost = buf1[0]` do C++ estende sinal -- `char` do x86 com
    destino `int`. `Ord` entregaria 200, e o erro seria mudo: o Save grava so
    o byte baixo, entao o round-trip devolve a imagem identica. }
  Checa('custo_nc/sinal', db.players[0].cost = -56,
        Format('%d', [db.players[0].cost]));
  Checa('custo_nc/positivo_intacto', db.players[1].cost = 36,
        Format('%d', [db.players[1].cost]));
  DeleteFile(caminho);
end;

function TamanhoDe(const caminho: string): Int64;
var
  f: TFileStream;
begin
  f := TFileStream.Create(caminho, fmOpenRead or fmShareDenyNone);
  try
    Result := f.Size;
  finally
    f.Free;
  end;
end;

{ ---- decisao 3: leitura curta NAO e erro ------------------------------- }
procedure LeituraCurtaNaoEErro;
var
  caminho: string;
  f: TFileStream;
  img: TCdImage;
  buf: array[0..63] of Byte;
  lidos: SizeInt;
  antes: Int64;
begin
  caminho := GetTempFileName;
  f := TFileStream.Create(caminho, fmCreate);
  try
    FillChar(buf, SizeOf(buf), $5A);
    f.WriteBuffer(buf, 64);
  finally
    f.Free;
  end;

  img.Init;
  Checa('cdimage/abre_leitura', img.OpenRead(caminho));
  img.Seek(32, soBeginning);
  lidos := img.Read(buf, 64);      { pede 64 a 32 bytes do fim }
  Checa('cdimage/leitura_curta', lidos = 32, Format('%d', [lidos]));
  img.Close;

  { fmOpenReadWrite, nunca fmCreate: fmCreate truncaria uma imagem de 474 MB. }
  antes := TamanhoDe(caminho);
  img.Init;
  Checa('cdimage/abre_escrita', img.OpenReadWrite(caminho));
  img.Close;
  Checa('cdimage/nao_trunca', TamanhoDe(caminho) = antes,
        Format('%d -> %d', [antes, TamanhoDe(caminho)]));

  img.Init;
  Checa('cdimage/arquivo_ausente',
        not img.OpenRead(caminho + '.nao-existe'));
  img.Close;
  DeleteFile(caminho);
end;

{ ---- o codec de kanji, que o Load chama 95 vezes ----------------------- }
procedure CodecDeKanji;
var
  ascii: array[0..19] of Byte;
  kanji: array[0..39] of Byte;
  volta: array[0..19] of Byte;
  i: LongInt;
  texto: string;
begin
  FillChar(ascii, SizeOf(ascii), 0);
  texto := 'BRASIL';
  for i := 1 to Length(texto) do
    ascii[i - 1] := Ord(texto[i]);
  AsciiToKanji(@ascii[0], @kanji[0], 8);
  Checa('kanji/maiuscula', (kanji[0] = 130) and (kanji[1] = Ord('B') + 31),
        Format('%d %d', [kanji[0], kanji[1]]));
  KanjiToAscii(@kanji[0], @volta[0], 8);
  Checa('kanji/ida_e_volta',
        (volta[0] = Ord('B')) and (volta[5] = Ord('L')) and (volta[7] = 0));
end;

{ ---- decisao 5: o sidecar `_url.txt` e byte a byte ---------------------- }
procedure SidecarDeUrl;
var
  base, sidecar: string;
  f: TFileStream;
  bytes: array of Byte;
  i, lf, cr: LongInt;
  url: string;
begin
  base := GetTempFileName + '.bin';
  db.Init;
  url := 'https://sofifa.com/player/158023';
  for i := 1 to Length(url) do
    db.players[0].url[i - 1] := AnsiChar(url[i]);

  sidecar := UrlSidecarPath(base);
  Checa('sidecar/caminho', sidecar = ChangeFileExt(base, '') + '_url.txt',
        sidecar);

  db.WriteUrlSidecar(base);
  f := TFileStream.Create(sidecar, fmOpenRead or fmShareDenyNone);
  try
    SetLength(bytes, f.Size);
    if f.Size > 0 then
      f.ReadBuffer(bytes[0], f.Size);
  finally
    f.Free;
  end;
  lf := 0;
  cr := 0;
  for i := 0 to High(bytes) do
  begin
    if bytes[i] = 10 then Inc(lf);
    if bytes[i] = 13 then Inc(cr);
  end;
  { Contar LINHA nao serve: TStringList com LineEnding de Windows daria 1911
    linhas com CRLF, e WriteBOM daria tres bytes a mais no comeco. Os dois
    passariam num teste de contagem de linha e reescreveriam arquivo do
    usuario. Por isso a conferencia e em BYTE. }
  Checa('sidecar/uma_linha_por_jogador', lf = PLAYERS_TOTAL,
        Format('%d', [lf]));
  Checa('sidecar/sem_cr', cr = 0, Format('%d', [cr]));
  Checa('sidecar/sem_bom',
        (Length(bytes) > 3) and not ((bytes[0] = $EF) and (bytes[1] = $BB)));
  Checa('sidecar/termina_em_lf', bytes[High(bytes)] = 10);
  Checa('sidecar/primeira_url',
        Copy(PAnsiChar(@bytes[0]), 1, Length(url)) = url);
  DeleteFile(sidecar);
  DeleteFile(base);
end;

begin
  NumerosDeCamisa;
  CopiaComSemanticaDeC;
  CharNumericoTemSinal;
  CustoNcEntraComSinal;
  LeituraCurtaNaoEErro;
  CodecDeKanji;
  SidecarDeUrl;
  if falhas > 0 then
    Halt(1);
end.
