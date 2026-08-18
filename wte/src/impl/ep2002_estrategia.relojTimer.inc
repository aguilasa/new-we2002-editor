{ estrategia.relojTimer -- 0x00409ba4, 936 bytes.
  Spec: wte/re/spec/estrategia.relojTimer.md

  A animacao de troca de formacao. `Interval = 1` no `.lfm`, quatro quadros --
  o efeito e quase instantaneo, e e proposital: o original nao teleporta os
  jogadores, ele os desliza.

  SAO DOIS RAMOS, e o teste esta na PRIMEIRA instrucao: se o contador chegou a
  QUADROS_DA_ANIMACAO, este disparo e o do encaixe final e o timer se desliga;
  senao e mais um passo de interpolacao. Ler so o segundo ramo daria uma
  animacao que nunca para e nunca chega ao destino inteiro.

  NAO GRAVA NADA. O inventario dos 936 bytes alcanca `FindComponent`,
  `CurrToStr`, concatenacao de `AnsiString`, `SetLeft`/`SetTop`, o auxiliar de
  arredondamento da RTL e `TTimer::SetEnabled` -- nenhuma escritora de imagem. }
var
  i: Integer;
  bola: TShape;
  etiqueta: TLabel;
begin
  REMark('estrategia.relojTimer');

  if PassoDaAnimacao = QUADROS_DA_ANIMACAO then
  begin
    { O encaixe. Depois de quatro somas em ponto flutuante a posicao acumulada
      nao e exatamente o destino; este ramo escreve o inteiro que a formacao
      pediu, zera o contador e para o timer. Sem ele a formacao ficaria um
      pixel fora, sempre no mesmo sentido. }
    for i := BOLA_PRIMEIRA to BOLA_ULTIMA do
    begin
      bola := BolaDeNumero(i);
      etiqueta := EtiquetaDeNumero(i);
      if bola = nil then
        Continue;
      BolaEmFoco := bola;
      bola.Left := campo.Left + DestinoX[i - 1];
      bola.Top := campo.Top + DestinoY[i - 1];
      if etiqueta <> nil then
      begin
        EtiquetaEmMovimento := etiqueta;
        etiqueta.Left := bola.Left + ETIQUETA_DX;
        etiqueta.Top := bola.Top + ETIQUETA_DY;
      end;
    end;
    PassoDaAnimacao := 0;
    reloj.Enabled := False;
    Exit;
  end;

  { Um passo. Soma o delta a posicao corrente e desenha o truncado -- o
    original chama o auxiliar da RTL que poe a FPU em arredondar-para-zero,
    que e `Trunc`, nao `Round`. Meio pixel de diferenca por quadro, e sempre
    para o mesmo lado. }
  for i := BOLA_PRIMEIRA to BOLA_ULTIMA do
  begin
    bola := BolaDeNumero(i);
    if bola = nil then
      Continue;
    BolaEmFoco := bola;
    AtualX[i - 1] := AtualX[i - 1] + DeltaX[i - 1];
    AtualY[i - 1] := AtualY[i - 1] + DeltaY[i - 1];
    bola.Left := campo.Left + Trunc(AtualX[i - 1]);
    bola.Top := campo.Top + Trunc(AtualY[i - 1]);

    etiqueta := EtiquetaDeNumero(i);
    if etiqueta <> nil then
    begin
      EtiquetaEmMovimento := etiqueta;
      etiqueta.Left := bola.Left + ETIQUETA_DX;
      etiqueta.Top := bola.Top + ETIQUETA_DY;
    end;
  end;
  Inc(PassoDaAnimacao);
end;
