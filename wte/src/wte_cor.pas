{ wte_cor -- o estado do editor de cor 2D do `ficha_color`.

  ESCRITA A MAO. E a terceira unidade da WTE-TASK-29 sem LCL: a `we2002_render`
  faz a aritmetica, a `we2002_bmp` cuida do recipiente, e esta guarda O QUE
  ESTA SENDO EDITADO. Quem desenha continua sendo a `wte_render2d`.

  ELA EXISTE PORQUE A SPEC DO `ficha_color.FormCreate` ADIOU A DECISAO. Aquele
  handler zera cinco globais do original e a spec dele diz, com todas as
  letras, que escrever o corpo antes de decidir onde esse estado mora seria
  inventar. A decisao e desta task, e e esta unidade.

  OS CINCO GLOBAIS, e o que cada um e:

      0x00433dc4   familia   qual paleta se edita (0..3) -- o digito do
                             `botonN` que o `botonClick` recorta do Name
      0x00433dc8   conjunto  qual jogo dentro da familia (o `lista_col1`)
      0x00433dc0   entrada   qual das 16 cores esta selecionada, BASE ZERO
      0x00433dcc   faixa_ini o comeco da faixa do gradiente, BASE UM
      0x00433dd0   faixa_fim o fim dela, base um -- e vale 16 no arranque

  E O VETOR, que e a parte que engana: as 16 palavras ficam em
  `0x00433dd4..0x00433e10`, e o pintor de amostra escreve em
  `[indice*4 + 0x00433dd0]` com `indice` de 1 a 16. Ou seja **o `faixa_fim` e o
  elemento zero do vetor**, e nunca colide porque o pintor comeca em 1. Aqui os
  dois sao campos separados, com nome, e o alias fica so no comentario -- mas
  as bases tem de ser respeitadas: `entrada` conta de 0, `faixa_*` contam de 1.

  DUAS FAMILIAS ESTAO PORTADAS, e as outras duas estao MEDIDAS e fora:

      0  bandeira   0x00432ef4                    portada
      1  uniforme   0x00432f56 + conjunto * 32    portada
      2  chuteira   0x00433096 + conjunto * 32    medida, nao portada
      3  (quarta)   0x004331b6                    medida, nao portada

  As duas de fora sao o combo `lista_col2` -- `BOOTS TYPE`, nove itens -- e uma
  quarta paleta sem combo visivel. Nenhuma das duas e camisa nem bandeira, que
  e o titulo desta task; portar chuteira exigiria descobrir onde o dado dela
  mora na imagem, e isso e trabalho que ninguem pediu. `FonteDaPaleta` devolve
  False para elas em vez de fingir. }

unit wte_cor;

{$mode objfpc}{$H+}

interface

uses
  we2002_render, we2002_offsets, wte_blococor;

const
  { Quantas amostras o formulario tem: `color1`..`color16`. E o mesmo 16 que o
    `FormCreate` escreve no `faixa_fim`. }
  COR_AMOSTRAS = 16;

  { As quatro familias, pelo digito do `botonN`. }
  COR_FAMILIA_BANDEIRA = 0;
  COR_FAMILIA_UNIFORME = 1;
  COR_FAMILIA_CHUTEIRA = 2;
  COR_FAMILIA_QUARTA   = 3;

type
  { Os dois vetores de offset que o bloco de cor tem: as CINCO copias do byte
    de forma de bandeira e as OITO paletas de chuteira. }
  TCincoOffsets = array[0 .. 4] of TOffset;
  TOitoOffsets = array[0 .. BLOCOCOR_CHUTEIRAS - 1] of TOffset;

  { O estado do editor. Os nomes sao os do comentario de cabecalho; as bases
    tambem. }
  TCorEmEdicao = record
    familia: Integer;
    conjunto: Integer;
    entrada: Integer;              { base ZERO, 0..15 }
    faixa_ini: Integer;            { base UM, 1..16 }
    faixa_fim: Integer;            { base UM }
    cores: TCoresDoTime;           { o vetor 0x00433dd4, aqui base zero }
  end;

var
  { Uma so, como no original: os cinco globais nao sao por instancia. }
  CorEmEdicao: TCorEmEdicao;

  { O time que o editor esta editando -- o `0x004335cc` do original, escrito
    pelo `MainForm.colorearClick` a partir do `lista_equipos_1`.

    NAO E o `lista_equipos.ItemIndex` lido na hora: o original copia o indice
    UMA vez, ao abrir, e o resto do formulario le a copia. Reler o combo daria
    o mesmo hoje e deixaria de dar no dia em que algo mudasse a selecao com o
    modal aberto. }
  TimeEmCor: Integer = -1;

var
  { O par de bytes do PADRAO DE CAMISA -- `NORMAL`, `ROMBOIDAL`, `EXTRA`.

    No original sao dois bytes por slot num vetor de dois: `0x004331d6` e
    `0x004331d7` sao o slot 0 (o que o carregador le da imagem e o gravador
    devolve a ela) e `0x004331d8` / `0x004331d9` sao o slot 1, que e o que o
    `lista_col3Change` escreve. Aqui so o slot 1 tem lugar, porque so ele tem
    quem o escreva.

    **O CONSUMIDOR CHEGOU NA CORR-WTE-081**: e a `GravaBlocoDeCorNaImagem`, o
    `OK` do editor, que grava estes dois bytes junto com as outras seis
    regioes. Ate 2026-08-21 esta variavel era escrita e nunca lida, e o
    comentario dizia isso.

    E COM O CONSUMIDOR VEIO A CARGA. O literal `(0, $65)` continua sendo o
    valor de partida, mas a `CarregaBlocoDeCorDaImagem` o substitui pelo que a
    imagem traz assim que o editor abre -- o `copia_slot(0, 1)` do fim da carga
    do original. Sem isso o `OK` gravaria `00 65` por cima de qualquer outro
    padrao, e o gate nao veria: as duas ROMs deste repositorio guardam
    exatamente `00 65` ali.

    O par continua sem campo na camada de dados -- nem `TTeam` nem `TMlTeam`
    guardam padrao de camisa --, e por isso o `MainForm.colorearClick` continua
    deixando o COMBO no default: o byte tem de onde vir, o item da lista nao. }
  PadraoDaCamisa: array[0 .. 1] of Byte = (0, $65);

var
  { O COLA-CORES, e sao dois blocos independentes no original:

      0x00433e14   duas palavras? nao -- DOIS BYTES: uma cor so
      0x00433e16   32 bytes: as 16, uma paleta inteira

    Os dois sao Ctrl + botao do mouse no `colorMouseDown`, e o `Shift` decide
    qual: sem ele e uma cor, com ele sao as 16. Botao DIREITO copia, ESQUERDO
    cola. Eles nao se sobrepoem -- `0x00433e14 + 2 = 0x00433e16` --, o que quer
    dizer que copiar uma cor NAO estraga a paleta guardada, e vice-versa.

    O conteudo sobrevive a troca de familia, de time e de conjunto: e o que
    torna o recurso util, e e o que o readme do original vende. }
  CorCopiada: TCorBgr555 = 0;
  PaletaCopiada: TCoresDoTime = (0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0);

{ O que o `ficha_color.FormCreate` escreve: familia 0, conjunto 0, entrada 0,
  faixa 1..16. Nao mexe no vetor -- quem o enche e a `CarregaPaleta`. }
procedure ZeraCorEmEdicao;

{ Diz se a familia corrente tem fonte portada, e qual e.

  `False` para as familias 2 e 3, que estao medidas e fora de escopo. O
  chamador nao deve pintar amostra nenhuma nesse caso: pintar com a paleta da
  familia anterior mostraria cor plausivel e errada, que e o pior. }
function FamiliaPortada(familia: Integer): Boolean;

{ Enche `CorEmEdicao.cores` a partir do time, respeitando familia e conjunto.

  Devolve False quando a familia nao e portada ou o indice nao e um time de
  verdade; nesse caso o vetor fica como estava. }
function CarregaPaleta(indice_do_time: Integer): Boolean;

{ O caminho de volta -- a `0x00405b48`, que o original chama de QUATORZE
  lugares e que este port chamava de nenhum ate a sexta passagem.

  Ela grava as 16 palavras de `CorEmEdicao.cores` de volta na fonte que a
  familia e o `conjunto` correntes escolhem. E o gemeo exato da
  `CarregaPaleta`, e as duas juntas sao o unico caminho entre o vetor de
  edicao e o dado.

  ONDE ELA GRAVA, E POR QUE ISSO E UMA DECISAO. No original o destino e o
  **slot 1** -- o rascunho que o carregador de time copia do slot 0 e que o
  `ficha_color` edita. Aqui o destino e o `Jogo`, porque e o `Jogo` que faz o
  papel de "estado carregado" deste port: e dele que a tela do `MainForm`
  desenha, e e ele que uma releitura da imagem descarta. O slot 0 do original
  -- a copia intocada, que o `BitBtn1` restaura -- nao tem equivalente aqui, e
  quem precisar dele e o desfazer, que ainda nao foi portado.

  **Nao toca a imagem de CD.** Nenhum dos quatorze chamadores toca: gravar e o
  `BitBtn3`, e o `BitBtn3` chama esta rotina ANTES de gravar, nao no lugar de.

  Devolve False, sem escrever nada, quando a familia nao e portada ou o indice
  nao e um time de verdade -- as mesmas duas recusas da `CarregaPaleta`. }
function SalvaPaleta(indice_do_time: Integer): Boolean;

{ As 16 palavras que ESTAO valendo para um time, por familia e conjunto --
  independente do que o editor tem no vetor.

  E a leitura que as duas rotinas de desenho fazem (`0x00432ef4` para a
  bandeira, `0x00432f56 + conjunto*32` para o uniforme). Devolve tudo zero para
  familia nao portada ou indice invalido, e quem chama confere antes. }
function CoresEmVigor(indice_do_time, familia, conjunto: Integer): TCoresDoTime;

{ A forma de bandeira em vigor -- o byte `0x00432f15` do original.

  O desenhista da bandeira (`0x00405270`) NAO le a forma do time: le esta
  copia, e o `lista_col0Change` a reescreve. Aqui ela mora no mesmo lugar que
  o resto do estado editado, pela mesma razao da `SalvaPaleta`: e
  `Jogo.teams[].flag_shape` / `Jogo.ml_teams[].flag_shape`.

  Devolve False se o indice nao for um time de verdade. }
function SalvaFormaDaBandeira(indice_do_time, forma: Integer): Boolean;

{ ... e a leitura dela. Devolve -1 se o indice nao for um time de verdade. }
function FormaEmVigor(indice_do_time: Integer): Integer;

{ O SLOT 0 -- a copia intocada que o `ficha_color.BitBtn1` restaura.

  Chegou na WTE-TASK-30, e o cabecalho da `SalvaPaleta` acima ja tinha escrito
  por que ele faltava: *"o slot 0 do original -- a copia intocada, que o
  `BitBtn1` restaura -- nao tem equivalente aqui, e quem precisar dele e o
  desfazer, que ainda nao foi portado"*. O desfazer sao os dois botoes de baixo
  do editor de cor, e sao estes dois procedimentos.

  O QUE ENTRA NA FOTO e o que a `0x00404F90` do original copia entre slots, na
  parte que este port tem campo para guardar: as cores da bandeira, os dois
  jogos de uniforme, a forma da bandeira e o par de bytes do padrao de camisa.
  As duas familias nao portadas -- chuteira e quarta paleta -- ficam de fora
  porque a camada de dados nao as tem, e nao ha o que restaurar no que ninguem
  edita: a `SalvaPaleta` recusa familia nao portada.

  ONDE A FOTO E TIRADA, e por que e equivalente sem ser igual. No original o
  slot 0 e refeito a CADA TROCA DE TIME, pela carga (`0x004050F0` le da imagem,
  `0x00405198` espelha no slot 1). Aqui ela sai no `MainForm.colorearClick`,
  imediatamente antes do `ShowModal`. A diferenca so apareceria se o time
  mudasse com o editor aberto, e ele e MODAL: nao muda.

  A foto guarda o indice junto. `RestauraOriginal` devolve False -- sem mexer em
  nada -- se for chamada para outro time ou sem foto: restaurar a cor de um time
  em cima de outro e o unico estrago que esta dupla poderia fazer. }
procedure GuardaOriginal(indice_do_time: Integer);
function RestauraOriginal(indice_do_time: Integer): Boolean;

{ AS PALETAS DE BANDEIRA QUE O `we2002_core` NAO CARREGA (CORR-WTE-083).

  Dez slots ficam com dezesseis zeros depois do `Database.Load`, e zero na
  paleta e PRETO: `teams[56..63]`, `ml_teams[5]` (`HIGHLANDS`) e `ml_teams[22]`
  (`EMILIA`). Sete deles sao os times `CLASSIC`; o `teams[63]` nao tem nome e
  nenhum item do combo o alcanca.

  A CAUSA E DE ALCANCE, NAO DE DEFEITO. O laco nacional do `we2002_core` para
  em 55 e o bloco de Master League e uma lista de indices que pula o 5, o 6, o
  22 e o 23. Para o `ed.exe` isso nunca foi problema: ele nao desenha bandeira
  nenhuma, e paleta que ele nao desenha ele nao precisa ler. O `wte.exe`
  desenha, e le a cor de todos pela tabela de offsets de `.data` -- a mesma que
  o `wte_blococor` extrai.

  POR QUE ELA MORA AQUI E NAO NO GERADOR DA CAMADA DE DADOS. Estender o laco
  transpilado faria o port divergir do `we2002_core` na CARGA, e o
  `compare_dumps.py` compara os dois dumps byte a byte -- ele reprovaria por
  construcao. A §4.5 do plano ja dizia de quem e cada metade: a camada de dados
  e do `we2002_core`, e o que o Obocaman le a mais e do Obocaman. Esta rotina e
  chamada por quem ABRE a imagem no app, depois do `Load`, e o
  `dump_estado.pas` -- que chama o `Load` direto -- nao a ve.

  O CRITERIO E "O CORE DEIXOU ZERADO", e ele nao e chute: medido nas duas ROMs,
  85 dos 95 slots batem exatamente entre a carga do core e a tabela do
  Obocaman, dez estao zerados, e UM diverge de proposito -- o `teams[39]`, que
  o core le de outro ponto do arquivo (o caso `36, 39, 47` do laco). Preencher
  so o que esta zerado nunca passa por cima do que o core leu, e e por isso que
  o 39 fica intocado.

  Devolve quantos slots preencheu. }
function CarregaBandeirasQueOCoreNaoLe: Integer;

{ A CARGA DO QUE O MODELO NAO GUARDA -- a parte do `0x004050D0` que este port
  nao tinha.

  Tres das sete regioes do bloco de cor nao tem campo na camada de dados: as
  oito paletas de chuteira, a quarta paleta e o par de bytes do padrao de
  camisa. O `MainForm.colorearClick` chama esta rotina imediatamente antes de
  abrir o editor, que e onde o original as le -- a carga dele roda a cada troca
  de time, e o editor e modal.

  ELA E O QUE TORNA A GRAVACAO POSSIVEL. Sem os bytes lidos, devolve-los
  intactos seria impossivel: pular os 288 + 32 gravaria menos que o original, e
  gravar zeros corromperia a imagem.

  E ELA TAMBEM ESPELHA O SLOT 0 NO SLOT 1, como o `0x00405198` faz no fim da
  carga (`copia_slot(0, 1)`): `PadraoDaCamisa` passa a valer o que a imagem
  diz, em vez do literal com que nasce. Sem isso o `OK` gravaria `00 65` por
  cima de qualquer outro padrao que a imagem tivesse -- e o gate so nao veria
  porque as duas ROMs deste repositorio guardam `00 65` ali.

  False quando nao ha imagem aberta, o indice nao e time, ou a leitura nao
  completa. }
function CarregaBlocoDeCorDaImagem(indice_do_time: Integer): Boolean;

{ ONDE MORA, NA IMAGEM, CADA UMA DAS SETE REGIOES DO BLOCO DE COR.

  E o `0x00404E70` do original, que enche sete globais de offset a cada troca
  de time; a carga (`0x004050D0`) e a gravacao (`0x004051A4`) leem as mesmas
  sete. Os numeros e a tabela de 95 bytes vem do `wte_blococor`, que os extrai
  do `.exe` e os confere contra oito `OFS_*` do `we2002_core`.

  Devolve False para indice que nao e time de verdade. }
function OffsetsDoBlocoDeCor(indice_do_time: Integer;
                             out bandeira: TOffset;
                             out forma: TCincoOffsets;
                             out uniforme0, uniforme1: TOffset;
                             out chuteira: TOitoOffsets;
                             out quarta, padrao: TOffset): Boolean;

{ A GRAVACAO DO BLOCO DE COR -- a `0x004051A4`, 383 bytes por time.

  E a setima rota de escrita na imagem, e o unico chamador dela e o
  `ficha_color.BitBtn3Click` (medido: um `call`, em `0x004069F9`). Espelha a
  carga bloco por bloco, com DUAS assimetrias que sao do original:

  1. **le 32 e grava 30** em quatro das sete regioes -- bandeira, os dois
     uniformes e a quarta paleta. A ultima palavra de cada paleta e carregada e
     nunca devolvida. Gravar 32 mudaria byte que o original nunca muda;
  2. **a forma da bandeira e lida de um offset e gravada em cinco.** A carga usa
     a copia do meio; a gravacao percorre as cinco. O byte mora replicado.

  As chuteiras (8 x 32) e o par de padrao de camisa (2) sao simetricos.

  AS DUAS FAMILIAS NAO PORTADAS SAEM DA FOTO. Chuteira e quarta paleta nao tem
  campo na camada de dados; a `GuardaOriginal` as le da imagem e esta rotina as
  devolve intactas. Pular os 288 + 32 bytes gravaria menos que o original;
  gravar zeros corromperia a imagem.

  Devolve False sem tocar em nada quando nao ha imagem aberta, quando o indice
  nao e time, ou quando a foto e de outro time -- gravar chuteira de um time
  em cima de outro e o unico estrago que esta rotina poderia fazer. }
function GravaBlocoDeCorNaImagem(indice_do_time: Integer): Boolean;

implementation

uses
  we2002_estado, we2002_types, we2002_cdimage;

procedure ZeraCorEmEdicao;
begin
  CorEmEdicao.familia := COR_FAMILIA_BANDEIRA;
  CorEmEdicao.conjunto := 0;
  CorEmEdicao.entrada := 0;
  { 1 e 16, e nao 0 e 15: a faixa do gradiente conta de UM, porque o vetor do
    original comeca no elemento 1. }
  CorEmEdicao.faixa_ini := 1;
  CorEmEdicao.faixa_fim := COR_AMOSTRAS;
end;

function FamiliaPortada(familia: Integer): Boolean;
begin
  Result := (familia = COR_FAMILIA_BANDEIRA) or (familia = COR_FAMILIA_UNIFORME);
end;

function CoresEmVigor(indice_do_time, familia, conjunto: Integer): TCoresDoTime;
var
  ml: Integer;
begin
  FillChar(Result, SizeOf(Result), 0);
  if not FamiliaPortada(familia) then
    Exit;
  if (indice_do_time < 0)
     or (indice_do_time >= TEAMS_NATIONAL_ALLSTAR + TEAMS_ML) then
    Exit;
  ml := indice_do_time - TEAMS_NATIONAL_ALLSTAR;
  if familia = COR_FAMILIA_BANDEIRA then
  begin
    if ml < 0 then
      Result := Jogo.teams[indice_do_time].flag_colours
    else
      Result := Jogo.ml_teams[ml].flag_colours;
  end
  else if ml < 0 then
  begin
    if conjunto = 0 then
      Result := Jogo.teams[indice_do_time].home_kit
    else
      Result := Jogo.teams[indice_do_time].away_kit;
  end
  else
  begin
    if conjunto = 0 then
      Result := Jogo.ml_teams[ml].home_kit
    else
      Result := Jogo.ml_teams[ml].away_kit;
  end;
end;

function FormaEmVigor(indice_do_time: Integer): Integer;
begin
  Result := -1;
  if (indice_do_time < 0)
     or (indice_do_time >= TEAMS_NATIONAL_ALLSTAR + TEAMS_ML) then
    Exit;
  if indice_do_time < TEAMS_NATIONAL_ALLSTAR then
    Result := Jogo.teams[indice_do_time].flag_shape
  else
    Result := Jogo.ml_teams[indice_do_time - TEAMS_NATIONAL_ALLSTAR].flag_shape;
end;

function CarregaPaleta(indice_do_time: Integer): Boolean;
begin
  Result := False;
  if not FamiliaPortada(CorEmEdicao.familia) then
    Exit;
  { `TEAMS_NATIONAL_ALLSTAR + TEAMS_ML` = 95, o mesmo `IDX_MODELO_ML` que o
    `.aux.inc` do MainForm declara. Aqui as duas parcelas vem da camada de
    dados em vez de um 95 escrito de novo: o item 95 do combo e o time-modelo
    da Master League, e ele nao tem paleta. }
  if (indice_do_time < 0)
     or (indice_do_time >= TEAMS_NATIONAL_ALLSTAR + TEAMS_ML) then
    Exit;

  { O `conjunto` e o item do `lista_col1` -- `Primeiro` ou `Segundo`, e so a
    familia de uniforme o consulta. }
  CorEmEdicao.cores := CoresEmVigor(indice_do_time, CorEmEdicao.familia,
                                    CorEmEdicao.conjunto);
  Result := True;
end;

function SalvaPaleta(indice_do_time: Integer): Boolean;
begin
  Result := False;
  if not FamiliaPortada(CorEmEdicao.familia) then
    Exit;
  if (indice_do_time < 0)
     or (indice_do_time >= TEAMS_NATIONAL_ALLSTAR + TEAMS_ML) then
    Exit;

  if CorEmEdicao.familia = COR_FAMILIA_BANDEIRA then
  begin
    if indice_do_time < TEAMS_NATIONAL_ALLSTAR then
      Jogo.teams[indice_do_time].flag_colours := CorEmEdicao.cores
    else
      Jogo.ml_teams[indice_do_time - TEAMS_NATIONAL_ALLSTAR].flag_colours :=
        CorEmEdicao.cores;
  end
  else
  begin
    if indice_do_time < TEAMS_NATIONAL_ALLSTAR then
    begin
      if CorEmEdicao.conjunto = 0 then
        Jogo.teams[indice_do_time].home_kit := CorEmEdicao.cores
      else
        Jogo.teams[indice_do_time].away_kit := CorEmEdicao.cores;
    end
    else
    begin
      if CorEmEdicao.conjunto = 0 then
        Jogo.ml_teams[indice_do_time - TEAMS_NATIONAL_ALLSTAR].home_kit :=
          CorEmEdicao.cores
      else
        Jogo.ml_teams[indice_do_time - TEAMS_NATIONAL_ALLSTAR].away_kit :=
          CorEmEdicao.cores;
    end;
  end;
  Result := True;
end;

function SalvaFormaDaBandeira(indice_do_time, forma: Integer): Boolean;
begin
  Result := False;
  if (indice_do_time < 0)
     or (indice_do_time >= TEAMS_NATIONAL_ALLSTAR + TEAMS_ML) then
    Exit;
  if indice_do_time < TEAMS_NATIONAL_ALLSTAR then
    Jogo.teams[indice_do_time].flag_shape := ShortInt(forma)
  else
    Jogo.ml_teams[indice_do_time - TEAMS_NATIONAL_ALLSTAR].flag_shape :=
      ShortInt(forma);
  Result := True;
end;

const
  { Os tamanhos do bloco de cor, do `0x004051A4`. `LIDOS` e o que a carga le,
    `GRAVADOS` e o que a gravacao devolve -- e os dois nao sao iguais nas
    quatro paletas, que e a primeira assimetria. }
  PALETA_BYTES_LIDOS   = 32;
  PALETA_BYTES_GRAVADOS = 30;
  PADRAO_BYTES         = 2;

type
  TPaletaCrua = array[0 .. PALETA_BYTES_LIDOS - 1] of Byte;

  TFotoDoTime = record
    valida: Boolean;
    indice: Integer;
    bandeira: TCoresDoTime;
    uniforme: array[0 .. 1] of TCoresDoTime;
    forma: Integer;
    padrao: array[0 .. 1] of Byte;
  end;

var
  Foto: TFotoDoTime;

  { AS DUAS FAMILIAS NAO PORTADAS, cruas, como a imagem as tem.

    Nao ha campo para elas na camada de dados e NAO HA QUEM AS EDITE -- a
    `SalvaPaleta` recusa familia nao portada. Por isso elas nao precisam do par
    slot 0 / slot 1 que o resto do bloco tem: uma copia so, lida na carga e
    devolvida na gravacao, faz o mesmo papel.

    `CruasIndice` guarda de quem sao. A gravacao confere, e se recusa: devolver
    chuteira de um time em cima de outro seria o unico estrago que a
    `GravaBlocoDeCorNaImagem` poderia fazer. }
  ChuteiraCrua: array[0 .. BLOCOCOR_CHUTEIRAS - 1] of TPaletaCrua;
  QuartaCrua: TPaletaCrua;
  CruasValidas: Boolean = False;
  CruasIndice: Integer = -1;

function CarregaBandeirasQueOCoreNaoLe: Integer;
var
  img: TCdImage;
  bandeira, uniforme0, uniforme1, quarta, padrao: TOffset;
  forma: TCincoOffsets;
  chuteira: TOitoOffsets;
  cru: TPaletaCrua;
  cores: TCoresDoTime;
  idx, i, ml: Integer;
  zerada: Boolean;
begin
  Result := 0;
  if ImagemAberta = '' then
    Exit;

  img.Init;
  if not img.OpenRead(ImagemAberta) then
    Exit;
  try
    for idx := 0 to BLOCOCOR_TIMES - 1 do
    begin
      cores := CoresEmVigor(idx, COR_FAMILIA_BANDEIRA, 0);
      zerada := True;
      for i := Low(cores) to High(cores) do
        if cores[i] <> 0 then
        begin
          zerada := False;
          Break;
        end;
      if not zerada then
        Continue;

      if not OffsetsDoBlocoDeCor(idx, bandeira, forma, uniforme0, uniforme1,
                                 chuteira, quarta, padrao) then
        Continue;
      if not LeDoFluxoEm(img, bandeira, cru, PALETA_BYTES_LIDOS) then
        Continue;
      for i := Low(cores) to High(cores) do
        cores[i] := TCorBgr555(cru[2 * i] or (cru[2 * i + 1] shl 8));

      ml := idx - TEAMS_NATIONAL_ALLSTAR;
      if ml < 0 then
        Jogo.teams[idx].flag_colours := cores
      else
        Jogo.ml_teams[ml].flag_colours := cores;
      Inc(Result);
    end;
  finally
    img.Close;
  end;
end;

function CarregaBlocoDeCorDaImagem(indice_do_time: Integer): Boolean;
var
  img: TCdImage;
  bandeira, uniforme0, uniforme1, quarta, padrao: TOffset;
  forma: TCincoOffsets;
  chuteira: TOitoOffsets;
  par: array[0 .. 1] of Byte;
  n: Integer;
begin
  Result := False;
  CruasValidas := False;
  CruasIndice := -1;
  if ImagemAberta = '' then
    Exit;
  if not OffsetsDoBlocoDeCor(indice_do_time, bandeira, forma,
                             uniforme0, uniforme1, chuteira, quarta,
                             padrao) then
    Exit;
  img.Init;
  if not img.OpenRead(ImagemAberta) then
    Exit;
  try
    for n := 0 to BLOCOCOR_CHUTEIRAS - 1 do
      if not LeDoFluxoEm(img, chuteira[n], ChuteiraCrua[n],
                         PALETA_BYTES_LIDOS) then
        Exit;
    if not LeDoFluxoEm(img, quarta, QuartaCrua, PALETA_BYTES_LIDOS) then
      Exit;
    if not LeDoFluxoEm(img, padrao, par, PADRAO_BYTES) then
      Exit;
  finally
    img.Close;
  end;
  { O `copia_slot(0, 1)` do fim da carga: o slot 1, que e o que o combo de
    padrao escreve e o que o `OK` grava, nasce valendo o que a imagem diz. }
  PadraoDaCamisa[0] := par[0];
  PadraoDaCamisa[1] := par[1];
  CruasValidas := True;
  CruasIndice := indice_do_time;
  Result := True;
end;

procedure GuardaOriginal(indice_do_time: Integer);
begin
  Foto.valida := False;
  if (indice_do_time < 0)
     or (indice_do_time >= TEAMS_NATIONAL_ALLSTAR + TEAMS_ML) then
    Exit;
  Foto.indice := indice_do_time;
  Foto.bandeira := CoresEmVigor(indice_do_time, COR_FAMILIA_BANDEIRA, 0);
  Foto.uniforme[0] := CoresEmVigor(indice_do_time, COR_FAMILIA_UNIFORME, 0);
  Foto.uniforme[1] := CoresEmVigor(indice_do_time, COR_FAMILIA_UNIFORME, 1);
  Foto.forma := FormaEmVigor(indice_do_time);
  Foto.padrao[0] := PadraoDaCamisa[0];
  Foto.padrao[1] := PadraoDaCamisa[1];
  Foto.valida := True;
end;

function OffsetsDoBlocoDeCor(indice_do_time: Integer;
                             out bandeira: TOffset;
                             out forma: TCincoOffsets;
                             out uniforme0, uniforme1: TOffset;
                             out chuteira: TOitoOffsets;
                             out quarta, padrao: TOffset): Boolean;

  { A conta do `0x00404E70`: indice logico no fluxo de dados -> offset
    absoluto. Ver o cabecalho do `wte_blococor`. }
  function Absoluto(logico, base: TOffset): TOffset;
  begin
    Result := logico + BLOCOCOR_SALTO * (logico div BLOCOCOR_DADOS) + base;
  end;

var
  i: Integer;
  logico: TOffset;
begin
  Result := False;
  if (indice_do_time < 0) or (indice_do_time >= BLOCOCOR_TIMES) then
    Exit;

  { O time 36 tem ramo proprio -- o `cmp eax,0x24` --, e a tabela guarda 255
    nele justamente porque ele nao a usa. }
  if indice_do_time = BLOCOCOR_TIME_SENEGAL then
    logico := BLOCOCOR_LOG_SENEGAL
  else
    logico := BLOCOCOR_LOG_BANDEIRA
              + PALETA_BYTES_LIDOS * PALETA_DA_BANDEIRA[indice_do_time];
  bandeira := Absoluto(logico, BLOCOCOR_BASE_PALETA);

  { As cinco copias sao offset ABSOLUTO mais o indice do time -- um byte por
    time, sem conversao. }
  for i := 0 to High(forma) do
    forma[i] := FORMA_DA_BANDEIRA[i] + indice_do_time;

  uniforme0 := Absoluto(BLOCOCOR_LOG_UNIFORME0
                        + BLOCOCOR_PASSO_UNIFORME * indice_do_time,
                        BLOCOCOR_BASE_UNIFORME);
  uniforme1 := Absoluto(BLOCOCOR_LOG_UNIFORME1
                        + BLOCOCOR_PASSO_UNIFORME * indice_do_time,
                        BLOCOCOR_BASE_UNIFORME);

  { As oito chuteiras e a quarta paleta NAO dependem do time: sao as mesmas
    para todos, e por isso o editor de cor mexe nelas para o jogo inteiro. }
  for i := 0 to BLOCOCOR_CHUTEIRAS - 1 do
    chuteira[i] := Absoluto(BLOCOCOR_LOG_CHUTEIRA + PALETA_BYTES_LIDOS * i,
                            BLOCOCOR_BASE_PALETA);
  quarta := BLOCOCOR_QUARTA_PALETA;
  padrao := BLOCOCOR_PADRAO_CAMISA;
  Result := True;
end;

function GravaBlocoDeCorNaImagem(indice_do_time: Integer): Boolean;
var
  img: TCdImage;
  bandeira, uniforme0, uniforme1, quarta, padrao: TOffset;
  forma: TCincoOffsets;
  chuteira: TOitoOffsets;
  cores: TCoresDoTime;
  b: Byte;
  i: Integer;
begin
  Result := False;
  if ImagemAberta = '' then
    Exit;
  if (not CruasValidas) or (CruasIndice <> indice_do_time) then
    Exit;
  if not OffsetsDoBlocoDeCor(indice_do_time, bandeira, forma,
                             uniforme0, uniforme1, chuteira, quarta,
                             padrao) then
    Exit;

  img.Init;
  if not img.OpenReadWrite(ImagemAberta) then
    Exit;
  try
    { A ordem e a do original. Ela nao muda byte nenhum -- as sete regioes nao
      se tocam --, e fica igual porque um diff de trace comparado com o do
      oraculo e mais facil de ler assim. }
    cores := CoresEmVigor(indice_do_time, COR_FAMILIA_BANDEIRA, 0);
    GravaNoFluxo(img, bandeira, cores[0], PALETA_BYTES_GRAVADOS);

    b := Byte(FormaEmVigor(indice_do_time));
    for i := 0 to High(forma) do
      GravaNoFluxo(img, forma[i], b, 1);

    { O UNIFORME COMECA NA SEGUNDA PALAVRA, e a bandeira nao. O offset que o
      `0x00404E70` calcula para o uniforme e `OFS_KIT_PREVIEW + 2`, ou seja o
      elemento 1 do vetor de 16 que o `we2002_database` carrega -- a palavra
      zero fica de fora da gravacao e vale `0000` na imagem.

      E o mesmo `cores[1..15]` que a `wte_render2d` ja usava para desenhar, e a
      mesma assimetria que o `render2d.md` mediu por outro caminho: 16 cores na
      bandeira, 15 no uniforme. Gravar a partir de `cores[0]` desloca os 30
      bytes em uma palavra e estraga o uniforme inteiro -- foi o que o
      `golden-16` mediu antes desta linha existir, 44 bytes de diferenca em
      `OFS_KIT_PREVIEW+130`. }
    cores := CoresEmVigor(indice_do_time, COR_FAMILIA_UNIFORME, 0);
    GravaNoFluxo(img, uniforme0, cores[1], PALETA_BYTES_GRAVADOS);
    cores := CoresEmVigor(indice_do_time, COR_FAMILIA_UNIFORME, 1);
    GravaNoFluxo(img, uniforme1, cores[1], PALETA_BYTES_GRAVADOS);

    { Chuteira: 32 gravados contra 32 lidos, e nao 30. Simetrica. }
    for i := 0 to BLOCOCOR_CHUTEIRAS - 1 do
      GravaNoFluxo(img, chuteira[i], ChuteiraCrua[i][0],
                   PALETA_BYTES_LIDOS);

    GravaNoFluxo(img, quarta, QuartaCrua[0], PALETA_BYTES_GRAVADOS);
    GravaNoFluxo(img, padrao, PadraoDaCamisa[0], PADRAO_BYTES);
  finally
    img.Close;
  end;
  Result := True;
end;

function RestauraOriginal(indice_do_time: Integer): Boolean;
begin
  Result := False;
  if not Foto.valida then
    Exit;
  if Foto.indice <> indice_do_time then
    Exit;
  if indice_do_time < TEAMS_NATIONAL_ALLSTAR then
  begin
    Jogo.teams[indice_do_time].flag_colours := Foto.bandeira;
    Jogo.teams[indice_do_time].home_kit := Foto.uniforme[0];
    Jogo.teams[indice_do_time].away_kit := Foto.uniforme[1];
    Jogo.teams[indice_do_time].flag_shape := ShortInt(Foto.forma);
  end
  else
  begin
    Jogo.ml_teams[indice_do_time - TEAMS_NATIONAL_ALLSTAR].flag_colours :=
      Foto.bandeira;
    Jogo.ml_teams[indice_do_time - TEAMS_NATIONAL_ALLSTAR].home_kit :=
      Foto.uniforme[0];
    Jogo.ml_teams[indice_do_time - TEAMS_NATIONAL_ALLSTAR].away_kit :=
      Foto.uniforme[1];
    Jogo.ml_teams[indice_do_time - TEAMS_NATIONAL_ALLSTAR].flag_shape :=
      ShortInt(Foto.forma);
  end;
  PadraoDaCamisa[0] := Foto.padrao[0];
  PadraoDaCamisa[1] := Foto.padrao[1];
  Result := True;
end;

initialization
  ZeraCorEmEdicao;
end.
