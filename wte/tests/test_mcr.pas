{ Prova o `we2002_mcr` -- o leitor de memory card da WTE-TASK-28.

  Tres invariantes que nao precisam de cartao, mais a leitura de um cartao de
  verdade quando houver um. As tres primeiras sao o que erra em silencio:
  arquivo que nao e cartao aceito como se fosse, aritmetica de 5 bits com a
  fronteira de byte errada, e registro dimensionado por conta que nao fecha.

  A quarta e a que vale: `WTE_TEST_MCR` diz o cartao e as outras variaveis
  dizem o que o `dump_mcr.py` leu do MESMO arquivo. Sao duas implementacoes
  independentes do mesmo layout -- se concordarem, o erro tem de estar nas
  duas.

  DOIS DOS TRES CASOS ESPECIAIS DO README moram aqui, sobre cartao sintetico
  -- capitao e cobradores, e espaco no nome. O terceiro, o "goleiro da Eire",
  nao e do leitor: ele vive no carimbo `+0x16 := 0xFF` que a `0x0040478c` poe
  no buffer, e por isso e conferido pelo `--check` do `dump_mcr.py` (o `.text`
  contra o Pascal) e medido pelo gate `golden-13-roundtrip`, que importa no
  time 0. Ver a secao dos casos especiais em `wte/re/mcr.md`.

  Cada linha de saida e `OK<TAB>nome` ou `FALHA<TAB>nome<TAB>detalhe`.
  Rodado por: wte/tools/test_dump_mcr.py
}

program test_mcr;

{$mode objfpc}{$H+}

uses
  SysUtils, Classes, we2002_mcr;

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

{ Um cartao sintetico: `MC`, o resto zerado, e o que o caso plantar. }
function CartaoSintetico(out caminho: string): TFileStream;
begin
  caminho := GetTempFileName('', 'wtemcr');
  Result := TFileStream.Create(caminho, fmCreate);
  Result.Size := CARTAO_BYTES;
  Result.Position := 0;
  Result.Write(PAnsiChar('MC')^, 2);
end;

procedure Planta(f: TFileStream; posicao: LongInt; valor: Byte);
begin
  f.Position := posicao;
  f.Write(valor, 1);
end;

{ CASO 1 do readme -- *the captain and kickers when loading from .mcr files*.

  A correcao mora em duas coisas que um port perde por simplificar: a tabela
  `0x00423F84` NAO e crescente, e o capitao nao esta nela -- mora sozinho em
  `MCR_CAPITAO`, quase um kilobyte adiante. Quem trocar a tabela por
  aritmetica devolve os cinco na ordem do endereco (2, 3, 1, 0, 4) e um
  capitao que e o vizinho do quinto. }
procedure OCapitaoEOsCobradores;
const
  { OS ENDERECOS SAO LITERAIS DE PROPOSITO, e nao `MCR_COBRADORES`: plantar
    pela mesma constante que se le seria tautologia -- qualquer ordem passaria.
    Esta e a segunda copia da tabela `0x00423F84`, do mesmo jeito que o
    `test_dump_mcr.py` tem a dele. Quem confere as duas contra o `.exe` e o
    `--check` do `dump_mcr.py`. }
  ENDERECOS: array[0 .. 4] of LongInt = ($614F, $6140, $6122, $6113, $6131);
  ENDERECO_CAPITAO = $6500;
var
  f: TFileStream;
  caminho: string;
  c: TCartaoDeMemoria;
  i: Integer;
  ok: Boolean;
begin
  f := CartaoSintetico(caminho);
  try
    { Cada cobrador leva o proprio indice mais 100 -- valores distintos e
      longe de zero, para ordem trocada nao passar por coincidencia. }
    for i := 0 to High(ENDERECOS) do
      Planta(f, ENDERECOS[i], 100 + i);
    Planta(f, ENDERECO_CAPITAO, 200);
  finally
    f.Free;
  end;
  try
    Checa('o cartao sintetico abre', LeCartaoDeMemoria(caminho, c));
    ok := True;
    for i := 0 to High(MCR_COBRADORES) do
      if c.cobradores[i] <> 100 + i then
        ok := False;
    Checa('os cinco cobradores voltam na ordem da tabela', ok,
          Format('%d,%d,%d,%d,%d', [c.cobradores[0], c.cobradores[1],
                 c.cobradores[2], c.cobradores[3], c.cobradores[4]]));
    Checa('o capitao vem de 0x6500, e nao do sexto vizinho',
          c.cobradores[COBRADORES_BYTES - 1] = 200,
          Format('%d', [c.cobradores[COBRADORES_BYTES - 1]]));
    { E a razao de a tabela ser tabela: se os cinco fossem crescentes, ler por
      aritmetica daria o mesmo resultado e o caso nao existiria. }
    ok := False;
    for i := 1 to High(MCR_COBRADORES) do
      if MCR_COBRADORES[i] < MCR_COBRADORES[i - 1] then
        ok := True;
    Checa('a tabela de cobradores nao e monotona', ok);
    Checa('o capitao nao e vizinho do bloco de cobradores',
          Abs(MCR_CAPITAO - MCR_COBRADORES[0]) > 1);
    Checa('e a unidade concorda com os enderecos plantados',
          (MCR_CAPITAO = ENDERECO_CAPITAO)
          and (MCR_COBRADORES[0] = ENDERECOS[0])
          and (MCR_COBRADORES[4] = ENDERECOS[4]));
  finally
    DeleteFile(caminho);
  end;
end;

{ CASO 3 do readme -- *the spaces in the players names*.

  O campo de nome do cartao sao DEZ BYTES CRUS, e nao uma cadeia C: o original
  os traz por `fread` de 10, e o `0x0040b2d8` tem um ramo proprio para `0x20`
  ao montar a lista da tela. Um port que tratasse o campo como cadeia perderia
  o fim do nome que enche os dez bytes e comeria o espaco.

  Tres nomes plantados, e cada um quebra um jeito diferente de errar:
  `'R. CARLOS '` (espacos no meio e no fim), `'ABCDEFGHIJ'` (dez bytes sem
  terminador) e um com NUL no meio (`'AB'#0'CD'`), que so sobrevive a copia
  por tamanho. }
procedure EspacosNoNome;
const
  SLOT_ESPACO = 5;
  SLOT_CHEIO  = 11;
  SLOT_NUL    = 22;
  COM_ESPACO: array[0 .. 9] of Byte = (Ord('R'), Ord('.'), Ord(' '), Ord('C'),
    Ord('A'), Ord('R'), Ord('L'), Ord('O'), Ord('S'), Ord(' '));
  CHEIO: array[0 .. 9] of Byte = (Ord('A'), Ord('B'), Ord('C'), Ord('D'),
    Ord('E'), Ord('F'), Ord('G'), Ord('H'), Ord('I'), Ord('J'));
  COM_NUL: array[0 .. 9] of Byte = (Ord('A'), Ord('B'), 0, Ord('C'), Ord('D'),
    0, 0, 0, 0, 0);
var
  f: TFileStream;
  caminho: string;
  c: TCartaoDeMemoria;

  { `$5910` e o literal do `.exe` (`push 0x5910` em `0x0040b9f9`), nao
    `MCR_JOGADORES + MCR_ATRIBUTO_BYTES` -- ver a nota do caso acima. }
  procedure PlantaNome(slot: Integer; const bytes: array of Byte);
  var
    i: Integer;
  begin
    for i := 0 to High(bytes) do
      Planta(f, $5910 + 32 * slot + i, bytes[i]);
  end;

  function Confere(slot: Integer; const bytes: array of Byte): Boolean;
  var
    i: Integer;
  begin
    Result := True;
    for i := 0 to High(bytes) do
      if c.nomes[slot * MCR_NOME_BYTES + i] <> bytes[i] then
        Result := False;
  end;

  function HexDoSlot(slot: Integer): string;
  var
    i: Integer;
  begin
    Result := '';
    for i := 0 to MCR_NOME_BYTES - 1 do
      Result := Result
                + LowerCase(IntToHex(c.nomes[slot * MCR_NOME_BYTES + i], 2));
  end;

begin
  f := CartaoSintetico(caminho);
  try
    PlantaNome(SLOT_ESPACO, COM_ESPACO);
    PlantaNome(SLOT_CHEIO, CHEIO);
    PlantaNome(SLOT_NUL, COM_NUL);
  finally
    f.Free;
  end;
  try
    Checa('o cartao dos nomes abre', LeCartaoDeMemoria(caminho, c));
    Checa('nome com espaco no meio e no fim volta inteiro',
          Confere(SLOT_ESPACO, COM_ESPACO), HexDoSlot(SLOT_ESPACO));
    Checa('nome que enche os dez bytes nao perde o ultimo',
          Confere(SLOT_CHEIO, CHEIO), HexDoSlot(SLOT_CHEIO));
    Checa('NUL no meio nao encurta o campo',
          Confere(SLOT_NUL, COM_NUL), HexDoSlot(SLOT_NUL));
    { O vizinho tem de continuar zerado: passo 32 lido como 22 encavalaria. }
    Checa('o slot seguinte ao cheio continua zerado',
          c.nomes[(SLOT_CHEIO + 1) * MCR_NOME_BYTES] = 0);
  finally
    DeleteFile(caminho);
  end;
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
  OCapitaoEOsCobradores;
  EspacosNoNome;
  LeUmCartaoDeVerdade;
  WriteLn('CASOS'#9, casos);
  if falhas > 0 then
    Halt(1);
end.
