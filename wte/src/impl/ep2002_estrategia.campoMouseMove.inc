{ estrategia.campoMouseMove -- 0x004090c8, 52 bytes.
  Spec: wte/re/spec/estrategia.campoMouseMove.md

  Sair de uma bola para o gramado apaga o destaque. Duas linhas, e sao as duas
  primeiras do `bolaMouseMove` -- o original nao as fatorou.

  ESTE ENDERECO CUSTOU UMA CORRECAO. O plano da task dava a este handler 1.404
  bytes, que e a distancia ate o proximo handler PUBLICADO; entre um e outro
  esta o `estrategia.FormCreate` (0x004090fc, 1.352 B). Somar o vizinho ao
  corpo e o modo silencioso de superestimar custo de leitura. }
begin
  REMark('estrategia.campoMouseMove');
  if BolaEmFoco <> nil then
    BolaEmFoco.Brush.Color := VERDE_APAGADO;
  if EtiquetaEmFoco <> nil then
    EtiquetaEmFoco.Font.Color := CINZA_CLARO;
end;
