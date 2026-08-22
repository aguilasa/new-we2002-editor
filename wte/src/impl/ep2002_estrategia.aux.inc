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
  { A `BolaEmFoco` (`0x00434340`) subiu para o `wte_tatica` na CORR-WTE-082: a
    `PreparaAnimacao` a semeia, e ela foi junto com a rotina. Continua visivel
    daqui pelo `uses`.

    0x00434344 -- o `etiqjugN` da bola em foco. }
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
