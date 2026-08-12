{ jugador.barrhabScroll -- 0x00407a88, 300 bytes.
  Spec: wte/re/spec/jugador.barrhabScroll.md

  Arrastar uma das nove primeiras barras de habilidade. O indice sai do NOME do
  componente, `Copy(Sender.Name, 8, 1)` -- um digito, portanto `barrhab1..9`.
  Os sete restantes sao do `barrhab_bisScroll`, que e o mesmo corpo com `2` no
  lugar do `1`.

  O corpo compartilhado esta no `.aux.inc`. }
begin
  REMark('jugador.barrhabScroll');
  if not (Sender is TComponent) then
    Exit;
  AtualizaHabilidade(Copy(TComponent(Sender).Name, 8, 1), ScrollPos);
end;
