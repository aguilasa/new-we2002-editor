{ Rotinas internas do `ficha_color` -- WTE-TASK-29, sexta passagem.

  Sao as tres que o original chama de mais de um handler do editor de cor e
  que precisam dos CAMPOS do formulario -- por isso nao cabem na
  `wte_render2d`, que e deliberadamente cega para a classe do formulario.
  Ver `wte/src/impl/README.md`.

  A quarta rotina compartilhada -- a `0x00405bc8`, que pinta uma amostra --
  MORA NA `wte_render2d`, e nao aqui, porque o `MainForm.colorearClick`
  tambem a alcanca (via `PreencheAmostras`) e `ep2002_mainform` nao pode usar
  `ep2002_color` na interface sem fechar ciclo. }

{ AtualizaFaixa -- 0x004062b4, 164 bytes.
  Spec: wte/re/spec/ficha_color.barra1Change.md

  Le a faixa do gradiente das duas trilhas e move os tres indicadores dela.

  **`barra1` e o INICIO e `barra2` e o FIM**, e os dois contam de UM: sao
  `Min = 1`, `Max = 16` no `.dfm`, e a base bate com a do vetor do original,
  onde `faixa_fim` e o elemento zero (ver o cabecalho da `wte_cor`).

  As quatro contas de pixel sao literais do `.text` -- `32` e a largura de uma
  amostra, e os `-11`, `-19`, `0x1f7` e `0x1ff` sao as folgas de cada
  indicador. Elas nao se derivam de nada: sao coordenadas de tempo de projeto,
  e o unico jeito de conferi-las e a tela. }
procedure AtualizaFaixa(dono: Tficha_color);
begin
  CorEmEdicao.faixa_ini := dono.barra1.Position;
  CorEmEdicao.faixa_fim := dono.barra2.Position;
  dono.seleccion.Left := CorEmEdicao.faixa_ini * 32 - 11;
  dono.seleccion.Width := $1F7 - 32 * (15 - CorEmEdicao.faixa_fim
                                       + CorEmEdicao.faixa_ini);
  dono.flecha_izquierda.Left := CorEmEdicao.faixa_ini * 32 - 19;
  dono.flecha_derecha.Left := $1FF - 32 * (16 - CorEmEdicao.faixa_fim);
end;

{ MostraCorSelecionada -- o trecho de cauda que o `gradienteClick`, o
  `oscurecerClick`, o `aclararClick` e o `colorMouseDown` repetem literal.

  Poe as tres barras de R, G e B nos cinco bits da amostra selecionada. Nao e
  a `PintaUmaAmostra`: aquela tambem grava no vetor e pinta o `TLabel`, e aqui
  o vetor ja esta certo -- so a leitura da tela e que ficou para tras. }
procedure MostraCorSelecionada(dono: Tficha_color);
var
  canais: TCanais;
begin
  if (CorEmEdicao.entrada < 0) or (CorEmEdicao.entrada >= COR_AMOSTRAS) then
    Exit;
  canais := DecodificaCor(CorEmEdicao.cores[CorEmEdicao.entrada]);
  dono.barra_rojo.Position := canais[0] shr RENDER_EXPANSAO;
  dono.barra_verde.Position := canais[1] shr RENDER_EXPANSAO;
  dono.barra_azul.Position := canais[2] shr RENDER_EXPANSAO;
end;

{ AplicaAosDesenhos -- a outra cauda repetida, e a que grava.

  Grava o vetor de volta na fonte (`SalvaPaleta`, a `0x00405b48`) e redesenha
  o que a familia escolhida manda. **O teste e o RADIO, e nao a variavel
  `familia`**: e assim no original, os dois `if` sao independentes, e nao ha
  `else` entre eles. Com `boton2` ou `boton3` marcados nenhum dos dois corre e
  o desenho fica como estava -- que e o comportamento certo para as duas
  familias que este port nao desenha.

  A ordem tambem e do original: grava PRIMEIRO, desenha depois. O desenho le
  da fonte, entao inverter mostraria a cor anterior. }
procedure AplicaAosDesenhos(dono: Tficha_color);
begin
  if dono.boton0.Checked then
  begin
    SalvaPaleta(TimeEmCor);
    RedesenhaBandeiraEmVigor;
  end;
  if dono.boton1.Checked then
  begin
    SalvaPaleta(TimeEmCor);
    RedesenhaUniformeEmVigor(dono.lista_col1.ItemIndex);
  end;
end;
