{ MainForm.mostrar_estrategiaClick -- 0x00410220, 1.446 bytes.
  Spec: wte/re/spec/MainForm.mostrar_estrategiaClick.md

  ESCOPO: navegacao, pela mesma divisao do irmao. Encher a tela de tatica
  (`0x0040a0b4`, 1.443 bytes) e da WTE-TASK-26, dona do formulario
  `estrategia`. }
var
  titular: Boolean;
begin
  REMark('MainForm.mostrar_estrategiaClick');
  titular := LadoTitular(Sender, 'mostrar_estrategia_1');
  if titular then
    TimeEmEdicao := lista_equipos_1.ItemIndex
  else
    TimeEmEdicao := lista_equipos_2.ItemIndex;
  estrategia.ShowModal;
end;
