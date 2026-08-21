{ estrategia.malla1MouseDown -- 0x00409f4c, 180 bytes.
  Spec: wte/re/spec/estrategia.malla1MouseDown.md

  A malha de quatro colunas. **O X escolhe a coluna e o Y escolhe a linha** --
  o `Left` de cada `simboloN` e fixo, quem anda e o `Top`.

  Os tres numeros nao estao aqui: `MALHA_PASSO_X`, `MALHA_PASSO_Y` e
  `MALHA_FOLGA` vem da `wte_zonas`, que os le do `.text` e os confere contra o
  `.lfm` a cada `make check`. Escrever 24, 16 e 3 neste arquivo transformaria
  tres medidas em tres literais.

  O marcador e achado por NOME (`simbolo` + o indice), como no original -- que
  monta a cadeia com `IntToStr` e chama `FindComponent`. Vetor de ponteiro
  daria o mesmo resultado e perderia a propriedade que interessa: nome que nao
  casa falha dizendo qual. }
begin
  REMark('estrategia.malla1MouseDown');
  MoveMarcadorDaMalha(SIMBOLO_PREFIXO, SIMBOLO_COLUNAS, malla1, X, Y);
end;
