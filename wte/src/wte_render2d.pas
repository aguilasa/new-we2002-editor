{ wte_render2d -- a bandeira e o uniforme na tela, recoloridos em memoria.

  ESCRITA A MAO. E a unica das tres unidades do render que precisa de janela:
  a `we2002_render` faz a aritmetica de cor, a `we2002_bmp` cuida do
  recipiente, e esta poe o resultado num `TImage`. A divisao existe para que as
  duas primeiras rodem no gate sem servidor X.

  O QUE ELA FAZ, e e a rotina do original com uma divergencia deliberada:

      original                          este port
      fopen(arquivo, "r+b")             le o arquivo UMA vez, para memoria
      fseek(0x36); fputc x 3 x N        troca as N entradas no buffer
      fclose
      TPicture::LoadFromFile(arquivo)   monta um TLazIntfImage e o atribui

  **O port nunca abre o `.bmp` para escrita.** A recomendacao e da secao 6.2 do
  `wte/re/assets.md` e a razao e concreta: reproduzir a gravacao tornaria o
  porte read-write numa pasta de dados que aqui e um symlink para a pasta do
  Obocaman -- e duas instancias desenhando ao mesmo tempo se atropelariam, que
  e defeito do original, nao caracteristica dele. O que se ve na tela e o
  mesmo; o que muda e o arquivo do usuario, que fica intacto.

  A SEGUNDA DIVERGENCIA, e ela e do cache: o original rele o arquivo a cada
  redesenho, porque para ele o arquivo E o estado. Aqui o arquivo e so a forma,
  entao ele e lido uma vez e guardado. Redesenhar passa a ser trocar 45 bytes e
  varrer um bitmap de 20x16 -- o que a task pede quando fala em "tempo real
  sem travar a janela".

  POR QUE `TLazIntfImage` e nao `Canvas.Pixels`: `Pixels` e uma chamada ao
  widgetset por pixel. Nestes tamanhos qualquer um dos dois serve, mas o
  criterio da task nomeia o certo, e o certo tambem e o que continua servindo
  se o desenho crescer. }

unit wte_render2d;

{$mode objfpc}{$H+}

interface

uses
  ExtCtrls, we2002_render;

{ Desenha `bandera<forma>.bmp` recolorido com as 16 palavras de `cores`.

  `forma` e o byte lido da IMAGEM DE CD, e nao a entrada da tabela
  `FORMA_PADRAO` -- a tabela alimenta o combo, o disco manda no desenho (secao
  3.2 do `assets.md`). Devolve False se o arquivo nao existir ou nao for um
  bitmap de 8 bpp com a forma que a mecanica exige; nesse caso o `TImage` fica
  como estava. }
function DesenhaBandeira(destino: TImage; forma: Integer;
                         const cores: array of TCorBgr555): Boolean;

{ Desenha a camisa e o calcao de `time` no jogo `qual` (0 = Primeiro,
  1 = Segundo), os dois com as MESMAS `cores`.

  O parametro se chama `qual` e nao `jogo` de proposito: em Pascal o
  identificador e insensivel a caixa, e `jogo` sombreia a global `Jogo` da
  `we2002_estado`. Aqui nao faria falta -- esta unidade nao le a global --, mas
  o nome combina com o do chamador, onde faz.

  As MESMAS cores nos dois arquivos nao e simplificacao: o desenhista do original monta o endereco das cores
  duas vezes com a mesma base e o mesmo passo, uma por arquivo. Um port com
  "cores da camisa" e "cores do calcao" separadas inventaria um grau de
  liberdade que o formato nao tem.

  Das 16 palavras, o desenho usa as 15 a partir da SEGUNDA -- `cores[1..15]`,
  e nao `cores[0..14]`. A palavra 0 de um bloco de uniforme e zero nos 190
  conjuntos das duas ROMs: ela nao e cor. Ver `PRIMEIRA_UNIFORME`. Devolve False se algum dos dois
  arquivos nao servir; o outro ainda e desenhado. }
function DesenhaUniforme(camisaImg, calcaoImg: TImage;
                         time, qual: Integer;
                         const cores: array of TCorBgr555): Boolean;

{ Esquece os arquivos ja lidos. Existe para o caso de alguem trocar a pasta de
  assets com o app aberto -- o original enxergaria a troca, e sem isto o port
  nao enxergaria. }
procedure EsqueceOsBitmaps;

implementation

uses
  SysUtils, Classes, Graphics, IntfGraphics, GraphType, FPImage,
  we2002_bmp, we2002_estado, wte_uniformes;

var
  { Cache de arquivo lido, chaveado pelo caminho. Cresce ate 105 camisas + 6
    calcoes + 53 bandeiras; sao ~400 KB no pior caso, e na pratica o usuario
    passa por uma duzia. }
  cache: TStringList = nil;

type
  TBmpGuardado = class
    bmp: TBmp8;
  end;

function Guardado(const caminho: string; out bmp: TBmp8): Boolean;
var
  i: Integer;
  item: TBmpGuardado;
begin
  if cache = nil then
  begin
    cache := TStringList.Create;
    cache.Sorted := True;
    cache.OwnsObjects := True;
  end;
  i := cache.IndexOf(caminho);
  if i >= 0 then
  begin
    item := TBmpGuardado(cache.Objects[i]);
    bmp := item.bmp;
    Exit(Length(bmp.dados) > 0);
  end;
  item := TBmpGuardado.Create;
  { Guarda mesmo quando falha: um arquivo ausente continua ausente, e insistir
    a cada redesenho so gastaria `stat`. }
  if not CarregaBmp8(caminho, item.bmp) then
  begin
    cache.AddObject(caminho, item);
    Exit(False);
  end;
  cache.AddObject(caminho, item);
  bmp := item.bmp;
  Result := True;
end;

{ O buffer recolorido vira um `TBitmap`, pixel a pixel, pelo indice de paleta.

  A expansao de 8 para os 16 bits do `TFPColor` e `(b shl 8) or b`: e a que
  devolve exatamente `b` quando o widgetset trunca de volta para o byte alto.
  Multiplicar por 256 perderia o valor cheio -- 248 voltaria como 247. }
procedure ParaOImage(destino: TImage; const bmp: TBmp8);
var
  intf: TLazIntfImage;
  bitmap: TBitmap;
  x, y: Integer;
  entrada: TEntradaDePaleta;
  cor: TFPColor;
begin
  intf := TLazIntfImage.Create(bmp.largura, bmp.altura);
  bitmap := TBitmap.Create;
  try
    intf.DataDescription := GetDescriptionFromDevice(0, bmp.largura,
                                                     bmp.altura);
    cor.alpha := alphaOpaque;
    for y := 0 to bmp.altura - 1 do
      for x := 0 to bmp.largura - 1 do
      begin
        entrada := EntradaCrua(bmp, IndiceDoPixel(bmp, x, y));
        { `EntradaCrua` devolve na ordem em que o arquivo guarda: B, G, R. }
        cor.blue := (Word(entrada[0]) shl 8) or entrada[0];
        cor.green := (Word(entrada[1]) shl 8) or entrada[1];
        cor.red := (Word(entrada[2]) shl 8) or entrada[2];
        intf.Colors[x, y] := cor;
      end;
    bitmap.LoadFromIntfImage(intf);
    destino.Picture.Assign(bitmap);
  finally
    bitmap.Free;
    intf.Free;
  end;
end;

function Pinta(destino: TImage; const caminho: string;
               const cores: array of TCorBgr555;
               primeira, quantas: Integer): Boolean;
var
  bmp: TBmp8;
begin
  Result := False;
  if destino = nil then
    Exit;
  if not Guardado(caminho, bmp) then
    Exit;
  { A copia e rasa: `bmp.dados` e um array dinamico, e `AplicaPaleta` escreve
    nele. Copiar de verdade antes seria desperdicio -- a paleta guardada e
    rascunho, exatamente como a do arquivo do original (secao 6.2 do
    `assets.md`), e a proxima pintura a reescreve inteira. }
  AplicaPaleta(bmp, cores, primeira, quantas);
  ParaOImage(destino, bmp);
  Result := True;
end;

function DesenhaBandeira(destino: TImage; forma: Integer;
                         const cores: array of TCorBgr555): Boolean;
begin
  Result := False;
  if (forma < 0) or (DirBanderas = '') then
    Exit;
  Result := Pinta(destino,
                  DirBanderas + DirectorySeparator
                  + 'bandera' + IntToStr(forma) + '.bmp',
                  cores, PRIMEIRA_BANDEIRA, PALETA_BANDEIRA);
end;

function DesenhaUniforme(camisaImg, calcaoImg: TImage;
                         time, qual: Integer;
                         const cores: array of TCorBgr555): Boolean;
var
  jogoDeUniforme: TJogoDeUniforme;
  raiz: string;
  okCamisa, okCalcao: Boolean;
begin
  Result := False;
  if (time < 0) or (time >= TIMES_TOTAL) or (qual < 0) or (qual > 1) then
    Exit;
  if DirUniformes2d = '' then
    Exit;
  jogoDeUniforme := UNIFORMES[time][qual];
  raiz := DirUniformes2d + DirectorySeparator;
  okCamisa := Pinta(camisaImg, raiz + 'camiseta'
                    + IntToStr(jogoDeUniforme.camisa) + '.bmp',
                    cores, PRIMEIRA_UNIFORME, PALETA_UNIFORME);
  okCalcao := Pinta(calcaoImg, raiz + 'pantalon'
                    + IntToStr(jogoDeUniforme.calcao) + '.bmp',
                    cores, PRIMEIRA_UNIFORME, PALETA_UNIFORME);
  Result := okCamisa and okCalcao;
end;

procedure EsqueceOsBitmaps;
begin
  FreeAndNil(cache);
end;

finalization
  FreeAndNil(cache);
end.
