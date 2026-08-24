{ Rotinas internas do MainForm -- WTE-TASK-25.

  O original chama rotinas que NAO sao metodo publicado, e algumas de mais de
  um handler. Elas nao cabem num `.inc` por handler, e e por isso que este
  arquivo existe; ver `wte/src/impl/README.md`.

  Cada uma traz o endereco no `.exe` e a medicao que a sustenta. O inventario
  das 91 rotinas internas que o grupo de carga alcanca esta em
  `wte/re/auxiliares.md`. }

const
  { O ultimo indice das tabelas de comprimento por time (`0..94`). O item 95
    do combo e o time-modelo, que nao tem linha propria: o original mede o
    registro 0 para ele, que e o do time 94. Ver `IndiceNaTabela`. }
  ULTIMO_TIME_COM_TABELA = 94;


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

const
  { A aritmetica de endereco das barras, do `boton_barras2isoClick`
    (`0x0040cab8`). O original nao usa `OFS_TEAM_BARS`: ele calcula
    `0x45FF0 + 5*idx` como indice de byte no fluxo de DADOS a partir do setor
    850, e converte para offset absoluto na hora.

    Os tres numeros sao do disassembly. `850 * 2352 + 24 = 1999224 = 0x1E8178`
    e a base que ele soma; `0x45FF0` poe o time 0 em 2328184, que e o
    `OFS_TEAM_BARS` do `we2002_core` -- as duas fontes concordam, e a spec traz
    a conferencia na fronteira de setor, que e onde elas poderiam divergir. }

  BARRAS_SETOR_BASE  = SETOR_BASE_DADOS;
  BARRAS_LOGICO_BASE = $45FF0;
  BARRAS_POR_TIME    = 5;

{ Leva as cinco barras do buffer de edicao para o modelo em memoria.

  NAO tem correspondente no original, e nao precisa ter: o `wte.exe` rele a
  imagem a cada troca de time, entao o disco e a fonte dele. O port carrega uma
  vez. Ver a spec do `boton_barras2isoClick`. }
procedure GuardaBarrasNoModelo(indice: Integer);
begin
  if (indice < 0) or (indice >= IDX_MODELO_ML) then
    Exit;
  if indice < TIMES_NACIONAIS then
    with Jogo.teams[indice] do
    begin
      bar_attack    := ShortInt(BarrasEmEdicao[0]);
      bar_defence   := ShortInt(BarrasEmEdicao[1]);
      bar_power     := ShortInt(BarrasEmEdicao[2]);
      bar_speed     := ShortInt(BarrasEmEdicao[3]);
      bar_technique := ShortInt(BarrasEmEdicao[4]);
    end
  else
    with Jogo.ml_teams[indice - TIMES_NACIONAIS] do
    begin
      bar_attack    := ShortInt(BarrasEmEdicao[0]);
      bar_defence   := ShortInt(BarrasEmEdicao[1]);
      bar_power     := ShortInt(BarrasEmEdicao[2]);
      bar_speed     := ShortInt(BarrasEmEdicao[3]);
      bar_technique := ShortInt(BarrasEmEdicao[4]);
    end;
end;

{ ------------------------------------------------------------------------ }
{ OS BLOCOS DE NOME -- a tabela `0x004231a0` e a varredura que a acompanha.

  Insumo do `boton_nombres2isoClick` (`0x0040d534`, WTE-TASK-27). Spec:
  `wte/re/spec/MainForm.boton_nombres2isoClick.md`.

  Tres linhas (um campo de nome cada) por seis colunas (os blocos em que aquele
  campo e gravado). Zero quer dizer "este campo nao tem esse bloco". Os valores
  sao os 18 `DWORD` de `0x004231a0`, extraidos pela WTE-TASK-06 para
  `wte/re/offsets.tsv` e ja casados com os `OFS_*` do `we2002_core` -- por isso
  aqui eles aparecem por NOME e nao por numero. }
const
  NOME_BLOCOS: array[0..2, 0..5] of TOffset = (
    (OFS_TEAM_NAME_KANJI, OFS_TEAM_MIXED_CASE_NAME, 0, 0, 0, 0),
    (OFS_TEAM_NAME_3, OFS_TEAM_NAME_1, OFS_TEAM_NAME_4,
     OFS_ML_TEAM_NAME_7, OFS_TEAM_NAME_2, OFS_TEAM_NAME_6),
    (OFS_TEAM_ABBREV_1, OFS_TEAM_ABBREV_3, OFS_TEAM_ABBREV_2, 0, 0, 0));

  { Os blocos guardam os times em ordem INVERSA: o offset da tabela e o slot do
    time 94, e a varredura anda `94 - indice` registros para frente. O
    `we2002_core` conhece a mesma inversao pelo outro lado -- o `Save` dele
    grava `ml_teams[31-i]`. }
  ULTIMO_TIME_DOS_BLOCOS = 94;

  { O bloco 3 do campo 2 so existe para clube de Master League: e o
    `OFS_ML_TEAM_NAME_7`. Para selecao o original pula. }
  BLOCO_SO_DE_ML_CAMPO = 1;
  BLOCO_SO_DE_ML_INDICE = 3;

  { Modo de codificacao do registro. So o par (campo 0, bloco 0) --
    `OFS_TEAM_NAME_KANJI` -- usa dois bytes por caractere. }
  MODO_DOIS_BYTES = 1;
  MODO_UM_BYTE    = 2;

  NOME_BUFFER_MAX = 64;

  { A regiao de textura, do `boton_tex2isoClick` (`0x0040de18`). Vinte setores
    por time, contíguos, a partir do setor 8400 -- `8400 * 2352 + 24` e
    `20 * 2352` sao os dois literais do disassembly. Medido: com o time 2 o
    original grava os setores 8440..8459, 2048 bytes de dados em cada. }
  TEXTURA_BASE            = 19756824;
  TEXTURA_SETORES         = 20;
  TEXTURA_BYTES_POR_TIME  = 47040;

{ ------------------------------------------------------------------------ }
{ O CARTAO DE MEMORIA -- insumo do `grabar_memoryClick` (`0x0040f69c`) e da
  rotina que ele chama, o `0x0040f150`. Spec:
  `wte/re/spec/MainForm.grabar_memoryClick.md`.

  Este e o unico dos seis handlers de gravacao da WTE-TASK-27 que NAO escreve
  na imagem de CD: ele emite um arquivo `.mcr` de 128 KiB. A imagem so e lida.

  As tres regioes de origem sao enderecos LOGICOS no fluxo de dados a partir do
  setor 850 -- a mesma base das barras, `850 * 2352 + 24 = 0x1E8178`. Duas
  delas casam com um `OFS_*` do `we2002_core` e uma nao:

  | logico | passo | time 0 | `we2002_core` |
  |---|---|---|---|
  | `0x40C2C` | 30 | 2303700 | `OFS_FORMATIONS` |
  | `0x408A8` |  5 | 2302800 | **sem nome** -- ver `wte/re/offsets-novos.md` |
  | `0x46228` |  6 | 2329056 | `OFS_KICKER` |

  O `+2` quando `indice div 95` e 1 nao e enfeite: e o mesmo par de bytes que o
  `we2002_core` pula entre os 32 clubes de ML e o time-modelo (`Read(buf,2)`
  no `Load`). Ele so tem efeito no item 95 do combo. }
const
  { O LAYOUT DO CARTAO MUDOU DE CASA na WTE-TASK-28: `CARTAO_BYTES`, os
    `MCR_*` e a tabela `MCR_COBRADORES` moram agora no `we2002_mcr`, que e a
    unidade do formato -- o leitor precisa dos mesmos enderecos que o escritor,
    e ter duas copias seria ter duas verdades. O `dump_mcr.py` confere as
    constantes de la contra o `.exe` a cada `make check`.

    O que ficou AQUI e o que nao e do cartao: os enderecos LOGICOS na imagem,
    de onde os dados saem. }
  FORMACAO_LOGICO_BASE = $40C2C;   { = OFS_FORMATIONS no time 0 }
  FORMACAO_POR_TIME    = 30;
  TATICA_LOGICO_BASE   = $408A8;   { sem nome no we2002_core }
  TATICA_POR_TIME      = 5;
  COBRADOR_LOGICO_BASE = $46228;   { = OFS_KICKER no time 0 }
  COBRADOR_POR_TIME    = 6;


type
  TBlocoDeNome = record
    offset: TOffset;
    comprimento: LongInt;
    modo: Integer;
  end;

{ Acha o slot do time `indice` no bloco `(campo, bloco)`, andando pelo fluxo
  como o `0x00403c0c` do original anda.

  A varredura e a unica fonte: o original nao tem tabela de offset por time
  nem de comprimento -- ele parte do offset do bloco, pula `94 - indice`
  registros terminados em NUL (com o enchimento que vier depois) e mede o slot
  que sobrou. Reproduzir a varredura evita decidir de fora qual `OFS_*` casa
  com qual time, que e onde um port erraria calado.

  O comprimento devolvido e a LARGURA DO SLOT -- nome mais enchimento --, e e
  ela que limita a gravacao. Para o bloco de dois bytes o original ainda
  desconta um. }
function LocalizaBlocoDeNome(var img: TCdImage; campo, bloco, indice: Integer;
                             out achado: TBlocoDeNome): Boolean;
var
  base: TOffset;
  restantes, i: Integer;
  b: Byte;
  n: LongInt;
begin
  Result := False;
  achado.offset := 0;
  achado.comprimento := 0;
  achado.modo := MODO_UM_BYTE;
  if (campo < 0) or (campo > 2) or (bloco < 0) or (bloco > 5) then
    Exit;
  base := NOME_BLOCOS[campo, bloco];
  if base = 0 then
    Exit;
  restantes := ULTIMO_TIME_DOS_BLOCOS - indice;
  if restantes < 0 then
    Exit;

  img.Seek(base + 1, soBeginning);
  for i := 1 to restantes do
  begin
    { ate o fim do nome corrente... }
    repeat
      if not LeDoFluxo(img, b) then Exit;
    until b = 0;
    { ...e pelo enchimento, ate o primeiro byte do nome seguinte. }
    repeat
      if not LeDoFluxo(img, b) then Exit;
    until b <> 0;
  end;

  { O ultimo byte lido e o primeiro caractere do slot procurado. }
  achado.offset := img.Tell - 1;
  n := 1;
  repeat
    if not LeDoFluxo(img, b) then Exit;
    if b <> 0 then Inc(n);
  until b = 0;
  repeat
    if not LeDoFluxo(img, b) then Exit;
    if b = 0 then Inc(n);
  until b <> 0;
  achado.comprimento := n + 1;

  if (campo = 0) and (bloco = 0) then
  begin
    Dec(achado.comprimento);
    achado.modo := MODO_DOIS_BYTES;
  end;
  Result := achado.comprimento > 0;
end;

{ Codifica `texto` no buffer, ate `comprimento` bytes, no modo do bloco.

  DIVERGE do `AsciiToKanji` do `we2002_core` num ponto, e o ponto e o espaco: o
  `ed.exe` escreve o par `0x82 0x80` e o `wte.exe` escreve **um** `0x20`. Foi
  medido no proprio byte gravado (`27-nomes-editados`), e como este projeto
  porta o editor do Obocaman, a regra que vale e a dele.

  O original nao trata caractere fora de `[A-Za-z0-9 .]` no modo de dois bytes:
  ele deixa o segundo byte com o valor do caractere ANTERIOR. Nao ha como
  chegar la pela tela -- os tres filtros de tecla do `KeyPress` so deixam passar
  esse conjunto --, entao aqui o caractere desconhecido vira espaco em vez de
  copiar lixo. Divergencia inalcancavel, registrada na spec. }
procedure CodificaNomeDoBloco(const texto: string; comprimento: LongInt;
                              modo: Integer; out buffer: array of Byte);
var
  origem, destino: LongInt;
  c: AnsiChar;
begin
  for destino := 0 to High(buffer) do
    buffer[destino] := 0;
  origem := 1;
  destino := 0;
  while destino < comprimento do
  begin
    if origem > Length(texto) then
    begin
      { Passou do texto: o resto do slot vai a zero. }
      Inc(destino);
      Inc(origem);
      Continue;
    end;
    c := AnsiChar(texto[origem]);
    if modo = MODO_UM_BYTE then
      buffer[destino] := Byte(c)
    else if c = ' ' then
      buffer[destino] := $20
    else
    begin
      case c of
        '.':      begin buffer[destino] := $81; c := AnsiChar($44); end;
        '0'..'9': begin buffer[destino] := $82; c := AnsiChar(Byte(c) + $1F); end;
        'A'..'Z': begin buffer[destino] := $82; c := AnsiChar(Byte(c) + $1F); end;
        'a'..'z': begin buffer[destino] := $82; c := AnsiChar(Byte(c) + $20); end;
      else
        begin buffer[destino] := $82; c := AnsiChar($80); end;
      end;
      Inc(destino);
      if destino >= comprimento then
        Break;
      buffer[destino] := Byte(c);
    end;
    Inc(destino);
    Inc(origem);
  end;
end;

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

{ A FORMA da bandeira do time, e ela vem da IMAGEM, nao da tabela do `.exe`.

  O `.exe` traz uma tabela de 95 bytes com a forma *padrao* de cada time
  (`FORMA_PADRAO`, em `wte_uniformes`), e e facil supor que o desenho a use.
  Nao usa: o original le um byte do disco para `0x00432f14`, copia para
  `0x00432f15` e desenha a partir dessa copia (`0x0040d21d`). A tabela serve ao
  combo de forma do `ficha_color`, que a INDEXA -- e e por isso que os oito
  indices sem arquivo (44..51) nunca sao pedidos.

  Aqui o byte sai de `flag_shape`, que a camada de dados ja carregou do mesmo
  lugar. Detalhe na secao 3.2 do `wte/re/assets.md`. }
function FormaDaBandeira(indice: Integer): Integer;
begin
  Result := -1;
  if indice < TIMES_NACIONAIS then
    Result := Jogo.teams[indice].flag_shape
  else if indice < IDX_MODELO_ML then
    Result := Jogo.ml_teams[indice - TIMES_NACIONAIS].flag_shape;
end;

{ As 16 palavras BGR555 da bandeira do time. }
function CoresDaBandeira(indice: Integer): TCoresDoTime;
begin
  FillChar(Result, SizeOf(Result), 0);
  if indice < TIMES_NACIONAIS then
    Result := Jogo.teams[indice].flag_colours
  else if indice < IDX_MODELO_ML then
    Result := Jogo.ml_teams[indice - TIMES_NACIONAIS].flag_colours;
end;

{ As 16 do jogo `jogo` de uniforme: 0 e o Primeiro, 1 e o Segundo.

  CAMISA E CALCAO USAM AS MESMAS. Nao e simplificacao do port -- o desenhista
  do original monta o endereco duas vezes com a mesma base e o mesmo passo, uma
  por arquivo (`lea ebx,[eax*8+0x432f56]`, medido pelo `dump_render2d.py`).
  Guardar dois conjuntos inventaria um grau de liberdade que o formato nao
  tem. Das 16, o desenho alcanca as 15 primeiras.

  O PARAMETRO NAO SE CHAMA `jogo`, e a razao e uma armadilha de Pascal: o
  identificador e insensivel a caixa, entao um parametro `jogo` **sombreia** a
  global `Jogo` -- o estado da imagem carregada. O corpo abaixo precisa das
  duas coisas, e com o nome bonito o compilador so diz `Illegal qualifier` na
  linha do `Jogo.teams`, que e onde o erro NAO esta. `qual` e o mesmo nome que
  o `BarraDoTime` ja usa. }
function CoresDoUniforme(indice, qual: Integer): TCoresDoTime;
begin
  FillChar(Result, SizeOf(Result), 0);
  if indice < TIMES_NACIONAIS then
  begin
    if qual = 0 then
      Result := Jogo.teams[indice].home_kit
    else
      Result := Jogo.teams[indice].away_kit;
  end
  else if indice < IDX_MODELO_ML then
  begin
    if qual = 0 then
      Result := Jogo.ml_teams[indice - TIMES_NACIONAIS].home_kit
    else
      Result := Jogo.ml_teams[indice - TIMES_NACIONAIS].away_kit;
  end;
end;

{ Os dois limites de campo de nome, que sao POR TIME -- e sao a coisa que este
  projeto errou duas vezes seguidas por supor que fosse constante.

  O original nao guarda numero nenhum: `lista_equiposChange` percorre a tabela
  de lotes de `0x004231a0` e, para cada lote, ANDA pelo arquivo ate o registro
  do time selecionado, medindo a largura dele (`0x00403c0c`). O resultado vai
  para `0x00433a0c + linha*312 + coluna*52 + 4`, e e de la que saem as duas
  globais que o disassembly mostra:

    [0x00433a10]  linha 0 coluna 0  = OFS_TEAM_NAME_KANJI  -> TEAM_NAME_KANJI_LEN
    [0x00433b48]  linha 1 coluna 0  = OFS_TEAM_NAME_3      -> TEAM_NAME_LEN_3

  Emulada a travessia sobre a imagem japonesa, a largura medida bate com a
  tabela do `we2002_core` em 95/95 times nos dois lotes -- a do kanji vale o
  DOBRO da tabela, que e o `*2` do proprio `Load`, e e por isso que o original
  faz `div 2` num e `- 1` no outro. O `dump_truncamento.py` reconfere o
  mapeamento a cada `make check`, decodificando o operando ate a entrada de
  `0x004231a0` em vez de aceitar um destino escrito a mao.

  As duas versoes anteriores: `SizeOf(raw_kanji_name) div 2` = 20, que fechava
  a aritmetica com o campo errado, e o literal 5 lido da tela do oraculo -- que
  lia 5 porque o sexto caractere de `ABC.D ` e um espaco. }
function IndiceNaTabela(indice: Integer): Integer;
begin
  { O item 95 (time-modelo) nao tem linha. O original pede `94 - 95 = -1`
    registros de salto, o laco nao roda, e ele mede o registro 0 -- que e o do
    time 94. Reproduzido, nao arredondado. }
  if indice > ULTIMO_TIME_COM_TABELA then
    Result := ULTIMO_TIME_COM_TABELA
  else if indice < 0 then
    Result := 0
  else
    Result := indice;
end;

{ O limite do PRIMEIRO campo, e o `- 1` dele nao e chute: e um `dec` do
  original que so vale para o lote kanji.

  `0x00403c0c` termina com um caso especial testado em `0x00403d59` --
  `test edi,edi` (linha 0) e `cmp [ebp-4],0` (coluna 0):

      dec  [0x00433a10 + linha*312 + coluna*52]
      mov  [0x00433a14 + ...], 1

  O lote kanji guarda a largura MENOS UM, e o campo `+8` recebe 1 em vez do 2
  que todos os outros recebem -- e o modo do decodificador de texto
  (`0x00403598` compara com `0x82`, o byte-lider Shift-JIS): 1 = dois bytes por
  caractere, 2 = um byte.

  Como a largura do registro e `TEAM_NAME_KANJI_LEN*2`, o `div 2` do valor
  decrementado da exatamente `TEAM_NAME_KANJI_LEN - 1`.

  Medido na tela do oraculo em TRES times de larguras diferentes, digitando
  `ABCDEFGHIJKLMNOP` (CORR-WTE-064, 2026-08-18):

      time  2  (LEN  6)  ->  ABCDE          =  5
      time  0  (LEN  8)  ->  ABCDEFG        =  7
      time 56  (LEN 14)  ->  ABCDEFGHIJKLM  = 13

  A diferenca contra a derivacao ingenua era CONSTANTE em 1, nao proporcional
  -- foi isso que apontou um decremento em vez de erro de escala. Antes desta
  medicao esta funcao devolvia o literal 5, que so valia para os 59 times de
  LEN 6. }
function LimiteDoNome1(indice: Integer): Integer;
begin
  Result := TEAM_NAME_KANJI_LEN[IndiceNaTabela(indice)] - 1;
end;

function LimiteDoNome2(indice: Integer): Integer;
begin
  Result := TEAM_NAME_LEN_3[IndiceNaTabela(indice)] - 1;
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


{ O FILTRO DE NOME do `0x0040b2d8`, byte a byte.

  Ele nao e enfeite de tela desde a CORR-WTE-081: o `jugador.BitBtn3Click`
  grava os dez bytes de nome A PARTIR DO CAMPO da ficha, e o campo mostra o
  nome JA FILTRADO. Sem reproduzir o filtro, o `Comple.` do port gravaria
  outros bytes que os do oraculo -- foi assim que ele apareceu, com quatro
  bytes de diferenca num gate que so tinha esses quatro.

  A regra sai da cadeia de comparacoes de `0x0040b3ce`..`0x0040b623`, com os
  literais que cada ramo concatena lidos de `0x00424c80`:

    byte > 'z' (0x7a)                        -> `?`   (0x00424c83)
    '.'                                      -> `.`   (0x00424c85)
    ' '                                      -> ` `   (0x00424c87)
    '0'..'9', 'A'..'Z', 'a'..'z'             -> o proprio byte
    qualquer outro                           -> nada, o byte SOME

  A ordem importa e esta reproduzida: o teste do `> 'z'` vem PRIMEIRO, e os
  outros nao alcancam o byte que ja virou `?`.

  ATE AQUI O PORT MOSTRAVA O BYTE CRU, e isso estava registrado como
  divergencia deliberada da WTE-TASK-35 -- "aparece so em nome com byte fora de
  `A-Za-z0-9. `, o que na ROM europeia nao acontece". Com a ROM japonesa
  acontece em todo nome, e a divergencia deixou de ser so de tela no dia em que
  a ficha ganhou o botao que grava. }
function NomeFiltrado(const bruto): string;
var
  b: PByte;
  i: Integer;
begin
  Result := '';
  b := @bruto;
  for i := 0 to 9 do
  begin
    if b[i] = 0 then
      Break;
    if b[i] > Ord('z') then
      Result := Result + '?'
    else if (b[i] = Ord('.')) or (b[i] = Ord(' '))
            or ((b[i] >= Ord('0')) and (b[i] <= Ord('9')))
            or ((b[i] >= Ord('A')) and (b[i] <= Ord('Z')))
            or ((b[i] >= Ord('a')) and (b[i] <= Ord('z'))) then
      Result := Result + AnsiChar(b[i]);
  end;
end;

{ Nome do jogador do slot, como a lista o mostra -- ou seja, FILTRADO.

  Ficou aqui quando o resto do buffer desceu para o `wte_ficha` (CORR-WTE-081):
  ele nao e do buffer, e do combo. }
function NomeDoJogador(indice, slot: Integer): string;
var
  k: LongInt;
begin
  k := IndiceDoJogador(indice, slot);
  if (k < 0) or (k >= Length(Jogo.players)) then
    Result := ''
  else
    Result := NomeFiltrado(Jogo.players[k].name);
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

{ O texto que a legenda `dorsalN` mostra AGORA -- `N` em base um.

  O `0x0040f150` le a tela, nao o modelo: ele monta `'dorsal' + IntToStr(j+1)`,
  chama `FindComponent` e pede o `Caption`. Quem escreveu ali foi a
  `PreencheCamisas` ou uma edicao de numero da WTE-TASK-26, e essa e justamente
  a razao de o original ir a tela -- o numero editado e o que ele grava. }
function TextoDoDorsal(numero: Integer): string;
var
  alvo: TComponent;
begin
  Result := '';
  alvo := MainForm.FindComponent('dorsal' + IntToStr(numero));
  if alvo is TStaticText then
    Result := TStaticText(alvo).Caption;
end;

{ Preenche uma lista de jogadores -- o `0x0040b2d8`, 1.548 bytes.

  O original le os nomes da imagem e os FILTRA: copia letra, digito, `.` e
  espaco, troca byte acima de `z` por `?` e descarta o resto (as duas tabelas
  que ele indexa sao identidade -- `wte/re/auxiliares.md`). O port faz o mesmo
  desde a CORR-WTE-081, no `NomeFiltrado` logo acima.

  ATE LA ELE MOSTRAVA O BYTE CRU, e isso estava registrado como divergencia
  deliberada da WTE-TASK-35 -- "e ela e de TELA: nenhum dos dois grava". A
  segunda metade da frase deixou de valer no dia em que o `jugador.BitBtn3Click`
  ganhou dono: o `Comple.` grava os dez bytes de nome A PARTIR DO CAMPO da
  ficha, e o campo mostra o texto da lista. A divergencia de tela virou
  divergencia de byte, e o gate `golden-15-ficha` a mediu em quatro bytes. }
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

var
  { O `BYTE[0x00434640 + i]`: a linha `i` da lista de descarte tem jogador.

    O `parribaClick` a marca ao encher a linha; o `pabajoClick` recusa com
    "Selecione um jogador para mover!!!" quando ela esta zerada. Nasce toda
    zero, como a `.bss` do original. }
  DescarteOcupado: array[0..JOGADORES_POR_TIME - 1] of Boolean;


{ AtualizaBlocosLivresDeMl -- a `0x004042d4` mais a linha que a segue.

  O original chama a rotina de contagem em DOIS lugares, e nos dois a proxima
  instrucao e a mesma: `casilla_xmlibres.Caption := IntToStr(WORD[0x4335c0])`,
  sobre o campo `+0x434` do `MainForm` (`wte/re/campos.tsv`). Os dois lugares
  sao `MainForm.FormShow` (`0x004116df`) e `MainForm.boton_dialogo_weClick`
  (`0x0040c241`) -- ou seja, toda vez que uma imagem passa a estar aberta.

  A conta em si mora no `we2002_ml`, com a medicao em `wte/re/ml-slots.md`.
  Aqui so o par contar-e-mostrar, que e o que o original faz. }
procedure AtualizaBlocosLivresDeMl;
begin
  BlocosLivresDeMl := ContaBlocosLivresDeMl(ImagemAberta);
  MainForm.casilla_xmlibres.Caption := IntToStr(BlocosLivresDeMl);
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


{ ------------------------------------------------------------------------ }
{ O CARTAO CARREGADO -- as globais que o `boton_mcrClick` enche e o
  `boton_mcr2isoClick` consome.

  No original sao cinco vetores da `.data` (`0x00434364` os nomes, `0x0043445a`
  os atributos, `0x0043444a` os numeros, `0x0043456e` a formacao, `0x0043458c`
  os cobradores). Aqui e um registro so, e o CAMINHO fica junto porque a tatica
  nao passa por esses vetores -- o `boton_mcr2iso` a le direto do arquivo, e
  sem o caminho guardado o port nao teria de onde. }
var
  CartaoCarregado: TCartaoDeMemoria;
  CartaoCaminho: string = '';

{ CarregaJogadorDoCartao -- 0x0040478c, 145 bytes.

  Enche um buffer de jogador com o slot `slot` do cartao. Nao le da imagem:
  le do `.mcr`, e por isso e outra rotina que a `CarregaJogador`.

  AS TRES ATRIBUICOES DO FIM NAO SAO ENFEITE, e sao elas que fazem o import
  funcionar em clube de Master League:

  - `tipo := TIPO_SOLTO` poe o buffer no unico estado que leva a `0x00404820`
    ao ramo de ALOCACAO. Jogador vindo de cartao nao tem bloco na imagem: tem
    de ganhar um;
  - `ident_time := 0xFF` garante que a recusa `-2` (mesmo jogador dos dois
    lados) nunca alcance este caminho -- `0xFF` nao e indice de time;
  - `condicional := 25` e literal do original (`mov BYTE [..+0x18],0x19`). O
    cartao nao guarda o campo, e 25 e o que entra no lugar. }
procedure CarregaJogadorDoCartao(slot, buffer: Integer);
var
  b: Integer;
begin
  if (buffer < BUF_DESTINO) or (buffer > BUF_ULTIMO) then
    Exit;
  if (slot < 0) or (slot >= JOGADORES_NO_CARTAO) then
    Exit;
  for b := 0 to MCR_NOME_BYTES - 1 do
    BufferJogador[buffer].nome[b] :=
      AnsiChar(CartaoCarregado.nomes[slot * MCR_NOME_BYTES + b]);
  BufferJogador[buffer].nome[MCR_NOME_BYTES] := #0;
  for b := 0 to MCR_ATRIBUTO_BYTES - 1 do
    BufferJogador[buffer].atributos[b] :=
      ShortInt(CartaoCarregado.atributos[slot * MCR_ATRIBUTO_BYTES + b]);
  BufferJogador[buffer].condicional := CARTAO_CONDICIONAL;
  BufferJogador[buffer].tipo := TIPO_SOLTO;
  BufferJogador[buffer].ident_time := IDENT_NENHUMA;
end;

{ Quantos blocos de Master League o import PRECISARIA para o time `indice`.

  O laco de `0x0040c4a1`..`0x0040c556`, e ele e aritmetica ANTES de gravar: le
  os 23 pares de vinculo do time e conta os que teriam de ganhar bloco novo --
  vinculo para jogador de selecao (`b1 < 23`), ou bloco proprio compartilhado
  com outro slot (`ocupacao > 1`). Bloco de dono unico nao conta: ele e
  reaproveitado.

  Devolve 0 para time de selecao, e ai nao ha o que contar. }
function BlocosQueOImportPrecisa(indice: Integer): Integer;
var
  img: TCdImage;
  slot, bloco: Integer;
  b0, b1: Byte;
begin
  Result := 0;
  if (indice < TIMES_NACIONAIS) or (ImagemAberta = '') then
    Exit;
  img.Init;
  if not img.OpenRead(ImagemAberta) then
    Exit;
  try
    img.Seek(OffsetDoVinculoMl(indice, 0), soBeginning);
    for slot := 0 to JOGADORES_POR_TIME - 1 do
    begin
      if img.Read(b0, 1) <> 1 then
        Break;
      if img.Read(b1, 1) <> 1 then
        Break;
      if b1 < JOGADORES_POR_TIME then
        Inc(Result)
      else
      begin
        bloco := IndiceDoBlocoMl(b0, b1);
        if (bloco < 0) or (bloco > High(OcupacaoMl))
           or (OcupacaoMl[bloco] > 1) then
          Inc(Result);
      end;
      SaltaFronteiraDeSetor(img);
    end;
  finally
    img.Close;
  end;
end;

{ ImportaCartaoParaImagem -- o corpo do `boton_mcr2isoClick` (0x0040c46c).

  Ele NAO e um gravador novo: e um laco em volta das duas rotinas que a
  WTE-TASK-27 portou. Para cada slot enche o buffer 23 do cartao e chama a
  `GravaJogador` -- a mesma dos handlers de mover --, depois a
  `GravaNumeroDaCamisa`. So formacao, tatica e cobradores tem endereco proprio.

  Devolve `COD_SEM_BLOCO_ML` quando a conta acima nao fecha, e ai NAO GRAVA
  BYTE NENHUM. E a diferenca entre esta recusa e a da `0x00404820`: aquela
  recusa um slot, esta recusa os 23 de uma vez. Sem ela, importar num clube
  quase cheio gravaria metade do time e pararia no meio. }
function ImportaCartaoParaImagem(indice: Integer): Integer;
var
  img: TCdImage;
  slot, precisa: Integer;
  tatica: TTaticaDoCartao;
begin
  Result := COD_GRAVOU;
  if (ImagemAberta = '') or (CartaoCaminho = '') or (indice < 0) then
    Exit;

  precisa := BlocosQueOImportPrecisa(indice);
  if (indice >= TIMES_NACIONAIS) and (BlocosLivresDeMl < precisa) then
  begin
    ficha_error.etiq1.Caption := 'Voce precisa de   ' + IntToStr(precisa)
                               + ' mais blocos livres!!!.       ';
    ficha_error.ShowModal;
    Result := COD_SEM_BLOCO_ML;
    Exit;
  end;

  for slot := 0 to JOGADORES_POR_TIME - 1 do
  begin
    CarregaJogadorDoCartao(slot, BUF_CARTAO);
    GravaJogador(BUF_CARTAO, indice, slot);
    GravaNumeroDaCamisa(NumeroDoCartao(CartaoCarregado, slot), indice, slot);
    GuardaNumeroNoModelo(NumeroDoCartao(CartaoCarregado, slot), indice, slot);
  end;

  img.Init;
  if not img.OpenReadWrite(ImagemAberta) then
    Exit;
  try
    GravaNoFluxo(img, EnderecoDeDados(SETOR_BASE_DADOS,
                   FORMACAO_LOGICO_BASE + FORMACAO_POR_TIME * indice
                   + 2 * (indice div IDX_MODELO_ML)),
                 CartaoCarregado.formacao[0], FORMACAO_BYTES);
    { A tatica vem do arquivo, e nao do registro: o leitor do cartao nao a
      traz, e o original a le aqui mesmo. Sao TRES bytes gravados, embora o
      rascunho do original tenha quatro. }
    if LeTaticaDoCartao(CartaoCaminho, tatica) then
      GravaNoFluxo(img, EnderecoDeDados(SETOR_BASE_DADOS,
                     TATICA_LOGICO_BASE + TATICA_POR_TIME * indice),
                   tatica[0], 3);
    GravaNoFluxo(img, EnderecoDeDados(SETOR_BASE_DADOS,
                   COBRADOR_LOGICO_BASE + COBRADOR_POR_TIME * indice),
                 CartaoCarregado.cobradores[0], 5);
    { O capitao sai cinco bytes adiante, e SO ele leva o `+2` do time-modelo --
      `0x4622D` contra `0x46228`, mais `2 * (indice div 95)`. }
    GravaNoFluxo(img, EnderecoDeDados(SETOR_BASE_DADOS,
                   COBRADOR_LOGICO_BASE + 5 + COBRADOR_POR_TIME * indice
                   + 2 * (indice div IDX_MODELO_ML)),
                 CartaoCarregado.cobradores[COBRADORES_BYTES - 1], 1);
  finally
    img.Close;
  end;
end;

{ GravaCartaoDeMemoria -- 0x0040f150, 1.356 bytes.

  A metade do `grabar_memoryClick` que sabe de bytes. O handler escolhe o
  arquivo; esta rotina copia o molde e escreve o time por cima.

  A ordem e a do original, e ela importa em um ponto so: o molde vai INTEIRO
  primeiro, e so depois os campos. Escrever campo antes do molde os apagaria.

  O que NAO se reproduz e a origem dos bytes de jogador. O original chama a
  `0x004046e8`, que rele nome e atributos DA IMAGEM para o buffer 23; o port
  chama a `CarregaJogador`, que le a camada de dados -- ja byte-identica ao
  `ed.exe`. E a mesma divergencia declarada do `boton_barras2isoClick`: mesmo
  byte, mesma posicao, outra fonte. O buffer continua sendo o 23, com o efeito
  colateral que ele tem no original (ver `BUF_CARTAO`). }
function GravaCartaoDeMemoria(const destino: string; indice: Integer): Boolean;
var
  img: TCdImage;
  cartao: TFileStream;
  molde: TFileStream;
  bloco: array[0..CARTAO_BYTES - 1] of Byte;
  formacao: array[0..FORMACAO_POR_TIME - 1] of Byte;
  tatica: array[0..3] of Byte;
  cobrador: array[0..COBRADOR_POR_TIME - 1] of Byte;
  numeros: array[0..15] of Byte;
  salto, j, k, bit, valor: Integer;
  registro: array[0..21] of Byte;

  procedure Poe(posicao: LongInt; b: Byte);
  begin
    cartao.Position := posicao;
    cartao.Write(b, 1);
  end;

begin
  Result := False;
  if (ImagemAberta = '') or (indice < 0) or (CaminhoDatBin = '') then
    Exit;
  { O `idx div 95` do original: o par de bytes que separa os clubes de ML do
    time-modelo. So o item 95 do combo o sente. }
  salto := 2 * (indice div IDX_MODELO_ML);

  img.Init;
  if not img.OpenReadWrite(ImagemAberta) then
    Exit;
  try
    LeDoFluxoEm(img, EnderecoDeDados(SETOR_BASE_DADOS,
                  FORMACAO_LOGICO_BASE + FORMACAO_POR_TIME * indice + salto),
                formacao, FORMACAO_POR_TIME);
    LeDoFluxoEm(img, EnderecoDeDados(SETOR_BASE_DADOS,
                  TATICA_LOGICO_BASE + TATICA_POR_TIME * indice),
                tatica, SizeOf(tatica));
    LeDoFluxoEm(img, EnderecoDeDados(SETOR_BASE_DADOS,
                  COBRADOR_LOGICO_BASE + COBRADOR_POR_TIME * indice + salto),
                cobrador, COBRADOR_POR_TIME);
  finally
    img.Close;
  end;

  { Os 23 numeros de camisa saem da TELA, nao da imagem: o original le o
    `Caption` de cada `dorsalN`, tira 1 e limita a 31. Um rotulo ilegivel vira
    zero no `StrToIntDef` e, menos 1, estoura para 255 -- que o limite corta em
    31, como o `jbe` do original corta. }
  FillChar(numeros, SizeOf(numeros), 0);
  for j := 0 to JOGADORES_POR_TIME - 1 do
  begin
    valor := (StrToIntDef(TextoDoDorsal(j + 1), 0) - 1) and $FF;
    if valor > NUMERO_MAXIMO then
      valor := NUMERO_MAXIMO;
    bit := NUMERO_BITS_GRUPO * (j div NUMERO_POR_GRUPO)
         + NUMERO_BITS * (j mod NUMERO_POR_GRUPO);
    for k := 0 to NUMERO_BITS - 1 do
      if (valor and (1 shl k)) <> 0 then
        numeros[(bit + k) div 8] :=
          numeros[(bit + k) div 8] or (1 shl ((bit + k) mod 8));
  end;

  molde := nil;
  cartao := nil;
  try
    try
      molde := TFileStream.Create(CaminhoDatBin, fmOpenRead or fmShareDenyNone);
      if molde.Read(bloco, CARTAO_BYTES) <> CARTAO_BYTES then
        Exit;
      cartao := TFileStream.Create(destino, fmCreate);
      cartao.Write(bloco, CARTAO_BYTES);
    except
      Exit;
    end;

    { A formacao, partida em 10 + 20. Os dois trechos sao contiguos na imagem e
      NAO no cartao. }
    cartao.Position := MCR_FORMACAO_1;
    cartao.Write(formacao[0], 10);
    cartao.Position := MCR_FORMACAO_2;
    cartao.Write(formacao[10], FORMACAO_POR_TIME - 10);

    { A tatica: o byte 0 duas vezes -- cru e mais 50 --, e os quatro nibbles
      dos bytes 1 e 2. O byte 3 e lido e nao e usado: o extrator do original
      recebe o par (baixo, alto) e nunca pede mais de 4 bits a partir do bit 4,
      entao o byte alto nunca entra na conta. }
    Poe(MCR_TATICA_CRUA, tatica[0]);
    Poe(MCR_TATICA_MAIS50, (tatica[0] + 50) and $FF);
    Poe(MCR_TATICA_1_BAIXO, tatica[1] and $0F);
    Poe(MCR_TATICA_1_ALTO, (tatica[1] shr 4) and $0F);
    Poe(MCR_TATICA_2_BAIXO, tatica[2] and $0F);
    Poe(MCR_TATICA_2_ALTO, (tatica[2] shr 4) and $0F);

    { Os cinco cobradores, cada um no seu destino, e o capitao a parte. }
    for j := 0 to 4 do
      Poe(MCR_COBRADORES[j], cobrador[j]);
    Poe(MCR_CAPITAO, cobrador[5]);

    { Os 23 jogadores: 12 bytes de atributo, 10 de nome, 10 sem uso. O original
      grava nessa ordem -- atributo ANTES do nome --, embora no buffer o nome
      venha primeiro. }
    for j := 0 to JOGADORES_POR_TIME - 1 do
    begin
      CarregaJogador(indice, j, BUF_CARTAO);
      for k := 0 to 11 do
        registro[k] := Byte(BufferJogador[BUF_CARTAO].atributos[k]);
      for k := 0 to 9 do
        registro[12 + k] := Byte(BufferJogador[BUF_CARTAO].nome[k]);
      cartao.Position := MCR_JOGADORES + MCR_JOGADOR_PASSO * j;
      cartao.Write(registro, SizeOf(registro));
    end;

    cartao.Position := MCR_NUMEROS;
    cartao.Write(numeros, SizeOf(numeros));
    Result := True;
  finally
    cartao.Free;
    molde.Free;
  end;
end;

