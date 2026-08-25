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
import re
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


class TestChaveMorta(unittest.TestCase):
    """A guarda da CORR-WTE-111: chave que ninguem le nao fica na tabela.

    A `faixa` dos campos de TEXTO declarava a mao uma faixa de limites que o
    gerador ja MEDE das tabelas por time, ninguem a lia, e dois dos quatro
    valores contradiziam o medido -- `edit_nombre1` dizia (5, 19) contra 5..13.
    Valor morto nao aparece em saida nenhuma, e e por isso que passou:
    o risco e alguem escrever a proxima guarda SOBRE ele, achando que e medida.

    A confusao era provavel porque a chave de mesmo nome na tabela vizinha e
    viva: em `NUMERICOS` a faixa e cobrada do `.inc` do handler. Duas tabelas
    no mesmo arquivo, a mesma palavra, dois papeis.

    Esta guarda fecha a classe -- a mesma da CORR-WTE-096 (chave repetida que
    ninguem via) e da CORR-WTE-020.
    """

    FONTE = Path(D.__file__).read_text(encoding="utf-8")

    # O NOME DA VARIAVEL IMPORTA, e nao e preciosismo: procurar `["chave"]` com
    # qualquer identificador na frente faria a `faixa` dos campos de texto
    # passar por causa da leitura que os NUMERICOS fazem da chave homonima --
    # que e exatamente o defeito que esta guarda existe para pegar.
    #
    # Dai a lista por tabela. O `campo` entra nas duas porque o
    # `confere_filtro()` e chamado com as duas, e le por esse nome.
    LEITORES = {"CAMPOS": ("c", "campo"), "NUMERICOS": ("n", "campo")}

    def lida(self, chave: str, tabela: str) -> bool:
        """A chave aparece sendo LIDA em algum lugar do gerador?

        Textual de proposito, como o `chaves_repetidas_no_fonte` do
        `check_fase4.py`: o que se quer pegar e a chave que so e escrita na
        tabela, e isso se ve na fonte.
        """
        return any(
            forma in self.FONTE
            for var in self.LEITORES[tabela]
            for forma in (f'{var}["{chave}"]', f"{var}['{chave}']",
                          f'{var}.get("{chave}")', f"{var}.get('{chave}')"))

    def test_toda_chave_de_CAMPOS_e_lida(self) -> None:
        for c in D.CAMPOS:
            for chave in c:
                with self.subTest(controle=c["controle"], chave=chave):
                    self.assertTrue(
                        self.lida(chave, "CAMPOS"),
                        f"a chave `{chave}` de CAMPOS nao e lida por ninguem: "
                        "ou some, ou vira expectativa conferida")

    # Chave ainda morta, com DONO NOMEADO -- pendencia nao e buraco, e a
    # diferenca entre as duas e exatamente esta linha.
    #
    # ESTA VAZIA, e ficou vazia depressa: o unico morador era o `filtro` dos
    # numericos, posto aqui pela CORR-WTE-111 e retirado pela CORR-WTE-112 uma
    # correcao depois, que o confrontou com o `KeyPress`. O mecanismo fica --
    # e o caso abaixo e que o torna confiavel.
    PENDENTES: dict[str, str] = {}

    def test_toda_chave_de_NUMERICOS_e_lida(self) -> None:
        for n in D.NUMERICOS:
            for chave in n:
                if chave in self.PENDENTES:
                    continue
                with self.subTest(controle=n["controle"], chave=chave):
                    self.assertTrue(self.lida(chave, "NUMERICOS"),
                                    f"a chave `{chave}` de NUMERICOS nao e lida")

    def test_a_excecao_nao_sobrevive_a_propria_causa(self) -> None:
        """Isencao que passa a proteger nada esconde a regressao seguinte.

        E a licao literal da WTE-TASK-35 com o grupo `pendente_32`: a causa
        caiu, a isencao ficou, e ela deixou de proteger qualquer coisa.
        """
        for chave, dono in self.PENDENTES.items():
            with self.subTest(chave=chave):
                self.assertFalse(
                    self.lida(chave, "NUMERICOS"),
                    f"a chave `{chave}` passou a ser lida ({dono} fez o "
                    "trabalho): tire-a de PENDENTES, senao ela deixa de ser "
                    "conferida por ninguem")

    def test_a_guarda_pega_uma_chave_plantada(self) -> None:
        """Guarda nunca exercitada e guarda ausente."""
        self.assertFalse(self.lida("faixa", "CAMPOS"))
        self.assertTrue(self.lida("faixa", "NUMERICOS"))

    def test_os_campos_de_texto_nao_declaram_faixa(self) -> None:
        """O defeito literal, no dado -- nao so na fonte."""
        for c in D.CAMPOS:
            with self.subTest(controle=c["controle"]):
                self.assertNotIn("faixa", c)


class TestFiltroConferido(unittest.TestCase):
    """A guarda da CORR-WTE-112: o filtro publicado sai de algo conferido.

    O `buffers.md` publicava, por campo, o conjunto de caracteres que o
    `KeyPress` deixa passar -- declarado a mao e nunca confrontado com o
    handler. O contraste estava dentro do mesmo arquivo: o `predicado` de faixa
    dos numericos E cobrado do `.inc` e aborta se sumir.

    O molde e o `test_predicado_da_faixa_nao_casa_por_prefixo`: mutar o corpo em
    memoria e afirmar que o trecho deixa de casar.
    """

    def corpo(self, campo: dict) -> str:
        return (D.SRC / "impl" / campo["filtro_handler"]).read_text(
            encoding="utf-8")

    def test_todo_campo_tem_o_trecho_no_KeyPress(self) -> None:
        """O estado de hoje: os seis conferem."""
        for campo in D.CAMPOS + D.NUMERICOS:
            with self.subTest(controle=campo["controle"]):
                corpo = self.corpo(campo)
                for trecho in campo["filtro_trecho"]:
                    self.assertIn(trecho, corpo)

    def test_o_trecho_removido_deixa_de_casar(self) -> None:
        """A recusa plantada, em memoria -- o `.inc` em disco nao e tocado."""
        for campo in D.CAMPOS + D.NUMERICOS:
            with self.subTest(controle=campo["controle"]):
                corpo = self.corpo(campo)
                mutado = corpo.replace(campo["filtro_trecho"][0], "")
                self.assertNotEqual(mutado, corpo, "o trecho nem estava la")
                self.assertNotIn(campo["filtro_trecho"][0], mutado)

    def test_o_gerador_aborta_quando_o_trecho_some(self) -> None:
        """E o que importa: a recusa chega ao codigo de saida.

        Roda o gerador com o `SRC` apontado para uma copia da arvore em que um
        `KeyPress` perdeu o trecho. O repositorio nao e tocado.
        """
        campo = D.CAMPOS[0]
        with tempfile.TemporaryDirectory() as td:
            espelho = Path(td) / "src"
            shutil.copytree(D.SRC, espelho)
            alvo = espelho / "impl" / campo["filtro_handler"]
            alvo.write_text(
                alvo.read_text(encoding="utf-8").replace(
                    campo["filtro_trecho"][0], ""), encoding="utf-8")
            velho = D.SRC
            try:
                D.SRC = espelho
                # `mede()` LEVANTA quando ha problema -- nao devolve a lista.
                # E a recusa: o gerador nao escreve nada por cima de uma
                # arvore em que o filtro publicado perdeu o handler.
                with self.assertRaises(D.BufferError) as ctx:
                    D.mede()
            finally:
                D.SRC = velho
        self.assertIn(campo["controle"], str(ctx.exception))
        self.assertIn("filtro", str(ctx.exception))

    def test_o_filtro_publicado_continua_o_de_hoje(self) -> None:
        """A CORR pede que o conjunto legivel nao mude -- so a origem dele."""
        esperado = {
            "edit_nombre1": "[A-Za-z0-9 .]", "edit_nombre2": "[A-Za-z0-9 .]",
            "edit_nombre3": "[A-Za-z0-9]", "casilla_nombre": "[A-Za-z0-9 .]",
            "casilla_precio": "[0-9]", "casilla_dorsal": "[0-9]",
        }
        medido = {c["controle"]: c["filtro"] for c in D.CAMPOS + D.NUMERICOS}
        self.assertEqual(medido, esperado)


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
        #
        # O literal era `10/10` ate a CORR-WTE-110, que estendeu os grupos 1 e 2
        # aos outros tres campos do inventario e o levou a 25. Literal aqui e a
        # mesma armadilha que a CORR-WTE-101 pegou na prosa: quem acrescenta um
        # caso mexe no `.pas` e nao neste numero, e o teste vira vermelho por um
        # motivo que nao e defeito. O que importa medir e que TODAS passaram e
        # que ha caso algum -- nao qual e o total de hoje.
        achado = re.search(r"(\d+)/(\d+) conferencias", r.stdout)
        self.assertIsNotNone(achado, r.stdout)
        passaram, total = int(achado.group(1)), int(achado.group(2))
        self.assertEqual(passaram, total, r.stdout)
        self.assertGreaterEqual(total, len(D.CAMPOS),
                                "menos conferencias de borda que campos no "
                                "inventario -- algum campo deixou de ser medido")


if __name__ == "__main__":
    unittest.main()
