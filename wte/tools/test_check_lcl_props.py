#!/usr/bin/env python3
"""Testes do `check_lcl_props.py`: as tres guardas, com entrada plantada.

Guarda nunca exercitada e guarda ausente -- foi o que a CORR-WTE-020 achou no
proprio `dfm2lfm.py`, cujo cabecalho afirmava ter medido a tabela contra a LCL
sem que nada remedisse. Repetir o defeito no conferidor seria comico.

A maior parte roda contra uma **LCL sintetica** montada em diretorio
temporario: tres unidades com cadeia de ancestrais e secoes `published`, mais
o `lazversion.pas` que da a versao. Assim os tres sentidos -- `ACEITA`
inventada, `DESCARTA` que existe, `LCL_VERSAO` divergindo do disco -- sao
exercitados sem depender do que esta instalado na maquina. Um teste so, sob
`skipUnless`, confere a LCL de verdade.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import check_lcl_props as mod
import dfm2lfm

# A LCL de verdade, quando ha uma. `ARVORE_DIRETA` (de `WTE_LAZARUS_DIR`) e o
# caminho de quem a instalou fora de `/usr/lib/lazarus` -- o Windows poe a
# arvore inteira em `C:\lazarus`, sem o nivel de versao.
LCL_REAL = (Path(mod.ARVORE_DIRETA) / "lcl" if mod.ARVORE_DIRETA
            else mod.LCL_BASE / dfm2lfm.LCL_VERSAO / "lcl")

UNIDADE = """
unit sintetica;
interface
type
  TComponente = class(TObject)
  published
    property Name;
    property Tag;
  end;

  TControle = class(TComponente)
  private
    property Escondida;
  published
    property Caption;
    property Color;
    property Font;
  public
    property Publica;
  end;

  TRotulo = class(TControle)
  published
    property Alignment;
    property Transparent;
  end;

  TCronometro = class(TComponente)
  published
    property Interval;
    property OnTimer;
  end;
implementation
const
  Nomes = 'clBlack clRed fsBold';
end.
"""


class BaseSintetica(unittest.TestCase):
    """Monta uma LCL de mentira e aponta o modulo para ela."""

    VERSAO = "9.9"

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        raiz = Path(self._tmp.name) / self.VERSAO
        (raiz / "lcl").mkdir(parents=True)
        (raiz / "components" / "lazutils").mkdir(parents=True)
        (raiz / "lcl" / "sintetica.pp").write_text(UNIDADE, encoding="utf-8")
        (raiz / "components" / "lazutils" / "lazversion.pas").write_text(
            "const\n  laz_major = 9;\n  laz_minor = 9;\n  laz_release = 0;\n",
            encoding="utf-8")
        self._base, self._versao = mod.LCL_BASE, dfm2lfm.LCL_VERSAO
        # `ARVORE_DIRETA` vem de `WTE_LAZARUS_DIR` e aponta a LCL de verdade
        # quando ela esta fora de `/usr/lib/lazarus` (o caso do Windows). Se
        # ficar de pe, ela ganha do `LCL_BASE` plantado abaixo e os casos
        # daqui medem a arvore instalada em vez da fixture.
        self._arvore = mod.ARVORE_DIRETA
        mod.ARVORE_DIRETA = ""
        self._aceita = dict(dfm2lfm.ACEITA)
        self._descarta = dict(dfm2lfm.DESCARTA)
        self._ident = set(dfm2lfm.IDENTIFICADORES)
        self._conj = set(dfm2lfm.ELEMENTOS_DE_CONJUNTO)
        mod.LCL_BASE = Path(self._tmp.name)
        dfm2lfm.LCL_VERSAO = self.VERSAO
        dfm2lfm.ACEITA = {"TRotulo": {"Caption", "Alignment"}}
        dfm2lfm.DESCARTA = {"TRotulo": {"OldCreateOrder": "nao existe"}}
        dfm2lfm.IDENTIFICADORES = {"clBlack", "clRed", "True"}
        dfm2lfm.ELEMENTOS_DE_CONJUNTO = {"fsBold"}
        self.addCleanup(self._restaura)

    def _restaura(self):
        mod.LCL_BASE, dfm2lfm.LCL_VERSAO = self._base, self._versao
        mod.ARVORE_DIRETA = self._arvore
        dfm2lfm.ACEITA, dfm2lfm.DESCARTA = self._aceita, self._descarta
        dfm2lfm.IDENTIFICADORES = self._ident
        dfm2lfm.ELEMENTOS_DE_CONJUNTO = self._conj
        self._tmp.cleanup()

    def _roda(self) -> tuple[list[str], dict[str, int]]:
        return mod.conferir(mod.caminho_da_lcl(dfm2lfm.LCL_VERSAO))


class TesteBase(BaseSintetica):
    """A LCL sintetica, sem planta, tem de passar."""

    def test_tabela_coerente_nao_acusa(self):
        problemas, _ = self._roda()
        self.assertEqual(problemas, [])

    def test_heranca_atravessa_a_cadeia(self):
        pai, props, _ = mod.indexar(mod.caminho_da_lcl(self.VERSAO))
        # `Name` vem de TComponente, dois niveis acima de TRotulo.
        self.assertIn("Name", mod.herdadas("TRotulo", pai, props))
        self.assertIn("Caption", mod.herdadas("TRotulo", pai, props))

    def test_secao_nao_published_fica_de_fora(self):
        pai, props, _ = mod.indexar(mod.caminho_da_lcl(self.VERSAO))
        disponiveis = mod.herdadas("TRotulo", pai, props)
        self.assertNotIn("Escondida", disponiveis)   # private
        self.assertNotIn("Publica", disponiveis)     # public

    def test_ramo_irmao_nao_vaza(self):
        pai, props, _ = mod.indexar(mod.caminho_da_lcl(self.VERSAO))
        self.assertNotIn("Interval", mod.herdadas("TRotulo", pai, props))


class TesteAceitaPlantada(BaseSintetica):
    """Sentido 1: propriedade inventada em ACEITA sai verbatim para o .lfm."""

    def test_propriedade_inexistente_acusa_com_classe_e_nome(self):
        dfm2lfm.ACEITA = {"TRotulo": {"Caption", "NaoExiste"}}
        problemas, _ = self._roda()
        self.assertEqual(len(problemas), 1)
        self.assertIn("TRotulo.NaoExiste", problemas[0])
        self.assertIn("sem published", problemas[0])

    def test_propriedade_de_ramo_irmao_acusa(self):
        # `Interval` existe na LCL, mas em TCronometro -- nao em TRotulo. E o
        # engano provavel: a propriedade "existe", so que noutra classe.
        dfm2lfm.ACEITA = {"TRotulo": {"Interval"}}
        problemas, _ = self._roda()
        self.assertEqual(len(problemas), 1)
        self.assertIn("TRotulo.Interval", problemas[0])

    def test_classe_ausente_acusa(self):
        dfm2lfm.ACEITA = {"TNaoExiste": {"Caption"}}
        problemas, _ = self._roda()
        self.assertIn("classe ausente", problemas[0])

    def test_subpropriedade_confere_pela_raiz(self):
        # A LCL publica `Font`; o DFM escreve `Font.Charset`.
        dfm2lfm.ACEITA = {"TRotulo": {"Font.Charset", "Font.Height"}}
        problemas, _ = self._roda()
        self.assertEqual(problemas, [])

    def test_excecao_designinfo_e_lista_fechada(self):
        # `Left` nao esta em published nenhuma da arvore sintetica. Em
        # TCronometro (nao nomeado nas excecoes) acusa; e a lista fechada e o
        # que impede um `if prop in ("Left","Top")` generico de calar tudo.
        dfm2lfm.ACEITA = {"TCronometro": {"Left"}}
        problemas, _ = self._roda()
        self.assertEqual(len(problemas), 1)
        self.assertIn("TCronometro.Left", problemas[0])
        self.assertNotIn(("TCronometro", "Left"), mod.EXCECOES_DESIGNINFO)


class TesteDescartaPlantada(BaseSintetica):
    """Sentido 2: descartar propriedade que a LCL tem perde dado do form."""

    def test_propriedade_existente_em_descarta_acusa(self):
        dfm2lfm.DESCARTA = {"TRotulo": {"Caption": "motivo qualquer"}}
        problemas, _ = self._roda()
        self.assertEqual(len(problemas), 1)
        self.assertIn("TRotulo.Caption", problemas[0])
        self.assertIn("a LCL **tem**", problemas[0])

    def test_propriedade_herdada_em_descarta_tambem_acusa(self):
        # `Name` vem de dois niveis acima: a conferencia tem de subir a cadeia
        # nos dois sentidos, senao DESCARTA passaria por herdada.
        dfm2lfm.DESCARTA = {"TRotulo": {"Name": "motivo"}}
        problemas, _ = self._roda()
        self.assertEqual(len(problemas), 1)
        self.assertIn("TRotulo.Name", problemas[0])


class TesteVersaoPlantada(BaseSintetica):
    """Sentido 3: o pino tem de pinar -- era codigo morto antes desta CORR."""

    def test_versao_divergente_recusa_antes_de_varrer(self):
        (Path(self._tmp.name) / self.VERSAO / "components" / "lazutils"
         / "lazversion.pas").write_text(
            "const\n  laz_major = 4;\n  laz_minor = 2;\n", encoding="utf-8")
        with self.assertRaises(mod.CheckError) as ctx:
            mod.caminho_da_lcl(dfm2lfm.LCL_VERSAO)
        self.assertIn("declara '4.2'", str(ctx.exception))
        self.assertIn("medida noutra versao", str(ctx.exception))

    def test_arvore_ausente_recusa_dizendo_o_caminho(self):
        dfm2lfm.LCL_VERSAO = "0.0"
        with self.assertRaises(mod.CheckError) as ctx:
            mod.caminho_da_lcl(dfm2lfm.LCL_VERSAO)
        self.assertIn("LCL nao encontrada", str(ctx.exception))

    def test_lazversion_sem_o_campo_recusa(self):
        (Path(self._tmp.name) / self.VERSAO / "components" / "lazutils"
         / "lazversion.pas").write_text("const\n  outro = 1;\n",
                                        encoding="utf-8")
        with self.assertRaises(mod.CheckError) as ctx:
            mod.caminho_da_lcl(dfm2lfm.LCL_VERSAO)
        self.assertIn("laz_major", str(ctx.exception))


class TesteIdentificadores(BaseSintetica):

    def test_identificador_inventado_acusa(self):
        dfm2lfm.IDENTIFICADORES = {"clBlack", "clNaoExiste"}
        problemas, _ = self._roda()
        self.assertEqual(len(problemas), 1)
        self.assertIn("clNaoExiste", problemas[0])

    def test_elemento_de_conjunto_inventado_acusa(self):
        dfm2lfm.ELEMENTOS_DE_CONJUNTO = {"fsNaoExiste"}
        problemas, _ = self._roda()
        self.assertEqual(len(problemas), 1)
        self.assertIn("fsNaoExiste", problemas[0])

    def test_true_e_false_nao_sao_cobrados_da_lcl(self):
        # Sao palavras do FPC. Exigi-las das fontes da LCL seria conferir a
        # coisa errada e o teste passaria por acaso.
        dfm2lfm.IDENTIFICADORES = {"True", "False"}
        problemas, _ = self._roda()
        self.assertEqual(problemas, [])


def _lcl_utilizavel() -> str:
    """Vazio se da para medir; senao, o motivo de nao dar.

    SAO DUAS CONDICOES, e a segunda so apareceu no Windows. A primeira e ter
    uma LCL no disco. A segunda e ela ser a versao que a tabela `PROPRIEDADES`
    mediu: o `winget` traz Lazarus 4.8 e o `LCL_VERSAO` do `dfm2lfm.py` esta
    pinado em `3.0`. Rodar contra a 4.8 e aceitar o que sair seria trocar a
    regua pelo objeto medido -- e por isso o proprio `check_lcl_props.py`
    recusa. Aqui o correto e PULAR dizendo qual e a versao do disco, nao
    quebrar: quebra parece regressao, e nao ha regressao nenhuma.
    """
    if not LCL_REAL.is_dir():
        return f"LCL nao instalada em {LCL_REAL}"
    try:
        no_disco = mod.versao_no_disco(LCL_REAL.parent)
    except mod.CheckError as erro:
        return str(erro)
    if no_disco != dfm2lfm.LCL_VERSAO:
        return (f"LCL do disco e {no_disco}, o LCL_VERSAO do dfm2lfm.py e "
                f"{dfm2lfm.LCL_VERSAO} -- a tabela PROPRIEDADES NAO foi "
                f"conferida nesta execucao")
    return ""


_MOTIVO = _lcl_utilizavel()


@unittest.skipIf(_MOTIVO, _MOTIVO)
class TesteLclInstalada(unittest.TestCase):
    """A conferencia que o `make -C wte check` roda, contra a LCL de verdade."""

    def test_tabela_bate_com_a_lcl_do_disco(self):
        problemas, contagem = mod.conferir(
            mod.caminho_da_lcl(dfm2lfm.LCL_VERSAO))
        self.assertEqual(problemas, [], "\n".join(problemas))
        self.assertGreater(contagem["propriedades em ACEITA"], 200)

    def test_as_oito_excecoes_sao_mesmo_excecao(self):
        # Se a LCL passar a publicar `Left`/`Top` nestas classes, a excecao
        # vira ruido e deve sair. O teste avisa quando isso acontecer.
        lcl = mod.caminho_da_lcl(dfm2lfm.LCL_VERSAO)
        pai, props, _ = mod.indexar(lcl)
        for classe, prop in sorted(mod.EXCECOES_DESIGNINFO):
            self.assertNotIn(prop, mod.herdadas(classe, pai, props),
                             f"{classe}.{prop} agora e published na LCL -- "
                             f"tire de EXCECOES_DESIGNINFO")


if __name__ == "__main__":
    unittest.main()
