{ ficha_color.lista_col0Change -- 0x0040688c, 36 bytes.
  Spec: wte/re/spec/ficha_color.lista_col0Change.md

  O combo de FORMA de bandeira. Ele nao digita o numero da forma: ele INDEXA a
  tabela `FORMA_PADRAO`, e por isso tem 95 itens com nome de time em vez de 53
  com nome de desenho.

  E e por isso que os oito indices sem arquivo (44..51) nunca sao pedidos --
  nenhum time os usa, entao nenhum item do combo os alcanca. A assimetria esta
  na secao 3.2 do `wte/re/assets.md`.

  A forma escolhida vira a forma EM VIGOR do time em edicao. No original isso e
  o byte `0x00432f15`, o rascunho que o desenhista le; aqui e o `flag_shape` do
  `Jogo`, pela mesma razao que a `SalvaPaleta` grava ali -- ver o cabecalho
  dela. }
begin
  REMark('ficha_color.lista_col0Change');
  if (lista_col0.ItemIndex < 0)
     or (lista_col0.ItemIndex >= TIMES_TOTAL) then
    Exit;
  SalvaFormaDaBandeira(TimeEmCor, FORMA_PADRAO[lista_col0.ItemIndex]);
  RedesenhaBandeiraEmVigor;
end;
