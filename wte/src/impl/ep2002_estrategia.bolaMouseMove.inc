{ estrategia.bolaMouseMove -- 0x00408e0c, 244 bytes.
  Spec: wte/re/spec/estrategia.bolaMouseMove.md

  Passar o mouse por uma bola a destaca e apaga a anterior. NAO GRAVA NADA e
  nao mexe no modelo: e so cor.

  DIVERGENCIA DELIBERADA (WTE-TASK-35): o original desreferencia `BolaEmFoco` e
  `EtiquetaEmFoco` sem conferir. No `.exe` isso nunca estoura porque o
  `relojTimer` roda antes e os semeia; aqui o timer ainda nao foi portado, e sem
  a guarda o primeiro movimento do mouse derrubaria o formulario. }
begin
  REMark('estrategia.bolaMouseMove');
  if not (Sender is TShape) then
    Exit;
  if Sender <> BolaEmFoco then
  begin
    if BolaEmFoco <> nil then
      BolaEmFoco.Brush.Color := VERDE_APAGADO;
    if EtiquetaEmFoco <> nil then
      EtiquetaEmFoco.Font.Color := CINZA_CLARO;
  end;
  BolaEmFoco := TShape(Sender);
  BolaEmFoco.Brush.Color := VERDE_VIVO;
  { O rotulo e achado por NOME, com o mesmo indice da bola. O literal do
    original e `etiqjug`, nao `etiqpos`: os dois prefixos existem no
    formulario, e o `estrategia.FormCreate` usa o outro. }
  EtiquetaEmFoco := nil;
  if FindComponent('etiqjug' + Copy(BolaEmFoco.Name, 5, 2)) is TLabel then
    EtiquetaEmFoco := TLabel(FindComponent('etiqjug'
                                           + Copy(BolaEmFoco.Name, 5, 2)));
  if EtiquetaEmFoco <> nil then
    EtiquetaEmFoco.Font.Color := BRANCO;
end;
