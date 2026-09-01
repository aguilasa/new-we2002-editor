#!/usr/bin/env python3
"""Testes do `check_fase1.py`: o perimetro da varredura e o corte por contexto.

O que este arquivo cobre e a logica **nova** da WTE-TASK-09 -- quem entra na
varredura de sitios, onde ela para de ler, e por que o corte exige contexto. As
contagens em si vem dos produtos das WTE-TASK-03 a 08, que ja tem `--check`
proprio; re-afirma-las aqui seria copiar a medida, nao testa-la.

Como o resto da bateria, **nao abre o `.exe`**: monta arvore de markdown em
diretorio temporario e aponta o `ROOT` do modulo para la.
"""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

import check_fase1 as mod


class TesteCorteContexto(unittest.TestCase):
    """O digito sozinho nao basta: dois projetos usam os mesmos numeros."""

    def _casa(self, chave: str, linha: str) -> bool:
        num, ctx, cur = next(
            (n, c, v) for nome, n, c, v, _ in mod.SITIOS if nome == chave)
        return bool(re.search(rf"\b{num}\b", linha) and re.search(ctx, linha)
                    and not mod._e_historia(linha, num, cur))

    def test_bitmaps_casa_afirmacao_viva(self):
        for linha in (
            "| Bitmaps externos em `image/` | 197 |",
            "197 bitmaps e um blob, todos em formato aberto",
            "Os 197 BMP e o `dat.bin` **não são redistribuídos**",
            "- `wte/assets/` alcança os 197 `.bmp` e o `data/dat.bin`",
        ):
            self.assertTrue(self._casa("197 bitmaps", linha), linha)

    def test_componentes_nao_casa_setor_do_outro_projeto(self):
        # O PLAN-LINUX fala do setor 430 da imagem de CD -- outro projeto,
        # outro assunto, mesmo digito. Sem o contexto isso viraria residuo.
        self.assertFalse(self._casa(
            "~430 componentes",
            "OFS_NOMI_SQ1 = 1012640  -> setor 430, byte 1280"))
        self.assertTrue(self._casa(
            "~430 componentes", "| Componentes nos formulários | ~430 |"))

    def test_imports_nao_casa_setores_de_ecc(self):
        self.assertFalse(self._casa(
            "300 imports de rtl60/vcl60",
            "| ECC | integro (0/300 setores amostrados zerados) |"))
        self.assertTrue(self._casa(
            "300 imports de rtl60/vcl60",
            "| Imports | 322, sendo 300 de `rtl60.bpl`/`vcl60.bpl` |"))

    def test_strings_exige_palavra_de_contexto(self):
        self.assertFalse(self._casa(
            "70 strings com enchimento", "o slot 70 da tabela fica vazio"))
        self.assertTrue(self._casa(
            "70 strings com enchimento",
            "o patch e so string, in-place -- 70 strings terminam em espaco"))

    def test_antes_e_constante_com_perimetro_escrito(self):
        # A coluna "sitios antes" nao e remedivel depois da correcao. Se
        # alguem zerar as constantes, a tabela da saida passa a dizer 0 -> 0 e
        # perde o unico registro que existe da varredura. Foi 19 ate a
        # CORR-WTE-018 remedir com `docs/prompts/` dentro do perimetro, o que
        # somou os tres sitios do `02-revisar.md`.
        self.assertEqual(sum(a for *_, a in mod.SITIOS), 22)


class TesteFormaDeHistoria(unittest.TestCase):
    """`velho -> corrente` diz o que mudou; o numero sozinho afirma o valor.

    Ate a CORR-WTE-018 a forma de historia so passava por acidente de quebra
    de linha: o bloco do `wte/README.md` tem o numero numa linha e a palavra
    de contexto noutra. Reflowar o paragrafo deixaria o `--check` vermelho sem
    nada ter piorado.
    """

    def _casa(self, chave: str, linha: str) -> bool:
        num, ctx, cur = next(
            (n, c, v) for nome, n, c, v, _ in mod.SITIOS if nome == chave)
        return bool(re.search(rf"\b{num}\b", linha) and re.search(ctx, linha)
                    and not mod._e_historia(linha, num, cur))

    def test_seta_para_o_corrente_e_historia(self):
        for linha in (
            "Exemplos do que já mudou uma vez: bitmaps (197 → 198).",
            "bitmaps (197 -> 198)",
            "o `.bmp`: `197` → `441`".replace("441", "198"),
            "**197 → 198** bitmaps, reconciliado na WTE-TASK-09",
        ):
            self.assertFalse(self._casa("197 bitmaps", linha), linha)

    def test_seta_para_outro_numero_nao_e_historia(self):
        # `197 -> 200` nao e a reconciliacao desta guarda: e afirmacao nova,
        # e tem de acusar. Senao qualquer seta viraria passe livre.
        self.assertTrue(self._casa("197 bitmaps", "bitmaps: 197 → 200"))

    def test_numero_velho_sozinho_continua_acusando(self):
        for chave, linha in (
            ("197 bitmaps", "a §1 do plano registra 197 bitmaps"),
            ("~430 componentes", "| Componentes nos formulários | ~430 |"),
            ("70 strings com enchimento", "70 strings com padding"),
        ):
            self.assertTrue(self._casa(chave, linha), linha)

    def test_historia_das_outras_tres(self):
        for chave, linha in (
            ("~430 componentes", "componentes (`~430` → 441)"),
            ("70 strings com enchimento", "strings com enchimento (70 → 13)"),
            ("300 imports de rtl60/vcl60", "imports de rtl60 (300 → 267)"),
        ):
            self.assertFalse(self._casa(chave, linha), linha)


class TesteCorteDeFaixa(unittest.TestCase):
    """A §3 parte os confirmados por endereço; o corte tem de ser por faixa.

    Até a CORR-WTE-017 ele era `"0x0042" not in va`. Cada teste daqui planta um
    endereço que a substring classifica errado e a faixa classifica certo — sem
    entrada plantada a guarda nova é guarda não exercitada.
    """

    def _linha(self, va: str, nota: str, nome: str = "OFS_PLANTADO"):
        return {"nome": nome, "va": va, "nota": nota, "classe": "confirmado"}

    def _substring(self, va: str) -> bool:
        """O corte velho, para provar que os dois discordam."""
        return "0x0042" not in va

    def test_fim_de_text_casa_a_substring_e_nao_a_faixa(self):
        # 0x00422abc e legitimo dentro de .text: .text vai ate 0x00423000.
        va = "0x00422abc"
        self.assertFalse(self._substring(va))   # velho: diria "mora na tabela"
        self.assertFalse(mod._em_data(va))      # novo: imediato de .text

    def test_data_alta_nao_casa_a_substring_e_casa_a_faixa(self):
        # O outro sentido: .data vai ate 0x0043c000, entao passa de 0x0042ffff.
        va = "0x00430010"
        self.assertTrue(self._substring(va))    # velho: diria "so em .text"
        self.assertTrue(mod._em_data(va))       # novo: mora em .data

    def test_enderecos_reais_do_binario(self):
        self.assertTrue(mod._em_data("0x004231bc|0x0042b76c"))
        self.assertTrue(mod._em_data("0x004054b7|0x0042363c"))  # .data,.text
        self.assertFalse(mod._em_data("0x0040448c|0x00404628"))
        self.assertFalse(mod._em_data("0x004042fd"))  # contem "0042", e .text

    def test_plantado_sai_como_imediato_e_nao_como_slot(self):
        confirmados = [self._linha("0x004231bc", ".data", "OFS_NA_TABELA"),
                       self._linha("0x00422abc", ".text")]
        slots = [self._linha("0x004231bc", ".data", "OFS_NA_TABELA")]
        fora = mod.particionar_confirmados(confirmados, slots)
        self.assertEqual([r["nome"] for r in fora], ["OFS_PLANTADO"])

    def test_nota_discordante_aborta(self):
        # A constante DATA_VA e medida e duplicada aqui; quem a segura e a
        # coluna `nota`, que vem do leitor de PE do dump_offsets.py.
        confirmados = [self._linha("0x00422abc", ".data")]
        with self.assertRaises(mod.CheckError) as ctx:
            mod.particionar_confirmados(confirmados, [])
        self.assertIn("discorda da secao", str(ctx.exception))

    def test_particao_que_nao_bate_com_os_slots_aborta(self):
        confirmados = [self._linha("0x004231bc", ".data")]
        with self.assertRaises(mod.CheckError) as ctx:
            mod.particionar_confirmados(confirmados, [])
        self.assertIn("nao bate com os slots preenchidos", str(ctx.exception))


class TestePerimetro(unittest.TestCase):
    """Quem entra na varredura, e ate que linha ela le."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        (self.raiz / "docs" / "tasks").mkdir(parents=True)
        (self.raiz / "docs" / "prompts").mkdir(parents=True)
        (self.raiz / "wte" / "re").mkdir(parents=True)
        self._root_original = mod.ROOT
        mod.ROOT = self.raiz
        self.addCleanup(self._restaura)

    def _restaura(self):
        mod.ROOT = self._root_original
        self._tmp.cleanup()

    def _escreve(self, rel: str, texto: str) -> Path:
        p = self.raiz / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto, encoding="utf-8")
        return p

    def test_task_concluida_sai_do_perimetro(self):
        feito = self._escreve(
            "docs/tasks/08-assets.md", "---\nstatus: concluído\n---\ncorpo\n")
        pendente = self._escreve(
            "docs/tasks/concluidos/39-empacotamento.md", "---\nstatus: pendente\n---\nx\n")
        self.assertFalse(mod._no_perimetro(feito))
        self.assertTrue(mod._no_perimetro(pendente))

    def test_narracao_sai_do_perimetro(self):
        for rel in ("docs/tasks/concluidos/correcoes-progresso.md",
                    "docs/tasks/concluidos/CORR-WTE-014.md",
                    "docs/tasks/concluidos/09-fechamento-fase-1.md",
                    "wte/re/assets.md",
                    "wte/re/strings.md",
                    # narra a propria guarda, e cita 430 para explicar o corte
                    "wte/tools/README.md",
                    f"wte/re/{mod.MD_NAME}"):
            self.assertFalse(mod._no_perimetro(self._escreve(rel, "x\n")), rel)

    def test_plano_e_progresso_ficam_no_perimetro(self):
        # `wte/README.md` entrou com a CORR-WTE-016: era o sitio vivo que o
        # perimetro antigo (`docs/` + `wte/re/`) nao alcancava. Os prompts
        # entraram com a CORR-WTE-018, pelo mesmo motivo -- a exclusao deles
        # valia para destino de link, que nao e o que esta guarda mede.
        for rel in ("docs/PLAN-WTE-LAZARUS.md", "docs/tasks/concluidos/progresso.md",
                    "wte/re/offsets.md", "wte/README.md",
                    "docs/prompts/01-executar.md",
                    "docs/prompts/02-revisar.md"):
            self.assertTrue(mod._no_perimetro(self._escreve(rel, "x\n")), rel)

    def test_varrer_acha_residuo_em_prompt(self):
        # O sitio real da CORR-WTE-018: um prompt citando o numero aposentado
        # como "o que ja esta no plano".
        p = self._escreve("docs/prompts/02-revisar.md",
                          "Exemplos: ~430 componentes, 197 bitmaps.\n")
        achados = dict(mod.varrer())
        self.assertEqual(len(achados["197 bitmaps"]), 1)
        self.assertEqual(len(achados["~430 componentes"]), 1)
        p.write_text("Exemplos do que mudou: componentes (~430 → 441), "
                     "bitmaps (197 → 198).\n", encoding="utf-8")
        achados = dict(mod.varrer())
        self.assertEqual(achados["197 bitmaps"], [])
        self.assertEqual(achados["~430 componentes"], [])

    def test_log_de_execucao_nao_e_lido(self):
        p = self._escreve("docs/tasks/40-final.md", "\n".join([
            "---", "status: pendente", "---",
            "corpo com 197 bitmaps",
            mod.LOG_HEADER,
            "- corrigi o 197 bitmaps aqui",
            "",
        ]))
        vivas = [linha for _, linha in mod._linhas_vivas(p)]
        self.assertIn("corpo com 197 bitmaps", vivas)
        self.assertNotIn("- corrigi o 197 bitmaps aqui", vivas)

    def test_arquivo_sem_log_e_lido_inteiro(self):
        p = self._escreve("docs/PLAN-WTE-LAZARUS.md", "a\nb\nc\n")
        self.assertEqual([l for _, l in mod._linhas_vivas(p)], ["a", "b", "c"])

    def test_markdowns_alcanca_wte_inteiro(self):
        # O `_no_perimetro` sozinho nao segura o alargamento: ele diria True
        # para `wte/README.md` mesmo com a base velha, porque nunca e chamado.
        # Quem escolhe os candidatos e o `_markdowns`, e e ele que a
        # CORR-WTE-016 mudou.
        for rel in ("docs/PLAN-WTE-LAZARUS.md", "wte/re/offsets.md",
                    "wte/README.md", "wte/tools/README.md"):
            self._escreve(rel, "x\n")
        achados = {p.relative_to(self.raiz).as_posix()
                   for p in mod._markdowns()}
        self.assertIn("wte/README.md", achados)
        self.assertIn("wte/tools/README.md", achados)
        self.assertIn("wte/re/offsets.md", achados)
        # e nenhum arquivo aparece duas vezes: `rglob` sobre `wte` ja cobre
        # `wte/re/`, entao a segunda base saiu
        self.assertEqual(len(mod._markdowns()), len(achados))

    def test_varrer_acha_residuo_no_readme_do_wte(self):
        alvo = self._escreve("wte/README.md",
                             "> **198, não 197.** A §1 registra 197 `.bmp`\n")
        self.assertEqual(len(dict(mod.varrer())["197 bitmaps"]), 1)
        alvo.write_text("> **São 198.** A §1 já registra 198 `.bmp`\n",
                        encoding="utf-8")
        self.assertEqual(dict(mod.varrer())["197 bitmaps"], [])

    def test_varrer_acha_residuo_e_zera_quando_corrigido(self):
        alvo = self._escreve("docs/tasks/concluidos/progresso.md",
                             "| Assets | 197 `.bmp` |\n")
        achados = dict(mod.varrer())
        self.assertEqual(len(achados["197 bitmaps"]), 1)
        alvo.write_text("| Assets | 198 `.bmp` |\n", encoding="utf-8")
        self.assertEqual(dict(mod.varrer())["197 bitmaps"], [])


if __name__ == "__main__":
    unittest.main()
