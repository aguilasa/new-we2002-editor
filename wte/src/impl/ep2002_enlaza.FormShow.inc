{ ficha_enlaza.FormShow -- 0x00402c44. Spec: wte/re/spec/ficha_enlaza.FormShow.md

  Forma `campo` do `wte/re/arranque.md`: uma chamada virtual sobre um campo
  publicado. O campo e o de deslocamento 0x304 -- `BitBtn2`, pelo
  `wte/re/campos.tsv` --, e o slot 0xC0 do VMT de `TBitBtn` nos packages e
  `TWinControl::SetFocus`.

  O `BitBtn2` e o "Nao". Focar o botao NEGATIVO ao abrir e o que impede que um
  `Return` distraido deslinke o jogador -- criterio da fase 6, "nenhuma acao
  destrutiva alcancavel por Return", que aqui ja vem do original. }
begin
  REMark('ficha_enlaza.FormShow');
  BitBtn2.SetFocus;
end;
