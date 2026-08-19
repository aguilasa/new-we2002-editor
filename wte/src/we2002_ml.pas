{ we2002_ml -- os blocos livres de Master League (WTE-TASK-33).

  A `0x004042d4` do original, e so ela. Escrita a mao, como o
  `we2002_estado`: nao ha gerador possivel para a rotina, e o que E gerado --
  a tabela de quantos jogadores non-contract cada time tem -- entra pelo
  include `we2002_ml_tabela.inc`, produzido pelo `wte/tools/conta_ml.py`.

  O QUE E UM BLOCO LIVRE, e a resposta nao e inferencia: o `Hint` do controle
  que mostra o numero diz `Free blocks for new Master League players`, e o
  `we2002_core` nomeia o pool -- `PLAYERS_NC = 462`, os jogadores
  non-contract em `players[0..461]`, antes dos 1449 de selecao. Bloco livre e
  indice de NC que nenhum par de vinculo reivindica. Nao e byte zero nem nome
  em branco.

  A CONTA, medida em `wte/re/ml-slots.md`:

    - 760 pares lidos a partir de `OFS_LINK_ML`, pelo FLUXO (com o salto de
      fronteira de setor do `we2002_estado`);
    - o par 23 e enchimento e nao conta -- e a distancia de 48 bytes entre
      `OFS_LINK_ML` e `OFS_LINK_ML1` para 46 de conteudo;
    - par com segundo byte < 23 e VINCULO para jogador de selecao, nao bloco
      proprio, e tambem nao conta;
    - o resto vira `ML_PREFIXO[b0] + b1 - 23`, que e letra por letra o
      `slot + START_LINK[team] - 23` do `ResolveMlLink` do `we2002_core`;
    - o contador comeca em 462 e cai UMA vez por indice distinto.

  UMA DIVERGENCIA DELIBERADA, para a WTE-TASK-35. O vetor de ocupacao do
  original tem 462 palavras e o `memset` dele limpa 462 BYTES -- metade. E o
  indice pode passar de 461, e ai o `inc` do original escreve em variavel
  vizinha: e o `0x004335e4` que o `crash-causa.md` mediu sendo atropelado pela
  ROM europeia, e a causa do travamento que aquela medicao deixou sem nome.
  Aqui o vetor cobre toda a faixa alcancavel e e zerado inteiro, entao o
  NUMERO sai igual ao do original e nenhuma variavel vizinha e atingida.
  Conferido: a europeia da 13 dos dois lados. }

unit we2002_ml;

{$mode objfpc}{$H+}

interface

uses
  Classes, we2002_cdimage, we2002_estado, we2002_offsets;

{$I we2002_ml_tabela.inc}

const
  { Os imediatos da `0x004042d4`, na ordem em que ela os usa. }
  ML_BLOCOS_TOTAL = 462;   { `mov WORD ds:0x4335c0,0x1ce` em 0x004042f1     }
  ML_PARES        = 760;   { `cmp ebx,0x2f8` em 0x00404366                 }
  ML_PAR_FILLER   = 23;    { `cmp ebx,0x17 / je` em 0x0040432f             }
  ML_SLOT_MIN     = 23;    { `cmp esi,0x16 / jle` em 0x00404334            }

  { O maior indice que a formula pode produzir com a tabela definida:
    `ML_PREFIXO[119] + 255 - 23`. `b0 >= 120` NAO e modelado -- ver
    `ContaBlocosLivresDeMl`. }
  ML_INDICE_MAX = ML_BLOCOS_TOTAL + 255 - ML_SLOT_MIN;

{ Quantos blocos de Master League estao livres na imagem de `caminho`.

  Devolve `ML_BLOCOS_TOTAL` quando nao da para abrir o arquivo ou ele acaba
  antes dos 760 pares -- o mesmo que o original mostraria, porque o `fgetc`
  dele em fim de arquivo devolve -1 e o `-1 < 23` cai no ramo do vinculo.

  `fora_do_vetor` sai com quantos indices DISTINTOS passaram de 461. E o que
  separa "a imagem e do jogo" de "a imagem faz o original escrever em memoria
  alheia": zero na japonesa, 8 na europeia. }
function ContaBlocosLivresDeMl(const caminho: string;
                               out fora_do_vetor: Integer): Word; overload;
function ContaBlocosLivresDeMl(const caminho: string): Word; overload;

{ O prefixo somado, exposto porque o teste o confere contra o `START_LINK[]`
  do `we2002_core` -- as duas codificacoes da mesma tabela. }
function MlPrefixoDoTime(time: Integer): Integer;

implementation

function MlPrefixoDoTime(time: Integer): Integer;
var
  t: Integer;
begin
  { O que a `0x0040423c` refaz a cada chamada: soma `ML_NC_POR_TIME[0..t-1]`.
    O original nao guarda o prefixo pronto; o `ed.exe` guarda. }
  Result := 0;
  if time <= 0 then
    Exit;
  if time > High(ML_NC_POR_TIME) then
    time := High(ML_NC_POR_TIME) + 1;
  for t := 0 to time - 1 do
    Inc(Result, ML_NC_POR_TIME[t]);
end;

function ContaBlocosLivresDeMl(const caminho: string;
                               out fora_do_vetor: Integer): Word;
var
  img: TCdImage;
  ocupacao: array[0..ML_INDICE_MAX] of Word;
  livres, par, indice, i: Integer;
  b0, b1: Byte;
begin
  Result := ML_BLOCOS_TOTAL;
  fora_do_vetor := 0;
  if caminho = '' then
    Exit;
  img.Init;
  if not img.OpenRead(caminho) then
    Exit;
  try
    for i := 0 to High(ocupacao) do
      ocupacao[i] := 0;
    livres := ML_BLOCOS_TOTAL;
    img.Seek(OFS_LINK_ML, soBeginning);
    for par := 0 to ML_PARES - 1 do
    begin
      { O original salta UMA vez por iteracao, antes dos dois `fgetc`, e nao
        entre eles. Nao e descuido que passe: de `OFS_LINK_ML` ate o fim do
        payload do setor 855 vao 352 bytes, 176 pares exatos, entao a
        fronteira cai entre pares. Fosse impar, o segundo byte viria do
        EDC/ECC. }
      SaltaFronteiraDeSetor(img);
      if img.Read(b0, 1) <> 1 then
        Break;
      if img.Read(b1, 1) <> 1 then
        Break;
      if (par = ML_PAR_FILLER) or (b1 < ML_SLOT_MIN) then
        Continue;
      { `b0 >= 120` nao e modelado: ali o original soma alem do fim da tabela
        e o resultado depende do que a `.data` guarda depois dela. Nenhuma das
        duas ROMs chega la -- o maior `b0` medido e 43. }
      if b0 > High(ML_NC_POR_TIME) then
        Continue;
      indice := MlPrefixoDoTime(b0) + b1 - ML_SLOT_MIN;
      if (indice < 0) or (indice > High(ocupacao)) then
        Continue;
      if ocupacao[indice] = 0 then
      begin
        Dec(livres);
        if indice >= ML_BLOCOS_TOTAL then
          Inc(fora_do_vetor);
      end;
      Inc(ocupacao[indice]);
    end;
    if livres < 0 then
      livres := 0;
    Result := Word(livres);
  finally
    img.Close;
  end;
end;

function ContaBlocosLivresDeMl(const caminho: string): Word;
var
  ignorado: Integer;
begin
  Result := ContaBlocosLivresDeMl(caminho, ignorado);
end;

end.
