{ MainForm.iguala_nombresClick -- 0x0040d43c, 248 bytes.
  Spec: wte/re/spec/MainForm.iguala_nombresClick.md

  "Usar Nome1 nos 3 tipos de nomes" -- e o que a dica do botao diz no DFM.
  Copia o texto do primeiro campo para os outros dois, cada um truncado ao que
  cabe nele:

    edit_nombre2.Text := Copy(edit_nombre1.Text, 1, <max do campo 2>)
    edit_nombre3.Text := Copy(edit_nombre1.Text, 1, 3)

  O `3` e literal no original e casa com o `MaxLength = 3` que o proprio DFM
  poe no campo -- e a abreviatura.

  O OUTRO LIMITE VEM DE UMA GLOBAL QUE NAO FOI MEDIDA. O original usa
  `DWORD[0x00433b48] - 1`, uma global de BSS que ninguem escreve por `mov`
  direto e cujo valor em execucao esta por medir. O mesmo numero aparece uma
  segunda vez, no `MaxLength` que o original poe em `edit_nombre2` ao carregar
  a imagem -- os dois sao `global - 1`.

  Aqui ele sai do TAMANHO DO CAMPO na camada de dados: `names` e
  `array[0..19] of AnsiChar`, entao cabem 19 caracteres mais o terminador. E o
  metodo da secao 4.2 do plano -- o mesmo numero por outro caminho --, mas
  DESTA VEZ SEM CONFIRMACAO CRUZADA: se a global valer outra coisa, o
  truncamento diverge. Esta na spec como pendencia nomeada, e e entrada da
  WTE-TASK-36.

  NAO GRAVA. Mexe so nos dois `TEdit`; quem leva nome para a imagem e o
  `boton_nombres2isoClick`, da WTE-TASK-27. }
begin
  REMark('MainForm.iguala_nombresClick');
  edit_nombre2.Text := Copy(edit_nombre1.Text, 1, TAMANHO_DO_NOME - 1);
  edit_nombre3.Text := Copy(edit_nombre1.Text, 1, 3);
end;
