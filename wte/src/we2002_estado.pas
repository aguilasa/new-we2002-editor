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
  SysUtils, we2002_database, we2002_cdimage, we2002_offsets;

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

  { A geometria MODE2/2352, escrita uma vez. O `PATCH_SALTO` acima e
    `SETOR_BYTES - SETOR_DADOS`, e continua com o proprio nome porque e o
    salto que o patch de arranque da entre um setor e o seguinte. }
  SETOR_BYTES         = 2352;
  SETOR_DADOS_INICIO  = 24;
  SETOR_DADOS         = 2048;

var
  { A imagem carregada. Vazio enquanto nenhuma foi aberta. }
  Jogo: TDatabase;
  ImagemAberta: string = '';

  { O arquivo de textura escolhido pelo `boton_dialogo_texClick`, e o tamanho
    dele -- os globais `0x00432e60` (o `FILE*`) e `0x00434598` (o tamanho) do
    original. Aqui e caminho e nao descritor: o port abre e fecha por operacao,
    e quem grava e o `boton_tex2isoClick`.

    AFORDANCIA DE HARNESS, e da mesma familia do argumento de imagem: o lado
    port do gate nao consegue digitar num `TOpenDialog` do gtk2 por coordenada
    fixa, entao `WTE_TEXTURA` semeia este par no `FormShow`. Nao muda byte
    nenhum -- muda por onde o caminho entra. }
  TexturaEscolhida: string = '';
  TexturaTamanho: Int64 = 0;

  { O caminho do `.mcr` que o `grabar_memoryClick` vai emitir.

    Mesma afordancia, mesmo motivo -- e aqui ela e ainda mais necessaria: o
    `TSaveDialog` do gtk2 tem de receber um nome DIGITADO, e o `:99` nao entrega
    tecla ao GTK2 sem gerenciador de janela. `WTE_MCR` semeia o destino no
    `FormShow`; com ele preenchido o handler pula o `Execute` e vai direto ao
    arquivo, que e o mesmo que o oraculo recebe pelo dialogo. }
  CartaoDestino: string = '';

  { O caminho do uniforme que o `grabar_camisetaClick` vai extrair.

    Terceiro membro da mesma familia, e pela mesma razao que o `CartaoDestino`:
    `TSaveDialog` do gtk2 quer nome DIGITADO. `WTE_UNI` semeia o destino no
    `FormShow`. }
  UniformeDestino: string = '';

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
    5 (WTE-TASK-28, 32); aqui elas so existem e sao montadas na mesma ordem. }
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

{ OS DOIS REMENDOS LITERAIS DO ARRANQUE, e eles NAO sao a injecao acima.

  Ate 2026-08-20 as duas faixas que eles gravam eram as unicas do arranque
  **sem explicacao**: `1921862..1921862` e `2012984..2012985` apareciam em todo
  `cmp` do gate, o oraculo as gravava, o port nao, e os roteiros as declaravam
  `conhecida:`. A WTE-TASK-33 deu significado a segunda; esta achou os autores,
  e eles estavam escondidos a plena vista -- o endereco e IMEDIATO no `.text`,
  entao procurar por `OFS_LINK_ML` nunca os encontraria.

  Os dois ficam FORA da guarda da sentinela: o `je` de `0x0041158e`, que pula a
  injecao quando a imagem ja foi injetada, salta para `0x00411616`, que e onde
  eles comecam. Ou seja rodam em toda abertura, injetando ou nao.

  `PATCH_VINCULO_POS` e um CONSERTO DE DADO, e da para ver o que ele conserta:
  o par `(102, 23)` do slot 13 do clube de ML 5 aponta para um bloco do time
  102, e o time 102 nao tem jogador non-contract nenhum -- e referencia
  pendurada. O remendo a manda para `(0, 27)`, que e o bloco 4. A condicao
  (`b0 = 102` e `b1 > 22`) o torna idempotente: depois de gravado `b0` vale 0 e
  ele nao dispara de novo.

  `PATCH_BYTE_SOLTO_POS` grava zero, sem condicao, e o que ele significa
  **continua sem resposta** -- e um byte no setor 817, dentro do payload, sem
  offset nomeado por perto (o mais proximo e o `OFS_FLAG_SHAPE_COPY_1`, 7142
  bytes adiante). Portar sem saber o significado e legitimo porque a
  especificacao esta completa: endereco fixo, sem condicao, valor zero. O que
  nao se pode e inventar um nome para ele.

  E ELES NAO ESTAO NO MESMO LUGAR. O `FormShow` (`0x00411616`) faz os dois; o
  `boton_dialogo_weClick` (`0x0040c19e`) faz **so** o do vinculo. Por isso o do
  vinculo mora no `AbreImagem`, que os dois caminhos usam, e o do byte solto e
  chamado do corpo do `FormShow`. }
const
  PATCH_BYTE_SOLTO_POS = 1921862;   { `0x001d5346`, gravado com zero        }
  PATCH_VINCULO_POS    = 2012984;   { `0x001eb738`, o par de vinculo        }
  PATCH_VINCULO_DE_B0  = 102;       { so dispara se o par for (102, >22)    }
  PATCH_VINCULO_DE_B1  = 22;        { estritamente maior                    }

{ O remendo do par de vinculo. True quando gravou. }
function PatchDeVinculoDeArranque(const imagem: string): Boolean;

{ O zero em `1921862`. Sempre grava; o valor ja estar zero e o caso normal. }
procedure PatchDeByteSoltoDeArranque(const imagem: string);

{ Abre a imagem: injeta o patch, aplica o remendo do vinculo e carrega o banco.
  False quando nao da para abrir o arquivo. }
function AbreImagem(const caminho: string): Boolean;

{ ------------------------------------------------------------------------ }
{ A GRAVACAO -- WTE-TASK-27.

  O original mantem um `FILE*` aberto o tempo todo (`0x00432e58`) e grava por
  ele. O port abre, grava e fecha a cada operacao, e a diferenca NAO aparece
  no gate: o que o `golden_check.sh` compara e o arquivo, e o arquivo recebe
  os mesmos bytes no mesmo offset.

  A diferenca que aparece e a oposta, e favorece o port: a saida do runtime C
  e bufferizada, entao o clique no original nao produz syscall nenhuma -- os
  bytes ficam no buffer ate algo depois procurar noutro ponto do mesmo
  arquivo. Medido em `wte/re/gravacao-controle.md` com um par de sondas. Aqui
  o `Close` esvazia na hora, e por isso todo roteiro de gravacao do lado
  ORACULO tem de terminar com uma acao que force a descarga -- senao o gate
  compara um oraculo truncado com um port inteiro. }

{ Endereco absoluto de um indice de byte no fluxo de DADOS DE USUARIO, contado
  a partir do primeiro byte de dados do setor `setor_base`.

  E a aritmetica MODE2/2352 que o `wte.exe` escreve a mao em cada gravacao:
  2352 = 24 de cabecalho + 2048 de dados + 280 de EDC/ECC, e o indice logico
  ignora os 304 que nao sao dados. Escrita uma vez aqui em vez de repetida em
  cada handler; o original a repete. }
function EnderecoDeDados(setor_base, indice_logico: TOffset): TOffset;

{ Grava `count` bytes em `offset` na imagem aberta. False quando nao ha imagem
  aberta ou nao da para abrir o arquivo.

  NAO recalcula EDC/ECC -- preservar e o comportamento do original, e do
  `we2002_core`. }
function GravaNaImagem(offset: TOffset; const buffer; count: SizeInt): Boolean;

{ O FLUXO DE DADOS -- a leitura e a gravacao sequenciais do original.

  O `wte.exe` trata a imagem como um fluxo continuo de dados de usuario e
  mantem o salto de setor a mao: depois de CADA byte, se a posicao chegou ao
  fim da regiao de dados (byte 2072 do setor), ele pula 304 -- os 280 de
  EDC/ECC mais os 24 de cabecalho do setor seguinte. E a rotina `0x00403388`,
  chamada por todo laco de leitura e de gravacao dele.

  Sem isso, um nome que atravessa fronteira de setor sairia gravado por cima do
  EDC/ECC. Com isso, o formato MODE2/2352 fica invisivel para quem chama. }
procedure SaltaFronteiraDeSetor(var img: TCdImage);

{ Um byte do fluxo, com o salto aplicado depois. False no fim do arquivo. }
function LeDoFluxo(var img: TCdImage; out b: Byte): Boolean;

{ Grava `count` bytes pelo FLUXO, a partir de `offset`. Mesma semantica do
  `0x00403400` do original: `Seek` absoluto e um byte de cada vez, com o salto
  entre eles. }
function GravaNoFluxo(var img: TCdImage; offset: TOffset;
                      const buffer; count: SizeInt): Boolean;

{ Le `count` bytes pelo FLUXO, a partir de `offset`. O simetrico do
  `GravaNoFluxo`, e a forma do `0x004033bc` do original. False quando o arquivo
  acaba antes -- e ai o que ja se leu fica no buffer, como no original. }
function LeDoFluxoEm(var img: TCdImage; offset: TOffset;
                     out buffer; count: SizeInt): Boolean;

{ Tamanho de um arquivo, ou 0 quando nao da para abrir. }
function TamanhoDoArquivo(const caminho: string): Int64;

{ ------------------------------------------------------------------------ }
{ O time e o jogador que a ficha esta editando -- as globais `0x004335cc` e
  `0x004335dc` do original.

  MORAVAM no `.aux.inc` do `MainForm` ate a decima segunda passagem da
  WTE-TASK-26, e mudaram de casa porque deixaram de ser estado de um
  formulario so: quem as enche e a navegacao do `MainForm`, quem as consome
  passou a ser o `jugador`. O `uses` que os 18 `ep2002_*` recebem sai na
  INTERFACE, entao `ep2002_jugador` nao pode usar `ep2002_mainform` -- seria
  referencia circular. Estado compartilhado por dois formularios mora aqui,
  que e o que o cabecalho desta unidade diz. }
var
  TimeEmEdicao: Integer = -1;
  JogadorEmEdicao: Integer = -1;

const
  { Os dois times cujos jogadores NAO tem o campo condicional na imagem.

    Medido nos dois oraculos, por caminhos independentes, e eles concordam: o
    `0x00404374` do `wte.exe` zera a coluna de offset quando o indice do time
    cai entre 0x35 e 0x38 exclusive -- 54 ou 55 --, e o `we2002_database.pas`
    pula os 46 jogadores 1704..1749 ao carregar `cost`, que e exatamente
    `462 + 54*23` ate `462 + 56*23 - 1`. Os dois primeiros times all-star. }
  TIMES_SEM_CONDICIONAL = [54, 55];

{ O jogador do slot tem o campo condicional na imagem?

  E a condicao `DWORD[0x00433614 + 44*buffer] <> 0` do original, que a setima
  passagem da WTE-TASK-26 identificou como a terceira coluna de offsets do
  buffer de jogador. Quando ela e zero, a ficha mostra o literal 50 no campo e
  o controle nasce desabilitado, e o `casilla_dorsalKeyPress` nao move o foco
  para la.

  Para clube de Master League o indice que decide e o do time RESOLVIDO pelo
  par de vinculo, nao o do clube -- por isso o parametro e o par (time, slot)
  e nao so o time. }
function JogadorTemCampoCondicional(indice, slot: Integer): Boolean;

implementation

uses
  Classes, wte_datafiles;

{ A REGRA MORA NO `wte_datafiles` desde a WTE-TASK-39, e este corpo virou
  encaminhamento. O nome fica aqui porque quatro chamadores o usam e porque a
  raiz e estado de execucao como qualquer outro desta unidade; o que saiu foi
  a ORDEM DE BUSCA, que passou a ser a mesma do log de trace -- e ela ganhou
  um candidato, o prefixo instalado (`../share/we2002Lazarus`), sem o qual a
  arvore instalada nao acharia os assets. }
function RaizDosAssets: string;
begin
  Result := wte_datafiles.RaizDosAssets;
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

function PatchDeVinculoDeArranque(const imagem: string): Boolean;
var
  img: TCdImage;
  b0, b1: Byte;
  par: array[0..1] of Byte;
begin
  Result := False;
  img.Init;
  if not img.OpenReadWrite(imagem) then
    Exit;
  try
    img.Seek(PATCH_VINCULO_POS, soBeginning);
    { O original le os dois bytes com `fgetc` cru, sem o salto de fronteira de
      setor -- e pode, porque o par inteiro cabe no payload do setor 855. }
    if img.Read(b0, 1) <> 1 then
      Exit;
    if b0 <> PATCH_VINCULO_DE_B0 then
      Exit;
    if img.Read(b1, 1) <> 1 then
      Exit;
    if b1 <= PATCH_VINCULO_DE_B1 then
      Exit;
    par[0] := 0;
    par[1] := 27;
    img.Seek(PATCH_VINCULO_POS, soBeginning);
    img.Write(par[0], 2);
    Result := True;
  finally
    img.Close;
  end;
end;

procedure PatchDeByteSoltoDeArranque(const imagem: string);
var
  img: TCdImage;
  zero: Byte;
begin
  img.Init;
  if not img.OpenReadWrite(imagem) then
    Exit;
  try
    img.Seek(PATCH_BYTE_SOLTO_POS, soBeginning);
    zero := 0;
    img.Write(zero, 1);
  finally
    img.Close;
  end;
end;

function JogadorTemCampoCondicional(indice, slot: Integer): Boolean;
var
  vinculo: PByte;
  resolvido: Byte;
begin
  Result := False;
  if (indice < 0) or (slot < 0) or (slot > 22) then
    Exit;
  if indice < 63 then
    resolvido := Byte(indice)
  else
  begin
    if indice < 95 then
      vinculo := @Jogo.ml_teams[indice - 63].link[slot * 2]
    else
      vinculo := @Jogo.ml_default.link[slot * 2];
    { Segundo byte >= 23 e bloco proprio do clube: o campo existe sempre. }
    if vinculo[1] >= 23 then
    begin
      Result := True;
      Exit;
    end;
    resolvido := vinculo[0];
  end;
  Result := not (resolvido in TIMES_SEM_CONDICIONAL);
end;

function EnderecoDeDados(setor_base, indice_logico: TOffset): TOffset;
begin
  Result := setor_base * SETOR_BYTES + SETOR_DADOS_INICIO
          + (indice_logico div SETOR_DADOS) * SETOR_BYTES
          + (indice_logico mod SETOR_DADOS);
end;

function GravaNaImagem(offset: TOffset; const buffer; count: SizeInt): Boolean;
var
  img: TCdImage;
begin
  Result := False;
  if (ImagemAberta = '') or (count <= 0) then
    Exit;
  img.Init;
  if not img.OpenReadWrite(ImagemAberta) then
    Exit;
  try
    img.Seek(offset, soBeginning);
    img.Write(buffer, count);
    Result := True;
  finally
    img.Close;
  end;
end;

procedure SaltaFronteiraDeSetor(var img: TCdImage);
begin
  if (img.Tell mod SETOR_BYTES) = (SETOR_DADOS_INICIO + SETOR_DADOS) then
    img.Seek(SETOR_BYTES - SETOR_DADOS, soCurrent);
end;

function LeDoFluxo(var img: TCdImage; out b: Byte): Boolean;
begin
  b := 0;
  Result := img.Read(b, 1) = 1;
  if Result then
    SaltaFronteiraDeSetor(img);
end;

function GravaNoFluxo(var img: TCdImage; offset: TOffset;
                      const buffer; count: SizeInt): Boolean;
var
  bytes: PByte;
  i: SizeInt;
begin
  Result := False;
  if count <= 0 then
    Exit;
  bytes := @buffer;
  img.Seek(offset, soBeginning);
  for i := 0 to count - 1 do
  begin
    img.Write(bytes[i], 1);
    SaltaFronteiraDeSetor(img);
  end;
  Result := True;
end;

function LeDoFluxoEm(var img: TCdImage; offset: TOffset;
                     out buffer; count: SizeInt): Boolean;
var
  bytes: PByte;
  i: SizeInt;
begin
  Result := False;
  if count <= 0 then
    Exit;
  bytes := @buffer;
  FillChar(buffer, count, 0);
  img.Seek(offset, soBeginning);
  for i := 0 to count - 1 do
    if not LeDoFluxo(img, bytes[i]) then
      Exit;
  Result := True;
end;

function TamanhoDoArquivo(const caminho: string): Int64;
var
  f: TFileStream;
begin
  Result := 0;
  if not FileExists(caminho) then
    Exit;
  try
    f := TFileStream.Create(caminho, fmOpenRead or fmShareDenyNone);
    try
      Result := f.Size;
    finally
      f.Free;
    end;
  except
    Result := 0;
  end;
end;

function AbreImagem(const caminho: string): Boolean;
begin
  Result := False;
  if not FileExists(caminho) then
    Exit;
  InjetaPatchDeArranque(caminho);
  { ANTES do `Load`, e a ordem importa: o remendo muda um par de vinculo, e o
    modelo em memoria tem de ver o par consertado. No original a questao nao
    existe -- ele rele a imagem a cada troca de time. }
  PatchDeVinculoDeArranque(caminho);
  Jogo.Init;
  Result := Jogo.Load(caminho, nil);
  if Result then
    ImagemAberta := caminho
  else
    ImagemAberta := '';
end;

end.
