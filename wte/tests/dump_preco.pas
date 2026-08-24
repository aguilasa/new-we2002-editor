{ Despeja o preco calculado de cada jogador de uma imagem -- WTE-TASK-32.

  E a metade NUMERICA da regua desta task. A outra metade e o gate de byte
  (`golden-22-precos`), e as duas medem coisas diferentes:

  - o gate compara o que o PORT grava com o que o ORACULO grava, num time;
  - este dump produz a tabela de verdade sobre TODOS os jogadores de uma
    imagem, para o `check_preco.py` confrontar com o que o oraculo gravou.

  Sem o dump, a evidencia seria "um time bate". Com ele, e "a formula bate em
  toda a populacao das duas ROMs".

    dump_preco <imagem.bin> [<primeiro time> <ultimo time>]

  Uma linha por jogador, campos separados por TAB e ordem estavel:

    time  slot  soma  posicao  preco  custo

  `soma` sai junto de proposito: quando um preco diverge, e ela que diz se o
  erro foi na soma das barras ou na formula sobre ela, e sao consertos
  diferentes.

  `custo` e o byte que ESTA na imagem, no campo condicional. Numa imagem virgem
  ele e o que o jogo trouxe de fabrica e nao tem relacao com a formula; numa
  imagem por onde o `base_teamClick` do ORACULO passou, ele e a resposta do
  oraculo -- e ai `preco = custo` e a conferencia da formula, jogador a
  jogador. Quem faz essa leitura e o `wte/tools/check_preco.py`. }
program dump_preco;

{$mode objfpc}{$H+}

uses
  SysUtils,
  we2002_types, we2002_team, we2002_player, we2002_database, we2002_preco;

const
  { Slots por time de selecao -- o elenco e contiguo depois dos sem-contrato. }
  SLOTS = 23;

var
  db: TDatabase;
  imagem: string;
  t, slot, k, t0, t1: Integer;

{ O indice do jogador `slot` do time `t` dentro de `db.players`.

  So a familia de SELECAO, que e a que o `base_teamClick` alcanca pelos dois
  combos. Clube de Master League resolve por vinculo e nao cabe num dump que
  quer ser diffavel -- a mesma decisao que o `dump_estado` tomou. }
function IndiceDeSelecao(time_, slot_: Integer): Integer;
begin
  Result := PLAYERS_NC + time_ * SLOTS + slot_;
end;

begin
  if ParamCount < 1 then
  begin
    WriteLn(StdErr, 'uso: dump_preco <imagem.bin> [<time0> <time1>]');
    Halt(2);
  end;
  imagem := ParamStr(1);
  t0 := 0;
  t1 := TEAMS_NATIONAL_ALLSTAR - 1;
  if ParamCount >= 3 then
  begin
    t0 := StrToInt(ParamStr(2));
    t1 := StrToInt(ParamStr(3));
  end;

  db.Init;
  if not db.Load(imagem, nil) then
  begin
    WriteLn(StdErr, 'ERRO: nao carregou ', imagem);
    Halt(1);
  end;

  WriteLn('time'#9'slot'#9'soma'#9'posicao'#9'preco'#9'custo');
  for t := t0 to t1 do
    for slot := 0 to SLOTS - 1 do
    begin
      k := IndiceDeSelecao(t, slot);
      if (k < 0) or (k >= Length(db.players)) then
        Continue;
      WriteLn(t, #9, slot, #9,
              SomaDasHabilidades(db.players[k]), #9,
              db.players[k].position, #9,
              PrecoDoJogador(db.players[k]), #9,
              db.players[k].cost);
    end;
end.
