#!/usr/bin/env python3
"""Testes do cobertura_gate.py -- CORR-WTE-089.

O que se mede aqui e a EXTRACAO e as GUARDAS, que sao as duas partes onde um
erro passaria por verde:

1. **a linha de trace**, porque um `REMark` com sufixo existe de verdade na
   arvore (`flechasapaClick: bitmap N sem dono`) e `grep -c` cru o contaria
   como disparo;
2. **as guardas de `valida`**, porque cada uma delas existe para impedir uma
   afirmacao falsa: handler fora dos 96, gate vermelho, e spec que cita o TSV
   sem ter linha nele.

Tudo roda offline: nao abre o `.exe`, nao precisa do `:98` nem de Wine.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import cobertura_gate as C


class TestLinhaDeTrace(unittest.TestCase):
    """A extracao do nome qualificado."""

    def nomes(self, texto: str) -> dict:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "port-trace.log"
            p.write_text(texto, encoding="utf-8")
            return C.conta_trace(p)

    def test_conta_disparo_e_ignora_stub(self) -> None:
        """`==` e corpo que rodou; sem `==` e `REStub`, que e buraco."""
        texto = ("  0.000  == MainForm.FormCreate\n"
                 "  0.082  estrategia.FormCreate\n"
                 "  7.878  == MainForm.lista_equiposChange\n"
                 "  7.900  == MainForm.lista_equiposChange\n")
        self.assertEqual(self.nomes(texto),
                         {"MainForm.FormCreate": 1,
                          "MainForm.lista_equiposChange": 2})

    def test_o_remark_com_sufixo_nao_conta(self) -> None:
        """A armadilha medida na coleta de 2026-08-24.

        O `flechasapaClick` emite um SEGUNDO `REMark` por sufixo. `grep -c` cru
        contaria os dois; o `$` do padrao descarta o de aviso.
        """
        texto = ("  1.000  == jugador.flechasapaClick\n"
                 "  1.001  == jugador.flechasapaClick: bitmap 2 sem dono\n")
        self.assertEqual(self.nomes(texto), {"jugador.flechasapaClick": 1})

    def test_a_linha_de_imagem_nao_e_handler(self) -> None:
        """`== imagem: <caminho>` e marca de sessao, nao disparo."""
        self.assertEqual(self.nomes("  0.157  == imagem: work/x.bin\n"), {})


class TestGuardas(unittest.TestCase):
    """Cada guarda de `valida`, com a recusa vista."""

    def setUp(self) -> None:
        self._handlers = C.handlers_conhecidos
        self._verdes = C.roteiros_verdes
        self._spec = C.S.SPEC
        C.handlers_conhecidos = lambda: {"MainForm.x", "MainForm.y"}
        C.roteiros_verdes = lambda: {"golden-11-descarte-ml"}
        # Nenhuma spec cita o TSV, para isolar as outras guardas.
        C.S.SPEC = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        C.handlers_conhecidos = self._handlers
        C.roteiros_verdes = self._verdes
        C.S.SPEC = self._spec

    def linha(self, **kw) -> dict:
        base = {"roteiro": "golden-11-descarte-ml", "handler": "MainForm.x",
                "disparos": 2}
        base.update(kw)
        return base

    def test_passa_o_caso_bom(self) -> None:
        C.valida([self.linha()])

    def test_handler_fora_dos_96_aborta(self) -> None:
        with self.assertRaises(C.CoberturaError) as ctx:
            C.valida([self.linha(handler="MainForm.inventado")])
        self.assertIn("nao esta entre os 96", str(ctx.exception))

    def test_zero_disparo_aborta(self) -> None:
        """Ausencia se escreve nao pondo a linha, nao pondo zero."""
        with self.assertRaises(C.CoberturaError) as ctx:
            C.valida([self.linha(disparos=0)])
        self.assertIn(">= 1", str(ctx.exception))

    def test_gate_vermelho_aborta(self) -> None:
        """Cobertura dentro de gate que nao passou nao verifica nada."""
        C.roteiros_verdes = lambda: set()
        with self.assertRaises(C.CoberturaError) as ctx:
            C.valida([self.linha()])
        self.assertIn("gate vermelho", str(ctx.exception))

    def test_roteiro_sem_par_port_aborta(self) -> None:
        with self.assertRaises(C.CoberturaError) as ctx:
            C.valida([self.linha(roteiro="golden-99-inexistente")])
        self.assertIn("falta o roteiro", str(ctx.exception))

    def test_spec_que_cita_o_tsv_sem_linha_aborta(self) -> None:
        """A licao do `check_edicao.py:106-111`, mecanizada.

        Citar regua e barato; ter disparo medido nao.
        """
        (C.S.SPEC / "MainForm.y.md").write_text(
            "cobre pelo " + C.TSV.name, encoding="utf-8")
        with self.assertRaises(C.CoberturaError) as ctx:
            C.valida([self.linha(handler="MainForm.x")])
        self.assertIn("MainForm.y", str(ctx.exception))

    def test_spec_que_cita_o_tsv_com_linha_passa(self) -> None:
        (C.S.SPEC / "MainForm.y.md").write_text(
            "cobre pelo " + C.TSV.name, encoding="utf-8")
        C.valida([self.linha(handler="MainForm.y")])


class TestEscrita(unittest.TestCase):
    def test_ordena_e_poe_cabecalho(self) -> None:
        saida = C.escreve([("b", "MainForm.z", 1), ("a", "MainForm.y", 3)])
        self.assertEqual(saida.splitlines()[0], "roteiro\thandler\tdisparos")
        self.assertEqual(saida.splitlines()[1], "a\tMainForm.y\t3")


if __name__ == "__main__":
    unittest.main()
