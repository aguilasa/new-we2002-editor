{ we2002_bmp -- o recipiente de 8 bpp em que a paleta da WTE-TASK-29 mora.

  ESCRITA A MAO, como a `we2002_render`, e pelo mesmo motivo: nao ha gerador
  possivel para uma rotina. O que e gerado e a *conferencia* -- o
  `wte/tools/dump_render2d.py` mede a forma real dos 198 `.bmp` do usuario e
  recusa se qualquer um deles deixar de casar com as constantes daqui.

  ESTA UNIDADE NAO DESENHA, e nao usa LCL. Ela le bytes de arquivo e devolve
  bytes; quem os poe na tela e a `wte_render2d`, que e a unica das duas que
  precisa de janela. A separacao e a mesma da `we2002_render`.

  POR QUE UM DECODIFICADOR PROPRIO, e nao o leitor de BMP da LCL: o que este
  port precisa fazer com o arquivo nao e exibi-lo, e **trocar a paleta antes de
  exibir**. O caminho da LCL entrega o bitmap ja convertido para 32 bpp, com a
  paleta consumida e jogada fora -- e o indice de cada pixel, que e o unico
  ativo real do arquivo (secao 6.2 do `assets.md`), some no caminho. Aqui o
  indice sobrevive, e a paleta e argumento.

  A DIVERGENCIA DELIBERADA, e ela e recomendacao antiga: **o original grava a
  paleta DENTRO do `.bmp` do usuario** (`fopen(..., "r+b")`, `fseek(0x36)`,
  `fputc`) e so entao chama `LoadFromFile`. Este port faz a mesma aritmetica
  num buffer em memoria e nunca abre o arquivo para escrita. A recomendacao e
  da secao 6.2 do `wte/re/assets.md`, e a razao e concreta: reproduzir a
  gravacao tornaria o porte read-write numa pasta de dados que, aqui, e um
  symlink para a pasta do Obocaman. Nenhum byte de imagem de CD passa por
  aqui, entao o gate nao mede esta unidade -- quem a mede sao os testes. }

unit we2002_bmp;

{$mode objfpc}{$H+}

interface

uses
  we2002_render;

const
  { A forma que a mecanica do original ASSUME, e que os 198 arquivos cumprem.
    Nao e "o formato BMP": e o subconjunto que faz o `0x36` do original cair na
    primeira entrada da paleta. Um so arquivo de 24 bpp na pasta quebraria a
    mecanica inteira -- o cabecalho teria outro tamanho e o `0x36` cairia no
    meio do pixel. Por isso a `ValidaBmp8` recusa em vez de tentar. }
  BMP_ASSINATURA = $4D42;        { 'BM', em little-endian }
  BMP_INFO_BYTES = 40;           { BITMAPINFOHEADER, e nao a de 12 do OS/2 }
  BMP_BITS = 8;
  BMP_SEM_COMPRESSAO = 0;
  BMP_PALETA_ENTRADAS = 256;
  { Onde os pixels comecam. E o numero que fecha o circulo com o `push 0x36`
    das tres rotinas de desenho: se a paleta tivesse outro tamanho, o `0x36`
    nao seria a entrada zero.

    LITERAL, e nao expressao, pelo mesmo motivo das constantes da
    `we2002_render`: o `dump_render2d.py` le esta secao com um parser de
    literal e a compara com o cabecalho REAL dos 198 `.bmp` do usuario. A
    derivacao mora aqui embaixo e e executada pelo `test_bmp.pas`. }
  BMP_DADOS = 1078;   { BMP_CABECALHO + BMP_PALETA_ENTRADAS * BMP_ENTRADA_BYTES }

type
  { O arquivo inteiro em memoria, mais o que o cabecalho diz. `dados` guarda os
    bytes crus de proposito: a troca de paleta e uma escrita de tres bytes por
    entrada no mesmo buffer, exatamente como o original a faz no arquivo. }
  TBmp8 = record
    dados: array of Byte;
    largura: Integer;
    altura: Integer;
  end;

{ Recusa tudo que nao seja a forma acima. Devolve False em vez de levantar: o
  chamador e a tela, e tela que morre por causa de um `.bmp` do usuario e pior
  do que tela que nao desenha. }
function ValidaBmp8(const bmp: TBmp8): Boolean;

{ Le o arquivo inteiro para memoria e confere a forma. `False` se nao existir,
  se for curto demais ou se nao passar na `ValidaBmp8`. }
function CarregaBmp8(const caminho: string; out bmp: TBmp8): Boolean;

{ Troca `quantas` entradas da paleta, no buffer, a partir de `cores[primeira]`.

  E a rotina do original, byte a byte: para cada entrada, escreve B, G e R --
  nessa ordem -- e **pula o quarto byte** em vez de zera-lo. O quarto e o
  reservado, e o original salta nele com `fseek(+1)`; preservar e o
  comportamento correto de um port.

  Os dois parametros existem porque os dois DIFEREM entre os desenhistas:
  a bandeira faz 16 entradas a partir da palavra 0, o uniforme faz 15 a partir
  da palavra 1. Decidir aqui dentro faria a unidade escolher por quem chama --
  e a escolha errada e invisivel, porque as duas produzem uma tela colorida. }
procedure AplicaPaleta(var bmp: TBmp8; const cores: array of TCorBgr555;
                       primeira, quantas: Integer);

{ Os tres bytes de uma entrada da paleta, como estao no buffer: B, G, R. }
function EntradaCrua(const bmp: TBmp8; indice: Integer): TEntradaDePaleta;

{ O indice de paleta de um pixel, com `y = 0` no TOPO.

  O BMP guarda as linhas de baixo para cima e alinha cada uma em quatro bytes;
  os dois detalhes ficam aqui para nao vazarem para quem desenha. Fora da
  imagem devolve 0. }
function IndiceDoPixel(const bmp: TBmp8; x, y: Integer): Byte;

{ Bytes por linha ja alinhados -- `((largura + 3) div 4) * 4`. }
function BytesPorLinha(largura: Integer): Integer;

implementation

uses
  Classes, SysUtils;

function LeWord(const bmp: TBmp8; posicao: Integer): Word; inline;
begin
  Result := Word(bmp.dados[posicao]) or (Word(bmp.dados[posicao + 1]) shl 8);
end;

function LeLongInt(const bmp: TBmp8; posicao: Integer): LongInt; inline;
begin
  Result := LongInt(bmp.dados[posicao])
            or (LongInt(bmp.dados[posicao + 1]) shl 8)
            or (LongInt(bmp.dados[posicao + 2]) shl 16)
            or (LongInt(bmp.dados[posicao + 3]) shl 24);
end;

function BytesPorLinha(largura: Integer): Integer;
begin
  Result := ((largura + 3) div 4) * 4;
end;

function ValidaBmp8(const bmp: TBmp8): Boolean;
var
  altura: LongInt;
begin
  Result := False;
  if Length(bmp.dados) < BMP_DADOS then
    Exit;
  if LeWord(bmp, 0) <> BMP_ASSINATURA then
    Exit;
  { O `bfOffBits` e a conferencia que importa: e ele que diz onde os pixels
    comecam, e o original nao o consulta -- ele assume `0x36` para a paleta.
    Se um arquivo trouxesse outro valor, a troca de paleta acertaria o lugar
    errado. }
  if LeLongInt(bmp, 10) <> BMP_DADOS then
    Exit;
  if LeLongInt(bmp, 14) <> BMP_INFO_BYTES then
    Exit;
  if LeWord(bmp, 28) <> BMP_BITS then
    Exit;
  if LeLongInt(bmp, 30) <> BMP_SEM_COMPRESSAO then
    Exit;
  altura := Abs(LeLongInt(bmp, 22));
  if (LeLongInt(bmp, 18) <= 0) or (altura <= 0) then
    Exit;
  if Length(bmp.dados) < BMP_DADOS + BytesPorLinha(LeLongInt(bmp, 18)) * altura
  then
    Exit;
  Result := True;
end;

function CarregaBmp8(const caminho: string; out bmp: TBmp8): Boolean;
var
  f: TFileStream;
  tamanho: Int64;
begin
  Result := False;
  bmp.dados := nil;
  bmp.largura := 0;
  bmp.altura := 0;
  if not FileExists(caminho) then
    Exit;
  try
    f := TFileStream.Create(caminho, fmOpenRead or fmShareDenyNone);
  except
    Exit;
  end;
  try
    tamanho := f.Size;
    { Um `.bmp` desta pasta tem alguns milhares de bytes. O teto existe so para
      que um arquivo trocado por engano nao vire alocacao de gigabytes. }
    if (tamanho < BMP_DADOS) or (tamanho > 16 * 1024 * 1024) then
      Exit;
    SetLength(bmp.dados, tamanho);
    f.ReadBuffer(bmp.dados[0], tamanho);
  finally
    f.Free;
  end;
  if not ValidaBmp8(bmp) then
  begin
    bmp.dados := nil;
    Exit;
  end;
  bmp.largura := LeLongInt(bmp, 18);
  bmp.altura := Abs(LeLongInt(bmp, 22));
  Result := True;
end;

procedure AplicaPaleta(var bmp: TBmp8; const cores: array of TCorBgr555;
                       primeira, quantas: Integer);
var
  i, posicao: Integer;
  entrada: TEntradaDePaleta;
begin
  if primeira < 0 then
    Exit;
  if primeira + quantas > Length(cores) then
    quantas := Length(cores) - primeira;
  if quantas > BMP_PALETA_ENTRADAS then
    quantas := BMP_PALETA_ENTRADAS;
  if Length(bmp.dados) < BMP_DADOS then
    Exit;
  for i := 0 to quantas - 1 do
  begin
    entrada := EntradaDePaleta(cores[primeira + i]);
    posicao := OffsetDaEntrada(i);
    bmp.dados[posicao] := entrada[0];       { B }
    bmp.dados[posicao + 1] := entrada[1];   { G }
    bmp.dados[posicao + 2] := entrada[2];   { R }
    { posicao + 3 -- o reservado -- fica como estava. O original o salta. }
  end;
end;

function EntradaCrua(const bmp: TBmp8; indice: Integer): TEntradaDePaleta;
var
  posicao: Integer;
begin
  Result[0] := 0;
  Result[1] := 0;
  Result[2] := 0;
  if (indice < 0) or (indice >= BMP_PALETA_ENTRADAS) then
    Exit;
  if Length(bmp.dados) < BMP_DADOS then
    Exit;
  posicao := OffsetDaEntrada(indice);
  Result[0] := bmp.dados[posicao];
  Result[1] := bmp.dados[posicao + 1];
  Result[2] := bmp.dados[posicao + 2];
end;

function IndiceDoPixel(const bmp: TBmp8; x, y: Integer): Byte;
var
  linha: Integer;
begin
  Result := 0;
  if (x < 0) or (y < 0) or (x >= bmp.largura) or (y >= bmp.altura) then
    Exit;
  { De baixo para cima: a linha 0 do arquivo e a de BAIXO da imagem. }
  linha := bmp.altura - 1 - y;
  Result := bmp.dados[BMP_DADOS + linha * BytesPorLinha(bmp.largura) + x];
end;

end.
