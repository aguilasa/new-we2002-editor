{ MainForm.dorsalClick -- 0x00410a74, 872 bytes.
  Spec: wte/re/spec/MainForm.dorsalClick.md

  Um corpo para os 23 rotulos `dorsal1..23`. Clicar num numero de camisa
  seleciona aquele jogador, realca a camisa, e abre o `ficha_dorsal` -- a
  janelinha de escolher numero -- posicionada ao lado do rotulo clicado.

  QUEM DECIDE QUAL CAMISA E O NOME DO COMPONENTE, nao o `Tag` nem o ponteiro:
  o original faz `Copy(Sender.Name, 7, 2)` sobre `'dorsalNN'` e converte. Sao
  os mesmos 7 e 2 aqui.

  A REGRA DE VALIDACAO DO NUMERO NAO E UM `if`: e o `Max` da barra. Clube de
  Master League (indice > 62) aceita ate 99; seleção, ate 32. Casa com a
  mensagem de erro que a WTE-TASK-05 mapeou (`[33 ... 99] somente na Master`) e
  com o teto de 32 do `newWe2002`, que grava os cinco bits.

  ---

  ELE GRAVA NA IMAGEM quando o modal fecha, e a gravacao chegou na WTE-TASK-27
  (2026-08-19). E a `0x00404048` -- a irma escritora da rotina de leitura
  `0x00403f00`, com os mesmos tres ramos --, que recebe numero, indice do time,
  slot do jogador e o arquivo aberto. Escrita PONTUAL, nao um `Save` do banco
  inteiro, e e la que o `- 1` da base zero acontece (`add al,0xff`).

  Ate essa data este corpo parava antes da escrita, com o dono nomeado: era a
  opcao A da WTE-TASK-26, que fechou nove handlers `aberto` para nao misturar
  duas causas possiveis num golden vermelho. Este e o primeiro dos nove a ser
  promovido. }
var
  numero, escolhido: Integer;
  nome_do_jogador: string;
  origem: Integer;
begin
  REMark('MainForm.dorsalClick');
  if lista_equipos.ItemIndex < 0 then
    Exit;

  { O bloco de selecao so roda se a camisa clicada NAO for a ja marcada --
    clicar de novo na mesma abre a janelinha sem remexer na lista. }
  if (Sender is TStaticText) and (TStaticText(Sender) <> CamisaMarcada) then
  begin
    numero := StrToIntDef(Copy(TComponent(Sender).Name, 7, 2), 0);
    if numero <= 0 then
      Exit;
    lista_jugadores_1.ItemIndex := numero - 1;
    MarcaCamisa(numero);
  end;
  if CamisaMarcada = nil then
    Exit;

  { A janelinha nasce colada no rotulo clicado: o deslocamento e sobre a
    posicao do proprio `Sender` para a horizontal e sobre o `GroupBox1` para a
    vertical -- os 23 rotulos estao todos na mesma linha, entao o `Top` nao
    precisa vir de cada um. }
  ficha_dorsal.Left := Left + TControl(Sender).Left + $26;
  ficha_dorsal.Top := Top + GroupBox1.Top + $3C;

  ficha_dorsal.etiq_dorsal.Caption := CamisaMarcada.Caption;
  if lista_equipos_1.ItemIndex > 62 then
    ficha_dorsal.scroll_dorsal.Max := 99
  else
    ficha_dorsal.scroll_dorsal.Max := 32;
  ficha_dorsal.scroll_dorsal.Position :=
    ficha_dorsal.scroll_dorsal.Max
    - StrToIntDef(CamisaMarcada.Caption, 1) + 1;

  { O titulo da janelinha traz o nome do jogador, recortado do item do combo.
    O item tem a forma `<n>. <NOME>`, e o original comeca no caractere 4 ou 5
    conforme o indice tenha um ou dois digitos -- aritmetica de largura de
    numero, nao de conteudo. }
  origem := 4;
  if lista_jugadores_1.ItemIndex < 9 then
    Inc(origem);
  nome_do_jogador := '';
  if (lista_jugadores_1.ItemIndex >= 0)
     and (lista_jugadores_1.ItemIndex < lista_jugadores_1.Items.Count) then
    nome_do_jogador :=
      Copy(lista_jugadores_1.Items[lista_jugadores_1.ItemIndex], origem, 10);
  { O prefixo e um espaco, e so -- a cadeia em `0x00425077` tem um caractere.
    O `Caption = 'Number'` do DFM e o de projeto, e some no primeiro clique. }
  ficha_dorsal.Caption := ' ' + nome_do_jogador;

  ficha_dorsal.ShowModal;

  { De volta do modal: o numero escolhido vai para o rotulo E para a imagem.
    A gravacao e a `0x00404048`, pontual, com os tres ramos -- ver
    `GravaNumeroDaCamisa` no `.aux.inc`. }
  escolhido := StrToIntDef(ficha_dorsal.etiq_dorsal.Caption, 0);
  if escolhido > 0 then
  begin
    CamisaMarcada.Caption := IntToStr(escolhido);
    GravaNumeroDaCamisa(escolhido, lista_equipos.ItemIndex,
                        lista_jugadores_1.ItemIndex);
    GuardaNumeroNoModelo(escolhido, lista_equipos.ItemIndex,
                         lista_jugadores_1.ItemIndex);
  end;
end;
