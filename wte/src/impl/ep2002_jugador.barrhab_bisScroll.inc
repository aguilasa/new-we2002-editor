{ jugador.barrhab_bisScroll -- 0x00407bb4, 300 bytes.
  Spec: wte/re/spec/jugador.barrhabScroll.md

  As sete ultimas barras de habilidade, `barrhab10..16`. Copia literal do
  `barrhabScroll` com `Copy(Sender.Name, 8, 2)` -- dois digitos. O `_bis` do
  nome e a largura do numero, nao outra familia de controles. }
begin
  REMark('jugador.barrhab_bisScroll');
  if not (Sender is TComponent) then
    Exit;
  AtualizaHabilidade(Copy(TComponent(Sender).Name, 8, 2), ScrollPos);
end;
