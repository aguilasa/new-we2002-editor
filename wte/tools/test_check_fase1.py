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
        num, ctx = next((n, c) for nome, n, c, _ in mod.SITIOS if nome == chave)
        return bool(re.search(rf"\b{num}\b", linha) and re.search(ctx, linha))

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
        # perde o unico registro que existe da varredura.
        self.assertEqual(sum(a for *_, a in mod.SITIOS), 19)


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
            "docs/tasks/39-empacotamento.md", "---\nstatus: pendente\n---\nx\n")
        self.assertFalse(mod._no_perimetro(feito))
        self.assertTrue(mod._no_perimetro(pendente))

    def test_narracao_e_prompt_saem_do_perimetro(self):
        for rel in ("docs/tasks/correcoes-progresso.md",
                    "docs/tasks/CORR-WTE-014.md",
                    "docs/tasks/09-fechamento-fase-1.md",
                    "docs/prompts/01-executar.md",
                    "wte/re/assets.md",
                    "wte/re/strings.md",
                    # narra a propria guarda, e cita 430 para explicar o corte
                    "wte/tools/README.md",
                    f"wte/re/{mod.MD_NAME}"):
            self.assertFalse(mod._no_perimetro(self._escreve(rel, "x\n")), rel)

    def test_plano_e_progresso_ficam_no_perimetro(self):
        # `wte/README.md` entrou com a CORR-WTE-016: era o sitio vivo que o
        # perimetro antigo (`docs/` + `wte/re/`) nao alcancava.
        for rel in ("docs/PLAN-WTE-LAZARUS.md", "docs/tasks/progresso.md",
                    "wte/re/offsets.md", "wte/README.md"):
            self.assertTrue(mod._no_perimetro(self._escreve(rel, "x\n")), rel)

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
        alvo = self._escreve("docs/tasks/progresso.md",
                             "| Assets | 197 `.bmp` |\n")
        achados = dict(mod.varrer())
        self.assertEqual(len(achados["197 bitmaps"]), 1)
        alvo.write_text("| Assets | 198 `.bmp` |\n", encoding="utf-8")
        self.assertEqual(dict(mod.varrer())["197 bitmaps"], [])


if __name__ == "__main__":
    unittest.main()
