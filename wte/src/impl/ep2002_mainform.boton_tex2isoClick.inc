{ MainForm.boton_tex2isoClick -- 0x0040de18, 460 bytes.
  Spec: wte/re/spec/MainForm.boton_tex2isoClick.md

  Copia o arquivo de textura escolhido para dentro da imagem: VINTE setores por
  time, sempre os vinte. Quando a fonte acaba antes, o resto do bloco corrente e
  os blocos que sobram vao a zero -- nao ficam com o conteudo velho.

  O endereco e aritmetica pura, sem varredura e sem tabela:

      offset = 19756824 + 47040 * (indice + 9 * (indice div 95))

  19756824 = 8400 * 2352 + 24, o primeiro byte de dados do setor 8400; 47040 =
  20 * 2352. O termo `9 * (indice div 95)` so tem efeito no item 95 do combo, o
  time-modelo da Master League.

  A gravacao passa pelo FLUXO, entao o salto de 304 bytes entre setores sai de
  graca -- e no original ele e explicito, um `fseek(+0x130)` no fim de cada
  bloco. }
var
  indice, bloco: Integer;
  offset: TOffset;
  img: TCdImage;
  origem: TFileStream;
  buffer: array[0..SETOR_DADOS - 1] of Byte;
  lidos: SizeInt;
  acabou: Boolean;
begin
  REMark('MainForm.boton_tex2isoClick');
  if (ImagemAberta = '') or (TexturaEscolhida = '') then
    Exit;

  indice := lista_equipos.ItemIndex;
  if indice < 0 then
    Exit;
  offset := TEXTURA_BASE
          + TEXTURA_BYTES_POR_TIME * (indice + 9 * (indice div IDX_MODELO_ML));

  img.Init;
  if not img.OpenReadWrite(ImagemAberta) then
    Exit;
  try
    origem := nil;
    try
      origem := TFileStream.Create(TexturaEscolhida,
                                   fmOpenRead or fmShareDenyNone);
    except
      origem := nil;
    end;
    if origem = nil then
      Exit;
    try
      img.Seek(offset, soBeginning);
      acabou := False;
      for bloco := 1 to TEXTURA_SETORES do
      begin
        FillChar(buffer, SizeOf(buffer), 0);
        lidos := 0;
        if not acabou then
        begin
          lidos := origem.Read(buffer, SizeOf(buffer));
          if lidos < SizeOf(buffer) then
            acabou := True;
        end;
        { O bloco inteiro vai para a imagem, com ou sem fonte: o que sobra e
          zero. Escrever so `lidos` deixaria o rabo do setor com a textura
          anterior, e o original nao deixa. }
        img.Write(buffer, SizeOf(buffer));
        img.Seek(SETOR_BYTES - SETOR_DADOS, soCurrent);
      end;
    finally
      origem.Free;
    end;
  finally
    img.Close;
  end;

  ficha_info3.etiq1.Caption := 'Textura inserida no jogo!!!';
  ficha_info3.ShowModal;
end;
