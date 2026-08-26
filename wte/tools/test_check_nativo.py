#!/usr/bin/env python3
"""Testes do `check_nativo.py` -- CORR-WTE-119.

As tres recusas plantadas, no molde do `test_check_divergencias.py`: espelho da
arvore em `tempfile`, caminhos do modulo repontados, sem `:98`, sem Wine e sem
imagem.

O que se protege aqui e o unico documento de fechamento que nao tinha quem o
defendesse. O `nativo.md` REPETE os sete valores do `nativo.tsv` numa tabela
propria; ate esta correcao, uma corrida futura podia mudar um valor no TSV e
deixar o `.md` afirmando o velho, em verde.
"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import check_nativo as C


class _aponta:
    """Troca atributos de modulo e devolve os originais ao sair."""

    def __init__(self, mod, **kw):
        self.mod, self.kw, self.velho = mod, kw, {}

    def __enter__(self):
        for k, v in self.kw.items():
            self.velho[k] = getattr(self.mod, k)
            setattr(self.mod, k, v)
        return self.mod

    def __exit__(self, *_):
        for k, v in self.velho.items():
            setattr(self.mod, k, v)
        return False


CAB = "medida\tvalor\tveredito\n"

# Duas medidas bastam para os casos, e a segunda e de proposito uma cujo `.md`
# ENFEITA o valor -- e o par que prova que a normalizacao existe e funciona.
TSV = (CAB
       + "ldd-wine\t0 de 56 bibliotecas\tok\n"
       + "janela\t522x475, titulo conferido\tok\n")

MD = """# nativo

| Caminho | Por que |
|---|---|
| `/var/lib/flatpak` | a tabela de mascaras, que NAO e a de medidas |

## As sete medidas

| Medida | Valor | Veredito |
|---|---|---|
| `ldd-wine` | 0 de 56 bibliotecas | ok |
| `janela` | 522×475, título conferido | ok |
"""


class Base(unittest.TestCase):
    def monta(self, tsv: str = TSV, md: str = MD) -> Path:
        d = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (d / "nativo.tsv").write_text(tsv, encoding="utf-8")
        (d / "nativo.md").write_text(md, encoding="utf-8")
        self.enterContext(_aponta(C, RAIZ=d, TSV=d / "nativo.tsv",
                                  MD=d / "nativo.md"))
        return d

    def problemas(self) -> list[str]:
        return C.mede()["problemas"]

    def codigo(self) -> int:
        """A saida do `main()` e engolida: sem isso o relatorio de uma recusa
        PLANTADA aparece no meio do `make -C wte check`."""
        with (contextlib.redirect_stderr(io.StringIO()),
              contextlib.redirect_stdout(io.StringIO())):
            return C.main([])


class TestEstadoDeHoje(Base):
    def test_a_arvore_real_passa(self) -> None:
        """Sem espelho: o modulo aponta para o `wte/re/` de verdade."""
        self.assertEqual(C.mede()["problemas"], [])

    def test_as_sete_medidas_estao_no_TSV(self) -> None:
        self.assertEqual(len(C.mede()["tsv"]), 7)

    def test_o_espelho_montado_passa(self) -> None:
        """Se este reprovar, o espelho e que esta errado, nao o gate."""
        self.monta()
        self.assertEqual(self.problemas(), [])


class TestNormalizacao(Base):
    """A comparacao aceita o `.md` mais bonito, e nao o `.md` que contradiz."""

    def test_x_multiplicacao_e_acento_passam(self) -> None:
        """`522x475, titulo` no TSV contra `522×475, título` no `.md`."""
        self.monta()
        self.assertEqual(self.problemas(), [])

    def test_crase_e_contexto_a_mais_passam(self) -> None:
        md = MD.replace("| `ldd-wine` | 0 de 56 bibliotecas |",
                        "| `ldd-wine` | **0** de 56 `bibliotecas`, medido |")
        self.monta(md=md)
        self.assertEqual(self.problemas(), [])

    def test_numero_diferente_NAO_passa(self) -> None:
        """O limite da tolerancia, e a razao de ela ser substring."""
        md = MD.replace("0 de 56 bibliotecas", "0 de 58 bibliotecas")
        self.monta(md=md)
        p = self.problemas()
        self.assertTrue(any("ldd-wine" in x and "58" in x for x in p), p)


class TestAsTresRecusas(Base):
    def test_1_valor_divergente_reprova(self) -> None:
        md = MD.replace("522×475", "640×480")
        self.monta(md=md)
        self.assertTrue(any("janela" in x for x in self.problemas()))
        self.assertEqual(self.codigo(), 2)

    def test_2_medida_no_md_que_o_TSV_nao_tem_reprova(self) -> None:
        md = MD + "| `inventada` | valor qualquer | ok |\n"
        self.monta(md=md)
        p = self.problemas()
        self.assertTrue(any("inventada" in x and "sem fonte" in x for x in p), p)
        self.assertEqual(self.codigo(), 2)

    def test_3_veredito_reprovou_no_TSV_derruba_o_gate(self) -> None:
        """Um `reprovou` que ficou no arquivo e RESULTADO -- a condicao 3 nao
        esta cumprida, e o gate nao pode ficar verde por cima."""
        tsv = TSV.replace("522x475, titulo conferido\tok",
                          "522x475, titulo conferido\treprovou")
        md = MD.replace("| `janela` | 522×475, título conferido | ok |",
                        "| `janela` | 522×475, título conferido | reprovou |")
        self.monta(tsv=tsv, md=md)
        p = self.problemas()
        self.assertTrue(any("nao esta cumprida" in x for x in p), p)
        self.assertEqual(self.codigo(), 2)

    def test_medida_do_TSV_ausente_do_md_reprova(self) -> None:
        """A quarta direcao, que a CORR nao numerou e o modulo cobre."""
        md = MD.replace("| `janela` | 522×475, título conferido | ok |\n", "")
        self.monta(md=md)
        p = self.problemas()
        self.assertTrue(any("janela" in x and "NAO na tabela" in x for x in p), p)


class TestLeitura(Base):
    def test_a_outra_tabela_do_md_nao_e_lida(self) -> None:
        """O `.md` tem a tabela de caminhos mascarados ANTES da de medidas, e o
        primeiro campo dela tambem vem entre crases. O que as separa e o numero
        de colunas -- se o leitor as confundisse, `/var/lib/flatpak` viraria uma
        medida sem fonte."""
        self.monta()
        self.assertEqual([x["medida"] for x in C.le_md(C.MD)],
                         ["ldd-wine", "janela"])

    def test_TSV_ausente_aborta(self) -> None:
        d = self.monta()
        (d / "nativo.tsv").unlink()
        with self.assertRaises(C.NativoError):
            C.mede()
        self.assertEqual(self.codigo(), 2)

    def test_cabecalho_errado_aborta(self) -> None:
        self.monta(tsv="medida\tvalor\n")
        with self.assertRaises(C.NativoError):
            C.mede()

    def test_linha_com_campo_faltando_aborta(self) -> None:
        self.monta(tsv=CAB + "janela\t522x475\n")
        with self.assertRaises(C.NativoError) as ctx:
            C.mede()
        self.assertIn("3 campos", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
