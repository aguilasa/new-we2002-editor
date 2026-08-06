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
  Application.Scaled := True;
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
