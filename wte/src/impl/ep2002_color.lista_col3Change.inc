{ ficha_color.lista_col3Change -- 0x0040690c, 92 bytes.
  Spec: wte/re/spec/ficha_color.lista_col3Change.md

  O combo de PADRAO DE CAMISA. Tres casos, e os dois bytes que cada um escreve
  sao literais do `.text` -- nao ha aritmetica nenhuma:

      ItemIndex = 0  (NORMAL)     -> 0x00, 0x65
      ItemIndex = 1  (ROMBOIDAL)  -> 0x28, 0x61
      qualquer outro (EXTRA)      -> 0x00, 0x64

  O terceiro caso e o `else` do original, e nao o teste de `= 2`: um combo com
  um quarto item cairia em EXTRA.

  ONDE ELES VAO PARAR: no `PadraoDaCamisa` da `wte_cor`, que e o slot 1 do
  par. Ate a CORR-WTE-081 nada neste port o lia; hoje o `OK` do editor
  (`ficha_color.BitBtn3Click`) grava os dois bytes na imagem, que e o unico
  consumidor que o original tambem tem. O cabecalho da variavel explica o
  resto.

  E o combo esta `Enabled = False` no `.dfm`: so codigo o move. }
begin
  REMark('ficha_color.lista_col3Change');
  if lista_col3.ItemIndex = 0 then
  begin
    PadraoDaCamisa[0] := $00;
    PadraoDaCamisa[1] := $65;
  end
  else if lista_col3.ItemIndex = 1 then
  begin
    PadraoDaCamisa[0] := $28;
    PadraoDaCamisa[1] := $61;
  end
  else
  begin
    PadraoDaCamisa[0] := $00;
    PadraoDaCamisa[1] := $64;
  end;
end;
