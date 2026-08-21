{ ficha_color.FormCreate -- 0x00405dcc, 116 bytes.
  Spec: wte/re/spec/ficha_color.FormCreate.md

  Quatro movimentos, e o terceiro e o que a spec adiou ate esta task: os cinco
  globais do editor de cor 2D. Eles moram na `wte_cor` agora, e o cabecalho
  daquela unidade explica cada um.

  A COR DE FUNDO E LITERAL, `$00E68F41`. No `TColor` do Delphi isso e
  `$00BBGGRR` -- azul 230, verde 143, vermelho 65 --, e e o mesmo azul do resto
  do editor. Escrever `$0041 8FE6` daria laranja.

  O `BringToFront` das duas primeiras nao e enfeite: `color1` e a amostra
  selecionada no arranque e `recuadro2` e a moldura que a marca, e as duas
  precisam ficar por cima das outras 15 amostras. }
begin
  REMark('ficha_color.FormCreate');
  Color := TColor($00E68F41);

  { Os dois primeiros globais, ANTES da ordem-z -- e a ordem do original. }
  CorEmEdicao.familia := COR_FAMILIA_BANDEIRA;
  CorEmEdicao.entrada := 0;

  color1.BringToFront;
  recuadro2.BringToFront;

  lista_col1.ItemIndex := 0;
  lista_col2.ItemIndex := 0;

  { E os tres do fim: conjunto 0, faixa de 1 a 16. }
  CorEmEdicao.conjunto := 0;
  CorEmEdicao.faixa_ini := 1;
  CorEmEdicao.faixa_fim := COR_AMOSTRAS;
end;
