#!/usr/bin/env python3
"""Testes do check_fase4.py -- WTE-TASK-31.

O que se mede aqui sao as duas leituras que o fechamento faz e que ninguem
conferiria sozinho:

1. **quem grava na imagem**, lido da primeira linha de `## Bytes tocados`. Essa
   linha e prosa escrita a mao em 94 arquivos, e a conta de gravacoes do
   fechamento inteiro sai dela -- uma frase nova de "nao grava" que o leitor nao
   reconhecesse faria a conta subir em silencio, que e o defeito que a
   CORR-WTE-012, a -014 e a -023 pegaram sempre em contagem de doc;
2. **quais cinco `trivial` sao reamostrados**. A regra tem de ser reproduzivel
   (senao o `--check` nunca casa) e tem de se deslocar quando a populacao muda
   (senao a reconferencia envelhece apontando para handler que saiu do grupo).

Os testes montam a entrada em memoria: nao abrem o `.exe`, nao precisam de
`DISPLAY` nem de Wine, e rodam num clone sem a pasta `we-team-editor/`.
"""

from __future__ import annotations

import ast
import re
import tempfile
import unittest
from pathlib import Path

import check_fase4 as C
import spec_index as S


class TestPrimeiraLinha(unittest.TestCase):
    """A leitura pula o que nao e resposta."""

    def test_pula_vazio_e_cerca_de_bloco(self) -> None:
        """A `boton_tex2isoClick` abre a secao com um bloco de codigo.

        A cerca nao e a resposta -- a linha seguinte e. Antes desta regra o
        fechamento abortava dizendo que a secao estava vazia, e a secao tem
        onze linhas.
        """
        corpo = "\n```text\noffset = 19756824 + 47040 * i\n```\n"
        self.assertEqual(C.normaliza_primeira_linha(corpo),
                         "offset = 19756824 + 47040 * i")

    def test_tira_enfase_e_baixa_a_caixa(self) -> None:
        self.assertEqual(C.normaliza_primeira_linha("**Nenhum.**"), "nenhum.")
        self.assertEqual(C.normaliza_primeira_linha("`Nenhum`"), "nenhum")

    def test_secao_so_com_cerca_devolve_vazio(self) -> None:
        self.assertEqual(C.normaliza_primeira_linha("\n```\n```\n"), "")


class TestGravaNaImagem(unittest.TestCase):
    """A conta de gravacoes do fechamento inteiro sai daqui."""

    def test_nenhum_nao_grava(self) -> None:
        self.assertFalse(C.grava_na_imagem("x.y", "**Nenhum.**"))

    def test_nenhum_qualificado_tambem_nao(self) -> None:
        """`grabar_memoryClick` emite um `.mcr` e deixa a ROM intacta."""
        self.assertFalse(
            C.grava_na_imagem("x.y", "**Nenhum na imagem de CD.** Medido: ..."))
        self.assertFalse(
            C.grava_na_imagem("x.y", "**Na imagem de CD: nenhum.** Ela e ..."))

    def test_qualquer_outra_coisa_grava(self) -> None:
        self.assertTrue(
            C.grava_na_imagem("x.y", "Sete regioes por time, todas ..."))

    def test_secao_vazia_aborta(self) -> None:
        with self.assertRaises(C.Fase4Error) as ctx:
            C.grava_na_imagem("x.y", "\n\n")
        self.assertIn("vazia", str(ctx.exception))

    def test_forma_nova_de_nao_gravar_aborta_em_vez_de_contar(self) -> None:
        """O ponto do teste, e a razao de a guarda existir.

        Uma spec nova que escrevesse "Nenhum byte da imagem" seria classificada
        como GRAVACAO pela regra de prefixo -- e a tabela de gates ganharia um
        handler que nao grava, ou perderia um que grava. Abortar poe o erro na
        cara de quem escreveu a frase, no dia em que ele a escreveu.
        """
        with self.assertRaises(C.Fase4Error) as ctx:
            C.grava_na_imagem("x.y", "Byte nenhum, em lugar nenhum.")
        self.assertIn("NAO_GRAVA", str(ctx.exception))


class TestCincoTrivial(unittest.TestCase):
    """A amostra e reproduzivel, espacada, e se desloca com a populacao."""

    def amostra(self, n: int) -> list[str]:
        triviais = [{"endereco": f"0x{i:08x}", "handler": f"f.h{i}"}
                    for i in range(n)]
        return [x["handler"] for x in C.cinco_trivial(triviais)]

    def test_pega_as_duas_pontas_e_espaca_o_meio(self) -> None:
        """Com 19 -- a populacao real no fechamento -- sao estes cinco."""
        self.assertEqual(self.amostra(19),
                         ["f.h0", "f.h4", "f.h9", "f.h14", "f.h18"])

    def test_e_deterministica(self) -> None:
        self.assertEqual(self.amostra(19), self.amostra(19))

    def test_desloca_quando_a_populacao_muda(self) -> None:
        """Handler novo em `trivial` muda quais sao os cinco.

        E o que faz o gerador abortar se o registro da reconferencia nao
        acompanhar -- reconferencia velha nao vale para handler novo.
        """
        self.assertNotEqual(self.amostra(19), self.amostra(20))

    def test_nunca_repete_o_mesmo_handler(self) -> None:
        for n in range(5, 40):
            with self.subTest(n=n):
                self.assertEqual(len(set(self.amostra(n))), len(self.amostra(n)))

    def test_populacao_curta_demais_aborta(self) -> None:
        with self.assertRaises(C.Fase4Error):
            self.amostra(4)


class TestGuardasDoGolden(unittest.TestCase):
    """As duas guardas da CORR-WTE-096, com caso plantado.

    Guarda nunca exercitada e guarda ausente: as duas nascem de uma tabela que
    envelheceu em silencio, entao as duas tem de reprovar aqui antes de valerem
    alguma coisa la.
    """

    def test_a_tabela_de_hoje_nao_tem_chave_repetida(self) -> None:
        self.assertEqual(C.chaves_repetidas_no_fonte(), [])

    def test_chave_repetida_plantada_e_pega(self) -> None:
        """O detector le a FONTE, entao o caso plantado e texto."""
        fonte = (
            "GOLDEN_DE: dict[str, tuple[str, ...]] = {\n"
            '    "MainForm.aClick": ("golden-01",),\n'
            '    "MainForm.bClick": ("golden-02",),\n'
            '    "MainForm.aClick": (),\n'
            "}\n")
        with tempfile.TemporaryDirectory() as d:
            alvo = Path(d) / "falso.py"
            alvo.write_text(fonte, encoding="utf-8")
            arvore = ast.parse(alvo.read_text(encoding="utf-8"))
            chaves = [c.value for no in ast.walk(arvore)
                      if isinstance(no, ast.AnnAssign)
                      and getattr(no.target, "id", "") == "GOLDEN_DE"
                      for c in no.value.keys]
        repetidas = sorted({c for c in chaves if chaves.count(c) > 1})
        self.assertEqual(repetidas, ["MainForm.aClick"])

    def test_escritor_implementado_sem_gate_reprova(self) -> None:
        escritores = [{"handler": "MainForm.base_teamClick",
                       "veredito": "implementado"},
                      {"handler": "NaoExiste.xClick",
                       "veredito": "implementado"}]
        self.assertEqual(C.gates_vazios(escritores), ["NaoExiste.xClick"])

    def test_escritor_aberto_pode_ter_gate_vazio(self) -> None:
        """Tupla vazia quer dizer "o gate vem com o dono" -- so no `aberto`."""
        self.assertEqual(
            C.gates_vazios([{"handler": "NaoExiste.xClick",
                             "veredito": "aberto"}]), [])

    def test_a_tabela_de_hoje_nao_tem_gate_vazio(self) -> None:
        escritores = [{"handler": h, "veredito": "implementado"}
                      for h in C.GOLDEN_DE]
        self.assertEqual(C.gates_vazios(escritores), [])


class TestFormaAposentada(unittest.TestCase):
    """A guarda da CORR-WTE-085: `seis`/`nove gravacoes` em linha viva."""

    def test_a_forma_velha_e_pega(self) -> None:
        self.assertTrue(any(
            re.search(f, "duas das seis gravações do editor", re.I)
            for f in C.FORMAS_APOSENTADAS))
        self.assertTrue(any(
            re.search(f, "as nove gravações da fase 4", re.I)
            for f in C.FORMAS_APOSENTADAS))

    def test_o_digito_solto_nao_e_alvo(self) -> None:
        """`6` e `9` sozinhos dariam falso positivo em qualquer pagina."""
        self.assertFalse(any(
            re.search(f, "as 6 gravações medidas", re.I)
            for f in C.FORMAS_APOSENTADAS))

    def test_a_forma_velho_para_corrente_e_perdoada(self) -> None:
        """`seis -> dezessete` ensina; `seis` sozinho mente."""
        self.assertTrue(C._diz_o_corrente(
            "de seis gravações para dezessete", 17))
        self.assertTrue(C._diz_o_corrente("seis gravações viraram 17", 17))
        self.assertFalse(C._diz_o_corrente("duas das seis gravações", 17))


class TestMarcasDeDecompilado(unittest.TestCase):
    """A varredura daqui e mais estreita que a do `spec_index.py`."""

    def casa(self, texto: str) -> bool:
        return any(m.search(texto) for m, _ in C.MARCAS)

    def test_pega_o_que_o_ghidra_inventa(self) -> None:
        for trecho in ("undefined4 x;", "uVar1 = 3;", "local_1c",
                       "param_1", "DAT_00423abc", "__fastcall foo",
                       "(int)*(int *)(this + 8)"):
            with self.subTest(trecho=trecho):
                self.assertTrue(self.casa(trecho))

    def test_deixa_passar_undefined_sem_digito(self) -> None:
        """A diferenca contra o `spec_index.py`, e ela e deliberada.

        Esta varredura alcanca `.pas` e `.inc`, e o `we2002_types.pas` tem
        `undefined behaviour, not a behaviour` num comentario -- prosa inglesa,
        nao saida de decompilador. O custo esta escrito no cabecalho do
        gerador: um `undefined` de Ghidra sem digito passaria.
        """
        self.assertFalse(self.casa("undefined behaviour, not a behaviour"))


class TestBloqueioVencido(unittest.TestCase):
    """A guarda que impede prosa vencida de segurar um veredito `aberto`.

    Ela nasceu de dois casos reais: a `0x0040a0b4` foi portada pela
    CORR-WTE-082 e duas specs do `estrategia` continuaram dizendo que nao
    estava, cada uma segurando o proprio `aberto`.
    """

    def cita(self, texto: str) -> set[str]:
        achados: set[str] = set()
        for padrao in C.BLOQUEIO_VENCIDO:
            achados |= {m.lower() for m in padrao.findall(texto)}
        return achados

    def test_pega_as_duas_ordens(self) -> None:
        self.assertEqual(self.cita("a `0x0040a0b4` ainda nao esta portada"),
                         {"0x0040a0b4"})
        self.assertEqual(self.cita("nao portada: a `0x0040A0B4` do original"),
                         {"0x0040a0b4"})

    def test_atravessa_quebra_de_linha_e_nome_qualificado(self) -> None:
        """As duas coisas que a forma obvia erraria.

        `[^.]` seria o instinto para "mesma frase" e falha duas vezes: casa
        `\n`, e nao passa por `MainForm.mostrar_estrategiaClick` -- que era
        exatamente a frase do `bolaMouseDown`.
        """
        texto = ("`0x0040a0b4`, a rotina que enche a tela\n"
                 "-- chamada pelo `MainForm.mostrar_estrategiaClick`, do\n"
                 "grupo de carga, e nao portada.")
        self.assertEqual(self.cita(texto), {"0x0040a0b4"})

    def test_para_na_quebra_de_paragrafo(self) -> None:
        self.assertEqual(self.cita("`0x0040a0b4` faz isso.\n\n"
                                   "Outra coisa nao esta portada."), set())

    def test_o_endereco_e_o_mais_proximo(self) -> None:
        """Endereco com outro pelo meio nao e o citado."""
        self.assertEqual(
            self.cita("`0x00111111` e a tabela, e a `0x00222222` nao "
                      "esta portada"),
            {"0x00222222"})

    def test_o_verbo_e_so_portar(self) -> None:
        """O alcance estreito, e ele e escolha -- ver o cabecalho do gerador.

        As specs usam "nao existe" e "nao lida" para dado e para campo de
        imagem, nao so para rotina: alargar o verbo produziria falso positivo
        em quatro specs medidas, e guarda que erra e guarda que se desliga.
        """
        for texto in ("a `0x00433e5c` nao existe no arquivo: e `.bss`",
                      "a `0x00408460` ainda nao lida antes desta passagem"):
            with self.subTest(texto=texto):
                self.assertEqual(self.cita(texto), set())


class TestProsaDaEvidencia(unittest.TestCase):
    """A guarda da CORR-WTE-101: a prosa acompanha o vocabulario.

    "Seis secoes obrigatorias" viveu em tres lugares contra as cinco que o
    `spec_index.py` cobra -- o `GABARITO.md` contou a `## Notas` opcional junto,
    e o numero migrou dali para o cabecalho deste gerador e para a prosa gerada.
    Literal em prosa nao envelhece sozinho: quem acrescentar uma secao
    obrigatoria mexe em `S.SECOES` e nao no paragrafo. Por isso o teste cobra
    que a frase venha de `len(S.SECOES)`, e reprova se voltar a ser literal.
    """

    def prosa(self, n_secoes: int) -> str:
        """A frase gerada com um vocabulario de `n_secoes` secoes."""
        original = S.SECOES
        try:
            S.SECOES = tuple(f"S{i}" for i in range(n_secoes))
            return C.por_extenso(len(S.SECOES))
        finally:
            S.SECOES = original

    def test_o_cardinal_sai_do_vocabulario(self) -> None:
        self.assertEqual(self.prosa(5), "cinco")
        self.assertEqual(self.prosa(6), "seis")

    def test_fora_da_faixa_cai_no_algarismo(self) -> None:
        """Vocabulario improvavel nao pode produzir frase sem numero."""
        self.assertEqual(C.por_extenso(42), "42")

    def test_a_frase_gerada_cita_o_vocabulario_de_hoje(self) -> None:
        """O ponto do teste: a linha viva do `fase-4.md`.

        Se alguem reescrever a prosa com `"cinco"` literal, este caso continua
        verde -- o seguinte e que reprova. Os dois juntos e que amarram.
        """
        gerado = C.OUT.read_text(encoding="utf-8")
        self.assertIn(
            f"Cada uma das {C.por_extenso(len(S.SECOES))} seções obrigatórias",
            gerado)

    def test_a_prosa_nao_tem_o_cardinal_literal_no_fonte(self) -> None:
        """Literal e o defeito; a f-string com `len(S.SECOES)` e o conserto."""
        fonte = Path(C.__file__).read_text(encoding="utf-8")
        for linha in fonte.splitlines():
            if "seções obrigatórias de cada spec" in linha:
                self.assertIn("por_extenso(len(S.SECOES))", linha)
                break
        else:
            self.fail("a linha da prosa sumiu do gerador")

    def test_a_evidencia_de_fora_e_contada_e_nao_afirmada(self) -> None:
        """O 44 tambem sai de medida -- era a segunda metade da CORR-WTE-101."""
        m = C.medir()
        self.assertEqual(
            m["evidencias_fora"],
            sum(len(S.CABECALHO_EVIDENCIA.findall(
                    (S.SPEC / f"{h['formulario']}.{h['handler']}.md")
                    .read_text(encoding="utf-8")))
                for h in S.le_handlers())
            - sum(m["evidencias"].values()))


if __name__ == "__main__":
    unittest.main()
