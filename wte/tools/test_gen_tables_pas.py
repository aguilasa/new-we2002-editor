#!/usr/bin/env python3
"""Testes do gen_tables_pas.py -- WTE-TASK-16.

Dois grupos, e o segundo e o que a task exige por escrito:

1. **Recusa com entrada plantada.** Cada construcao que o gerador nao sabe
   traduzir tem de abortar com arquivo, linha e motivo -- nunca emitir numero
   plausivel e errado.

2. **Os valores conferidos por dois compiladores.** `wte/tests/test_offsets.pas`
   e `wte/tests/test_offsets.cpp` emitem as mesmas linhas; um le o Pascal
   gerado, o outro le o C++ original. Comparar a saida do gerador contra o
   proprio parser do gerador nao provaria nada -- um erro de leitura de literal
   apareceria identico dos dois lados.

O grupo 2 precisa de `fpc` e de `g++`. Sem eles o teste **pula** e diz o que
deixou de medir, em vez de passar em silencio.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

import gen_tables_pas as G


def write(tmp: Path, name: str, text: str) -> Path:
    p = tmp / name
    p.write_text(textwrap.dedent(text), encoding="utf-8")
    return p


class TestRecusa(unittest.TestCase):
    """Entrada plantada: o gerador tem de recusar, com a linha certa."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    # -- Offsets.hpp ---------------------------------------------------------

    def test_constexpr_com_expressao(self) -> None:
        p = write(self.tmp, "Offsets.hpp", """\
            inline constexpr Offset OFS_A = 100;
            inline constexpr Offset OFS_B = 100 + 2352;
            """)
        with self.assertRaises(G.GenError) as ctx:
            G.parse_offsets(p)
        self.assertIn("Offsets.hpp:2", str(ctx.exception))

    def test_constexpr_com_sufixo(self) -> None:
        p = write(self.tmp, "Offsets.hpp", """\
            inline constexpr Offset OFS_A = 100LL;
            """)
        with self.assertRaises(G.GenError):
            G.parse_offsets(p)

    def test_offsets_vazio(self) -> None:
        p = write(self.tmp, "Offsets.hpp", "// nada aqui\n")
        with self.assertRaises(G.GenError):
            G.parse_offsets(p)

    def test_comentario_de_bloco_nao_desloca_a_linha(self) -> None:
        p = write(self.tmp, "Offsets.hpp", """\
            /* duas
               linhas */
            inline constexpr Offset OFS_A = 1 << 3;
            """)
        with self.assertRaises(G.GenError) as ctx:
            G.parse_offsets(p)
        self.assertIn("Offsets.hpp:3", str(ctx.exception))

    # -- Tables.cpp ----------------------------------------------------------

    def _tables(self, hpp: str, cpp: str):
        h = write(self.tmp, "Tables.hpp", hpp)
        c = write(self.tmp, "Tables.cpp", cpp)
        decls, consts, order = G.parse_tables_hpp(h)
        return G.parse_tables_cpp(c, decls, {x.name: x.value for x in consts}), order

    def test_definicao_nao_declarada_aborta(self) -> None:
        with self.assertRaises(G.GenError) as ctx:
            self._tables(
                "extern const char T[3];\n",
                "const char T[3] =\n{\n1,2,3\n};\n\n"
                "const char INTRUSO[2] =\n{\n1,2\n};\n")
        self.assertIn("INTRUSO", str(ctx.exception))
        self.assertIn("UNDECLARED_OK", str(ctx.exception))

    def test_definicao_na_lista_de_excecao_e_ignorada(self) -> None:
        tables, order = self._tables(
            "extern const char T[3];\n",
            "const char T[3] =\n{\n1,2,3\n};\n\n"
            "char nomi_squadre[1][2] =\n{\n\"a\"\n};\n")
        self.assertEqual(list(tables), ["T"])
        self.assertEqual(order, ["T"])

    def test_contagem_diferente_da_dimensao(self) -> None:
        with self.assertRaises(G.GenError) as ctx:
            self._tables("extern const char T[3];\n",
                         "const char T[3] =\n{\n1,2,3,4\n};\n")
        self.assertIn("declarado com 3", str(ctx.exception))

    def test_inicializador_misturado(self) -> None:
        with self.assertRaises(G.GenError) as ctx:
            self._tables("extern const char T[2][4];\n",
                         "const char T[2][4] =\n{\n\"ab\",7\n};\n")
        self.assertIn("mistura", str(ctx.exception))

    def test_elemento_irreconhecivel(self) -> None:
        with self.assertRaises(G.GenError) as ctx:
            self._tables("extern const int T[2];\n",
                         "const int T[2] =\n{\n1,\n0x2\n};\n")
        # A linha tem de ser a do elemento (4), nao a do cabecalho (1): a
        # mensagem existe para levar direto ao literal.
        self.assertIn("Tables.cpp:4", str(ctx.exception))

    def test_literal_nao_cabe_na_dimensao(self) -> None:
        with self.assertRaises(G.GenError) as ctx:
            self._tables("extern const char T[1][3];\n",
                         "const char T[1][3] =\n{\n\"abcd\"\n};\n")
        self.assertIn("nao cabe", str(ctx.exception))

    def test_dimensao_por_constante_resolve(self) -> None:
        tables, _ = self._tables(
            "inline constexpr int N = 2;\nextern const char T[N][4];\n",
            "const char T[N][4] =\n{\n\"ab\",\n\"cd\"\n};\n")
        self.assertEqual(tables["T"].inner, 4)
        self.assertEqual(len(tables["T"].elements), 2)

    def test_dimensao_que_nao_resolve(self) -> None:
        with self.assertRaises(G.GenError) as ctx:
            self._tables("extern const char T[2][LARGURA];\n",
                         "const char T[2][LARGURA] =\n{\n\"ab\",\n\"cd\"\n};\n")
        self.assertIn("LARGURA", str(ctx.exception))

    def test_definicao_sem_const(self) -> None:
        with self.assertRaises(G.GenError) as ctx:
            self._tables("extern const char T[2];\n",
                         "char T[2] =\n{\n1,2\n};\n")
        self.assertIn("sem 'const'", str(ctx.exception))

    def test_declarada_e_sem_definicao(self) -> None:
        h = write(self.tmp, "Tables.hpp",
                  "extern const char T[2];\nextern const char U[2];\n")
        c = write(self.tmp, "Tables.cpp", "const char T[2] =\n{\n1,2\n};\n")
        decls, consts, order = G.parse_tables_hpp(h)
        tables = G.parse_tables_cpp(c, decls, {})
        missing = [n for n in order if n not in tables]
        self.assertEqual(missing, ["U"])


class TestEmissao(unittest.TestCase):
    """Forma da saida, sem compilar nada."""

    def test_chave_em_comentario_nao_fecha_o_bloco(self) -> None:
        # '}' num comentario `{ }` fecharia o comentario e o resto viraria
        # codigo. O escape e obrigatorio, nao cosmetico.
        self.assertNotIn("}", G.pascal_comment("std::map<int, int> m {};")[2:-2])

    def test_saida_e_deterministica(self) -> None:
        self.assertEqual(G.build(), G.build())

    def test_os_69_offsets(self) -> None:
        offsets = G.parse_offsets(G.OFFSETS_HPP)
        ofs = [c for c in offsets if c.name.startswith("OFS_")]
        self.assertEqual(len(ofs), 69)
        self.assertEqual(len(offsets) - len(ofs), 3)  # as 3 de setor
        self.assertEqual(len(set(c.name for c in offsets)), len(offsets))

    def test_as_16_tabelas(self) -> None:
        decls, _, order = G.parse_tables_hpp(G.TABLES_HPP)
        self.assertEqual(len(order), 16)
        self.assertEqual(len(decls), 16)


class TestDumpersConcordam(unittest.TestCase):
    """O gate da task: os 69 valores conferidos por dois compiladores."""

    def test_pascal_e_cpp_emitem_as_mesmas_linhas(self) -> None:
        fpc = shutil.which("fpc")
        gpp = shutil.which("g++")
        if not fpc or not gpp:
            self.skipTest(
                "sem fpc e/ou g++ -- os valores dos 69 offsets e das 16 "
                "tabelas NAO foram conferidos nesta execucao")

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            subprocess.run(
                [fpc, f"-Fu{G.ROOT / 'wte/src'}", f"-FU{tmp}",
                 f"-o{tmp / 'dump_pas'}", str(G.OUT_DUMP_PAS)],
                check=True, capture_output=True, text=True)
            subprocess.run(
                [gpp, "-std=c++17", f"-I{G.ROOT / 'src/core/include'}",
                 "-o", str(tmp / "dump_cpp"), str(G.OUT_DUMP_CPP),
                 str(G.ROOT / "src/core/Tables.cpp")],
                check=True, capture_output=True, text=True)

            pas = subprocess.run([str(tmp / "dump_pas")], check=True,
                                 capture_output=True, text=True).stdout
            cpp = subprocess.run([str(tmp / "dump_cpp")], check=True,
                                 capture_output=True, text=True).stdout

        self.assertTrue(pas.strip(), "o dumper Pascal nao emitiu nada")
        pas_lines = pas.splitlines()
        cpp_lines = cpp.splitlines()
        # Diferenca util na falha: a primeira linha divergente, nao 1383.
        for i, (a, b) in enumerate(zip(pas_lines, cpp_lines), 1):
            self.assertEqual(a, b, f"divergencia na linha {i}")
        self.assertEqual(len(pas_lines), len(cpp_lines))

        kinds = {ln.split("\t")[0] for ln in pas_lines}
        self.assertEqual(kinds, {"CONST", "NUM", "TXT"})


if __name__ == "__main__":
    unittest.main()
