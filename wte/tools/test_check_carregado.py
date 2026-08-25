#!/usr/bin/env python3
"""Testes do `check_carregado.py` -- CORR-WTE-115.

A WTE-TASK-37 escreveu DOIS conferidores no mesmo commit e so um ganhou par de
teste. Este arquivo e o par que faltava.

## Onde a metade das recusas ja estava, e por que isso importa

**Nem tudo aqui e novo, e o achado da correcao foi esse.** As tres conferencias
da moldura e a dos retangulos moravam no `test_check_retorno.py` -- o irmao --,
porque foi ele que nasceu primeiro. Testar um modulo do arquivo de outro e como
a CORR-WTE-115 veio a acreditar que a recusa da moldura nao era exercitada: o
`ls` nao a achava, e ela estava la o tempo todo. Foram trazidas para ca, e o
irmao voltou a ser so sobre o `check_retorno`.

## O que e genuinamente novo

A recusa do `cliente()` -- formulario sem `ClientWidth` nem `Width` --, que era
a unica do modulo sem exercicio nenhum, e os dois caminhos bons dela: os 13
formularios que declaram `ClientWidth`, e os 5 que declaram `Width` e cujo
cliente e o declarado MENOS a moldura.

Nao abrem o `.exe`, nao dirigem janela e nao dependem das capturas para as
partes puras: montam o `.dfm` em `tempfile`.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import check_carregado as C
import check_retorno


def escreve(texto: str) -> Path:
    tmp = Path(tempfile.mkdtemp()) / "f.dfm"
    tmp.write_text(texto, encoding="utf-8")
    return tmp


# Um formulario com as duas formas de declarar tamanho, um blob de icone (que o
# parser NAO pode virar objeto) e um `TStaticText` sem nome -- que e o caso real
# do `MainForm` e o que faz a conta fechar em 37.
DFM_CLIENTE = """object ficha_x: Tficha_x
  ClientWidth = 100
  ClientHeight = 50
  Icon.Data = {
    0000010001001010
    1000
  }
  object TStaticText
    Left = 4
    Top = 30
    Width = 10
    Height = 10
  end
end
"""

DFM_WIDTH = """object ficha_y: Tficha_y
  Width = 106
  Height = 82
end
"""

DFM_SEM_TAMANHO = """object ficha_z: Tficha_z
  Caption = 'sem tamanho nenhum'
end
"""


class TestCliente(unittest.TestCase):
    """A recusa que nao tinha exercicio nenhum, e os dois caminhos bons."""

    def cliente(self, texto: str):
        caminho = escreve(texto)
        return C.cliente(check_retorno.le_arvore(caminho), caminho)

    def test_ClientWidth_e_lido_direto(self) -> None:
        self.assertEqual(self.cliente(DFM_CLIENTE), (100, 50))

    def test_Width_vira_cliente_menos_a_moldura(self) -> None:
        """Cinco dos 18 declaram `Width`/`Height`, e neles o cliente e o
        declarado menos a moldura -- 106x82 com 6x32 da 100x50, o mesmo
        formulario do caso acima por outro caminho."""
        self.assertEqual(self.cliente(DFM_WIDTH), (100, 50))
        self.assertEqual(self.cliente(DFM_WIDTH), self.cliente(DFM_CLIENTE))

    def test_sem_ClientWidth_nem_Width_aborta(self) -> None:
        """O ponto do caso: sem tamanho declarado nao ha cliente a calcular, e
        seguir daria coordenada sobre um retangulo inventado."""
        with self.assertRaises(C.CarregadoError) as ctx:
            self.cliente(DFM_SEM_TAMANHO)
        self.assertIn("sem ClientWidth nem Width", str(ctx.exception))


class TestMoldura(unittest.TestCase):
    """A moldura que o Wine desenha POR DENTRO da janela.

    Sem esta regra, a coordenada de um controle sobre a captura do oraculo cai
    3 px a esquerda e 29 px acima do lugar -- e a medida sai plausivel e
    errada, que e o pior resultado possivel.

    Os tres casos vieram do `test_check_retorno.py` (CORR-WTE-115).
    """

    def test_sem_moldura_o_deslocamento_e_zero(self) -> None:
        self.assertEqual(C.deslocamento((522, 475), (522, 475), "x"), (0, 0))

    def test_com_moldura_o_deslocamento_e_3_29(self) -> None:
        self.assertEqual(C.deslocamento((135, 153), (129, 121), "x"), (3, 29))

    def test_tamanho_que_nao_e_nem_um_nem_outro_aborta(self) -> None:
        with self.assertRaises(C.CarregadoError):
            C.deslocamento((200, 100), (129, 121), "x")

    def test_um_pixel_a_menos_ja_aborta(self) -> None:
        """A plantacao que a CORR-WTE-115 descreve: a captura do
        `ficha_dorsal` encolhida em UM pixel. A recusa nao e por ordem de
        grandeza -- e por igualdade, e tem de ser."""
        with self.assertRaises(C.CarregadoError) as ctx:
            C.deslocamento((134, 153), (129, 121), "ficha_dorsal.png")
        self.assertIn("134x153", str(ctx.exception))
        self.assertIn("129x121", str(ctx.exception))

    def test_a_mensagem_diz_por_que_isso_importa(self) -> None:
        """Recusa sem a razao vira `--force` na cabeca de quem a ve."""
        with self.assertRaises(C.CarregadoError) as ctx:
            C.deslocamento((200, 100), (129, 121), "x")
        self.assertIn("lugar errado", str(ctx.exception))


class TestRetangulos(unittest.TestCase):
    """Veio do `test_check_retorno.py` (CORR-WTE-115)."""

    def test_o_objeto_sem_nome_entra_na_conta(self) -> None:
        """Ha um `TStaticText` anonimo no `MainForm`, e os 37 o incluem."""
        caminho = escreve(DFM_CLIENTE)
        objetos = check_retorno.le_arvore(caminho)
        achados = C.retangulos(objetos, caminho, "TStaticText")
        self.assertEqual(achados, [("", (4, 30, 10, 10))])


class TestEstadoDeHoje(unittest.TestCase):
    """O que pega alguem apagando uma captura sem regerar o TSV."""

    def linhas(self):
        try:
            return C.mede()
        except ModuleNotFoundError as e:
            self.skipTest(f"sem {e.name} -- as capturas nao foram lidas")

    def test_os_dezoito_formularios_sao_medidos(self) -> None:
        self.assertEqual(len(self.linhas()), 18)

    def test_quinze_estao_fotografados_dos_dois_lados(self) -> None:
        dois = sum(1 for l in self.linhas()
                   if l["foto_oraculo"] != "—" and l["foto_port"] != "—")
        self.assertEqual(dois, 15)

    def test_o_TSV_em_disco_bate_com_a_medida(self) -> None:
        """O gerado e o que se le -- o gerador certo nao basta se o
        `carregado.tsv` nao tiver sido regerado."""
        _md, tsv = C.render(self.linhas())
        self.assertEqual(C.SAIDA_TSV.read_text(encoding="utf-8"), tsv)


if __name__ == "__main__":
    unittest.main()
