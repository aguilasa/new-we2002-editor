#!/usr/bin/env python3
"""Testes do check_golden.py -- WTE-TASK-34.

O que se mede aqui sao as duas guardas do gerador da bateria completa, e as
duas existem porque a alternativa e uma tabela que envelhece sozinha:

1. **`golden` sem `controle` na mesma ROM.** A bateria ja recusa rodar nessa
   ordem, mas o TSV e um arquivo de texto: quem o editasse a mao publicaria um
   `golden` verde sem a corrida que prova que o par roteiro+imagem e
   deterministico. Zero divergencia no `golden` pode ser paridade -- ou pode
   ser que nenhum dos dois lados gravou nada.
2. **Roteiro com par em disco e ausente do TSV.** E o defeito que a conta de
   gravacoes teve ate a WTE-TASK-31: a lista cresce, o numero nao, e ninguem
   repara porque o arquivo continua bem formado.

Os testes montam o TSV em memoria e apontam os caminhos do modulo para um
diretorio temporario: nao abrem o `.exe`, nao precisam de `DISPLAY` nem de
Wine, e rodam num clone sem a pasta `we-team-editor/`.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import check_golden as C

CAB = "roteiro\trom\tmodo\tveredito\tsegundos\tdata\n"


def linha(roteiro: str, rom: str, modo: str, veredito: str = "PASSOU") -> str:
    return f"{roteiro}\t{rom}\t{modo}\t{veredito}\t10\t2026-08-24\n"


class Base(unittest.TestCase):
    """Aponta o modulo para uma arvore temporaria e devolve tudo no fim."""

    def monta(self, tsv: str, roteiros: list[str]):
        d = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (d / "re").mkdir()
        (d / "roteiros").mkdir()
        (d / "re" / "golden.tsv").write_text(tsv, encoding="utf-8")
        for r in roteiros:
            (d / "roteiros" / f"{r}.txt").write_text("alvo: original\n")
            (d / "roteiros" / f"{r}.port.txt").write_text("alvo: port\n")
        self.enterContext(_aponta(C, TSV=d / "re" / "golden.tsv",
                                  OUT=d / "re" / "golden.md",
                                  ROTEIROS=d / "roteiros"))
        return d


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


class TestControleAntesDoTeste(Base):

    def test_golden_sem_controle_aborta(self) -> None:
        """A guarda 1: sem controle, verde e vermelho nao significam nada."""
        self.monta(CAB + linha("golden-01", "japonesa", "golden"), ["golden-01"])
        with self.assertRaises(C.CheckError) as e:
            C.mede()
        self.assertIn("sem o controle", str(e.exception))
        self.assertIn("golden-01/japonesa", str(e.exception))

    def test_par_completo_passa(self) -> None:
        self.monta(CAB
                   + linha("golden-01", "japonesa", "controle")
                   + linha("golden-01", "japonesa", "golden"), ["golden-01"])
        m = C.mede()
        self.assertEqual(len(m["corridas"]), 2)

    def test_controle_sozinho_passa(self) -> None:
        """Controle sem golden e legitimo: e o que a bateria registra quando o
        controle reprova e o golden vira NAO_APLICAVEL noutra linha."""
        self.monta(CAB + linha("golden-01", "japonesa", "controle", "SEM_ORACULO"),
                   ["golden-01"])
        self.assertEqual(len(C.mede()["corridas"]), 1)


class TestCobertura(Base):

    def test_roteiro_em_disco_e_ausente_do_tsv_aborta(self) -> None:
        """A guarda 2: bateria que cresce e tabela que nao acompanha."""
        self.monta(CAB
                   + linha("golden-01", "japonesa", "controle")
                   + linha("golden-01", "japonesa", "golden"),
                   ["golden-01", "golden-99"])
        with self.assertRaises(C.CheckError) as e:
            C.mede()
        self.assertIn("golden-99", str(e.exception))

    def test_tsv_citando_roteiro_que_sumiu_aborta(self) -> None:
        self.monta(CAB
                   + linha("golden-01", "japonesa", "controle")
                   + linha("golden-01", "japonesa", "golden")
                   + linha("golden-77", "japonesa", "controle")
                   + linha("golden-77", "japonesa", "golden"), ["golden-01"])
        with self.assertRaises(C.CheckError) as e:
            C.mede()
        self.assertIn("golden-77", str(e.exception))

    def test_roteiro_sem_par_nao_e_exigido(self) -> None:
        """Roteiro sem `.port` julga o oraculo contra ele mesmo e mais nada."""
        d = self.monta(CAB
                       + linha("golden-01", "japonesa", "controle")
                       + linha("golden-01", "japonesa", "golden"), ["golden-01"])
        (d / "roteiros" / "golden-02-so-oraculo.txt").write_text("alvo: original\n")
        self.assertEqual(C.mede()["disco"], ["golden-01"])


class TestVocabulario(Base):

    def test_veredito_desconhecido_aborta(self) -> None:
        """Palavra nova de veredito faria a distribuicao mentir em silencio."""
        self.monta(CAB + linha("golden-01", "japonesa", "controle", "QUASE"),
                   ["golden-01"])
        with self.assertRaises(C.CheckError) as e:
            C.mede()
        self.assertIn("QUASE", str(e.exception))

    def test_sem_oraculo_e_reprovou_sao_palavras_diferentes(self) -> None:
        """A distincao e a task inteira: uma acusa o port, a outra nao."""
        self.assertIn("SEM_ORACULO", C.VEREDITOS)
        self.assertIn("REPROVOU", C.VEREDITOS)

    def test_cabecalho_errado_aborta(self) -> None:
        self.monta("roteiro\tmodo\tveredito\n", ["golden-01"])
        with self.assertRaises(C.CheckError):
            C.mede()


class TestSaida(Base):

    def test_gera_tabela_com_as_duas_roms(self) -> None:
        self.monta(CAB
                   + linha("golden-01", "japonesa", "controle")
                   + linha("golden-01", "japonesa", "golden")
                   + linha("golden-01", "europeia", "controle", "SEM_ORACULO")
                   + linha("golden-01", "europeia", "golden", "NAO_APLICAVEL"),
                   ["golden-01"])
        texto = C.gera(C.mede())
        self.assertIn("| japonesa |", texto)
        self.assertIn("| europeia |", texto)
        self.assertIn("SEM_ORACULO / NAO_APLICAVEL", texto)
        self.assertIn("GERADO", texto)


if __name__ == "__main__":
    unittest.main()
