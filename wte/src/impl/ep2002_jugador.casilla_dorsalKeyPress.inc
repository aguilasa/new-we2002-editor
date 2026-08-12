{ jugador.casilla_dorsalKeyPress -- 0x00408b50, 73 bytes.
  Spec: wte/re/spec/jugador.casilla_dorsalKeyPress.md

  Filtro de tecla do campo de numero de camisa da ficha: **so digito**, mais o
  BackSpace. Qualquer outra tecla vira #0, que e como a VCL e a LCL descartam
  a tecla no `OnKeyPress`.

  O `Return` NAO e engolido: ele passa pelo filtro (nao e digito, entao vira
  #0) DEPOIS de ter movido o foco. A ordem e a do original -- primeiro o
  encadeamento, depois o filtro --, e ela importa: invertida, o `Return`
  chegaria zerado no teste do `#13` e o foco nunca andaria.

  A condicao que guarda o encadeamento NAO foi medida: o original so move o
  foco se `DWORD[0x00433614 + 44*0x004335c4] <> 0`, uma tabela de 44 bytes por
  entrada indexada por uma global que esta task nao identificou. Ate saber o
  que ela guarda, o port move o foco sempre -- e isso e divergencia declarada,
  nao descuido. Ver a secao Notas da spec. }
begin
  REMark('jugador.casilla_dorsalKeyPress');
  if Key = #13 then
    casilla_precio.SetFocus;
  if (Key <> #8) and not (Key in ['0'..'9']) then
    Key := #0;
end;
