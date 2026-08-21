{ ficha_color.aclararClick -- 0x00406744, 328 bytes.
  Spec: wte/re/spec/ficha_color.aclararClick.md

  Espelho exato do `oscurecerClick`, com a `Clareia` no lugar da `Escurece`.
  O teto do canal e `$F8`, e nao `$FF`: a expansao de cinco para oito bits e
  deslocamento, entao branco satura em 248. Ver `RENDER_MAXIMO`. }
var
  i: Integer;
begin
  REMark('ficha_color.aclararClick');
  for i := CorEmEdicao.faixa_ini to CorEmEdicao.faixa_fim do
  begin
    if (i < 1) or (i > COR_AMOSTRAS) then
      Continue;
    PintaUmaAmostra(Self, i, Clareia(CorEmEdicao.cores[i - 1]));
  end;
  MostraCorSelecionada(Self);
  AplicaAosDesenhos(Self);
end;
