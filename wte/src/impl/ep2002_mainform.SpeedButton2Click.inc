{ MainForm.SpeedButton2Click -- 0x00410fa4, 27 bytes.
  Spec: wte/re/spec/MainForm.SpeedButton2Click.md

  O ` Sair    `: pergunta, e sai se a resposta for sim. O 6 do original e
  `mrYes`, e casa com o `.dfm` do `ficha_salida` -- ` Sim` com `ModalResult = 6`
  e `Nao` com 7, nenhum dos dois com `OnClick`.

  O ORIGINAL CHAMA A `exit()` DA RTL DE C, e o port chama
  `Application.Terminate`. A diferenca e de fecho, nao de efeito: a `exit()`
  mata o processo de dentro do `OnClick`, com o formulario ainda na tela; o
  `Terminate` encerra o laco de mensagens e desmonta os formularios. As duas
  terminam com codigo zero, e a imagem de CD ja esta fechada nos dois casos --
  este port abre e fecha o `TCdImage` em cada gravacao e nao mantem descritor
  entre operacoes.

  Matar o processo de dentro de um `OnClick` da LCL deixaria o GTK sem chance
  de liberar a janela, e o `:98` guardaria a janela orfa -- que e exatamente a
  armadilha que derruba o golden seguinte.

  Nao ha "salvar ao sair" para fazer: o editor grava in-place a cada operacao,
  entao o que estava para ser gravado ja foi. }
begin
  REMark('MainForm.SpeedButton2Click');
  if ficha_salida.ShowModal = mrYes then
    Application.Terminate;
end;
