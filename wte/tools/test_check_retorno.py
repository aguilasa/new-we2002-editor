#!/usr/bin/env python3
"""Testes do `check_retorno.py` e das partes puras do `check_carregado.py`.

Nao abrem o `.exe`, nao dirigem janela e nao dependem das capturas: montam o
texto em arquivo temporario. O que eles protegem e o que ja errou nesta task --
o parser que engolia o objeto SEM NOME (e contava 36 `TStaticText` onde ha 37)
e a regra da moldura de 6x32, que decide se a coordenada de um controle cai no
lugar certo da captura.
"""

import tempfile
import unittest
from pathlib import Path

import check_carregado
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


class TestRetangulos(unittest.TestCase):
    def test_o_objeto_sem_nome_entra_na_conta(self):
        """Ha um `TStaticText` anonimo no `MainForm`, e os 37 o incluem."""
        caminho = escreve(DFM)
        objetos = check_retorno.le_arvore(caminho)
        achados = check_carregado.retangulos(objetos, caminho, "TStaticText")
        self.assertEqual(achados, [("", (4, 30, 10, 10))])


class TestMoldura(unittest.TestCase):
    """A moldura que o Wine desenha POR DENTRO da janela.

    Sem esta regra, a coordenada de um controle sobre a captura do oraculo cai
    3 px a esquerda e 29 px acima do lugar -- e a medida sai plausivel e
    errada, que e o pior resultado possivel.
    """

    def test_sem_moldura_o_deslocamento_e_zero(self):
        self.assertEqual(
            check_carregado.deslocamento((522, 475), (522, 475), "x"), (0, 0))

    def test_com_moldura_o_deslocamento_e_3_29(self):
        self.assertEqual(
            check_carregado.deslocamento((135, 153), (129, 121), "x"), (3, 29))

    def test_tamanho_que_nao_e_nem_um_nem_outro_aborta(self):
        with self.assertRaises(check_carregado.CarregadoError):
            check_carregado.deslocamento((200, 100), (129, 121), "x")


if __name__ == "__main__":
    unittest.main()
