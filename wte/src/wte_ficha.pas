{ wte_ficha -- o buffer de jogador, a gravacao de jogador e o que a ficha
  compartilha com o `MainForm` (CORR-WTE-081).

  ESCRITO A MAO, como o `we2002_estado`, e pela mesma razao estrutural -- que
  aqui e a razao de ele existir.

  Tudo o que esta neste arquivo MORAVA no `impl/ep2002_mainform.aux.inc`. Saiu
  de la quando o `jugador.BitBtn3Click` -- o `Comple.` da ficha -- passou a
  precisar de `GravaJogador` e `GravaNumeroDaCamisa`: o `.aux.inc` e incluido
  na IMPLEMENTACAO do `ep2002_mainform`, entao nada dele e visivel de fora, e o
  `uses` que o `dfm2lfm.py` emite sai na INTERFACE, o que impede
  `ep2002_jugador` de usar `ep2002_mainform` de qualquer jeito. As duas coisas
  juntas nao deixam saida: quem os dois formularios precisam chamar tem de
  morar numa unidade que NENHUM dos dois possui. E a solucao que a
  `wte_render2d` ja tinha usado, e que a spec do
  `wte/re/spec/jugador.BitBtn1Click.md` descreveu antes de haver quem a
  executasse.

  A REGRA DE CORTE foi mecanica, e vale registrar porque ela e o que torna o
  resultado conferivel: entrou aqui o FECHO das chamadas de `GravaJogador`,
  `GravaNumeroDaCamisa` e `BufferJogador`. Nenhuma rotina daqui chama rotina
  que ficou no `.aux.inc` -- se chamasse, o corte estaria errado e o
  compilador diria. O que ficou la e o que toca a tela do `MainForm`:
  `MarcaCamisa`, `PreencheCamisas`, `PreencheJogadores`, `MostraCodigo`,
  `AtualizaBlocosLivresDeMl`, os blocos de nome, o cartao e as barras.

  `CamisaMarcada` desceu junto com o buffer, e ela e a excecao aparente: e um
  controle do `MainForm`. Quem a ATRIBUI continua sendo a `MarcaCamisa`, la;
  aqui ela so precisa existir num lugar que o `jugador` alcance, porque o
  `Comple.` reescreve o rotulo da camisa marcada quando a ficha veio do lado
  esquerdo -- o `cmp DWORD ds:0x4335c4,1` de `0x00408a8b`.

  As tres globais da ficha (`BufferDaFicha`, `NumeroNaFicha`, `NomeNaFicha`)
  sao novas AQUI mas nao no original: sao `0x004335c4`, `0x004335c8` e
  `0x004335d4`, as tres que o `mostrar_jugadorClick` enche e que o
  `PreencheFicha` e o `BitBtn3Click` leem. }

unit wte_ficha;

{$mode objfpc}{$H+}

interface

uses
  SysUtils, Classes, StdCtrls, Controls, ComCtrls,
  we2002_types, we2002_database, we2002_offsets, we2002_cdimage,
  we2002_estado, we2002_ml,
  we2002_player;  { `TPlayer`, no `PreencheFicha` (CORR-WTE-091) }

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

  { O setor de onde o original conta TODO endereco logico deste grupo. Ele
    nao e das barras: o `boton_nombres2iso`, o `grabar_memory` e o
    `mostrar_estrategia` somam o mesmo `0x1E8178`. Fica com nome proprio, e
    o das barras passa a ser um apelido dele. }
  SETOR_BASE_DADOS   = 850;

  { O buffer de jogador que o original usa como rascunho: o 23. Ele cai DENTRO
    da lista de descarte (`BUF_DESCARTE_BASE + 20`), e isso nao e engano de
    leitura -- o `0x0040f150` passa `ecx = 0x17` para a `0x004046e8`, e a
    `0x00404374` indexa o array de 44 bytes por esse valor. Emitir um cartao
    embaralha a linha 20 do descarte no original, e aqui tambem. }
  BUF_CARTAO = 23;

  { O literal que a `0x0040478c` poe no campo condicional de um jogador vindo
    de cartao (`mov BYTE PTR [..+0x18],0x19`). O `.mcr` nao guarda o campo. }
  CARTAO_CONDICIONAL = 25;

  { Os 23 numeros de camisa, 5 bits cada, em grupos de SEIS por `DWORD`: o
    original calcula `32 * (j div 6) + 5 * (j mod 6)` como posicao de bit. Sao
    30 bits usados por grupo e 2 perdidos, quatro grupos, 16 bytes -- a mesma
    forma do `SquadNumbers` do `we2002_core`. }
  NUMERO_BITS       = 5;
  NUMERO_POR_GRUPO  = 6;
  NUMERO_BITS_GRUPO = 32;
  NUMERO_MAXIMO     = 31;      { o `cmp ..,0x1f` / `jbe` do original }

  { A gravacao pontual do numero -- `0x00404048`, o irmao escritor da
    `NumeroDaCamisa`. Tres regioes, uma por ramo; ver `GravaNumeroDaCamisa`.

    Os dois enderecos que tem nome no `we2002_core` foram conferidos contra ele:
    `EnderecoDeDados(24, $4A094)` = 404716 = `OFS_SQUAD_NUMBERS_NATIONAL`, e a
    formula de ML no time 95 = 2014504 = `OFS_SQUAD_NUMBERS_ML`. }
  NUMERO_NACIONAL_SETOR  = 24;
  NUMERO_NACIONAL_LOGICO = $4A094;

  { O time 48 e o unico com ramo proprio, e o numero dele mora dentro do
    registro de atributos do jogador: `$265EC + 276*48 + 12*slot + 3`. }
  NUMERO_TIME_ALL_STAR   = 48;
  NUMERO_ALL_STAR_LOGICO = $299AF;
  NUMERO_ALL_STAR_BIT    = 2;

  { Offset ABSOLUTO, nao logico -- o ramo de ML nao passa pelo fluxo. }
  NUMERO_ML_BASE = $1EB797;

  { As tres colunas de offset do registro de jogador -- `0x00404374`, ramo de
    selecao. Insumo do `GravaJogador`; ver `OffsetsDoJogador`.

    Os dois primeiros sao LOGICOS, o terceiro e ABSOLUTO. `NOME_JOGADOR_LOGICO`
    no time 0 slot 0 da `OFS_PLAYER_NAME` = 387792, e `ATRIBUTO_LOGICO` da
    `OFS_PLAYER_ATTR` = 2179492 -- os dois nomes do `we2002_core`. }
  NOME_JOGADOR_SETOR  = 24;
  NOME_JOGADOR_LOGICO = $467F8;
  ATRIBUTO_LOGICO     = $265EC;
  CONDICIONAL_BASE    = 3067404;

  { AS MESMAS TRES COLUNAS, PARA UM BLOCO PROPRIO DE MASTER LEAGUE.

    Lidas do ramo `0x00404635` do `0x00404374` e reescritas identicas no ramo
    de alocacao do `0x00404820` (`0x00404abb`..`0x00404b6a`) -- o original
    repete a conta nos dois lugares. O indice aqui NAO e `(time, slot)`: e o
    indice LINEAR do bloco, o mesmo que a WTE-TASK-33 conta.

    As tres batem com offsets que o port ja nomeia, e essa e a conferencia:
    para o bloco 0, o nome da 2006288 = `OFS_ML_PLAYER_NAME`, os atributos dao
    2204112 = `OFS_ML_PLAYER_ATTR`, e a base do condicional E `OFS_COST_NC`.

    A ultima reenquadra o campo: para bloco de ML, o `+0x28` do buffer nao e
    condicao nenhuma -- e o CUSTO do jogador non-contract. O `OFS_COST_NC`
    estava `confirmado` no `offsets.tsv` com a evidencia
    `0x004046b9|0x00404b66`, que sao exatamente estas duas instrucoes; o que
    faltava era saber de quem elas eram. }
  ML_BLOCO_NOME_LOGICO     = $1808;     { 6152                              }
  ML_BLOCO_ATRIBUTO_LOGICO = $2B908;    { 178440                            }
  ML_BLOCO_CUSTO_BASE      = $2ED648;   { 3069512 = OFS_COST_NC, ABSOLUTO   }

  { A coluna do VINCULO, `+0x24`, do ramo `0x00404499`. So existe para time de
    Master League: para selecao o original zera o campo (`0x00404439`).

    `L = 46*time + 2*slot + 9086 - 1520*(time div 95)`, logico sobre o setor
    850. O `- 1520` so dispara no time-modelo (95), e e ele que faz o modelo
    cair ANTES dos clubes em vez de depois: para o time 63 slot 0 a conta da
    2012728 = `OFS_LINK_ML1`, e para o 95 slot 0 da 2012680 = `OFS_LINK_ML`.
    As duas batem com offsets ja versionados, e e assim que se sabe que a
    formula esta certa sem gravar nada. }
  ML_VINCULO_LOGICO = $237E;   { 9086                                       }
  ML_VINCULO_AJUSTE = 1520;    { o desconto do time-modelo                  }

  { O que o original grava no lugar do condicional, para os times 54 e 55: o
    nome numa segunda regiao e o par de identidade. Os dois absolutos. }
  NOME_JOGADOR_2_BASE = 390432;
  VINCULO_BASE        = 2326480;

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

  { Os outros dois que a `0x00404820` devolve, e que a tabela de salto do
    `0x00403e20` manda para a saida sem mensagem -- como o 1. Existem para
    quem le o codigo saber O QUE aconteceu, nao so que deu certo:
    `0` = alocou bloco novo, `2` = o bloco do destino ficou livre. }
  COD_ML_ALOCOU  = 0;
  COD_ML_LIBEROU = 2;

  { O `0x32` que a `0x004046e8` escreve quando o campo condicional nao existe
    na imagem para aquele jogador. }
  CONDICIONAL_AUSENTE = 50;

  { `TIMES_SEM_CONDICIONAL` mudou para o `we2002_estado` junto com
    `TimeEmEdicao` -- a ficha precisa da mesma regra. }

var
  BufferJogador: array[BUF_DESTINO..BUF_ULTIMO] of TBufferJogador;

  { O `0x004335e4` do original: qual `dorsalN` esta marcado agora.

    E o MESMO ponteiro da `wte/re/crash-causa.md`. La ele derruba o `wte.exe`
    com a ROM europeia porque a carga de time o sobrescreve com dado de tabela
    vizinha, e o `TFont::SetSize` seguinte cai com `this` nulo. Aqui ele e
    tipado e so recebe o que o `FindComponent` devolveu, entao o modo de falha
    do original nao tem por onde acontecer. }
  CamisaMarcada: TStaticText = nil;

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

    QUEM O ENCHE e a `AtualizaBlocosLivresDeMl` logo abaixo, com a conta do
    `we2002_ml` -- a [WTE-TASK-33] fechou em 2026-08-19. Os oito handlers de
    mover o exibem no `casilla_xmlibres` ao terminar, e a recusa `-1` o
    consulta.

    Continua nascendo zero porque antes de abrir imagem nao ha o que contar; o
    original tambem so o preenche no `FormShow` e no botao de abrir. }
  BlocosLivresDeMl: Word = 0;

var
  { AS TRES GLOBAIS DA FICHA DO JOGADOR -- `0x004335c4`, `0x004335c8` e
    `0x004335d4`.

    O `mostrar_jugadorClick` enche as tres antes de mostrar o formulario, o
    `PreencheFicha` le as duas ultimas para encher os campos de nome e de
    numero, e o `jugador.BitBtn3Click` le a primeira para saber DE QUAL buffer
    gravar. Sao estado de dois formularios, como o `TimeEmEdicao`, e por isso
    moram aqui e nao no `.aux.inc` de nenhum dos dois.

    `NomeNaFicha` nasce VAZIA e ISSO NAO E DESCUIDO NEM DAQUI NEM DE LA. No
    `.text` inteiro ha uma unica escrita em `0x004335d4` -- a de `0x004088da`,
    dentro do proprio `BitBtn3Click` --, entao a ficha abre com o campo de nome
    em branco ate que alguem clique `Comple.` uma vez. E como o `Comple.` grava
    os dez bytes de nome A PARTIR DO CAMPO, o primeiro clique escreve dez zeros
    por cima do nome do jogador. E destrutivo, e e o que o original faz. }
  BufferDaFicha: Integer = BUF_ESQUERDA;
  NumeroNaFicha: Integer = 0;
  NomeNaFicha: string = '';

{ Indice do jogador `slot` do time `indice` dentro de `Jogo.players`. }
function IndiceDoJogador(indice, slot: Integer): LongInt;

{ Numero de camisa do slot, em BASE UM -- como a tela o mostra. }
function NumeroDaCamisa(indice, slot: Integer): LongInt;

{ Identidade, tipo e existencia do campo condicional do par (time, slot). }
procedure PreparaBuffer(indice, slot, buffer: Integer);

{ Enche um buffer com o jogador do par (time, slot). }
procedure CarregaJogador(indice, slot, buffer: Integer);

{ Leva o jogador gravado para o modelo em memoria. }
procedure GuardaJogadorNoModelo(origem, indice, slot: Integer);

{ As tres colunas de offset de um bloco proprio de Master League. }
procedure OffsetsDoBlocoMl(bloco: Integer;
                           out nome, atributos, custo: TOffset);

{ Onde na imagem mora o par de vinculo do slot. Zero para selecao. }
function OffsetDoVinculoMl(indice, slot: Integer): TOffset;

{ As tres colunas de offset do registro de jogador de selecao. }
procedure OffsetsDoJogador(indice, slot: Integer;
                           out nome, atributos, condicional: TOffset);

{ Leva o par de vinculo gravado para o modelo em memoria. }
procedure GuardaVinculoNoModelo(indice, slot: Integer; b0, b1: Byte);

{ A metade de Master League da `0x00404820`. }
function GravaJogadorEmMl(origem, indice, slot: Integer): Integer;

{ Grava o jogador do buffer `origem` no par (time, slot). Devolve `COD_*`. }
function GravaJogador(origem, indice, slot: Integer): Integer;

{ A gravacao pontual do numero de camisa -- `0x00404048`. Base UM na entrada. }
procedure GravaNumeroDaCamisa(numero, indice, slot: Integer);

{ Leva o numero para o modelo em memoria. }
procedure GuardaNumeroNoModelo(numero, indice, slot: Integer);

{ Enche a ficha do jogador a partir do registro carregado -- `0x0040756c`.

  DOIS CHAMADORES, em formularios diferentes, e e por isso que ela esta na
  interface desta unidade neutra e nao num `.aux.inc`:

  - `MainForm.mostrar_jugadorClick`, que a chama antes do `ShowModal`;
  - `jugador.BitBtn1Click`, o botao `Original `, que a chama sozinho para
    recarregar a ficha e descartar o que foi digitado.

  Ver o bloco de comentario da implementacao para a razao de Pascal. }
procedure PreencheFicha(const p: TPlayer; indice, slot: Integer);

implementation

uses
  ep2002_info4,   { ficha_info4.etiq3, no aviso de bloco compartilhado }
  ep2002_jugador, { os controles da ficha, no `PreencheFicha` (CORR-WTE-091) }
  wte_legendas;   { `Legenda` e `LegendaDoCabelo`, idem }

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
  certo e pergunta da [WTE-TASK-32], e nada nesta task le o valor. }
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

{ O `GravaJogador` chama a gravacao pontual do numero, que mora mais abaixo --
  o time 48 guarda o numero dentro do registro de atributos. }

{ Leva o jogador gravado para o modelo em memoria.

  Mesma divergencia declarada das barras e do numero: o `wte.exe` rele a imagem
  a cada troca de time, o port carrega uma vez. }
procedure GuardaJogadorNoModelo(origem, indice, slot: Integer);
var
  k, b: LongInt;
begin
  k := IndiceDoJogador(indice, slot);
  if (k < 0) or (k >= Length(Jogo.players)) then
    Exit;
  for b := 0 to 9 do
    Jogo.players[k].name[b] := BufferJogador[origem].nome[b];
  for b := 0 to 11 do
    Jogo.players[k].raw_attributes[b] := BufferJogador[origem].atributos[b];
  if not (indice in TIMES_SEM_CONDICIONAL) then
    Jogo.players[k].cost := BufferJogador[origem].condicional;
end;

{ GravaJogador -- 0x00404820, 1459 bytes. DESTINO DE SELECAO PORTADO.

  O que esta aqui e a metade que decide: prepara o buffer 0 com a identidade
  do DESTINO e recusa com -2 quando ela bate com a do buffer de origem. A
  regra tem uma valvula, e ela e do original: `IgnoraJogadorRepetido`.

  A GRAVACAO chegou na WTE-TASK-27 (2026-08-19), para destino de SELECAO: 10
  bytes de nome, 12 de atributos e o byte condicional, todos pelo fluxo
  (`0x00403400`). Duas particularidades, e as duas so aparecem lendo o
  disassembly:

  1. **O time 48 le o numero de camisa ANTES e o regrava DEPOIS.** Ele guarda o
     numero dentro do registro de atributos, e a gravacao dos 12 bytes passaria
     por cima. A ordem do original nao e estilo -- e correcao.
  2. **Times 54 e 55 nao tem campo condicional**, e no lugar dele o original
     grava outras duas coisas: o nome de novo, numa segunda regiao, e o par de
     identidade `(time, slot)`. O par vai por `fseek`/`fputc` crus, sem fluxo.

  O QUE AINDA NAO ESTA AQUI, e e lacuna DECLARADA: **destino de Master
  League**. O ramo do original aloca um bloco livre, atualiza a tabela de
  vinculos e decrementa o contador `0x004335c0` -- que e a
  [WTE-TASK-33] quem calcula --, e dai sai o outro codigo de recusa, `-1`.
  Gravar meio bloco seria pior do que nao gravar: aqui a rotina sai sem tocar
  em byte nenhum quando o destino nao e selecao. }
{ As TRES colunas de offset do registro de buffer -- `+0x1c`, `+0x20`, `+0x28`
  do `0x00404374`, para destino de SELECAO.

  A WTE-TASK-25 as deixou de fora de proposito: naquele momento so a leitura
  importava, e a leitura vem da camada de dados. A gravacao precisa delas, e
  elas nao sao derivaveis do `Jogo` -- sao aritmetica sobre a imagem.

  Duas sao logicas (passam por `EnderecoDeDados`) e a terceira e ABSOLUTA. O
  `condicional` sai ZERO para os times 54 e 55, que e o mesmo furo que o
  `we2002_database.pas` pula ao carregar `cost` -- e ai o original grava noutro
  lugar, ver `GravaJogador`.

  Conferencia: para o time 2, slot 0, o condicional da **3067450**, que e
  exatamente a sexta leitura que o `0x0040f150` faz ao montar o cartao. }
{ As tres colunas de um BLOCO PROPRIO de Master League, do indice linear.

  Mesma forma da `OffsetsDoJogador`, outra tabela. O terceiro e absoluto ali e
  aqui, e aqui ele e o custo do jogador non-contract -- ver
  `ML_BLOCO_CUSTO_BASE`. }
procedure OffsetsDoBlocoMl(bloco: Integer;
                           out nome, atributos, custo: TOffset);
begin
  nome := EnderecoDeDados(SETOR_BASE_DADOS,
            ML_BLOCO_NOME_LOGICO + 10 * bloco);
  atributos := EnderecoDeDados(SETOR_BASE_DADOS,
            ML_BLOCO_ATRIBUTO_LOGICO + 12 * bloco);
  custo := ML_BLOCO_CUSTO_BASE + bloco;
end;

{ Onde na imagem mora o par de vinculo do slot `slot` do time `indice`.

  So faz sentido para time de Master League (`indice >= TIMES_NACIONAIS`); o
  original zera a coluna para selecao, e aqui isso vira zero tambem. }
function OffsetDoVinculoMl(indice, slot: Integer): TOffset;
begin
  if indice < TIMES_NACIONAIS then
    Exit(0);
  Result := EnderecoDeDados(SETOR_BASE_DADOS,
              46 * indice + 2 * slot + ML_VINCULO_LOGICO
              - ML_VINCULO_AJUSTE * (indice div IDX_MODELO_ML));
end;

procedure OffsetsDoJogador(indice, slot: Integer;
                           out nome, atributos, condicional: TOffset);
begin
  nome := EnderecoDeDados(NOME_JOGADOR_SETOR,
            NOME_JOGADOR_LOGICO + 230 * indice + 10 * slot);
  atributos := EnderecoDeDados(SETOR_BASE_DADOS,
            ATRIBUTO_LOGICO + 276 * indice + 12 * slot);
  if indice in TIMES_SEM_CONDICIONAL then
    condicional := 0
  else
    condicional := CONDICIONAL_BASE + 23 * indice + 2 * (indice div 56) + slot;
end;

{ Leva o par de vinculo gravado para o modelo em memoria.

  Mesma divergencia declarada do `GuardaJogadorNoModelo`: o `wte.exe` rele a
  imagem a cada troca de time, o port carrega uma vez. Sem isto o combo de
  jogadores continuaria mostrando quem estava no slot antes da troca. }
procedure GuardaVinculoNoModelo(indice, slot: Integer; b0, b1: Byte);
var
  vinculo: PByte;
begin
  if (indice < TIMES_NACIONAIS) or (slot < 0)
     or (slot >= JOGADORES_POR_TIME) then
    Exit;
  if indice < IDX_MODELO_ML then
    vinculo := @Jogo.ml_teams[indice - TIMES_NACIONAIS].link[slot * 2]
  else if indice = IDX_MODELO_ML then
    vinculo := @Jogo.ml_default.link[slot * 2]
  else
    Exit;
  vinculo[0] := b0;
  vinculo[1] := b1;
end;

{ A METADE DE MASTER LEAGUE da `0x00404820` -- de `0x00404a24` ao fim.

  O ramo nacional acima grava jogador SOBRE jogador, num par (time, slot) que
  a imagem sempre tem. Aqui o slot de destino nao guarda jogador: guarda um
  PAR DE VINCULO de dois bytes, e o que se move e para onde ele aponta. Por
  isso este ramo tem tres saidas onde o nacional tem uma, e por isso ele
  precisa do vetor de ocupacao vivo -- a mesma tabela que a WTE-TASK-33 enche.

  As tres, com o codigo que cada uma devolve:

  | situacao | o que faz | codigo |
  |---|---|---|
  | origem VAZIA e o destino nao esta sozinho no bloco | aloca bloco livre, grava o jogador nele e aponta o vinculo para la | `0` |
  | origem com identidade, destino idem | so reescreve o vinculo | `1` |
  | destino e slot vazio, ou dono unico do bloco | grava o jogador DIRETO no bloco do destino, sem alocar | `1` |
  | ... e a origem tem identidade | reescreve o vinculo e LIBERA o bloco do destino | `2` |

  A RECUSA `-1` mora aqui, e so no primeiro caso: sem bloco livre nao ha onde
  por o jogador. E a unica das duas recusas que depende de estado da imagem --
  a `-2` e comparacao de identidade.

  O QUE O ORIGINAL FAZ E O PORT NAO: no caminho de `0x00404d73` ele decrementa
  `ocupacao[bloco_do_destino]` sem ter calculado o indice quando o destino e
  do tipo 3, e escreve onde calhar. Nao e alcancavel na pratica -- o
  `0x00404374` so poe tipo 3 nos buffers de descarte, e o destino e sempre o
  buffer 0 --, e aqui a guarda `>= 0` o torna impossivel de vez. }
function GravaJogadorEmMl(origem, indice, slot: Integer): Integer;
var
  img: TCdImage;
  d_bloco, o_bloco, novo, t, sl, restantes: Integer;
  off_vinc, off_nome, off_attr, off_custo: TOffset;
  par: array[0..1] of Byte;
  direto: Boolean;
begin
  Result := COD_GRAVOU;
  if ImagemAberta = '' then
    Exit;

  { Os dois indices lineares, e cada um so existe se aquele lado tiver bloco
    proprio. O original os calcula ANTES do desvio, em `0x0040488e` e
    `0x004048a7`, e e por isso que eles aparecem aqui em cima. }
  d_bloco := -1;
  if BufferJogador[BUF_DESTINO].tipo = TIPO_ML_BLOCO then
    d_bloco := IndiceDoBlocoMl(BufferJogador[BUF_DESTINO].ident_time,
                               BufferJogador[BUF_DESTINO].ident_slot);
  o_bloco := -1;
  if BufferJogador[origem].tipo = TIPO_ML_BLOCO then
    o_bloco := IndiceDoBlocoMl(BufferJogador[origem].ident_time,
                               BufferJogador[origem].ident_slot);
  if (d_bloco > High(OcupacaoMl)) or (o_bloco > High(OcupacaoMl)) then
    Exit;

  off_vinc := OffsetDoVinculoMl(indice, slot);
  if off_vinc = 0 then
    Exit;

  { O desvio de `0x00404a24`. Destino do tipo 1 vai sempre pelo caminho de
    alocacao; do tipo 2, so se houver OUTRO dono do mesmo bloco. }
  direto := (BufferJogador[BUF_DESTINO].tipo <> TIPO_ML_VINCULO)
            and ((BufferJogador[BUF_DESTINO].tipo <> TIPO_ML_BLOCO)
                 or (d_bloco < 0) or (OcupacaoMl[d_bloco] <= 1));

  img.Init;
  if not img.OpenReadWrite(ImagemAberta) then
    Exit;
  try
    if direto then
    begin
      { `0x00404cf5`. Origem vazia -- ou a recusa de repetido desligada -- e o
        jogador vai direto para o bloco do destino, sem mexer em vinculo nem
        em contador. }
      if (BufferJogador[origem].tipo = TIPO_SOLTO)
         or IgnoraJogadorRepetido then
      begin
        if d_bloco < 0 then
          Exit;
        OffsetsDoBlocoMl(d_bloco, off_nome, off_attr, off_custo);
        GravaNoFluxo(img, off_nome, BufferJogador[origem].nome[0], 10);
        GravaNoFluxo(img, off_attr, BufferJogador[origem].atributos[0], 12);
        GravaNoFluxo(img, off_custo, BufferJogador[origem].condicional, 1);
        GuardaJogadorNoModelo(origem, indice, slot);
        Exit;
      end;
      { `0x00404d73`. O vinculo passa a apontar para a identidade da origem, e
        o bloco que o destino tinha fica LIVRE -- e o unico lugar do programa
        que devolve bloco. }
      par[0] := BufferJogador[origem].ident_time;
      par[1] := BufferJogador[origem].ident_slot;
      GravaNoFluxo(img, off_vinc, par[0], 2);
      GuardaVinculoNoModelo(indice, slot, par[0], par[1]);
      if d_bloco >= 0 then
        Dec(OcupacaoMl[d_bloco]);
      if o_bloco >= 0 then
        Inc(OcupacaoMl[o_bloco]);
      Inc(BlocosLivresDeMl);
      Result := COD_ML_LIBEROU;
      Exit;
    end;

    if BufferJogador[origem].tipo = TIPO_SOLTO then
    begin
      { `0x00404a57`. A recusa: nao ha bloco onde por o jogador. }
      if BlocosLivresDeMl = 0 then
      begin
        Result := COD_SEM_BLOCO_ML;
        Exit;
      end;
      novo := PrimeiroBlocoLivreMl;
      if novo < 0 then
      begin
        Result := COD_SEM_BLOCO_ML;
        Exit;
      end;
      ParDoIndiceLinearMl(novo, t, sl);
      if t < 0 then
      begin
        Result := COD_SEM_BLOCO_ML;
        Exit;
      end;
      par[0] := Byte(t);
      par[1] := Byte(sl);
      GravaNoFluxo(img, off_vinc, par[0], 2);
      GuardaVinculoNoModelo(indice, slot, par[0], par[1]);
      Inc(OcupacaoMl[novo]);
      Dec(BlocosLivresDeMl);
      OffsetsDoBlocoMl(novo, off_nome, off_attr, off_custo);
      GravaNoFluxo(img, off_nome, BufferJogador[origem].nome[0], 10);
      GravaNoFluxo(img, off_attr, BufferJogador[origem].atributos[0], 12);
      GravaNoFluxo(img, off_custo, BufferJogador[origem].condicional, 1);
      if d_bloco >= 0 then
        Dec(OcupacaoMl[d_bloco]);
      GuardaJogadorNoModelo(origem, indice, slot);
      Result := COD_ML_ALOCOU;
      Exit;
    end;

    { `0x00404b91`. Os dois lados tem identidade: so o vinculo muda. }
    par[0] := BufferJogador[origem].ident_time;
    par[1] := BufferJogador[origem].ident_slot;
    GravaNoFluxo(img, off_vinc, par[0], 2);
    GuardaVinculoNoModelo(indice, slot, par[0], par[1]);
  finally
    img.Close;
  end;

  if d_bloco >= 0 then
  begin
    Dec(OcupacaoMl[d_bloco]);
    { O aviso de `0x00404bd1`, e ele NAO sai durante uma troca: o
      `paderechaeizquierdaClick` liga o `TrocaEmCurso` justamente para
      cala-lo nas duas gravacoes que faz.

      O NUMERO PASSA POR UM `Currency` no original -- `(ocupacao - 1)` vezes
      10.000 pelo `__llmul` e depois `CurrToStr`. E a mesma armadilha do
      `LegendaDoDescarte`: 10.000 e a escala do tipo, entao a conta nao
      produz 10.000, produz o proprio numero. }
    restantes := OcupacaoMl[d_bloco] - 1;
    if not TrocaEmCurso then
    begin
      ficha_info4.etiq3.Caption := 'in another ' + IntToStr(restantes)
                                 + ' different place(s) in the game';
      ficha_info4.ShowModal;
    end;
  end;
  if o_bloco >= 0 then
  begin
    Inc(OcupacaoMl[o_bloco]);
    if OcupacaoMl[o_bloco] = 1 then
      Dec(BlocosLivresDeMl);
  end;
end;

function GravaJogador(origem, indice, slot: Integer): Integer;
var
  img: TCdImage;
  off_nome, off_attr, off_cond: TOffset;
  numero: Integer;
  b: Byte;
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

  { DESTINO DE MASTER LEAGUE: outra rotina, logo acima. O que muda nao e o
    detalhe -- e o objeto: la se grava um PAR DE VINCULO e se administra o
    vetor de blocos, aqui se grava o jogador em cima do jogador. }
  if BufferJogador[BUF_DESTINO].tipo <> TIPO_NACIONAL then
  begin
    Result := GravaJogadorEmMl(origem, indice, slot);
    Exit;
  end;

  if (ImagemAberta = '') or (indice < 0) or (slot < 0) then
    Exit;
  OffsetsDoJogador(indice, slot, off_nome, off_attr, off_cond);

  img.Init;
  if not img.OpenReadWrite(ImagemAberta) then
    Exit;
  try
    { O time 48 guarda o numero de camisa DENTRO do registro de atributos, e a
      gravacao abaixo passa por cima dele. O original le o numero ANTES e o
      regrava DEPOIS -- ordem que so faz sentido sabendo disso. }
    numero := 0;
    if indice = NUMERO_TIME_ALL_STAR then
      numero := NumeroDaCamisa(indice, slot);

    GravaNoFluxo(img, off_nome, BufferJogador[origem].nome[0], 10);
    GravaNoFluxo(img, off_attr, BufferJogador[origem].atributos[0], 12);

    if off_cond <> 0 then
      GravaNoFluxo(img, off_cond, BufferJogador[origem].condicional, 1)
    else
    begin
      { Times 54 e 55: sem campo condicional, e o original grava OUTRAS duas
        coisas no lugar -- o nome de novo, numa segunda regiao, e o par de
        identidade `(time, slot)`. O par vai por `fseek`/`fputc` crus, sem
        fluxo, como o ramo de ML do numero de camisa. }
      GravaNoFluxo(img, NOME_JOGADOR_2_BASE + 230 * indice + 10 * slot,
                   BufferJogador[origem].nome[0], 10);
      img.Seek(VINCULO_BASE + 46 * indice + 2 * slot, soBeginning);
      b := Byte(indice);
      img.Write(b, 1);
      b := Byte(slot);
      img.Write(b, 1);
    end;
  finally
    img.Close;
  end;

  if indice = NUMERO_TIME_ALL_STAR then
    GravaNumeroDaCamisa(numero, indice, slot);

  GuardaJogadorNoModelo(origem, indice, slot);
end;

{ ------------------------------------------------------------------------ }
{ GravaNumeroDaCamisa -- 0x00404048, 365 bytes.

  A metade de GRAVACAO do `dorsalClick`, e a irma escritora da `0x00403f00` que
  a `NumeroDaCamisa` ja reproduz na leitura. Dona: WTE-TASK-27. Ate 2026-08-19 o
  `dorsalClick` do port parava antes desta chamada, com o dono nomeado no
  proprio comentario.

  E uma escrita PONTUAL -- nao um `Save` do banco inteiro --, e tem TRES ramos,
  testados nesta ordem:

  | ramo | condicao | onde | como |
  |---|---|---|---|
  | all-star | `indice = 48` | setor 850, logico `$299AF + 12*slot` | 2 B, 5 bits no bit 2 |
  | ML | `indice > 62` | offset ABSOLUTO `$1EB797 + 23*i - 760*(i div 95) + slot` | 1 B cru |
  | nacional | `indice <= 62` | setor 24, logico `$4A094 + 16*indice` | 16 B, 5 bits em `32*(slot div 6) + 5*(slot mod 6)` |

  As duas fontes concordam onde poderiam divergir, que e a conferencia que a
  §4.2 do plano manda fazer: `EnderecoDeDados(24, $4A094)` da **404716**, o
  `OFS_SQUAD_NUMBERS_NATIONAL` do `we2002_core`, e a formula de ML no time 95
  da **2014504**, o `OFS_SQUAD_NUMBERS_ML`. O `+1` entre o time-modelo e o
  primeiro clube tambem bate: o `Load` do core le 23 bytes, **pula um**, e so
  entao os 32 clubes -- e a formula poe o time 63 em 2014528, que e
  `2014504 + 23 + 1`.

  O ramo de ML e o unico que NAO passa pelo fluxo: ele usa `fseek`/`fputc`
  crus, sem o salto de fronteira de setor. Nao e descuido reproduzido por
  reproduzir -- e um byte so, e o original nao pula. Passar pelo fluxo aqui
  daria o mesmo byte hoje e outro no dia em que o slot caisse na fronteira.

  O numero chega em BASE UM e vai ao disco em base zero: o `add al,0xff` do
  original, que e `-1` num byte. }
procedure GravaNumeroDaCamisa(numero, indice, slot: Integer);
var
  img: TCdImage;
  buffer: array[0..15] of Byte;
  offset: TOffset;
  valor, bit, k, largura: Integer;
begin
  if (ImagemAberta = '') or (numero <= 0) then
    Exit;
  if (slot < 0) or (slot >= JOGADORES_POR_TIME) then
    Exit;
  valor := (numero - 1) and $FF;

  img.Init;
  if not img.OpenReadWrite(ImagemAberta) then
    Exit;
  try
    if indice = NUMERO_TIME_ALL_STAR then
    begin
      { O numero deste time mora DENTRO do registro de atributos do jogador --
        `$265EC + 276*48 + 12*slot + 3` e exatamente o `$299AF + 12*slot` do
        disassembly. Cinco bits a partir do bit 2 do par lido. }
      offset := EnderecoDeDados(SETOR_BASE_DADOS,
                  NUMERO_ALL_STAR_LOGICO + 12 * slot);
      largura := 2;
      bit := NUMERO_ALL_STAR_BIT;
    end
    else if indice >= TIMES_NACIONAIS then
    begin
      { Um byte cru, em offset absoluto, sem fluxo. }
      img.Seek(NUMERO_ML_BASE + 23 * indice
               - 760 * (indice div IDX_MODELO_ML) + slot, soBeginning);
      img.Write(valor, 1);
      Exit;
    end
    else
    begin
      offset := EnderecoDeDados(NUMERO_NACIONAL_SETOR,
                  NUMERO_NACIONAL_LOGICO + 16 * indice);
      largura := 16;
      bit := NUMERO_BITS_GRUPO * (slot div NUMERO_POR_GRUPO)
           + NUMERO_BITS * (slot mod NUMERO_POR_GRUPO);
    end;

    { Ler, trocar os cinco bits, gravar de volta -- o original faz os tres
      passos com o mesmo comprimento, e nao so o byte que mudou. }
    if not LeDoFluxoEm(img, offset, buffer, largura) then
      Exit;
    for k := 0 to NUMERO_BITS - 1 do
      if (valor and (1 shl k)) <> 0 then
        buffer[(bit + k) div 8] :=
          buffer[(bit + k) div 8] or (1 shl ((bit + k) mod 8))
      else
        buffer[(bit + k) div 8] :=
          buffer[(bit + k) div 8] and not (1 shl ((bit + k) mod 8));
    GravaNoFluxo(img, offset, buffer, largura);
  finally
    img.Close;
  end;
end;

{ Leva o numero para o modelo em memoria.

  Mesma divergencia declarada das barras: o `wte.exe` rele a imagem a cada troca
  de time, o port carrega uma vez. Sem isto a tela do proprio port discordaria
  do proprio arquivo na volta ao time. }
procedure GuardaNumeroNoModelo(numero, indice, slot: Integer);
begin
  if (slot < 0) or (slot >= JOGADORES_POR_TIME) or (numero <= 0) then
    Exit;
  if indice >= IDX_MODELO_ML then
    Jogo.ml_default.raw_numbers[slot] := ShortInt(numero - 1)
  else if indice >= TIMES_NACIONAIS then
    Jogo.ml_teams[indice - TIMES_NACIONAIS].raw_numbers[slot] :=
      ShortInt(numero - 1)
  else
    SetSquadNumberAt(Jogo.teams[indice].squad_numbers, slot, numero - 1);
end;

{ ------------------------------------------------------------------------ }
{ O preenchimento da ficha do jogador -- WTE-TASK-26, decima segunda passagem.

  NAO E METODO DE FORMULARIO NENHUM, e e assim no original: o `0x0040756c` e
  rotina solta que alcanca os controles pelo ponteiro global `0x00433e38`
  (`_jugador`) -- a mesma forma da `MarcaCamisa`, que alcanca o `MainForm` por
  `0x00434360`.

  DESCEU PARA A `wte_ficha` NA CORR-WTE-091, e a razao e a de sempre neste
  port: ela passou a ter DOIS chamadores em formularios diferentes. O
  `mostrar_jugadorClick` (`MainForm`) a chamava desde a WTE-TASK-26; o
  `jugador.BitBtn1Click` -- o botao `Original `, que recarrega a ficha e
  descarta o que foi digitado -- e seis bytes que nao fazem outra coisa senao
  chama-la. Enquanto ela morava no `impl/ep2002_mainform.aux.inc` o segundo nao
  tinha como alcanca-la: `.aux.inc` e incluido na IMPLEMENTACAO, logo invisivel
  de fora, e o `uses` que o `dfm2lfm.py` emite sai na INTERFACE, entao
  `ep2002_jugador` nao pode usar `ep2002_mainform` de jeito nenhum.

  E a mesma forma que a `wte_render2d` estreou e que a `wte_tatica` repetiu, e
  a regra de corte do cabecalho desta unidade vale: veio a rotina inteira, e
  nada do que ela chama ficou para tras -- `FindComponent` e da VCL/LCL,
  `Legenda`/`LegendaDoCabelo` sao da `wte_legendas`, e `CONDICIONAL_AUSENTE` ja
  morava aqui. }

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
  mesma familia do `11*v + 9` das barras de forca do time.

  ELE REENTRA NOS DEZESSEIS `barrhabScroll`, e isso e medido, nao suposto:
  `TScrollBar.Position :=` DISPARA `OnChange` na LCL -- e so quando o valor
  muda de verdade --, enquanto `TUpDown.Position :=` nao dispara o `OnClick`
  (`wte/tools/check_lcl_combo.py`). Cada reentrada reescreve rotulo, largura e
  cor com o MESMO valor, entao a tela nao muda; o que muda e a contagem de
  disparos, e e isso que um gate de trace sobre a ficha tem de esperar.

  As duas escritas continuam necessarias: quando o valor ja e o que estava la,
  o `OnChange` nao dispara e so a daqui acontece. }
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

  { Uma volta do segundo laco. `cru` e o valor de bit; `legenda` chega
    preenchida so nos dois campos NUMERICOS -- altura e idade --, que sao os
    unicos que o original monta com `IntToStr`.

    Nos outros dez o rotulo e PALAVRA, buscada nas tabelas de `wte_legendas`.
    O despacho de tres ramos aqui e o mesmo do `jugador.flechasapaClick`, e
    nao por acaso: os dois escrevem o mesmo rotulo, um na carga e o outro ao
    mexer na seta. Se um dia divergirem, a ficha muda de texto so por ser
    tocada. }
  procedure Aparencia(n, cru: Integer; const pronta: string);
  var
    c: TComponent;
    texto: string;
  begin
    c := Controle('flechasapa', n);
    if c is TUpDown then
      TUpDown(c).Position := cru;
    { `pronta`, e nao `legenda`: Pascal nao distingue caixa, e um parametro
      chamado `legenda` esconderia a funcao `Legenda` da tabela. }
    if pronta <> '' then
      texto := pronta
    else if n = 3 then
      texto := LegendaDoCabelo(cru)     { faixa de 32, tabela propria }
    else
      texto := Legenda(n, cru);
    c := Controle('valorapa', n);
    if c is TLabel then
      TLabel(c).Caption := texto;
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

  { Segundo laco -- tabela `0x00423708`. A cadeia vazia nos dez campos
    ENUMERADOS nao quer dizer "sem rotulo": quer dizer "o rotulo sai da tabela
    de legendas", e o `Aparencia` a busca. Os dois campos NUMERICOS, altura e
    idade, sao os unicos que o original monta com `IntToStr`, e por isso sao os
    unicos que trazem a legenda pronta.

    Ate a decima setima passagem essa distincao nao existia: os dez saiam sem
    rotulo nenhum, e a ficha mostrava as legendas de PROJETO do `.lfm` (`Gl`,
    `A`, `A1`, `Dire.`, `NO`) iguais para todo jogador -- pior do que branco,
    porque parecia dado. As tabelas foram medidas pelo `dump_legendas.py`. }
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
  { OS DOIS CAMPOS DE TEXTO, e eles nao saem do jogador -- saem das globais.

    `casilla_nombre` recebe o `0x004335d4` (`0x0040794b`) e `casilla_dorsal` o
    `IntToStr(0x004335c8)` (`0x0040796b`). Faltavam ate a CORR-WTE-081, e a
    falta so aparecia ao GRAVAR: o `BitBtn3Click` le os dois campos, entao sem
    isto o `Comple.` gravaria o texto de tempo de projeto do `.lfm`.

    `NomeNaFicha` chega enchida pelo `mostrar_jugadorClick`, que e onde o
    original a enche -- `0x0040fa8c`, com o nome recortado do item da lista. }
  jugador.casilla_nombre.Text := NomeNaFicha;
  jugador.casilla_dorsal.Text := IntToStr(NumeroNaFicha);

  jugador.casilla_precio.Enabled := JogadorTemCampoCondicional(indice, slot);
  if jugador.casilla_precio.Enabled then
    jugador.casilla_precio.Text := IntToStr(p.cost)
  else
    jugador.casilla_precio.Text := IntToStr(CONDICIONAL_AUSENTE);
end;

end.
