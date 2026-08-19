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
  ImagemInexistenteNaoExplode;
  ContaNaImagem;
  WriteLn('CASOS'#9, casos);
  if falhas > 0 then
    Halt(1);
end.
