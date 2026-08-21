{ MainForm.colorearClick -- 0x00410ea8, 249 bytes.
  Spec: wte/re/spec/MainForm.colorearClick.md

  Abre o editor de cor 2D. Quatro coisas antes do modal e duas depois.

  ANTES: escolhe o item do `lista_col3` pelo padrao de camisa do time, copia o
  indice do time para o global do editor (`0x004335cc`), enche as 16 amostras
  (`0x00405d6c`) e REDESENHA O UNIFORME com o jogo que o `lista_col1` mostra.

  DEPOIS do modal: `banderita1` copia o `bandera`, e `banderita2` tambem se as
  duas listas apontarem para o mesmo time. E o mesmo par de copias do
  `lista_equiposChange` -- as cores podem ter mudado, e as duas bandeirinhas
  nao se redesenham sozinhas.

  O `lista_col3` FICA COMO ESTA, e e a unica parte que este port nao faz. O
  original escolhe entre `NORMAL`, `ROMBOIDAL` e `EXTRA` por dois bytes que ele
  le da imagem para `0x004331d6` e `0x004331d7`, e esses dois bytes NAO estao na
  camada de dados: nem `TTeam` nem `TMlTeam` tem campo de padrao de camisa.
  Inventar de onde eles saem seria pior do que deixar o combo no default do
  formulario. Medido e registrado na spec; e pendencia nomeada, nao esquecimento. }
var
  indice: Integer;
begin
  REMark('MainForm.colorearClick');
  indice := lista_equipos_1.ItemIndex;
  if indice < 0 then
    Exit;

  { O global do editor, copiado UMA vez. Ver `TimeEmCor` na `wte_cor`. }
  TimeEmCor := indice;

  { A FOTO DO SLOT 0, para o `Original` e o `Cancela` do editor terem o que
    restaurar (WTE-TASK-30). No original o slot 0 e refeito a cada troca de
    time, pela carga; aqui a foto sai aqui, e a diferenca so apareceria se o
    time mudasse com o editor aberto -- e ele e modal. }
  GuardaOriginal(indice);

  PreencheAmostras(ficha_color, indice);

  { O redesenho usa o jogo que o combo do EDITOR mostra, e nao 0 -- diferente
    do `lista_equiposChange`, que passa `xor edx,edx`. Abrir o editor com o
    `Segundo` escolhido mantem o Segundo na tela. }
  DesenhaUniforme(home1, home2, indice, ficha_color.lista_col1.ItemIndex,
                  CoresDoUniforme(indice, ficha_color.lista_col1.ItemIndex));

  ficha_color.ShowModal;

  banderita1.Picture.Assign(bandera.Picture);
  if lista_equipos_2.ItemIndex = lista_equipos.ItemIndex then
    banderita2.Picture.Assign(bandera.Picture);
end;
