{ ficha_about.FormCreate -- 0x00402de4. Spec: wte/re/spec/ficha_about.FormCreate.md

  Forma `vazio` do `wte/re/arranque.md`: o corpo do original e UM byte, um
  `ret`. O handler esta ligado no DFM (`OnCreate = FormCreate`) e nao faz nada
  -- e o unico dos 18 assim, e por isso o `ficha_about` e o unico formulario
  que fica com a cor de projeto (`clBtnFace`) na tela.

  Existe como corpo escrito e nao como stub de propriedade. Stub e "ainda nao
  se sabe"; isto e "medido, e nao faz nada", e a diferenca aparece no trace:
  `REStub` diz que ha buraco, `REMark` diz que passou por aqui. }
begin
  REMark('ficha_about.FormCreate');
end;
