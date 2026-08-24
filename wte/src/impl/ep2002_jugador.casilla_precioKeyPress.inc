{ jugador.casilla_precioKeyPress -- 0x00408b9c, 27 bytes.
  Spec: wte/re/spec/jugador.casilla_precioKeyPress.md

  O filtro de tecla do campo de preco. Deixa passar BackSpace e digito, e
  engole o resto -- `mov BYTE PTR [ebx],0x0` em `0x00408bb2`, que e `Key := #0`.

  IRMAO DO `casilla_dorsalKeyPress` E MAIS CURTO QUE ELE: aquele encadeia o
  foco no `Return` e este nao. Medido: o corpo inteiro sao treze instrucoes, e
  a unica comparacao alem do `isdigit` (`0x00419070`) e contra `8`.

  NAO GRAVA NADA. }
begin
  REMark('jugador.casilla_precioKeyPress');
  if (Key <> #8) and not (Key in ['0'..'9']) then
    Key := #0;
end;
