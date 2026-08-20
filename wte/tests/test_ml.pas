{ Prova o `we2002_ml` -- a conta de blocos livres de Master League da
  WTE-TASK-33.

  Tres invariantes que nao precisam de imagem, mais a conta sobre a imagem
  quando houver uma. As tres primeiras sao o que erra em silencio: tabela que
  deixou de fechar com o `PLAYERS_NC`, prefixo que anda para tras, e o teto do
  vetor de ocupacao dimensionado com folga errada.

  A quarta e a que vale: `WTE_TEST_IMAGEM` diz a copia e `WTE_TEST_LIVRES` diz
  o numero que o `conta_ml.py` obteve da MESMA copia. Sao duas implementacoes
  independentes da mesma rotina -- se concordarem, o erro tem de estar nas
  duas.

  Cada linha de saida e `OK<TAB>nome` ou `FALHA<TAB>nome<TAB>detalhe`.
  Rodado por: wte/tools/test_conta_ml.py
}

program test_ml;

{$mode objfpc}{$H+}

uses
  SysUtils, we2002_ml;

var
  falhas: LongInt = 0;
  casos: LongInt = 0;

procedure Checa(const nome: string; ok: Boolean; const detalhe: string = '');
begin
  Inc(casos);
  if ok then
    WriteLn('OK'#9, nome)
  else
  begin
    WriteLn('FALHA'#9, nome, #9, detalhe);
    Inc(falhas);
  end;
end;

procedure TabelaFecha;
var
  t, soma: Integer;
begin
  soma := 0;
  for t := Low(ML_NC_POR_TIME) to High(ML_NC_POR_TIME) do
    Inc(soma, ML_NC_POR_TIME[t]);
  Checa('tabela soma o total de blocos', soma = ML_BLOCOS_TOTAL,
        Format('soma=%d total=%d', [soma, ML_BLOCOS_TOTAL]));
  Checa('a tabela tem 120 times',
        High(ML_NC_POR_TIME) - Low(ML_NC_POR_TIME) + 1 = 120,
        Format('%d', [High(ML_NC_POR_TIME) - Low(ML_NC_POR_TIME) + 1]));
end;

procedure PrefixoEMonotono;
var
  t, ant, cur: Integer;
  ok: Boolean;
begin
  ok := True;
  ant := -1;
  for t := 0 to High(ML_NC_POR_TIME) + 1 do
  begin
    cur := MlPrefixoDoTime(t);
    if cur < ant then
      ok := False;
    ant := cur;
  end;
  Checa('prefixo nao anda para tras', ok);
  Checa('prefixo do time 0 e zero', MlPrefixoDoTime(0) = 0,
        Format('%d', [MlPrefixoDoTime(0)]));
  Checa('prefixo depois do ultimo time e o total',
        MlPrefixoDoTime(High(ML_NC_POR_TIME) + 1) = ML_BLOCOS_TOTAL,
        Format('%d', [MlPrefixoDoTime(High(ML_NC_POR_TIME) + 1)]));
end;

procedure TetoDoVetor;
begin
  { O maior indice que a formula alcanca com `b1` no maximo de um byte. Se o
    teto encolher, o `Continue` de guarda passa a descartar par valido e a
    conta sai alta sem nada reclamar. }
  Checa('o teto do vetor cobre o maior indice possivel',
        ML_INDICE_MAX >= MlPrefixoDoTime(High(ML_NC_POR_TIME) + 1) + 255 - 23,
        Format('%d', [ML_INDICE_MAX]));
end;

procedure IdaEVoltaDoIndiceLinear;
var
  t, slot, indice, vt, vs, primeiro_zero: Integer;
  ok_todos, ok_zero: Boolean;
  detalhe: string;
begin
  { A `0x0040427c` e o INVERSO da `0x0040423c`, e inverso conferido num ponto
    so nao e inverso conferido. O golden-11-descarte-ml exercita um bloco --
    o 350 --, entao a ida e volta de todos os 462 mora aqui. }
  ok_todos := True;
  detalhe := '';
  for t := Low(ML_NC_POR_TIME) to High(ML_NC_POR_TIME) do
    for slot := ML_SLOT_MIN to ML_SLOT_MIN + Integer(ML_NC_POR_TIME[t]) - 1 do
    begin
      indice := IndiceDoBlocoMl(t, slot);
      ParDoIndiceLinearMl(indice, vt, vs);
      if (vt <> t) or (vs <> slot) then
      begin
        if ok_todos then
          detalhe := Format('(%d,%d) -> %d -> (%d,%d)',
                            [t, slot, indice, vt, vs]);
        ok_todos := False;
      end;
    end;
  Checa('ida e volta fecha em todo bloco valido', ok_todos, detalhe);

  { Fronteira: o primeiro slot de um time e o `ML_SLOT_MIN` cru, e o ultimo e
    onde o prefixo do time seguinte comeca. Sao os dois pontos em que um erro
    de um no `+ ML_SLOT_MIN` aparece. }
  t := -1;
  for slot := Low(ML_NC_POR_TIME) to High(ML_NC_POR_TIME) do
    if ML_NC_POR_TIME[slot] > 1 then
    begin
      t := slot;
      Break;
    end;
  if t < 0 then
    Checa('achou time com mais de um NC', False)
  else
  begin
    ParDoIndiceLinearMl(IndiceDoBlocoMl(t, ML_SLOT_MIN), vt, vs);
    Checa('o primeiro slot de um time volta igual',
          (vt = t) and (vs = ML_SLOT_MIN), Format('(%d,%d)', [vt, vs]));
    slot := ML_SLOT_MIN + Integer(ML_NC_POR_TIME[t]) - 1;
    ParDoIndiceLinearMl(IndiceDoBlocoMl(t, slot), vt, vs);
    Checa('o ultimo slot de um time volta igual',
          (vt = t) and (vs = slot), Format('(%d,%d) esperado (%d,%d)',
                                           [vt, vs, t, slot]));
  end;

  { Time sem NC nenhum nao pode sair do inverso para indice algum: ele nao tem
    bloco. E a condicao que faz o ORIGINAL escrever fora do vetor quando um
    vinculo o endereca -- ver `wte/re/ml-slots.md`. }
  primeiro_zero := -1;
  for t := Low(ML_NC_POR_TIME) to High(ML_NC_POR_TIME) do
    if ML_NC_POR_TIME[t] = 0 then
    begin
      primeiro_zero := t;
      Break;
    end;
  ok_zero := True;
  detalhe := 'nenhum time com zero NC na tabela';
  if primeiro_zero >= 0 then
  begin
    detalhe := '';
    for indice := 0 to ML_BLOCOS_TOTAL - 1 do
    begin
      ParDoIndiceLinearMl(indice, vt, vs);
      if vt = primeiro_zero then
      begin
        if ok_zero then
          detalhe := Format('indice %d devolveu o time %d, que tem 0 NC',
                            [indice, primeiro_zero]);
        ok_zero := False;
      end;
    end;
  end;
  Checa('time sem NC nao e devolvido por indice nenhum', ok_zero, detalhe);
end;

procedure ForaDaFaixaSaiMenosUm;
var
  vt, vs: Integer;
begin
  ParDoIndiceLinearMl(-1, vt, vs);
  Checa('indice negativo sai (-1,-1)', (vt = -1) and (vs = -1),
        Format('(%d,%d)', [vt, vs]));
  ParDoIndiceLinearMl(ML_BLOCOS_TOTAL, vt, vs);
  Checa('indice igual ao total sai (-1,-1)', (vt = -1) and (vs = -1),
        Format('(%d,%d)', [vt, vs]));
  Checa('IndiceDoBlocoMl recusa time alem da tabela',
        IndiceDoBlocoMl(High(ML_NC_POR_TIME) + 1, ML_SLOT_MIN) = -1,
        Format('%d', [IndiceDoBlocoMl(High(ML_NC_POR_TIME) + 1,
                                      ML_SLOT_MIN)]));
end;

procedure AlocadorDeBloco;
var
  i: Integer;
begin
  { `PrimeiroBlocoLivreMl` le o `OcupacaoMl`, que e global e vivo. Aqui ele e
    plantado a mao, porque o caminho que interessa -- vetor cheio -- nao
    acontece com nenhuma das duas imagens. }
  for i := Low(OcupacaoMl) to High(OcupacaoMl) do
    OcupacaoMl[i] := 1;
  Checa('vetor cheio nao tem bloco livre', PrimeiroBlocoLivreMl = -1,
        Format('%d', [PrimeiroBlocoLivreMl]));

  OcupacaoMl[350] := 0;
  Checa('o furo e o primeiro bloco livre', PrimeiroBlocoLivreMl = 350,
        Format('%d', [PrimeiroBlocoLivreMl]));

  OcupacaoMl[0] := 0;
  Checa('furo em 0 devolve 0', PrimeiroBlocoLivreMl = 0,
        Format('%d', [PrimeiroBlocoLivreMl]));

  { O ultimo bloco: fora dele o laco pararia em ML_BLOCOS_TOTAL-1 sem olhar. }
  for i := Low(OcupacaoMl) to High(OcupacaoMl) do
    OcupacaoMl[i] := 1;
  OcupacaoMl[ML_BLOCOS_TOTAL - 1] := 0;
  Checa('o ultimo bloco ainda e alcancado',
        PrimeiroBlocoLivreMl = ML_BLOCOS_TOTAL - 1,
        Format('%d', [PrimeiroBlocoLivreMl]));

  { Bloco livre ALEM do total nao conta: a folga do vetor existe para o indice
    fora da faixa ser contado sem atingir vizinho, nao para ser alocado. }
  for i := Low(OcupacaoMl) to High(OcupacaoMl) do
    OcupacaoMl[i] := 1;
  OcupacaoMl[ML_BLOCOS_TOTAL] := 0;
  Checa('bloco livre alem do total nao e alocado',
        PrimeiroBlocoLivreMl = -1, Format('%d', [PrimeiroBlocoLivreMl]));

  for i := Low(OcupacaoMl) to High(OcupacaoMl) do
    OcupacaoMl[i] := 0;
end;

procedure ContaNaImagem;
var
  imagem, esperado_s: string;
  esperado, fora: Integer;
  livres: Word;
begin
  imagem := GetEnvironmentVariable('WTE_TEST_IMAGEM');
  esperado_s := GetEnvironmentVariable('WTE_TEST_LIVRES');
  if (imagem = '') or (esperado_s = '') then
  begin
    WriteLn('PULADO'#9'conta na imagem'#9 +
            'sem WTE_TEST_IMAGEM/WTE_TEST_LIVRES');
    Exit;
  end;
  esperado := StrToIntDef(esperado_s, -1);
  livres := ContaBlocosLivresDeMl(imagem, fora);
  Checa('a conta bate com a do conta_ml.py', livres = esperado,
        Format('pascal=%d python=%d fora=%d', [livres, esperado, fora]));
end;

procedure ImagemInexistenteNaoExplode;
var
  fora: Integer;
begin
  Checa('imagem inexistente devolve o total',
        ContaBlocosLivresDeMl('/nao/existe/imagem.bin', fora)
          = ML_BLOCOS_TOTAL);
end;

begin
  TabelaFecha;
  PrefixoEMonotono;
  TetoDoVetor;
  IdaEVoltaDoIndiceLinear;
  ForaDaFaixaSaiMenosUm;
  AlocadorDeBloco;
  ImagemInexistenteNaoExplode;
  ContaNaImagem;
  WriteLn('CASOS'#9, casos);
  if falhas > 0 then
    Halt(1);
end.
