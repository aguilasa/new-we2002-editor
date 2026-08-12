{ test_lcl_combo.pas -- o que a LCL dispara quando o CODIGO mexe num TComboBox.

  Da WTE-TASK-25, criterio "comportamento de `OnChange` na carga decidido e
  testado". Escrito a mao.

  A pergunta que ele responde, e por que ela nao se responde por leitura: o
  Win32 nao dispara `CBN_SELCHANGE` em `SetCurSel`, entao um handler do
  original pode depender de mexer no combo sem se auto-chamar. Se a LCL
  disparar `OnChange` em `ItemIndex :=`, o `lista_equiposChange` do port entra
  em recursao ou recarrega duas vezes -- e o sintoma nao e travamento, e uma
  carga a mais que ninguem ve.

  A mesma armadilha ja foi paga no `newWe2002`, do outro lado: la o Qt
  DISPARA `currentIndexChanged` em `setCurrentIndex` enquanto o MFC nao
  disparava, e as cargas de time precisaram de `QSignalBlocker` (ver o
  CLAUDE.md, secao do App). Aqui a pergunta e a mesma com outro widgetset, e a
  resposta tem de ser MEDIDA: gtk2 nao e Qt e nao e Win32.

  Cada linha da saida e `<caso><TAB>disparou|nao-disparou`. Quem compila, roda
  e julga e `wte/tools/check_lcl_combo.py`.

  Nao abre imagem, nao le nada do disco: so a LCL instalada. }
program test_lcl_combo;

{$mode objfpc}{$H+}

uses
  Interfaces, Forms, StdCtrls, ComCtrls, Classes, SysUtils;

type
  TSonda = class
  public
    Disparos: Integer;
    procedure AoMudar(Sender: TObject);
    procedure AoClicarSeta(Sender: TObject; Button: TUDBtnType);
  end;

procedure TSonda.AoMudar(Sender: TObject);
begin
  Inc(Disparos);
end;

{ O `OnClick` do `TUpDown` tem assinatura propria -- e o evento que os doze
  `flechasapa` do formulario `jugador` usam. }
procedure TSonda.AoClicarSeta(Sender: TObject; Button: TUDBtnType);
begin
  Inc(Disparos);
end;

var
  Form: TForm;
  Combo: TComboBox;
  Barra: TScrollBar;
  Seta: TUpDown;
  Sonda: TSonda;

procedure Relata(const Caso: string; Antes: Integer);
begin
  if Sonda.Disparos > Antes then
    WriteLn(Caso, #9, 'disparou')
  else
    WriteLn(Caso, #9, 'nao-disparou');
end;

var
  Marca: Integer;
begin
  Application.Initialize;
  Form := TForm.Create(nil);
  Combo := TComboBox.Create(Form);
  Combo.Parent := Form;
  Combo.Style := csDropDownList;
  Combo.Items.Add('  0 Irlanda');
  Combo.Items.Add('  1 Escocia');
  Combo.Items.Add(' 95 Master L. ');
  Sonda := TSonda.Create;
  Combo.OnChange := @Sonda.AoMudar;

  { 1. o caso central: o codigo escolhe um item. }
  Marca := Sonda.Disparos;
  Combo.ItemIndex := 1;
  Relata('ItemIndex-atribuido', Marca);

  { 2. atribuir o MESMO indice de novo -- a LCL pode ou nao curto-circuitar. }
  Marca := Sonda.Disparos;
  Combo.ItemIndex := 1;
  Relata('ItemIndex-igual-ao-atual', Marca);

  { 3. limpar a lista com um item selecionado. O `0x0040b2d8` do original
       esvazia a lista de jogadores antes de reenche-la, e se `Clear` dispara
       `OnChange` o port ganha uma carga a mais por troca de time. }
  Marca := Sonda.Disparos;
  Combo.Items.Clear;
  Relata('Items-Clear-com-selecao', Marca);

  { 4. reencher e selecionar, que e a sequencia da carga de time. }
  Combo.Items.Add('Jogador 1');
  Combo.Items.Add('Jogador 2');
  Marca := Sonda.Disparos;
  Combo.ItemIndex := 0;
  Relata('ItemIndex-apos-reencher', Marca);

  { 5. `ItemIndex := -1`, que e como o original desmarca. }
  Marca := Sonda.Disparos;
  Combo.ItemIndex := -1;
  Relata('ItemIndex-menos-um', Marca);

  { 6 e 7. Os dois controles que o `PreencheFicha` da WTE-TASK-26 escreve, e a
    pergunta e a mesma do combo com outra consequencia: se `Position :=`
    dispara, encher a ficha REENTRA nos dezesseis `barrhabScroll` e nos doze
    `flechasapaClick`, e cada um deles reescreve o rotulo que o preenchimento
    acabou de escrever. O `TTrackBar` ja respondeu "dispara" na segunda
    passagem daquela task; nao da para supor que estes tres concordem. }
  Barra := TScrollBar.Create(Form);
  Barra.Parent := Form;
  Barra.Min := 0;
  Barra.Max := 7;
  Barra.OnChange := @Sonda.AoMudar;
  Marca := Sonda.Disparos;
  Barra.Position := 5;
  Relata('ScrollBar-Position-atribuida', Marca);

  Marca := Sonda.Disparos;
  Barra.Position := 5;
  Relata('ScrollBar-Position-igual-a-atual', Marca);

  Seta := TUpDown.Create(Form);
  Seta.Parent := Form;
  Seta.Min := 0;
  Seta.Max := 7;
  Seta.OnClick := @Sonda.AoClicarSeta;
  Marca := Sonda.Disparos;
  Seta.Position := 3;
  Relata('UpDown-Position-atribuida', Marca);

  Sonda.Free;
  Form.Free;
end.
