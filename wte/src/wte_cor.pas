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

  if CorEmEdicao.familia = COR_FAMILIA_BANDEIRA then
  begin
    if indice_do_time < TEAMS_NATIONAL_ALLSTAR then
      CorEmEdicao.cores := Jogo.teams[indice_do_time].flag_colours
    else
      CorEmEdicao.cores :=
        Jogo.ml_teams[indice_do_time - TEAMS_NATIONAL_ALLSTAR].flag_colours;
  end
  else
  begin
    { O `conjunto` e o item do `lista_col1` -- `Primeiro` ou `Segundo`. }
    if indice_do_time < TEAMS_NATIONAL_ALLSTAR then
    begin
      if CorEmEdicao.conjunto = 0 then
        CorEmEdicao.cores := Jogo.teams[indice_do_time].home_kit
      else
        CorEmEdicao.cores := Jogo.teams[indice_do_time].away_kit;
    end
    else
    begin
      if CorEmEdicao.conjunto = 0 then
        CorEmEdicao.cores :=
          Jogo.ml_teams[indice_do_time - TEAMS_NATIONAL_ALLSTAR].home_kit
      else
        CorEmEdicao.cores :=
          Jogo.ml_teams[indice_do_time - TEAMS_NATIONAL_ALLSTAR].away_kit;
    end;
  end;
  Result := True;
end;

initialization
  ZeraCorEmEdicao;
end.
