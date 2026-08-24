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
  `0x00411178`), mas cada volta comeca com

      call 0x4046e8                        ' carrega_jogador(time, slot, 2)
      cmp DWORD PTR ds:0x43366c,0x0        ' a terceira coluna do buffer 2
      je  0x411175                         ' pula o slot

  e para o slot 22 a coluna sai ZERO. Medido em dois times da ROM japonesa
  (2 e 9): os bytes gravados vao de `CONDICIONAL_BASE + 23*t` ate `+ 21`, e o
  do slot 22 fica com o valor de fabrica nos dois. No time 9 o slot 21 e o 22
  tem a MESMA soma (36) e a mesma posicao (0), e so o 21 e gravado -- o que
  descarta explicacao pelo conteudo do jogador.

  A CAUSA ESTA ABERTA (CORR-WTE-095): a conta de offset que este port herdou do
  `we2002_core` da coluna nao-nula para o slot 22, e o `we2002_core` e
  byte-identico ao `ed.exe`. Ou seja, o `ed.exe` e o editor do Obocaman
  discordam sobre o ultimo slot. O port reproduz o que o ORACULO faz, porque e
  contra ele que o gate mede -- e a divergencia fica escrita em vez de
  silenciosa.

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
