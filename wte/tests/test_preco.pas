{ Testes da formula de preco -- WTE-TASK-32.

  O gate de byte (`golden-22-precos`) e a tabela de verdade (`check_preco.py`)
  medem a formula contra o ORACULO, e sao a evidencia principal. Estes testes
  medem o que aquela evidencia NAO alcanca, e a task nomeia os tres casos em
  "onde a tabela pode enganar":

  1. **saturacao** -- a amostra medida vai de soma 36 a 77, porque jogador real
     de WE2002 vive nessa faixa. Fora dela a formula pode fazer qualquer coisa,
     e faz: o `s*s*s*s` e de 32 BITS no original e TRANSBORDA. Aqui isso e
     testado de proposito, com o valor exato onde vira.
  2. **arredondamento** -- divisao inteira truncando para ZERO, nao para baixo.
     So aparece com soma negativa, que so o transbordo produz.
  3. **termo cruzado** -- nao ha: a formula toma UM numero. O termo cruzado da
     feature esta noutro lugar, no `x 5 div 3` do goleiro, e ele e testado
     junto com a ordem em que se aplica.

  Roda sem imagem, sem Wine e sem `:98`. }
program test_preco;

{$mode objfpc}{$H+}

uses
  SysUtils, we2002_player, we2002_preco;

var
  falhas: Integer = 0;
  total: Integer = 0;

procedure Confere(const rotulo: string; obtido, esperado: LongInt);
begin
  Inc(total);
  if obtido <> esperado then
  begin
    Inc(falhas);
    WriteLn(StdErr, 'FALHOU ', rotulo, ': obtido ', obtido,
            ', esperado ', esperado);
  end;
end;

{ A formula em Int64, para mostrar ONDE ela diverge da de 32 bits. }
function PrecoEmInt64(soma: LongInt): Int64;
var
  s: Int64;
begin
  s := soma;
  Result := (s*s*s*s div DIV_QUARTA) + (s*s*s div DIV_CUBO)
          + (s*s div DIV_QUADRADO) + (s div DIV_LINEAR) + TERMO_FIXO;
end;

var
  p: TPlayer;
  s, primeiro: LongInt;

begin
  { ---- os valores que o oraculo respondeu, conferidos a mao ---- }
  Confere('soma 38', PrecoDaSoma(38), 13);
  Confere('soma 36', PrecoDaSoma(36), 12);
  Confere('soma 77', PrecoDaSoma(77), 46);

  { ---- o goleiro, e a ORDEM em que o fator entra ---- }
  { 13 * 5 div 3 = 21, e nao 13 + 5 nem (13 div 3) * 5. }
  Confere('goleiro soma 38', (PrecoDaSoma(38) * 5) div 3, 21);
  Confere('goleiro soma 36', (PrecoDaSoma(36) * 5) div 3, 20);

  p.Init;
  p.attack := 12 + 38;   { uma habilidade sozinha ja da soma 38 }
  p.position := POSICAO_GOLEIRO;
  Confere('PrecoDoJogador goleiro', PrecoDoJogador(p), 21);
  p.position := 1;
  Confere('PrecoDoJogador linha', PrecoDoJogador(p), 13);

  { ---- o piso da barra: atributo abaixo de 12 nao conta negativo ---- }
  p.Init;
  p.attack := 5;         { 5 - 12 = -7, e a barra mostra 0 }
  p.position := 1;
  Confere('atributo abaixo do piso', SomaDasHabilidades(p), 0);
  Confere('soma zero', PrecoDaSoma(0), 5);

  { ---- SATURACAO: onde o s^4 de 32 bits transborda ---- }
  {
    2^31 = 2147483648, e 215^4 = 2136750625 cabe; 216^4 = 2176782336 nao.
    A partir dai o original le a metade baixa COM SINAL, e o termo da quarta
    potencia vira negativo -- o preco DESPENCA em vez de crescer.
  }
  primeiro := 0;
  for s := 200 to 260 do
    if (PrecoDaSoma(s) <> PrecoEmInt64(s)) and (primeiro = 0) then
      primeiro := s;
  Confere('primeira soma em que 32 bits diverge de 64', primeiro, 216);
  { E a divergencia nao e de um: a de 64 bits cresce, a de 32 cai. }
  if not (PrecoDaSoma(216) < PrecoDaSoma(215)) then
  begin
    Inc(falhas);
    WriteLn(StdErr, 'FALHOU transbordo: o preco de 216 devia CAIR ',
            'abaixo do de 215 (32 bits), e deu ', PrecoDaSoma(216));
  end;
  Inc(total);

  { ---- ARREDONDAMENTO: truncar para ZERO, nao para baixo ---- }
  {
    So aparece com soma negativa, e soma negativa so vem do transbordo acima.
    `-7 div 2` e -3 em Pascal e no `idiv`; `Floor` daria -4.
  }
  Confere('div trunca para zero', -7 div 2, -3);

  if falhas = 0 then
    WriteLn('test_preco: ', total, ' conferencias, todas passaram')
  else
  begin
    WriteLn(StdErr, 'test_preco: ', falhas, ' de ', total, ' FALHARAM');
    Halt(1);
  end;
end.
