{ WE2002 Team Editor, reimplementado em Lazarus/LCL.

  Reimplementacao do "WE2002 Team Editor v0.99" do Obocaman (C++Builder 6,
  Win32). Projeto SEPARADO do newWe2002 -- ver wte/README.md.

  O nome do produto ainda nao foi escolhido: e decisao da WTE-TASK-38, por
  causa da secao 2 do plano. Ate la o binario se chama "wte". }

program wte;

{$mode objfpc}{$H+}

uses
  Interfaces,   // widgetset da LCL -- tem de vir antes de Forms
  Forms,
  wtemain;      // auto-create na ordem medida, e a linha de comando

begin
  RequireDerivedFormResource := True;
  // NAO religar `Application.Scaled`. A linha veio do gabarito de projeto do
  // Lazarus e nunca foi argumentada; medida na decima terceira passagem da
  // WTE-TASK-26, ela fazia a janela sair 1,0421 vez a do projeto -- 544x495
  // contra os 522x475 do `.lfm` -- e essa razao depende do DPI de fonte da
  // maquina, entao o tamanho da janela do port nao era nem estavel entre
  // maquinas.
  //
  // O alvo e um Win32 de 2002 sem escala nenhuma, e a fidelidade de geometria
  // e criterio deste projeto: com a escala ligada, toda regua de pixel media
  // o DPI junto. Sem ela as coordenadas do `.lfm` valem nos DOIS lados, que e
  // o que o `compara_tela.sh` precisa.
  //
  // O TITULO TEM DE SER DIFERENTE DO ORIGINAL. O wte.exe se chama
  // "W11 Team Editor PT by chagas_michel!"; a partir da WTE-TASK-22 os dois
  // rodam no mesmo :99, e os scripts acham janela por titulo e por tamanho.
  // Titulo igual faria o harness dirigir o lado errado, e o diff pareceria
  // bug do port -- e a armadilha 6 do progresso.md.
  Application.Title := 'WE2002 Team Editor (Lazarus)';
  Application.Initialize;
  CriaFormularios;
  if TrataLinhaDeComando then
    Application.Run;
end.
