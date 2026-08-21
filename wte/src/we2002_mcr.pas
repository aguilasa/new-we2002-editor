{ we2002_mcr -- o memory card do PSX (WTE-TASK-28).

  ESCRITO A MAO, como o `we2002_estado`: nao ha gerador possivel para a rotina,
  e o que E gerado -- a conferencia do layout contra o `.exe` -- e o
  `wte/tools/dump_mcr.py`, que a cada `make check` confere as constantes daqui
  contra o que o binario usa. Documentacao do formato em `wte/re/mcr.md`.

  A DIVISAO QUE O ENUNCIADO DA TASK MANDA FAZER: conteiner pela documentacao
  publica, conteudo por engenharia reversa. O cartao do PSX sao 16 blocos de
  8192 bytes, o bloco 0 sendo cabecalho `MC` mais 15 quadros de diretorio de
  128 bytes; o que o WE2002 guarda dentro do bloco dele e que nao e publico.

  UM ACHADO QUE VALE SABER ANTES DE MEXER AQUI: dos 17 destinos, 14 caem no
  bloco 3, que o diretorio do proprio cartao declara LIVRE -- o save diz ocupar
  os blocos 1 e 2. Jogadores e numeros de camisa vao para o 2; formacao, tatica
  e cobradores vao para o 3. Medido, com o diretorio saindo intacto; o veredito
  esta em `wte/re/mcr.md`. }

unit we2002_mcr;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils;

const
  { O molde: a PRIMEIRA metade do `dat.bin` e um cartao PSX formatado, com o
    slot do WE2002 pronto. `0x20000` = 131.072 = o tamanho exato de um memory
    card. A segunda metade e outra coisa -- os 7 setores que o arranque injeta
    na imagem, ja portados no `we2002_estado`. }
  CARTAO_BYTES = $20000;
  CARTAO_BLOCO = 8192;          { 16 blocos; o 0 e cabecalho + diretorio      }

  { Os destinos dentro do cartao. Todos medidos: a sonda `27-mcr.txt` produz um
    `.mcr` pelo oraculo e o compara com o molde do `dat.bin`. }
  MCR_NUMEROS       = $5404;   { 16 B: os 23 dorsais, 5 bits cada        }
  MCR_JOGADORES     = $5904;   { 23 registros, 22 B uteis em 32 de passo }
  MCR_JOGADOR_PASSO = 32;
  MCR_ATRIBUTO_BYTES = 12;     { a metade que vem primeiro no registro   }
  MCR_NOME_BYTES     = 10;     { a metade que vem depois                 }
  MCR_FORMACAO_1    = $63D5;   { os 10 primeiros bytes da formacao       }
  MCR_FORMACAO_2    = $62A8;   { os 20 restantes                         }
  MCR_TATICA_CRUA   = $64E2;   { tatica[0], como esta na imagem          }
  MCR_TATICA_MAIS50 = $6102;   { tatica[0] + 50, o mesmo byte de novo    }
  MCR_TATICA_1_BAIXO = $6488;
  MCR_TATICA_1_ALTO  = $6479;
  MCR_TATICA_2_BAIXO = $6497;
  MCR_TATICA_2_ALTO  = $64A6;
  MCR_CAPITAO        = $6500;  { o sexto byte do bloco de cobradores     }

  JOGADORES_NO_CARTAO = 23;
  FORMACAO_BYTES      = 30;
  COBRADORES_BYTES    = 6;
  NUMEROS_BYTES       = 16;

  { Os cinco destinos dos cobradores, na ORDEM em que o original os grava --
    a tabela de cinco `DWORD` em `0x00423F84`. Ela NAO e crescente, e por isso
    e tabela e nao aritmetica. O sexto -- o capitao -- nao esta nela: mora em
    `MCR_CAPITAO`, longe dos outros. }
  MCR_COBRADORES: array[0..4] of LongInt = ($614F, $6140, $6122, $6113, $6131);

type
  { O conteudo do bloco do WE2002, do jeito que a `0x0040b9ec` o le.

    NAO TEM TATICA, e a ausencia e do original: o escritor grava seis campos de
    tatica e o leitor nao le nenhum deles. Quem le tatica de um `.mcr` e o
    `boton_mcr2isoClick`, direto do arquivo. Por isso este registro reproduz o
    que o LEITOR traz, e nao o que o cartao guarda. }
  { Os tres bytes de tatica que a imagem guarda por time. }
  TTaticaDoCartao = array[0 .. 2] of Byte;

  TCartaoDeMemoria = record
    nomes: array[0 .. JOGADORES_NO_CARTAO * MCR_NOME_BYTES - 1] of Byte;
    atributos: array[0 .. JOGADORES_NO_CARTAO * MCR_ATRIBUTO_BYTES - 1] of Byte;
    numeros: array[0 .. NUMEROS_BYTES - 1] of Byte;
    formacao: array[0 .. FORMACAO_BYTES - 1] of Byte;
    cobradores: array[0 .. COBRADORES_BYTES - 1] of Byte;
  end;

{ Le um `.mcr` para o registro acima -- a `0x0040b9ec`, que o
  `boton_mcrClick` chama depois de escolher o arquivo.

  False quando o arquivo nao abre ou nao tem `CARTAO_BYTES`. O original nao
  confere o tamanho; aqui a conferencia existe porque um arquivo curto faria o
  leitor trazer lixo silenciosamente, e lixo daqui vai PARA A IMAGEM pelo
  `boton_mcr2iso`. Divergencia deliberada, WTE-TASK-35. }
function LeCartaoDeMemoria(const caminho: string;
                           out cartao: TCartaoDeMemoria): Boolean;

{ O numero de camisa do slot `j`, dos 16 bytes de `numeros`.

  Cinco bits por jogador, SEIS jogadores por grupo de 4 bytes: 30 bits usados
  e 2 perdidos, quatro grupos, 16 bytes -- a mesma forma do `SquadNumbers` do
  `we2002_core`. O `+1` e do original: o cartao guarda o numero menos um. }
function NumeroDoCartao(const cartao: TCartaoDeMemoria; j: Integer): Integer;

{ Os TRES bytes de tatica, montados dos cinco campos do cartao.

  NAO E O `LeCartaoDeMemoria` quem faz isto, e a separacao e do original: a
  `0x0040b9ec`, que enche o registro acima, nao le tatica nenhuma. Quem le e o
  `boton_mcr2isoClick`, direto do arquivo (`0x0040c759` em diante), montando um
  rascunho de 4 bytes com quatro insercoes de nibble e gravando os TRES
  primeiros na imagem. Esta funcao e esse trecho, e por isso mora fora do
  registro.

  A montagem e o inverso exato do que o escritor desmonta:

      tatica[0] := byte cru de MCR_TATICA_CRUA
      tatica[1] := MCR_TATICA_1_BAIXO  or  (MCR_TATICA_1_ALTO  shl 4)
      tatica[2] := MCR_TATICA_2_BAIXO  or  (MCR_TATICA_2_ALTO  shl 4)

  O `MCR_TATICA_MAIS50` nao entra: e o mesmo byte 0 mais 50, que o cartao
  guarda duas vezes e o original nunca le de volta. }
function LeTaticaDoCartao(const caminho: string; out tatica: TTaticaDoCartao): Boolean;

{ O cartao declara ocupar quantos blocos? Le o diretorio pelo formato publico.

  Devolve 0 quando o arquivo nao e cartao (nao comeca com `MC`). Existe para o
  teste: e a unica leitura de CONTEINER que o port faz, e o achado do bloco 3
  depende dela. }
function BlocosDeclarados(const caminho: string): Integer;

implementation

function LeBloco(f: TFileStream; posicao: Int64; var destino;
                 quantos: Integer): Boolean;
begin
  Result := False;
  if posicao + quantos > f.Size then
    Exit;
  f.Position := posicao;
  Result := f.Read(destino, quantos) = quantos;
end;

function LeCartaoDeMemoria(const caminho: string;
                           out cartao: TCartaoDeMemoria): Boolean;
var
  f: TFileStream;
  j: Integer;
begin
  Result := False;
  FillChar(cartao, SizeOf(cartao), 0);
  if not FileExists(caminho) then
    Exit;
  try
    f := TFileStream.Create(caminho, fmOpenRead or fmShareDenyNone);
  except
    Exit;
  end;
  try
    if f.Size <> CARTAO_BYTES then
      Exit;
    { Nomes e atributos saem do MESMO registro de 32 bytes, e a ordem dentro
      dele e atributo primeiro. O original faz dois lacos separados, cada um
      com o seu `fseek` de passo; aqui e um laco so por campo, pela mesma
      razao de o resultado ser identico e a conta ser mais curta. }
    for j := 0 to JOGADORES_NO_CARTAO - 1 do
      if not LeBloco(f, MCR_JOGADORES + MCR_JOGADOR_PASSO * j,
                     cartao.atributos[j * MCR_ATRIBUTO_BYTES],
                     MCR_ATRIBUTO_BYTES) then
        Exit;
    for j := 0 to JOGADORES_NO_CARTAO - 1 do
      if not LeBloco(f, MCR_JOGADORES + MCR_ATRIBUTO_BYTES
                        + MCR_JOGADOR_PASSO * j,
                     cartao.nomes[j * MCR_NOME_BYTES], MCR_NOME_BYTES) then
        Exit;
    if not LeBloco(f, MCR_NUMEROS, cartao.numeros[0], NUMEROS_BYTES) then
      Exit;
    { A formacao sai PARTIDA e volta contigua: 10 bytes de um lugar, 20 de
      outro, e no buffer eles se encostam. O corte e depois do decimo, e no
      original ele e um teste dentro do proprio laco de 30. }
    if not LeBloco(f, MCR_FORMACAO_1, cartao.formacao[0], 10) then
      Exit;
    if not LeBloco(f, MCR_FORMACAO_2, cartao.formacao[10], 20) then
      Exit;
    for j := 0 to High(MCR_COBRADORES) do
      if not LeBloco(f, MCR_COBRADORES[j], cartao.cobradores[j], 1) then
        Exit;
    if not LeBloco(f, MCR_CAPITAO, cartao.cobradores[COBRADORES_BYTES - 1], 1)
    then
      Exit;
    Result := True;
  finally
    f.Free;
  end;
end;

function NumeroDoCartao(const cartao: TCartaoDeMemoria; j: Integer): Integer;
var
  grupo, dentro, bit, byte_ini, valor: Integer;
begin
  Result := 0;
  if (j < 0) or (j >= JOGADORES_NO_CARTAO) then
    Exit;
  grupo := j div 6;
  dentro := j mod 6;
  bit := (5 * dentro) mod 8;
  byte_ini := grupo * 4 + (5 * dentro) div 8;
  { Dois bytes bastam: `bit + 5 <= 12`, entao o valor nunca atravessa mais de
    uma fronteira. E a mesma conta do `0x00403278` do original, que recebe o
    par (baixo, alto) e devolve `comprimento` bits a partir de `deslocamento`. }
  valor := cartao.numeros[byte_ini];
  if byte_ini + 1 <= High(cartao.numeros) then
    valor := valor or (cartao.numeros[byte_ini + 1] shl 8);
  Result := ((valor shr bit) and $1F) + 1;
end;

function LeTaticaDoCartao(const caminho: string;
                          out tatica: TTaticaDoCartao): Boolean;
var
  f: TFileStream;
  cru, b1_baixo, b1_alto, b2_baixo, b2_alto: Byte;
begin
  Result := False;
  FillChar(tatica, SizeOf(tatica), 0);
  if not FileExists(caminho) then
    Exit;
  try
    f := TFileStream.Create(caminho, fmOpenRead or fmShareDenyNone);
  except
    Exit;
  end;
  try
    if f.Size <> CARTAO_BYTES then
      Exit;
    if not LeBloco(f, MCR_TATICA_CRUA, cru, 1) then Exit;
    if not LeBloco(f, MCR_TATICA_1_BAIXO, b1_baixo, 1) then Exit;
    if not LeBloco(f, MCR_TATICA_1_ALTO, b1_alto, 1) then Exit;
    if not LeBloco(f, MCR_TATICA_2_BAIXO, b2_baixo, 1) then Exit;
    if not LeBloco(f, MCR_TATICA_2_ALTO, b2_alto, 1) then Exit;
    tatica[0] := cru;
    tatica[1] := (b1_baixo and $0F) or ((b1_alto and $0F) shl 4);
    tatica[2] := (b2_baixo and $0F) or ((b2_alto and $0F) shl 4);
    Result := True;
  finally
    f.Free;
  end;
end;

function BlocosDeclarados(const caminho: string): Integer;
var
  f: TFileStream;
  quadro: array[0 .. 127] of Byte;
  i: Integer;
begin
  Result := 0;
  if not FileExists(caminho) then
    Exit;
  try
    f := TFileStream.Create(caminho, fmOpenRead or fmShareDenyNone);
  except
    Exit;
  end;
  try
    if f.Size < CARTAO_BLOCO then
      Exit;
    f.Position := 0;
    if f.Read(quadro, 2) <> 2 then
      Exit;
    if (quadro[0] <> Ord('M')) or (quadro[1] <> Ord('C')) then
      Exit;
    { Os quadros 1..15 descrevem os blocos 1..15. O nibble alto do byte 0
      separa em uso (`0x5x`) de livre (`0xAx`); e a documentacao publica do
      formato, nao inferencia. }
    for i := 1 to 15 do
    begin
      f.Position := i * 128;
      if f.Read(quadro, SizeOf(quadro)) <> SizeOf(quadro) then
        Exit;
      if (quadro[0] and $F0) = $50 then
        Inc(Result);
    end;
  finally
    f.Free;
  end;
end;

end.
