#!/usr/bin/env python3
"""Testes do check_fase2.py (WTE-TASK-14).

Montam uma arvore de fase 2 sintetica num diretorio temporario -- NAO abrem o
we-team-editor.exe e nao leem a arvore real. Cobrem as rotas de **aborto**, que
sao o que o `--check` verde sobre a arvore boa nunca exercita: stub que sumiu,
stub na unidade errada, formulario sem `.lfm`, formulario sem veredito visual,
`eventos.md` sem achado.

Aborto e o comportamento desejado: residuo e falha, como no `FORBIDDEN` do
`port_database.py`. Um fechamento de fase que passa com stub faltando entrega
uma casca errada para a fase 4 inteira.
"""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import check_fase2


TSV = ("endereco\thandler\tformulario\tcomponente\tevento\tgrupo\tregra\tnota\n"
       "0x00402b40\tBitBtn1Click\tficha_dorsal\tBitBtn1\tOnClick\tauxiliar\tR6\t\n"
       "0x004120a4\tlista_equiposChange\tMainForm\tlista_equipos\tOnChange\tcarga\tR8\t\n")

UNIDADE = """\
{{ Esqueleto gerado por `wte/tools/dfm2lfm.py`.
  **NAO EDITAR A MAO.** }}
unit {unidade};
interface
type
  T{form} = class(TForm)
  end;
implementation
{corpo}
end.
"""

LFM = "object {form}: T{form}\n  Left = 0\n  Top = 0\nend\n"

VISUAL = """\
# visual

## Veredito por formulário

| Formulário | Original | Veredito |
|---|---|---|
{linhas}

## Outra seção
"""

EVENTOS = "# eventos\n\n## Achado 1 — algo\n\ntexto\n"


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        raiz = Path(self._tmp.name)
        self.src = raiz / "wte" / "src"
        self.forms = raiz / "wte" / "forms"
        self.dfm = raiz / "wte" / "re" / "dfm"
        self.re_ = raiz / "wte" / "re"
        for d in (self.src, self.forms, self.dfm):
            d.mkdir(parents=True, exist_ok=True)

        self._antigo = {k: getattr(check_fase2, k) for k in
                        ("ROOT", "SRC", "FORMS", "DFM", "PUB", "VISUAL",
                         "EVENTOS", "LPR", "OUT", "PLANO")}
        check_fase2.ROOT = raiz
        check_fase2.SRC = self.src
        check_fase2.FORMS = self.forms
        check_fase2.DFM = self.dfm
        check_fase2.PUB = self.re_ / "published_methods.tsv"
        check_fase2.VISUAL = self.re_ / "visual.md"
        check_fase2.EVENTOS = self.re_ / "eventos.md"
        check_fase2.LPR = raiz / "wte" / "wte.lpr"
        check_fase2.OUT = self.re_
        check_fase2.PLANO = raiz / "docs" / "PLAN-WTE-LAZARUS.md"
        check_fase2.PLANO.parent.mkdir(parents=True, exist_ok=True)

        self.arvore_boa()

    def tearDown(self):
        for k, v in self._antigo.items():
            setattr(check_fase2, k, v)
        self._tmp.cleanup()

    def escreve_plano(self):
        """O plano com a frase da §4.4 que a medida da arvore corrente produz.

        A frase sai do proprio `frase_da_fracao`, e nao de um literal: a arvore
        do fixture nao tem as linhas da arvore real, e fixar o numero aqui
        obrigaria a mexer no teste a cada componente novo do fixture.
        """
        check_fase2.PLANO.write_text(
            "# plano\n\n**Medido: "
            + check_fase2.frase_da_fracao(check_fase2.inventario())
            + ".**\n", encoding="utf-8")

    def arvore_boa(self):
        check_fase2.PUB.write_text(TSV, encoding="utf-8")
        check_fase2.LPR.write_text("program wte;\nbegin\nend.\n",
                                   encoding="utf-8")
        self.escreve_unidade("ep2002_dorsal", "ficha_dorsal",
                             ["ficha_dorsal.BitBtn1Click"])
        self.escreve_unidade("ep2002_mainform", "MainForm",
                             ["MainForm.lista_equiposChange"])
        for form in ("ficha_dorsal", "MainForm"):
            (self.dfm / f"{form}.dfm").write_text(LFM.format(form=form),
                                                 encoding="utf-8")
        (self.forms / "ep2002_dorsal.lfm").write_text(
            LFM.format(form="ficha_dorsal"), encoding="utf-8")
        (self.forms / "ep2002_mainform.lfm").write_text(
            LFM.format(form="MainForm"), encoding="utf-8")
        self.escreve_visual(["ficha_dorsal", "MainForm"])
        check_fase2.EVENTOS.write_text(EVENTOS, encoding="utf-8")
        self.escreve_plano()

    def escreve_unidade(self, unidade, form, chaves):
        corpo = "\n".join(f"  REStub('{c}');" for c in chaves)
        (self.src / f"{unidade}.pas").write_text(
            UNIDADE.format(unidade=unidade, form=form, corpo=corpo),
            encoding="utf-8")

    def escreve_visual(self, forms, origem="sim", veredito="sem ressalva"):
        linhas = "\n".join(f"| `{f}` | {origem} | {veredito} |" for f in forms)
        check_fase2.VISUAL.write_text(VISUAL.format(linhas=linhas),
                                      encoding="utf-8")

    def erro(self):
        with self.assertRaises(check_fase2.CheckError) as ctx:
            check_fase2.gerar()
        return str(ctx.exception)


class TestArvoreBoa(Base):
    def test_gera_e_conta(self):
        files = check_fase2.gerar()
        md = files["fase-2.md"]
        self.assertIn("| Handlers do `published_methods.tsv` com stub próprio "
                      "| **2** |", md)
        self.assertIn("| Formulários com `.lfm` e `.dfm` pareados | **2** |",
                      md)
        self.assertIn("| Formulários com veredito visual escrito | **2** |", md)
        self.assertIn("| …confrontados com captura do original / só com o DFM "
                      "| **2** / **0** |", md)

    def test_guarda_o_veredito_e_nao_a_coluna_original(self):
        """O grupo 3 da regex e o veredito; o grupo 2 e a origem.

        Ate a CORR-WTE-028 esta funcao guardava o grupo 2 e chamava o resultado
        de veredito. So `len()` era lido, entao nada ficava vermelho -- e por
        isso o assert aqui e sobre o VALOR, nao sobre a contagem.
        """
        forms = check_fase2.conferir_formularios()
        vereditos = check_fase2.conferir_vereditos(forms)
        for form in forms:
            origem, veredito = vereditos[form]
            self.assertEqual(veredito, "sem ressalva")
            self.assertEqual(origem, "sim")
        self.assertEqual(check_fase2.contar_origens(vereditos),
                         (len(forms), 0))

    def test_conta_origem_com_negrito_e_com_dfm(self):
        # A tabela real escreve `**sim**` numa das linhas; negrito e o mesmo
        # valor. E `DFM` cai do outro lado da conta.
        forms = check_fase2.conferir_formularios()
        self.escreve_visual(forms, origem="**sim**")
        self.assertEqual(
            check_fase2.contar_origens(
                check_fase2.conferir_vereditos(forms)), (len(forms), 0))
        self.escreve_visual(forms, origem="DFM")
        self.assertEqual(
            check_fase2.contar_origens(
                check_fase2.conferir_vereditos(forms)), (0, len(forms)))

    def test_separa_gerado_de_escrito_a_mao(self):
        # Uma unidade sem a marca do gerador conta como escrita a mao.
        (self.src / "retrace.pas").write_text(
            "unit retrace;\ninterface\nimplementation\nend.\n",
            encoding="utf-8")
        inv = check_fase2.inventario()
        self.assertEqual(len(inv["pas_gerados"]), 2)
        self.assertEqual(sorted(n for n, _ in inv["pas_mao"]),
                         ["src/retrace.pas", "wte.lpr"])

    def test_hex_de_blob_nao_conta_como_estrutura(self):
        (self.forms / "ep2002_mainform.lfm").write_text(
            "object MainForm: TMainForm\n"
            "  Icon.Data = {\n"
            "    0000010001001010\n"
            "    AABBCCDDEEFF0011\n"
            "  }\n"
            "  Left = 0\n"
            "end\n", encoding="utf-8")
        inv = check_fase2.inventario()
        # 3 linhas de hex (as duas de dados mais a que fecha), 4 de estrutura.
        self.assertEqual(inv["lfm_hex"], 3)
        self.assertEqual(inv["lfm_estrutura"], 4 + 4)

    def test_check_reclama_quando_o_md_esta_velho(self):
        # do_check/do_write falam em stdout e stderr; calar os dois mantem a
        # saida de `make -C wte check` legivel -- ERRO esperado no meio da
        # bateria ensina a ignorar vermelho.
        files = check_fase2.gerar()
        (self.re_ / "fase-2.md").write_text("# velho\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(check_fase2.do_check(files), 1)
            check_fase2.do_write(files)
            self.assertEqual(check_fase2.do_check(files), 0)


class TestAborta(Base):
    def test_plano_com_fracao_velha(self):
        # A guarda que existe para o numero da §4.4 nao apodrecer em silencio.
        # Ela apodreceria a CADA handler implementado: o corpo sai do `.pas`
        # gerado e entra num `.inc` escrito a mao, e a fracao se move sozinha.
        check_fase2.PLANO.write_text(
            "# plano\n\n**Medido: 99,9% do Pascal da casca é saída de "
            "gerador** — 1 linhas geradas contra 1 escritas à mão.**\n",
            encoding="utf-8")
        self.assertIn("nao traz a fracao medida hoje", self.erro())

    def test_plano_ausente(self):
        check_fase2.PLANO.unlink()
        self.assertIn("nao existe", self.erro())

    def test_origem_fora_de_sim_ou_dfm(self):
        # Valor novo na coluna `Original` nao pode cair calado no lado "so
        # DFM": o par publicado no fase-2.md deixaria de ser medida.
        self.escreve_visual(check_fase2.conferir_formularios(),
                            origem="talvez")
        self.assertIn("coluna `Original` fora de sim/DFM", self.erro())

    def test_stub_faltando(self):
        self.escreve_unidade("ep2002_mainform", "MainForm", [])
        self.assertIn("0 ocorrencia", self.erro())

    def test_stub_duplicado(self):
        self.escreve_unidade("ep2002_mainform", "MainForm",
                             ["MainForm.lista_equiposChange",
                              "MainForm.lista_equiposChange"])
        # duas ocorrencias no MESMO arquivo contam como um dono; o que pega
        # duplicata entre arquivos e o len(donos) != 1
        self.escreve_unidade("ep2002_dorsal", "ficha_dorsal",
                             ["ficha_dorsal.BitBtn1Click",
                              "MainForm.lista_equiposChange"])
        self.assertIn("2 ocorrencia", self.erro())

    def test_stub_na_unidade_errada(self):
        # o stub do MainForm mora numa unidade que nao declara TMainForm
        self.escreve_unidade("ep2002_mainform", "OutraCoisa",
                             ["MainForm.lista_equiposChange"])
        self.assertIn("nao declara TMainForm", self.erro())

    def test_formulario_sem_lfm(self):
        (self.forms / "ep2002_mainform.lfm").unlink()
        self.assertIn(".dfm contra", self.erro())

    def test_lfm_que_nao_casa_com_dfm_nenhum(self):
        (self.forms / "ep2002_mainform.lfm").write_text(
            LFM.format(form="ficha_inventada"), encoding="utf-8")
        self.assertIn("sem .dfm", self.erro())

    def test_formulario_sem_veredito_visual(self):
        self.escreve_visual(["MainForm"])
        msg = self.erro()
        self.assertIn("sem veredito", msg)
        self.assertIn("ficha_dorsal", msg)

    def test_visual_sem_a_secao_de_veredito(self):
        check_fase2.VISUAL.write_text("# visual\n\n## Outra\n",
                                      encoding="utf-8")
        self.assertIn("Veredito por formulario", self.erro())

    def test_eventos_sem_achado(self):
        check_fase2.EVENTOS.write_text("# eventos\n\nnada aqui\n",
                                       encoding="utf-8")
        self.assertIn("nenhum '## Achado'", self.erro())

    def test_sem_tsv(self):
        check_fase2.PUB.unlink()
        self.assertIn("nao existe", self.erro())

    def test_sem_unidade_gerada(self):
        for pas in self.src.glob("*.pas"):
            pas.write_text("unit x;\ninterface\nimplementation\nend.\n",
                           encoding="utf-8")
        self.assertIn("NAO EDITAR A MAO", self.erro())


if __name__ == "__main__":
    unittest.main()
