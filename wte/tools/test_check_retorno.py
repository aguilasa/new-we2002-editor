#!/usr/bin/env python3
"""Testes do `check_retorno.py`.

Nao abrem o `.exe`, nao dirigem janela: montam o texto em arquivo temporario. O
que eles protegem e o parser da arvore de objetos e as tres afirmacoes que o
`check_retorno.py` faz sobre ela -- `Default` unico, `Cancel` unico, ordem de
tabulacao na ordem do arquivo.

**A moldura e os retangulos saiam daqui em 2026-08-25** (CORR-WTE-115). Eles
sao do `check_carregado.py` e moravam neste arquivo so porque ele nasceu
primeiro -- e foi assim que a correcao veio a acreditar que a recusa da moldura
nao era exercitada: o `ls` procurava um `test_check_carregado.py` que nao
existia, e os casos estavam aqui o tempo todo. Agora estao em
`test_check_carregado.py`, com o resto do modulo deles.
"""

import tempfile
import unittest
from pathlib import Path

import check_retorno


def escreve(texto: str) -> Path:
    tmp = Path(tempfile.mkdtemp()) / "f.dfm"
    tmp.write_text(texto, encoding="utf-8")
    return tmp


DFM = """object ficha_x: Tficha_x
  ClientWidth = 100
  ClientHeight = 50
  Icon.Data = {
    0000010001001010
    1000
  }
  object BitBtn1: TBitBtn
    Left = 8
    Top = 8
    Width = 20
    Height = 10
    Default = True
    ModalResult = 6
    TabOrder = 0
  end
  object BitBtn2: TBitBtn
    Left = 40
    Top = 8
    Width = 20
    Height = 10
    Cancel = True
    ModalResult = 7
    TabOrder = 1
  end
  object TStaticText
    Left = 4
    Top = 30
    Width = 10
    Height = 10
  end
end
"""


class TestArvore(unittest.TestCase):
    def test_o_blob_hexadecimal_nao_vira_objeto(self):
        """O `.lfm` traz o blob cru; o `.dfm`, uma referencia. Um parser so."""
        objetos = check_retorno.le_arvore(escreve(DFM))
        self.assertEqual([o["classe"] for o in objetos],
                         ["Tficha_x", "TBitBtn", "TBitBtn", "TStaticText"])

    def test_default_e_cancel_saem_unicos(self):
        objetos = check_retorno.le_arvore(escreve(DFM))
        self.assertEqual(check_retorno.unico(objetos, "Default")["nome"],
                         "BitBtn1")
        self.assertEqual(check_retorno.unico(objetos, "Cancel")["nome"],
                         "BitBtn2")

    def test_dois_defaults_abortam(self):
        """Dois botoes `Default` fariam o `Return` ser indeterminado."""
        texto = DFM.replace("Cancel = True", "Default = True")
        objetos = check_retorno.le_arvore(escreve(texto))
        with self.assertRaises(check_retorno.RetornoError):
            check_retorno.unico(objetos, "Default")

    def test_a_tabordem_segue_a_ordem_do_arquivo(self):
        objetos = check_retorno.le_arvore(escreve(DFM))
        self.assertEqual(check_retorno.tabordem(objetos),
                         "BitBtn1:0,BitBtn2:1")


if __name__ == "__main__":
    unittest.main()
