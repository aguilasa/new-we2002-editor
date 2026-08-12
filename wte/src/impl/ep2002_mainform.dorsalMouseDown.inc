{ MainForm.dorsalMouseDown -- 0x00410ddc, 203 bytes.
  Spec: wte/re/spec/MainForm.dorsalMouseDown.md

  O botao DIREITO sobre um numero de camisa abre a ficha do jogador. O
  esquerdo nao passa daqui -- quem o atende e o `dorsalClick`, e os dois
  eventos convivem no mesmo rotulo.

  O teste e `Button = mbRight`, e no `TMouseButton` da VCL isso e o valor **1**
  (`mbLeft = 0`, `mbRight = 1`, `mbMiddle = 2`); a LCL declara a mesma ordem,
  entao a comparacao por nome vale nos dois.

  O bloco de selecao e LETRA POR LETRA o do `dorsalClick`: mesmo
  `Copy(Name, 7, 2)`, mesmo `ItemIndex := numero - 1`, mesmo `MarcaCamisa`. O
  original repete o codigo em vez de chamar uma rotina comum, e a repeticao
  esta reproduzida aqui em vez de fatorada -- fatorar mudaria a ordem de
  execucao se um dos dois lados ganhar uma linha depois, e a fidelidade e o
  criterio.

  No fim ele CHAMA o `mostrar_jugadorClick` passando o `mostrar_jugador_1`
  como `Sender` -- nao um botao qualquer, o titular. E o que faz o
  `LadoTitular` daquele handler devolver verdadeiro e a ficha abrir com o time
  de cima. }
var
  numero: Integer;
begin
  REMark('MainForm.dorsalMouseDown');
  if lista_equipos.ItemIndex < 0 then
    Exit;
  if Button <> mbRight then
    Exit;
  if (Sender is TStaticText) and (TStaticText(Sender) <> CamisaMarcada) then
  begin
    numero := StrToIntDef(Copy(TComponent(Sender).Name, 7, 2), 0);
    if numero <= 0 then
      Exit;
    lista_jugadores_1.ItemIndex := numero - 1;
    MarcaCamisa(numero);
  end;
  mostrar_jugadorClick(mostrar_jugador_1);
end;
