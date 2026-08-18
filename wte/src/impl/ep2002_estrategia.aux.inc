{ Rotinas e estado internos do formulario `estrategia` -- WTE-TASK-26, decima
  oitava passagem. Ver `wte/src/impl/README.md`.

  Os seis handlers de arrastar bola compartilham cinco globais do original. Elas
  moram aqui porque um `.inc` por handler nao teria onde guarda-las, e porque
  duplicar o ajuste de grade em dois handlers e a forma de eles divergirem. }

const
  { A bola tem 15x14 no `.lfm`; o original centra com 7 nos dois eixos, tanto
    ao medir (`+7` no `bolaMouseDown`) quanto ao posicionar (`-7` no
    `rectanguloDragOver`). O par TEM de continuar batendo: e ele que faz a bola
    nao pular ao comecar o arrasto. }
  RAIO_DA_BOLA = 7;

  { A grade em que a bola cai ao ser arrastada, medida no `rectanguloDragOver`.
    O eixo X anda de 8 em 8 com FASE 5 -- ou seja, os pontos validos sao
    ...,5,13,21,... e nao ...,0,8,16,... O eixo Y anda de 5 em 5 sem fase. }
  PASSO_X = 8;
  FASE_X = 5;
  PASSO_Y = 5;

  { O rotulo `etiqjugN` acompanha a bola com este deslocamento fixo. }
  ETIQUETA_DX = -24;
  ETIQUETA_DY = 16;

  { As quatro cores do destaque, no $00BBGGRR da VCL -- que e tambem o da LCL,
    entao passam sem conversao. Escritas como $00RRGGBB elas trocariam verde
    por vermelho sem erro de compilacao. }
  VERDE_APAGADO = $00008000;   { a bola que perdeu o destaque }
  VERDE_VIVO    = $0000FF00;   { a bola sob o ponteiro }
  CINZA_CLARO   = $00C0C0C0;   { o rotulo que perdeu o destaque }
  BRANCO        = $00FFFFFF;   { o rotulo da bola sob o ponteiro }

var
  { 0x00434340 -- a bola sob o ponteiro.

    O MESMO ponteiro serve de "bola destacada" e de "bola sendo arrastada", e a
    leitura apressada veria duas coisas: o `bolaMouseMove` o move a cada
    passagem do mouse e o `bolaMouseDown` simplesmente o reusa, porque para
    apertar o botao sobre a bola o ponteiro ja passou por ela. }
  BolaEmFoco: TShape = nil;
  { 0x00434344 -- o `etiqjugN` da bola em foco. }
  EtiquetaEmFoco: TLabel = nil;

  { 0x0043434c/0x00434350 e 0x00434354/0x00434358 -- ponteiro e centro da bola,
    ambos em coordenada de TELA. O original os grava no `bolaMouseDown` e os le
    no `relojTimer`, que ainda nao foi portado. }
  PonteiroNaTela: TPoint;
  CentroDaBolaNaTela: TPoint;

  { 0x00433e54/0x00433e58 -- a posicao ja ajustada a grade, em coordenada do
    `campo`. Global no original, e nao local do handler; mantida assim. }
  GradeX: Integer = 0;
  GradeY: Integer = 0;

  { O vetor bola -> zona que o `0x00434230` do original aponta. Quem o preenche
    e o `estrategia.lista_formacionesClick`, que NAO e desta passagem: ate ele
    existir toda bola cai na zona 0. O retangulo aparece com a geometria certa
    de UMA zona, o que e visivelmente diferente de nao aparecer. }
  ZonaDaBola: array[0..10] of Byte;

{ O indice de uma bola ou de um rotulo a partir do nome do componente.

  `bola` tem quatro letras, entao o corte comeca na posicao 5 e leva dois
  caracteres -- um so corte serve `bola1` e `bola10`, porque `Copy` devolve o
  que houver. E o mesmo desenho do `jugador.flechasapaClick`. }
function IndiceDaBola(Sender: TObject): Integer;
begin
  Result := -1;
  if Sender is TComponent then
    Result := StrToIntDef(Copy(TComponent(Sender).Name, 5, 2), -1);
end;

{ O ajuste de grade do eixo X -- `0x0040967b`..`0x004096df` do original.

  Quatro ramos, e a ordem deles importa porque as faixas se tocam:

      resto = 5          -> ja esta na grade
      1 < resto < 5      -> sobe ate 5
      resto > 5          -> desce ate 5
      resto <= 1         -> desce ate o 5 ANTERIOR (tira resto + 3)

  O `mod` do Pascal segue o sinal do dividendo, igual ao `idiv` do x86 -- e a
  razao de o original precisar daquele `and 0x80000007` com correcao de sinal,
  que aqui nao tem equivalente escrito. }
function AjustaX(v: Integer): Integer;
var
  resto: Integer;
begin
  resto := v mod PASSO_X;
  if resto = FASE_X then
    Result := v
  else if (resto > 1) and (resto < FASE_X) then
    Result := v + (FASE_X - resto)
  else if resto > FASE_X then
    Result := v - (resto - FASE_X)
  else
    Result := v - (resto + 3);
end;

{ O ajuste do eixo Y -- `0x004096e0`..`0x00409719`. Sem fase: arredonda para o
  multiplo de 5 mais proximo, com o empate (resto 2) descendo. }
function AjustaY(v: Integer): Integer;
var
  resto: Integer;
begin
  resto := v mod PASSO_Y;
  if resto = 0 then
    Result := v
  else if resto > 2 then
    Result := v + (PASSO_Y - resto)
  else
    Result := v - resto;
end;

{ --------------------------------------------------------------------------
  O estado da animacao de formacao -- WTE-TASK-26, decima nona passagem.

  Trocar de formacao nao teleporta os jogadores: o `lista_formacionesClick`
  calcula um delta por bola, liga o `reloj` (Interval = 1 ms) e o
  `relojTimer` desenha QUATRO quadros. No quinto ele encaixa cada bola na
  coordenada final inteira e se desliga.

  As seis tabelas sao contiguas em `.bss`, e a contiguidade e o que confirma o
  tamanho de cada uma: 0x00434238, 0x00434264, 0x00434294, 0x004342c0,
  0x004342ec, 0x00434318 -- 0x2c (11 entradas) entre bases sucessivas, e logo
  depois da ultima vem o `0x00434340`, a bola em foco. O laco usa 1..10; a
  entrada extra e da `bola0`, o goleiro, que nao anda. }
const
  { Quantos quadros a animacao tem. O `relojTimer` compara com este numero e,
    ao chegar nele, encaixa e desliga o timer. }
  QUADROS_DA_ANIMACAO = 4;
  { A primeira e a ultima bola que a animacao move. `bola0` fica de fora. }
  BOLA_PRIMEIRA = 1;
  BOLA_ULTIMA = 10;

var
  { 0x0043428c -- o contador de quadros. }
  PassoDaAnimacao: Integer = 0;
  { 0x00434238 / 0x00434264 -- o destino final, ja inteiro. }
  DestinoX: array[0..10] of Integer;
  DestinoY: array[0..10] of Integer;
  { 0x00434294 / 0x004342c0 -- a posicao corrente, em ponto flutuante. E
    `Single`, nao `Double`: o original usa `fld DWORD PTR`, quatro bytes. }
  AtualX: array[0..10] of Single;
  AtualY: array[0..10] of Single;
  { 0x004342ec / 0x00434318 -- o passo somado a cada quadro. }
  DeltaX: array[0..10] of Single;
  DeltaY: array[0..10] of Single;
  { 0x00434348 -- o `etiqjugN` da bola que a animacao esta movendo agora.
    E OUTRO ponteiro, nao o `EtiquetaEmFoco`: o destaque do mouse e a animacao
    andam ao mesmo tempo e escrevem em rotulos diferentes. }
  EtiquetaEmMovimento: TLabel = nil;

{ A bola `n` e o rotulo dela, achados por nome como o original os acha.

  O original monta o nome com `CurrToStr(n * 10000)`: `Currency` na Borland e
  inteiro de 64 bits escalado por 10.000, entao a multiplicacao desfaz a escala
  e o resultado sai `'1'`, nao `'10000'`. `IntToStr` da o mesmo texto sem o
  rodeio. }
function BolaDeNumero(n: Integer): TShape;
var
  c: TComponent;
begin
  c := estrategia.FindComponent('bola' + IntToStr(n));
  if c is TShape then
    Result := TShape(c)
  else
    Result := nil;
end;

function EtiquetaDeNumero(n: Integer): TLabel;
var
  c: TComponent;
begin
  c := estrategia.FindComponent('etiqjug' + IntToStr(n));
  if c is TLabel then
    Result := TLabel(c)
  else
    Result := nil;
end;
