{ MainForm.boton_dialogo_weClick -- 0x0040bd60.
  Spec: wte/re/spec/MainForm.boton_dialogo_weClick.md

  Abre o `dialogo_we` (TOpenDialog, filtro `ISO do W11(.bin)|*.BIN`, titulo
  `Abre`, tudo vindo do DFM) e carrega a imagem escolhida. A carga GRAVA:
  injeta sete setores vindos de `dat.bin[0x20000..]` -- ver
  `we2002_estado.InjetaPatchDeArranque` e `wte/re/assets.md` secao 8.2.

  O `Execute` nao chega a rodar no gate: sem teclado no `:99` o lado port nao
  digita caminho em dialogo. Quem carrega ali e o `FormShow`, pela linha de
  comando. Este caminho existe para o uso a mao. }
begin
  REMark('MainForm.boton_dialogo_weClick');
  if not dialogo_we.Execute then
    Exit;
  if AbreImagem(dialogo_we.FileName) then
  begin
    { As dez paletas de bandeira que o `we2002_core` nao le (CORR-WTE-083) --
      o mesmo passo do `FormShow`, pelo mesmo motivo. Os dois caminhos de
      abrir imagem precisam dele. }
    CarregaBandeirasQueOCoreNaoLe;
    texto_dialogo_we.Caption := ExtractFileName(dialogo_we.FileName);
  end
  else
    texto_dialogo_we.Caption :=
      'nao foi possivel abrir ' + ExtractFileName(dialogo_we.FileName);

  { A segunda das duas chamadas a `0x004042d4` -- a outra e o `FormShow`. O
    original conta em `0x0040c241` e mostra na instrucao seguinte, tenha a
    carga dado certo ou nao: com imagem que nao abriu, o `fgetc` devolve -1,
    o `-1 < 23` cai no ramo do vinculo, e o rotulo mostra o total. }
  AtualizaBlocosLivresDeMl;
end;
