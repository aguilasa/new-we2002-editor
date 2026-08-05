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
  WteMain;

begin
  RequireDerivedFormResource := True;
  Application.Scaled := True;
  Application.Title := 'WE2002 Team Editor (Lazarus)';
  Application.Initialize;
  Application.CreateForm(TWteMainForm, WteMainForm);
  Application.Run;
end.
