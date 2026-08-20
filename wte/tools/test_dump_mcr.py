#!/usr/bin/env python3
"""Testes do dump_mcr.py -- WTE-TASK-28.

Tres grupos:

1. **O conteiner bate com a documentacao publica.** O molde tem de comecar com
   `MC`, ter 16 blocos de 8192, e o diretorio tem de descrever um save com nome
   e tamanho coerentes -- estado da cadeia, link, e tamanho igual ao numero de
   blocos vezes 8192.
2. **Os guards recusam com entrada plantada.** As duas tabelas que o script le
   do `.exe` sao conferidas contra o layout escrito; guard que nunca foi visto
   recusar e guard que se supoe funcionar.
3. **O achado do bloco 3 e verdade, nao redacao.** Os destinos de escrita caem
   em blocos que o diretorio nao declara inteiros, e o teste mede isso em vez
   de confiar na prosa.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import dump_mcr as M


class TestConteiner(unittest.TestCase):
    def setUp(self) -> None:
        if not M.DAT.is_file():
            self.skipTest(f"sem {M.REL_DAT} -- o conteiner NAO foi conferido")
        self.card = M.DAT.read_bytes()[:M.CARTAO_BYTES]
        self.dir = M.diretorio(self.card)

    def test_magica_e_tamanho(self) -> None:
        self.assertEqual(self.card[:2], b"MC")
        self.assertEqual(M.CARTAO_BYTES, 16 * M.BLOCO_BYTES)

    def test_o_diretorio_tem_quinze_quadros(self) -> None:
        self.assertEqual(len(self.dir), 15)

    def test_a_cadeia_do_save_e_coerente(self) -> None:
        usados = M.blocos_do_save(self.dir)
        self.assertTrue(usados, "nenhum bloco em uso no molde")
        # O primeiro da cadeia declara o tamanho total; os seguintes, zero.
        primeiro = self.dir[usados[0] - 1]
        self.assertEqual(primeiro["estado"], 0x51)
        self.assertEqual(primeiro["tamanho"], len(usados) * M.BLOCO_BYTES)
        self.assertEqual(self.dir[usados[-1] - 1]["estado"], 0x53)

    def test_o_save_e_o_do_we2002(self) -> None:
        self.assertIn("SLPM-86600", self.dir[0]["nome"])

    def test_o_resto_esta_livre(self) -> None:
        usados = set(M.blocos_do_save(self.dir))
        for d in self.dir:
            if d["bloco"] not in usados:
                self.assertEqual(d["estado"], 0xA0, f"bloco {d['bloco']}")


class TestGuards(unittest.TestCase):
    """As duas tabelas do `.exe` sao conferidas, e a recusa foi vista."""

    def setUp(self) -> None:
        if not M.EXE.is_file():
            self.skipTest(f"sem {M.REL_EXE} -- as tabelas NAO foram conferidas")
        self.blob = M.EXE.read_bytes()

    def test_a_tabela_de_cobradores_bate(self) -> None:
        self.assertEqual(M.le_dwords(self.blob, M.VA_TABELA_COBRADORES, 5),
                         M.COBRADORES_ESPERADOS)

    def test_a_tabela_de_bits_bate(self) -> None:
        self.assertEqual(M.le_dwords(self.blob, M.VA_TABELA_BITS, 6),
                         M.BITS_ESPERADOS)

    def test_os_bits_sao_a_formula_do_squadnumbers(self) -> None:
        # `(5 * (j mod 6)) mod 8` -- a mesma forma do we2002_core.
        self.assertEqual(M.BITS_ESPERADOS,
                         tuple((5 * j) % 8 for j in range(6)))

    def test_gera_recusa_com_exe_plantado(self) -> None:
        # Planta um `.exe` cujo VA pedido cai fora de toda secao: o leitor tem
        # de recusar em vez de devolver lixo.
        with self.assertRaises(M.McrError):
            M.le_dwords(self.blob, 0x7FFFFFFF, 1)

    def test_os_cinco_cobradores_nao_sao_crescentes(self) -> None:
        # E a razao de serem tabela e nao aritmetica. Se um dia virarem
        # crescentes, a prosa do markdown deixa de ser verdade.
        c = M.COBRADORES_ESPERADOS
        self.assertNotEqual(list(c), sorted(c))


class TestAchadoDoBloco3(unittest.TestCase):
    def setUp(self) -> None:
        if not M.DAT.is_file():
            self.skipTest(f"sem {M.REL_DAT}")
        self.card = M.DAT.read_bytes()[:M.CARTAO_BYTES]
        self.dir = M.diretorio(self.card)

    def test_ha_destino_fora_dos_blocos_declarados(self) -> None:
        usados = set(M.blocos_do_save(self.dir))
        alvo = {off // M.BLOCO_BYTES for off, _, _, _, _ in M.LAYOUT}
        fora = alvo - usados
        self.assertTrue(fora, "o achado do markdown deixou de valer")

    def test_o_bloco_de_fora_esta_zerado_no_molde(self) -> None:
        usados = set(M.blocos_do_save(self.dir))
        for b in {off // M.BLOCO_BYTES for off, _, _, _, _ in M.LAYOUT} - usados:
            blk = self.card[b * M.BLOCO_BYTES:(b + 1) * M.BLOCO_BYTES]
            self.assertEqual(sum(blk), 0, f"bloco {b} nao esta zerado")

    def test_nenhum_destino_cai_no_diretorio(self) -> None:
        # O escritor copia o molde e escreve por cima; se algum destino caisse
        # no bloco 0, o cartao sairia com o diretorio corrompido.
        for off, campo, *_ in M.LAYOUT:
            self.assertGreaterEqual(off, M.BLOCO_BYTES, campo)

    def test_capitao_e_cobradores_ficam_no_bloco_de_fora(self) -> None:
        # E a coincidencia que o markdown registra contra o readme da v0.98.
        usados = set(M.blocos_do_save(self.dir))
        for off, campo, *_ in M.LAYOUT:
            if "cobrador" in campo:
                self.assertNotIn(off // M.BLOCO_BYTES, usados, campo)


class TestMedicao(unittest.TestCase):
    """A fixture nao e versionada; a medicao dela e."""

    def test_a_linha_medida_fecha_com_a_spec_do_escritor(self) -> None:
        med = M.linhas_medidas()
        if not med:
            self.skipTest("sem wte/re/mcr-medido.tsv -- a fixture NAO foi "
                          "conferida. Gere com o roteiro 27-mcr.txt e rode "
                          "dump_mcr.py --medir")
        r = med[0]
        self.assertEqual(r[3], "sim", "o escritor tocou o diretorio")
        self.assertGreater(int(r[1]), 0)
        # O escritor mexe em DOIS blocos, e sao os do layout.
        blocos = {int(p.split("=")[0]) for p in r[4].split(";")}
        alvo = {off // M.BLOCO_BYTES for off, _, _, _, _ in M.LAYOUT}
        self.assertEqual(blocos, alvo)


if __name__ == "__main__":
    unittest.main()
