{ MainForm.lista_jugadores_1Change -- 0x0040f8b8.
  Spec: wte/re/spec/MainForm.lista_jugadores_1Change.md

  O menor handler do formulario: 28 bytes, e o corpo inteiro e uma chamada.
  Passa `ItemIndex + 1` para a rotina que marca a camisa -- o `+1` e a unica
  aritmetica do original, e diz que ela numera jogador a partir de 1 enquanto
  o combo numera a partir de 0.

  Nao ha guarda de `ItemIndex = -1` aqui porque o original tambem nao tem: com
  a lista vazia o argumento vira `0`, e quem decide o que fazer com isso e a
  `MarcaCamisa` (que, ao contrario do original, nao estoura -- ver o `.aux.inc`
  ao lado).

  Nao ha `QSignalBlocker` equivalente, e isso e medido, nao suposto: o
  `wte/tools/check_lcl_combo.py` roda o `wte/tests/test_lcl_combo.pas` a cada
  `make -C wte check` e mostra que a LCL/gtk2 NAO dispara `OnChange` quando o
  codigo atribui `ItemIndex` -- igual ao Win32 do original, ao contrario do Qt
  do newWe2002, que precisou bloquear sinal nas cargas de time. }
begin
  REMark('MainForm.lista_jugadores_1Change');
  MarcaCamisa(lista_jugadores_1.ItemIndex + 1);
end;
