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

import os
import shutil
import subprocess
import tempfile
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


class TestPascal(unittest.TestCase):
    """O `we2002_mcr.pas` e escrito a mao; o layout daqui e o guard dele."""

    def setUp(self) -> None:
        if not M.PASCAL.is_file():
            self.skipTest(f"sem {M.REL_PASCAL}")
        self.original = M.PASCAL.read_text(encoding="utf-8")

    def test_o_pascal_bate_com_o_layout(self) -> None:
        M.confere_pascal(M.COBRADORES_ESPERADOS)

    def test_constante_plantada_recusa(self) -> None:
        try:
            M.PASCAL.write_text(
                self.original.replace("MCR_CAPITAO        = $6500;",
                                      "MCR_CAPITAO        = $6501;"),
                encoding="utf-8")
            with self.assertRaises(M.McrError) as ctx:
                M.confere_pascal(M.COBRADORES_ESPERADOS)
            self.assertIn("MCR_CAPITAO", str(ctx.exception))
        finally:
            M.PASCAL.write_text(self.original, encoding="utf-8")

    def test_tabela_de_cobradores_plantada_recusa(self) -> None:
        try:
            M.PASCAL.write_text(
                self.original.replace("($614F, $6140", "($6140, $614F"),
                encoding="utf-8")
            with self.assertRaises(M.McrError) as ctx:
                M.confere_pascal(M.COBRADORES_ESPERADOS)
            self.assertIn("MCR_COBRADORES", str(ctx.exception))
        finally:
            M.PASCAL.write_text(self.original, encoding="utf-8")

    def test_toda_constante_da_tabela_existe_no_pascal(self) -> None:
        achados = M.constantes_do_pascal()
        for nome in M.CONSTANTES_PASCAL:
            self.assertIn(nome, achados)


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


class TestPascalConcorda(unittest.TestCase):
    """O `we2002_mcr` compila e le o mesmo cartao que o Python."""

    PROGRAMA = M.ROOT / "wte" / "tests" / "test_mcr.pas"
    FONTES = M.ROOT / "wte" / "src"
    # Fixture gerada pelo original, fora do git -- ver a decisao no `mcr.md`.
    CARTAO = M.ROOT / "work" / "saida.mcr"

    def _roda(self, ambiente: dict) -> str:
        fpc = shutil.which("fpc")
        if not fpc:
            self.skipTest("sem fpc -- o we2002_mcr NAO foi compilado nesta "
                          "execucao")
        with tempfile.TemporaryDirectory() as td:
            binario = Path(td) / "test_mcr"
            r = subprocess.run(
                [fpc, f"-Fu{self.FONTES}", f"-FU{td}", f"-o{binario}",
                 str(self.PROGRAMA)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            env = dict(os.environ)
            env.update(ambiente)
            r = subprocess.run([str(binario)], capture_output=True, text=True,
                               env=env)
        self.assertEqual([ln for ln in r.stdout.splitlines()
                          if ln.startswith("FALHA")], [], r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def test_invariantes_sem_cartao(self) -> None:
        saida = self._roda({"WTE_TEST_MCR": ""})
        self.assertIn("PULADO\tleitura de cartao", saida)
        # Numero medido, e nao suposto: caso que some do programa Pascal
        # sumiria em silencio e o teste seguiria verde.
        self.assertIn("CASOS\t10", saida)

    def test_a_leitura_bate_com_a_do_python(self) -> None:
        if not self.CARTAO.is_file():
            self.skipTest(
                f"sem {self.CARTAO.relative_to(M.ROOT)} -- as duas leituras "
                "NAO foram confrontadas. Gere a fixture com o roteiro "
                "wte/tests/roteiros/27-mcr.txt")
        mcr = self.CARTAO.read_bytes()
        form = bytes(mcr[0x63D5:0x63D5 + 10]) + bytes(mcr[0x62A8:0x62A8 + 20])
        cob = bytes([mcr[a] for a in M.COBRADORES_ESPERADOS] + [mcr[0x6500]])

        def numero(j: int) -> int:
            grupo, dentro = divmod(j, 6)
            bit = (5 * dentro) % 8
            bi = grupo * 4 + (5 * dentro) // 8
            v = mcr[0x5404 + bi] | (mcr[0x5404 + bi + 1] << 8)
            return ((v >> bit) & 0x1F) + 1

        saida = self._roda({
            "WTE_TEST_MCR": str(self.CARTAO),
            "WTE_TEST_MCR_FORMACAO": form.hex(),
            "WTE_TEST_MCR_COBRADORES": cob.hex(),
            "WTE_TEST_MCR_DORSAIS": ",".join(str(numero(j)) for j in range(23)),
            "WTE_TEST_MCR_BLOCOS": str(len(M.blocos_do_save(
                M.diretorio(mcr)))),
        })
        self.assertIn("OK\ta formacao bate com a do dump_mcr.py", saida)
        self.assertIn("OK\tos 23 dorsais batem", saida)

    def test_a_fixture_bate_com_a_spec_do_escritor(self) -> None:
        """O que a spec do `grabar_memoryClick` mediu, o leitor recupera.

        Nao e teste do Pascal: e a terceira ponta. A spec anotou formacao e
        cobradores do time 2 quando o handler foi portado, e esses numeros
        estao no markdown ha uma task. Se o layout deste leitor estivesse
        errado, ele nao os reproduziria.
        """
        if not self.CARTAO.is_file():
            self.skipTest("sem a fixture")
        mcr = self.CARTAO.read_bytes()
        cob = [mcr[a] for a in M.COBRADORES_ESPERADOS] + [mcr[0x6500]]
        self.assertEqual(cob, [7, 7, 8, 7, 7, 8])
        form = list(mcr[0x63D5:0x63D5 + 10])
        self.assertEqual(form, [2, 3, 6, 7, 8, 0x0A, 0x0E, 0x10, 0x11, 0x13])


if __name__ == "__main__":
    unittest.main()
