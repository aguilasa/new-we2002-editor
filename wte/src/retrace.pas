{ retrace -- o registrador de disparo de evento da casca (WTE-TASK-11).

  A casca da fase 2 nao faz nada: cada um dos 96 handlers gerados pelo
  dfm2lfm.py chama REStub com o proprio nome qualificado. O que parece
  desperdicio e a ferramenta de RE mais barata do projeto -- clicando no
  original e na casca lado a lado, a ORDEM REAL de disparo aparece, e ela
  nao sai de analise estatica nenhuma. E o insumo da WTE-TASK-13.

  A unidade NAO pode se chamar `restub`: identificador em Pascal nao
  distingue maiuscula de minuscula, entao uma unidade `restub` exportando
  uma rotina `REStub` nao compila -- "Syntax error, "." expected but "("
  found". A WTE-TASK-11 pedia `wte/src/restub.pas`; virou este arquivo, e o
  nome da rotina ficou como o plano escreveu.

  O formato do log e ESTAVEL E DIFFAVEL de proposito: a WTE-TASK-13 compara
  duas execucoes com `diff`. Por isso o carimbo e relativo ao inicio do
  processo, nao a hora do dia -- hora do dia faria toda linha divergir.

    0.000  MainForm.FormCreate
    0.184  MainForm.FormShow
    1.902  MainForm.lista_equiposChange

  Tres casas de milissegundo bastam para ordenar e nao bastam para virar
  ruido de agendamento; a coluna existe para ler INTERVALO, e a ordem das
  linhas e que carrega a informacao. }

unit retrace;

{$mode objfpc}{$H+}

interface

// Registra um disparo. `Nome` e o nome qualificado, `formulario.handler`,
// como o dfm2lfm.py emite -- sem ele `FormCreate` seria ambiguo entre 16.
procedure REStub(const Nome: string);

// Escreve uma linha de marcacao no mesmo log, para a WTE-TASK-13 separar os
// trechos de uma sessao ("abri o formulario X", "cliquei no botao Y").
//
// NAO se chama `RETrace`: colidiria com o nome desta unidade, pelo mesmo
// motivo que impediu `restub` -- identificador em Pascal nao distingue
// maiuscula, e `RETrace('x')` vira "Syntax error, "." expected but "("
// found". O erro so aparece no primeiro uso, nao na declaracao.
procedure REMark(const Marca: string);

// Caminho do log em uso. Vazio antes do primeiro registro.
function RETraceFile: string;

implementation

uses
  SysUtils, wte_datafiles;

var
  Inicio: TDateTime;
  Arquivo: string = '';
  Saida: TextFile;
  Aberto: Boolean = False;
  // Ligado uma vez quando o log nao abre. Sem ele, cada `REMark` tentaria de
  // novo e a sessao inteira pagaria uma excecao por marca.
  Desligado: Boolean = False;

// Onde o log mora: a regra inteira esta no `wte_datafiles`, junto com a dos
// assets, e o motivo de ela ter saido daqui e concreto.
//
// ISTO DERRUBAVA O APP FORA DE `wte/build/`. Esta funcao resolvia
// `<dir do executavel>/../re/trace.log` e entregava o caminho sem conferir
// nada; o `Rewrite` abaixo levantava `EInOutError` quando o diretorio nao
// existia, e a LCL mostrava `File not found. / Press OK to ignore and risk
// data corruption.` ANTES da primeira janela. Medido na WTE-TASK-38, com
// controle: `mkdir re` ao lado da copia e o mesmo binario abria.
//
// `wte/re/trace.log` continua sendo o destino na arvore de fonte -- e o que a
// WTE-TASK-13 le, e ele NAO e versionado.
function ResolveArquivo: string;
begin
  Result := CaminhoDeTrace;
end;

// TRACE NUNCA DERRUBA O APP. Se o arquivo nao abrir -- diretorio somente
// leitura, disco cheio, caminho vazio --, o trace se desliga para a sessao
// inteira e o programa segue. Um log e diagnostico; diagnostico que mata o
// paciente e pior que nenhum, e este ja matou.
procedure Garante;
begin
  if Aberto or Desligado then
    Exit;
  Inicio := Now;
  Arquivo := ResolveArquivo;
  if Arquivo = '' then
  begin
    Desligado := True;
    Exit;
  end;
  AssignFile(Saida, Arquivo);
  try
    // Trunca: cada execucao e um trace novo. Acumular faria a WTE-TASK-13
    // comparar duas sessoes coladas e chamar isso de divergencia.
    Rewrite(Saida);
  except
    on E: Exception do
    begin
      Desligado := True;
      Arquivo := '';
      Exit;
    end;
  end;
  Aberto := True;
end;

function Decorrido: Double;
begin
  Result := (Now - Inicio) * 86400.0;
  if Result < 0 then
    Result := 0;
end;

procedure Emite(const Prefixo, Texto: string);
begin
  Garante;
  if not Aberto then
    Exit;
  WriteLn(Saida, Format('%7.3f  %s%s', [Decorrido, Prefixo, Texto]));
  // Flush a cada linha: a sessao termina com a janela sendo morta por
  // `xdotool`/`kill`, e buffer nao esvaziado perde justamente o fim do
  // trace, que e a parte que interessa.
  Flush(Saida);
end;

procedure REStub(const Nome: string);
begin
  Emite('', Nome);
end;

procedure REMark(const Marca: string);
begin
  Emite('== ', Marca);
end;

function RETraceFile: string;
begin
  Result := Arquivo;
end;

finalization
  if Aberto then
    CloseFile(Saida);
end.
