{ MainForm.boton_nombres2isoClick -- 0x0040d534, 2268 bytes.
  Spec: wte/re/spec/MainForm.boton_nombres2isoClick.md

  O maior do grupo de gravacao, e o unico que depende de duas tabelas e de tres
  rotinas internas do original. A varredura que acha o slot do time esta no
  `.aux.inc` (`LocalizaBlocoDeNome`), a codificacao tambem
  (`CodificaNomeDoBloco`), e o salto de setor esta no `we2002_estado`.

  Tres validacoes antes de qualquer gravacao, e tres exclusoes DENTRO do laco.
  As exclusoes nao sao validacao de entrada -- sao regras de formato, e cada
  uma esta na spec com o endereco que a decide. }
var
  campo, bloco, indice, i: Integer;
  textos: array[0..2] of string;
  achado: TBlocoDeNome;
  buffer: array[0..NOME_BUFFER_MAX - 1] of Byte;
  img: TCdImage;
  rotulo: string;
  combo: TComponent;
  guardado: Integer;
begin
  REMark('MainForm.boton_nombres2isoClick');

  { --- 1. as tres validacoes ------------------------------------------- }
  if edit_nombre1.Text = '' then
  begin
    ficha_error2.etiq1.Caption := 'Insira o nome (1)   ';
    ficha_error2.ShowModal;
    edit_nombre1.SetFocus;
    Exit;
  end;
  if edit_nombre2.Text = '' then
  begin
    ficha_error2.etiq1.Caption := 'Insira o nome (2)   ';
    ficha_error2.ShowModal;
    edit_nombre2.SetFocus;
    Exit;
  end;
  if Length(edit_nombre3.Text) < 3 then
  begin
    ficha_error2.etiq1.Caption := 'Insira o nome (3) de 3 letras ';
    ficha_error2.ShowModal;
    edit_nombre3.SetFocus;
    Exit;
  end;

  indice := lista_equipos.ItemIndex;
  textos[0] := edit_nombre1.Text;
  textos[1] := edit_nombre2.Text;
  textos[2] := edit_nombre3.Text;

  { --- 2. o rotulo dos outros dois combos ------------------------------- }
  { Indice alinhado a direita em tres colunas, mais o nome longo. Atribuir a
    `Items[]` zera a selecao, entao o `ItemIndex` e guardado e reposto -- e so
    quando ele ainda for o mesmo do combo principal, como no original. }
  if indice < 10 then
    rotulo := '  ' + IntToStr(indice) + textos[0]
  else
    rotulo := ' ' + IntToStr(indice) + textos[0];
  for i := 1 to 2 do
  begin
    combo := FindComponent('lista_equipos_' + IntToStr(i));
    if not (combo is TComboBox) then
      Continue;
    guardado := TComboBox(combo).ItemIndex;
    if (indice >= 0) and (indice < TComboBox(combo).Items.Count) then
      TComboBox(combo).Items[indice] := rotulo;
    if lista_equipos.ItemIndex = guardado then
      TComboBox(combo).ItemIndex := guardado;
  end;

  { --- 3. os blocos ----------------------------------------------------- }
  if ImagemAberta <> '' then
  begin
    img.Init;
    if img.OpenReadWrite(ImagemAberta) then
    try
      for campo := 0 to 2 do
      begin
        { O `?` e o que a carga mostra quando nao soube decodificar o nome.
          Regravar por cima destruiria o original, e o teste vale para TODOS
          os blocos daquele campo. No original ele e refeito por bloco; aqui
          uma vez, porque o texto nao muda no meio do laco. }
        if (campo = 0) and (Copy(textos[campo], 1, 1) = '?') then
          Continue;
        for bloco := 0 to 5 do
        begin
          if NOME_BLOCOS[campo, bloco] = 0 then
            Continue;
          { O bloco 3 do campo 2 e o `OFS_ML_TEAM_NAME_7`: so clube de Master
            League o tem. }
          if (campo = BLOCO_SO_DE_ML_CAMPO) and (bloco = BLOCO_SO_DE_ML_INDICE)
             and (indice < TIMES_NACIONAIS) then
            Continue;
          if not LocalizaBlocoDeNome(img, campo, bloco, indice, achado) then
            Continue;
          if achado.comprimento > Length(buffer) then
            Continue;
          CodificaNomeDoBloco(textos[campo], achado.comprimento, achado.modo,
                              buffer);
          GravaNoFluxo(img, achado.offset, buffer, achado.comprimento);
        end;
      end;
    finally
      img.Close;
    end;
  end;

  ficha_info3.etiq1.Caption := 'Nomes inseridos no jogo!!!     ';
  ficha_info3.ShowModal;
end;
