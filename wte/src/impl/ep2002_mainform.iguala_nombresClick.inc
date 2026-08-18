{ MainForm.iguala_nombresClick -- 0x0040d43c, 248 bytes.
  Spec: wte/re/spec/MainForm.iguala_nombresClick.md

  "Usar Nome1 nos 3 tipos de nomes" -- e o que a dica do botao diz no DFM.
  Copia o texto do primeiro campo para os outros dois, cada um truncado ao que
  cabe nele:

    edit_nombre2.Text := Copy(edit_nombre1.Text, 1, <max do campo 2>)
    edit_nombre3.Text := Copy(edit_nombre1.Text, 1, 3)

  O `3` e literal no original e casa com o `MaxLength = 3` que o proprio DFM
  poe no campo -- e a abreviatura.

  O OUTRO LIMITE E POR TIME, E ISSO FOI MEDIDO. O original usa
  `DWORD[0x00433b48] - 1`, e essa global nao e constante: e a largura do
  registro do time selecionado no lote `OFS_TEAM_NAME_3`, remedida a cada
  `lista_equiposChange`. O mesmo numero aparece no `MaxLength` que ele poe em
  `edit_nombre2`, e agora os dois saem do mesmo lugar aqui tambem --
  `LimiteDoNome2`, no `.aux.inc`, que le `TEAM_NAME_LEN_3`.

  A versao anterior usava `TAMANHO_DO_NOME - 1` = 19, tirado de `names` ser
  `array[0..19] of AnsiChar`. Fechava a aritmetica e estava errada: para o time
  2 o limite e 7, nao 19. O `dump_truncamento.py` agora prova o lote em vez de
  aceitar um destino escrito a mao.

  NAO GRAVA. Mexe so nos dois `TEdit`; quem leva nome para a imagem e o
  `boton_nombres2isoClick`, da WTE-TASK-27. }
begin
  REMark('MainForm.iguala_nombresClick');
  edit_nombre2.Text := Copy(edit_nombre1.Text, 1,
                           LimiteDoNome2(lista_equipos.ItemIndex));
  edit_nombre3.Text := Copy(edit_nombre1.Text, 1, 3);
end;
