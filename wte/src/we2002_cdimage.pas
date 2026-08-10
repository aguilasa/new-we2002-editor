{ GERADO por wte/tools/port_database_pas.py -- NAO editar a mao.

  Transpilado de src/core/include/we2002/CdImage.hpp, src/core/CdImage.cpp, que ja e byte-identico ao `ed.exe` nas duas ROMs.
  A entrada do transpilador e SEMPRE codigo deste repositorio -- nunca saida de
  decompilador (PLAN-WTE-LAZARUS §8.10).

  Os seeks, os comprimentos de leitura e os limites de laco estao intocados:
  eles codificam o layout MODE2/2352 da imagem, inclusive os saltos manuais
  sobre cabecalho de setor.

  Os trechos marcados PORTE A MAO nao sao transpilacao: sao decisao ja escrita
  em wte/re/tipos.md, com a rota registrada em wte/re/recusas.md.

  Regenerar:  python3 wte/tools/port_database_pas.py
  Conferir:   python3 wte/tools/port_database_pas.py --check }

unit we2002_cdimage;

{$mode objfpc}{$H+}
{$modeswitch advancedrecords}

interface

uses
  Classes, we2002_offsets;

type
  { PORTE A MAO (rota 3) -- wte/re/tipos.md, decisao 3.

    Tres propriedades do CFile do MFC sao load-bearing e o newWe2002 as
    preservou de proposito; o Pascal as preserva de novo:

      1. ponteiro de arquivo unico;
      2. LEITURA CURTA NAO E ERRO -- por isso `Read` e nunca `ReadBuffer`, que
         levanta EReadError no fim do arquivo;
      3. EDC/ECC NAO e recalculado na gravacao.

    E `fmOpenReadWrite`, nunca `fmCreate`: `fmCreate` truncaria uma imagem de
    474 MB. }
  TSectorPosition = record
    sector: TOffset;
    byte_in_sector: TOffset;
    in_data_region: Boolean;   { true quando byte_in_sector cai em [24, 2072) }
  end;

  TCdImage = record
  private
    FStream: TFileStream;
    FPath: string;
  public
    { Registro local nao e zerado pelo FPC; o `CdImage image_file;` do C++ vira
      declaracao + esta chamada. }
    procedure Init;
    function OpenRead(const path: string): Boolean;
    function OpenReadWrite(const path: string): Boolean;
    procedure Close;
    function IsOpen: Boolean;
    function Path: string;
    procedure Seek(position: TOffset; origin: TSeekOrigin);
    function Tell: TOffset;
    function Read(var buffer; count: SizeInt): SizeInt;
    procedure Write(const buffer; count: SizeInt);
    function Size: TOffset;
  end;


function Locate(absolute: TOffset): TSectorPosition;

implementation

uses
  SysUtils;

{ PORTE A MAO (rota 3) -- ver o comentario do tipo, na interface. }
procedure TCdImage.Init;
begin
  FStream := nil;
  FPath := '';
end;

function TCdImage.OpenRead(const path: string): Boolean;
begin
  Close;
  try
    FStream := TFileStream.Create(path, fmOpenRead or fmShareDenyNone);
  except
    on EStreamError do
    begin
      FStream := nil;
      Result := False;
      Exit;
    end;
  end;
  FPath := path;
  Result := True;
end;

function TCdImage.OpenReadWrite(const path: string): Boolean;
begin
  Close;
  try
    { fmOpenReadWrite e NUNCA fmCreate: a imagem e editada no lugar. }
    FStream := TFileStream.Create(path, fmOpenReadWrite or fmShareDenyNone);
  except
    on EStreamError do
    begin
      FStream := nil;
      Result := False;
      Exit;
    end;
  end;
  FPath := path;
  Result := True;
end;

procedure TCdImage.Close;
begin
  FreeAndNil(FStream);
  FPath := '';
end;

function TCdImage.IsOpen: Boolean;
begin
  Result := FStream <> nil;
end;

function TCdImage.Path: string;
begin
  Result := FPath;
end;

procedure TCdImage.Seek(position: TOffset; origin: TSeekOrigin);
begin
  if FStream <> nil then
    FStream.Seek(Int64(position), origin);
end;

function TCdImage.Tell: TOffset;
begin
  if FStream = nil then
    Result := -1
  else
    Result := FStream.Position;
end;

function TCdImage.Read(var buffer; count: SizeInt): SizeInt;
begin
  if FStream = nil then
  begin
    Result := 0;
    Exit;
  end;
  { TStream.Read, NUNCA ReadBuffer: leitura curta e fato, nao falha. }
  Result := FStream.Read(buffer, count);
end;

procedure TCdImage.Write(const buffer; count: SizeInt);
begin
  { WriteBuffer e aceitavel: escrita curta AQUI e erro. E nada de EDC/ECC. }
  if FStream <> nil then
    FStream.WriteBuffer(buffer, count);
end;

function TCdImage.Size: TOffset;
begin
  if FStream = nil then
    Result := -1
  else
    Result := FStream.Size;
end;

function Locate(absolute: TOffset): TSectorPosition;
var
  b: TOffset;
begin
  b := absolute mod SECTOR_SIZE;
  Result.sector := absolute div SECTOR_SIZE;
  Result.byte_in_sector := b;
  Result.in_data_region := (b >= SECTOR_DATA_BEGIN) and (b < SECTOR_DATA_END);
end;

end.
