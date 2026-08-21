{ ficha_color.barra2Change -- 0x00406384, 44 bytes.
  Spec: wte/re/spec/ficha_color.barra2Change.md

  A trilha do FIM da faixa, espelho exato do `barra1Change`: aqui quem cede e
  o `barra2`, subindo para um a mais que o inicio. Ver a nota de la. }
begin
  REMark('ficha_color.barra2Change');
  if barra1.Position >= barra2.Position then
    barra2.Position := barra1.Position + 1;
  AtualizaFaixa(Self);
end;
