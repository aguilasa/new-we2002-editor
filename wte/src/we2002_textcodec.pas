{ GERADO por wte/tools/port_database_pas.py -- NAO editar a mao.

  Transpilado de src/core/include/we2002/TextCodec.hpp, src/core/TextCodec.cpp, que ja e byte-identico ao `ed.exe` nas duas ROMs.
  A entrada do transpilador e SEMPRE codigo deste repositorio -- nunca saida de
  decompilador (PLAN-WTE-LAZARUS §8.10).

  Os seeks, os comprimentos de leitura e os limites de laco estao intocados:
  eles codificam o layout MODE2/2352 da imagem, inclusive os saltos manuais
  sobre cabecalho de setor.

  Os trechos marcados PORTE A MAO nao sao transpilacao: sao decisao ja escrita
  em wte/re/tipos.md, com a rota registrada em wte/re/recusas.md.

  Regenerar:  python3 wte/tools/port_database_pas.py
  Conferir:   python3 wte/tools/port_database_pas.py --check }

unit we2002_textcodec;

{$mode objfpc}{$H+}
{$modeswitch advancedrecords}
{$POINTERMATH ON}  { `lk[0]` sobre PByte, como no C++ }

interface

/// Convert ASCII to the game's two-byte Shift-JIS-like encoding.
///
/// `l` is the ASCII length *including* the terminating NUL, matching the
/// TEAM_NAME_KANJI_LEN table. `kj` must have room for `l * 2` bytes.
///
/// Only A-Z, a-z, 0-9 and '.' round-trip; everything else becomes a
/// full-width space. That lossiness is original behaviour and the golden
/// tests depend on it.
procedure AsciiToKanji(as_: PByte; kj: PByte; l: LongInt);
/// Inverse of AsciiToKanji. `as` must have room for `l` bytes.
procedure KanjiToAscii(kj: PByte; as_: PByte; l: LongInt);

implementation

procedure AsciiToKanji(as_: PByte; kj: PByte; l: LongInt);
var
  i: LongInt;
begin
  i := 0;
  while i < l - 1 do
  begin
    // lettere maiuscole
    if (as_[i] > 64)  and  (as_[i] < 91) then
    begin
      kj[i * 2] := 130;
      // 31 = 96-65, 96 = 0x(82)60 A in kanji, 65 = A in ascii
      kj[(i * 2) + 1] := as_[i] + 31;
      // lettere minuscole
    end
    else
    begin
      if (as_[i] > 96)  and  (as_[i] < 123) then
      begin
        kj[i * 2] := 130;
        // 32 = 129-97, 129 = 0x(82)81 a in kanji, 97 = a in ascii
        kj[(i * 2) + 1] := as_[i] + 32;
        // digits
      end
      else
      begin
        if (as_[i] > 47)  and  (as_[i] < 58) then
        begin
          kj[i * 2] := 130;
          kj[(i * 2) + 1] := as_[i] + 31;
          // punto
        end
        else
        begin
          if as_[i] = 46 then
          begin
            kj[i * 2] := 129;
            kj[(i * 2) + 1] := 66;
            // null
          end
          else
          begin
            if as_[i] = 0 then
            begin
              kj[i * 2] := 0;
              kj[(i * 2) + 1] := 0;
              // default spazio
            end
            else
            begin
              kj[i * 2] := 130;
              kj[(i * 2) + 1] := 128;
            end;
          end;
        end;
      end;
    end;
    Inc(i);
  end;
  kj[i * 2] := 0;
  kj[(i * 2) + 1] := 0;
end;

procedure KanjiToAscii(kj: PByte; as_: PByte; l: LongInt);
var
  i: LongInt;
  aux: array[0..39] of ShortInt;
begin
  i := 0;
  while i < (l - 1) * 2 do
  begin
    // lettere maiuscole
    if (kj[i] = 130)  and  (kj[i + 1] > 95)  and  (kj[i + 1] < 122) then
    begin
      aux[i] := kj[i + 1] - 31;
      // lettere minuscole
    end
    else
    begin
      if (kj[i] = 130)  and  (kj[i + 1] > 128)  and  (kj[i + 1] < 155) then
      begin
        aux[i] := kj[i + 1] - 32;
        // digits
      end
      else
      begin
        if (kj[i] = 130)  and  (kj[i + 1] > 78)  and  (kj[i + 1] < 89) then
        begin
          aux[i] := kj[i + 1] - 31;
          // punto
        end
        else
        begin
          if (kj[i] = 129)  and  (kj[i + 1] = 66) then
          begin
            aux[i] := 46;
            // null
          end
          else
          begin
            if (kj[i] = 0)  and  (kj[i + 1] = 0) then
            begin
              aux[i] := 0;
              // default spazio
            end
            else
            begin
              aux[i] := 32;
            end;
          end;
        end;
      end;
    end;
    Inc(i, 2);
  end;
  i := 0;
  while i < l - 1 do
  begin
    as_[i] := aux[i * 2];
    Inc(i);
  end;
  as_[i] := 0;
end;

end.
