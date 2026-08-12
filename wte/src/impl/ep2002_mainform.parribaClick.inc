{ MainForm.parribaClick -- 0x0040e998, 807 bytes.
  Spec: wte/re/spec/MainForm.parribaClick.md

  A seta para cima: poe o jogador selecionado no lado esquerdo na linha da
  LISTA DE DESCARTE que estiver selecionada. E a metade de guardar; a de
  devolver e o `pabajoClick`.

  NAO GRAVA NADA. Ele so carrega o jogador para o buffer daquela linha
  (`lista_descarte.ItemIndex + 3`) e reescreve a legenda. E o unico handler
  deste lote que nao chama a rotina de gravacao, e por isso e o unico que
  fecha sem depender da WTE-TASK-27.

  Dos 807 bytes, a maior parte e montagem de cadeia: o numero da linha passa
  por um `Currency` (a multiplicacao por 10.000 e a escala do tipo, nao um
  preco) e a legenda sai em duas larguras, `'  1 NOME'` ate `'23 NOME'`. Ver
  a `LegendaDoDescarte` do `.aux.inc`.

  A ORDEM E LOAD-BEARING: o nome sai do combo ANTES de o buffer ser carregado
  -- na verdade o original carrega o buffer primeiro e so depois recorta o
  nome, e nenhum dos dois toca o outro, entao a ordem esta reproduzida sem
  consequencia. O que teria consequencia e o `ItemIndex` da lista de descarte
  ser lido uma vez so, e e o que acontece. }
var
  linha: Integer;
  nome: string;
begin
  REMark('MainForm.parribaClick');
  linha := lista_descarte.ItemIndex;
  if (linha < 0) or (linha >= JOGADORES_POR_TIME)
     or (lista_equipos_1.ItemIndex < 0)
     or (lista_jugadores_1.ItemIndex < 0) then
    Exit;

  CarregaJogador(lista_equipos_1.ItemIndex, lista_jugadores_1.ItemIndex,
                 linha + BUF_DESCARTE_BASE);
  nome := NomeDoItemSelecionado(lista_jugadores_1);

  lista_descarte.Items[linha] := LegendaDoDescarte(linha, nome);
  lista_descarte.Update;
  lista_descarte.ItemIndex := linha;
  DescarteOcupado[linha] := True;
end;
