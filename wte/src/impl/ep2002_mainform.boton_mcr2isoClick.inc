{ MainForm.boton_mcr2isoClick -- 0x0040c46c, 1.361 bytes.
  Spec: wte/re/spec/MainForm.boton_mcr2isoClick.md

  Leva o time inteiro do memory card para a imagem: 23 jogadores, 23 numeros
  de camisa, formacao, tatica e cobradores.

  QUASE NADA DELE E GRAVACAO NOVA. O corpo esta na `ImportaCartaoParaImagem`
  do `.aux.inc`, e ela e um laco em volta da `GravaJogador` e da
  `GravaNumeroDaCamisa` -- as duas portadas e com golden verde desde a
  WTE-TASK-27. Reimplementar aqui duplicaria cinco ramos que ja tem gate.

  A RECUSA E DELE, e nao da rotina de gravacao: aquela recusa um slot por
  falta de bloco, esta recusa os 23 de uma vez, contando ANTES quantos blocos
  o import precisaria. }
begin
  REMark('MainForm.boton_mcr2isoClick');
  if lista_equipos.ItemIndex < 0 then
    Exit;
  MostraCodigo(ImportaCartaoParaImagem(lista_equipos.ItemIndex));
  { O contador de blocos livres mudou -- o import alocou. Os oito handlers de
    mover atualizam o rotulo do mesmo jeito ao terminar. }
  casilla_xmlibres.Caption := IntToStr(BlocosLivresDeMl);
end;
