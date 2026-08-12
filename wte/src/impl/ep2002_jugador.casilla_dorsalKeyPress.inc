{ jugador.casilla_dorsalKeyPress -- 0x00408b50, 73 bytes.
  Spec: wte/re/spec/jugador.casilla_dorsalKeyPress.md

  Filtro de tecla do campo de numero de camisa da ficha: **so digito**, mais o
  BackSpace. Qualquer outra tecla vira #0, que e como a VCL e a LCL descartam
  a tecla no `OnKeyPress`.

  O `Return` NAO e engolido: ele passa pelo filtro (nao e digito, entao vira
  #0) DEPOIS de ter movido o foco. A ordem e a do original -- primeiro o
  encadeamento, depois o filtro --, e ela importa: invertida, o `Return`
  chegaria zerado no teste do `#13` e o foco nunca andaria.

  A CONDICAO QUE GUARDA O ENCADEAMENTO ESTA MEDIDA desde a decima segunda
  passagem da WTE-TASK-26, e o port deixou de mover o foco sempre. O original
  so encadeia se `DWORD[0x00433614 + 44*0x004335c4] <> 0` -- a terceira coluna
  de offsets do buffer de jogador, indexada pelo buffer em edicao. Ela vale
  zero quando o jogador NAO TEM o campo condicional na imagem, e nesse caso a
  ficha mostra o literal 50 num campo desabilitado: o `Return` nao leva o
  cursor para um campo que nao existe no formato.

  Aqui a mesma pergunta e feita a `JogadorTemCampoCondicional`, do
  `we2002_estado`. }
begin
  REMark('jugador.casilla_dorsalKeyPress');
  if (Key = #13)
     and JogadorTemCampoCondicional(TimeEmEdicao, JogadorEmEdicao) then
    casilla_precio.SetFocus;
  if (Key <> #8) and not (Key in ['0'..'9']) then
    Key := #0;
end;
