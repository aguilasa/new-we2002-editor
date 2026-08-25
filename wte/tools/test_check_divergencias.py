#!/usr/bin/env python3
"""Testes do check_divergencias.py -- CORR-WTE-106.

O criterio da [WTE-TASK-35](../../docs/tasks/35-divergencias-deliberadas.md)
dizia *"mecanizado nos dois sentidos, com as tres recusas vistas"*. **Ver nao e
o mesmo que deixar visto:** as recusas foram observadas na execucao e nao
sobreviveram a ela. E a regra que o proprio repositorio escreveu, no cabecalho
do `test_check_fase4.py`: *guarda nunca exercitada e guarda ausente*.

Este arquivo e o par que todos os irmaos de recusa ja tinham -- `check_fase1`
a `check_fase4`, `check_golden`, `check_preco`, `check_edicao`,
`check_glifos_disabled`, `cobertura_gate`, `gravacao_controle`, `spec_index`.
As ferramentas sem teste que sobram medem o mundo de fora (o `.exe`, pelos
`check_barras`/`check_bitfields`/`sonda_dorsal`/`dump_*`, e a LCL instalada,
pelo `check_lcl_combo`), e nelas a saida E a medicao.

## Os quatro sentidos, e por que sao quatro e nao dois

A conferencia e nos DOIS sentidos por lado, e cada um pega uma coisa diferente:

| # | O que se planta | O que ele prova |
|---|---|---|
| 1 | a isencao some da ferramenta | entrada viva sem isencao -> **prosa vencida** |
| 2 | a secao some do documento | isencao viva sem entrada -> **buraco** |
| 3 | uma isencao RETIRADA volta | a retirada desfeita pela porta dos fundos |
| 4 | um roteiro ganha `conhecida:` | faixa nova torna a secao 8 falsa |

Os testes montam a arvore em `tempfile` e apontam os caminhos do modulo para
ela: nao abrem o `.exe`, nao precisam de `DISPLAY` nem de Wine, e rodam num
clone sem a pasta `we-team-editor/`.
"""

from __future__ import annotations

import contextlib
import io
import re
import tempfile
import unittest
from pathlib import Path

import check_divergencias as C


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


class Base(unittest.TestCase):
    """Um espelho minimo da arvore: o documento, as ferramentas, os roteiros.

    O espelho e montado a partir das tabelas REAIS do modulo, e nao de uma copia
    literal delas -- assim uma excecao nova no `EXCECOES` entra nestes testes
    sozinha, em vez de os deixar medindo um mundo que nao existe mais.
    """

    def monta(self, *, secoes=None, ferramentas=None, roteiros=None):
        d = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (d / "re").mkdir()
        (d / "tools").mkdir()
        (d / "roteiros").mkdir()

        if secoes is None:
            secoes = sorted({e["secao"] for e in C.EXCECOES}
                            | {r["secao"] for r in C.RETIRADAS})
        doc = "# divergencias\n\n" + "".join(
            f"## {n}. secao {n}\n\nprosa.\n\n" for n in secoes)
        (d / "re" / "divergencias.md").write_text(doc, encoding="utf-8")

        if ferramentas is None:
            ferramentas = {}
            for e in C.EXCECOES:
                ferramentas.setdefault(e["arquivo"], "")
                ferramentas[e["arquivo"]] += self.corpo_que_casa(e) + "\n"
            for r in C.RETIRADAS:
                ferramentas.setdefault(r["arquivo"], "")
        for nome, corpo in ferramentas.items():
            (d / "tools" / nome).write_text(corpo, encoding="utf-8")

        for nome, corpo in (roteiros or {"golden-01-arranque": "alvo: original\n"}).items():
            (d / "roteiros" / f"{nome}.txt").write_text(corpo, encoding="utf-8")

        # `ROOT` entra junto porque o modulo relata o caminho como
        # `DOC.relative_to(ROOT)`, e um espelho em /tmp nao e subpath da arvore
        # real -- sem isto o teste estoura com `ValueError` no lugar de medir a
        # recusa. E artefato do espelho, nao defeito do gate: em uso normal o
        # documento mora sempre sob a raiz.
        self.enterContext(_aponta(
            C, ROOT=d, DOC=d / "re" / "divergencias.md", TOOLS=d / "tools",
            ROTEIROS=d / "roteiros"))
        return d

    @staticmethod
    def corpo_que_casa(excecao: dict) -> str:
        """Uma linha que satisfaz o predicado daquela excecao.

        Os predicados de hoje sao `"glifo_cinza"`, `^INVARIANTES = \\{` e
        `ULTIMO_SLOT_PRECADO`. O primeiro e o terceiro casam como substring; o
        segundo esta ancorado em inicio de linha, entao a linha e escrita
        literal a partir do proprio padrao, sem as ancoras.
        """
        return excecao["predicado"].replace("^", "").replace("\\", "")

    def problemas(self) -> list[str]:
        return C.mede()["problemas"]


class TestEstadoDeHoje(Base):
    """A arvore REAL passa -- e este e o caso que pega quem mexer nela."""

    def test_o_repositorio_de_hoje_nao_tem_problema(self) -> None:
        """Sem espelho: o modulo aponta para a arvore de verdade.

        Se alguem tirar uma isencao sem tirar a entrada, ou o contrario, este
        caso reprova antes do `make -C wte check`.
        """
        self.assertEqual(C.mede()["problemas"], [])

    def test_o_espelho_montado_das_tabelas_reais_passa(self) -> None:
        """Se este reprovar, o espelho e que esta errado, nao o gate."""
        self.monta()
        self.assertEqual(self.problemas(), [])


class TestExcecaoQueSome(Base):
    """Sentido 1: entrada viva e isencao morta -> prosa vencida."""

    def test_excecao_sumida_da_ferramenta_reprova(self) -> None:
        alvo = C.EXCECOES[0]
        ferramentas = {}
        for e in C.EXCECOES:
            ferramentas.setdefault(e["arquivo"], "")
            if e["nome"] != alvo["nome"]:
                ferramentas[e["arquivo"]] += self.corpo_que_casa(e) + "\n"
        for r in C.RETIRADAS:
            ferramentas.setdefault(r["arquivo"], "")
        self.monta(ferramentas=ferramentas)
        p = self.problemas()
        self.assertTrue(any(alvo["nome"] in x and "PROSA VENCIDA" in x
                            for x in p), p)

    def test_ferramenta_inteira_ausente_reprova_com_outra_frase(self) -> None:
        """Arquivo que sumiu nao e o mesmo defeito que predicado que sumiu."""
        ferramentas = {r["arquivo"]: "" for r in C.RETIRADAS}
        self.monta(ferramentas=ferramentas)
        p = self.problemas()
        self.assertTrue(any("nao existe" in x for x in p), p)


class TestSecaoQueSome(Base):
    """Sentido 2: isencao viva e entrada morta -> buraco."""

    def test_excecao_sem_secao_reprova(self) -> None:
        alvo = C.EXCECOES[-1]
        outras = sorted(({e["secao"] for e in C.EXCECOES}
                         | {r["secao"] for r in C.RETIRADAS})
                        - {alvo["secao"]})
        self.monta(secoes=outras)
        p = self.problemas()
        self.assertTrue(any(alvo["nome"] in x and "BURACO" in x for x in p), p)

    def test_retirada_sem_secao_reprova(self) -> None:
        alvo = C.RETIRADAS[0]
        outras = sorted(({e["secao"] for e in C.EXCECOES}
                         | {r["secao"] for r in C.RETIRADAS})
                        - {alvo["secao"]})
        self.monta(secoes=outras)
        p = self.problemas()
        self.assertTrue(any(alvo["nome"] in x and "retirada" in x for x in p), p)

    def test_documento_ausente_aborta(self) -> None:
        d = self.monta()
        (d / "re" / "divergencias.md").unlink()
        with self.assertRaises(C.DivergError):
            C.mede()


class TestRetiradaQueVolta(Base):
    """Sentido 3: a isencao retirada reaparece pela porta dos fundos."""

    def test_retirada_que_volta_reprova(self) -> None:
        alvo = C.RETIRADAS[0]
        ferramentas = {}
        for e in C.EXCECOES:
            ferramentas.setdefault(e["arquivo"], "")
            ferramentas[e["arquivo"]] += self.corpo_que_casa(e) + "\n"
        ferramentas.setdefault(alvo["arquivo"], "")
        ferramentas[alvo["arquivo"]] += f'grupos = ("{alvo["nome"]}",)\n'
        self.monta(ferramentas=ferramentas)
        p = self.problemas()
        self.assertTrue(any(alvo["nome"] in x and "VOLTOU" in x for x in p), p)

    def test_a_mencao_entre_crases_nao_conta(self) -> None:
        """O casamento e por ASPAS, e isso e escolha, nao acaso.

        O `compara_tela.py` de verdade CITA `pendente_32` na prosa que explica a
        remocao. Ele passa hoje porque a citacao usa crase, e o predicado e
        `"nome"` com aspas. Sem este caso, ninguem saberia que a diferenca e
        load-bearing -- e a proxima pessoa a "melhorar" o predicado para uma
        busca por substring derrubaria o gate com um comentario.
        """
        alvo = C.RETIRADAS[0]
        ferramentas = {}
        for e in C.EXCECOES:
            ferramentas.setdefault(e["arquivo"], "")
            ferramentas[e["arquivo"]] += self.corpo_que_casa(e) + "\n"
        ferramentas.setdefault(alvo["arquivo"], "")
        ferramentas[alvo["arquivo"]] += (
            f"# o grupo `{alvo['nome']}` foi retirado -- ver a secao "
            f"{alvo['secao']}\n")
        self.monta(ferramentas=ferramentas)
        self.assertEqual(self.problemas(), [])

    def test_a_mencao_entre_aspas_num_comentario_conta(self) -> None:
        """O outro lado da escolha acima, e ele e o custo dela.

        Aspas em comentario reprovam como se fossem codigo. E falso positivo, e
        e o preco de um predicado textual -- deixado escrito aqui para que a
        proxima pessoa o encontre medido em vez de o descobrir num gate
        vermelho.
        """
        alvo = C.RETIRADAS[0]
        ferramentas = {}
        for e in C.EXCECOES:
            ferramentas.setdefault(e["arquivo"], "")
            ferramentas[e["arquivo"]] += self.corpo_que_casa(e) + "\n"
        ferramentas.setdefault(alvo["arquivo"], "")
        ferramentas[alvo["arquivo"]] += f'# o grupo "{alvo["nome"]}" saiu\n'
        self.monta(ferramentas=ferramentas)
        p = self.problemas()
        self.assertTrue(any("VOLTOU" in x for x in p), p)


class TestFaixaConhecida(Base):
    """Sentido 4: faixa nova na bateria de bytes torna a secao 8 falsa."""

    def test_roteiro_com_faixa_conhecida_reprova(self) -> None:
        self.monta(roteiros={"golden-01-arranque":
                             "alvo: original\nconhecida: 1..2\n"})
        p = self.problemas()
        self.assertTrue(any("conhecida" in x and "golden-01-arranque" in x
                            for x in p), p)

    def test_sem_faixa_nenhuma_passa(self) -> None:
        self.monta(roteiros={"golden-01-arranque": "alvo: original\n",
                             "golden-02-gravacao": "alvo: original\n"})
        self.assertEqual(self.problemas(), [])

    def test_a_bateria_de_hoje_nao_declara_faixa(self) -> None:
        """A afirmacao da secao 8, contra o disco de verdade."""
        self.assertEqual(C.mede()["com_faixa"], [])

    def test_conhecida_no_meio_da_linha_nao_conta(self) -> None:
        """O padrao e ancorado em inicio de linha, e a prosa dos roteiros usa a
        palavra: `# a faixa conhecida foi portada` nao e uma declaracao."""
        self.monta(roteiros={"golden-01-arranque":
                             "alvo: original\n# nenhuma faixa conhecida\n"})
        self.assertEqual(self.problemas(), [])


class TestSaida(Base):
    """O codigo de saida, que e o que o `make -C wte check` le.

    A saida do `main()` e engolida de proposito: sem isso o relatorio de uma
    recusa PLANTADA aparece no meio do `make -C wte check`, e quem estiver
    lendo o gate ve a mensagem de um problema que nao existe.
    """

    def codigo(self) -> int:
        with (contextlib.redirect_stderr(io.StringIO()),
              contextlib.redirect_stdout(io.StringIO())):
            return C.main([])

    def test_arvore_sa_sai_zero(self) -> None:
        self.monta()
        self.assertEqual(self.codigo(), 0)

    def test_problema_sai_dois(self) -> None:
        self.monta(roteiros={"golden-01-arranque":
                             "alvo: original\nconhecida: 1..2\n"})
        self.assertEqual(self.codigo(), 2)

    def test_documento_ausente_sai_dois(self) -> None:
        d = self.monta()
        (d / "re" / "divergencias.md").unlink()
        self.assertEqual(self.codigo(), 2)


class TestSecoes(unittest.TestCase):
    """A leitura dos cabecalhos, que e por numero e nao por titulo."""

    def test_le_o_numero_e_nao_o_titulo(self) -> None:
        t = "## 2. Glifos\n\n## 9. Retiradas\n"
        self.assertEqual(C.secoes(t), {2: "Glifos", 9: "Retiradas"})

    def test_titulo_reescrito_nao_derruba_o_gate(self) -> None:
        """Deliberado, e esta escrito no gerador: renomear a secao pode,
        remove-la nao."""
        self.assertEqual(set(C.secoes("## 2. Outro nome qualquer\n")), {2})

    def test_cabecalho_sem_numero_nao_entra(self) -> None:
        self.assertEqual(C.secoes("## Sem numero\n### 3. fundo demais\n"), {})


class TestPendenciaDeclarada(unittest.TestCase):
    """A guarda da CORR-WTE-114: a direcao que as tabelas nao cobriam.

    O gate confere EXCECAO DE FERRAMENTA contra entrada. Achado de divergencia
    escrito numa task e sem entrada no registro passava batido -- e foi o que
    aconteceu com as tres candidatas da WTE-TASK-37, uma delas se declarando
    *"ainda sem entrada aqui"* no markdown de uma task ja `concluido`.

    O alcance e estreito, e a palavra que o define e `ainda`: o enunciado da
    REGRA (*"uma excecao no golden sem entrada aqui e buraco"*) vive em cinco
    lugares e nao e pendencia nenhuma.
    """

    def casa(self, texto: str) -> bool:
        return any(p.search(texto) for p in C.PENDENCIA_DECLARADA)

    def test_a_declaracao_de_pendencia_e_pega(self) -> None:
        for texto in ("Divergencia deliberada, ainda sem entrada aqui.",
                      "e esta ainda  sem  entrada  aqui",
                      "ainda sem entrada no registro"):
            with self.subTest(texto=texto):
                self.assertTrue(self.casa(texto))

    def test_o_enunciado_da_regra_nao_e_alvo(self) -> None:
        """Guarda que erra e guarda que se desliga.

        Esta frase e a que define o gate, e aparece em cinco arquivos vivos.
        Alargar o padrao para `sem entrada aqui` cru marcaria os cinco.
        """
        for texto in ("uma excecao no golden sem entrada aqui e buraco",
                      "Excecao sem entrada aqui e BURACO",
                      "exceção no golden sem entrada aqui é buraco"):
            with self.subTest(texto=texto):
                self.assertFalse(self.casa(texto))

    def test_a_arvore_de_hoje_nao_tem_pendencia_declarada(self) -> None:
        """Depois da CORR-WTE-114, as tres tem destino."""
        self.assertEqual(C.pendencias_declaradas(), [])

    def test_o_registro_e_o_indice_ficam_de_fora(self) -> None:
        """Quem CITA a frase para a descrever nao pode ser marcado.

        O markdown de cada correcao e o `correcoes-progresso.md` citam-na, e a
        diferenca entre citar e declarar nao se le de uma regex -- se le de
        onde a frase esta.
        """
        self.assertIn("correcoes-progresso.md",
                      Path(C.__file__).read_text(encoding="utf-8"))
        self.assertIn("CORR-WTE-",
                      Path(C.__file__).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
