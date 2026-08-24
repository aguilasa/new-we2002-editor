{ we2002_preco -- o preco derivado dos atributos (WTE-TASK-32).

  ESCRITA A MAO, como a `we2002_estado` e a `wte_ficha`. O prefixo `we2002_` e
  o da camada de FORMATO, e esta unidade e disso: uma funcao pura sobre valores
  ja decodificados, sem LCL, sem I/O, sem estado. E o que permite testa-la sem
  abrir janela.

  ## A feature

  O `ed.exe` calcula preco e nao tem botao para isso (CORR-WTE-094); o editor
  do Obocaman tem dois, e sao as duas metades desta task:

  - `jugador.etiqprecioClick` (`0x00408bb8`) -- o preco de UM jogador, na tela;
  - `MainForm.base_teamClick` (`0x00410ff4`) -- o preco dos 23, GRAVADO.

  As duas somam de jeitos diferentes e caem na MESMA formula.

  ## A soma

  O `etiqprecioClick` soma o campo `+0x20c` de dezesseis componentes achados por
  `FindComponent('barrhab' + N)` -- e `+0x20c` num `TScrollBar` e a `Position`.
  Ou seja: ele soma o que esta NA TELA, e o que esta na tela e
  `max(atributo - 12, 0)`, que e o que a `PreencheFicha` poe la.

  O `base_teamClick` nao tem tela por jogador: ele soma dezesseis chamadas a
  `0x00403278` sobre uma tabela de 16 registros de 12 bytes em `0x00423648`, com
  os atributos crus em `0x0043364e`/`0x0043364f`. Chega ao mesmo numero por
  outro caminho -- decodificar o atributo e o que a `TPlayer.Decode` ja faz aqui.

  POR ISSO O PORT NAO PORTA A `0x00403278`. Ela e o decodificador de atributo do
  original, e este port tem o dele, transpilado do `we2002_core` e conferido
  contra as duas ROMs desde a fase 3. Reproduzi-la seria ter dois.

  ## A formula

  Aritmetica INTEIRA sobre a soma, identica nos dois handlers
  (`0x004110e7`..`0x0041112a` e `0x00408c3b`..`0x00408c83`):

      preco := s*s*s*s div 3000000
             + s*s*s   div   40000
             + s*s     div     700
             + s       div       7
             + 5

  ## Tres coisas que a leitura ingenua erraria

  1. **O `s*s*s*s` e de 32 BITS, e transborda.** O original faz `imul` de 32x32
     -- que produz 64 bits em `edx:eax` -- e logo em seguida um `cdq`, que
     REESCREVE `edx` com o sinal de `eax`. A metade alta e jogada fora antes da
     divisao. Em Pascal isso e `LongInt` deliberado, nao `Int64`: com `Int64` o
     preco divergiria para toda soma acima de ~215, e nao ha teto que impeca uma
     soma dessas.

  2. **A divisao trunca para ZERO, nao para baixo.** `idiv` do x86 e o `div` do
     Object Pascal fazem o mesmo; `Floor` faria outra coisa em negativo. Soma
     negativa nao acontece (a `Position` e nao-negativa), mas o transbordo do
     item 1 PRODUZ valor negativo, e ai a diferenca aparece.

  3. **O `x 5 div 3` e do goleiro, e a condicao mora em lugares diferentes nos
     dois handlers.** No `etiqprecioClick` e `flechasapa1.Position = 0`
     (`0x00408c90`), e o `flechasapa1` e a seta de POSICAO; no `base_teamClick`
     e a mesma pergunta feita a memoria, via `0x00403278` sobre o indice 0.
     Posicao 0 e goleiro.

  A ordem tambem importa: o `x 5 div 3` vem DEPOIS do `+ 5`, sobre o preco
  inteiro. }
unit we2002_preco;

{$mode objfpc}{$H+}

interface

uses
  we2002_player;

const
  { Os quatro divisores, na ordem em que o original os aplica. Ficam nomeados
    porque aparecem duas vezes no `.exe` -- uma por handler -- e a conferencia
    entre os dois e o que prova que a formula e uma so. }
  DIV_QUARTA  = 3000000;   { 0x2DC6C0 }
  DIV_CUBO    =   40000;   { 0x9C40   }
  DIV_QUADRADO =    700;   { 0x2BC    }
  DIV_LINEAR  =       7;
  TERMO_FIXO  =       5;

  { O desconto de 12 que a tela aplica antes de mostrar a barra. }
  PISO_DA_BARRA = 12;

  { A posicao do goleiro, e o unico valor de `position` que muda o preco. }
  POSICAO_GOLEIRO = 0;

  { O `etiqprecioClick` MOSTRA o preco vezes dez mil (`imul` de 64 bits por
    `0x2710` em `0x00408cb3`). O byte gravado na imagem e o preco SEM o fator:
    quem multiplica e so a exibicao, e confundir os dois poria 210000 num byte. }
  FATOR_DE_EXIBICAO = 10000;

{ A soma das dezesseis barras de habilidade, como a tela as mostra.

  E a entrada da formula nos DOIS handlers. A ordem das dezesseis e a da ficha
  (`PreencheFicha`), e ela nao e arbitraria: e a ordem da tabela de 16 registros
  que o `base_teamClick` percorre. }
function SomaDasHabilidades(const p: TPlayer): LongInt;

{ A formula, sobre a soma. Sem o ajuste do goleiro. }
function PrecoDaSoma(soma: LongInt): LongInt;

{ O preco de um jogador: soma, formula, e o `x 5 div 3` se for goleiro. }
function PrecoDoJogador(const p: TPlayer): LongInt;

implementation

function SomaDasHabilidades(const p: TPlayer): LongInt;

  { O que a `PreencheFicha` poe na `barrhab<n>.Position`. }
  function Barra(valor: LongInt): LongInt;
  begin
    Result := valor - PISO_DA_BARRA;
    if Result < 0 then
      Result := 0;
  end;

begin
  Result := Barra(p.attack)        + Barra(p.defence)
          + Barra(p.strength)      + Barra(p.stamina)
          + Barra(p.speed)         + Barra(p.acceleration)
          + Barra(p.passing)       + Barra(p.shot_power)
          + Barra(p.shot_accuracy) + Barra(p.jump)
          + Barra(p.heading)       + Barra(p.technique)
          + Barra(p.dribbling)     + Barra(p.swerve)
          + Barra(p.aggression)    + Barra(p.reflexes);
end;

function PrecoDaSoma(soma: LongInt): LongInt;
var
  s2, s3, s4: LongInt;
begin
  { LongInt em TODOS os quatro, e transbordo e o comportamento pedido -- ver o
    item 1 do cabecalho. `$Q-` porque o FPC pode estar com verificacao de
    overflow ligada, e ai o transbordo viraria excecao em vez de valor. }
  {$PUSH}{$Q-}{$R-}
  s2 := soma * soma;
  s3 := s2 * soma;
  s4 := s3 * soma;
  Result := (s4 div DIV_QUARTA)
          + (s3 div DIV_CUBO)
          + (s2 div DIV_QUADRADO)
          + (soma div DIV_LINEAR)
          + TERMO_FIXO;
  {$POP}
end;

function PrecoDoJogador(const p: TPlayer): LongInt;
begin
  Result := PrecoDaSoma(SomaDasHabilidades(p));
  { Depois do `+ 5`, sobre o preco inteiro. }
  if p.position = POSICAO_GOLEIRO then
    Result := (Result * 5) div 3;
end;

end.
