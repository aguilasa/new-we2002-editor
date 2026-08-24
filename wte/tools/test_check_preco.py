#!/usr/bin/env python3
"""Testes do check_preco.py -- WTE-TASK-32.

Duas coisas se medem aqui, e as duas ja falharam de verdade nesta task:

1. **a guarda que exige prova de que o oraculo rodou.** A ROM europeia nao
   hospeda este oraculo (o `wte.exe` morre na troca de time, CORR-WTE-044), e a
   corrida sobre ela gravou ZERO bytes. A primeira versao do coletor creditou
   ao oraculo os precos DE FABRICA daquela imagem e acusou 21 divergencias que
   nao existiam;

2. **o `test_preco.pas`**, compilado e rodado -- a formula em Pascal contra os
   valores que o oraculo respondeu, mais os tres casos que a amostra medida nao
   alcanca (saturacao por transbordo de 32 bits, truncamento para zero, e a
   ordem do `x 5 div 3`).

O item 2 PULA sem `fpc`, e diz o que deixou de medir em vez de passar calado.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import check_preco as C


class TestGuardas(unittest.TestCase):
    """As recusas do `--check`."""

    def linha(self, **kw) -> dict:
        base = {"rom": "japanese-shift-jis", "time": 2, "slot": 0, "soma": 38,
                "posicao": 1, "previsto": 13, "medido": 13}
        base.update(kw)
        return base

    def amostra(self, n: int, **kw) -> list[dict]:
        return [self.linha(slot=i % 22, **kw) for i in range(n)]

    def test_passa_o_caso_bom(self) -> None:
        C.valida(self.amostra(C.MINIMO_AMOSTRA))

    def test_amostra_curta_aborta(self) -> None:
        """"100%" sobre tres linhas nao e afirmacao sobre populacao."""
        with self.assertRaises(C.PrecoError) as ctx:
            C.valida(self.amostra(3))
        self.assertIn("minimo", str(ctx.exception))

    def test_divergencia_aborta_e_diz_a_soma(self) -> None:
        linhas = self.amostra(C.MINIMO_AMOSTRA)
        linhas[0]["previsto"] = 99
        with self.assertRaises(C.PrecoError) as ctx:
            C.valida(linhas)
        self.assertIn("soma", str(ctx.exception))

    def test_slot_22_medido_aborta(self) -> None:
        """O oraculo nunca preca o slot 22 -- se aparecer, a regra caiu."""
        linhas = self.amostra(C.MINIMO_AMOSTRA)
        linhas[0]["slot"] = C.SLOT_NUNCA_PRECADO
        with self.assertRaises(C.PrecoError) as ctx:
            C.valida(linhas)
        self.assertIn(str(C.SLOT_NUNCA_PRECADO), str(ctx.exception))

    def test_linha_sem_medido_nao_entra_na_conta(self) -> None:
        """Imagem por onde o oraculo nao passou nao vira evidencia."""
        linhas = self.amostra(C.MINIMO_AMOSTRA)
        linhas.append(self.linha(previsto=99, medido=None))
        C.valida(linhas)


class TestOArquivoReal(unittest.TestCase):
    """O TSV versionado passa na propria guarda."""

    def test_check_do_arquivo_commitado(self) -> None:
        self.assertEqual(C.main(["--check"]), 0)


class TestPascal(unittest.TestCase):
    """O `test_preco.pas` compila e passa."""

    PROGRAMA = C.ROOT / "wte" / "tests" / "test_preco.pas"
    FONTES = C.ROOT / "wte" / "src"

    def test_a_formula_em_pascal(self) -> None:
        fpc = shutil.which("fpc")
        if not fpc:
            self.skipTest("sem fpc -- a formula de preco NAO foi conferida "
                          "nesta execucao")
        with tempfile.TemporaryDirectory() as td:
            binario = Path(td) / "test_preco"
            r = subprocess.run(
                [fpc, f"-Fu{self.FONTES}", f"-FU{td}", f"-o{binario}",
                 str(self.PROGRAMA)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            r = subprocess.run([str(binario)], capture_output=True, text=True,
                               env=dict(os.environ))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # Numero medido: caso que sumisse do programa sumiria em silencio.
        self.assertIn("12 conferencias", r.stdout)


if __name__ == "__main__":
    unittest.main()
