{ estrategia.malla2MouseDown -- 0x0040a000, 180 bytes.
  Spec: wte/re/spec/estrategia.malla2MouseDown.md

  A malha de seis colunas, e o corpo e o do irmao com outro prefixo e outra
  imagem. O original tambem os escreveu duas vezes -- os 180 bytes de cada um
  sao a mesma sequencia de instrucoes com dois imediatos diferentes. Aqui os
  dois chamam a mesma rotina, e a diferenca fica nos argumentos. }
begin
  REMark('estrategia.malla2MouseDown');
  MoveMarcadorDaMalha(TIRADOR_PREFIXO, TIRADOR_COLUNAS, malla2, X, Y);
end;
