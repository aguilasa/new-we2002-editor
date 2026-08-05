{ Formulario principal -- provisorio.

  Na fase 2 os 18 formularios do original passam a ser GERADOS pelo
  dfm2lfm.py (WTE-TASK-10), e esta unidade sai ou vira a casca do
  Tep2002_princ. Ate la ela existe so para provar que o build fecha e que a
  janela abre no :99. Nao invista nela. }

unit WteMain;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, Forms, Controls, StdCtrls;

type

  { TWteMainForm }

  TWteMainForm = class(TForm)
    LabelPlaceholder: TLabel;
  end;

var
  WteMainForm: TWteMainForm;

implementation

// O .lfm mora em wte/forms/, nao ao lado desta unidade.
//
// A forma usual -- $R com curinga -- NAO respeita o include path: o FPC
// expande o curinga para o nome da unidade e procura o arquivo no diretorio
// do .pas, e so ali. Com o layout do plano (src/ para codigo, forms/ para
// formulario) isso falha com "Can't open resource file .../src/WteMain.lfm",
// mesmo com forms/ em IncludeFiles. O caminho explicito abaixo e a saida, e o
// dfm2lfm.py da WTE-TASK-10 tem de emitir esta mesma linha nos 18 esqueletos.
{$R ../forms/WteMain.lfm}

end.
