{ Prova o `we2002_bmp` -- o recipiente de 8 bpp da WTE-TASK-29.

  Tres grupos, e o primeiro e o que impede o modo de falhar mais feio:

  1. **a recusa.** A mecanica do original ASSUME um cabecalho de 54 bytes e uma
     paleta de 256 entradas, e nao confere nada -- ele manda `fseek(0x36)` e
     escreve. Um `.bmp` de outra forma faria a troca de paleta acertar o lugar
     errado. O port confere, e cada teste aqui e um jeito diferente de o
     arquivo estar errado;
  2. **a troca de paleta.** A ordem `B, G, R`, o byte reservado que NAO se
     escreve, e o limite: 16 na bandeira, 15 no uniforme. A entrada 15 tem de
     sobreviver a uma troca de 15;
  3. **o pixel.** Linha de baixo primeiro e alinhamento em quatro bytes -- os
     dois detalhes que ficam presos aqui para nao vazarem para quem desenha.

  E o grupo 4 e opcional: `WTE_TEST_BMP` aponta um arquivo REAL da pasta do
  usuario. Sem ele o teste diz PULADO em vez de mentir que passou.

  Cada linha de saida e `OK<TAB>nome` ou `FALHA<TAB>nome<TAB>detalhe`.
  Rodado por: wte/tools/test_dump_render2d.py }

program test_bmp;

{$mode objfpc}{$H+}

uses
  SysUtils, Classes, we2002_render, we2002_bmp;

var
  falhas: LongInt = 0;
  casos: LongInt = 0;

procedure Checa(const nome: string; ok: Boolean; const detalhe: string = '');
begin
  Inc(casos);
  if ok then
    WriteLn('OK'#9, nome)
  else
  begin
    WriteLn('FALHA'#9, nome, #9, detalhe);
    Inc(falhas);
  end;
end;

procedure PoeLongInt(var bmp: TBmp8; posicao: Integer; valor: LongInt);
begin
  bmp.dados[posicao] := Byte(valor);
  bmp.dados[posicao + 1] := Byte(valor shr 8);
  bmp.dados[posicao + 2] := Byte(valor shr 16);
  bmp.dados[posicao + 3] := Byte(valor shr 24);
end;

{ Um bitmap sintetico com a forma que a mecanica exige. Os pixels recebem o
  proprio indice de coluna, para que a leitura de pixel tenha o que conferir. }
function Sintetico(largura, altura: Integer): TBmp8;
var
  x, y, linha: Integer;
begin
  Result.largura := largura;
  Result.altura := altura;
  SetLength(Result.dados, BMP_DADOS + BytesPorLinha(largura) * altura);
  FillChar(Result.dados[0], Length(Result.dados), 0);
  Result.dados[0] := Byte(BMP_ASSINATURA and $FF);
  Result.dados[1] := Byte(BMP_ASSINATURA shr 8);
  PoeLongInt(Result, 2, Length(Result.dados));
  PoeLongInt(Result, 10, BMP_DADOS);
  PoeLongInt(Result, 14, BMP_INFO_BYTES);
  PoeLongInt(Result, 18, largura);
  PoeLongInt(Result, 22, altura);
  Result.dados[26] := 1;                       { planos }
  Result.dados[28] := BMP_BITS;
  PoeLongInt(Result, 30, BMP_SEM_COMPRESSAO);
  { Linha 0 do ARQUIVO e a de baixo da imagem: o pixel guarda `y` de tela. }
  for y := 0 to altura - 1 do
  begin
    linha := altura - 1 - y;
    for x := 0 to largura - 1 do
      Result.dados[BMP_DADOS + linha * BytesPorLinha(largura) + x] :=
        Byte(y * 16 + x);
  end;
end;

procedure ARecusa;
var
  bmp: TBmp8;
begin
  bmp := Sintetico(20, 16);
  Checa('o sintetico passa', ValidaBmp8(bmp));

  bmp := Sintetico(20, 16);
  bmp.dados[1] := Ord('X');
  Checa('assinatura errada e recusada', not ValidaBmp8(bmp));

  bmp := Sintetico(20, 16);
  bmp.dados[28] := 24;
  Checa('24 bpp e recusado', not ValidaBmp8(bmp),
        'e o unico erro que quebraria o 0x36 sem parecer erro');

  { O `bfOffBits` e o mais perigoso: o original NAO o le. }
  bmp := Sintetico(20, 16);
  PoeLongInt(bmp, 10, BMP_DADOS + 4);
  Checa('pixel comecando noutro lugar e recusado', not ValidaBmp8(bmp));

  bmp := Sintetico(20, 16);
  PoeLongInt(bmp, 30, 1);
  Checa('bitmap comprimido e recusado', not ValidaBmp8(bmp));

  bmp := Sintetico(20, 16);
  PoeLongInt(bmp, 14, 12);
  Checa('cabecalho de informacao do OS/2 e recusado', not ValidaBmp8(bmp));

  bmp := Sintetico(20, 16);
  SetLength(bmp.dados, BMP_DADOS + 4);
  Checa('arquivo curto demais para os pixels e recusado', not ValidaBmp8(bmp));

  bmp.dados := nil;
  Checa('buffer vazio e recusado', not ValidaBmp8(bmp));

  { A derivacao que o `dump_render2d.py` nao consegue ler, executada aqui. }
  Checa('BMP_DADOS e o cabecalho mais a paleta inteira',
        BMP_DADOS = BMP_CABECALHO + BMP_PALETA_ENTRADAS * BMP_ENTRADA_BYTES,
        Format('%d', [BMP_DADOS]));
end;

procedure ATrocaDePaleta;
var
  bmp: TBmp8;
  cores: array[0 .. 15] of TCorBgr555;
  e: TEntradaDePaleta;
  i: Integer;
begin
  bmp := Sintetico(20, 16);
  for i := 0 to 15 do
    cores[i] := CodificaCor(i, 31 - i, 16);
  { Marca o byte reservado das duas primeiras entradas: ele TEM de sobreviver. }
  bmp.dados[OffsetDaEntrada(0) + 3] := $AB;
  bmp.dados[OffsetDaEntrada(1) + 3] := $CD;
  AplicaPaleta(bmp, cores, PRIMEIRA_BANDEIRA, PALETA_BANDEIRA);

  e := EntradaCrua(bmp, 0);
  Checa('a entrada 0 sai na ordem B, G, R',
        (e[0] = 16 shl 3) and (e[1] = 31 shl 3) and (e[2] = 0),
        Format('%d,%d,%d', [e[0], e[1], e[2]]));
  Checa('o byte reservado nao e tocado',
        (bmp.dados[OffsetDaEntrada(0) + 3] = $AB)
        and (bmp.dados[OffsetDaEntrada(1) + 3] = $CD),
        'o original o pula com fseek(+1); zerar seria invencao do port');

  e := EntradaCrua(bmp, 15);
  Checa('a entrada 15 e escrita quando sao 16',
        e[2] = 15 shl 3, Format('%d', [e[2]]));

  { O uniforme: 15 entradas A PARTIR DA PALAVRA 1. As duas pontas importam --
    a decima sexta ENTRADA do arquivo nao e tocada, e a palavra 0 das cores
    nao e lida. Escrever `cores[0..14]` daria uma tela colorida e errada, que
    e o modo de falhar que este teste existe para pegar. }
  bmp := Sintetico(20, 16);
  bmp.dados[OffsetDaEntrada(15)] := $11;
  bmp.dados[OffsetDaEntrada(15) + 1] := $22;
  bmp.dados[OffsetDaEntrada(15) + 2] := $33;
  AplicaPaleta(bmp, cores, PRIMEIRA_UNIFORME, PALETA_UNIFORME);
  e := EntradaCrua(bmp, 15);
  Checa('com 15 a decima sexta ENTRADA sobrevive',
        (e[0] = $11) and (e[1] = $22) and (e[2] = $33),
        Format('%d,%d,%d -- a assimetria bandeira/uniforme e do original',
               [e[0], e[1], e[2]]));
  e := EntradaCrua(bmp, 0);
  Checa('e a entrada 0 recebe a palavra 1, e nao a 0',
        e[2] = 1 shl 3, Format('%d -- deveria ser a cor de indice 1',
                               [e[2] shr 3]));
  e := EntradaCrua(bmp, 14);
  Checa('a decima quinta entrada recebe a palavra 15',
        e[2] = 15 shl 3, Format('%d', [e[2] shr 3]));

  { E a bandeira NAO pula: entrada 0 recebe palavra 0. Se as duas comecassem
    no mesmo lugar, a constante nao teria razao de existir. }
  bmp := Sintetico(20, 16);
  AplicaPaleta(bmp, cores, PRIMEIRA_BANDEIRA, PALETA_BANDEIRA);
  Checa('a bandeira comeca na palavra 0',
        EntradaCrua(bmp, 0)[2] = 0, 'e a do uniforme comeca na 1');
  Checa('e as duas primeiras nao comecam no mesmo lugar',
        PRIMEIRA_BANDEIRA <> PRIMEIRA_UNIFORME);

  { Pedir mais do que se tem nao estoura -- o parametro e limitado ao vetor. }
  bmp := Sintetico(20, 16);
  AplicaPaleta(bmp, cores, 0, 300);
  e := EntradaCrua(bmp, 15);
  Checa('pedir 300 de um vetor de 16 nao estoura', e[2] = 15 shl 3);
  e := EntradaCrua(bmp, 16);
  Checa('e nao escreve alem do vetor',
        (e[0] = 0) and (e[1] = 0) and (e[2] = 0));

  Checa('entrada fora da paleta devolve zero',
        (EntradaCrua(bmp, 256)[0] = 0) and (EntradaCrua(bmp, -1)[0] = 0));
end;

procedure OPixel;
var
  bmp: TBmp8;
begin
  { 20 divide por 4; 21 nao, e e ai que o alinhamento aparece. }
  Checa('linha de 20 ocupa 20 bytes', BytesPorLinha(20) = 20);
  Checa('linha de 21 ocupa 24', BytesPorLinha(21) = 24,
        Format('%d', [BytesPorLinha(21)]));
  Checa('linha de 51 ocupa 52', BytesPorLinha(51) = 52,
        Format('%d -- a camisa de clube de ML tem 51 px', [BytesPorLinha(51)]));

  bmp := Sintetico(20, 16);
  { O sintetico guarda `y * 16 + x` na coordenada de TELA. Se a unidade lesse
    de cima para baixo, o topo devolveria o valor da ultima linha. }
  Checa('o pixel do topo e o do topo', IndiceDoPixel(bmp, 0, 0) = 0,
        Format('%d', [IndiceDoPixel(bmp, 0, 0)]));
  Checa('e o de baixo e o de baixo', IndiceDoPixel(bmp, 3, 15) = 15 * 16 + 3,
        Format('%d', [IndiceDoPixel(bmp, 3, 15)]));
  Checa('fora da imagem devolve zero',
        (IndiceDoPixel(bmp, 20, 0) = 0) and (IndiceDoPixel(bmp, 0, 16) = 0)
        and (IndiceDoPixel(bmp, -1, 0) = 0));

  bmp := Sintetico(21, 3);
  Checa('com alinhamento a linha ainda comeca no lugar',
        (IndiceDoPixel(bmp, 0, 0) = 0) and (IndiceDoPixel(bmp, 0, 1) = 16)
        and (IndiceDoPixel(bmp, 0, 2) = 32),
        Format('%d,%d,%d', [IndiceDoPixel(bmp, 0, 0),
                            IndiceDoPixel(bmp, 0, 1),
                            IndiceDoPixel(bmp, 0, 2)]));
end;

{ Um arquivo de verdade da pasta do usuario, se o driver apontar um. }
procedure UmArquivoDeVerdade;
var
  caminho: string;
  bmp: TBmp8;
  cores: array[0 .. 15] of TCorBgr555;
  e: TEntradaDePaleta;
  i: Integer;
begin
  caminho := GetEnvironmentVariable('WTE_TEST_BMP');
  if caminho = '' then
  begin
    WriteLn('PULADO'#9'arquivo real'#9'sem WTE_TEST_BMP');
    Exit;
  end;
  Checa('o arquivo real carrega', CarregaBmp8(caminho, bmp), caminho);
  if Length(bmp.dados) = 0 then
    Exit;
  Checa('e traz largura e altura', (bmp.largura > 0) and (bmp.altura > 0),
        Format('%dx%d', [bmp.largura, bmp.altura]));
  for i := 0 to 15 do
    cores[i] := CodificaCor(31, 0, 0);
  AplicaPaleta(bmp, cores, PRIMEIRA_BANDEIRA, PALETA_BANDEIRA);
  e := EntradaCrua(bmp, 0);
  Checa('e aceita a troca de paleta',
        (e[0] = 0) and (e[1] = 0) and (e[2] = RENDER_MAXIMO),
        Format('%d,%d,%d', [e[0], e[1], e[2]]));
  Checa('arquivo inexistente nao carrega',
        not CarregaBmp8(caminho + '.nao-existe', bmp));
end;

begin
  ARecusa;
  ATrocaDePaleta;
  OPixel;
  UmArquivoDeVerdade;
  WriteLn('CASOS'#9, casos);
  if falhas > 0 then
    Halt(1);
end.
