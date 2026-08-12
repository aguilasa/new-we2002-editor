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

{ O time e o jogador que a ficha vai editar -- as globais `0x004335cc` e
  `0x004335dc` do original.

  Quem as enche e a navegacao (`mostrar_jugadorClick`,
  `mostrar_estrategiaClick`); quem as consome e o formulario aberto, que e da
  WTE-TASK-26. Por isso elas existem aqui e ninguem mais as le ainda. }
var
  TimeEmEdicao: Integer = -1;
  JogadorEmEdicao: Integer = -1;

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

