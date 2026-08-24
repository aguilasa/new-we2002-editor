{ MainForm.boton_dialogo_texClick -- 0x0040dfe8, 448 bytes.
  Spec: wte/re/spec/MainForm.boton_dialogo_texClick.md

  Abre o `dialogo_tex` (TOpenDialog, propriedades do DFM) e guarda o `.tex`
  escolhido. IRMAO EXATO do `boton_dialogo_weClick`, e escrito espelhando-o.

  NAO GRAVA NA IMAGEM. O arquivo que ele abre e a textura externa; quem leva
  esses bytes para a ROM e o `boton_tex2isoClick`, que ja esta portado e tem
  gate proprio (`golden-06-textura`).

  UMA DIVERGENCIA DELIBERADA, e ela ja estava tomada e escrita antes deste
  corpo existir -- ver `TexturaEscolhida` no `we2002_estado`. O original guarda
  um `FILE*` em `0x00432e60` e o tamanho em `0x00434598`, mantendo o arquivo
  ABERTO pela sessao; o port guarda CAMINHO e tamanho, e abre e fecha por
  operacao. Consequencia visivel: no original, apagar o `.tex` depois de
  escolhe-lo nao impede a gravacao (o descritor continua valido); aqui impede.
  Nenhum byte de imagem depende disso, e o `boton_tex2isoClick` grava o mesmo
  conteudo pelos dois caminhos.

  POR ISSO A LEITURA DE `0x00417170` NAO E PRE-REQUISITO DESTE CORPO. A spec a
  listava como metade nao medida, e ela e a rotina de I/O da RTL que abre o
  arquivo e le o tamanho -- exatamente o par que o port substitui pelo caminho.
  O que se faz com os BYTES do `.tex` e assunto do `boton_tex2isoClick`.

  O `Execute` nao roda no gate, pela mesma razao do irmao: sem gerenciador de
  janela o gtk2 nao recebe teclado, entao o lado port nao digita caminho em
  dialogo nenhum. Quem semeia a textura no gate e o `FormShow`, por
  `WTE_TEXTURA`, e os dois caminhos terminam no MESMO par de globais. Este
  corpo existe para o uso a mao.

  E ELE LIGA O `boton_tex2iso`, como o original faz em `0x0040e17d` --
  `SetEnabled(True)` pela VMT[0x64] sobre o campo `0x0474`. O botao nasce
  `Enabled = False` no DFM: sem fonte escolhida nao ha o que gravar. }
begin
  REMark('MainForm.boton_dialogo_texClick');
  if not dialogo_tex.Execute then
    Exit;
  if not FileExists(dialogo_tex.FileName) then
  begin
    texto_dialogo_tex.Caption :=
      'nao foi possivel abrir ' + ExtractFileName(dialogo_tex.FileName);
    Exit;
  end;
  TexturaEscolhida := dialogo_tex.FileName;
  TexturaTamanho := TamanhoDoArquivo(TexturaEscolhida);
  texto_dialogo_tex.Caption := ExtractFileName(TexturaEscolhida);
  boton_tex2iso.Enabled := True;
end;
