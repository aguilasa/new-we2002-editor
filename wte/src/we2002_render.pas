{ we2002_render -- a aritmetica de cor do render 2D (WTE-TASK-29).

  ESCRITO A MAO, como o `we2002_mcr`: nao ha gerador possivel para a rotina, e
  o que E gerado -- a conferencia contra o `.exe` -- e o
  `wte/tools/dump_render2d.py`, que a cada `make check` le as constantes daqui
  e as compara com os padroes de instrucao do binario. A documentacao do
  formato, com a prova de cada afirmacao, esta em `wte/re/render2d.md`.

  ESTA UNIDADE NAO DESENHA. Ela nao usa LCL, nao abre arquivo e nao sabe o que
  e um `TBitmap` -- so converte, escurece, clareia e interpola cor. A separacao
  e a mesma do `src/core/` do `newWe2002`: a aritmetica e testavel headless, e
  quem a poe na tela e outro modulo. Um teste de cor que precise de janela e um
  teste que nao roda no gate.

  AS TRES COISAS QUE UM PORT ERRA AQUI, e as tres estao medidas:

  1. **a expansao de 5 para 8 bits e `shl 3`, e nao `v * 255 / 31`.** O teto do
     clarear no original e `$F8`, que e `31 shl 3` -- se a expansao fosse a
     regra de tres, o teto seria `$FF`. Branco de camisa clara sairia diferente;
  2. **escurecer e clarear nao mudam de espaco de cor.** A conta e no proprio
     `Word` BGR555 empacotado: `1`, `$20`, `$400`. Nao ha RGB de 8 bits nem HSL
     no caminho -- a decodificacao existe so para TESTAR o limite;
  3. **o gradiente acumula em `Single` e TRUNCA para zero.** Nao e `Round`. O
     original chama o `__ftol` da RTL, que poe `$C01` no control word do 387
     antes do `fistp`, e os bits 10-11 em `11` sao *round toward zero*. E o
     risco nomeado da secao 9 do plano, e e onde a rampa inteira desloca de um
     degrau se alguem escrever `Round`. }

unit we2002_render;

{$mode objfpc}{$H+}

interface

const
  { O formato da palavra de cor. Cinco bits por canal, tres canais, e o bit 15
    sem uso. A ORDEM DOS CAMPOS saiu de dois fatos que se encontram: o
    decodificador consome os cinco bits mais baixos primeiro e os poe no byte 0
    do buffer, e o escritor de paleta despeja esse buffer na ordem 2, 1, 0
    sobre uma entrada BMP, que e `B, G, R, reservado`. }
  RENDER_BITS = 5;
  RENDER_CANAIS = 3;
  { Os tres sao LITERAIS de proposito, e nao expressoes: o
    `dump_render2d.py` le esta secao e compara cada um com o operando da
    instrucao correspondente no `.exe`, e uma expressao o obrigaria a
    reimplementar Pascal para conferir. A derivacao fica no comentario, e o
    `test_render.pas` a executa -- ele exige `RENDER_MAXIMO = 31 shl 3`. }
  RENDER_MASCARA = $1F;      { (1 shl RENDER_BITS) - 1 }
  RENDER_EXPANSAO = 3;       { o `shl 3` do 0x00404dd4 }
  RENDER_MAXIMO = $F8;       { RENDER_MASCARA shl RENDER_EXPANSAO = 248 }

  { Um degrau em cada campo, na palavra empacotada. Sao os tres imediatos que
    o `oscurecerClick` subtrai e o `aclararClick` soma. }
  RENDER_PASSO_R = $0001;
  RENDER_PASSO_G = $0020;
  RENDER_PASSO_B = $0400;

  { O bitmap de 8 bpp: e por isso que o `fseek` do original e `$36`. }
  BMP_CABECALHO = 54;
  BMP_ENTRADA_BYTES = 4;

  { Quantas entradas cada renderizador reescreve, POR ARQUIVO. Nao e o mesmo
    nos dois, e a assimetria e do original -- `cmp esi,0x10` na bandeira e
    `cmp esi,0xf` no uniforme. Um laco compartilhado escreveria uma entrada a
    mais em toda camisa. }
  PALETA_BANDEIRA = 16;
  PALETA_UNIFORME = 15;
  { E quantos arquivos cada um toca: o uniforme faz camiseta e calcao. }
  ARQUIVOS_BANDEIRA = 1;
  ARQUIVOS_UNIFORME = 2;

type
  { A palavra como o jogo a guarda. `Word` e nao `LongInt` de proposito: o
    tamanho e do formato, nao da plataforma -- a armadilha do `DWORD` que
    embaralhou numero de camisa no `newWe2002` mora exatamente aqui. }
  TCorBgr555 = Word;

  { Os tres canais JA EXPANDIDOS para 8 bits, na ordem R, G, B. E o buffer de
    tres bytes que o `0x00404dd4` enche. }
  TCanais = array[0 .. RENDER_CANAIS - 1] of Byte;

  { Os tres bytes que o original escreve numa entrada de paleta, na ordem em
    que ele os escreve. O quarto byte da entrada -- o reservado -- ele NAO
    escreve: pula com `fseek(+1)`. Ver `EntradaDePaleta`. }
  TEntradaDePaleta = array[0 .. RENDER_CANAIS - 1] of Byte;

{ Os cinco bits de cada canal, expandidos para 8 -- a `0x00404dd4`.

  O canal 0 sai dos bits 0..4, o 1 dos 5..9 e o 2 dos 10..14, e cada um vira
  `v shl 3`. O bit 15 e ignorado. }
function DecodificaCor(palavra: TCorBgr555): TCanais;

{ A palavra de volta, a partir dos tres valores de CINCO bits.

  Nao e o inverso da `DecodificaCor` -- aquela devolve oito bits. Existe para
  os testes e para quem monta cor nova; o original nunca precisa dela, porque
  soma e subtrai na palavra sem desmonta-la. }
function CodificaCor(r5, g5, b5: Integer): TCorBgr555;

{ Um degrau para baixo em cada canal -- o `oscurecerClick` (0x004065fc).

  O canal so desce se o byte EXPANDIDO for maior que zero, e essa guarda e o
  que impede o campo de dar a volta e roubar do vizinho. }
function Escurece(palavra: TCorBgr555): TCorBgr555;

{ Um degrau para cima -- o `aclararClick` (0x00406744).

  Espelho exato do anterior, com o teto em `RENDER_MAXIMO`. Que o teto seja
  `$F8` e nao `$FF` e a prova de que a expansao e deslocamento. }
function Clareia(palavra: TCorBgr555): TCorBgr555;

{ A rampa do `gradienteClick` (0x004063b0) -- o MIOLO entre duas pontas.

  `distancia` e quantas posicoes separam as duas pontas na paleta, e a rampa
  preenche as `distancia - 1` entradas DE DENTRO: `saida[i]` e a cor da posicao
  `inicio + i + 1`. As pontas nao sao reescritas -- elas ja tem a cor que o
  usuario escolheu, e o laco do original vai de `ini + 1` ate `fim - 1`
  (`cmp ebx,[0x433dd0]` com `jl`).

  **Errar isto e escrever `distancia` entradas e apagar a ponta final.** Devolve
  False se `distancia` nao for maior que zero ou se o miolo nao couber na
  saida.

  DUAS COISAS AQUI SAO O RISCO NOMEADO DA SECAO 9 DO PLANO:

  - o passo e o acumulador sao `Single`, e nao `Double`. O original guarda os
    dois com `fstp DWORD PTR`, que e precisao simples;
  - a conversao para inteiro e `Trunc`, e nao `Round`. Escrever `Round` aqui
    desloca a rampa inteira de um degrau em metade dos casos.

  E a soma NAO recompoe a palavra canal a canal: soma os deslocamentos
  truncados sobre a palavra de partida, que e como o original faz. }
function Rampa(inicio, fim: TCorBgr555; distancia: Integer;
               var saida: array of TCorBgr555): Boolean;

{ Os tres bytes de uma entrada de paleta, NA ORDEM EM QUE O ORIGINAL OS ESCREVE.

  `B, G, R`. O quarto byte da entrada BMP -- o reservado -- fica como estava:
  o original o pula com `fseek(+1)` em vez de zera-lo, e preservar e o
  comportamento correto de um port. }
function EntradaDePaleta(palavra: TCorBgr555): TEntradaDePaleta;

{ Onde no arquivo mora a entrada `indice` da paleta.

  `BMP_CABECALHO + 4 * indice`. Para `indice = 0` da `$36`, que e o `fseek` que
  as tres rotinas de desenho fazem. }
function OffsetDaEntrada(indice: Integer): LongInt;

implementation

function DecodificaCor(palavra: TCorBgr555): TCanais;
var
  c: Integer;
begin
  for c := 0 to RENDER_CANAIS - 1 do
    Result[c] := Byte(((palavra shr (RENDER_BITS * c)) and RENDER_MASCARA)
                      shl RENDER_EXPANSAO);
end;

function CodificaCor(r5, g5, b5: Integer): TCorBgr555;
begin
  Result := TCorBgr555((r5 and RENDER_MASCARA)
                       or ((g5 and RENDER_MASCARA) shl RENDER_BITS)
                       or ((b5 and RENDER_MASCARA) shl (2 * RENDER_BITS)));
end;

function Escurece(palavra: TCorBgr555): TCorBgr555;
var
  canais: TCanais;
begin
  canais := DecodificaCor(palavra);
  Result := palavra;
  if canais[0] > 0 then
    Result := Result - RENDER_PASSO_R;
  if canais[1] > 0 then
    Result := Result - RENDER_PASSO_G;
  if canais[2] > 0 then
    Result := Result - RENDER_PASSO_B;
end;

function Clareia(palavra: TCorBgr555): TCorBgr555;
var
  canais: TCanais;
begin
  canais := DecodificaCor(palavra);
  Result := palavra;
  if canais[0] < RENDER_MAXIMO then
    Result := Result + RENDER_PASSO_R;
  if canais[1] < RENDER_MAXIMO then
    Result := Result + RENDER_PASSO_G;
  if canais[2] < RENDER_MAXIMO then
    Result := Result + RENDER_PASSO_B;
end;

function Rampa(inicio, fim: TCorBgr555; distancia: Integer;
               var saida: array of TCorBgr555): Boolean;
var
  passo, acumulado: array[0 .. RENDER_CANAIS - 1] of Single;
  a, b: TCanais;
  c, i: Integer;
  palavra: LongInt;
begin
  Result := False;
  if (distancia <= 0) or (distancia - 1 > Length(saida)) then
    Exit;
  { As pontas entram em CINCO bits: o original divide o byte expandido por 8
    antes de subtrair (`sar edi,0x3`), e e a diferenca de cinco bits que vira
    numerador do passo. }
  a := DecodificaCor(inicio);
  b := DecodificaCor(fim);
  for c := 0 to RENDER_CANAIS - 1 do
  begin
    passo[c] := Single(Integer(b[c] shr RENDER_EXPANSAO)
                       - Integer(a[c] shr RENDER_EXPANSAO)) / Single(distancia);
    acumulado[c] := 0;
  end;
  for i := 0 to distancia - 2 do
  begin
    for c := 0 to RENDER_CANAIS - 1 do
      acumulado[c] := acumulado[c] + passo[c];
    { `Trunc`, NAO `Round` -- ver o cabecalho da unidade. E a soma e sobre a
      palavra de partida, com os deslocamentos ja aplicados. }
    palavra := LongInt(inicio)
               + Trunc(acumulado[0])
               + (Trunc(acumulado[1]) shl RENDER_BITS)
               + (Trunc(acumulado[2]) shl (2 * RENDER_BITS));
    saida[i] := TCorBgr555(palavra);
  end;
  Result := True;
end;

function EntradaDePaleta(palavra: TCorBgr555): TEntradaDePaleta;
var
  canais: TCanais;
begin
  canais := DecodificaCor(palavra);
  Result[0] := canais[2];   { B }
  Result[1] := canais[1];   { G }
  Result[2] := canais[0];   { R }
end;

function OffsetDaEntrada(indice: Integer): LongInt;
begin
  Result := BMP_CABECALHO + BMP_ENTRADA_BYTES * indice;
end;

end.
