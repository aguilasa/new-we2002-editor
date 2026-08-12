{ jugador.casilla_nombreKeyPress -- 0x00408af8, 88 bytes.
  Spec: wte/re/spec/jugador.casilla_nombreKeyPress.md

  Filtro de tecla do campo de nome da ficha. O conjunto aceito e o mesmo que o
  FILTRO DE EXIBICAO de nome do original usa (`0x0040b2d8`, medido na
  WTE-TASK-25): letra, digito, ponto e espaco. Aqui entra tambem o BackSpace;
  o resto vira #0.

  Nao ha limite de comprimento nesta funcao -- o truncamento vem do
  `MaxLength` do proprio `TEdit` e do buffer de gravacao, e e a
  WTE-TASK-36 quem inventaria isso.

  `Return` move o foco para o campo de numero, e o filtro roda depois. Mesma
  ordem do original, pela mesma razao do `casilla_dorsalKeyPress`. }
begin
  REMark('jugador.casilla_nombreKeyPress');
  if Key = #13 then
    casilla_dorsal.SetFocus;
  if not ((Key = ' ') or (Key = '.') or (Key = #8)
          or (Key in ['0'..'9']) or (Key in ['A'..'Z']) or (Key in ['a'..'z'])) then
    Key := #0;
end;
