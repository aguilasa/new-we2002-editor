{ MainForm.mostrar_jugadorClick -- 0x0040f8d4, 2.378 bytes.
  Spec: wte/re/spec/MainForm.mostrar_jugadorClick.md

  ESCOPO: navegacao. Das 2.378 instrucoes do original, o que a WTE-TASK-25 deve
  e escolher o par de listas certo, guardar a selecao e mostrar o formulario.
  Encher a ficha -- `0x00404820` e `0x0040756c`, 2.734 bytes -- e editar
  jogador, e isso e da WTE-TASK-26, dona do formulario `jugador`. A divisao
  esta escrita no enunciado da task.

  Um corpo serve dois botoes, e quem decide qual e o `Sender.Name`, nao o
  ponteiro -- ver `LadoTitular` no `.aux.inc`. }
var
  titular: Boolean;
begin
  REMark('MainForm.mostrar_jugadorClick');
  titular := LadoTitular(Sender, 'mostrar_jugador_1');
  if titular then
  begin
    TimeEmEdicao := lista_equipos_1.ItemIndex;
    JogadorEmEdicao := lista_jugadores_1.ItemIndex;
  end
  else
  begin
    TimeEmEdicao := lista_equipos_2.ItemIndex;
    JogadorEmEdicao := lista_jugadores_2.ItemIndex;
  end;
  { A ficha abre com o estado que a WTE-TASK-26 vai preencher. Abrir vazio e
    o comportamento honesto do escopo desta task -- o alternativo seria nao
    abrir, e ai o `--show` nao poderia sair. }
  jugador.ShowModal;
end;
