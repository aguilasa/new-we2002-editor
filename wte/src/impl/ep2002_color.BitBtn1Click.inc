{ ficha_color.BitBtn1Click -- 0x00406968, 93 bytes.
  Spec: wte/re/spec/ficha_color.BitBtn1Click.md

  O `Original`: desfaz tudo o que foi editado desde que a janela abriu, SEM
  fecha-la.

  O SLOT 0 NAO EXISTIA NESTE PORT ATE AGORA, e a `wte_cor` registrava a
  ausencia nas suas proprias palavras -- "o slot 0 do original, a copia
  intocada que o `BitBtn1` restaura, nao tem equivalente aqui, e quem precisar
  dele e o desfazer, que ainda nao foi portado". Este handler e o desfazer;
  `GuardaOriginal`/`RestauraOriginal` chegaram junto com ele.

  A ULTIMA LINHA E UMA BUSCA, NAO UMA CONTA. O combo de forma mostra nome de
  time e INDEXA a `FORMA_PADRAO`, entao repor a selecao exige achar a primeira
  posicao cujo valor seja a forma restaurada.

  E A BUSCA DO PORT PARA NO FIM DA TABELA. A do original nao para: o laco em
  `0x004069A6` incrementa ate encontrar o byte e nao confere limite, entao
  forma fora das 95 sai varrendo alem da tabela. Reproduzir isso seria
  reproduzir comportamento indefinido, que nao e comportamento -- a mesma
  decisao, com as mesmas palavras, que o `botonClick` tomou para a familia fora
  de 0..3. Forma ausente deixa o combo como esta. }
var
  forma, i: Integer;
begin
  REMark('ficha_color.BitBtn1Click');
  RestauraOriginal(TimeEmCor);
  PreencheAmostras(Self, TimeEmCor);
  RedesenhaBandeiraEmVigor;
  RedesenhaUniformeEmVigor(lista_col1.ItemIndex);

  forma := FormaEmVigor(TimeEmCor);
  for i := 0 to TIMES_TOTAL - 1 do
    if FORMA_PADRAO[i] = forma then
    begin
      lista_col0.ItemIndex := i;
      Break;
    end;
end;
