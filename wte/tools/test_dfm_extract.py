#!/usr/bin/env python3
"""Testes do `dfm_extract.py` -- stdlib pura, sem depender do `.exe`.

    python3 -m unittest discover wte/tools -p 'test_*.py'
    make -C wte test

Por que este arquivo existe
---------------------------

Dos 21 `TValueType`, os 18 formularios do `we-team-editor.exe` exercitam
**nove**: `vaList`, `vaInt8`, `vaInt16`, `vaString`, `vaIdent`, `vaFalse`,
`vaTrue`, `vaBinary` e `vaSet`. Os outros doze -- `vaNull`, `vaInt32`,
`vaExtended`, `vaLString`, `vaNil`, `vaCollection`, `vaSingle`, `vaCurrency`,
`vaDate`, `vaWString`, `vaInt64`, `vaUTF8String` -- nao ocorrem, e o byte de
flags de objeto (`ffInherited`, `ffChildPos`, `ffInline`) nao ocorre em
nenhum dos 459 objetos. Rodar o gerador sobre o `.exe` nao toca nada disso:
`--check` verde nao diz absolutamente nada sobre metade do decodificador.

Nem sobre as rotas de aborto, que sao o outro lado da mesma moeda -- a §8 do
plano chama o extrator que "parece completo" de furo principal da fase 1, e o
que separa completo de plausivel e justamente o caminho que aborta com offset
em vez de emitir saida parcial.

Os streams aqui sao montados em memoria, byte a byte, e o `.exe` nunca e
aberto: o teste roda num clone sem `we-team-editor/`.

Isto NAO e um gerador
---------------------

Nao aceita `--check` e nao entra na bateria do `make -C wte check` por
wildcard -- o Makefile filtra `tools/test_*.py` de `GENERATORS` e os roda pelo
alvo `test`, do qual `check` depende. Ver `wte/tools/README.md`.
"""

from __future__ import annotations

import hashlib
import math
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dfm_extract as d  # noqa: E402

# Offset ficticio do stream dentro do .exe. Nao e zero de proposito: todo
# aborto tem de somar a base ao deslocamento local, e com base zero um bug
# nessa soma passaria despercebido.
BASE = 4118


# ------------------------------------------------------- montagem do stream --


def s(text: str) -> bytes:
    """String curta do DFM: um byte de tamanho e os bytes ASCII."""
    raw = text.encode("ascii")
    return bytes([len(raw)]) + raw


def raw_short(raw: bytes) -> bytes:
    return bytes([len(raw)]) + raw


def typed_int(n: int) -> bytes:
    """Inteiro como `ReadInteger` espera: byte de tipo mais o valor."""
    if -128 <= n <= 127:
        return bytes([d.VA_INT8]) + struct.pack("<b", n)
    if -32768 <= n <= 32767:
        return bytes([d.VA_INT16]) + struct.pack("<h", n)
    return bytes([d.VA_INT32]) + struct.pack("<i", n)


def x87(value: float) -> bytes:
    """Codifica um double no extended de 80 bits, para casar com `extended()`."""
    if math.isinf(value):
        return (1 << 63).to_bytes(8, "little") + \
            struct.pack("<H", 0x7FFF | (0x8000 if value < 0 else 0))
    if math.isnan(value):
        return (3 << 62).to_bytes(8, "little") + struct.pack("<H", 0x7FFF)
    if value == 0.0:
        return b"\0" * 10
    mant, exp = math.frexp(abs(value))
    sign = 0x8000 if value < 0 else 0
    return int(mant * (1 << 64)).to_bytes(8, "little") + \
        struct.pack("<H", sign | (exp + 16382))


def obj(cls: str, name: str, props: bytes = b"", children: bytes = b"",
        flags: int | None = None, child_pos: int | None = None) -> bytes:
    """Um objeto DFM, com o prefixo de flags so quando `flags` e dado."""
    head = b""
    if flags is not None:
        head += bytes([0xF0 | flags])
        if flags & d.FF_CHILD_POS:
            head += typed_int(child_pos if child_pos is not None else 0)
    return head + s(cls) + s(name) + props + b"\0" + children + b"\0"


def stream(body: bytes) -> bytes:
    return b"TPF0" + body


def parse(data: bytes, form: str = "TEST"):
    return d.parse_form(form, BASE, data)


def render(data: bytes, form: str = "TEST") -> str:
    root, _blobs = parse(data, form)
    return d.render(root)


# --------------------------------------------------------- valores, um a um --
#
# (rotulo, TValueType exercitado, bytes do valor, texto esperado a direita do
# `=`). A cobertura dos 21 tipos e conferida por TestCobertura, que soma esta
# tabela ao vaNull das duas rotas dedicadas.

BLOB_BYTES = b"\x01\x02\x03\x04"
BLOB_SHA = hashlib.sha256(BLOB_BYTES).hexdigest()

VALUE_CASES: list[tuple[str, int, bytes, str]] = [
    ("lista", d.VA_LIST,
     bytes([d.VA_LIST]) + typed_int(1) + typed_int(2) + b"\0",
     "(\n    1\n    2)"),
    ("lista vazia", d.VA_LIST, bytes([d.VA_LIST]) + b"\0", "()"),
    ("int8", d.VA_INT8, bytes([d.VA_INT8]) + struct.pack("<b", -3), "-3"),
    ("int16", d.VA_INT16, bytes([d.VA_INT16]) + struct.pack("<h", 300), "300"),
    ("int32", d.VA_INT32, bytes([d.VA_INT32]) + struct.pack("<i", 100000),
     "100000"),
    ("extended", d.VA_EXTENDED, bytes([d.VA_EXTENDED]) + x87(2.5), "2.5"),
    ("extended inteiro", d.VA_EXTENDED, bytes([d.VA_EXTENDED]) + x87(-8.0),
     "-8"),
    ("extended infinito", d.VA_EXTENDED,
     bytes([d.VA_EXTENDED]) + x87(math.inf), "Inf"),
    ("extended -infinito", d.VA_EXTENDED,
     bytes([d.VA_EXTENDED]) + x87(-math.inf), "-Inf"),
    ("extended NaN", d.VA_EXTENDED,
     bytes([d.VA_EXTENDED]) + x87(math.nan), "NaN"),
    ("string", d.VA_STRING, bytes([d.VA_STRING]) + s("hi"), "'hi'"),
    ("string com aspa", d.VA_STRING, bytes([d.VA_STRING]) + s("it's"),
     "'it''s'"),
    ("string vazia", d.VA_STRING, bytes([d.VA_STRING]) + s(""), "''"),
    ("string com byte nao imprimivel", d.VA_STRING,
     bytes([d.VA_STRING]) + raw_short(b"a\r\nb"), "'a'#13#10'b'"),
    ("ident", d.VA_IDENT, bytes([d.VA_IDENT]) + s("clBtnFace"), "clBtnFace"),
    ("binario", d.VA_BINARY,
     bytes([d.VA_BINARY]) + struct.pack("<i", len(BLOB_BYTES)) + BLOB_BYTES,
     f"{{blob Form1.P.bin {len(BLOB_BYTES)} sha256:{BLOB_SHA}}}"),
    ("false", d.VA_FALSE, bytes([d.VA_FALSE]), "False"),
    ("true", d.VA_TRUE, bytes([d.VA_TRUE]), "True"),
    ("conjunto", d.VA_SET,
     bytes([d.VA_SET]) + s("fsBold") + s("fsItalic") + b"\0",
     "[fsBold, fsItalic]"),
    ("conjunto vazio", d.VA_SET, bytes([d.VA_SET]) + b"\0", "[]"),
    ("lstring", d.VA_LSTRING,
     bytes([d.VA_LSTRING]) + struct.pack("<i", 3) + b"abc", "'abc'"),
    ("nil", d.VA_NIL, bytes([d.VA_NIL]), "nil"),
    ("colecao com indice", d.VA_COLLECTION,
     bytes([d.VA_COLLECTION]) + typed_int(0) + bytes([d.VA_LIST])
     + s("Name") + bytes([d.VA_STRING]) + s("x") + b"\0" + b"\0",
     "<\n    item [0]\n      Name = 'x'\n    end>"),
    ("colecao sem indice", d.VA_COLLECTION,
     bytes([d.VA_COLLECTION]) + bytes([d.VA_LIST])
     + s("Name") + bytes([d.VA_STRING]) + s("y") + b"\0" + b"\0",
     "<\n    item\n      Name = 'y'\n    end>"),
    ("colecao vazia", d.VA_COLLECTION, bytes([d.VA_COLLECTION]) + b"\0", "<>"),
    ("single", d.VA_SINGLE,
     bytes([d.VA_SINGLE]) + struct.pack("<f", 1.5), "1.5"),
    ("single inteiro", d.VA_SINGLE,
     bytes([d.VA_SINGLE]) + struct.pack("<f", 3.0), "3"),
    ("currency", d.VA_CURRENCY,
     bytes([d.VA_CURRENCY]) + struct.pack("<q", 123400), "12.34"),
    ("date", d.VA_DATE, bytes([d.VA_DATE]) + struct.pack("<d", 1.5), "1.5"),
    ("wstring ascii", d.VA_WSTRING,
     bytes([d.VA_WSTRING]) + struct.pack("<i", 3) + "abc".encode("utf-16-le"),
     "'abc'"),
    ("int64", d.VA_INT64,
     bytes([d.VA_INT64]) + struct.pack("<q", 1099511627776), "1099511627776"),
    ("utf8string", d.VA_UTF8STRING,
     bytes([d.VA_UTF8STRING]) + struct.pack("<i", 2) + b"ok", "'ok'"),
]


class TestValores(unittest.TestCase):
    """Cada TValueType decodificado E impresso -- o texto e metade do contrato.

    Comparar so o valor de volta deixaria `quote()`, `fmt_float()` e
    `emit_value()` sem teste, e sao eles que decidem o que a fase 2 le.
    """

    def test_cada_tipo_decodifica_e_imprime(self):
        for label, _va, payload, expected in VALUE_CASES:
            with self.subTest(label):
                data = stream(obj("TForm1", "Form1", s("P") + payload))
                self.assertEqual(
                    render(data),
                    f"object Form1: TForm1\n  P = {expected}\nend\n")


class TestCobertura(unittest.TestCase):
    """Os 21 tipos, sem exceção -- o teste que impede a tabela de envelhecer."""

    def test_os_21_tipos_tem_caso(self):
        coberto = {va for _l, va, _p, _e in VALUE_CASES}
        # vaNull nunca e um valor: ele termina lista, propriedade e filho, e
        # como valor e uma das rotas de aborto. TestAbortos cobre as duas.
        coberto.add(d.VA_NULL)
        faltando = sorted(d.VA_NAMES[t] for t in range(21) if t not in coberto)
        self.assertEqual(faltando, [], f"TValueType sem caso: {faltando}")

    def test_os_tipos_ausentes_do_exe_estao_entre_os_cobertos(self):
        # Os que o .exe nao exercita sao a razao de ser deste arquivo.
        ausentes_do_exe = {
            d.VA_NULL, d.VA_INT32, d.VA_EXTENDED, d.VA_LSTRING, d.VA_NIL,
            d.VA_COLLECTION, d.VA_SINGLE, d.VA_CURRENCY, d.VA_DATE,
            d.VA_WSTRING, d.VA_INT64, d.VA_UTF8STRING,
        }
        coberto = {va for _l, va, _p, _e in VALUE_CASES} | {d.VA_NULL}
        self.assertTrue(ausentes_do_exe <= coberto)


class TestFlagsDeObjeto(unittest.TestCase):
    """O byte 0xFn nao ocorre nos 459 objetos do `.exe`.

    E ele que decide entre `object`, `inherited` e `inline` -- uma troca de
    constante aqui nao seria pega por nenhum formulario real.
    """

    def test_sem_flags_sai_object(self):
        self.assertEqual(render(stream(obj("TForm1", "Form1"))),
                         "object Form1: TForm1\nend\n")

    def test_ffinherited(self):
        data = stream(obj("TForm1", "Form1", flags=d.FF_INHERITED))
        self.assertEqual(render(data), "inherited Form1: TForm1\nend\n")

    def test_ffinline(self):
        data = stream(obj("TForm1", "Form1", flags=d.FF_INLINE))
        self.assertEqual(render(data), "inline Form1: TForm1\nend\n")

    def test_ffchildpos_traz_a_posicao(self):
        data = stream(obj("TForm1", "Form1", flags=d.FF_CHILD_POS,
                          child_pos=7))
        self.assertEqual(render(data), "object Form1: TForm1 [7]\nend\n")

    def test_ffchildpos_aceita_int32(self):
        data = stream(obj("TForm1", "Form1", flags=d.FF_CHILD_POS,
                          child_pos=70000))
        self.assertEqual(render(data), "object Form1: TForm1 [70000]\nend\n")

    def test_inherited_ganha_de_inline(self):
        data = stream(obj("TForm1", "Form1",
                          flags=d.FF_INHERITED | d.FF_INLINE))
        self.assertEqual(render(data), "inherited Form1: TForm1\nend\n")

    def test_inherited_com_posicao(self):
        data = stream(obj("TForm1", "Form1",
                          flags=d.FF_INHERITED | d.FF_CHILD_POS, child_pos=2))
        self.assertEqual(render(data), "inherited Form1: TForm1 [2]\nend\n")

    def test_objeto_sem_nome_sai_so_com_a_classe(self):
        self.assertEqual(render(stream(obj("TForm1", ""))),
                         "object TForm1\nend\n")


class TestAninhamento(unittest.TestCase):

    def test_filho_indenta_dois_espacos(self):
        child = obj("TButton", "Button1", s("Left") + typed_int(10))
        data = stream(obj("TForm1", "Form1", s("Top") + typed_int(1), child))
        self.assertEqual(
            render(data),
            "object Form1: TForm1\n"
            "  Top = 1\n"
            "  object Button1: TButton\n"
            "    Left = 10\n"
            "  end\n"
            "end\n")

    def test_lista_dentro_de_filho_usa_o_recuo_do_filho(self):
        child = obj("TPanel", "Panel1",
                    s("Items") + bytes([d.VA_LIST]) + typed_int(1) + b"\0")
        data = stream(obj("TForm1", "Form1", b"", child))
        self.assertEqual(
            render(data),
            "object Form1: TForm1\n"
            "  object Panel1: TPanel\n"
            "    Items = (\n"
            "      1)\n"
            "  end\n"
            "end\n")


class TestBlob(unittest.TestCase):

    def test_referencia_traz_nome_tamanho_e_sha256(self):
        # `Icon.Data` e um unico nome de propriedade, com ponto -- nao dois
        # niveis. O nome do arquivo junta o dono a ele.
        data = stream(obj(
            "TForm1", "Form1",
            s("Icon.Data") + bytes([d.VA_BINARY])
            + struct.pack("<i", len(BLOB_BYTES)) + BLOB_BYTES))
        root, blobs = parse(data)
        self.assertEqual([b.filename for b in blobs], ["Form1.Icon.Data.bin"])
        self.assertEqual(blobs[0].data, BLOB_BYTES)
        self.assertEqual(
            d.render(root),
            "object Form1: TForm1\n"
            f"  Icon.Data = {{blob Form1.Icon.Data.bin 4 "
            f"sha256:{BLOB_SHA}}}\n"
            "end\n")

    def test_dono_do_blob_e_o_objeto_que_o_contem(self):
        child = obj("TImage", "Image1",
                    s("Picture.Data") + bytes([d.VA_BINARY])
                    + struct.pack("<i", 1) + b"\xaa")
        _root, blobs = parse(stream(obj("TForm1", "Form1", b"", child)))
        self.assertEqual([b.filename for b in blobs],
                         ["Image1.Picture.Data.bin"])

    def test_blob_dentro_de_colecao_junta_as_duas_propriedades(self):
        # As duas pilhas do Reader existem por isto: o dono vem da de objetos,
        # o nome do arquivo da de propriedades. Numa unica pilha o dono sairia
        # repetido no nome.
        item = bytes([d.VA_LIST]) + s("Glyph.Data") + bytes([d.VA_BINARY]) \
            + struct.pack("<i", 1) + b"\xbb" + b"\0"
        data = stream(obj("TForm1", "Form1",
                          s("Items") + bytes([d.VA_COLLECTION]) + item + b"\0"))
        _root, blobs = parse(data)
        self.assertEqual([b.filename for b in blobs],
                         ["Form1.Items.Glyph.Data.bin"])


# --------------------------------------------------------------- os abortos --
#
# Toda rota confere o **offset absoluto** na mensagem, nao so que levantou
# DfmError: o offset e o que torna o aborto util, e e a primeira coisa que uma
# refatoracao quebra em silencio. Os offsets sao derivados do proprio prefixo
# do stream (`BASE + len(prefixo)`), nunca escritos a mao.


class TestAbortos(unittest.TestCase):

    def assertAborta(self, data: bytes, offset: int, trecho: str,
                     form: str = "TEST"):
        with self.assertRaises(d.DfmError) as ctx:
            parse(data, form)
        msg = str(ctx.exception)
        self.assertIn(f"+{offset} (0x{offset:x})", msg)
        self.assertIn(trecho, msg)
        return msg

    def test_tipo_desconhecido(self):
        prefix = stream(s("TForm1") + s("Form1") + s("Left"))
        msg = self.assertAborta(
            prefix + bytes([99]) + b"\0\0", BASE + len(prefix),
            "TValueType desconhecido: 99 (0x63)")
        # O rastro tem de dizer onde, nao so o que.
        self.assertIn("TEST: Form1 > Left:", msg)

    def test_tipo_desconhecido_no_limite_superior(self):
        prefix = stream(s("TForm1") + s("Form1") + s("P"))
        self.assertAborta(prefix + bytes([21]) + b"\0\0", BASE + len(prefix),
                          "TValueType desconhecido: 21 (0x15)")

    def test_vanull_como_valor(self):
        prefix = stream(s("TForm1") + s("Form1") + s("P"))
        self.assertAborta(prefix + bytes([d.VA_NULL]) + b"\0\0",
                          BASE + len(prefix),
                          "vaNull onde se esperava um valor")

    def test_fim_do_stream(self):
        prefix = stream(s("TForm1") + s("Form1") + s("Data")
                        + bytes([d.VA_BINARY]) + struct.pack("<i", 16))
        self.assertAborta(prefix + b"abc", BASE + len(prefix),
                          "fim do stream: pedidos 16 bytes, restam 3")

    def test_tamanho_negativo(self):
        prefix = stream(s("TForm1") + s("Form1") + s("Data")
                        + bytes([d.VA_LSTRING]) + struct.pack("<i", -1))
        self.assertAborta(prefix, BASE + len(prefix), "tamanho negativo (-1)")

    def test_fim_do_stream_ao_espiar(self):
        prefix = stream(s("TForm1") + s("Form1"))
        self.assertAborta(prefix, BASE + len(prefix),
                          "fim do stream ao espiar o proximo byte")

    def test_bytes_sobrando_depois_da_raiz(self):
        body = obj("TForm1", "Form1")
        self.assertAborta(stream(body) + b"\xde\xad",
                          BASE + len(stream(body)),
                          "sobraram 2 bytes depois do fim do formulario")

    def test_nome_de_propriedade_nao_ascii(self):
        prefix = stream(s("TForm1") + s("Form1"))
        nome = raw_short(b"Cap\xe7ao")
        self.assertAborta(
            prefix + nome + bytes([d.VA_TRUE]) + b"\0\0",
            BASE + len(prefix) + len(nome),
            "nome de propriedade com byte fora de ASCII imprimivel (0xe7)")

    def test_nome_de_classe_nao_ascii(self):
        prefix = stream(b"")
        cls = raw_short(b"TFor\xe7a")
        self.assertAborta(prefix + cls + s("Form1") + b"\0\0",
                          BASE + len(prefix) + len(cls),
                          "nome de classe com byte fora de ASCII imprimivel")

    def test_nome_de_objeto_nao_ascii(self):
        prefix = stream(s("TForm1"))
        nome = raw_short(b"For\xe7a")
        self.assertAborta(prefix + nome + b"\0\0",
                          BASE + len(prefix) + len(nome),
                          "nome de objeto com byte fora de ASCII imprimivel")

    def test_identificador_nao_ascii(self):
        prefix = stream(s("TForm1") + s("Form1") + s("Color")
                        + bytes([d.VA_IDENT]))
        ident = raw_short(b"cl\xe7x")
        self.assertAborta(prefix + ident + b"\0\0",
                          BASE + len(prefix) + len(ident),
                          "identificador com byte fora de ASCII imprimivel")

    def test_elemento_de_conjunto_nao_ascii(self):
        prefix = stream(s("TForm1") + s("Form1") + s("Style")
                        + bytes([d.VA_SET]))
        elem = raw_short(b"fs\xe7B")
        self.assertAborta(prefix + elem + b"\0\0\0",
                          BASE + len(prefix) + len(elem),
                          "elemento de conjunto com byte fora de ASCII")

    def test_wstring_nao_ascii(self):
        prefix = stream(s("TForm1") + s("Form1") + s("W"))
        # A forma textual de UTF-16 fora de ASCII nao foi decidida -- o
        # decodificador aborta em vez de inventar um escape plausivel.
        payload = bytes([d.VA_WSTRING]) + struct.pack("<i", 1) \
            + "ç".encode("utf-16-le")
        self.assertAborta(prefix + payload + b"\0\0", BASE + len(prefix),
                          "vaWString com caractere fora de ASCII imprimivel "
                          "(U+00E7)")

    def test_esperado_inteiro_no_child_pos(self):
        prefix = stream(bytes([0xF0 | d.FF_CHILD_POS]))
        self.assertAborta(prefix + bytes([d.VA_TRUE]) + s("TForm1")
                          + s("Form1") + b"\0\0",
                          BASE + len(prefix),
                          "esperado inteiro, veio vaTrue")

    def test_item_de_colecao_sem_valist(self):
        prefix = stream(s("TForm1") + s("Form1") + s("Items")
                        + bytes([d.VA_COLLECTION]) + typed_int(0))
        self.assertAborta(
            prefix + bytes([d.VA_TRUE]) + b"\0\0\0", BASE + len(prefix),
            "esperado vaList abrindo o item da colecao, veio vaTrue")

    def test_magica_tpf0_ausente(self):
        with self.assertRaises(d.DfmError) as ctx:
            parse(b"XXXX" + obj("TForm1", "Form1"))
        msg = str(ctx.exception)
        self.assertIn(f"+{BASE} (0x{BASE:x})", msg)
        self.assertIn("esperado 'TPF0'", msg)

    def test_blob_duplicado(self):
        primeiro = s("Data") + bytes([d.VA_BINARY]) + struct.pack("<i", 1) \
            + b"\x01"
        prefix = stream(s("TForm1") + s("Form1") + primeiro
                        + s("Data") + bytes([d.VA_BINARY])
                        + struct.pack("<i", 1) + b"\x02")
        # O aborto e no fim do segundo blob: e ali que o nome ja esta formado.
        self.assertAborta(prefix + b"\0\0", BASE + len(prefix),
                          "dois blobs disputam o arquivo Form1.Data.bin")

    def test_blob_duplicado_ignora_caixa(self):
        primeiro = s("Data") + bytes([d.VA_BINARY]) + struct.pack("<i", 1) \
            + b"\x01"
        prefix = stream(s("TForm1") + s("Form1") + primeiro
                        + s("DATA") + bytes([d.VA_BINARY])
                        + struct.pack("<i", 1) + b"\x02")
        self.assertAborta(prefix + b"\0\0", BASE + len(prefix),
                          "dois blobs disputam o arquivo Form1.DATA.bin")


# ------------------------------------------------------------ PE sintetico ---
#
# A colisao de nome de formulario mora em `generate()`, que le o `.exe`. Para
# exercita-la sem o binario do Obocaman, monta-se aqui o PE32 minimo que
# `read_rcdata` sabe ler -- o que tambem poe os abortos do leitor de PE sob
# teste, que nenhum outro caminho alcanca.


def synth_pe(resources: list[tuple[str, bytes]]) -> bytes:
    """PE32 minimo com `resources` como RT_RCDATA, um idioma cada."""
    sec_va, sec_raw = 0x1000, 0x400
    n = len(resources)

    root_dir = 0
    type_dir = root_dir + 16 + 8
    name_dirs = type_dir + 16 + 8 * n
    name_dir_size = 16 + 8
    data_entries = name_dirs + n * name_dir_size
    strings = data_entries + n * 16

    blob = bytearray()
    str_offsets, str_area = [], bytearray()
    for name, _data in resources:
        str_offsets.append(strings + len(str_area))
        str_area += struct.pack("<H", len(name)) + name.encode("utf-16-le")
    payload_at = strings + len(str_area)

    def directory(entries: list[tuple[int, int]], named: int) -> bytes:
        out = struct.pack("<IIHHHH", 0, 0, 0, 0, named, len(entries) - named)
        for name_field, data_field in entries:
            out += struct.pack("<II", name_field, data_field)
        return out

    # nivel 1: o tipo RT_RCDATA aponta para o diretorio de nomes
    blob += directory([(d.RT_RCDATA, 0x80000000 | type_dir)], named=0)
    # nivel 2: um nome por recurso, cada um apontando para o seu de idioma
    blob += directory(
        [(0x80000000 | str_offsets[i], 0x80000000 | (name_dirs + i * name_dir_size))
         for i in range(n)], named=n)
    # nivel 3: um idioma por recurso, folha, apontando para a entrada de dados
    for i in range(n):
        blob += directory([(0x409, data_entries + i * 16)], named=0)
    # entradas de dados
    cursor = payload_at
    for _name, data in resources:
        blob += struct.pack("<IIII", sec_va + cursor, len(data), 0, 0)
        cursor += len(data)
    blob += str_area
    for _name, data in resources:
        blob += data

    opt = struct.pack("<H", 0x10B) + b"\0" * 90 + struct.pack("<I", 16)
    opt += b"\0" * 8 * 2                             # export, import
    opt += struct.pack("<II", sec_va, len(blob))     # resource
    opt += b"\0" * 8 * 13
    section = (b".rsrc\0\0\0" + struct.pack("<IIII", len(blob), sec_va,
                                            len(blob), sec_raw) + b"\0" * 16)
    coff = struct.pack("<HHIIIHH", 0x14C, 1, 0, 0, 0, len(opt), 0x102)

    head = bytearray(b"MZ" + b"\0" * 0x3E)
    struct.pack_into("<I", head, 0x3C, 0x40)
    head += b"PE\0\0" + coff + opt + section
    return bytes(head).ljust(sec_raw, b"\0") + blob


class TestPeSintetico(unittest.TestCase):

    def exe_com(self, resources: list[tuple[str, bytes]]):
        """Aponta `d.EXE` para um PE temporario; devolve o resultado do fim."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sintetico.exe"
            path.write_bytes(synth_pe(resources))
            original = d.EXE
            d.EXE = path
            try:
                return d.generate()
            finally:
                d.EXE = original

    def test_read_rcdata_acha_os_recursos(self):
        blob = synth_pe([("TA", b"TPF0" + obj("TForm1", "A")),
                         ("TB", b"nao e formulario")])
        achados = d.read_rcdata(blob)
        self.assertEqual([n for n, _o, _b in achados], ["TA", "TB"])
        self.assertEqual(achados[1][2], b"nao e formulario")
        # O offset devolvido e o do arquivo: e ele que vira base dos abortos.
        nome, offset, data = achados[0]
        self.assertEqual(blob[offset:offset + len(data)], data)

    def test_colisao_de_nome_de_formulario(self):
        with self.assertRaises(d.DfmError) as ctx:
            self.exe_com([("TA", b"TPF0" + obj("TFormA", "Form1")),
                          ("TB", b"TPF0" + obj("TFormB", "Form1"))])
        # Sem offset: a colisao e entre dois streams, nao dentro de um.
        self.assertIn("o formulario 'Form1' colide com 'Form1'",
                      str(ctx.exception))

    def test_colisao_ignora_caixa(self):
        with self.assertRaises(d.DfmError) as ctx:
            self.exe_com([("TA", b"TPF0" + obj("TFormA", "Form1")),
                          ("TB", b"TPF0" + obj("TFormB", "FORM1"))])
        self.assertIn("colide com", str(ctx.exception))

    def test_conta_dezoito_formularios(self):
        with self.assertRaises(d.DfmError) as ctx:
            self.exe_com([("TA", b"TPF0" + obj("TFormA", "Form1"))])
        self.assertIn("esperados 18 formularios TPF0 em RT_RCDATA, achados 1",
                      str(ctx.exception))

    def test_exe_ausente_diz_o_que_falta(self):
        original = d.EXE
        d.EXE = Path("/nao/existe/we-team-editor.exe")
        try:
            with self.assertRaises(d.DfmError) as ctx:
                d.generate()
        finally:
            d.EXE = original
        self.assertIn("nao existe", str(ctx.exception))

    def test_sem_mz(self):
        with self.assertRaises(d.DfmError) as ctx:
            d.read_rcdata(b"ZZ" + b"\0" * 200)
        self.assertIn("nao comeca com 'MZ'", str(ctx.exception))

    def test_sem_assinatura_pe(self):
        blob = bytearray(synth_pe([("TA", b"x")]))
        blob[0x40:0x44] = b"XX\0\0"
        with self.assertRaises(d.DfmError) as ctx:
            d.read_rcdata(bytes(blob))
        self.assertIn("assinatura PE ausente", str(ctx.exception))

    def test_recusa_pe32_mais(self):
        blob = bytearray(synth_pe([("TA", b"x")]))
        struct.pack_into("<H", blob, 0x40 + 4 + 20, 0x20B)
        with self.assertRaises(d.DfmError) as ctx:
            d.read_rcdata(bytes(blob))
        self.assertIn("esperado PE32 (0x10b), veio 0x20b", str(ctx.exception))


class TestSaidaAscii(unittest.TestCase):

    def test_render_recusa_saida_nao_ascii(self):
        # `render()` e a ultima linha de defesa: se algum dia um valor chegar
        # com byte alto, ele para em vez de escrever um .dfm que a fase 2 leria
        # com a codificacao errada.
        root = d.Obj("TForm1", "Form1", 0, None)
        root.props.append(("P", d.Ident("café")))
        with self.assertRaises(d.DfmError) as ctx:
            d.render(root)
        self.assertIn("deixou de ser ASCII", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
