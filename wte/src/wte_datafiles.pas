{ wte_datafiles -- onde os arquivos moram, em tempo de execucao.

  Produto da WTE-TASK-39. Uma unidade so, e ela existe porque as duas
  resolucoes de caminho do app estavam em lugares diferentes e uma delas
  derrubava o programa:

  - os ASSETS (os 198 `.bmp` e o `data/dat.bin`) moravam no
    `we2002_estado.RaizDosAssets`;
  - o LOG DE TRACE morava no `retrace.ResolveArquivo`, e ele resolvia
    `<dir do executavel>/../re/trace.log` sem conferir se o diretorio existe.
    O `Rewrite` levantava `EInOutError` e a LCL mostrava o dialogo generico
    `File not found. / Press OK to ignore and risk data corruption.` ANTES de
    qualquer janela: o binario nao abria fora de `wte/build/`. Medido na
    WTE-TASK-38, com controle -- `mkdir re` ao lado da copia e a janela abria.

  As duas continuam com nomes proprios nos lugares de origem; o que muda e que
  a REGRA mora aqui, uma vez.

  ## A ordem de busca, e por que esta

  E a mesma que o `wte/README.md` fixou na fase 0, herdada do
  `src/app/DataFiles.cpp` do `newWe2002`: **variavel de ambiente, ao lado do
  executavel, o prefixo instalado, a arvore de fonte**. Ela permite mover a
  arvore instalada, que e a condicao 3 da WTE-TASK-40 -- nenhum caminho
  absoluto e compilado no binario.

  ## O que NAO se resolve aqui

  A imagem de CD. Ela vem da linha de comando ou do dialogo de abrir, e o
  caminho e do usuario. }
unit wte_datafiles;

{$mode objfpc}{$H+}

interface

const
  { O slug da WTE-TASK-38 -- o nome que o sistema de arquivos le. O nome de
    produto (`WE2002 - Lazarus Editor`) nao entra em caminho nenhum: tem
    espaco e hifen. }
  SLUG = 'we2002Lazarus';

{ Raiz que contem `image/` e `data/`. Vazia quando nao se acha nenhuma.

  Ordem: `$WTE_ASSETS_DIR`, ao lado do executavel (`../assets`, a arvore de
  desenvolvimento), o prefixo instalado (`../share/we2002Lazarus`), e a arvore
  de fonte um nivel acima. O teste de cada candidato e a existencia do
  `data/dat.bin` -- e o arquivo que o arranque exige, e o unico que serve de
  sentinela para os dois grupos. }
function RaizDosAssets: string;

{ O texto que o app mostra quando a raiz nao existe.

  Ele diz **o que falta e onde por**, que e o criterio da WTE-TASK-39, e nao
  um erro generico de arquivo nao encontrado. Os assets nao sao
  redistribuidos (WTE-TASK-38): quem recebe o app nao tem como adivinhar. }
function MensagemDeAssetsAusentes: string;

{ Caminho do log de trace, sempre gravavel.

  Ordem: `$WTE_TRACE_FILE` (o que o harness golden define), o `re/` ao lado do
  executavel SE ELE EXISTIR, o diretorio de estado do usuario
  (`$XDG_STATE_HOME` ou `~/.local/state`), e por fim o temporario. Devolve
  vazio se nenhum servir -- e ai o `retrace` desliga o trace em vez de
  derrubar o app. }
function CaminhoDeTrace: string;

implementation

uses
  SysUtils;

function DirDoExecutavel: string;
begin
  Result := IncludeTrailingPathDelimiter(ExtractFilePath(ParamStr(0)));
end;

function TemAssets(const raiz: string): Boolean;
begin
  Result := (raiz <> '')
    and FileExists(IncludeTrailingPathDelimiter(raiz)
                   + 'data' + DirectorySeparator + 'dat.bin');
end;

function RaizDosAssets: string;
var
  candidatos: array[0..3] of string;
  i: Integer;
  base: string;
begin
  base := DirDoExecutavel;
  candidatos[0] := GetEnvironmentVariable('WTE_ASSETS_DIR');
  candidatos[1] := base + '..' + DirectorySeparator + 'assets';
  candidatos[2] := base + '..' + DirectorySeparator + 'share'
                        + DirectorySeparator + SLUG;
  candidatos[3] := base + '..' + DirectorySeparator + '..'
                        + DirectorySeparator + 'assets';
  for i := Low(candidatos) to High(candidatos) do
    if TemAssets(candidatos[i]) then
      Exit(IncludeTrailingPathDelimiter(candidatos[i]));
  Result := '';
end;

function MensagemDeAssetsAusentes: string;
begin
  Result :=
    'Faltam os arquivos do editor original (os 198 .bmp de image/ e o'
    + LineEnding + 'data/dat.bin). Eles nao sao distribuidos com este'
    + ' programa.' + LineEnding + LineEnding
    + 'Ponha a pasta do WE2002 Team Editor num destes lugares:'
    + LineEnding + LineEnding
    + '  1. no diretorio que a variavel WTE_ASSETS_DIR apontar; ou'
    + LineEnding
    { `ExpandFileName` porque o candidato e montado com `..` e o caminho cru
      sai `.../bin/../assets` -- legivel para o computador, feio para quem tem
      de digitar. }
    + '  2. em ' + ExpandFileName(DirDoExecutavel + '..' + DirectorySeparator
                                  + 'assets') + '; ou'
    + LineEnding
    + '  3. em ' + ExpandFileName(DirDoExecutavel + '..' + DirectorySeparator
                                  + 'share' + DirectorySeparator + SLUG)
    + LineEnding + LineEnding
    + 'A pasta tem de conter image/ e data/dat.bin.';
end;

function DirGravavel(const dir: string): Boolean;
begin
  Result := False;
  if dir = '' then
    Exit;
  if not DirectoryExists(dir) then
    if not ForceDirectories(dir) then
      Exit;
  Result := DirectoryExists(dir);
end;

function CaminhoDeTrace: string;
var
  dir, estado: string;
begin
  Result := GetEnvironmentVariable('WTE_TRACE_FILE');
  if Result <> '' then
    Exit;

  { A arvore de fonte: `wte/build/wte` escreve em `wte/re/trace.log`, que e
    onde a WTE-TASK-13 o le. SO se o diretorio ja existir -- criar um `re/` ao
    lado de um binario instalado seria inventar diretorio no prefixo do
    usuario. }
  dir := DirDoExecutavel + '..' + DirectorySeparator + 're';
  if DirectoryExists(dir) then
    Exit(IncludeTrailingPathDelimiter(dir) + 'trace.log');

  { O diretorio de estado do usuario, que e onde log de aplicacao instalada
    mora no freedesktop. }
  estado := GetEnvironmentVariable('XDG_STATE_HOME');
  if estado = '' then
  begin
    estado := GetEnvironmentVariable('HOME');
    if estado <> '' then
      estado := IncludeTrailingPathDelimiter(estado)
                + '.local' + DirectorySeparator + 'state';
  end;
  if estado <> '' then
  begin
    dir := IncludeTrailingPathDelimiter(estado) + SLUG;
    if DirGravavel(dir) then
      Exit(IncludeTrailingPathDelimiter(dir) + 'trace.log');
  end;

  dir := GetTempDir;
  if dir <> '' then
    Exit(IncludeTrailingPathDelimiter(dir) + SLUG + '-trace.log');

  Result := '';
end;

end.
