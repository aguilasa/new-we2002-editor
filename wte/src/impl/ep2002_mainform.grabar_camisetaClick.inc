{ MainForm.grabar_camisetaClick -- 0x0040ee80, 656 bytes.
  Spec: wte/re/spec/MainForm.grabar_camisetaClick.md

  EXTRAI o uniforme 3D do time para um arquivo. Nao grava na imagem: a ROM sai
  intacta, e o unico `fopen` de escrita e o do destino, em `"wb"`. O enunciado
  da WTE-TASK-29 dizia o contrario ate 2026-08-20.

  E o INVERSO EXATO do `boton_tex2isoClick`: os dois calculam o endereco com a
  mesma expressao, literal a literal, e o que muda e a direcao. Por isso as
  constantes sao as mesmas -- `TEXTURA_BASE` e `TEXTURA_BYTES_POR_TIME`, do
  `.aux.inc`.

  O QUE NAO E ARITMETICA E O TAMANHO. Todo o resto do enderecamento e
  constante; o tamanho sao dois bytes lidos em `offset + 44`, little-endian,
  MAIS 32. O `+ 32` diz que o campo conta o corpo e nao o cabecalho de 32 bytes
  que o precede. Somar 0 emitiria um arquivo 32 bytes curto, e ler o campo como
  32 bits leria lixo -- os dois erros dao arquivo plausivel com tamanho errado.

  OS DOIS LACOS. O primeiro copia payload inteiro e salta os 304 bytes de
  cabecalho e EDC/ECC de cada setor; o segundo copia o resto, `tamanho mod
  2048`, e nao precisa de salto nenhum -- o primeiro deixou o ponteiro no
  comeco do payload seguinte, e o resto sempre cabe la. }
var
  destino: string;
  indice: Integer;
  offset: TOffset;
  img: TCdImage;
  saida: TFileStream;
  buffer: array[0..SETOR_DADOS - 1] of Byte;
  cabecalho: array[0..1] of Byte;
  tamanho, blocos, resto, i: LongInt;
begin
  REMark('MainForm.grabar_camisetaClick');
  indice := lista_equipos.ItemIndex;
  if (ImagemAberta = '') or (indice < 0) then
    Exit;

  repeat
    { A afordancia de harness, irma do `WTE_MCR`. Ver `UniformeDestino`. }
    if UniformeDestino <> '' then
    begin
      destino := UniformeDestino;
      Break;
    end;
    if not dialogo_grabar_camiseta.Execute then
      Exit;
    destino := dialogo_grabar_camiseta.FileName;
    if destino <> dialogo_tex.FileName then
      Break;
    { A recusa e contra o dialogo de IMPORTAR textura, nao contra o de gravar:
      gravar por cima da fonte que o editor tem aberta a apagaria. }
    ficha_error2.etiq1.Caption :=
      'That file name is already being used by Team Editor';
    ficha_error2.ShowModal;
  until False;

  offset := TEXTURA_BASE
          + TEXTURA_BYTES_POR_TIME * (indice + 9 * (indice div IDX_MODELO_ML));

  img.Init;
  if not img.OpenRead(ImagemAberta) then
    Exit;
  try
    { O tamanho, antes de qualquer copia: le os dois bytes e VOLTA. }
    img.Seek(offset + 44, soBeginning);
    if img.Read(cabecalho, 2) <> 2 then
      Exit;
    tamanho := LongInt(cabecalho[0]) + LongInt(cabecalho[1]) * 256 + 32;

    saida := nil;
    try
      saida := TFileStream.Create(destino, fmCreate);
    except
      saida := nil;
    end;
    if saida = nil then
      Exit;
    try
      img.Seek(offset, soBeginning);
      blocos := tamanho div SETOR_DADOS;
      resto := tamanho mod SETOR_DADOS;
      for i := 1 to blocos do
      begin
        if img.Read(buffer, SETOR_DADOS) <> SETOR_DADOS then
          Exit;
        saida.WriteBuffer(buffer, SETOR_DADOS);
        img.Seek(SETOR_BYTES - SETOR_DADOS, soCurrent);
      end;
      if resto > 0 then
      begin
        if img.Read(buffer, resto) <> resto then
          Exit;
        saida.WriteBuffer(buffer, resto);
      end;
    finally
      saida.Free;
    end;
  finally
    img.Close;
  end;

  ficha_info3.etiq1.Caption := 'O uni foi salvo!!!.     ';
  ficha_info3.ShowModal;
end;
