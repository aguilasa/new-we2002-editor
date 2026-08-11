{ we2002_estado -- o estado que os 96 handlers compartilham (WTE-TASK-25).

  ESCRITO A MAO, e de proposito. As oito unidades `we2002_*` da fase 3 sao
  saida de gerador e nao podem crescer; as 18 `ep2002_*` sao saida do
  `dfm2lfm.py` e tambem nao. O que a fase 4 acrescenta -- estado global,
  abertura de imagem, o patch de arranque -- nao e transpilacao de nada e nao
  tem gerador possivel. Fica aqui, num lugar so, em vez de espalhado pelos
  `.inc` de `src/impl/`.

  No original este estado sao globais de modulo do `.exe`: o `FILE*` do
  `dat.bin` em `0x00432e68`, o diretorio corrente em `0x00432e80`, e o
  ponteiro de time em `0x004335e4` -- este ultimo o que a CORR-WTE-044 mediu
  sobrescrito pela carga de time com a ROM europeia. }

unit we2002_estado;

{$mode objfpc}{$H+}

interface

uses
  SysUtils, we2002_database, we2002_cdimage;

const
  { O patch de arranque, medido na WTE-TASK-08 (`wte/re/assets.md` secao 8.2) e
    lido do disassembly em 0x40c0ee..0x40c1a0. Abrir a imagem injeta sete
    setores vindos da segunda metade do `dat.bin`.

    `PATCH_IMAGEM_INICIO` = 0x2e08 = 5 * 2352 + 24, o primeiro byte de dados do
    setor 5. `PATCH_SALTO` = 0x130 = 2352 - 2048, o salto sobre EDC/ECC e o
    cabecalho do setor seguinte -- a mesma aritmetica sector-aware do resto do
    formato. `PATCH_SENTINELA_POS` = 0x2e14 guarda 0xFC quando a injecao ja
    aconteceu, e o original NAO reinjeta nesse caso. }
  PATCH_DAT_INICIO    = $20000;   { onde o patch comeca dentro do dat.bin     }
  PATCH_IMAGEM_INICIO = $2e08;    { setor 5, primeiro byte de dados          }
  PATCH_SENTINELA_POS = $2e14;    { 0xFC = ja injetado                       }
  PATCH_SENTINELA     = $FC;
  PATCH_SETORES       = 7;
  PATCH_BYTES         = 2048;     { dados de usuario de um setor MODE2/2352  }
  PATCH_SALTO         = $130;     { 2352 - 2048                             }

var
  { A imagem carregada. Vazio enquanto nenhuma foi aberta. }
  Jogo: TDatabase;
  ImagemAberta: string = '';

  { As seis pastas de asset, montadas pelo `MainForm.FormCreate` (0x004107c8).

    No original sao seis globais de AnsiString, medidos na WTE-TASK-08
    (`wte/re/assets.md` secao 2) e reconfirmados pelo `wte/re/arranque.md`:

      0x00432e6c  <cwd>\image              base das quatro pastas de imagem
      0x00432e70  <cwd>\image\barba
      0x00432e74  <cwd>\image\pelo
      0x00432e78  <cwd>\image\banderas
      0x00432e7c  <cwd>\image\uniformes2d
      0x00432e80  <cwd>\data               o `dat.bin`

    Vazias enquanto o `MainForm.FormCreate` nao rodou. Quem le asset e a fase
    5 (WTE-TASK-31, 32); aqui elas so existem e sao montadas na mesma ordem. }
  DirImage: string = '';
  DirBarba: string = '';
  DirPelo: string = '';
  DirBanderas: string = '';
  DirUniformes2d: string = '';
  DirData: string = '';

{ Monta as seis pastas acima. Idempotente.

  DIVERGENCIA DELIBERADA, para a WTE-TASK-35: o original monta os seis a
  partir de `GetCurrentDir()`, e por isso exige ser clicado de dentro da
  propria pasta -- e dai vem a mensagem `The file "dat.bin" must be in the
  "data" directory`. Reproduzir a dependencia do diretorio corrente seria
  reproduzir um defeito de empacotamento. Aqui a raiz sai de `RaizDosAssets`;
  os seis nomes, a ordem e o encadeamento (os quatro de imagem penduram em
  `image`, e `data` pendura na raiz) sao os do original. }
procedure ResolveDiretorios;

{ Raiz que contem `image/` e `data/`. Vazia quando nao se acha nenhuma.

  Procura, na ordem, `$WTE_ASSETS_DIR`, a pasta ao lado do executavel, e a
  arvore de fonte. A resolucao definitiva (prefixo instalado) e da
  WTE-TASK-39. }
function RaizDosAssets: string;

{ Caminho do `data/dat.bin`. Vazio quando nao se acha nenhum. }
function CaminhoDatBin: string;

{ Injeta os sete setores, se ainda nao estiverem la. Devolve o numero de
  setores gravados -- 0 quando a sentinela ja valia 0xFC.

  Grava NA IMAGEM. E a unica escrita do grupo de carga, e ela existe: a
  WTE-TASK-25 previa provar que a carga nao grava nada, e a medicao do gate
  (WTE-TASK-22) mostra o contrario. }
function InjetaPatchDeArranque(const imagem: string): Integer;

{ Abre a imagem: injeta o patch e carrega o banco. False quando nao da para
  abrir o arquivo. }
function AbreImagem(const caminho: string): Boolean;

implementation

uses
  Classes;

function RaizDosAssets: string;
var
  candidatos: array[0..2] of string;
  i: Integer;
  base: string;
begin
  base := ExtractFilePath(ParamStr(0));
  candidatos[0] := GetEnvironmentVariable('WTE_ASSETS_DIR');
  candidatos[1] := base + '..' + DirectorySeparator + 'assets';
  candidatos[2] := base + '..' + DirectorySeparator + '..'
                        + DirectorySeparator + 'assets';
  for i := Low(candidatos) to High(candidatos) do
  begin
    if candidatos[i] = '' then
      Continue;
    Result := IncludeTrailingPathDelimiter(candidatos[i]);
    if FileExists(Result + 'data' + DirectorySeparator + 'dat.bin') then
      Exit;
  end;
  Result := '';
end;

procedure ResolveDiretorios;
var
  raiz: string;
begin
  raiz := RaizDosAssets;
  if raiz = '' then
    Exit;
  { A ordem e o encadeamento sao os do original: `image` sai da raiz, os quatro
    seguintes saem de `image`, e `data` sai da raiz de novo. }
  DirImage       := raiz + 'image';
  DirBarba       := DirImage + DirectorySeparator + 'barba';
  DirPelo        := DirImage + DirectorySeparator + 'pelo';
  DirBanderas    := DirImage + DirectorySeparator + 'banderas';
  DirUniformes2d := DirImage + DirectorySeparator + 'uniformes2d';
  DirData        := raiz + 'data';
end;

function CaminhoDatBin: string;
begin
  { Chamavel antes do `FormCreate` -- o `InjetaPatchDeArranque` a usa, e o
    `wte/tests/` a usa sem formulario nenhum. }
  if DirData = '' then
    ResolveDiretorios;
  if DirData = '' then
    Exit('');
  Result := DirData + DirectorySeparator + 'dat.bin';
  if not FileExists(Result) then
    Result := '';
end;

function InjetaPatchDeArranque(const imagem: string): Integer;
var
  img: TCdImage;
  dat: TFileStream;
  caminho_dat: string;
  buffer: array[0..PATCH_BYTES - 1] of Byte;
  sentinela: Byte;
  i: Integer;
begin
  Result := 0;
  caminho_dat := CaminhoDatBin;
  if caminho_dat = '' then
    Exit;

  img.Init;
  if not img.OpenReadWrite(imagem) then
    Exit;
  try
    { A sentinela vem antes de tudo: reinjetar sobre uma imagem ja injetada
      gravaria os mesmos bytes e nao mudaria nada, mas o original checa, e o
      gate compara o que os dois GRAVAM. }
    img.Seek(PATCH_SENTINELA_POS, soBeginning);
    sentinela := 0;
    if img.Read(sentinela, 1) <> 1 then
      Exit;
    if sentinela = PATCH_SENTINELA then
      Exit;

    dat := TFileStream.Create(caminho_dat, fmOpenRead or fmShareDenyNone);
    try
      dat.Position := PATCH_DAT_INICIO;
      img.Seek(PATCH_IMAGEM_INICIO, soBeginning);
      for i := 1 to PATCH_SETORES do
      begin
        if dat.Read(buffer, PATCH_BYTES) <> PATCH_BYTES then
          Break;
        img.Write(buffer, PATCH_BYTES);
        img.Seek(PATCH_SALTO, soCurrent);
        Inc(Result);
      end;
    finally
      dat.Free;
    end;
  finally
    img.Close;
  end;
end;

function AbreImagem(const caminho: string): Boolean;
begin
  Result := False;
  if not FileExists(caminho) then
    Exit;
  InjetaPatchDeArranque(caminho);
  Jogo.Init;
  Result := Jogo.Load(caminho, nil);
  if Result then
    ImagemAberta := caminho
  else
    ImagemAberta := '';
end;

end.
