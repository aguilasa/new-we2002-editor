{ wte_tatica -- a tela de tatica: a carga da imagem, o estado da animacao e o
  preenchimento do formulario `estrategia` (CORR-WTE-082).

  ESCRITA A MAO, e a terceira unidade neutra deste port pela mesma razao
  estrutural das duas anteriores: o `PreencheTelaDeTatica` precisa do
  `ep2002_estrategia` (os componentes que ele posiciona) E do `ep2002_mainform`
  (a lista de jogadores de onde saem os nomes). O `uses` que o `dfm2lfm.py`
  emite sai na INTERFACE, entao nenhum dos dois formularios pode usar o outro;
  quem os dois precisam chamar tem de morar numa unidade que NENHUM deles
  possui. E a forma que a `wte_ficha` estreou na CORR-WTE-081, e que a
  `wte_render2d` tinha estreado antes dela.

  O QUE DESCEU PARA CA veio do `impl/ep2002_estrategia.aux.inc`: o estado da
  animacao (as seis tabelas, o `PassoDaAnimacao`, os dois ponteiros em foco), a
  `ZonaDaBola`, a `BolaDeNumero`, a `EtiquetaDeNumero`, a `PreparaAnimacao` e a
  `PintaPosicoes`. O que ficou la e o que so o formulario usa: o ajuste a
  grade, o indice pelo nome, o marcador da malha e os handlers.

  AS DUAS ROTINAS DE ANIMACAO MUDARAM DE ASSINATURA, e a mudanca e o miolo
  desta correcao. Elas recebiam um INDICE na tabela de formacoes predefinidas
  (`FORMACOES[n]`), porque ate agora so o `lista_formacionesClick` as chamava.
  O original nao passa indice: passa o PONTEIRO do registro escolhido
  (`0x00434224`..`0x00434230`), e ele aponta ora para a tabela predefinida, ora
  para o buffer VIVO do time. Recebendo `const f: TFormacao` as duas servem os
  dois casos, que e o que o original faz com um ponteiro so.

  A TATICA VIVA E TRES BLOCOS DE ONZE BYTES, e nao trinta seguidos. O
  `MainForm.mostrar_estrategiaClick` le a formacao em tres pedacos de dez
  (`+0`, `+10`, `+20` do mesmo indice logico) para `0x00432e89`, `0x00432e94` e
  `0x00432e9f` -- passo 11, com o byte zero de cada linha de fora. Sao os
  papeis, os X e os Y, e e por isso que a gravacao do ` Accept` escreve
  `[0x00434224][1..10]` e nao `[0..9]`. }

unit wte_tatica;

{$mode objfpc}{$H+}

interface

uses
  SysUtils, Classes, Controls, ExtCtrls, StdCtrls, Graphics,
  we2002_offsets, we2002_cdimage, we2002_estado, wte_formacoes, wte_zonas;

const
  { As cinco regioes que a tela de tatica le, todas em indice LOGICO sobre o
    setor 850 -- o `0x001E8178` que o original soma em forma fechada. Sao as
    mesmas cinco que o ` Accept` grava de volta; ver a spec dele.

    O passo da formacao e 30 e o da tatica e 5, mas o `mostrar_estrategiaClick`
    LE QUATRO bytes de tatica e o ` Accept` GRAVA CINCO. A assimetria e do
    original e esta reproduzida: o quinto byte nao e lido por ninguem, e o que
    a gravacao poe nele vem do buffer local do handler. }
  TATICA_SETOR_BASE      = 850;
  TATICA_FORMACAO_LOGICO = $40C2C;
  TATICA_FORMACAO_PASSO  = 30;
  TATICA_FORMACAO_LINHA  = 10;
  TATICA_COBRADOR_LOGICO = $46228;
  TATICA_COBRADOR_PASSO  = 6;
  TATICA_TATICA_LOGICO   = $408A8;
  TATICA_TATICA_PASSO    = 5;
  TATICA_TATICA_LIDOS    = 4;
  TATICA_RADAR1_LOGICO   = $3F534;
  TATICA_RADAR2_LOGICO   = $3F634;
  TATICA_RADAR_BYTES     = 2;

  { O ajuste do time-modelo, o mesmo `2 * (t div 95)` que o resto do formato
    usa -- e ele NAO aparece na tatica nem no radar. }
  TATICA_TIMES_COM_TABELA = 95;

  { O codigo de zona que quer dizer "nenhuma das 16": cai no registro STOCK.

    O original guarda um PONTEIRO em `0x00434230`, e ele aponta para dentro da
    mesma tabela de 18 registros de 44 bytes que a `wte_formacoes` traz: o
    campo `zona` fica no deslocamento 33 de cada registro, e os dois enderecos
    imediatos do binario sao `0x00433F2D` (registro 0) e `0x00433F85 + 44*n`
    (registro n + 2). Por isso o deslocamento de dois. }
  TATICA_CODIGO_STOCK      = 16;
  TATICA_ZONA_DESLOCAMENTO = 2;

  { Os quatro marcadores `simboloN` saem de quatro campos de QUATRO bits,
    empacotados nos bytes 1..3 do buffer de tatica -- 1 e 2 para os dois
    primeiros, 2 e 3 para os dois ultimos. }
  TATICA_MARCADORES     = 4;
  TATICA_MARCADOR_BITS  = 4;
  { O passo e a folga da malha sao os do `wte_zonas` -- `MALHA_PASSO_Y` (o
    `shl 4` do original) e `MALHA_FOLGA` (o `+ 3`). Sao os MESMOS que o clique
    usa, e por isso nao ganham nome novo aqui. }

  { Os seis cobradores, e o mesmo `passo * valor + folga` dos marcadores. }
  TATICA_COBRADORES = 6;

  { As dez bolas que andam -- `bola1`..`bola10`. O goleiro (`bola0`) nao entra
    nem aqui nem no laco da animacao. }
  TATICA_JOGADORES_EM_CAMPO = 10;

  { As duas conversoes de pixel para celula, e elas sao o INVERSO exato do que
    a `PreparaAnimacao` faz na ida:

        DestinoX := x * 8 - 2  ->  x := (Left - campo.Left + 2) div 8
        DestinoY := ((y - 3) div 2) * 5 - 7
                               ->  y := ((Top - campo.Top + 7) div 5) * 2 + 3 }
  TATICA_X_PASSO = 8;
  TATICA_X_FOLGA = 2;
  TATICA_Y_PASSO = 5;
  TATICA_Y_FOLGA = 7;

  { O item que o formulario seleciona ao abrir: `DEFAULT`. }
  TATICA_ITEM_DEFAULT = 1;

  { Quantos nomes a lista de jogadores rende para a tela, e onde comeca o
    recorte. O original usa 5 para os nove primeiros e 4 do decimo em diante --
    a mesma regra do `NomeDoItemSelecionado`, e pelo mesmo motivo: o prefixo
    numerico do item tem um digito a mais depois do nono. }
  TATICA_NOMES          = 11;
  TATICA_NOME_COMPRIMENTO = 10;
  TATICA_NOME_CORTE_CURTO = 4;    { o do original, do decimo item em diante }
  TATICA_NOME_CORTE_LONGO = 5;    { o do original, nos nove primeiros       }
  TATICA_NOMES_CORTE_LONGO = 9;
  { O do PORT, e o porque esta no corpo: a lista daqui nao tem prefixo. }
  TATICA_NOME_CORTE_PORT  = 1;

type
  { A tatica VIVA do time, como a imagem a guarda.

    `formacao` reusa o `TFormacao` da `wte_formacoes` de proposito: os campos
    sao os mesmos (papeis, X, Y, zona), e assim as duas rotinas de animacao
    servem tanto a tabela predefinida quanto esta. A `zona` NAO vem da imagem:
    ela e escolhida pelo codigo do primeiro byte de `tatica`, como o original
    escolhe o ponteiro. }
  TTaticaViva = record
    valida: Boolean;
    indice: Integer;
    formacao: TFormacao;
    cobrador: array[0 .. TATICA_COBRADORES - 1] of Byte;
    tatica: array[0 .. TATICA_TATICA_LIDOS - 1] of Byte;
    radar: array[0 .. 1, 0 .. TATICA_RADAR_BYTES - 1] of Byte;
    tem_radar: Boolean;
  end;

var
  { Uma so, como no original: o buffer de tatica e global, nao por instancia. }
  TaticaViva: TTaticaViva;

{ Le da imagem as cinco regioes da tela de tatica -- a parte do
  `MainForm.mostrar_estrategiaClick` (`0x00410220`) que este port nao tinha.

  As duas de radar so existem para time de selecao: o original desabilita os
  dois combos quando o indice chega a 95 e nem tenta ler. `tem_radar` guarda
  isso.

  False quando nao ha imagem aberta, o indice nao e time, ou a leitura nao
  completa -- e ai o `PreencheTelaDeTatica` se recusa, em vez de posicionar a
  tela com lixo. }
function CarregaTaticaDaImagem(indice_do_time: Integer): Boolean;

{ Um campo de quatro bits do par de bytes, como a `0x00403278` o extrai. }
function CampoDeQuatroBits(b0, b1: Byte; bit: Integer): Integer;

{ O item do combo cuja cor casa com o par de bytes lido, ou -1.

  O original percorre a tabela de oito de `0x00423624` comparando byte a byte e
  para no primeiro que casar; sem casar, ele nao mexe no combo. }
function IndiceDaCorDeRadar(b0, b1: Byte): Integer;

var
  { O `0x00434230` do original -- o registro de formacao EM VIGOR.

    Era `FormacaoAplicada: Integer` no `.aux.inc` do `estrategia`, um indice na
    tabela predefinida, e a CORR-WTE-082 o trocou pelo registro porque a tatica
    VIVA do time nao tem indice em tabela nenhuma. E o que o original sempre
    teve: um ponteiro, que ora aponta para a tabela, ora para o buffer vivo. }
  FormacaoEmVigor: TFormacao;
  FormacaoEmVigorValida: Boolean = False;


{ GRAVA A TATICA NA IMAGEM -- a metade de escrita do `estrategia.BitBtn3Click`
  (`0x0040a660`), CORR-WTE-081.

  Cinco regioes, 45 bytes por time, e as tres ultimas NAO passam pela
  `0x00403400`: o original chama `fseek` e `fputc` da RTL direto, um byte por
  vez, com o teste de fronteira de setor escrito no proprio laco. Aqui as
  cinco vao pelo `GravaNoFluxo`, que faz o mesmo salto -- o arquivo recebe os
  mesmos bytes nos mesmos offsets, que e o que o gate compara.

  A FORMACAO SAO TRES BLOCOS DE DEZ no mesmo indice logico (`+0`, `+10`,
  `+20`), e o primeiro deles e o vetor de PAPEIS -- que ninguem edita na tela e
  que vem da tatica viva. Os outros dois sao os X e os Y lidos dos componentes.

  False quando nao ha imagem aberta ou o indice nao e time. }
function GravaTaticaNaImagem(indice_do_time: Integer;
                             const papel, x, y, cobrador, tatica): Boolean;

{ Grava UMA cor de radar -- `qual` e 0 (casa) ou 1 (visitante), `item` e o
  indice do combo, que indexa a tabela de oito de `0x00423624`.

  So faz sentido para selecao: o original pula o bloco inteiro quando o indice
  chega a 95. }
function GravaCorDeRadar(indice_do_time, qual, item: Integer): Boolean;

{ ENCHE A TELA DE TATICA -- a `0x0040A0B4`, 1.443 bytes.

  Ela e a leitora que faltava, e a ausencia dela era o que impedia o ` Accept`
  (`estrategia.BitBtn3Click`) de ter dono: aquele handler le a POSICAO dos
  componentes para converter em celula da malha, e num formulario que ninguem
  posicionou isso seria a coordenada de tempo de projeto do `.lfm`.

  Ela NAO faz I/O -- medido, e vale registrar porque contraria a leitura
  apressada do nome: nao ha `0x004033BC`, nao ha `0x00403388`, nao ha `fseek`
  no corpo. Tudo o que ela usa ja esta em memoria, posto la pela
  `CarregaTaticaDaImagem`.

  Seis coisas, nesta ordem:

  1. os onze nomes, da lista de jogadores do lado escolhido, em `etiqjug<i>` e
     `jugador<i+1>`;
  2. os seis `tirador<i+1>`, posicionados a partir do `malla2`;
  3. o registro de zona, escolhido pelo codigo da tatica;
  4. `lista_formaciones.ItemIndex := 1` -- o item `DEFAULT`;
  5. a animacao e os rotulos de posicao, pelas duas rotinas acima;
  6. os quatro `simbolo`, de quatro campos de quatro bits, e os dois combos de
     cor de radar, por busca na tabela de oito cores.

  False quando nao ha tatica viva carregada. }
function PreencheTelaDeTatica: Boolean;

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
  { 0x00434340 -- a bola sob o ponteiro.

    O MESMO ponteiro serve de "bola destacada" e de "bola sendo arrastada", e a
    leitura apressada veria duas coisas: o `bolaMouseMove` o move a cada
    passagem do mouse e o `bolaMouseDown` simplesmente o reusa, porque para
    apertar o botao sobre a bola o ponteiro ja passou por ela.

    Morava no `.aux.inc` do `estrategia` ate a CORR-WTE-082; veio junto com a
    `PreparaAnimacao`, que a semeia a cada iteracao. }
  BolaEmFoco: TShape = nil;

  { 0x00434348 -- o `etiqjugN` da bola que a animacao esta movendo agora.
    E OUTRO ponteiro, nao o `EtiquetaEmFoco`: o destaque do mouse e a animacao
    andam ao mesmo tempo e escrevem em rotulos diferentes. }
  EtiquetaEmMovimento: TLabel = nil;


{ A zona da bola `i`, do registro em vigor. Zero sem formacao em vigor. }
function ZonaDaBola(i: Integer): Integer;

{ A bola `n` e o rotulo dela, achados por nome como o original os acha. }
function BolaDeNumero(n: Integer): TShape;
function EtiquetaDeNumero(n: Integer): TLabel;

{ Prepara a animacao de formacao e liga o `reloj` -- a `0x004097d4`. }
procedure PreparaAnimacao(const f: TFormacao);

{ Pinta os onze `etiqposN` -- a `0x004099bc`. }
procedure PintaPosicoes(const f: TFormacao);

implementation

uses
  ep2002_estrategia, ep2002_mainform;


function IndiceDaCorDeRadar(b0, b1: Byte): Integer;
var
  i: Integer;
begin
  Result := -1;
  for i := 0 to CORES_DE_RADAR_TOTAL - 1 do
    if (Byte(CORES_DE_RADAR[i] and $FF) = b0)
       and (Byte(CORES_DE_RADAR[i] shr 8) = b1) then
      Exit(i);
end;

{ A zona da bola `i`, para o `bolaMouseDown` dimensionar o `rectangulo`.

  No original isto e `[0x00434230]^[i]` -- um ponteiro para os 11 bytes de zona
  do registro da formacao escolhida. Aqui o ponteiro virou o proprio registro,
  `FormacaoEmVigor`, e o motivo e a CORR-WTE-082: ate ela o port so sabia
  apontar para a tabela de formacoes predefinidas, por INDICE, e a tatica VIVA
  do time nao tinha como entrar.

  A DIVERGENCIA QUE MORAVA AQUI ERA ESTA, e ela fechou: o comentario dizia
  *"zona 0 enquanto nao houver formacao aplicada ... no original quem aponta os
  quatro ponteiros ao abrir o formulario e o `0x0040a0b4`, que nao esta
  portado"*. Ele esta portado agora, e o `PreencheTelaDeTatica` logo abaixo
  aponta este registro para a tatica lida da imagem. }
function ZonaDaBola(i: Integer): Integer;
begin
  Result := 0;
  if not FormacaoEmVigorValida then
    Exit;
  if (i < 0) or (i >= FORMACAO_JOGADORES) then
    Exit;
  Result := FormacaoEmVigor.zona[i];
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
procedure PreparaAnimacao(const f: TFormacao);
var
  i: Integer;
  bola: TShape;
  dy: Integer;
begin
  for i := BOLA_PRIMEIRA to BOLA_ULTIMA do
  begin
    DestinoX[i - 1] := f.x[i] * 8 - 2;
    dy := f.y[i] - 3;
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
procedure PintaPosicoes(const f: TFormacao);
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
    papel := f.papel[i];
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

function CampoDeQuatroBits(b0, b1: Byte; bit: Integer): Integer;
var
  par: Integer;
begin
  { O `0x00403278` recebe os dois bytes em AL e DL, o bit inicial em ECX e a
    largura empilhada; para os quatro marcadores a largura e sempre 4 e o bit
    e 0 ou 4. Aqui a conta e a mesma, escrita como deslocamento sobre o par. }
  par := b0 or (b1 shl 8);
  Result := (par shr bit) and ((1 shl TATICA_MARCADOR_BITS) - 1);
end;

function GravaCorDeRadar(indice_do_time, qual, item: Integer): Boolean;
var
  img: TCdImage;
  logico: TOffset;
  par: array[0 .. 1] of Byte;
  base: TOffset;
begin
  Result := False;
  if ImagemAberta = '' then
    Exit;
  if (indice_do_time < 0) or (indice_do_time >= TATICA_TIMES_COM_TABELA) then
    Exit;
  if (item < 0) or (item >= CORES_DE_RADAR_TOTAL) then
    Exit;
  if qual = 0 then
    base := TATICA_RADAR1_LOGICO
  else
    base := TATICA_RADAR2_LOGICO;
  { O ORIGINAL NAO GRAVA O INDICE DO COMBO: ele passa o ENDERECO da entrada da
    tabela como origem dos dois bytes (`0x00423624 + 2 * item`). O que vai para
    a imagem e a palavra BGR555, e e por isso que a carga faz a busca inversa. }
  par[0] := Byte(CORES_DE_RADAR[item] and $FF);
  par[1] := Byte(CORES_DE_RADAR[item] shr 8);
  logico := base + TATICA_RADAR_BYTES * indice_do_time;

  img.Init;
  if not img.OpenReadWrite(ImagemAberta) then
    Exit;
  try
    GravaNoFluxo(img, EnderecoDeDados(TATICA_SETOR_BASE, logico),
                 par[0], TATICA_RADAR_BYTES);
  finally
    img.Close;
  end;
  Result := True;
end;

function GravaTaticaNaImagem(indice_do_time: Integer;
                             const papel, x, y, cobrador, tatica): Boolean;
var
  img: TCdImage;
  logico: TOffset;
begin
  Result := False;
  if ImagemAberta = '' then
    Exit;
  if (indice_do_time < 0) or (indice_do_time > TATICA_TIMES_COM_TABELA) then
    Exit;

  img.Init;
  if not img.OpenReadWrite(ImagemAberta) then
    Exit;
  try
    logico := TATICA_FORMACAO_LOGICO
              + TATICA_FORMACAO_PASSO * indice_do_time
              + 2 * (indice_do_time div TATICA_TIMES_COM_TABELA);
    GravaNoFluxo(img, EnderecoDeDados(TATICA_SETOR_BASE, logico),
                 papel, TATICA_FORMACAO_LINHA);
    GravaNoFluxo(img, EnderecoDeDados(TATICA_SETOR_BASE,
                                      logico + TATICA_FORMACAO_LINHA),
                 x, TATICA_FORMACAO_LINHA);
    GravaNoFluxo(img, EnderecoDeDados(TATICA_SETOR_BASE,
                                      logico + 2 * TATICA_FORMACAO_LINHA),
                 y, TATICA_FORMACAO_LINHA);

    logico := TATICA_COBRADOR_LOGICO
              + TATICA_COBRADOR_PASSO * indice_do_time
              + 2 * (indice_do_time div TATICA_TIMES_COM_TABELA);
    GravaNoFluxo(img, EnderecoDeDados(TATICA_SETOR_BASE, logico),
                 cobrador, TATICA_COBRADOR_PASSO);

    { CINCO bytes, e a carga le QUATRO. A assimetria e do original. }
    logico := TATICA_TATICA_LOGICO + TATICA_TATICA_PASSO * indice_do_time;
    GravaNoFluxo(img, EnderecoDeDados(TATICA_SETOR_BASE, logico),
                 tatica, TATICA_TATICA_PASSO);
  finally
    img.Close;
  end;
  Result := True;
end;

function CarregaTaticaDaImagem(indice_do_time: Integer): Boolean;
var
  img: TCdImage;
  logico: TOffset;
  codigo: Integer;
begin
  Result := False;
  TaticaViva.valida := False;
  TaticaViva.tem_radar := False;
  if ImagemAberta = '' then
    Exit;
  if (indice_do_time < 0) or (indice_do_time > TATICA_TIMES_COM_TABELA) then
    Exit;

  img.Init;
  if not img.OpenRead(ImagemAberta) then
    Exit;
  try
    { A formacao, em TRES pedacos de dez -- o original le `+0`, `+10` e `+20`
      do mesmo indice logico para tres linhas de onze bytes, e o byte zero de
      cada linha fica de fora. Aqui as tres linhas sao os tres vetores do
      `TFormacao`, e o `[0]` deles e o mesmo byte que ninguem toca. }
    logico := TATICA_FORMACAO_LOGICO
              + TATICA_FORMACAO_PASSO * indice_do_time
              + 2 * (indice_do_time div TATICA_TIMES_COM_TABELA);
    if not LeDoFluxoEm(img, EnderecoDeDados(TATICA_SETOR_BASE, logico),
                       TaticaViva.formacao.papel[1],
                       TATICA_FORMACAO_LINHA) then
      Exit;
    if not LeDoFluxoEm(img,
           EnderecoDeDados(TATICA_SETOR_BASE,
                           logico + TATICA_FORMACAO_LINHA),
           TaticaViva.formacao.x[1], TATICA_FORMACAO_LINHA) then
      Exit;
    if not LeDoFluxoEm(img,
           EnderecoDeDados(TATICA_SETOR_BASE,
                           logico + 2 * TATICA_FORMACAO_LINHA),
           TaticaViva.formacao.y[1], TATICA_FORMACAO_LINHA) then
      Exit;

    logico := TATICA_COBRADOR_LOGICO
              + TATICA_COBRADOR_PASSO * indice_do_time
              + 2 * (indice_do_time div TATICA_TIMES_COM_TABELA);
    if not LeDoFluxoEm(img, EnderecoDeDados(TATICA_SETOR_BASE, logico),
                       TaticaViva.cobrador[0], TATICA_COBRADORES) then
      Exit;

    { A tatica NAO leva o ajuste do time-modelo, e o radar tambem nao. }
    logico := TATICA_TATICA_LOGICO + TATICA_TATICA_PASSO * indice_do_time;
    if not LeDoFluxoEm(img, EnderecoDeDados(TATICA_SETOR_BASE, logico),
                       TaticaViva.tatica[0], TATICA_TATICA_LIDOS) then
      Exit;

    if indice_do_time < TATICA_TIMES_COM_TABELA then
    begin
      if not LeDoFluxoEm(img,
             EnderecoDeDados(TATICA_SETOR_BASE,
                             TATICA_RADAR1_LOGICO + 2 * indice_do_time),
             TaticaViva.radar[0][0], TATICA_RADAR_BYTES) then
        Exit;
      if not LeDoFluxoEm(img,
             EnderecoDeDados(TATICA_SETOR_BASE,
                             TATICA_RADAR2_LOGICO + 2 * indice_do_time),
             TaticaViva.radar[1][0], TATICA_RADAR_BYTES) then
        Exit;
      TaticaViva.tem_radar := True;
    end;
  finally
    img.Close;
  end;

  { A ZONA NAO VEM DA IMAGEM: o codigo escolhe um dos 18 registros da tabela,
    com o deslocamento de dois que os dois enderecos imediatos do binario
    revelam. Codigo 16 quer dizer "nenhuma das 16" e cai no registro 0. }
  codigo := TaticaViva.tatica[0];
  if codigo = TATICA_CODIGO_STOCK then
    codigo := 0
  else
    codigo := codigo + TATICA_ZONA_DESLOCAMENTO;
  if (codigo >= 0) and (codigo < FORMACOES_TOTAL) then
    TaticaViva.formacao.zona := FORMACOES[codigo].zona
  else
    FillChar(TaticaViva.formacao.zona, SizeOf(TaticaViva.formacao.zona), 0);

  TaticaViva.indice := indice_do_time;
  TaticaViva.valida := True;
  Result := True;
end;

function PreencheTelaDeTatica: Boolean;
var
  i, corte, valor: Integer;
  nome: string;
  c: TComponent;

  { `malla2.Top + MALHA_PASSO_Y * valor + MALHA_FOLGA`, dez vezes no original.

    E O `Top`, NAO O `Left`, e a diferenca custou uma corrida de tela: os dez
    marcadores ficaram amontoados no canto superior direito, porque o `Left`
    somado empurra na horizontal e o de projeto ja estava certo. O
    `MoveMarcadorDaMalha` do `.aux.inc` diz isso desde a WTE-TASK-29 -- *"o
    `Left` do marcador nao e tocado: ele ja esta na coluna certa desde o
    `.dfm`"* -- e o valor lido da imagem escolhe a LINHA.

    Os dois numeros sao os mesmos do clique, e vem do `wte_zonas`: passo 16,
    folga 3. }
  procedure PoeNaMalha(alvo: TControl; valor: Integer);
  begin
    if alvo = nil then
      Exit;
    alvo.Top := estrategia.malla2.Top + MALHA_PASSO_Y * valor + MALHA_FOLGA;
  end;

  function Componente(const prefixo: string; n: Integer): TComponent;
  begin
    Result := estrategia.FindComponent(prefixo + IntToStr(n));
  end;

begin
  Result := False;
  if not TaticaViva.valida then
    Exit;

  { 1. OS ONZE NOMES, do item da lista de jogadores do lado escolhido.

       O CORTE E 1 AQUI E 4 OU 5 NO ORIGINAL, e a diferenca nao e escolha: a
       lista do original traz um PREFIXO NUMERICO antes do nome, e por isso ele
       corta na posicao 5 nos nove primeiros e na 4 do decimo em diante -- a
       mesma regra que o `NomeDoItemSelecionado` do `MainForm` reproduz. A
       lista do port nao tem prefixo: o `PreencheJogadores` a enche com o nome
       filtrado e mais nada.

       Cortar em 4 aqui comeria as quatro primeiras letras. Medido na tela
       antes de esta linha existir: onde o oraculo mostrava `?I???` o port
       mostrava `?`, e onde ele mostrava `?W????????` o port mostrava `??????`.

       O prefixo ausente e uma inconsistencia HERDADA, e ela tem outro
       sintoma: o `NomeDoItemSelecionado` corta 4 ou 5 de um item que nao tem
       o que cortar. Nao e desta correcao. }
  for i := 0 to TATICA_NOMES - 1 do
  begin
    if i >= MainForm.lista_jugadores_1.Items.Count then
      Break;
    corte := TATICA_NOME_CORTE_PORT;
    nome := Copy(MainForm.lista_jugadores_1.Items[i], corte,
                 TATICA_NOME_COMPRIMENTO);
    c := Componente('etiqjug', i);
    if c is TLabel then
      TLabel(c).Caption := nome;
    c := Componente('jugador', i + 1);
    if c is TLabel then
      TLabel(c).Caption := nome;
  end;

  { 2. OS SEIS COBRADORES. }
  for i := 0 to TATICA_COBRADORES - 1 do
  begin
    c := Componente('tirador', i + 1);
    if c is TControl then
      PoeNaMalha(TControl(c), TaticaViva.cobrador[i]);
  end;

  { 3 e 4. A formacao em vigor passa a ser a VIVA, e a lista mostra `DEFAULT`. }
  FormacaoEmVigor := TaticaViva.formacao;
  FormacaoEmVigorValida := True;
  estrategia.lista_formaciones.ItemIndex := TATICA_ITEM_DEFAULT;

  { 5. A animacao e os rotulos de posicao, pelas mesmas duas rotinas que o
       `lista_formacionesClick` usa -- e e por isso que elas passaram a receber
       o registro em vez do indice. }
  PreparaAnimacao(TaticaViva.formacao);
  PintaPosicoes(TaticaViva.formacao);

  { 6a. OS QUATRO MARCADORES, de quatro campos de quatro bits. Os dois
       primeiros saem do par (tatica[1], tatica[2]); os dois ultimos do par
       (tatica[2], tatica[3]). }
  PoeNaMalha(estrategia.simbolo1,
             CampoDeQuatroBits(TaticaViva.tatica[1], TaticaViva.tatica[2], 0));
  PoeNaMalha(estrategia.simbolo2,
             CampoDeQuatroBits(TaticaViva.tatica[1], TaticaViva.tatica[2], 4));
  PoeNaMalha(estrategia.simbolo3,
             CampoDeQuatroBits(TaticaViva.tatica[2], TaticaViva.tatica[3], 0));
  PoeNaMalha(estrategia.simbolo4,
             CampoDeQuatroBits(TaticaViva.tatica[2], TaticaViva.tatica[3], 4));

  { 6b. OS DOIS COMBOS DE COR DE RADAR. O original varre uma tabela de oito
       pares de bytes e seleciona o indice que casar; sem casar, nao mexe no
       combo. }
  if TaticaViva.tem_radar then
  begin
    valor := IndiceDaCorDeRadar(TaticaViva.radar[0][0], TaticaViva.radar[0][1]);
    if valor >= 0 then
      estrategia.ComboBox1.ItemIndex := valor;
    valor := IndiceDaCorDeRadar(TaticaViva.radar[1][0], TaticaViva.radar[1][1]);
    if valor >= 0 then
      estrategia.ComboBox2.ItemIndex := valor;
  end;

  Result := True;
end;

end.
