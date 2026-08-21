{ jugador.BitBtn3Click -- 0x00408548, 1.453 bytes.
  Spec: wte/re/spec/jugador.BitBtn3Click.md
  Dono: CORR-WTE-081, primeira das tres gravacoes orfas.

  O `Comple.` da ficha: valida os dois campos numericos, copia a tela inteira
  para o buffer de jogador e GRAVA NA IMAGEM. E o maior handler do grupo
  `auxiliar`, e nao e auxiliar coisa nenhuma.

  As duas escritoras ja existiam -- `GravaJogador` (`0x00404820`) e
  `GravaNumeroDaCamisa` (`0x00404048`), da WTE-TASK-27. O que faltava era
  alcanca-las: elas moravam no `.aux.inc` do `MainForm`, que e includo na
  IMPLEMENTACAO daquela unidade. Desceram para o `wte_ficha`; o cabecalho de
  la conta o corte.

  A RECUSA `-2` NAO DISPARA AQUI, E ISSO E DELIBERADO DO ORIGINAL. O destino e
  o MESMO par (time, slot) da origem, entao a identidade bate e a
  `GravaJogador` sairia sem tocar em byte nenhum. Por isso o
  `mostrar_jugadorClick` liga `IgnoraJogadorRepetido` antes do `ShowModal` e o
  desliga depois -- `mov BYTE ds:0x423168,1` em `0x0040ffb3`, `ShowModal` em
  `0x0040ffc6`, `mov ..,0` em `0x0040ffcc`. Sem essa valvula o botao nao
  gravaria nada.

  OS DEZ BYTES DE NOME SAEM DO CAMPO, E O CAMPO NASCE VAZIO. Ver
  `NomeNaFicha` no `wte_ficha`: ha uma unica escrita em `0x004335d4` no `.text`
  inteiro, e ela e a da linha marcada abaixo. Primeiro `Comple.` numa sessao
  grava dez zeros por cima do nome do jogador. Destrutivo, e do original.

  AS 28 CAIXAS DE BIT NAO SAO REESCRITAS AQUI, e essa e a unica liberdade de
  forma que o corpo toma. O original percorre as tabelas `0x00423648` (16
  registros) e `0x00423708` (12) chamando a escritora de bits `0x00403010`;
  aqui os valores da tela vao para um `TPlayer`, e o `Encode` do
  `we2002_player` reempacota. E a MESMA tabela vista do outro lado: o
  `wte/tools/check_bitfields.py` le os 28 registros do `.exe` a cada `make -C
  wte check` e exige a expressao correspondente no `we2002_player.pas`. As
  mascaras abaixo sao as do `Decode`, campo a campo, para que valor fora de
  faixa trunque como o original trunca em vez de vazar para o vizinho.

  O `Encode` toca um bit a mais que as tabelas -- os cinco de `number`, em
  `raw_attributes[3]` --, e isso nao muda byte nenhum: o valor sai do `Decode`
  do mesmo buffer e volta igual. Quem grava numero de camisa e a
  `GravaNumeroDaCamisa`, depois, e para o time 48 ela reescreve exatamente
  esses cinco bits.

  DIVERGENCIA DELIBERADA (WTE-TASK-35), e ela e de erro de entrada: o original
  chama a `StrToInt` da VCL, que LEVANTA excecao com texto nao numerico e cai
  na caixa de erro do runtime. Aqui `StrToIntDef` devolve zero, que reprova na
  faixa e leva a mesma `ficha_error2` da validacao. Os dois `KeyPress` da ficha
  ja filtram tudo o que nao e digito, entao o caminho so existe para texto
  colado. }
var
  p: TPlayer;
  buf, i, creditos, numero: Integer;
  texto: string;

  { O valor cru de uma das dezesseis barrinhas de habilidade. O original le o
    campo `+0x20c` do `TScrollBar` que o `FindComponent` devolveu. }
  function Habilidade(n: Integer): Integer;
  var
    c: TComponent;
  begin
    Result := 0;
    c := FindComponent('barrhab' + IntToStr(n));
    if c is TScrollBar then
      Result := TScrollBar(c).Position;
  end;

  { O valor cru de uma das doze setas de aparencia. O `and $ff` e do original
    (`and edi,0xff` em `0x0040885b`). }
  function Aparencia(n: Integer): Integer;
  var
    c: TComponent;
  begin
    Result := 0;
    c := FindComponent('flechasapa' + IntToStr(n));
    if c is TUpDown then
      Result := TUpDown(c).Position and $FF;
  end;

  { A caixa de erro dos dois campos, com o foco de volta no culpado. }
  procedure Recusa(const mensagem: string; campo: TWinControl);
  begin
    ficha_error2.etiq1.Caption := mensagem;
    ficha_error2.ShowModal;
    campo.SetFocus;
  end;

begin
  REMark('jugador.BitBtn3Click');
  buf := BufferDaFicha;
  if (buf < BUF_DESTINO) or (buf > BUF_ULTIMO) then
    Exit;

  { Primeira validacao: os creditos, e SO quando o jogador tem o campo na
    imagem -- o `cmpl $0x0,0x433614(,%ecx,4)` de `0x00408580`. Os times 54 e 55
    nao tem, e ali a ficha mostra o literal 50 num campo desabilitado. }
  creditos := 0;
  if BufferJogador[buf].tem_condicional then
  begin
    creditos := StrToIntDef(casilla_precio.Text, 0);
    if (creditos < 1) or (creditos > 250) then
    begin
      Recusa('Insert a valid number of credits (1 ... 250)', casilla_precio);
      Exit;
    end;
  end;

  { Segunda validacao: o numero de camisa. Ate 32 sempre; de 33 a 99 so em
    clube de Master League, que e o teste `cmpb $0x0,0x433605(,%ecx,4)` sobre o
    tipo do buffer. A cadeia esta truncada no binario (`0x00424ac0`), com o `e`
    e os quatro espacos que sobraram da traducao, e sai daqui como esta la. }
  numero := StrToIntDef(casilla_dorsal.Text, 0);
  if (numero < 1) or (numero > 99)
     or ((numero > 32) and (BufferJogador[buf].tipo = TIPO_NACIONAL)) then
  begin
    Recusa('Numero do uniforme invalido ([33 ... 99] somente na Mastere    ',
           casilla_dorsal);
    Exit;
  end;
  NumeroNaFicha := numero;

  { As 28 caixas de bit, na ordem das duas tabelas -- a mesma ordem do
    `PreencheFicha`, lida ao contrario. }
  p.Init;
  for i := 0 to 11 do
    p.raw_attributes[i] := BufferJogador[buf].atributos[i];
  p.Decode;

  p.attack        := 12 + (Habilidade(1)  and $07);
  p.defence       := 12 + (Habilidade(2)  and $07);
  p.strength      := 12 + (Habilidade(3)  and $07);
  p.stamina       := 12 + (Habilidade(4)  and $07);
  p.speed         := 12 + (Habilidade(5)  and $07);
  p.acceleration  := 12 + (Habilidade(6)  and $07);
  p.passing       := 12 + (Habilidade(7)  and $07);
  p.shot_power    := 12 + (Habilidade(8)  and $07);
  p.shot_accuracy := 12 + (Habilidade(9)  and $07);
  p.jump          := 12 + (Habilidade(10) and $07);
  p.heading       := 12 + (Habilidade(11) and $07);
  p.technique     := 12 + (Habilidade(12) and $07);
  p.dribbling     := 12 + (Habilidade(13) and $07);
  p.swerve        := 12 + (Habilidade(14) and $07);
  p.aggression    := 12 + (Habilidade(15) and $07);
  p.reflexes      := 12 + (Habilidade(16) and $07);

  p.position        := Aparencia(1)  and $07;
  p.skin_colour     := Aparencia(2)  and $03;
  p.hair_style      := Aparencia(3)  and $1F;
  p.hair_colour     := Aparencia(4)  and $07;
  p.beard_style     := Aparencia(5)  and $07;
  p.beard_colour    := Aparencia(6)  and $07;
  p.height          := 148 + (Aparencia(7) and $3F);
  p.build           := Aparencia(8)  and $07;
  p.age             := 15 + (Aparencia(9) and $1F);
  p.boots           := Aparencia(10) and $07;
  p.foot            := Aparencia(11) and $03;
  p.out_of_position := Aparencia(12) and $01;

  p.Encode;
  for i := 0 to 11 do
    BufferJogador[buf].atributos[i] := p.raw_attributes[i];

  { A UNICA escrita em `0x004335d4` do programa inteiro. }
  NomeNaFicha := casilla_nombre.Text;

  { Os dez bytes de nome, do campo, com o bit 7 derrubado (`and $0x7f`) e
    zero no que sobrar. }
  texto := casilla_nombre.Text;
  for i := 0 to 9 do
    if i < Length(texto) then
      BufferJogador[buf].nome[i] := AnsiChar(Byte(texto[i + 1]) and $7F)
    else
      BufferJogador[buf].nome[i] := #0;
  BufferJogador[buf].nome[10] := #0;

  { O campo condicional, e so quando ele existe. O original guarda o byte
    baixo (`mov %al,0x433604(,%edx,4)`). }
  if BufferJogador[buf].tem_condicional then
    BufferJogador[buf].condicional := ShortInt(creditos and $FF);

  { As duas gravacoes, nesta ordem -- para o time 48 a segunda reescreve os
    cinco bits que a primeira acabou de passar por cima. }
  { O CODIGO DE RETORNO E DESCARTADO, como no original: a `MostraCodigo` nao e
    chamada deste botao. Com `IgnoraJogadorRepetido` ligado, as duas recusas
    que ele poderia devolver ficam fora de alcance por aqui. }
  GravaJogador(buf, TimeEmEdicao, JogadorEmEdicao);
  GravaNumeroDaCamisa(NumeroNaFicha, TimeEmEdicao, JogadorEmEdicao);

  { So o lado ESQUERDO tem camisa marcada no `MainForm` -- o
    `cmpl $0x1,0x4335c4` de `0x00408a8b`. }
  if (BufferDaFicha = BUF_ESQUERDA) and (CamisaMarcada <> nil) then
    CamisaMarcada.Caption := IntToStr(NumeroNaFicha);

  { O `movl $0x1,0x24c(%ecx)`: `mrOk`, sem `Hide` -- quem fecha o modal e o
    proprio `ModalResult`. }
  ModalResult := mrOk;
end;
