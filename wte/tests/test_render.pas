{ Prova o `we2002_render` -- a aritmetica de cor da WTE-TASK-29.

  Quatro grupos, e o terceiro e o que a secao 9 do plano chama de risco:

  1. **a palavra e os campos.** Decodificar, codificar, e o mapeamento de cada
     canal para os seus cinco bits. Erro aqui troca vermelho por azul, o que se
     ve; os outros tres erram de um degrau, o que nao se ve;
  2. **escurecer e clarear.** Um degrau por campo, o piso que impede o campo de
     dar a volta e roubar do vizinho, e o teto em 31 -- que so satura ali
     porque a expansao e `shl 3`;
  3. **a rampa.** Que ela preencha o MIOLO e nao as pontas, que o passo seja
     `Single`, e que truncar e arredondar DIVIRJAM -- se dessem sempre o mesmo,
     a escolha nao importaria e o plano teria errado ao chamar isso de risco;
  4. **a entrada de paleta.** A ordem `B, G, R` e o `$36`.

  E o grupo 5 e a terceira ponta: `WTE_TEST_RENDER_*` traz o que o
  `test_dump_render2d.py` calculou em Python para as MESMAS entradas. Duas
  implementacoes independentes da mesma aritmetica -- se concordarem, o erro
  tem de estar nas duas.

  Cada linha de saida e `OK<TAB>nome` ou `FALHA<TAB>nome<TAB>detalhe`.
  Rodado por: wte/tools/test_dump_render2d.py
}

program test_render;

{$mode objfpc}{$H+}

uses
  SysUtils, we2002_render;

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

procedure APalavraEOsCampos;
var
  c: TCanais;
begin
  { R = 31, G = 0, B = 0 -- se a ordem estiver trocada, o canal cheio aparece
    no lugar errado, e isso e o unico erro desta unidade que se ve na tela. }
  c := DecodificaCor(CodificaCor(31, 0, 0));
  Checa('o canal 0 sai dos bits 0..4',
        (c[0] = RENDER_MAXIMO) and (c[1] = 0) and (c[2] = 0),
        Format('%d,%d,%d', [c[0], c[1], c[2]]));
  c := DecodificaCor(CodificaCor(0, 31, 0));
  Checa('o canal 1 sai dos bits 5..9',
        (c[0] = 0) and (c[1] = RENDER_MAXIMO) and (c[2] = 0),
        Format('%d,%d,%d', [c[0], c[1], c[2]]));
  c := DecodificaCor(CodificaCor(0, 0, 31));
  Checa('o canal 2 sai dos bits 10..14',
        (c[0] = 0) and (c[1] = 0) and (c[2] = RENDER_MAXIMO),
        Format('%d,%d,%d', [c[0], c[1], c[2]]));

  { A expansao: 31 tem de dar 248, e nao 255. E o que o teto `$F8` do
    `aclararClick` prova do outro lado. }
  Checa('a expansao satura em 248, e nao em 255',
        (RENDER_MAXIMO = 248) and (RENDER_MAXIMO = 31 shl 3),
        Format('%d', [RENDER_MAXIMO]));

  { O bit 15 nao e canal: uma palavra com ele ligado decodifica igual. }
  Checa('o bit 15 e ignorado',
        DecodificaCor($1234)[2] = DecodificaCor($9234)[2]);
end;

procedure UmDegrauPorCampo;
var
  p: TCorBgr555;
  c: TCanais;
begin
  p := Escurece(CodificaCor(30, 20, 10));
  c := DecodificaCor(p);
  Checa('escurecer tira um de cada canal',
        (c[0] shr 3 = 29) and (c[1] shr 3 = 19) and (c[2] shr 3 = 9),
        Format('%d,%d,%d', [c[0] shr 3, c[1] shr 3, c[2] shr 3]));

  p := Clareia(CodificaCor(30, 20, 10));
  c := DecodificaCor(p);
  Checa('clarear poe um em cada canal',
        (c[0] shr 3 = 31) and (c[1] shr 3 = 21) and (c[2] shr 3 = 11),
        Format('%d,%d,%d', [c[0] shr 3, c[1] shr 3, c[2] shr 3]));

  { O PISO, e e ele que impede o estrago: sem a guarda, `0 - 1` no canal 0
    emprestaria do canal 1, e escurecer um preto viraria magenta. }
  Checa('preto escurecido continua preto', Escurece(0) = 0,
        Format('%d', [Escurece(0)]));
  p := Escurece(CodificaCor(0, 1, 0));
  c := DecodificaCor(p);
  Checa('canal zerado nao rouba do vizinho',
        (c[0] = 0) and (c[1] = 0) and (c[2] = 0),
        Format('%d,%d,%d', [c[0], c[1], c[2]]));

  { O TETO, pelo mesmo motivo do outro lado. }
  p := CodificaCor(31, 31, 31);
  Checa('branco clareado continua branco', Clareia(p) = p,
        Format('%d', [Clareia(p)]));
  p := Clareia(CodificaCor(31, 30, 31));
  c := DecodificaCor(p);
  Checa('canal cheio nao transborda para o vizinho',
        (c[0] shr 3 = 31) and (c[1] shr 3 = 31) and (c[2] shr 3 = 31),
        Format('%d,%d,%d', [c[0] shr 3, c[1] shr 3, c[2] shr 3]));

  { Os dois sao inversos enquanto nao encostam num limite. }
  p := CodificaCor(15, 15, 15);
  Checa('escurecer e clarear se desfazem no meio da faixa',
        Clareia(Escurece(p)) = p);
end;

procedure ARampa;
var
  saida: array[0 .. 31] of TCorBgr555;
  arredondada: array[0 .. 31] of TCorBgr555;
  i, distancia: Integer;
  acumulado: Single;
  diferentes: Boolean;
begin
  { O MIOLO, e nao as pontas: distancia 4 preenche tres entradas. }
  Checa('distancia 4 preenche tres entradas',
        Rampa(CodificaCor(0, 0, 0), CodificaCor(8, 0, 0), 4, saida));
  Checa('e a ultima delas NAO e a ponta final',
        (saida[2] and RENDER_MASCARA) = 6,
        Format('%d', [saida[2] and RENDER_MASCARA]));
  Checa('a primeira e um passo depois da ponta inicial',
        (saida[0] and RENDER_MASCARA) = 2,
        Format('%d', [saida[0] and RENDER_MASCARA]));

  Checa('distancia zero e recusada',
        not Rampa(0, 0, 0, saida));
  Checa('miolo que nao cabe na saida e recusado',
        not Rampa(0, 0, 100, saida));
  Checa('distancia 1 nao tem miolo, e passa sem escrever nada',
        Rampa(0, CodificaCor(31, 0, 0), 1, saida));

  { A RAMPA SOBE. Um degrau nunca desce, e ela chega perto da ponta. }
  Checa('rampa de 0 a 31 em 8 passos', Rampa(CodificaCor(0, 0, 0),
        CodificaCor(31, 0, 0), 8, saida));
  diferentes := False;
  for i := 1 to 6 do
    if (saida[i] and RENDER_MASCARA) < (saida[i - 1] and RENDER_MASCARA) then
      diferentes := True;
  Checa('a rampa nunca desce', not diferentes);
  Checa('e para um degrau antes da ponta',
        (saida[6] and RENDER_MASCARA) < 31,
        Format('%d', [saida[6] and RENDER_MASCARA]));

  { O RISCO NOMEADO: truncar e arredondar divergem. Este bloco refaz a mesma
    rampa com `Round` no lugar de `Trunc` e exige que o resultado seja OUTRO --
    se fosse o mesmo, a escolha nao importaria e nao haveria risco. }
  distancia := 5;
  Rampa(CodificaCor(0, 0, 0), CodificaCor(7, 0, 0), distancia, saida);
  acumulado := 0;
  for i := 0 to distancia - 2 do
  begin
    acumulado := acumulado + Single(7) / Single(distancia);
    arredondada[i] := TCorBgr555(Round(acumulado));
  end;
  diferentes := False;
  for i := 0 to distancia - 2 do
    if saida[i] <> arredondada[i] then
      diferentes := True;
  Checa('truncar e arredondar dao rampas DIFERENTES', diferentes,
        'se derem a mesma, o risco da secao 9 nao existe e este teste mente');
  for i := 0 to distancia - 2 do
    Checa(Format('e a diferenca no passo %d e de um degrau, no maximo', [i]),
          Abs(Integer(saida[i]) - Integer(arredondada[i])) <= 1,
          Format('%d contra %d', [saida[i], arredondada[i]]));
end;

procedure AEntradaDePaleta;
var
  e: TEntradaDePaleta;
begin
  { A ordem de escrita e `B, G, R` -- a da entrada BMP, e nao a do buffer. }
  e := EntradaDePaleta(CodificaCor(31, 0, 0));
  Checa('o vermelho vai no TERCEIRO byte escrito',
        (e[0] = 0) and (e[1] = 0) and (e[2] = RENDER_MAXIMO),
        Format('%d,%d,%d', [e[0], e[1], e[2]]));
  e := EntradaDePaleta(CodificaCor(0, 0, 31));
  Checa('e o azul no PRIMEIRO',
        (e[0] = RENDER_MAXIMO) and (e[1] = 0) and (e[2] = 0),
        Format('%d,%d,%d', [e[0], e[1], e[2]]));

  Checa('a entrada 0 mora em 0x36', OffsetDaEntrada(0) = $36,
        Format('%d', [OffsetDaEntrada(0)]));
  Checa('e o passo entre entradas e 4', OffsetDaEntrada(1)
        - OffsetDaEntrada(0) = BMP_ENTRADA_BYTES);
  { A assimetria medida: nao sao os mesmos dois numeros. }
  Checa('bandeira e uniforme nao reescrevem o mesmo tanto',
        (PALETA_BANDEIRA = 16) and (PALETA_UNIFORME = 15));
end;

{ A terceira ponta: o que o Python leu e calculou para as MESMAS entradas. }
procedure ContraOPython;
var
  esperado, obtido: string;
  saida: array[0 .. 31] of TCorBgr555;
  i, distancia: Integer;
  inicio, fim: TCorBgr555;
begin
  esperado := GetEnvironmentVariable('WTE_TEST_RENDER_RAMPA');
  if esperado = '' then
  begin
    WriteLn('PULADO'#9'rampa contra o Python'#9'sem WTE_TEST_RENDER_RAMPA');
    Exit;
  end;
  inicio := TCorBgr555(StrToIntDef(
    GetEnvironmentVariable('WTE_TEST_RENDER_INICIO'), 0));
  fim := TCorBgr555(StrToIntDef(
    GetEnvironmentVariable('WTE_TEST_RENDER_FIM'), 0));
  distancia := StrToIntDef(
    GetEnvironmentVariable('WTE_TEST_RENDER_DISTANCIA'), 0);
  Checa('a rampa do confronto roda', Rampa(inicio, fim, distancia, saida));
  obtido := '';
  for i := 0 to distancia - 2 do
  begin
    if i > 0 then
      obtido := obtido + ',';
    obtido := obtido + IntToStr(saida[i]);
  end;
  Checa('a rampa bate com a do dump_render2d.py', obtido = esperado,
        obtido + ' <> ' + esperado);
end;

begin
  APalavraEOsCampos;
  UmDegrauPorCampo;
  ARampa;
  AEntradaDePaleta;
  ContraOPython;
  WriteLn('CASOS'#9, casos);
  if falhas > 0 then
    Halt(1);
end.
