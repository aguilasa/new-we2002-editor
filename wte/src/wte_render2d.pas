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
  Classes, Controls, ExtCtrls, we2002_render;

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

{ Pinta as 16 amostras do editor de cor -- a `0x00405bc8` e a `0x00405d6c`.

  `dono` e o formulario que tem os `TLabel` chamados `color1`..`color16`. O
  original os acha por NOME (`FindComponent('color' + IntToStr(n))`, com a
  string `color` literal em `0x00424838`) e nao por vetor de ponteiro, e aqui e
  a mesma busca -- pela mesma razao que o `Bind<T>` do `newWe2002` existe: nome
  que nao casa tem de falhar dizendo qual, em vez de virar ponteiro nulo tres
  quadros adiante.

  A COR DA AMOSTRA E `TColor`, e a conversao nao e livre: `R or (G shl 8) or
  (B shl 16)`, que e o `$00BBGGRR` do Delphi. Montar na outra ordem daria
  vermelho no lugar de azul em toda amostra, e e o unico erro desta rotina que
  se ve.

  A rotina recebe o formulario em vez de conhece-lo: assim ela nao depende da
  unidade do `ficha_color`, e os dois chamadores -- o proprio formulario e o
  `MainForm.colorearClick` -- a alcancam sem ciclo de `uses`. }
procedure PintaAmostras(dono: TComponent; const cores: TCoresDoTime);

{ Uma amostra so -- a `0x00405bc8`, chamada de cinco lugares.

  Ela faz TRES coisas, e sao tres de proposito: guarda a palavra no vetor de
  edicao, pinta a amostra `color<indice>`, e -- SE `indice` for a amostra
  selecionada -- move as tres barras de R, G e B para os cinco bits de cada
  canal. `indice` conta de UM, como no original.

  A TERCEIRA E A QUE SURPREENDE, e ela tambem existe no original: escrever
  `Position` num `TScrollBar` dispara `OnChange` nos DOIS widgetsets (a VCL
  chama `Change` dentro do proprio `SetPosition`), entao pintar a amostra
  selecionada faz o `barraChange` rodar tres vezes. As duas primeiras veem
  canal novo com os outros dois velhos e gravam cor intermediaria; a terceira
  fecha certo. O estado final e o mesmo com ou sem o disparo, e e por isso que
  nenhum chamador depende dele.

  O `indice` da amostra selecionada NAO e o parametro: e o sufixo do `Name` do
  `TLabel`, relido com `Copy(Name, 6, 2)`, como o original faz. Os dois
  coincidem sempre; ler o nome e o que mantem a rotina indiferente a quem
  chamou. }
procedure PintaUmaAmostra(dono: TComponent; indice: Integer;
                          palavra: TCorBgr555);

{ Carrega a paleta do time pela familia corrente e pinta as 16.

  Devolve False sem pintar nada quando a familia nao e portada (ver
  `FamiliaPortada` na `wte_cor`) ou o indice nao e um time de verdade. O
  original pinta de qualquer jeito: com a familia fora de 0..3 ele cai no laco
  com o ponteiro de fonte NAO INICIALIZADO. Reproduzir isso seria reproduzir
  comportamento indefinido, que nao e comportamento. }
function PreencheAmostras(dono: TComponent; indice_do_time: Integer): Boolean;

{ Repinta as 16 a partir do VETOR de edicao, sem reler o time -- a
  `0x00405d6c` quando ela e chamada depois de o vetor ja ter sido mexido.

  Diferente da `PreencheAmostras`, que comeca recarregando do `Jogo`. }
procedure RepintaAmostras(dono: TComponent);

{ Os tres `TImage` do `MainForm` que o editor de cor redesenha, registrados
  uma vez.

  ELES NAO SAO PARAMETRO POR UM MOTIVO DE ESTRUTURA, e nao de gosto. As duas
  rotinas de desenho do original (`0x00405270` e `0x004056c8`) sao globais que
  leem globais: o `ficha_color` as chama sem saber que existe um `MainForm`.
  Em Pascal a mesma chamada exigiria `ep2002_color` usar `ep2002_mainform`, que
  ja usa `ep2002_color` -- ciclo de `uses` de interface, que nao compila.
  Registrar os tres aqui poe a indirecao no mesmo lugar onde o original ja a
  tinha. }
procedure RegistraImagensDoEditor(bandeira, camisa, calcao: TImage);

{ A `0x00405270`: redesenha a bandeira em vigor -- forma e cores do time que o
  editor esta editando. Devolve False se nao houver imagem registrada ou time
  em edicao. }
function RedesenhaBandeiraEmVigor: Boolean;

{ A `0x004056c8` chamada de dentro do editor: redesenha camisa e calcao do
  jogo `qual`, com as cores que a `SalvaPaleta` acabou de gravar. }
function RedesenhaUniformeEmVigor(qual: Integer): Boolean;

{ Esquece os arquivos ja lidos. Existe para o caso de alguem trocar a pasta de
  assets com o app aberto -- o original enxergaria a troca, e sem isto o port
  nao enxergaria. }
procedure EsqueceOsBitmaps;

implementation

uses
  SysUtils, Graphics, StdCtrls, IntfGraphics, GraphType, FPImage,
  we2002_bmp, we2002_estado, wte_uniformes, wte_cor;

var
  { Cache de arquivo lido, chaveado pelo caminho. Cresce ate 105 camisas + 6
    calcoes + 53 bandeiras; sao ~400 KB no pior caso, e na pratica o usuario
    passa por uma duzia. }
  cache: TStringList = nil;

  { Os tres `TImage` do `MainForm`, registrados pelo `FormCreate` dele. Ver
    `RegistraImagensDoEditor`. }
  img_bandeira: TImage = nil;
  img_camisa: TImage = nil;
  img_calcao: TImage = nil;

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

procedure PintaAmostras(dono: TComponent; const cores: TCoresDoTime);
var
  i: Integer;
  alvo: TComponent;
  canais: TCanais;
begin
  if dono = nil then
    Exit;
  for i := 1 to COR_AMOSTRAS do
  begin
    alvo := dono.FindComponent('color' + IntToStr(i));
    if not (alvo is TControl) then
      Continue;
    canais := DecodificaCor(cores[i - 1]);
    { `Transparent := False` ANTES da cor, e nao e gosto: o `TLabel` da LCL
      desenha transparente por default e o proprio `Color` nao aparece. Com ele
      ligado as 16 amostras somem no fundo do formulario -- medido no `:98` na
      quinta passagem da WTE-TASK-29, com a janela aberta e nenhuma amostra
      visivel. A VCL de 2002 nao tinha a propriedade separada. }
    if alvo is TLabel then
      TLabel(alvo).Transparent := False;
    TControl(alvo).Color := TColor(LongInt(canais[0])
                                   or (LongInt(canais[1]) shl 8)
                                   or (LongInt(canais[2]) shl 16));
  end;
end;

procedure PintaUmaAmostra(dono: TComponent; indice: Integer;
                          palavra: TCorBgr555);
var
  alvo: TComponent;
  canais: TCanais;
  sufixo: Integer;

  { As tres barras do editor, por nome. O original as alcanca por campo
    (`[this+0x348]`, `+0x34c`, `+0x350`); aqui e `FindComponent`, pelo mesmo
    motivo das amostras -- esta unidade nao conhece a classe do formulario. }
  procedure Barra(const nome: string; valor: Integer);
  var
    c: TComponent;
  begin
    c := dono.FindComponent(nome);
    if c is TScrollBar then
      TScrollBar(c).Position := valor;
  end;

begin
  if dono = nil then
    Exit;
  if (indice < 1) or (indice > COR_AMOSTRAS) then
    Exit;
  { O vetor de edicao recebe a palavra ANTES da tinta. E a ordem do original, e
    ela importa: o disparo de `OnChange` das barras, la embaixo, le o vetor. }
  CorEmEdicao.cores[indice - 1] := palavra;

  alvo := dono.FindComponent('color' + IntToStr(indice));
  if not (alvo is TControl) then
    Exit;
  canais := DecodificaCor(palavra);
  { `Transparent := False` ANTES da cor -- ver a nota na `PintaAmostras`. }
  if alvo is TLabel then
    TLabel(alvo).Transparent := False;
  TControl(alvo).Color := TColor(LongInt(canais[0])
                                 or (LongInt(canais[1]) shl 8)
                                 or (LongInt(canais[2]) shl 16));

  { E so a amostra SELECIONADA move as barras. O original compara o sufixo do
    `Name` com `entrada + 1`, e nao o parametro -- os dois sao iguais, e ler o
    nome e o que mantem a rotina indiferente a quem chamou. }
  sufixo := StrToIntDef(Copy(TComponent(alvo).Name, 6, 2), -1);
  if sufixo <> CorEmEdicao.entrada + 1 then
    Exit;
  Barra('barra_rojo', canais[0] shr RENDER_EXPANSAO);
  Barra('barra_verde', canais[1] shr RENDER_EXPANSAO);
  Barra('barra_azul', canais[2] shr RENDER_EXPANSAO);
end;

procedure RepintaAmostras(dono: TComponent);
var
  i: Integer;
begin
  for i := 1 to COR_AMOSTRAS do
    PintaUmaAmostra(dono, i, CorEmEdicao.cores[i - 1]);
end;

function PreencheAmostras(dono: TComponent; indice_do_time: Integer): Boolean;
begin
  Result := CarregaPaleta(indice_do_time);
  if not Result then
    Exit;
  RepintaAmostras(dono);
end;

procedure RegistraImagensDoEditor(bandeira, camisa, calcao: TImage);
begin
  img_bandeira := bandeira;
  img_camisa := camisa;
  img_calcao := calcao;
end;

function RedesenhaBandeiraEmVigor: Boolean;
var
  forma: Integer;
begin
  Result := False;
  if (img_bandeira = nil) or (TimeEmCor < 0) then
    Exit;
  forma := FormaEmVigor(TimeEmCor);
  if forma < 0 then
    Exit;
  Result := DesenhaBandeira(img_bandeira, forma, CoresEmVigor(TimeEmCor,
                            COR_FAMILIA_BANDEIRA, 0));
end;

function RedesenhaUniformeEmVigor(qual: Integer): Boolean;
begin
  Result := False;
  if (img_camisa = nil) or (img_calcao = nil) or (TimeEmCor < 0) then
    Exit;
  Result := DesenhaUniforme(img_camisa, img_calcao, TimeEmCor, qual,
                            CoresEmVigor(TimeEmCor, COR_FAMILIA_UNIFORME,
                                         qual));
end;

procedure EsqueceOsBitmaps;
begin
  FreeAndNil(cache);
end;

finalization
  FreeAndNil(cache);
end.
