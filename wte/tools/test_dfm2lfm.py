#!/usr/bin/env python3
"""Testes do `dfm2lfm.py` -- stdlib pura, sem depender do `.exe`.

    python3 -m unittest discover wte/tools -p 'test_*.py'
    make -C wte test

Por que este arquivo existe
---------------------------

`dfm2lfm.py --check` verde prova que os 18 `.lfm` e as 18 unidades continuam
saindo dos 18 `.dfm`. Nao prova nada sobre o que os 18 formularios **nao**
contem, que e justamente onde o gerador decide:

- as rotas de aborto -- classe sem mapeamento, propriedade que nao esta nem em
  `ACEITA` nem em `DESCARTA`, identificador que a LCL nao conhece, handler no
  DFM e ausente do TSV, par `(classe, evento)` sem assinatura, blob ausente.
  Nenhuma dispara no corpus, e sao elas que separam "converteu" de "emitiu
  formulario parcial";
- construcoes do DFM textual que o `dfm_extract.py` sabe emitir e que os 18
  nao tem: `inherited`, `inline`, posicao explicita de filho;
- o caso limite da mascara do `--check`: o gabarito marca cada digito
  hexadecimal com um caractere impossivel, e um caractere *possivel* (`?`)
  casaria com o `Caption` de `ficha_creditos_equipo`. Ja aconteceu neste
  gerador, durante a WTE-TASK-10, e o teste existe para nao voltar.

Todos os DFM daqui sao montados em memoria; o `.exe` nunca e aberto, e
`wte/re/dfm/blobs/` -- que e gitignored -- nunca e lido. Os testes que olham o
corpus de verdade leem so os `.dfm` versionados.

Guarda de contrato entre geradores
----------------------------------

O `wte/tools/README.md` exige guarda para o que dois geradores compartilham.
`dfm2lfm.py` nao copia codigo de ninguem, mas depende de um **formato** que o
`dfm_extract.py` escreve: a referencia `{blob <arquivo> <tamanho>
sha256:<hash>}`. Sao dois arquivos com a mesma sintaxe em lados opostos, e uma
mudanca de um lado so quebraria a conversao no lugar mais caro (blob perdido,
que so aparece na comparacao visual da WTE-TASK-12). `TestContratoBlob`
alimenta a regex do leitor com o texto que o escritor produz.

Isto NAO e um gerador
---------------------

Nao aceita `--check` e nao entra na bateria do `make -C wte check` por
wildcard -- o Makefile filtra `tools/test_*.py` de `GENERATORS` e os roda pelo
alvo `test`, do qual `check` depende. Ver `wte/tools/README.md`.
"""

from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dfm2lfm as g  # noqa: E402
import dfm_extract as e  # noqa: E402


# ------------------------------------------------------------- utilitarios --


def converte_um(texto: str, formulario: str = "ficha_x",
                blobs: dict[str, bytes] | None = None) -> str:
    """Le um DFM sintetico e devolve o `.lfm`, ignorando os descartes."""
    raiz = g.ler_dfm(formulario, texto)
    return g.emite_lfm(raiz, formulario, blobs, [],
                       g.nomes_substituidos(raiz))


def descartes_de(texto: str, formulario: str = "ficha_x") -> list:
    raiz = g.ler_dfm(formulario, texto)
    fora: list = []
    g.emite_lfm(raiz, formulario, None, fora, g.nomes_substituidos(raiz))
    return fora


ASSINATURA_MOUSE = g.ASSINATURAS["mouse"][0]

FORM_MINIMO = """\
object ficha_x: Tficha_x
  Left = 1
  Top = 2
  OldCreateOrder = False
  PixelsPerInch = 96
  TextHeight = 13
end
"""


# ------------------------------------------------------------------ leitor --


class TestLeitor(unittest.TestCase):
    def test_arvore_aninhada(self):
        raiz = g.ler_dfm("ficha_x", """\
object ficha_x: Tficha_x
  Left = 1
  object Grupo: TGroupBox
    Left = 2
    object Rotulo: TLabel
      Left = 3
    end
  end
  object Fim: TLabel
    Left = 4
  end
end
""")
        self.assertEqual(raiz.cls, "Tficha_x")
        self.assertEqual([f.nome for f in raiz.filhos], ["Grupo", "Fim"])
        self.assertEqual(raiz.filhos[0].filhos[0].nome, "Rotulo")
        self.assertEqual(len(list(g._todos(raiz))), 4)

    def test_objeto_sem_nome(self):
        # Ha um no MainForm: `object TStaticText`, sem nome. O DFM nao lhe deu
        # nome e o gerador nao inventa um.
        raiz = g.ler_dfm("ficha_x", """\
object ficha_x: Tficha_x
  object TStaticText
    Left = 1
  end
end
""")
        self.assertEqual(raiz.filhos[0].nome, "")
        self.assertEqual(raiz.filhos[0].cls, "TStaticText")

    def test_lista_de_strings_multilinha(self):
        raiz = g.ler_dfm("ficha_x", """\
object ficha_x: Tficha_x
  object Combo: TComboBox
    Items.Strings = (
      'a  '
      'b')
    Left = 1
  end
end
""")
        prop = raiz.filhos[0].props[0]
        self.assertEqual(prop.nome, "Items.Strings")
        self.assertEqual(prop.linhas,
                         ["(", "      'a  '", "      'b')"])

    def test_referencia_de_blob(self):
        sha = "0" * 64
        raiz = g.ler_dfm("ficha_x", f"""\
object ficha_x: Tficha_x
  Icon.Data = {{blob ficha_x.Icon.Data.bin 4 sha256:{sha}}}
end
""")
        blob = raiz.props[0].blob
        self.assertEqual(blob.arquivo, "ficha_x.Icon.Data.bin")
        self.assertEqual(blob.tamanho, 4)
        self.assertEqual(blob.sha256, sha)


class TestLeitorAborta(unittest.TestCase):
    def um(self, texto: str) -> str:
        with self.assertRaises(g.Dfm2LfmError) as ctx:
            g.ler_dfm("ficha_x", texto)
        return str(ctx.exception)

    def test_inherited(self):
        # `dfm_extract.py` sabe emitir; os 18 nao tem. Converter sem decidir a
        # forma LFM daria saida plausivel e errada.
        msg = self.um("inherited ficha_x: Tficha_x\nend\n")
        self.assertIn("inherited", msg)

    def test_inline(self):
        self.assertIn("inline", self.um("inline ficha_x: Tficha_x\nend\n"))

    def test_posicao_explicita_de_filho(self):
        msg = self.um("object ficha_x: Tficha_x\n"
                      "  object A: TLabel [2]\n  end\nend\n")
        self.assertIn("[n]", msg)

    def test_end_sobrando(self):
        self.assertIn("'end' sem objeto",
                      self.um("object ficha_x: Tficha_x\nend\nend\n"))

    def test_end_faltando(self):
        msg = self.um("object ficha_x: Tficha_x\n  object A: TLabel\n  end\n")
        self.assertIn("sem 'end'", msg)

    def test_linha_desconhecida(self):
        self.assertIn("nao e objeto",
                      self.um("object ficha_x: Tficha_x\n  ???\nend\n"))

    def test_propriedade_fora_de_objeto(self):
        self.assertIn("fora de objeto", self.um("  Left = 1\n"))

    def test_chave_que_nao_e_blob(self):
        msg = self.um("object ficha_x: Tficha_x\n  Icon.Data = {DEADBEEF}\nend\n")
        self.assertIn("referencia de blob", msg)

    def test_lista_sem_fechamento(self):
        msg = self.um("object ficha_x: Tficha_x\n  Items.Strings = (\n"
                      "    'a'\nend\n")
        self.assertIn("sem ')'", msg)

    def test_colecao_nao_suportada(self):
        msg = self.um("object ficha_x: Tficha_x\n  Coisas = <\nend\n")
        self.assertIn("nao esperado", msg)

    def test_dois_objetos_raiz(self):
        msg = self.um("object a: Ta\nend\nobject b: Tb\nend\n")
        self.assertIn("segundo objeto raiz", msg)

    def test_arquivo_vazio(self):
        self.assertIn("vazio", self.um(""))


# ------------------------------------------------------------ propriedades --


class TestPropriedades(unittest.TestCase):
    def test_aceita_sai_verbatim(self):
        lfm = converte_um("""\
object ficha_x: Tficha_x
  Caption = 'don''t'
  Font.Style = [fsBold, fsUnderline]
  Left = -8
end
""")
        self.assertIn("  Caption = 'don''t'\n", lfm)
        self.assertIn("  Font.Style = [fsBold, fsUnderline]\n", lfm)
        self.assertIn("  Left = -8\n", lfm)

    def test_descartada_some_do_lfm_e_e_registrada(self):
        lfm = converte_um(FORM_MINIMO)
        self.assertNotIn("OldCreateOrder", lfm)
        self.assertNotIn("TextHeight", lfm)
        self.assertIn("  PixelsPerInch = 96\n", lfm)

        ds = descartes_de(FORM_MINIMO)
        self.assertEqual([d.propriedade for d in ds],
                         ["OldCreateOrder", "TextHeight"])
        self.assertEqual([d.valor for d in ds], ["False", "13"])
        # O motivo tem de ser texto util, nao "nao suportado".
        for d in ds:
            self.assertGreater(len(d.motivo), 30)
            self.assertIn("LCL", d.motivo)

    def test_ctl3d_cai_nos_quatro_donos(self):
        for classe in ("TComboBox", "TListBox", "TRadioButton", "TScrollBar"):
            with self.subTest(classe=classe):
                ds = descartes_de(f"""\
object ficha_x: Tficha_x
  object C: {classe}
    Left = 1
    Ctl3D = False
    ParentCtl3D = False
  end
end
""")
                self.assertEqual([d.propriedade for d in ds],
                                 ["Ctl3D", "ParentCtl3D"])

    def test_propriedade_fora_das_duas_listas_aborta(self):
        # O caso "nao sei em que balde isto cai" -- diferente de "a LCL nao
        # tem", que e o balde DESCARTA. Emitir sem saber daria um LFM que so
        # falha ao abrir a janela.
        with self.assertRaises(g.Dfm2LfmError) as ctx:
            converte_um("object ficha_x: Tficha_x\n  Xyzzy = 1\nend\n")
        msg = str(ctx.exception)
        self.assertIn("Xyzzy", msg)
        self.assertIn("ACEITA", msg)
        self.assertIn("DESCARTA", msg)

    def test_classe_sem_mapeamento_aborta(self):
        with self.assertRaises(g.Dfm2LfmError) as ctx:
            converte_um("object ficha_x: Tficha_x\n"
                        "  object G: TRichEdit\n    Left = 1\n  end\nend\n")
        self.assertIn("TRichEdit", str(ctx.exception))

    def test_identificador_desconhecido_aborta(self):
        with self.assertRaises(g.Dfm2LfmError) as ctx:
            converte_um("object ficha_x: Tficha_x\n  Color = clBanana\nend\n")
        self.assertIn("clBanana", str(ctx.exception))

    def test_elemento_de_conjunto_desconhecido_aborta(self):
        with self.assertRaises(g.Dfm2LfmError) as ctx:
            converte_um("object ficha_x: Tficha_x\n"
                        "  Font.Style = [fsBold, fsFake]\nend\n")
        self.assertIn("fsFake", str(ctx.exception))

    def test_conjunto_vazio_passa(self):
        lfm = converte_um("object ficha_x: Tficha_x\n  BorderIcons = []\nend\n")
        self.assertIn("  BorderIcons = []\n", lfm)

    def test_nome_de_handler_nao_e_conferido_como_identificador(self):
        # `On*` guarda nome de metodo, nao valor. Quem confere e o TSV.
        lfm = converte_um("object ficha_x: Tficha_x\n"
                          "  OnCreate = QualquerCoisa\nend\n")
        self.assertIn("  OnCreate = QualquerCoisa\n", lfm)


# ------------------------------------------------------------- substituicao --

FORM_BROWSEURL = """\
object ficha_x: Tficha_x
  object Botao: TSpeedButton
    Left = 1
    Action = lanza_url
  end
  object ActionList1: TActionList
    Left = 2
    object lanza_url: TBrowseURL
      Category = 'Internet'
      Caption = '&Browse URL'
      Hint = 'Browse URL'
      URL = 'http://exemplo   '
    end
  end
end
"""


class TestBrowseURL(unittest.TestCase):
    def test_vira_tlabel_no_lugar(self):
        lfm = converte_um(FORM_BROWSEURL)
        self.assertIn("    object lanza_url: TLabel\n", lfm)
        self.assertNotIn("TBrowseURL", lfm)
        # Fica dentro do TActionList: a arvore nao se mexe.
        self.assertLess(lfm.index("object ActionList1"),
                        lfm.index("object lanza_url"))

    def test_propriedades_de_acao_caem_com_motivo(self):
        ds = {d.propriedade: d for d in descartes_de(FORM_BROWSEURL)}
        self.assertIn("Category", ds)
        self.assertIn("URL", ds)
        # O valor sai **verbatim**, com os espacos que o original tem: ele e o
        # dado a preservar.
        self.assertEqual(ds["URL"].valor, "'http://exemplo   '")
        # Caption e Hint existem em TLabel e sobrevivem.
        lfm = converte_um(FORM_BROWSEURL)
        self.assertIn("Caption = '&Browse URL'", lfm)
        self.assertIn("Hint = 'Browse URL'", lfm)

    def test_action_apontando_para_substituido_cai(self):
        lfm = converte_um(FORM_BROWSEURL)
        self.assertNotIn("Action = lanza_url", lfm)
        ds = [d for d in descartes_de(FORM_BROWSEURL)
              if d.propriedade == "Action"]
        self.assertEqual(len(ds), 1)
        self.assertIn("TBasicAction", ds[0].motivo)

    def test_action_para_objeto_nao_substituido_fica(self):
        texto = """\
object ficha_x: Tficha_x
  object Botao: TSpeedButton
    Left = 1
    Action = ActionList1
  end
  object ActionList1: TActionList
    Left = 2
  end
end
"""
        self.assertIn("    Action = ActionList1\n", converte_um(texto))

    def test_action_para_objeto_inexistente_aborta(self):
        with self.assertRaises(g.Dfm2LfmError) as ctx:
            converte_um("object ficha_x: Tficha_x\n"
                        "  object B: TSpeedButton\n    Action = fantasma\n"
                        "  end\nend\n")
        self.assertIn("fantasma", str(ctx.exception))


# -------------------------------------------------------------------- blobs --


class TestBlobs(unittest.TestCase):
    def dfm(self, tamanho: int, sha: str = "0" * 64) -> str:
        return (f"object ficha_x: Tficha_x\n"
                f"  object Img: TImage\n"
                f"    Left = 1\n"
                f"    Picture.Data = {{blob Img.Picture.Data.bin {tamanho} "
                f"sha256:{sha}}}\n"
                f"  end\nend\n")

    def test_layout_canonico(self):
        # 32 bytes por linha, hexadecimal MAIUSCULO, indentado em prop+2, `}`
        # na coluna da propriedade. E o formato do ObjectBinaryToText do FPC,
        # conferido contra os .lfm do proprio Lazarus.
        dados = bytes(range(35))
        lfm = converte_um(self.dfm(35), blobs={"Img.Picture.Data.bin": dados})
        esperado = (
            "    Picture.Data = {\n"
            "      " + dados[:32].hex().upper() + "\n"
            "      " + dados[32:].hex().upper() + "\n"
            "    }\n")
        self.assertIn(esperado, lfm)
        self.assertEqual(lfm.count("\n      "), 2)

    def test_multiplo_exato_nao_gera_linha_vazia(self):
        dados = bytes(64)
        lfm = converte_um(self.dfm(64), blobs={"Img.Picture.Data.bin": dados})
        corpo = lfm.split("Picture.Data = {\n")[1].split("    }")[0]
        self.assertEqual(len(corpo.strip().splitlines()), 2)

    def test_gabarito_usa_caractere_impossivel(self):
        # `?` nao serve: ha `Caption = '...jogadores???      '` em
        # ficha_creditos_equipo, e o gabarito casaria com o texto do usuario.
        self.assertNotIn(g.SENTINELA, "".join(chr(c) for c in range(0x20, 0x7F)))
        gabarito = converte_um(self.dfm(4))
        self.assertEqual(gabarito.count(g.SENTINELA), 8)

    def test_gabarito_e_hex_tem_o_mesmo_layout(self):
        dados = bytes(range(70))
        real = converte_um(self.dfm(70),
                           blobs={"Img.Picture.Data.bin": dados})
        gabarito = converte_um(self.dfm(70))
        self.assertEqual(len(real), len(gabarito))
        self.assertEqual(
            real.replace("\n", ""),
            "".join(r if gb != g.SENTINELA else r
                    for r, gb in zip(real.replace("\n", ""),
                                     gabarito.replace("\n", ""))))
        for r, gb in zip(real, gabarito):
            if gb != g.SENTINELA:
                self.assertEqual(r, gb)

    def test_confere_hex_aceita_digito_e_recusa_o_resto(self):
        dados = bytes([0xAB, 0xCD, 0xEF, 0x01])
        real = converte_um(self.dfm(4), blobs={"Img.Picture.Data.bin": dados})
        gabarito = converte_um(self.dfm(4))
        self.assertEqual(g.confere_hex("x.lfm", gabarito, real), [])

        # A LCL le hex minusculo, mas o gerador escreve maiusculo -- e a saida
        # tem de ser byte-estavel, entao minuscula e divergencia.
        minusculo = real.replace(dados.hex().upper(), dados.hex())
        self.assertNotEqual(minusculo, real)
        problemas = g.confere_hex("x.lfm", gabarito, minusculo)
        self.assertEqual(len(problemas), 1)
        self.assertIn("hexadecimal maiusculo", problemas[0])

    def test_confere_hex_aponta_a_linha_da_divergencia(self):
        gabarito = converte_um(FORM_MINIMO)
        alterado = gabarito.replace("Left = 1", "Left = 9")
        problemas = g.confere_hex("x.lfm", gabarito, alterado)
        self.assertEqual(problemas, ["x.lfm: linha 2 diverge"])

    def test_confere_hex_reclama_de_tamanho(self):
        gabarito = converte_um(FORM_MINIMO)
        problemas = g.confere_hex("x.lfm", gabarito, gabarito + "\n")
        self.assertIn("bytes no disco", problemas[0])

    def test_extrai_blobs_fatia_na_ordem(self):
        texto = ("object ficha_x: Tficha_x\n"
                 f"  Icon.Data = {{blob A.bin 3 sha256:{'0' * 64}}}\n"
                 "  object Img: TImage\n"
                 "    Left = 1\n"
                 f"    Picture.Data = {{blob B.bin 40 sha256:{'1' * 64}}}\n"
                 "  end\nend\n")
        a, b = bytes([1, 2, 3]), bytes(range(40))
        real = converte_um(texto, blobs={"A.bin": a, "B.bin": b})
        gabarito = converte_um(texto)
        raiz = g.ler_dfm("ficha_x", texto)
        blobs = [p.blob for o in g._todos(raiz) for p in o.props
                 if p.blob is not None]
        achados, sobra = g.extrai_blobs_do_lfm(gabarito, real, blobs)
        self.assertEqual(sobra, 0)
        self.assertEqual(achados, [a, b])


# --------------------------------------------------- nome de unidade e uses --


class TestNomeDaUnidade(unittest.TestCase):
    def test_reproduz_os_treze_medidos(self):
        for formulario, esperado in g.UNIDADES_MEDIDAS.items():
            self.assertEqual(g.nome_da_unidade(formulario), esperado)
        self.assertEqual(len(g.UNIDADES_MEDIDAS), 13)

    def test_extrapola_para_os_cinco_sem_medida(self):
        self.assertEqual(g.nome_da_unidade("MainForm"), "ep2002_mainform")
        self.assertEqual(g.nome_da_unidade("estrategia"), "ep2002_estrategia")
        self.assertEqual(g.nome_da_unidade("jugador"), "ep2002_jugador")
        self.assertEqual(g.nome_da_unidade("ficha_color"), "ep2002_color")
        self.assertEqual(g.nome_da_unidade("ficha_error"), "ep2002_error")

    def test_assinatura_curta_fica_numa_linha(self):
        self.assertEqual(g._assinatura("procedure Foo", "Sender: TObject", "  "),
                         "  procedure Foo(Sender: TObject);\n")

    def test_assinatura_longa_quebra_nos_ponto_e_virgula(self):
        saida = g._assinatura(
            "procedure TMainForm.dorsalMouseDown",
            ASSINATURA_MOUSE, "")
        self.assertEqual(
            saida,
            "procedure TMainForm.dorsalMouseDown(Sender: TObject; "
            "Button: TMouseButton;\n  Shift: TShiftState; X, Y: Integer);\n")
        for linha in saida.splitlines():
            self.assertLessEqual(len(linha), 79)

    def test_unidade_do_restub_nao_pode_colidir(self):
        # Unidade `restub` exportando `REStub` nao compila: identificador em
        # Pascal nao distingue maiusculas, e o FPC resolve o nome cru como o
        # da unidade --
        #   Fatal: Syntax error, "." expected but "(" found
        self.assertNotEqual(g.UNIDADE_RESTUB.lower(), "restub")


# ------------------------------------------------------- contrato dos blobs --


class TestContratoBlob(unittest.TestCase):
    """A referencia que o `dfm_extract.py` escreve e a que este le.

    Sao dois arquivos com a mesma sintaxe em lados opostos. Guarda exigida
    pelo `wte/tools/README.md` para o que dois geradores compartilham.
    """

    def test_regex_do_leitor_casa_a_saida_do_escritor(self):
        dados = b"conteudo qualquer de blob"
        escrito = e.Blob("Img.Picture.Data.bin", dados).reference()
        casou = g.RE_BLOB.match(escrito)
        self.assertIsNotNone(casou, f"{escrito!r} nao casa com RE_BLOB")
        self.assertEqual(casou.group("arq"), "Img.Picture.Data.bin")
        self.assertEqual(int(casou.group("tam")), len(dados))
        self.assertEqual(casou.group("sha"),
                         hashlib.sha256(dados).hexdigest())

    def test_blob_vazio_tambem_casa(self):
        escrito = e.Blob("X.bin", b"").reference()
        casou = g.RE_BLOB.match(escrito)
        self.assertIsNotNone(casou)
        self.assertEqual(int(casou.group("tam")), 0)


# ----------------------------------------------------- conversao completa ----

TSV_CABECALHO = ("endereco\thandler\tformulario\tcomponente\tevento\tgrupo\t"
                 "regra\tnota\n")


class Arvore:
    """Arvore de entrada sintetica, com o modulo apontado para ela."""

    def __init__(self, dfms: dict[str, str], tsv: str,
                 blobs: dict[str, bytes] | None = None):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        (base / "dfm").mkdir()
        for nome, texto in dfms.items():
            (base / "dfm" / f"{nome}.dfm").write_text(texto, encoding="ascii")
        for rel, dados in (blobs or {}).items():
            alvo = base / "dfm" / "blobs" / rel
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_bytes(dados)
        (base / "methods.tsv").write_text(TSV_CABECALHO + tsv,
                                          encoding="utf-8")
        (base / "wte" / "forms").mkdir(parents=True)
        (base / "wte" / "src").mkdir(parents=True)
        self.antigos = (g.DFM_DIR, g.BLOBS_DIR, g.METHODS_TSV, g.FORMS_OUT,
                        g.SRC_OUT, g.ROOT)
        g.DFM_DIR = base / "dfm"
        g.BLOBS_DIR = base / "dfm" / "blobs"
        g.METHODS_TSV = base / "methods.tsv"
        g.FORMS_OUT = base / "wte" / "forms"
        g.SRC_OUT = base / "wte" / "src"
        g.ROOT = base

    def __enter__(self):
        return self

    def __exit__(self, *_):
        (g.DFM_DIR, g.BLOBS_DIR, g.METHODS_TSV, g.FORMS_OUT, g.SRC_OUT,
         g.ROOT) = self.antigos
        self.tmp.cleanup()


def dezoito(base: str, tsv_extra: str = "") -> tuple[dict[str, str], str]:
    """18 formularios triviais, para satisfazer a contagem, mais um de teste."""
    dfms = {"ficha_x": base}
    for i in range(17):
        nome = f"ficha_v{i}"
        dfms[nome] = f"object {nome}: T{nome}\n  Left = 0\nend\n"
    return dfms, tsv_extra


class TestConversaoCompleta(unittest.TestCase):
    def test_stub_na_unidade_do_dono_e_com_a_assinatura_certa(self):
        dfms, tsv = dezoito("""\
object ficha_x: Tficha_x
  Left = 0
  OnCreate = FormCreate
  object Barra: TScrollBar
    Left = 1
    OnScroll = barraScroll
  end
  object Setas: TUpDown
    Left = 2
    OnClick = setasClick
  end
end
""", "0x1\tFormCreate\tficha_x\tficha_x\tOnCreate\tcarga\tR2\t\n"
     "0x2\tbarraScroll\tficha_x\tBarra\tOnScroll\tedicao\tR8\t\n"
     "0x3\tsetasClick\tficha_x\tSetas\tOnClick\tedicao\tR8\t\n")
        with Arvore(dfms, tsv):
            arquivos, _f = g.converte()
        pas = arquivos["wte/src/ep2002_x.pas"]
        self.assertIn("procedure FormCreate(Sender: TObject);", pas)
        # Passa de 79 colunas e quebra nos `;` da lista de parametros.
        self.assertIn("    procedure barraScroll(Sender: TObject; "
                      "ScrollCode: TScrollCode;\n"
                      "      var ScrollPos: Integer);\n", pas)
        # TUpDown.OnClick NAO e TNotifyEvent -- e TUDClickEvent. Assinatura
        # adivinhada da um .pas que nao compila.
        self.assertIn("procedure setasClick(Sender: TObject; "
                      "Button: TUDBtnType);", pas)
        self.assertIn("REStub('ficha_x.FormCreate');", pas)
        self.assertIn("{$R ../forms/ep2002_x.lfm}", pas)
        # Nenhum stub caiu numa unidade vizinha.
        self.assertNotIn("FormCreate", arquivos["wte/src/ep2002_v0.pas"])

    def test_formcreate_homonimo_nao_colide(self):
        # 16 dos 96 handlers se chamam FormCreate. O escopo de classe resolve.
        base = ("object ficha_x: Tficha_x\n  Left = 0\n"
                "  OnCreate = FormCreate\nend\n")
        dfms, tsv = dezoito(
            base, "0x1\tFormCreate\tficha_x\tficha_x\tOnCreate\tcarga\tR2\t\n"
                  "0x2\tFormCreate\tficha_v0\tficha_v0\tOnCreate\tcarga\tR2\t\n")
        dfms["ficha_v0"] = ("object ficha_v0: Tficha_v0\n  Left = 0\n"
                            "  OnCreate = FormCreate\nend\n")
        with Arvore(dfms, tsv):
            arquivos, _f = g.converte()
        self.assertIn("procedure Tficha_x.FormCreate(Sender: TObject);",
                      arquivos["wte/src/ep2002_x.pas"])
        self.assertIn("procedure Tficha_v0.FormCreate(Sender: TObject);",
                      arquivos["wte/src/ep2002_v0.pas"])

    def test_handler_no_dfm_e_ausente_do_tsv_aborta(self):
        dfms, tsv = dezoito("object ficha_x: Tficha_x\n  Left = 0\n"
                            "  OnCreate = FormCreate\nend\n", "")
        with Arvore(dfms, tsv):
            with self.assertRaises(g.Dfm2LfmError) as ctx:
                g.converte()
        self.assertIn("published_methods.tsv", str(ctx.exception))

    def test_par_classe_evento_sem_assinatura_aborta(self):
        # Todo `On*` que esta em ACEITA tem entrada em EVENTOS, por
        # construcao -- e o que faz a conversao fechar. Para exercitar o
        # aborto, a entrada e removida por um teste so: o caso real e alguem
        # acrescentar um `On*` a ACEITA e esquecer a assinatura.
        dfms, tsv = dezoito("""\
object ficha_x: Tficha_x
  Left = 0
  object Rot: TLabel
    Left = 1
    OnClick = rotClick
  end
end
""", "0x1\trotClick\tficha_x\tRot\tOnClick\tedicao\tR8\t\n")
        guardado = g.EVENTOS.pop(("TLabel", "OnClick"))
        try:
            with Arvore(dfms, tsv):
                with self.assertRaises(g.Dfm2LfmError) as ctx:
                    g.converte()
        finally:
            g.EVENTOS[("TLabel", "OnClick")] = guardado
        self.assertIn("EVENTOS", str(ctx.exception))

    def test_linha_sem_componente_e_fora_da_lista_aborta(self):
        dfms, tsv = dezoito("object ficha_x: Tficha_x\n  Left = 0\nend\n",
                            "0x1\tOrfaoClick\tficha_x\t\t\tauxiliar\tR7\t\n")
        with Arvore(dfms, tsv):
            with self.assertRaises(g.Dfm2LfmError) as ctx:
                g.converte()
        self.assertIn("SEM_COMPONENTE", str(ctx.exception))

    def test_handler_repetido_no_mesmo_formulario_aborta(self):
        dfms, tsv = dezoito(
            "object ficha_x: Tficha_x\n  Left = 0\n"
            "  OnCreate = FormCreate\nend\n",
            "0x1\tFormCreate\tficha_x\tficha_x\tOnCreate\tcarga\tR2\t\n"
            "0x2\tFormCreate\tficha_x\tficha_x\tOnCreate\tcarga\tR2\t\n")
        with Arvore(dfms, tsv):
            with self.assertRaises(g.Dfm2LfmError) as ctx:
                g.converte()
        self.assertIn("repetido", str(ctx.exception))

    def test_numero_de_dfm_diferente_de_dezoito_aborta(self):
        with Arvore({"ficha_x": FORM_MINIMO}, ""):
            with self.assertRaises(g.Dfm2LfmError) as ctx:
                g.converte()
        self.assertIn("18", str(ctx.exception))

    def test_blob_ausente_aborta_na_escrita_e_aponta_o_extrator(self):
        sha = hashlib.sha256(b"abc").hexdigest()
        dfms, tsv = dezoito(
            f"object ficha_x: Tficha_x\n  Left = 0\n"
            f"  Icon.Data = {{blob ficha_x.Icon.Data.bin 3 sha256:{sha}}}\n"
            f"end\n", "")
        with Arvore(dfms, tsv):
            _a, formularios = g.converte()
            with self.assertRaises(g.Dfm2LfmError) as ctx:
                g.carrega_blobs(formularios)
        msg = str(ctx.exception)
        self.assertIn("dfm_extract.py", msg)
        self.assertIn("ficha_x.Icon.Data.bin", msg)

    def test_blob_com_sha_errado_aborta(self):
        sha = hashlib.sha256(b"abc").hexdigest()
        dfms, tsv = dezoito(
            f"object ficha_x: Tficha_x\n  Left = 0\n"
            f"  Icon.Data = {{blob ficha_x.Icon.Data.bin 3 sha256:{sha}}}\n"
            f"end\n", "")
        with Arvore(dfms, tsv, blobs={"ficha_x/ficha_x.Icon.Data.bin": b"xyz"}):
            _a, formularios = g.converte()
            with self.assertRaises(g.Dfm2LfmError) as ctx:
                g.carrega_blobs(formularios)
        self.assertIn("SHA-256", str(ctx.exception))

    def test_blob_com_tamanho_errado_aborta(self):
        sha = hashlib.sha256(b"abcd").hexdigest()
        dfms, tsv = dezoito(
            f"object ficha_x: Tficha_x\n  Left = 0\n"
            f"  Icon.Data = {{blob ficha_x.Icon.Data.bin 4 sha256:{sha}}}\n"
            f"end\n", "")
        with Arvore(dfms, tsv, blobs={"ficha_x/ficha_x.Icon.Data.bin": b"abc"}):
            _a, formularios = g.converte()
            with self.assertRaises(g.Dfm2LfmError) as ctx:
                g.carrega_blobs(formularios)
        self.assertIn("bytes no disco", str(ctx.exception))

    def test_sem_handler_nao_puxa_a_unidade_do_restub(self):
        # Hint 5023 ("unit not used") -- `ficha_error2` nao tem handler nenhum.
        dfms, tsv = dezoito("object ficha_x: Tficha_x\n  Left = 0\nend\n", "")
        with Arvore(dfms, tsv):
            arquivos, _f = g.converte()
        pas = arquivos["wte/src/ep2002_x.pas"]
        clausula = pas.split("uses\n")[1].split(";")[0]
        self.assertNotIn(g.UNIDADE_RESTUB, clausula)

    def test_duas_execucoes_dao_o_mesmo_texto(self):
        dfms, tsv = dezoito(FORM_MINIMO, "")
        with Arvore(dfms, tsv):
            a, _f1 = g.converte()
            b, _f2 = g.converte()
        self.assertEqual(a, b)


# ------------------------------------------------------------- corpus real --


class TestCorpusReal(unittest.TestCase):
    """Le so os 18 `.dfm` versionados -- nem o `.exe` nem `blobs/`."""

    @classmethod
    def setUpClass(cls):
        cls.arvores = []
        for caminho in sorted(g.DFM_DIR.glob("*.dfm")):
            cls.arvores.append(
                (caminho.stem,
                 g.ler_dfm(caminho.stem, caminho.read_text(encoding="ascii"))))

    def test_dezoito_formularios(self):
        self.assertEqual(len(self.arvores), 18)

    def test_441_componentes(self):
        # O mesmo total do `re/dfm/censo.md`. Se divergir, um dos dois
        # geradores parou de ver o que o outro ve.
        total = sum(len(list(g._todos(r))) - 1 for _n, r in self.arvores)
        self.assertEqual(total, 441)

    def test_37_statictext(self):
        # A secao 8.9 do plano: 36 com nome mais o anonimo do MainForm.
        total = sum(1 for _n, r in self.arvores for o in g._todos(r)
                    if o.cls == "TStaticText")
        self.assertEqual(total, 37)

    def test_118_blobs(self):
        total = sum(1 for _n, r in self.arvores for o in g._todos(r)
                    for p in o.props if p.blob is not None)
        self.assertEqual(total, 118)

    def test_dois_browseurl(self):
        total = sum(1 for _n, r in self.arvores for o in g._todos(r)
                    if o.cls == "TBrowseURL")
        self.assertEqual(total, 2)

    def test_96_handlers_no_tsv(self):
        por_formulario = g.le_handlers()
        self.assertEqual(sum(len(v) for v in por_formulario.values()), 96)

    def test_toda_classe_do_corpus_tem_mapeamento(self):
        for nome, raiz in self.arvores:
            for obj in g._todos(raiz):
                if obj is raiz:
                    continue
                cls = g.SUBSTITUICOES.get(obj.cls, obj.cls)
                with self.subTest(formulario=nome, classe=cls):
                    self.assertIn(cls, g.ACEITA)
                    self.assertIn(cls, g.UNIDADE_DA_CLASSE)


if __name__ == "__main__":
    unittest.main()
