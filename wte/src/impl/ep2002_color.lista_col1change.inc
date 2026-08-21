{ ficha_color.lista_col1change -- 0x004068b0, 60 bytes.
  Spec: wte/re/spec/ficha_color.lista_col1change.md

  Troca o jogo de uniforme -- `Primeiro` ou `Segundo`.

  A ORDEM E O QUE IMPORTA AQUI, e ela tem tres passos que nao comutam:

    1. grava o vetor de volta no jogo ANTERIOR (`SalvaPaleta`). Sem isto, o
       que o usuario acabou de editar no Primeiro se perde ao ir para o
       Segundo;
    2. so entao troca o `conjunto`;
    3. recarrega as 16 do jogo novo e redesenha o uniforme.

  O nome do handler e minusculo no `c` -- `lista_col1change`, e nao
  `...Change`. E como o `.dfm` o escreve, e o gerador nao o corrige: nome de
  handler e chave de busca contra o binario. }
begin
  REMark('ficha_color.lista_col1change');
  SalvaPaleta(TimeEmCor);
  CorEmEdicao.conjunto := lista_col1.ItemIndex;
  PreencheAmostras(Self, TimeEmCor);
  RedesenhaUniformeEmVigor(lista_col1.ItemIndex);
end;
