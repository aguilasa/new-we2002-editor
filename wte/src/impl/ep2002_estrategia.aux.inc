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

  { O `0x00434230` do original e um PONTEIRO, nao um vetor: ele aponta para os
    11 bytes de zona do registro da formacao escolhida. Aqui o ponteiro vira
    indice, que e a mesma coisa sem ponteiro solto.

    `-1` = nenhuma formacao aplicada ainda. No original isso nao acontece,
    porque `0x0040a0b4` aponta os quatro ponteiros ao ABRIR o formulario; essa
    rotina nao esta portada, e enquanto nao estiver o port abre com toda bola
    na zona 0. Ver `ZonaDaBola`. }
  FormacaoAplicada: Integer = -1;

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

  { O `ItemIndex` de `lista_formaciones` que NAO indexa a tabela: `DEFAULT` le
    o buffer da formacao viva do time (`0x00432e88`), preenchido por
    `0x0040a0b4`, que nao esta portado. Ver `AplicaFormacao`. }
  FORMACAO_DEFAULT = 1;

  { Os `etiqposN` comecam em 1 e o goleiro e o `etiqpos1`, entao o jogador `i`
    da tabela cai no rotulo `i + 1`. }
  ETIQPOS_DESLOCAMENTO = 1;

  { As tres cores do `0x004099bc`, em $00BBGGRR -- o mesmo formato da VCL e da
    LCL, entao passam sem conversao. O criterio nao e o que o nome sugere:

        papel = 4 ou papel > 16  ->  vermelho
        papel < 9                ->  ciano
        senao (9..16)            ->  verde

    O `papel = 4` e `Zl`, um zagueiro, e ele cai no ramo dos atacantes. E
    excentricidade do original -- `cmp al,4 / je` e a PRIMEIRA instrucao do
    teste, antes de qualquer comparacao de faixa --, nao erro de leitura. }
  COR_ATAQUE = $000000FF;
  COR_DEFESA = $00FFFF00;
  COR_MEIO   = $0000FF00;
  PAPEL_EXCECAO_VERMELHA = 4;
  PAPEL_ULTIMO_DEFENSOR = 8;
  PAPEL_ULTIMO_MEIO = 16;

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

{ A zona da bola `i`, para o `bolaMouseDown` dimensionar o `rectangulo`.

  No original isto e `[0x00434230]^[i]` -- um ponteiro para os 11 bytes de zona
  do registro da formacao escolhida. Aqui e um indice na `FORMACOES` do
  `wte_formacoes.pas`, que e a MESMA tabela: a de `0x00433f0c`, montada pelo
  `estrategia.FormCreate` a partir de quatro blobs de `.data`, extraida pelo
  `dump_formacoes.py`.

  Zona 0 enquanto nao houver formacao aplicada. Isso e DIVERGENCIA, e ela tem
  dono: no original quem aponta os quatro ponteiros ao abrir o formulario e o
  `0x0040a0b4`, que nao esta portado -- ver a spec do `lista_formacionesClick`. }
function ZonaDaBola(i: Integer): Integer;
begin
  Result := 0;
  if (FormacaoAplicada < 0) or (FormacaoAplicada >= FORMACOES_TOTAL) then
    Exit;
  if (i < 0) or (i >= FORMACAO_JOGADORES) then
    Exit;
  Result := FORMACOES[FormacaoAplicada].zona[i];
end;

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

{ 0x004097d4, 474 bytes -- prepara a animacao e liga o `reloj`.

  Tres lacos de `1..10` (o goleiro nao anda), e as seis tabelas que o
  `relojTimer` consome saem daqui:

      DestinoX[i] := x[i]*8 - 2
      DestinoY[i] := ((y[i] - 3) div 2)*5 - 7
      AtualX[i]   := bola_i.Left - campo.Left
      DeltaX[i]   := (DestinoX[i] - AtualX[i]) * PASSO_DA_ANIMACAO

  O `PASSO_DA_ANIMACAO` e 0.2, decodificado de um `long double` de 80 bits em
  `0x004099b0` -- dentro da `.text`, logo depois do corpo. Com os quatro
  quadros do `relojTimer` isso cobre 80% do trajeto, e o ramo de encaixe da o
  ultimo quinto de uma vez: NAO e correcao de arredondamento de um pixel.

  A divisao do Y trunca para ZERO, como o `idiv` do original -- e nao para
  -infinito, como o `div` do Pascal faria com negativo. So o registro 0
  (goleiro, `y = 0`) cai nesse caso, e ele nao entra no laco; a diferenca esta
  aqui porque o dia em que entrar, entra certo.

  Efeito colateral do original, reproduzido: ele semeia `BolaEmFoco`
  (`0x00434340`) a cada iteracao, terminando na `bola10`. E o que dispensaria a
  guarda de `nil` dos handlers de arrastar -- que fica, porque no port o
  formulario ainda pode abrir sem nenhuma formacao aplicada. }
procedure PreparaAnimacao(formacao: Integer);
var
  i: Integer;
  bola: TShape;
  dy: Integer;
begin
  for i := BOLA_PRIMEIRA to BOLA_ULTIMA do
  begin
    DestinoX[i - 1] := FORMACOES[formacao].x[i] * 8 - 2;
    dy := FORMACOES[formacao].y[i] - 3;
    if dy < 0 then
      DestinoY[i - 1] := -((-dy) div 2) * 5 - 7
    else
      DestinoY[i - 1] := (dy div 2) * 5 - 7;

    bola := BolaDeNumero(i);
    if bola = nil then
      Continue;
    BolaEmFoco := bola;
    AtualX[i - 1] := bola.Left - estrategia.campo.Left;
    AtualY[i - 1] := bola.Top - estrategia.campo.Top;
    DeltaX[i - 1] := (DestinoX[i - 1] - AtualX[i - 1]) * PASSO_DA_ANIMACAO;
    DeltaY[i - 1] := (DestinoY[i - 1] - AtualY[i - 1]) * PASSO_DA_ANIMACAO;
  end;
  PassoDaAnimacao := 0;
  estrategia.reloj.Enabled := True;
end;

{ 0x004099bc, 227 bytes -- pinta os onze `etiqposN`.

  Recebe o vetor de papeis (o `[0x00434224]` do original) e, para cada jogador
  `1..10`, poe o texto e a cor no rotulo `etiqpos<i+1>`. O deslocamento existe
  porque `etiqpos1` e o goleiro.

  O criterio de cor esta nas constantes do topo, e o `papel = 4` no ramo
  vermelho e do original. }
procedure PintaPosicoes(formacao: Integer);
var
  i, papel: Integer;
  c: TComponent;
  rotulo: TLabel;
begin
  for i := BOLA_PRIMEIRA to BOLA_ULTIMA do
  begin
    c := estrategia.FindComponent(
      'etiqpos' + IntToStr(i + ETIQPOS_DESLOCAMENTO));
    if not (c is TLabel) then
      Continue;
    rotulo := TLabel(c);
    papel := FORMACOES[formacao].papel[i];
    if (papel = PAPEL_EXCECAO_VERMELHA) or (papel > PAPEL_ULTIMO_MEIO) then
      rotulo.Font.Color := COR_ATAQUE
    else if papel <= PAPEL_ULTIMO_DEFENSOR then
      rotulo.Font.Color := COR_DEFESA
    else
      rotulo.Font.Color := COR_MEIO;
    if (papel >= 0) and (papel < POSICOES_TOTAL) then
      rotulo.Caption := POSICOES[papel];
  end;
end;

{ MoveMarcadorDaMalha -- o corpo comum dos dois `mallaNMouseDown`
  (`0x00409f4c` e `0x0040a000`), WTE-TASK-29.

  O original NAO fatorou: os 180 bytes de cada handler sao a mesma sequencia de
  instrucoes com dois imediatos diferentes -- o endereco da cadeia de prefixo e
  o deslocamento do campo da `TImage`. Aqui os dois chamam esta rotina, e a
  diferenca fica nos argumentos.

  O QUE ELA FAZ: o X escolhe a COLUNA, o Y escolhe a LINHA.

      indice := X div MALHA_PASSO_X + 1
      <prefixo><indice>.Top := malha.Top
                             + (Y div MALHA_PASSO_Y) * MALHA_PASSO_Y
                             + MALHA_FOLGA

  O `Left` do marcador nao e tocado: ele ja esta na coluna certa desde o `.dfm`,
  e e por isso que o `indice` sai do X em vez de o marcador ser movido para ele.

  QUAL DOS DOIS E O X CUSTOU UMA CONFERENCIA. Na convencao da Borland o
  `Self`, o `Sender` e o `Button` vao em EAX, EDX e CL, e o `Shift`, o `X` e o
  `Y` sobram na pilha -- com o `X` em `[ebp+0xc]` e o `Y` em `[ebp+0x8]`. Quem
  decide isso nao e este handler: e o `bolaMouseDown`, que guarda os dois num
  `TPoint` global (`0x0043434c`) e assim diz qual e qual. Trocados, o handler
  compila, roda, e move o marcador errado para a altura errada.

  A DIVISAO E TRUNCADA PARA ZERO nos dois casos, como a do original: o `idiv`
  do X ja e assim, e o snap do Y e `sar`/`shl` com o `+ (passo - 1)` de fixup
  antes do deslocamento -- que e o que o Pascal escreve com `div`. Com X e Y
  sempre positivos dentro da imagem os dois ramos coincidem; o fixup existe no
  binario e nao se ve na tela.

  O GUARDA DE FAIXA NAO E DO ORIGINAL, e a diferenca e de comportamento
  indefinido contra comportamento: o `FindComponent` do original devolveria nulo
  para um indice fora de `1..colunas` e o `SetTop` seguinte cairia com `this`
  nulo. Como o clique chega em coordenada de cliente da propria `TImage`, o
  indice so sai da faixa se o widgetset entregar X fora dela -- e um port que
  travasse ali estaria reproduzindo um modo de falha, nao um comportamento. }
procedure MoveMarcadorDaMalha(const prefixo: string; colunas: Integer;
                              malha: TImage; X, Y: Integer);
var
  indice: Integer;
  c: TComponent;
begin
  indice := X div MALHA_PASSO_X + 1;
  if (indice < 1) or (indice > colunas) then
    Exit;
  c := estrategia.FindComponent(prefixo + IntToStr(indice));
  if not (c is TControl) then
    Exit;
  TControl(c).Top := malha.Top
                     + (Y div MALHA_PASSO_Y) * MALHA_PASSO_Y
                     + MALHA_FOLGA;
end;
