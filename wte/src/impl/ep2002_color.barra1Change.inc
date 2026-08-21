{ ficha_color.barra1Change -- 0x00406358, 44 bytes.
  Spec: wte/re/spec/ficha_color.barra1Change.md

  A trilha do INICIO da faixa. Duas linhas: mantem a invariante `barra1 <
  barra2` e manda a `AtualizaFaixa` reler as duas.

  A CORRECAO E EM `barra1`, e nao em `barra2` -- este handler abaixa o proprio
  controle para um a menos que o fim, e o `barra2Change` faz o espelho. Trocar
  qual dos dois cede faria a faixa andar sozinha quando o usuario empurra uma
  ponta contra a outra.

  `Position :=` dispara `OnChange` nos dois widgetsets, entao a correcao
  reentra neste handler uma vez. A segunda passagem ja acha a invariante
  valendo e nao corrige nada -- e por isso que a recursao para. }
begin
  REMark('ficha_color.barra1Change');
  if barra2.Position <= barra1.Position then
    barra1.Position := barra2.Position - 1;
  AtualizaFaixa(Self);
end;
