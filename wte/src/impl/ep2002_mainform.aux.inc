{ Rotinas internas do MainForm -- WTE-TASK-25.

  O original chama rotinas que NAO sao metodo publicado, e algumas de mais de
  um handler. Elas nao cabem num `.inc` por handler, e e por isso que este
  arquivo existe; ver `wte/src/impl/README.md`.

  Cada uma traz o endereco no `.exe` e a medicao que a sustenta. O inventario
  das 91 rotinas internas que o grupo de carga alcanca esta em
  `wte/re/auxiliares.md`. }

var
  { O `0x004335e4` do original: qual `dorsalN` esta marcado agora.

    E o MESMO ponteiro da `wte/re/crash-causa.md`. La ele derruba o `wte.exe`
    com a ROM europeia porque a carga de time o sobrescreve com dado de tabela
    vizinha, e o `TFont::SetSize` seguinte cai com `this` nulo. Aqui ele e
    tipado e so recebe o que o `FindComponent` devolveu, entao o modo de falha
    do original nao tem por onde acontecer. }
  CamisaMarcada: TStaticText = nil;

{ MarcaCamisa -- 0x0040b188, 335 bytes.
  Spec: wte/re/spec/MainForm.lista_jugadores_1Change.md

  Apaga a camisa marcada, acha a nova pelo nome e a destaca. Chamada por dois
  handlers: o `lista_jugadores_1Change` (com `ItemIndex + 1`) e o
  `lista_equiposChange`, com `1`, no fim da carga de time.

  As cores sao as do original, no `$00BBGGRR` da VCL -- que e tambem o do
  `TColor` da LCL, entao os valores passam sem conversao. `$000000FF` e
  vermelho puro; escrito como `#0000FF` seria azul.

  Os nomes de propriedade nao sao inferencia: saem dos simbolos importados que
  o corpo chama -- `TControl::SetLeft`, `SetWidth`, `SetTop`, `SetHeight`,
  `SetColor`, `BringToFront`, `SendToBack`, `TFont::SetSize`,
  `TFont::SetColor` e `TComponent::FindComponent`.

  Os 23 `dorsalN` declaram `Color = clGray` no DFM e a LCL tem
  `Transparent = True` por padrao no `TStaticText`, o que poderia engolir a
  cor de fundo -- a marcacao e feita de cor de fundo, entao seria o caso de
  falhar sem sintoma. Medido em 2026-08-11 no `:99`, gtk2: o pixel dentro de
  um `dorsalN` e (128, 128, 128), o `clGray` do DFM. A cor aparece, e nao ha o
  que compensar.

  DIVERGENCIA DELIBERADA (WTE-TASK-35): o original guarda o resultado do
  `FindComponent` sem conferir e o desreferencia na linha seguinte. Com
  numero fora da faixa 1..23 -- e `ItemIndex = -1` produz `0` -- isso e
  violacao de acesso. Aqui a marcacao apenas nao acontece. }
procedure MarcaCamisa(Numero: Integer);
var
  Achado: TComponent;
begin
  if CamisaMarcada <> nil then
  begin
    CamisaMarcada.Font.Size := 8;
    CamisaMarcada.Left := CamisaMarcada.Left + 5;
    CamisaMarcada.Width := CamisaMarcada.Width - 10;
    CamisaMarcada.Top := CamisaMarcada.Top + 5;
    CamisaMarcada.Height := CamisaMarcada.Height - 10;
    CamisaMarcada.Color := $00808080;
    CamisaMarcada.Font.Color := $00C0C0C0;
    CamisaMarcada.SendToBack;
    CamisaMarcada := nil;
  end;
  Achado := MainForm.FindComponent('dorsal' + IntToStr(Numero));
  if not (Achado is TStaticText) then
    Exit;
  CamisaMarcada := TStaticText(Achado);
  CamisaMarcada.BringToFront;
  CamisaMarcada.Left := CamisaMarcada.Left - 5;
  CamisaMarcada.Width := CamisaMarcada.Width + 10;
  CamisaMarcada.Top := CamisaMarcada.Top - 5;
  CamisaMarcada.Height := CamisaMarcada.Height + 10;
  CamisaMarcada.Color := $00FFFFFF;
  CamisaMarcada.Font.Color := $000000FF;
  CamisaMarcada.Font.Size := 14;
end;
