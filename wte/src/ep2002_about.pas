{ Esqueleto gerado por `wte/tools/dfm2lfm.py` (WTE-TASK-10).

  Formulario `ficha_about`, classe `Tficha_about`.
  Origem: `wte/re/dfm/ficha_about.dfm`.
  6 componentes, 2 handlers publicados.

  **NAO EDITAR A MAO.** Correcao entra no gerador e o arquivo e regerado;
  `python3 wte/tools/dfm2lfm.py --check` compara com o commitado e e o que
  `make -C wte check` roda.

  Os corpos dos handlers sao stub que registra o proprio nome (secao 4.3 do
  plano): a fase 2 monta a casca inteira e a fase 4 e que preenche. `REStub`
  vem de `retrace.pas`, da WTE-TASK-11 -- a unidade nao pode se chamar
  `restub`, porque o nome colidiria com o da rotina.
}
unit ep2002_about;

{$mode objfpc}{$H+}

interface

uses
  Forms, StdCtrls, ExtCtrls, Buttons, ActnList, retrace;

type
  Tficha_about = class(TForm)
    {
      Descartado: OldCreateOrder = False
      Motivo: propriedade de compatibilidade do Delphi 4; a LCL nao a tem e
      sempre usa a ordem nova de criacao.

      Descartado: TextHeight = 13
      Motivo: medida de tempo de projeto do Delphi, gravada para reescalar o
      formulario; a LCL nao a tem.
    }
    Image1: TImage;
    {
      Descartado: Action = lanza_url
      Motivo: a propriedade existe na LCL, mas o valor aponta para
      'lanza_url', que era TBrowseURL e virou TLabel; TLabel nao e
      TBasicAction e o leitor de LFM recusaria a atribuicao.
    }
    SpeedButton1: TSpeedButton;
    imagen_url: TImage;
    BitBtn3: TBitBtn;
    ActionList1: TActionList;
    {
      TODO WTE-TASK-10: 'lanza_url' era TBrowseURL -- a acao padrao da VCL
      (unidade Extactns), medida na WTE-TASK-07. A LCL nao a tem, e virou
      TLabel. O comportamento original abria a URL da constante LANZA_URL_URL
      no navegador: reimplementar com OpenURL() de LCLIntf no handler que
      dispara.

      Descartado: Category = 'Internet'
      Motivo: categoria de TAction; some com a acao, porque TLabel nao e acao.

      Descartado: URL = 'http://www.w11.com.br         '
      Motivo: propriedade do TBrowseURL; o valor fica na constante <NOME>_URL
      da unidade e o comportamento vira OpenURL() no handler.
    }
    lanza_url: TLabel;
    procedure FormCreate(Sender: TObject);
    procedure imagen_urlClick(Sender: TObject);
  private

  public

  end;

const
  { URL do TBrowseURL 'lanza_url', descartada do .lfm porque
    TLabel nao tem a propriedade. Guardada aqui para que o
    valor nao se perca -- ver wte/forms/conversao.md. }
  LANZA_URL_URL = 'http://www.w11.com.br         ';

var
  ficha_about: Tficha_about;

implementation

{$R ../forms/ep2002_about.lfm}

{$PUSH}{$WARN 5024 OFF}  // stub ignora os parametros

procedure Tficha_about.FormCreate(Sender: TObject);
begin
  REStub('ficha_about.FormCreate');
end;

procedure Tficha_about.imagen_urlClick(Sender: TObject);
begin
  REStub('ficha_about.imagen_urlClick');
end;

{$POP}

end.
