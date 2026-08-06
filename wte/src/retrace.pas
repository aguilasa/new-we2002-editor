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
  SysUtils;

var
  Inicio: TDateTime;
  Arquivo: string = '';
  Saida: TextFile;
  Aberto: Boolean = False;

// Onde o log mora, na mesma ordem de resolucao que o wte/README.md fixou
// para os assets -- variavel de ambiente primeiro, arvore de fonte depois.
// Aqui a arvore de fonte e o destino normal: `wte/re/trace.log` e o que a
// WTE-TASK-13 le. Note que ele NAO e versionado (e saida de execucao), e a
// WTE-TASK-13 e que decide o que vai para `wte/re/eventos.md`.
function ResolveArquivo: string;
var
  Dir: string;
begin
  Result := GetEnvironmentVariable('WTE_TRACE_FILE');
  if Result <> '' then
    Exit;
  // O binario vive em wte/build/; o log vai para wte/re/.
  Dir := ExtractFilePath(ParamStr(0));
  Result := IncludeTrailingPathDelimiter(Dir) + '../re/trace.log';
end;

procedure Garante;
begin
  if Aberto then
    Exit;
  Inicio := Now;
  Arquivo := ResolveArquivo;
  AssignFile(Saida, Arquivo);
  // Trunca: cada execucao e um trace novo. Acumular faria a WTE-TASK-13
  // comparar duas sessoes coladas e chamar isso de divergencia.
  Rewrite(Saida);
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
