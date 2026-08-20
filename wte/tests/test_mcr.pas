{ Prova o `we2002_mcr` -- o leitor de memory card da WTE-TASK-28.

  Tres invariantes que nao precisam de cartao, mais a leitura de um cartao de
  verdade quando houver um. As tres primeiras sao o que erra em silencio:
  arquivo que nao e cartao aceito como se fosse, aritmetica de 5 bits com a
  fronteira de byte errada, e registro dimensionado por conta que nao fecha.

  A quarta e a que vale: `WTE_TEST_MCR` diz o cartao e as outras variaveis
  dizem o que o `dump_mcr.py` leu do MESMO arquivo. Sao duas implementacoes
  independentes do mesmo layout -- se concordarem, o erro tem de estar nas
  duas.

  Cada linha de saida e `OK<TAB>nome` ou `FALHA<TAB>nome<TAB>detalhe`.
  Rodado por: wte/tools/test_dump_mcr.py
}

program test_mcr;

{$mode objfpc}{$H+}

uses
  SysUtils, we2002_mcr;

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

function Hex(const dados: array of Byte; n: Integer): string;
var
  i: Integer;
begin
  Result := '';
  for i := 0 to n - 1 do
    Result := Result + LowerCase(IntToHex(dados[i], 2));
end;

procedure OConteinerFecha;
begin
  Checa('o cartao tem 16 blocos', CARTAO_BYTES = 16 * CARTAO_BLOCO,
        Format('%d / %d', [CARTAO_BYTES, CARTAO_BLOCO]));
  Checa('os cinco cobradores nao sao crescentes',
        (MCR_COBRADORES[0] > MCR_COBRADORES[1])
        and (MCR_COBRADORES[3] < MCR_COBRADORES[4]));
  Checa('o registro do jogador cabe no passo',
        MCR_ATRIBUTO_BYTES + MCR_NOME_BYTES <= MCR_JOGADOR_PASSO,
        Format('%d + %d > %d', [MCR_ATRIBUTO_BYTES, MCR_NOME_BYTES,
                                MCR_JOGADOR_PASSO]));
end;

procedure ArquivoQueNaoECartao;
var
  c: TCartaoDeMemoria;
begin
  Checa('cartao inexistente devolve False',
        not LeCartaoDeMemoria('/nao/existe/cartao.mcr', c));
  Checa('cartao inexistente declara zero blocos',
        BlocosDeclarados('/nao/existe/cartao.mcr') = 0);
end;

procedure AAritmeticaDeCincoBits;
var
  c: TCartaoDeMemoria;
  j, esperado: Integer;
  ok: Boolean;
begin
  { Planta 0 em todos os 16 bytes: todo dorsal tem de sair 1, que e o `+1`. }
  FillChar(c, SizeOf(c), 0);
  ok := True;
  for j := 0 to JOGADORES_NO_CARTAO - 1 do
    if NumeroDoCartao(c, j) <> 1 then
      ok := False;
  Checa('buffer zerado da dorsal 1 em todos os 23', ok);

  { Planta 0xFF: todo dorsal tem de saturar em 32 -- cinco bits mais o `+1`. }
  FillChar(c.numeros, SizeOf(c.numeros), $FF);
  ok := True;
  for j := 0 to JOGADORES_NO_CARTAO - 1 do
    if NumeroDoCartao(c, j) <> 32 then
      ok := False;
  Checa('buffer com 0xFF satura em 32 nos 23', ok);

  { O sexto de cada grupo comeca no bit 1 do quarto byte e NAO atravessa para
    o grupo seguinte: e o que os 2 bits perdidos por grupo garantem. Planta o
    grupo 0 com o padrao que poe 31 no slot 5 e zero nos outros. }
  FillChar(c, SizeOf(c), 0);
  c.numeros[3] := $3E;                 { bits 1..5 do quarto byte }
  esperado := 32;
  Checa('o sexto do grupo le do bit 1 do quarto byte',
        NumeroDoCartao(c, 5) = esperado,
        Format('%d', [NumeroDoCartao(c, 5)]));
  Checa('e nao vaza para o grupo seguinte', NumeroDoCartao(c, 6) = 1,
        Format('%d', [NumeroDoCartao(c, 6)]));

  Checa('indice fora da faixa devolve zero',
        (NumeroDoCartao(c, -1) = 0) and (NumeroDoCartao(c, 23) = 0));
end;

procedure LeUmCartaoDeVerdade;
var
  caminho, form_esperada, cob_esperados, dorsais_esperados, blocos_s: string;
  c: TCartaoDeMemoria;
  i: Integer;
  dorsais: string;
begin
  caminho := GetEnvironmentVariable('WTE_TEST_MCR');
  form_esperada := GetEnvironmentVariable('WTE_TEST_MCR_FORMACAO');
  cob_esperados := GetEnvironmentVariable('WTE_TEST_MCR_COBRADORES');
  dorsais_esperados := GetEnvironmentVariable('WTE_TEST_MCR_DORSAIS');
  blocos_s := GetEnvironmentVariable('WTE_TEST_MCR_BLOCOS');
  if (caminho = '') or (form_esperada = '') then
  begin
    WriteLn('PULADO'#9'leitura de cartao'#9 + 'sem WTE_TEST_MCR');
    Exit;
  end;
  Checa('o cartao abre', LeCartaoDeMemoria(caminho, c));
  Checa('a formacao bate com a do dump_mcr.py',
        Hex(c.formacao, FORMACAO_BYTES) = form_esperada,
        Hex(c.formacao, FORMACAO_BYTES) + ' <> ' + form_esperada);
  Checa('os cobradores batem', Hex(c.cobradores, COBRADORES_BYTES)
        = cob_esperados,
        Hex(c.cobradores, COBRADORES_BYTES) + ' <> ' + cob_esperados);
  dorsais := '';
  for i := 0 to JOGADORES_NO_CARTAO - 1 do
  begin
    if i > 0 then
      dorsais := dorsais + ',';
    dorsais := dorsais + IntToStr(NumeroDoCartao(c, i));
  end;
  Checa('os 23 dorsais batem', dorsais = dorsais_esperados,
        dorsais + ' <> ' + dorsais_esperados);
  Checa('o diretorio declara o mesmo numero de blocos',
        IntToStr(BlocosDeclarados(caminho)) = blocos_s,
        Format('%d <> %s', [BlocosDeclarados(caminho), blocos_s]));
end;

begin
  OConteinerFecha;
  ArquivoQueNaoECartao;
  AAritmeticaDeCincoBits;
  LeUmCartaoDeVerdade;
  WriteLn('CASOS'#9, casos);
  if falhas > 0 then
    Halt(1);
end.
