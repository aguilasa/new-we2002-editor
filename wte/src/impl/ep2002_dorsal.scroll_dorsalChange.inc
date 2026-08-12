{ ficha_dorsal.scroll_dorsalChange -- 0x00402b58, 101 bytes.
  Spec: wte/re/spec/ficha_dorsal.scroll_dorsalChange.md

  Uma linha: a legenda mostra `Max - Position + 1`.

  A INVERSAO e o ponto. A barra e vertical (`Kind = sbVertical`), e numa barra
  vertical a posicao cresce para BAIXO -- entao o numero maior tem de ficar em
  cima, e por isso a conta subtrai. Quem escolhe o numero e o `dorsalClick`,
  que faz a conta ao contrario (`Position := Max - numero + 1`); as duas juntas
  se cancelam e a legenda mostra o numero pedido.

  Os deslocamentos de campo do `TScrollBar` nao foram adivinhados: `SetMin`,
  `SetMax` e `SetPosition` do `vcl60.bpl` sao tres invocacoes finas do mesmo
  `SetParams(Position, Min, Max)`, e a ordem em que cada uma carrega os
  argumentos identifica os tres campos -- `FPosition = 0x20c`, `FMin = 0x210`,
  `FMax = 0x214`. Uma primeira leitura, por varredura de prologo, tinha trocado
  os tres; ver a spec. }
begin
  REMark('ficha_dorsal.scroll_dorsalChange');
  etiq_dorsal.Caption :=
    IntToStr(scroll_dorsal.Max - scroll_dorsal.Position + 1);
end;
