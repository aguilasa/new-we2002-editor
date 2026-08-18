{ estrategia.bolaMouseDown -- 0x00408f00, 456 bytes.
  Spec: wte/re/spec/estrategia.bolaMouseDown.md

  Comeca o arrasto: guarda de onde a bola saiu, desenha em volta dela o
  retangulo da zona em que ela pode cair, e chama `BeginDrag`.

  NAO GRAVA NADA na imagem -- o inventario de chamadas dos 456 bytes so alcanca
  VCL. A tatica so vai ao disco pelo botao de gravar, que e da WTE-TASK-27. }
var
  indice: Integer;
  zona: Integer;
begin
  REMark('estrategia.bolaMouseDown');
  { So o botao esquerdo. O original testa `cl` logo na entrada e sai sem fazer
    nada para qualquer outro -- inclusive sem limpar estado. }
  if Button <> mbLeft then
    Exit;
  if not (Sender is TShape) then
    Exit;
  BolaEmFoco := TShape(Sender);
  indice := IndiceDaBola(Sender);

  { Os dois pontos que o original converte para coordenada de TELA. Ele nao os
    usa aqui: quem le e o `relojTimer`, que ainda nao foi portado. Escritos
    assim mesmo, porque deixar de escrever seria a divergencia. }
  PonteiroNaTela := ClientToScreen(Point(X, Y));
  CentroDaBolaNaTela := ClientToScreen(Point(BolaEmFoco.Left + RAIO_DA_BOLA,
                                             BolaEmFoco.Top + RAIO_DA_BOLA));

  { O retangulo da zona. `ZonaDaBola` le a formacao aplicada; sem nenhuma
    aplicada ela devolve 0 -- ver o `.aux.inc`. }
  zona := ZonaDaBola(indice);
  if (zona >= 0) and (zona < ZONAS_TOTAL) then
  begin
    rectangulo.Left := campo.Left + ZONAS[zona].x1;
    rectangulo.Top := campo.Top + ZONAS[zona].y1;
    { O `+ 1` e do original: a largura desenhada e inclusiva nas duas pontas. }
    rectangulo.Width := ZONAS[zona].x2 - ZONAS[zona].x1 + 1;
    rectangulo.Height := ZONAS[zona].y2 - ZONAS[zona].y1 + 1;
  end;

  BolaEmFoco.BeginDrag(True, 0);
  BolaEmFoco.Enabled := False;
  if EtiquetaEmFoco <> nil then
    EtiquetaEmFoco.Visible := False;
  rectangulo.Visible := True;
end;
