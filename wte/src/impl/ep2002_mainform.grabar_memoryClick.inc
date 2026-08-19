{ MainForm.grabar_memoryClick -- 0x0040f69c, 540 bytes.
  Spec: wte/re/spec/MainForm.grabar_memoryClick.md

  O unico dos seis handlers de gravacao da WTE-TASK-27 que NAO toca a imagem de
  CD: ele emite um arquivo `.mcr` de 128 KiB -- um memory card PSX com o time
  selecionado dentro. A imagem so e LIDA.

  O corpo aqui e so o dialogo e a recusa; quem escreve bytes e a
  `GravaCartaoDeMemoria` (`0x0040f150`).

  O LACO importa. O original nao aceita e nao desiste na primeira: ele reabre o
  `TSaveDialog` enquanto o nome escolhido for o mesmo do `.mcr` que o editor ja
  tem aberto para importar. Sair do laco tem duas portas -- nome bom, ou
  cancelar --, e so a primeira leva ao aviso de sucesso. }
var
  destino: string;
begin
  REMark('MainForm.grabar_memoryClick');
  if (ImagemAberta = '') or (lista_equipos.ItemIndex < 0) then
    Exit;

  repeat
    { A afordancia de harness: com `WTE_MCR` semeado o destino ja esta escolhido
      e o dialogo nao entra. Ver `CartaoDestino` no `we2002_estado`. }
    if CartaoDestino <> '' then
    begin
      destino := CartaoDestino;
      Break;
    end;
    if not dialogo_grabar_memory.Execute then
      Exit;
    destino := dialogo_grabar_memory.FileName;
    if destino <> dialogo_mcr.FileName then
      Break;
    { A recusa: gravar por cima do `.mcr` de importacao apagaria a fonte que o
      proprio editor esta usando. }
    ficha_error2.etiq1.Caption :=
      'That file name is already being used by Team Editor';
    ficha_error2.ShowModal;
  until False;

  if not GravaCartaoDeMemoria(destino, lista_equipos.ItemIndex) then
    Exit;

  ficha_info3.etiq1.Caption := 'A MCR foi salva!!!.    ';
  ficha_info3.ShowModal;
end;
