{ MainForm.paderechaeizquierdaClick -- 0x0040e304, 428 bytes.
  Spec: wte/re/spec/MainForm.paderechaeizquierdaClick.md

  A seta `<>`: TROCA os dois jogadores selecionados, um de cada lado. Nao e a
  seta de um so nem a de lote -- e a unica que grava nas duas direcoes.

  A CHECAGEM DE BLOCO LIVRE VEM ANTES DE QUALQUER GRAVACAO, e a condicao e
  estreita: so recusa quando NAO ha bloco de ML livre E um dos dois lados e
  jogador de selecao (`tipo = 0`) enquanto o outro e slot de clube de ML
  apontando para selecao (`tipo = 1`). Trocar dois de selecao, ou dois de
  clube com bloco proprio, nao consome bloco e passa.

  DEPOIS DISSO ELE MEXE NOS TIPOS DOS BUFFERS: o lado que e selecao vira
  `TIPO_SOLTO` quando o outro e de clube de ML. E o que faz a rotina de
  gravacao tratar aquele jogador como conteudo novo em vez de vinculo.

  A chave `TrocaEmCurso` fica ligada durante as duas gravacoes. Quem a le e a
  metade de gravacao da `0x00404820` (`0x00404bc4`), que e da WTE-TASK-27 --
  aqui ela so e ligada e desligada na hora certa.

  DUAS COISAS QUE O CORPO FAZ E QUE PARECEM DESCUIDO, e sao do original:

  1. no caminho de erro ele mostra sempre `-2`, mesmo que a gravacao tenha
     devolvido `-1`;
  2. ele nao recarrega buffer nenhum no fim -- o repovoamento das duas listas
     e feito pela `0x0040b934`, que preserva as duas selecoes. }
var
  codigo: Integer;
begin
  REMark('MainForm.paderechaeizquierdaClick');
  if (lista_equipos_1.ItemIndex < 0) or (lista_jugadores_1.ItemIndex < 0)
     or (lista_equipos_2.ItemIndex < 0) or (lista_jugadores_2.ItemIndex < 0) then
    Exit;

  CarregaJogador(lista_equipos_1.ItemIndex, lista_jugadores_1.ItemIndex,
                 BUF_ESQUERDA);
  CarregaJogador(lista_equipos_2.ItemIndex, lista_jugadores_2.ItemIndex,
                 BUF_DIREITA);

  if (BlocosLivresDeMl = 0)
     and (((BufferJogador[BUF_ESQUERDA].tipo = TIPO_NACIONAL)
           and (BufferJogador[BUF_DIREITA].tipo = TIPO_ML_VINCULO))
          or ((BufferJogador[BUF_DIREITA].tipo = TIPO_NACIONAL)
              and (BufferJogador[BUF_ESQUERDA].tipo = TIPO_ML_VINCULO))) then
  begin
    MostraCodigo(COD_SEM_BLOCO_ML);
    Exit;
  end;

  TrocaEmCurso := True;
  if (BufferJogador[BUF_ESQUERDA].tipo = TIPO_NACIONAL)
     and (BufferJogador[BUF_DIREITA].tipo in [TIPO_ML_VINCULO, TIPO_ML_BLOCO]) then
    BufferJogador[BUF_ESQUERDA].tipo := TIPO_SOLTO;
  if (BufferJogador[BUF_DIREITA].tipo = TIPO_NACIONAL)
     and (BufferJogador[BUF_ESQUERDA].tipo in [TIPO_ML_VINCULO, TIPO_ML_BLOCO]) then
    BufferJogador[BUF_DIREITA].tipo := TIPO_SOLTO;

  codigo := GravaJogador(BUF_ESQUERDA, lista_equipos_2.ItemIndex,
                         lista_jugadores_2.ItemIndex);
  if codigo >= 0 then
  begin
    codigo := GravaJogador(BUF_DIREITA, lista_equipos_1.ItemIndex,
                           lista_jugadores_1.ItemIndex);
    MostraCodigo(codigo);
    RepovoaAsDuasListas;
    casilla_xmlibres.Caption := IntToStr(BlocosLivresDeMl);
  end
  else
    { O original nao repassa o codigo aqui: ele forca -2. }
    MostraCodigo(COD_MESMO_JOGADOR);
  TrocaEmCurso := False;
end;
