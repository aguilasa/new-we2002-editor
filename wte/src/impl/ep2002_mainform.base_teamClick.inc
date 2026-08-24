{ MainForm.base_teamClick -- 0x00410ff4, 484 bytes.
  Spec: wte/re/spec/MainForm.base_teamClick.md

  ESCOPO: a MOLDURA. Os rotulos `Time Tit.` e `Time Res.` -- os dois com o
  `Hint` `Calcular precos` -- abrem o `ficha_creditos_equipo` e, se a resposta
  nao for cancelar, calculam o preco dos 23 jogadores do time e GRAVAM um byte
  em cada. O calculo e a gravacao sao da WTE-TASK-32, que e a dona de preco; o
  que este corpo faz e abrir e fechar.

  ELE GRAVA NA IMAGEM, e a task de preco precisa saber disso. A WTE-TASK-32 foi
  descrita como "isolada, nao depende de gravacao" -- verdade para o
  `jugador.etiqprecioClick`, que so mostra o numero na tela, e FALSO para este,
  que percorre 23 jogadores e escreve um byte em cada. A regua da 32 tem de ser
  dupla: tela para a formula, byte para este.

  QUEM SEPARA TITULAR DE RESERVA E O PONTEIRO DO `Sender`, e nao o nome --
  diferente do `mostrar_jugadorClick`, que compara nome. Por isso o
  `LadoTitular` do `.aux.inc` nao serve aqui.

  Os dois deslocamentos sao literais do `.text` -- `-65` do lado do titular,
  `Width - 200` do lado do reserva. Sao coordenadas de tempo de projeto e nao
  se derivam de nada.

  ------------------------------------------------------------------------
  O MIOLO, DA WTE-TASK-32.

  A formula e a mesma do `jugador.etiqprecioClick` -- conferido instrucao a
  instrucao: `0x004110e7`..`0x0041112a` aqui e `0x00408c3b`..`0x00408c83` la,
  as mesmas quatro constantes e o mesmo `+ 5`. O que muda e de onde vem a soma:
  la, das dezesseis `barrhab<N>.Position` da tela; aqui, de dezesseis chamadas a
  `0x00403278` sobre a tabela de `0x00423648`, porque nao ha tela por jogador.
  As duas chegam ao mesmo numero, e o port usa a `SomaDasHabilidades`, que
  calcula do `TPlayer` decodificado.

  O PORT NAO PORTA A `0x00403278`, e a razao e a mesma que vale para a tabela
  de formacoes do `estrategia.FormCreate`: ela e o decodificador de atributo do
  original, e este port tem o dele, transpilado do `we2002_core` e conferido
  contra as duas ROMs desde a fase 3.

  ELE PRECA VINTE E DOIS SLOTS, NAO VINTE E TRES, e isso e MEDIDO, nao
  suposto. O laco do original vai de 0 a 22 (`cmp DWORD PTR [ebp-0x2c],0x17` em
  `0x00411178`) e grava 22 bytes. Medido em seis times da ROM japonesa
  (0, 2, 9, 17, 30, 48): vao de `CONDICIONAL_BASE + 23*t` ate `+ 21`, e o do
  slot 22 fica com o valor de fabrica nos seis. No time 9 o slot 21 e o 22 tem
  a MESMA soma (36) e a mesma posicao (0), e so o 21 e gravado -- o que
  descarta explicacao pelo conteudo do jogador.

  NAO E O `je` DA TERCEIRA COLUNA, e este cabecalho dizia que era ate
  2026-08-24. O laco realmente comeca com

      call 0x4046e8                        ' carrega_jogador(time, slot, 2)
      cmp DWORD PTR ds:0x43366c,0x0        ' a terceira coluna do buffer 2
      je  0x411175                         ' pula o slot

  mas a coluna do slot 22 NAO e zero: sob `strace` o oraculo LE o byte
  condicional dele em 3067472, com o mesmo numero de seeks dos outros 22, e a
  `0x4046e8` so faz essa leitura na rota de coluna nao nula (`0x00404748`
  desvia para `0x0040477e` no caso zero, e la nao ha I/O). O byte se perde na
  ESCRITA -- dentro da `0x00403400`, entre o `fseek` de `0x00403410` e o
  `fputc` de `0x0040342a` --, e o mecanismo continua aberto na CORR-WTE-095.

  Como se remede a amostra, em uma linha:

      awk -F'\t' '$3==22 && $7!="-"' wte/re/preco.tsv | wc -l   # tem de dar 0

  E COMO SE REMEDE O SALTO, que e outra pergunta: plante um byte no slot 22 e
  rode o oraculo sobre a copia. Feito em 2026-08-24 no time 2, com `0xFF` nos
  slots 20, 21 e 22: os dois primeiros voltaram 26 e 21 -- o `previsto` do
  `preco.tsv` -- e o terceiro continuou 255. Sem esse plantio a leitura "nao
  grava" nao se separa de "grava o valor que ja estava la".

  A CAUSA ESTA ABERTA (CORR-WTE-095), e o que ela ja fechou importa aqui: a
  `0x00404374` do proprio oraculo NAO tem ramo por slot -- ela decide por time
  (`cmp ecx,0x3f`, e os times 54 e 55 em `cmp ecx,0x35`/`cmp ecx,0x38`) e
  escreve `0x2ece0c + 23*time + 2*(time div 56) + slot` para os 23. Ou seja, a
  conta de offset deste port NAO esta errada para o slot 22: ela e a mesma do
  oraculo. E o slot 22 e enderecavel: o `io-medido.tsv`, sessao `27-mcr2iso`,
  mostra o import de `.mcr` gravando os 23 bytes condicionais do time 3. O que
  sobra aberto e por que a `0x00403400` posiciona e nao escreve na 23a volta.
  O port reproduz o que o ORACULO faz, porque e contra ele que o gate mede --
  e a divergencia fica escrita em vez de silenciosa.

  A MENSAGEM DO FIM sai do `.exe` em `0x00425079`. }
const
  { O laco do original vai ate aqui; o slot 22 nunca e alcancado pela gravacao.
    Ver o bloco acima -- e medida, nao escolha. }
  ULTIMO_SLOT_PRECADO = 21;
var
  time_, slot, k: Integer;
  preco: LongInt;
  b: Byte;
  nome, atributos, condicional: TOffset;
begin
  REMark('MainForm.base_teamClick');
  if Sender = TObject(base_team) then
  begin
    ficha_creditos_equipo.Left := Left - 65;
    time_ := lista_equipos_1.ItemIndex;
  end
  else
  begin
    ficha_creditos_equipo.Left := Left + Width - 200;
    time_ := lista_equipos_2.ItemIndex;
  end;

  if ficha_creditos_equipo.ShowModal = mrCancel then
    Exit;

  for slot := 0 to ULTIMO_SLOT_PRECADO do
  begin
    if not JogadorTemCampoCondicional(time_, slot) then
      Continue;
    k := IndiceDoJogador(time_, slot);
    if (k < 0) or (k >= Length(Jogo.players)) then
      Continue;
    preco := PrecoDoJogador(Jogo.players[k]);
    OffsetsDoJogador(time_, slot, nome, atributos, condicional);
    if condicional = 0 then
      Continue;
    b := Byte(preco);
    if GravaNaImagem(condicional, b, 1) then
      Jogo.players[k].cost := preco;
  end;

  ficha_info3.etiq1.Caption := 'Precos dos jogadores calculados!!!!!!!!!!!';
  ficha_info3.ShowModal;
end;
