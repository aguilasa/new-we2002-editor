{ Rotinas internas do MainForm -- WTE-TASK-25.

  O original chama rotinas que NAO sao metodo publicado, e algumas de mais de
  um handler. Elas nao cabem num `.inc` por handler, e e por isso que este
  arquivo existe; ver `wte/src/impl/README.md`.

  Cada uma traz o endereco no `.exe` e a medicao que a sustenta. O inventario
  das 91 rotinas internas que o grupo de carga alcanca esta em
  `wte/re/auxiliares.md`. }

const
  { O item `95 Master L. ` do combo: o time-modelo que a Master League usa ao
    criar clube. NAO e o numero de times -- os de verdade sao 0..94. Medido na
    spec do `lista_equiposChange`. }
  IDX_MODELO_ML = 95;
  { Indices 0..62 sao `teams` (selecoes e all-star); 63..94 sao os 32
    `ml_teams`. A contiguidade foi conferida byte a byte contra o
    `dump_estado.pas` na terceira passagem da WTE-TASK-25. }
  TIMES_NACIONAIS = 63;
  { Jogadores sem contrato, antes dos elencos. `PLAYERS_NC` do we2002_core. }
  JOGADORES_SEM_CONTRATO = 462;
  JOGADORES_POR_TIME = 23;
  { Bytes de um campo de nome de time, terminador incluido -- o `names` do
    `we2002_team.pas` e `array[0..19] of AnsiChar`. O original guarda o mesmo
    numero na global `0x00433b48`, que ele usa para o `MaxLength` de
    `edit_nombre2` e para o truncamento do `iguala_nombresClick`. Que os dois
    sejam o MESMO numero e inferencia, nao medicao -- ver a spec do
    `iguala_nombresClick`. }
  TAMANHO_DO_NOME = 20;

var
  { O `0x004335e4` do original: qual `dorsalN` esta marcado agora.

    E o MESMO ponteiro da `wte/re/crash-causa.md`. La ele derruba o `wte.exe`
    com a ROM europeia porque a carga de time o sobrescreve com dado de tabela
    vizinha, e o `TFont::SetSize` seguinte cai com `this` nulo. Aqui ele e
    tipado e so recebe o que o `FindComponent` devolveu, entao o modo de falha
    do original nao tem por onde acontecer. }
  CamisaMarcada: TStaticText = nil;

{ MarcaCamisa -- 0x0040b188, 335 bytes.
  Spec: wte/re/spec/MainForm.lista_jugadores_1Change.md

  Apaga a camisa marcada, acha a nova pelo nome e a destaca. Chamada por dois
  handlers: o `lista_jugadores_1Change` (com `ItemIndex + 1`) e o
  `lista_equiposChange`, com `1`, no fim da carga de time.

  As cores sao as do original, no `$00BBGGRR` da VCL -- que e tambem o do
  `TColor` da LCL, entao os valores passam sem conversao. `$000000FF` e
  vermelho puro; escrito como `#0000FF` seria azul.

  Os nomes de propriedade nao sao inferencia: saem dos simbolos importados que
  o corpo chama -- `TControl::SetLeft`, `SetWidth`, `SetTop`, `SetHeight`,
  `SetColor`, `BringToFront`, `SendToBack`, `TFont::SetSize`,
  `TFont::SetColor` e `TComponent::FindComponent`.

  Os 23 `dorsalN` declaram `Color = clGray` no DFM e a LCL tem
  `Transparent = True` por padrao no `TStaticText`, o que poderia engolir a
  cor de fundo -- a marcacao e feita de cor de fundo, entao seria o caso de
  falhar sem sintoma. Medido em 2026-08-11 no `:99`, gtk2: o pixel dentro de
  um `dorsalN` e (128, 128, 128), o `clGray` do DFM. A cor aparece, e nao ha o
  que compensar.

  DIVERGENCIA DELIBERADA (WTE-TASK-35): o original guarda o resultado do
  `FindComponent` sem conferir e o desreferencia na linha seguinte. Com
  numero fora da faixa 1..23 -- e `ItemIndex = -1` produz `0` -- isso e
  violacao de acesso. Aqui a marcacao apenas nao acontece. }
procedure MarcaCamisa(Numero: Integer);
var
  Achado: TComponent;
begin
  if CamisaMarcada <> nil then
  begin
    CamisaMarcada.Font.Size := 8;
    CamisaMarcada.Left := CamisaMarcada.Left + 5;
    CamisaMarcada.Width := CamisaMarcada.Width - 10;
    CamisaMarcada.Top := CamisaMarcada.Top + 5;
    CamisaMarcada.Height := CamisaMarcada.Height - 10;
    CamisaMarcada.Color := $00808080;
    CamisaMarcada.Font.Color := $00C0C0C0;
    CamisaMarcada.SendToBack;
    CamisaMarcada := nil;
  end;
  Achado := MainForm.FindComponent('dorsal' + IntToStr(Numero));
  if not (Achado is TStaticText) then
    Exit;
  CamisaMarcada := TStaticText(Achado);
  CamisaMarcada.BringToFront;
  CamisaMarcada.Left := CamisaMarcada.Left - 5;
  CamisaMarcada.Width := CamisaMarcada.Width + 10;
  CamisaMarcada.Top := CamisaMarcada.Top - 5;
  CamisaMarcada.Height := CamisaMarcada.Height + 10;
  CamisaMarcada.Color := $00FFFFFF;
  CamisaMarcada.Font.Color := $000000FF;
  CamisaMarcada.Font.Size := 14;
end;

{ Qual dos cinco `sel_barra` esta marcado -- o `0x0043459c` do original. }
var
  BarraMarcada: Integer = 0;

{ As cinco barras do time carregado agora -- o `0x00434592` do original.

  NAO e cache da camada de dados, e a distincao decide a fase 4 inteira: e o
  modelo em memoria que a EDICAO altera. O original enche estes cinco bytes ao
  trocar de time (le da imagem, um a um, com salto de setor), o
  `track_barraChange` grava neles o valor novo, e o `boton_barras2isoClick`
  (`0x0040cab8`, WTE-TASK-27) le DAQUI para gravar na imagem -- os tres tocam o
  mesmo `0x00434592`, e e por isso que ele tem de existir separado de
  `Jogo.teams[].bar_*`. Sem ele, editar uma barra mudaria a largura na tela e a
  gravacao escreveria o valor velho.

  Cinco bytes, e so com `nacional`: o original pula o laco de leitura inteiro
  quando o indice e >= 95 (`cmp eax,0x5f` / `jge` em 0x0040cefa). }
var
  BarrasEmEdicao: array[0..4] of Byte;

{ Cadeia a partir de um vetor de AnsiChar terminado em NUL, que e como a
  camada de dados guarda todo nome. }
function Cadeia(const bruto): string;
begin
  Result := string(PAnsiChar(@bruto));
end;

{ As cinco barras de forca do time `indice`, na ordem em que a tela as mostra:
  ataque, defesa, equipe, velocidade, tecnica.

  Nao le a imagem. O original calcula o endereco
  (`2352 * (t div 2048) + (t mod 2048) + 0x1e8178`, com `t = 0x45ff0 + 5*i`) e
  le cinco bytes; essa conta cai na `OFS_TEAM_BARS`, que a camada de dados ja
  carregou -- conferido byte a byte na terceira passagem da WTE-TASK-25 e
  remedido a cada build pelo `wte/tools/check_barras.py`. }
function BarraDoTime(indice, qual: Integer): ShortInt;
begin
  Result := 0;
  if indice < TIMES_NACIONAIS then
    case qual of
      0: Result := Jogo.teams[indice].bar_attack;
      1: Result := Jogo.teams[indice].bar_defence;
      2: Result := Jogo.teams[indice].bar_power;
      3: Result := Jogo.teams[indice].bar_speed;
      4: Result := Jogo.teams[indice].bar_technique;
    end
  else if indice < IDX_MODELO_ML then
    case qual of
      0: Result := Jogo.ml_teams[indice - TIMES_NACIONAIS].bar_attack;
      1: Result := Jogo.ml_teams[indice - TIMES_NACIONAIS].bar_defence;
      2: Result := Jogo.ml_teams[indice - TIMES_NACIONAIS].bar_power;
      3: Result := Jogo.ml_teams[indice - TIMES_NACIONAIS].bar_speed;
      4: Result := Jogo.ml_teams[indice - TIMES_NACIONAIS].bar_technique;
    end;
end;

{ Um dos seis nomes em caixa alta do time `indice`. }
function NomeDoTime(indice, slot: Integer): string;
begin
  if indice < TIMES_NACIONAIS then
    Result := Cadeia(Jogo.teams[indice].names[slot])
  else if indice < IDX_MODELO_ML then
    Result := Cadeia(Jogo.ml_teams[indice - TIMES_NACIONAIS].names[slot])
  else
    Result := Cadeia(Jogo.ml_default.names[slot]);
end;

{ A abreviatura de tres letras do time -- o terceiro campo de nome da tela.

  NAO e `names[2]` truncado, e a diferenca so aparece em clube de Master
  League: para Gales os dois caminhos dao `WAL` e o erro passa despercebido,
  para o Manchester `names[2]` e `ARAGON` (que o campo corta em `ARA`) enquanto
  a tela do original mostra `AGN`, que e `abbreviations[0]`. Medido na oitava
  passagem da WTE-TASK-25, comparando tela com tela. }
function AbreviaturaDoTime(indice: Integer): string;
begin
  if indice < TIMES_NACIONAIS then
    Result := Cadeia(Jogo.teams[indice].abbreviations[0])
  else if indice < IDX_MODELO_ML then
    Result := Cadeia(Jogo.ml_teams[indice - TIMES_NACIONAIS].abbreviations[0])
  else
    Result := Cadeia(Jogo.ml_default.abbreviations[0]);
end;

{ Indice do jogador `slot` do time `indice` dentro de `Jogo.players`.

  Selecao: o elenco e contiguo depois dos sem-contrato. Clube de ML: o elenco e
  uma tabela de vinculos de dois bytes, resolvida por `ResolveMlLink`. As duas
  formas sao as do `we2002_core`, ja byte-identico ao `ed.exe`. }
function IndiceDoJogador(indice, slot: Integer): LongInt;
begin
  if indice < TIMES_NACIONAIS then
    Result := JOGADORES_SEM_CONTRATO + indice * JOGADORES_POR_TIME + slot
  else if indice < IDX_MODELO_ML then
    Result := ResolveMlLink(
      @Jogo.ml_teams[indice - TIMES_NACIONAIS].link[slot * 2])
  else
    Result := ResolveMlLink(@Jogo.ml_default.link[slot * 2]);
end;

function NomeDoJogador(indice, slot: Integer): string;
var
  k: LongInt;
begin
  k := IndiceDoJogador(indice, slot);
  if (k < 0) or (k >= Length(Jogo.players)) then
    Result := ''
  else
    Result := Cadeia(Jogo.players[k].name);
end;

{ Numero de camisa do slot, COMO A TELA O MOSTRA. A selecao guarda os 23
  empacotados em cinco bits cada (`TSquadNumbers`); o clube de ML guarda um byte
  por slot.

  O `+ 1` NAO e enfeite: o formato guarda o numero base zero e a tela mostra
  base um. Os dois oraculos dizem o mesmo, por caminhos independentes --
  `0x00403f00` do `wte.exe` termina em `inc eax` nos **tres** ramos
  (`0x00403f65` para o time 48, `0x00403fae` para clube de ML, `0x0040403f`
  para selecao), e o `newWe2002`, que e byte-identico ao `ed.exe`, soma 1 ao
  exibir (`src/app/TeamView.cpp:195`) e subtrai 1 ao gravar (`:468`).

  **Quem for gravar numero -- `dorsalClick` e `scroll_dorsalChange`, desta mesma
  task -- tem de subtrair 1 aqui de volta.** O que vai para a imagem e o base
  zero; a soma existe so entre o dado e o olho.

  Este `+ 1` faltava ate 2026-08-12, e a conferencia de tela da
  [CORR-WTE-057] tinha medido a diferenca sem que ela tivesse dono. }
function NumeroDaCamisa(indice, slot: Integer): LongInt;
begin
  if indice < TIMES_NACIONAIS then
    Result := LongInt(SquadNumberAt(Jogo.teams[indice].squad_numbers, slot))
  else if indice < IDX_MODELO_ML then
    Result := Jogo.ml_teams[indice - TIMES_NACIONAIS].raw_numbers[slot]
  else
    Result := Jogo.ml_default.raw_numbers[slot];
  Result := Result + 1;
end;

{ Preenche as 23 legendas `dorsalN` -- o `0x0040b0b4`, 210 bytes.

  O original acha cada legenda por `FindComponent('dorsal' + N)` e pede o
  numero a `0x00403f00`, que le a imagem. Aqui o numero vem da camada de dados,
  pelo mesmo motivo das barras: e o mesmo byte, ja carregado. }
procedure PreencheCamisas(indice: Integer);
var
  slot: Integer;
  alvo: TComponent;
begin
  for slot := 0 to JOGADORES_POR_TIME - 1 do
  begin
    alvo := MainForm.FindComponent('dorsal' + IntToStr(slot + 1));
    if alvo is TStaticText then
      TStaticText(alvo).Caption := IntToStr(NumeroDaCamisa(indice, slot));
  end;
end;

{ Preenche uma lista de jogadores -- o `0x0040b2d8`, 1.548 bytes.

  O original le os nomes da imagem e os FILTRA: copia letra, digito, `.` e
  espaco, troca byte acima de `z` por `?` e descarta o resto (as duas tabelas
  que ele indexa sao identidade -- `wte/re/auxiliares.md`). Aqui o nome vem da
  camada de dados, ja decodificado pelo `KanjiToAscii`, que para byte
  desconhecido devolve espaco em vez de `?`.

  DIVERGENCIA DELIBERADA (WTE-TASK-35), e ela e de TELA: nenhum dos dois grava.
  Aparece so em nome com byte fora de `A-Za-z0-9. `, o que na ROM europeia nao
  acontece. }
procedure PreencheJogadores(lista: TComboBox; indice: Integer);
var
  slot: Integer;
begin
  lista.Items.BeginUpdate;
  try
    lista.Items.Clear;
    for slot := 0 to JOGADORES_POR_TIME - 1 do
      lista.Items.Add(NomeDoJogador(indice, slot));
  finally
    lista.Items.EndUpdate;
  end;
end;

{ `TimeEmEdicao` e `JogadorEmEdicao` moraram aqui ate a decima segunda passagem
  da WTE-TASK-26. Estao no `we2002_estado`, com o porque: o `jugador` passou a
  le-las, e o `uses` gerado sai na interface -- `ep2002_jugador` usando
  `ep2002_mainform` seria referencia circular. }

{ ------------------------------------------------------------------------ }
{ O BUFFER DE JOGADOR -- `0x004335ec`, registros de 44 bytes (WTE-TASK-26).

  Nao e cache, pela mesma razao que o `BarrasEmEdicao` nao e: e o modelo em
  memoria que os oito handlers de mover jogador leem e escrevem. O original
  guarda tres em uso -- 0 e o DESTINO, 1 e o lado esquerdo da tela
  (`lista_equipos_1`/`lista_jugadores_1`) e 2 e o direito. O indice NAO
  distingue origem de destino: ele distingue LADO. `paderechaClick` carrega o
  1 e grava a partir dele; `paizquierdaClick` carrega o 2 e grava a partir
  dele; os dois terminam recarregando o buffer do lado que mudou.

  O layout saiu de duas leituras independentes que fecharam nos oito
  deslocamentos -- a leitora `0x004046e8` (setima passagem) e a escritora
  `0x00404820` (oitava):

    +0x00  10 B  nome
    +0x0a  12 B  atributos
    +0x16   1 B  identidade, primeiro byte
    +0x17   1 B  identidade, segundo byte
    +0x18   1 B  o campo condicional
    +0x19   1 B  tipo
    +0x1c   4 B  offset do nome na imagem
    +0x20   4 B  offset dos atributos
    +0x28   4 B  offset do condicional, ou ZERO se o campo nao existe

  As tres colunas de offset (`+0x1c`, `+0x20`, `+0x28`) NAO sao portadas: sao
  aritmetica sector-aware sobre a imagem, e o port le a camada de dados, que
  ja e byte-identica ao `ed.exe`. O que se porta e o que elas SIGNIFICAM --
  em particular `+0x28 = 0`, que quer dizer "este jogador nao tem o campo
  condicional na imagem". }
type
  TBufferJogador = record
    nome: array[0..10] of AnsiChar;       { +0x00, 10 B + terminador }
    atributos: array[0..11] of ShortInt;  { +0x0a }
    condicional: ShortInt;                { +0x18 }
    ident_time: Byte;                     { +0x16 }
    ident_slot: Byte;                     { +0x17 }
    tipo: Byte;                           { +0x19 }
    tem_condicional: Boolean;             { +0x28 <> 0 }
  end;

const
  { Os buffers, e eles nao sao tres.

    0, 1 e 2 sao o destino e os dois lados da tela. Do 3 em diante comeca a
    LISTA DE DESCARTE: o `parribaClick` carrega para o buffer
    `lista_descarte.ItemIndex + 3` e o `pabajoClick` grava a partir do mesmo,
    o que da 23 buffers a mais, um por linha da lista.

    E dai sai o ramo `indice > 2` do `0x00404374`, que a oitava passagem viu
    sem saber de quem era: para esses buffers ele sobrescreve a identidade com
    `+0x16 := 0xff` e o tipo com `+0x19 := 3` depois de calcular tudo. `0xff`
    nao e indice de time valido, entao um jogador vindo do descarte NUNCA bate
    identidade com o destino -- a recusa `-2` nao alcanca esse caminho. }
  BUF_DESTINO       = 0;
  BUF_ESQUERDA      = 1;
  BUF_DIREITA       = 2;
  BUF_DESCARTE_BASE = 3;
  BUF_ULTIMO        = BUF_DESCARTE_BASE + JOGADORES_POR_TIME - 1;  { 25 }

  { O `+0x19`. Lido do `0x00404374`. }
  TIPO_NACIONAL   = 0;  { selecao ou all-star: identidade = (time, slot)      }
  TIPO_ML_VINCULO = 1;  { clube de ML apontando para um jogador de selecao    }
  TIPO_ML_BLOCO   = 2;  { clube de ML com bloco proprio                       }
  TIPO_SOLTO      = 3;  { buffer de descarte, ou slot marcado como vazio      }

  { O `0xff` que o ramo `indice > 2` poe na identidade. }
  IDENT_NENHUMA = $FF;

  { Os codigos que `0x00404820` devolve e que `0x00403e20` traduz em mensagem. }
  COD_MESMO_JOGADOR  = -2;
  COD_SEM_BLOCO_ML   = -1;
  COD_GRAVOU         =  1;

  { O `0x32` que a `0x004046e8` escreve quando o campo condicional nao existe
    na imagem para aquele jogador. }
  CONDICIONAL_AUSENTE = 50;

  { `TIMES_SEM_CONDICIONAL` mudou para o `we2002_estado` junto com
    `TimeEmEdicao` -- a ficha precisa da mesma regra. }

var
  BufferJogador: array[BUF_DESTINO..BUF_ULTIMO] of TBufferJogador;

  { O `BYTE[0x00434640 + i]`: a linha `i` da lista de descarte tem jogador.

    O `parribaClick` a marca ao encher a linha; o `pabajoClick` recusa com
    "Selecione um jogador para mover!!!" quando ela esta zerada. Nasce toda
    zero, como a `.bss` do original. }
  DescarteOcupado: array[0..JOGADORES_POR_TIME - 1] of Boolean;

  { O `BYTE[0x00423169]`, e ele NAO e o `0x00423168` do vizinho acima.

    O `paderechaeizquierdaClick` o liga antes das duas gravacoes da troca e o
    desliga depois; quem o le e a rotina de gravacao, uma vez, em
    `0x00404bc4` -- dentro da metade que e da [WTE-TASK-27]. Aqui ele so e
    ligado e desligado na hora certa, para que aquela metade o encontre como
    encontraria no original. }
  TrocaEmCurso: Boolean = False;

  { O `BYTE[0x00423168]`: desliga a recusa de jogador repetido.

    Nasce zero no arquivo e ha UMA escrita no `.text` inteiro -- `mov BYTE
    ds:0x423168,1` em `0x0040fd7a`, dentro do corpo do `mostrar_jugadorClick`
    (`0x0040f8d4`..`0x00410220`), na mesma vizinhanca em que ele marca um
    buffer como vazio. Nenhum outro `mov` alcanca o endereco.

    Aqui ele so existe e continua False: quem o ligaria e o preenchimento da
    ficha do jogador, que ainda nao foi lido. Enquanto isso, a recusa `-2`
    vale sempre -- como vale no original ate alguem abrir a ficha. }
  IgnoraJogadorRepetido: Boolean = False;

  { O contador de blocos de Master League livres -- o `WORD[0x004335c0]`.

    QUEM O CALCULA E A [WTE-TASK-33]. Aqui ele existe porque os oito handlers
    de mover o exibem no `casilla_xmlibres` ao terminar, e porque a recusa
    `-1` o consulta. Enquanto a 33 nao rodar, ele vale zero e o rotulo mostra
    zero -- lacuna declarada, com dono escrito, em vez de uma linha de
    handler omitida em silencio. }
  BlocosLivresDeMl: Word = 0;

{ PreparaBuffer -- 0x00404374, 881 bytes.

  Calcula, para o par (time, slot), a IDENTIDADE do jogador, o tipo e se o
  campo condicional existe. NAO le nome nem atributos: quem faz isso e a
  `CarregaJogador`, e a distincao importa -- a `0x00404820` chama esta aqui
  para o buffer de destino e nunca le o conteudo dele.

  A identidade e um par de bytes, e o que ele significa depende do time:

  - selecao (indice < 63): e literalmente `(time, slot)`;
  - clube de ML: e o PAR DE VINCULO que a imagem guarda para aquele slot. O
    original le os dois bytes do arquivo; aqui eles vem de `link[slot*2]`, que
    e o mesmo par que o `ResolveMlLink` do `we2002_core` consome.

  E dai sai a regra de recusa do lote de mover: dois clubes de ML que apontem
  para o mesmo jogador de selecao tem a MESMA identidade, e mover um para o
  outro e recusado. Comparar indice resolvido daria o mesmo resultado; o
  original compara o par, e e o par que esta reproduzido.

  O segundo byte >= 23 e o que separa vinculo de bloco proprio -- o mesmo
  `slot > 22` do `ResolveMlLink`. }
procedure PreparaBuffer(indice, slot, buffer: Integer);
var
  vinculo: PByte;
begin
  if (buffer < BUF_DESTINO) or (buffer > BUF_ULTIMO) then
    Exit;
  if indice < TIMES_NACIONAIS then
  begin
    BufferJogador[buffer].ident_time := Byte(indice);
    BufferJogador[buffer].ident_slot := Byte(slot);
    BufferJogador[buffer].tipo := TIPO_NACIONAL;
  end
  else
  begin
    if indice < IDX_MODELO_ML then
      vinculo := @Jogo.ml_teams[indice - TIMES_NACIONAIS].link[slot * 2]
    else
      vinculo := @Jogo.ml_default.link[slot * 2];
    BufferJogador[buffer].ident_time := vinculo[0];
    BufferJogador[buffer].ident_slot := vinculo[1];
    if vinculo[1] >= JOGADORES_POR_TIME then
      BufferJogador[buffer].tipo := TIPO_ML_BLOCO
    else
      BufferJogador[buffer].tipo := TIPO_ML_VINCULO;
  end;
  BufferJogador[buffer].tem_condicional :=
    (BufferJogador[buffer].tipo = TIPO_ML_BLOCO)
    or not (BufferJogador[buffer].ident_time in TIMES_SEM_CONDICIONAL);
  { O ramo `indice > 2`, e ele vem DEPOIS de tudo, sobrescrevendo. Buffer de
    descarte nao tem identidade que valha: `0xff` nao e indice de time. }
  if buffer > BUF_DIREITA then
  begin
    BufferJogador[buffer].ident_time := IDENT_NENHUMA;
    BufferJogador[buffer].tipo := TIPO_SOLTO;
  end;
end;

{ CarregaJogador -- 0x004046e8, 164 bytes.

  Enche um dos buffers com o jogador do par (time, slot): 10 bytes de nome,
  12 de atributos e o byte condicional -- ou o literal 50 quando o campo nao
  existe na imagem para aquele jogador.

  O original le da imagem pelos offsets que a `PreparaBuffer` acabou de
  calcular; aqui o dado vem da camada de dados, pelo mesmo motivo das barras e
  do numero de camisa: e o mesmo byte, ja carregado (§4.2, §4.5 do plano).

  O CAMPO CONDICIONAL TEM UMA DIVERGENCIA MEDIDA E AINDA SEM RESPOSTA, e ela
  esta escrita na spec do `paderechaClick`: o `wte.exe` calcula o offset dele
  em `0x2ece0c + 23*time + slot + 2*(time div 56)` e o `we2002_core` le a
  mesma coisa a partir de `OFS_COST_NATIONAL = 3067404 = 0x2ecc0c`, com o furo
  em outro lugar. Os dois discordam do ENDERECO e concordam na REGRA (quais
  jogadores nao tem o campo). Aqui ele sai do `cost` do modelo, que e o campo
  de mesmo papel, mesma largura e mesma ausencia; qual dos dois offsets esta
  certo e pergunta da [WTE-TASK-30], e nada nesta task le o valor. }
procedure CarregaJogador(indice, slot, buffer: Integer);
var
  k: LongInt;
  b: Integer;
begin
  if (buffer < BUF_DESTINO) or (buffer > BUF_ULTIMO) then
    Exit;
  PreparaBuffer(indice, slot, buffer);
  k := IndiceDoJogador(indice, slot);
  if (k < 0) or (k >= Length(Jogo.players)) then
    Exit;
  for b := 0 to 9 do
    BufferJogador[buffer].nome[b] := Jogo.players[k].name[b];
  BufferJogador[buffer].nome[10] := #0;
  for b := 0 to 11 do
    BufferJogador[buffer].atributos[b] := Jogo.players[k].raw_attributes[b];
  if BufferJogador[buffer].tem_condicional then
    BufferJogador[buffer].condicional := ShortInt(Jogo.players[k].cost)
  else
    BufferJogador[buffer].condicional := CONDICIONAL_AUSENTE;
end;

{ MostraCodigo -- 0x00403e20, 224 bytes.

  Traduz o codigo que a rotina de gravacao devolveu em uma das duas mensagens
  do usuario, no `ficha_error`. O original soma 2 ao codigo e indexa uma
  tabela de salto de cinco entradas em `0x00403e46`; as tres ultimas (0, 1, 2)
  apontam para a saida, e codigo fora de -2..2 nao entra na tabela -- a
  comparacao e sem sinal, entao -3 vira um numero enorme e cai fora.

  As duas cadeias sao as do binario, em `0x00424767` e `0x0042478d`, copiadas
  caractere a caractere. }
procedure MostraCodigo(codigo: Integer);
begin
  case codigo of
    COD_MESMO_JOGADOR:
      begin
        ficha_error.etiq1.Caption := 'It''s the same player in both teams...';
        ficha_error.ShowModal;
      end;
    COD_SEM_BLOCO_ML:
      begin
        ficha_error.etiq1.Caption :=
          'You need at least 1 memory block free to do that';
        ficha_error.ShowModal;
      end;
  end;
end;

{ GravaJogador -- 0x00404820, 1459 bytes. METADE ESCRITA, METADE DA WTE-TASK-27.

  O que esta aqui e a metade que decide: prepara o buffer 0 com a identidade
  do DESTINO e recusa com -2 quando ela bate com a do buffer de origem. A
  regra tem uma valvula, e ela e do original: `IgnoraJogadorRepetido`.

  O QUE NAO ESTA AQUI, e o dono esta nomeado: a gravacao. A rotina do original
  escreve os 10 bytes de nome, os 12 de atributos e o byte condicional no
  destino, direto no arquivo (`0x00403400`), mais o numero de camisa quando o
  slot e o 48 (`0x00404048`); e, quando o destino e um clube de ML sem bloco
  proprio, aloca um bloco livre, atualiza a tabela de vinculos e decrementa o
  contador -- e dai sai o outro codigo de recusa, `-1`, quando nao ha bloco.
  Isso e escrita na imagem, e a WTE-TASK-27 e a unica com gate por byte;
  escrever aqui devolveria duas causas possiveis a cada golden vermelho, que e
  o que a separacao entre a 26 e a 27 existe para evitar.

  Consequencia, aceita e registrada (opcao A da decisao de 2026-08-12): os
  handlers de mover ficam com veredito `aberto` ate a 27, como o
  `dorsalClick`. }
function GravaJogador(origem, indice, slot: Integer): Integer;
begin
  Result := COD_GRAVOU;
  if (origem < BUF_DESTINO) or (origem > BUF_ULTIMO) then
    Exit;
  PreparaBuffer(indice, slot, BUF_DESTINO);
  if (BufferJogador[origem].ident_time = BufferJogador[BUF_DESTINO].ident_time)
     and (BufferJogador[origem].ident_slot
          = BufferJogador[BUF_DESTINO].ident_slot)
     and not IgnoraJogadorRepetido then
  begin
    Result := COD_MESMO_JOGADOR;
    Exit;
  end;
  { A GRAVACAO E DA WTE-TASK-27 -- ver o cabecalho. Ate la o retorno e o do
    caminho feliz, e nenhum byte da imagem muda. }
end;

{ RepovoaAsDuasListas -- 0x0040b934, 181 bytes.

  Repovoa os dois combos de jogador preservando a selecao de cada um, e e o
  que o `paderechaeizquierdaClick` usa no lugar do repovoamento inline que os
  outros handlers de mover fazem.

  A ASSIMETRIA E DO ORIGINAL: o lado esquerdo e repovoado sempre, o direito so
  se `lista_jugadores_2.Enabled`. O teste e uma chamada virtual ao slot
  `+0x50` do VMT, que o `vcl60.bpl` diz ser `TControl::GetEnabled` -- medido
  pelo mesmo caminho que deu o `SetEnabled` em `+0x64`.

  Ela pega o formulario pelo ponteiro global `0x00434360` (`_MainForm`), nao
  por `this`: nao e metodo, e um procedimento solto. }
procedure RepovoaAsDuasListas;
var
  sel1, sel2: Integer;
begin
  sel1 := MainForm.lista_jugadores_1.ItemIndex;
  sel2 := MainForm.lista_jugadores_2.ItemIndex;
  PreencheJogadores(MainForm.lista_jugadores_1,
                    MainForm.lista_equipos_1.ItemIndex);
  MainForm.lista_jugadores_1.Update;
  MainForm.lista_jugadores_1.ItemIndex := sel1;
  if not MainForm.lista_jugadores_2.Enabled then
    Exit;
  PreencheJogadores(MainForm.lista_jugadores_2,
                    MainForm.lista_equipos_2.ItemIndex);
  MainForm.lista_jugadores_2.Update;
  MainForm.lista_jugadores_2.ItemIndex := sel2;
end;

{ O nome do jogador recortado do item de um combo.

  Os itens tem a forma `<n>. <NOME>`, e o original comeca no caractere 4 ou 5
  conforme o indice tenha um ou dois digitos -- aritmetica de largura de
  numero, nao de conteudo. O `dorsalClick` faz a mesma conta inline, como o
  original faz nos dois lugares. }
function NomeDoItemSelecionado(lista: TComboBox): string;
var
  origem: Integer;
begin
  Result := '';
  if (lista.ItemIndex < 0) or (lista.ItemIndex >= lista.Items.Count) then
    Exit;
  origem := 4;
  if lista.ItemIndex < 9 then
    Inc(origem);
  Result := Copy(lista.Items[lista.ItemIndex], origem, 10);
end;

{ A legenda de uma linha da lista de descarte: `'  1 NOME'` ate `'23 NOME'`.

  O NUMERO PASSA POR UM `Currency`, e essa e a armadilha do corpo do
  `parribaClick`. Ele multiplica `slot + 1` por 10.000 com o `__llmul` da RTL
  e converte com `SysUtils::CurrToStr` -- e 10.000 e exatamente a escala do
  tipo `Currency` da Borland, entao a conta nao produz 10.000: produz `'1'`.
  Lido como inteiro, o `* 10000` pareceria preco.

  As duas larguras batem com o que o proprio `.dfm` traz de fabrica (`'  1
  ...'` ate `'23 ...'`): ate 9 sao duas casas de recuo, dai em diante uma. }
function LegendaDoDescarte(slot: Integer; const nome: string): string;
begin
  if slot < 9 then
    Result := '  ' + IntToStr(slot + 1) + ' ' + nome
  else
    Result := IntToStr(slot + 1) + ' ' + nome;
end;

{ Os quatro botoes de mover jogador tem um so par de corpos, e as duas formas
  abaixo sao esse par. O que muda entre `paderecha` e `paizquierda` e apenas
  qual lado e a origem -- os buffers acompanham o LADO, nao o papel.

  A GUARDA E LIDA ANTES DE QUALQUER COISA: o `ItemIndex` da lista de DESTINO,
  que o repovoamento seguinte perderia. O original a restaura depois de
  repovoar, e so entao recarrega o buffer daquele lado.

  DIVERGENCIA DELIBERADA (WTE-TASK-35), de robustez: o original nao confere
  `ItemIndex >= 0` em lugar nenhum, e com lista vazia calcularia offset a
  partir de -1. Aqui os quatro saem sem fazer nada. Nao e alcancavel pela tela
  com imagem carregada.

  `ItemIndex :=` num `TComboBox` da LCL NAO dispara `OnChange` -- medido pelo
  [`check_lcl_combo.py`](../../tools/check_lcl_combo.py), e e o mesmo que o
  `SetItemIndex` da VCL fazia. Se disparasse, a restauracao da guarda
  reentraria na carga de jogador. }
procedure MoveUmJogador(equipos_org, jugadores_org,
                        equipos_dst, jugadores_dst: TComboBox;
                        buf_org, buf_dst: Integer);
var
  guarda, codigo: Integer;
begin
  guarda := jugadores_dst.ItemIndex;
  if (equipos_org.ItemIndex < 0) or (jugadores_org.ItemIndex < 0)
     or (equipos_dst.ItemIndex < 0) or (guarda < 0) then
    Exit;
  CarregaJogador(equipos_org.ItemIndex, jugadores_org.ItemIndex, buf_org);
  codigo := GravaJogador(buf_org, equipos_dst.ItemIndex, guarda);
  if codigo >= 0 then
  begin
    PreencheJogadores(jugadores_dst, equipos_dst.ItemIndex);
    jugadores_dst.Update;
    jugadores_dst.ItemIndex := guarda;
    CarregaJogador(equipos_dst.ItemIndex, jugadores_dst.ItemIndex, buf_dst);
  end;
  MainForm.casilla_xmlibres.Caption := IntToStr(BlocosLivresDeMl);
  MostraCodigo(codigo);
end;

{ A forma de LOTE -- os dois botoes `paderecha2`/`paizquierda2`.

  TRES DIFERENCAS PARA A FORMA DE UM SO, e as tres sao medidas:

  1. **Ela pergunta.** `ficha_movertodos` sobe como modal e o laco so roda se
     o resultado for `mrYes` (o `6` que o `.dfm` poe no `BitBtn1`, e o mesmo
     `cmp eax,0x6` do binario). Esta e a tela do lote de 23 -- NAO e a do
     `paderechaeizquierdaClick`, que o enunciado da task atribuia a ela e que,
     medido, nao a abre.
  2. **Ela ignora o codigo de retorno.** As 23 gravacoes nao sao conferidas e
     `MostraCodigo` nao e chamada: mover um elenco inteiro para um time que ja
     tenha um daqueles jogadores nao produz mensagem nenhuma.
  3. **Ela repovoa sempre**, sem depender de o lote ter dado certo. }
procedure MoveTodosOsJogadores(equipos_org, equipos_dst,
                               jugadores_dst: TComboBox;
                               buf_org, buf_dst: Integer);
var
  guarda, slot: Integer;
begin
  guarda := jugadores_dst.ItemIndex;
  if (equipos_org.ItemIndex < 0) or (equipos_dst.ItemIndex < 0)
     or (guarda < 0) then
    Exit;
  if ficha_movertodos.ShowModal <> mrYes then
    Exit;
  for slot := 0 to JOGADORES_POR_TIME - 1 do
  begin
    CarregaJogador(equipos_org.ItemIndex, slot, buf_org);
    GravaJogador(buf_org, equipos_dst.ItemIndex, slot);
  end;
  PreencheJogadores(jugadores_dst, equipos_dst.ItemIndex);
  jugadores_dst.Update;
  jugadores_dst.ItemIndex := guarda;
  CarregaJogador(equipos_dst.ItemIndex, jugadores_dst.ItemIndex, buf_dst);
  MainForm.casilla_xmlibres.Caption := IntToStr(BlocosLivresDeMl);
end;

{ ------------------------------------------------------------------------ }
{ O preenchimento da ficha do jogador -- WTE-TASK-26, decima segunda passagem.

  MORA NO AUX DO `MainForm`, e nao no do `jugador`, porque e assim no original:
  o `0x0040756c` nao e metodo do formulario da ficha. E rotina solta que o
  handler do `MainForm` chama, e ela alcanca os controles pelo ponteiro global
  `0x00433e38` (`_jugador`) -- a mesma forma da `MarcaCamisa`, que alcanca o
  `MainForm` por `0x00434360`.

  E ha uma razao de Pascal que aponta para o mesmo lugar: o `uses` que o
  gerador emite sai na INTERFACE, entao `ep2002_jugador` nao pode usar
  `ep2002_mainform`. Rotina que precisa dos dois lados so cabe aqui. }

const
  { Os dois lacos do `0x0040756c`, e quantas voltas cada um da. }
  CAMPOS_HABILIDADE = 16;   { `cmp edi,0x10` do primeiro laco  }
  CAMPOS_APARENCIA  = 12;   { `cmp edi,0xc`  do segundo        }

{ PreencheFicha -- 0x0040756c, 1275 bytes.

  Enche a ficha do jogador. O corpo do original NAO tem deslocamento de bit
  nenhum: ele percorre duas tabelas de registros de 12 bytes em `.data`
  (`0x00423648`, 16 registros; `0x00423708`, 12) no formato
  `(byte, bit inicial, largura)` e chama o extrator `0x00403278` com cada uma.

  OS 28 REGISTROS BATEM COM O `TPlayer.Decode`, um a um -- conferido a cada
  build pelo `wte/tools/check_bitfields.py`, que le as tabelas do `.exe` e
  exige a expressao correspondente no `we2002_player.pas`. E por isso que aqui
  nao ha aritmetica de bit: os valores vem da camada de dados, ja
  desempacotados, na ORDEM DAS TABELAS -- que e a ordem em que o original os
  consome, e portanto a ordem dos controles na tela.

  Os controles sao achados POR NOME, como no original (`FindComponent` sobre
  `'<prefixo>' + IntToStr(n)`, com n de 1 a 16 ou 1 a 12), nao por campo do
  formulario:

    barrhab<n>    TScrollBar  Position := valor cru (0..7)
    valorhab<n>   TLabel      Caption  := valor + 12; fonte AMARELA se cru >= 5
    imghab<n>     TImage      Width    := 7 * cru + 8
    flechasapa<n> TUpDown     Position := valor cru
    valorapa<n>   TLabel      Caption  := ver abaixo

  O `12 +` e o `>= 5` sao do original; o `7*v + 8` e a largura da barrinha, da
  mesma familia do `11*v + 9` das barras de forca do time. }
procedure PreencheFicha(const p: TPlayer; indice, slot: Integer);

  function Controle(const prefixo: string; n: Integer): TComponent;
  begin
    Result := jugador.FindComponent(prefixo + IntToStr(n));
  end;

  { Uma volta do primeiro laco. `valor` e o valor JA somado de 12, como o
    `TPlayer.Decode` o entrega; o cru e `valor - 12`. }
  procedure Habilidade(n, valor: Integer);
  var
    cru: Integer;
    c: TComponent;
  begin
    cru := valor - 12;
    if cru < 0 then
      cru := 0;
    c := Controle('barrhab', n);
    if c is TScrollBar then
      TScrollBar(c).Position := cru;
    c := Controle('imghab', n);
    if c is TControl then
      TControl(c).Width := 7 * cru + 8;
    c := Controle('valorhab', n);
    if not (c is TLabel) then
      Exit;
    TLabel(c).Caption := IntToStr(valor);
    { O `0x00406fb4`, 44 bytes: amarelo a partir de 5, branco abaixo. }
    if cru >= 5 then
      TLabel(c).Font.Color := $0000FFFF
    else
      TLabel(c).Font.Color := $00FFFFFF;
  end;

  { Uma volta do segundo laco. `cru` e o valor de bit; `legenda` e o que vai
    para o rotulo, ou vazio quando o original o tira de uma tabela que ainda
    nao foi medida (ver as notas da spec). }
  procedure Aparencia(n, cru: Integer; const legenda: string);
  var
    c: TComponent;
  begin
    c := Controle('flechasapa', n);
    if c is TUpDown then
      TUpDown(c).Position := cru;
    if legenda = '' then
      Exit;
    c := Controle('valorapa', n);
    if c is TLabel then
      TLabel(c).Caption := legenda;
  end;

begin
  { Primeiro laco -- a ordem e a da tabela `0x00423648`, e ela e a mesma do
    `bitfields.md`. }
  Habilidade(1, p.attack);
  Habilidade(2, p.defence);
  Habilidade(3, p.strength);
  Habilidade(4, p.stamina);
  Habilidade(5, p.speed);
  Habilidade(6, p.acceleration);
  Habilidade(7, p.passing);
  Habilidade(8, p.shot_power);
  Habilidade(9, p.shot_accuracy);
  Habilidade(10, p.jump);
  Habilidade(11, p.heading);
  Habilidade(12, p.technique);
  Habilidade(13, p.dribbling);
  Habilidade(14, p.swerve);
  Habilidade(15, p.aggression);
  Habilidade(16, p.reflexes);

  { Segundo laco -- tabela `0x00423708`. As legendas dos campos ENUMERADOS
    ficam vazias de proposito: o original as tira de um vetor de 12x8
    `AnsiString` em `0x00423798`, que nasce zerado no arquivo e e preenchido em
    tempo de execucao por codigo que ainda nao foi lido. Inventar as cadeias
    seria escrever ficcao no lugar de medicao. Os dois campos NUMERICOS -- os
    unicos que o original monta com `IntToStr` -- estao aqui. }
  Aparencia(1, p.position, '');
  Aparencia(2, p.skin_colour, '');
  Aparencia(3, p.hair_style, '');
  Aparencia(4, p.hair_colour, '');
  Aparencia(5, p.beard_style, '');
  Aparencia(6, p.beard_colour, '');
  Aparencia(7, p.height - 148, IntToStr(p.height));
  Aparencia(8, p.build, '');
  Aparencia(9, p.age - 15, IntToStr(p.age));
  Aparencia(10, p.boots, '');
  Aparencia(11, p.foot, '');
  Aparencia(12, p.out_of_position, '');

  { O bloco final: quando o jogador nao tem o campo condicional na imagem, o
    original escreve o literal e DESABILITA o controle -- `call [ecx+0x64]`, o
    `TControl::SetEnabled` virtual que a WTE-TASK-25 identificou. }
  jugador.casilla_precio.Enabled := JogadorTemCampoCondicional(indice, slot);
  if jugador.casilla_precio.Enabled then
    jugador.casilla_precio.Text := IntToStr(p.cost)
  else
    jugador.casilla_precio.Text := IntToStr(CONDICIONAL_AUSENTE);
end;

{ Qual lado da tela disparou -- titular ou reserva.

  O original NAO compara o ponteiro do `Sender` com o do botao: ele le o campo
  `Name` do componente e o compara com a cadeia do botao titular
  (`'mostrar_jugador_1'` em 0x00424f57, `'mostrar_estrategia_1'` em
  0x00425001). Reproduzido como esta: comparar ponteiro daria o mesmo
  resultado hoje e deixaria de dar no dia em que alguem religar o evento a
  outro controle com o mesmo nome, que e exatamente o que o original tolera. }
function LadoTitular(Sender: TObject; const nome_titular: string): Boolean;
begin
  Result := (Sender is TComponent)
            and (TComponent(Sender).Name = nome_titular);
end;

