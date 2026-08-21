{ ficha_color.lista_col2Change -- 0x004068ec, 32 bytes.
  Spec: wte/re/spec/ficha_color.lista_col2Change.md

  O combo de CHUTEIRA, e ele escreve o MESMO global que o `lista_col1change`:
  os dois sao "qual conjunto dentro da familia", e a familia corrente decide
  qual dos dois esta valendo. Foi por isso que o `botonClick` le o `ItemIndex`
  de `lista_col1` ou `lista_col2` conforme a familia seja 1 ou 2.

  **A familia 2 nao e portada** (ver `FamiliaPortada` na `wte_cor`): as cores
  de chuteira nao estao na camada de dados, e descobrir onde elas moram na
  imagem e trabalho que ninguem pediu. O `conjunto` e escrito assim mesmo,
  porque e estado do editor e nao dado -- o que nao acontece e o
  `PreencheAmostras` achar fonte, e ele devolve False sem pintar. O original
  pinta, com o ponteiro de fonte nao inicializado.

  O combo esta `Enabled = False` no `.dfm`, entao na pratica so o `botonClick`
  o alcanca. }
begin
  REMark('ficha_color.lista_col2Change');
  SalvaPaleta(TimeEmCor);
  CorEmEdicao.conjunto := lista_col2.ItemIndex;
  PreencheAmostras(Self, TimeEmCor);
end;
