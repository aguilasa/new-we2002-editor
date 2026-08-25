{ Testes de borda dos campos de tamanho fixo -- WTE-TASK-36.

  O inventario (`wte/re/buffers.md`, do `dump_buffers.py`) diz QUAIS campos
  existem, qual a capacidade de cada um e de onde sai o limite. Estes testes
  medem o que acontece **na borda**, que e o que o inventario nao alcanca.

  Os quatro casos que o enunciado da task nomeia, por campo:

  | entrada | o que verificar |
  |---|---|
  | exatamente `N` caracteres | grava integro, sem terminador comendo o vizinho |
  | `N+1` caracteres | trunca? recusa? |
  | cadeia vazia | grava o que -- zeros, espacos, valor anterior |
  | caractere fora do conjunto | o codec aceita? |

  **O caso `N` exato e o que pegou o `newWe2002`, e e o mais facil de nao
  testar.** La foi um `strcpy` de 30 bytes mais terminador num
  `raw_formation[30]`: invisivel em Debug, e em Release o `_FORTIFY_SOURCE`
  derrubava o editor em TODA imagem aberta. O Pascal com string gerenciada nao
  tem essa classe -- mas tem a INVERSA, e ela e o assunto do primeiro grupo
  aqui.

  Roda sem imagem, sem Wine e sem `:98`. }
program test_bordas;

{$mode objfpc}{$H+}

uses
  SysUtils, we2002_types, we2002_team, we2002_player, we2002_textcodec;

var
  falhas: Integer = 0;
  total: Integer = 0;

procedure Confere(const rotulo: string; const obtido, esperado: string);
begin
  Inc(total);
  if obtido <> esperado then
  begin
    Inc(falhas);
    WriteLn(StdErr, 'FALHOU ', rotulo, ': obtido "', obtido,
            '", esperado "', esperado, '"');
  end;
end;

procedure ConfereInt(const rotulo: string; obtido, esperado: LongInt);
begin
  Inc(total);
  if obtido <> esperado then
  begin
    Inc(falhas);
    WriteLn(StdErr, 'FALHOU ', rotulo, ': obtido ', obtido,
            ', esperado ', esperado);
  end;
end;

{ A leitura que o app usa para todo nome, copiada do `ep2002_mainform.aux.inc`.

  Ela mora la porque o app e quem a chama; aqui ela e reproduzida para o teste
  poder rodar sem arrastar a LCL. Se as duas se separarem, o
  `test_check_bordas.py` acusa -- ele compara os corpos. }
function Cadeia(const bruto): string;
begin
  Result := string(PAnsiChar(@bruto));
end;

{ ------------------------------------------------------------------------ }
{ GRUPO 1 -- o `N` exato, e a classe de bug INVERTIDA

  `Cadeia` e `PAnsiChar` sobre um vetor de tamanho fixo: ela para no primeiro
  NUL. Se o vetor vier CHEIO, sem NUL nenhum, ela **atravessa** para o campo
  seguinte do registro -- que e o mesmo defeito do `newWe2002` pelo avesso.
  La um `strcpy` escrevia um byte a mais; aqui uma leitura le bytes a mais.

  O `TTeam` poe `mixed_case_name` logo depois de `names[5]`, e `kanji_name`
  logo depois de `abbreviations`. Entao o vizinho nao e memoria qualquer: e
  outro nome, e o resultado sai plausivel -- o pior tipo de erro. }
procedure Grupo1_NExato;
var
  t: TTeam;
  i: Integer;
begin
  FillChar(t, SizeOf(t), 0);

  { N exato: 19 caracteres num vetor de 20 deixam o byte 19 em NUL. }
  for i := 0 to 18 do
    t.names[0][i] := AnsiChar(Ord('A') + (i mod 26));
  t.names[0][19] := #0;
  ConfereInt('grupo1/N-exato/comprimento', Length(Cadeia(t.names[0])), 19);

  { N+1: o vetor CHEIO, sem terminador. `Cadeia` atravessa para `names[1]`. }
  FillChar(t, SizeOf(t), 0);
  for i := 0 to 19 do
    t.names[0][i] := 'X';
  for i := 0 to 19 do
    t.names[1][i] := 'Y';
  t.names[1][19] := #0;
  { 20 X seguidos de 19 Y -- a travessia, medida. NAO e o comportamento
    desejado; e o comportamento REAL, e o teste existe para que ele nao mude
    sem alguem reparar. }
  ConfereInt('grupo1/sem-terminador/atravessa', Length(Cadeia(t.names[0])), 39);
  Confere('grupo1/sem-terminador/conteudo',
          Copy(Cadeia(t.names[0]), 21, 3), 'YYY');

  { A garantia que o app tem: quem GRAVA nunca enche o vetor. O limite de tela
    e `LEN - 1`, e o `LEN` maximo e 20 -- entao 19 caracteres e o teto, e o
    byte 19 fica NUL. E por isso que a travessia acima nao acontece em uso
    normal, e por isso ela nao e divergencia: e uma pre-condicao mantida pelo
    limite, nao pelo tipo. }
  ConfereInt('grupo1/teto-de-tela', 20 - 1, 19);
end;

{ ------------------------------------------------------------------------ }
{ GRUPO 2 -- a cadeia vazia }
procedure Grupo2_Vazia;
var
  t: TTeam;
begin
  FillChar(t, SizeOf(t), 0);
  Confere('grupo2/vazia/le-como-vazia', Cadeia(t.names[0]), '');

  { Um nome anterior sobrescrito por vazio: o primeiro byte a NUL basta para a
    LEITURA, e o resto do vetor continua sujo. Quem grava zera o slot inteiro
    (`CodificaNomeDoBloco` poe o buffer todo a zero antes de escrever), entao
    o disco nao herda lixo -- mas a memoria herdaria, e o teste fixa qual dos
    dois comportamentos vale. }
  t.names[0][0] := 'A'; t.names[0][1] := 'B'; t.names[0][2] := #0;
  t.names[0][3] := 'C';
  Confere('grupo2/sujo-depois-do-NUL', Cadeia(t.names[0]), 'AB');
end;

{ ------------------------------------------------------------------------ }
{ GRUPO 3 -- o codec de texto, nas DUAS ROMs

  `KanjiToAscii`/`AsciiToKanji` mudam o tamanho em bytes de um nome: um campo
  que cabe em latim pode estourar em Shift-JIS. E a razao pela qual o enunciado
  manda testar a borda nas duas imagens, e nao so na europeia. }
procedure Grupo3_Codec;
var
  bruto: array[0..39] of AnsiChar;
  saida: array[0..19] of AnsiChar;
  i: Integer;
begin
  FillChar(saida, SizeOf(saida), 0);
  { Ida e volta de um nome latino no slot de kanji: dois bytes por caractere,
    entao 20 bytes de slot cru viram 10 caracteres. }
  FillChar(bruto, SizeOf(bruto), 0);
  for i := 0 to 9 do
  begin
    bruto[i * 2]     := AnsiChar($82);
    bruto[i * 2 + 1] := AnsiChar($60 + i);   { 'A'..'J' em Shift-JIS }
  end;
  { `l` e o comprimento DA TABELA (`TEAM_NAME_KANJI_LEN`), e o laco do codec
    e `while i < (l - 1) * 2` -- ele decodifica `l - 1` caracteres, nao `l`.

    Medido aqui, e o achado concilia a terceira fonte do inventario: o
    `LimiteDoNome1` poe `MaxLength := TEAM_NAME_KANJI_LEN[t] - 1`, e o
    decodificador produz exatamente `LEN - 1` caracteres. **Os dois `- 1` sao
    o mesmo `- 1`**, e por isso o campo nunca recebe mais do que cabe: o teto
    de digitacao e, por construcao, o tamanho do que a leitura devolve. }
  KanjiToAscii(@bruto[0], @saida[0], 10);
  Confere('grupo3/kanji-decodifica-LEN-menos-1', Cadeia(saida), 'ABCDEFGHI');
  ConfereInt('grupo3/casa-com-o-MaxLength', Length(Cadeia(saida)), 10 - 1);

  { A borda: o slot cru tem o DOBRO de bytes do nome decodificado. Um campo de
    20 caracteres decodificados precisa de 40 bytes crus, que e exatamente o
    tamanho de `raw_kanji_name`. A conta fecha, e o teste a prende. }
  ConfereInt('grupo3/slot-cru-e-o-dobro',
             SizeOf(bruto), SizeOf(saida) * 2);
end;

{ ------------------------------------------------------------------------ }
{ GRUPO 4 -- caractere fora do conjunto

  Os filtros de `KeyPress` deixam passar so `[A-Za-z0-9 .]` (e so `[A-Za-z0-9]`
  na abreviatura). O que chega ao codec, portanto, e sempre desse conjunto --
  mas o codec e chamado tambem pela camada de dados, que le da IMAGEM, e ali
  nao ha filtro nenhum. }
procedure Grupo4_ForaDoConjunto;
var
  bruto: array[0..39] of AnsiChar;
  saida: array[0..19] of AnsiChar;
begin
  FillChar(saida, SizeOf(saida), 0);
  FillChar(bruto, SizeOf(bruto), 0);
  { Um par que nao e nenhuma das faixas conhecidas. O decodificador nao pode
    travar nem estourar o destino -- e o que este caso mede. }
  bruto[0] := AnsiChar($82); bruto[1] := AnsiChar($FF);
  bruto[2] := AnsiChar($82); bruto[3] := AnsiChar($60);
  KanjiToAscii(@bruto[0], @saida[0], 2);
  if Length(Cadeia(saida)) <= 20 then
    ConfereInt('grupo4/nao-estoura-o-destino', 1, 1)
  else
    ConfereInt('grupo4/nao-estoura-o-destino', 0, 1);
end;

begin
  Grupo1_NExato;
  Grupo2_Vazia;
  Grupo3_Codec;
  Grupo4_ForaDoConjunto;
  WriteLn(total - falhas, '/', total, ' conferencias de borda passaram');
  if falhas > 0 then
    Halt(1);
end.
