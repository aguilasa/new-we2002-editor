{ Esqueleto gerado por `wte/tools/dfm2lfm.py` (WTE-TASK-10).

  Formulario `ficha_info4`, classe `Tficha_info4`.
  Origem: `wte/re/dfm/ficha_info4.dfm`.
  4 componentes, 1 handlers publicados.

  **NAO EDITAR A MAO.** Correcao entra no gerador e o arquivo e regerado;
  `python3 wte/tools/dfm2lfm.py --check` compara com o commitado e e o que
  `make -C wte check` roda.

  Cada handler sai de uma de duas formas. Sem corpo escrito, sai como stub que
  registra o proprio nome (secao 4.3 do plano); `REStub` vem de
  `retrace.pas`, da WTE-TASK-11 -- a unidade nao pode se chamar `restub`,
  porque o nome colidiria com o da rotina. Com corpo escrito, sai como a
  assinatura mais `{$I impl/<unidade>.<handler>.inc}`: o corpo e da fase 4,
  vem da spec de `wte/re/spec/`, e por isso mora fora deste arquivo gerado.
  Ver `wte/src/impl/README.md`.
}
unit ep2002_info4;

{$mode objfpc}{$H+}

interface

uses
  Forms, StdCtrls, Buttons, retrace;

type
  Tficha_info4 = class(TForm)
    {
      Descartado: OldCreateOrder = False
      Motivo: propriedade de compatibilidade do Delphi 4; a LCL nao a tem e
      sempre usa a ordem nova de criacao.

      Descartado: TextHeight = 13
      Motivo: medida de tempo de projeto do Delphi, gravada para reescalar o
      formulario; a LCL nao a tem.
    }
    etiq1: TLabel;
    etiq2: TLabel;
    etiq3: TLabel;
    BitBtn6: TBitBtn;
    procedure FormCreate(Sender: TObject);
  private

  public

  end;

var
  ficha_info4: Tficha_info4;

implementation

{$R ../forms/ep2002_info4.lfm}

{$PUSH}{$WARN 5024 OFF}  // stub ignora os parametros
procedure Tficha_info4.FormCreate(Sender: TObject);
begin
  REStub('ficha_info4.FormCreate');
end;
{$POP}

end.
