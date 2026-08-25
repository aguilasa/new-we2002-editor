#!/usr/bin/env python3
"""Testes do dump_buffers.py e do test_bordas.pas -- WTE-TASK-36.

Duas coisas se medem aqui:

1. **as guardas do `dump_buffers.py`**, que sao o que torna o inventario uma
   conferencia em vez de uma descricao. Cada uma ja falhou uma vez durante a
   execucao da task, e as duas falhas valem registro porque sao de naturezas
   diferentes:

   - o predicado da faixa era `numero > 99` sem o parentese de fecho, e casava
     dentro de `numero > 9999`. Guarda que aceita o proprio contra-exemplo nao
     guarda nada -- e a mesma familia da armadilha 2 do prompt (`[^x]` casando
     `\\n`), so que por prefixo em vez de por classe;
   - campo de limite de RUNTIME nunca era conferido contra `MaxLength`
     estatico. Os dois brigam: o estatico vale ate a primeira troca de time e
     depois nao.

2. **o `test_bordas.pas`**, compilado e rodado. O numero de conferencias e
   fixado aqui: caso que sumisse do programa sumiria em silencio.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dump_buffers as D  # noqa: E402


class TestGuardas(unittest.TestCase):
    """As recusas, cada uma vista falhar antes de virar teste."""

    def corpo(self, nome: str) -> str:
        return (D.SRC / "impl" / nome).read_text(encoding="utf-8")

    def test_predicado_da_faixa_nao_casa_por_prefixo(self) -> None:
        """`numero > 99` NAO pode casar dentro de `numero > 9999`."""
        for n in D.NUMERICOS:
            if n["controle"] != "casilla_dorsal":
                continue
            corpo = self.corpo(n["handler"])
            self.assertIn(n["predicado"], corpo)
            alargado = corpo.replace("(numero > 99)", "(numero > 9999)")
            self.assertNotIn(n["predicado"], alargado,
                             "o predicado casa por prefixo -- falta o fecho")

    def test_todo_numerico_tem_a_faixa_no_handler(self) -> None:
        for n in D.NUMERICOS:
            self.assertIn(n["predicado"], self.corpo(n["handler"]),
                          f"{n['controle']}: a validacao de faixa sumiu")

    def test_campo_de_runtime_nao_tem_maxlength_estatico(self) -> None:
        """O DFM do original nao declara MaxLength nos dois de nome de time."""
        est = D.maxlength_dos_forms()
        for c in D.CAMPOS:
            if c["origem"] == "runtime":
                self.assertNotIn(c["controle"], est)

    def test_todo_maxlength_do_lfm_tem_dono(self) -> None:
        est = set(D.maxlength_dos_forms())
        donos = ({c["controle"] for c in D.CAMPOS}
                 | {n["controle"] for n in D.NUMERICOS})
        self.assertEqual(est - donos, set(),
                         "MaxLength no .lfm sem linha no inventario")

    def test_todo_limite_cabe_no_vetor(self) -> None:
        for l in D.mede()["linhas"]:
            self.assertTrue(
                l["cabe"],
                f"{l['controle']}: {l['lim_max']} nao cabe em {l['capacidade']}")


class TestInventario(unittest.TestCase):

    def test_os_dois_menos_um_sao_o_mesmo(self) -> None:
        """O `- 1` do MaxLength e o `- 1` do decodificador.

        `LimiteDoNome1` poe `TEAM_NAME_KANJI_LEN[t] - 1`, e o `KanjiToAscii`
        percorre `(l - 1) * 2` bytes. O campo nunca recebe mais do que a
        leitura devolve, e isso e propriedade -- nao coincidencia.
        """
        aux = (D.SRC / "impl" / "ep2002_mainform.aux.inc").read_text(
            encoding="utf-8")
        self.assertIn("TEAM_NAME_KANJI_LEN[IndiceNaTabela(indice)] - 1", aux)
        codec = (D.SRC / "we2002_textcodec.pas").read_text(encoding="utf-8")
        self.assertIn("(l - 1) * 2", codec)

    def test_gerador_bate_com_o_commitado(self) -> None:
        self.assertEqual(D.main(["--check"]), 0)


class TestBordasEmPascal(unittest.TestCase):
    PROGRAMA = D.WTE / "tests" / "test_bordas.pas"

    def test_as_bordas_passam(self) -> None:
        fpc = shutil.which("fpc")
        if not fpc:
            self.skipTest("sem fpc -- as bordas NAO foram conferidas")
        with tempfile.TemporaryDirectory() as td:
            binario = Path(td) / "test_bordas"
            r = subprocess.run(
                [fpc, f"-Fu{D.SRC}", f"-FU{td}", f"-o{binario}",
                 str(self.PROGRAMA)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            r = subprocess.run([str(binario)], capture_output=True, text=True,
                               env=dict(os.environ))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # Numero medido: caso que sumisse do programa sumiria em silencio.
        self.assertIn("10/10", r.stdout)


if __name__ == "__main__":
    unittest.main()
