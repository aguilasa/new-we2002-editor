{ MainForm.sel_barraClick -- 0x0040c9d0, 61 bytes.
  Spec: wte/re/spec/MainForm.sel_barraClick.md

  Um corpo para os cinco radios (`sel_barra0..4`), e quem decide qual e a
  ARITMETICA DE INDICE DE COMPONENTE, nao o `Sender` comparado com cada botao:

      indice := Sender.ComponentIndex - sel_barra0.ComponentIndex

  Reproduzido como esta. Vale nos dois lados porque os cinco `object` sao
  consecutivos no formulario (posicoes 44 a 48 do `ep2002_mainform.lfm`, mesma
  ordem do `.dfm`), e a LCL cria na ordem do arquivo como a VCL criava. Se
  alguem inserir um componente no meio, os dois quebram junto -- que e a
  fragilidade do original, preservada.

  NAO le a imagem e NAO grava: so move a `track_barra` para o valor que o
  buffer de edicao ja tem. }
var
  indice: Integer;
begin
  REMark('MainForm.sel_barraClick');
  if not (Sender is TComponent) then
    Exit;
  indice := TComponent(Sender).ComponentIndex - sel_barra0.ComponentIndex;
  if (indice < Low(BarrasEmEdicao)) or (indice > High(BarrasEmEdicao)) then
    Exit;
  BarraMarcada := indice;
  track_barra.Position := BarrasEmEdicao[BarraMarcada];
end;
