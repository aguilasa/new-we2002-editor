#!/usr/bin/env python3
"""Testes do compare_dumps.py -- WTE-TASK-20.

Tres grupos:

1. **o comparador de bytes**, com arquivo plantado. Ele produz os numeros que
   o `fase-3.md` publica sobre gravacao; contar faixa errada ali faria a
   ressalva das all-star parecer maior ou menor do que e;
2. **os dois dumpers como par** -- o que da para conferir sem compilar: mesma
   versao de formato e mesmo verbo `--roundtrip` nos dois. Um lado sem o outro
   nao seria pego pelo `diff`, seria pego por um traceback;
3. **a evidencia commitada** -- o `fase-3.tsv` tem de dizer zero divergencia
   nas duas metades, senao a fase 3 nao fechou.

A **remedicao completa** (compilar, copiar 1,9 GB, rodar) fica sob
`WTE_ROUNDTRIP=1`, e nao no caminho normal: `make -C wte test` roda em
segundos e tem de continuar assim. Sem a variavel o grupo 4 **pula** e diz o
que deixou de medir, em vez de passar em silencio.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import compare_dumps as C

PAS = C.TESTES / "dump_estado.pas"
CPP = C.TESTES / "dump_estado.cpp"


class TestComparadorDeBytes(unittest.TestCase):

    def faixas(self, a: bytes, b: bytes):
        with tempfile.TemporaryDirectory() as d:
            pa, pb = Path(d) / "a", Path(d) / "b"
            pa.write_bytes(a)
            pb.write_bytes(b)
            return C.faixas_diferentes(pa, pb)

    def test_iguais_nao_tem_faixa(self) -> None:
        self.assertEqual(self.faixas(b"\x00" * 100, b"\x00" * 100), (0, 0))

    def test_bytes_vizinhos_sao_uma_faixa(self) -> None:
        a = bytearray(100)
        b = bytearray(100)
        b[10] = 1
        b[11] = 1
        self.assertEqual(self.faixas(bytes(a), bytes(b)), (1, 2))

    def test_folga_de_16_une(self) -> None:
        # Mesmo criterio do diff_dirigido.sh, para que os dois numeros sejam
        # comparaveis entre as duas ferramentas.
        a = bytearray(100)
        b = bytearray(100)
        b[10] = 1
        b[26] = 1  # exatamente 16 depois: ainda a mesma faixa
        self.assertEqual(self.faixas(bytes(a), bytes(b)), (1, 2))

    def test_folga_de_17_separa(self) -> None:
        a = bytearray(100)
        b = bytearray(100)
        b[10] = 1
        b[27] = 1
        self.assertEqual(self.faixas(bytes(a), bytes(b)), (2, 2))


class TestOParDeDumpers(unittest.TestCase):
    """O que da para conferir nos dois fontes sem compilar nada."""

    def test_a_mesma_versao_de_formato(self) -> None:
        marca = "we2002-state v1"
        self.assertIn(marca, PAS.read_text(encoding="utf-8"))
        self.assertIn(marca, CPP.read_text(encoding="utf-8"))

    def test_os_dois_aceitam_roundtrip(self) -> None:
        # A metade de gravacao do aceite depende do verbo existir dos dois
        # lados; se so um tiver, o `--medir` morre com CalledProcessError e a
        # causa fica escondida no stderr capturado.
        self.assertIn("--roundtrip", PAS.read_text(encoding="utf-8"))
        self.assertIn("--roundtrip", CPP.read_text(encoding="utf-8"))

    def test_o_cpp_nao_puxa_sofifa(self) -> None:
        # Sofifa.cpp e o unico do nucleo que exige libcurl. Entrar na lista
        # faria o dumper deixar de compilar numa maquina sem a lib, por nada:
        # nenhum campo despejado vem dele.
        self.assertNotIn("Sofifa.cpp", C.FONTES_CPP)


REAL = C.OUT_TSV.exists()


@unittest.skipUnless(REAL, "sem wte/re/fase-3.tsv -- rode --medir")
class TestEvidencia(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.linhas = C.ler_tsv()

    def test_as_duas_roms_foram_medidas(self) -> None:
        # Uma ROM so nao fecha a fase 3: a europeia cobre os ramos de
        # mapeamento do codec e a japonesa cobre o ramo padrao.
        self.assertEqual({r["rom"] for r in self.linhas},
                         {nome for nome, _a, _v in C.ROMS})

    def test_leitura_sem_divergencia(self) -> None:
        for r in self.linhas:
            self.assertEqual(r["divergencias_dump"], "0", r["rom"])

    def test_gravacao_sem_divergencia(self) -> None:
        for r in self.linhas:
            self.assertEqual(r["divergencias_rt_pascal_vs_cpp"], "0", r["rom"])

    def test_o_roundtrip_mexeu_na_imagem(self) -> None:
        """Zero contra zero nao prova nada.

        `Load`+`Save` sem editar **tem** de mudar bytes -- o Save reconstroi as
        all-star e troca os cobradores de ML. Se esta coluna zerar, ou o Save
        parou de gravar, ou a medicao comparou o arquivo consigo mesmo, e a
        linha de cima passaria verde do mesmo jeito.
        """
        for r in self.linhas:
            self.assertGreater(int(r["bytes_rt_vs_original"]), 0, r["rom"])

    def test_o_sidecar_saiu_dos_dois_lados_igual(self) -> None:
        for r in self.linhas:
            self.assertEqual(r["sidecar_igual"], "sim", r["rom"])
            # 1.911 linhas em branco -- decisao 5 do tipos.md, em bytes.
            self.assertEqual(int(r["sidecar_bytes"]), 1911, r["rom"])

    def test_o_dado_exercitado_nao_e_trivial(self) -> None:
        for r in self.linhas:
            self.assertGreater(int(r["squad_numbers_nao_zero"]), 0, r["rom"])
            self.assertGreater(int(r["kanji_duplo"]), 0, r["rom"])

    def test_a_premissa_do_codec_esta_invertida(self) -> None:
        """Achado da execucao, preso em teste.

        O enunciado da task diz que a japonesa e o unico teste real do codec.
        Medido, quem exercita os ramos de mapeamento e a EUROPEIA -- a
        japonesa guarda katakana (`0x83`), que o `KanjiToAscii` nao conhece e
        transforma em espaco. Se isto se inverter de novo, o `fase-3.md` passa
        a afirmar o contrario do que foi medido.
        """
        por_rom = {r["rom"]: r for r in self.linhas}
        self.assertGreater(int(por_rom["european-deluxe"]["kanji_decodificado"]), 0)
        self.assertEqual(int(por_rom["japanese"]["kanji_decodificado"]), 0)

    def test_o_gerado_esta_em_dia(self) -> None:
        self.assertEqual(C.OUT_MD.read_text(encoding="utf-8"), C.gerar())


@unittest.skipUnless(os.environ.get("WTE_ROUNDTRIP") == "1",
                     "remedicao completa: ~1,9 GB de copia e dois "
                     "compiladores. Rode com WTE_ROUNDTRIP=1")
class TestRemedicao(unittest.TestCase):

    def test_medir_reproduz_a_evidencia(self) -> None:
        antes = C.OUT_TSV.read_text(encoding="utf-8") if REAL else None
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(C.medir(Path(d)), 0)
        if antes is not None:
            self.assertEqual(C.OUT_TSV.read_text(encoding="utf-8"), antes)


if __name__ == "__main__":
    unittest.main()
