{ ficha_color.BitBtn3Click -- 0x004069e8, 35 bytes.
  Spec: wte/re/spec/ficha_color.BitBtn3Click.md
  Dono: CORR-WTE-081, segunda das tres gravacoes orfas.

  O `OK` do editor de cor, e a SETIMA rota de escrita na imagem de CD. Trinta e
  cinco bytes de corpo e quatro chamadas -- e a terceira delas grava 383 bytes
  por time.

  A ORDEM NAO COMUTA, e o original a escreve nesta:

    0x00405B48  a paleta desce do vetor de edicao para o slot 1
    0x00404F90  o slot 1 vira slot 0 -- e a confirmacao
    0x004051A4  o slot 0 vai para a imagem      <- A ESCRITA
    0x004056C8  redesenha o uniforme, jogo 0

  Gravar antes de confirmar gravaria o que estava la; confirmar antes de salvar
  a paleta confirmaria sem a ultima cor mexida.

  O SLOT 1 E O SLOT 0 DESTE PORT nao sao dois vetores como no original. O slot
  1 e o `Jogo` -- e dele que a tela do `MainForm` desenha --, e o slot 0 e a
  `Foto` da `wte_cor`, a copia que o `BitBtn1` restaura. Entao `copia_slot(1,
  0)` aqui e refazer a foto: depois do `OK`, o `Original` volta para o que
  acabou de ser gravado, e nao para o que a janela abriu. E o que o original
  faz.

  O `xor edx,edx` antes do redesenho e literal: jogo 0, sempre, mesmo que o
  `lista_col1` esteja no segundo uniforme. Igual ao `BitBtn2`, e pela mesma
  razao -- o `MainForm` mostra o primeiro.

  NAO FECHA A JANELA, e nao e esquecimento: o `.dfm` traz `ModalResult = 1` no
  `BitBtn3`, e quem fecha e o widgetset. Nao ha `Hide` nem escrita em
  `ModalResult` no corpo.

  NAO CONFERE NADA antes de gravar -- nem imagem aberta, nem time selecionado.
  Clicar `OK` grava. As guardas do port estao na `GravaBlocoDeCorNaImagem`, e
  todas elas sao recusa de gravar, nunca gravacao parcial. }
begin
  REMark('ficha_color.BitBtn3Click');
  SalvaPaleta(TimeEmCor);
  GuardaOriginal(TimeEmCor);
  GravaBlocoDeCorNaImagem(TimeEmCor);
  RedesenhaUniformeEmVigor(0);
end;
