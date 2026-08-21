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
  we2002_render;

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

    **NADA NESTE PORT AINDA LE ESTES DOIS BYTES**, e isso e a metade portada de
    uma divergencia ja registrada: o unico consumidor no original e a gravacao
    do `BitBtn3`, que copia o slot 1 para o slot 0 e o grava. O par tambem nao
    tem campo na camada de dados -- nem `TTeam` nem `TMlTeam` guardam padrao de
    camisa --, e e por isso que o `MainForm.colorearClick` deixa o combo no
    default em vez de inventar de onde ele sai. Ver a spec daquele handler. }
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

implementation

uses
  we2002_estado, we2002_types;

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

type
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
