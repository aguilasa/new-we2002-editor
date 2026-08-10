#!/usr/bin/env python3
"""Testes do spec_index.py (WTE-TASK-23).

Montam TSV e specs num diretorio temporario -- NAO abrem o
we-team-editor.exe, e rodam num clone sem a pasta do Obocaman. Cobrem o que
nenhuma spec real cobre hoje, porque hoje nao existe nenhuma: as rotas de
recusa. `--check` verde sobre 96 `aberto` nao mede regra nenhuma.

Sao tambem a prova do criterio "gerador de indice funcionando sobre um `.md`
de exemplo" -- o exemplo e sintetico de proposito: uma spec de verdade e
trabalho da WTE-TASK-25 em diante, e commitar uma spec inventada so para o
gerador ter o que ler poria hipotese em `re/spec/` com cara de fato.
"""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import spec_index


CABECALHO = ("endereco\thandler\tformulario\tcomponente\tevento\tgrupo\t"
             "regra\tnota")

SPEC_BOA = """\
---
handler: {handler}
formulario: {formulario}
endereco: {endereco}
veredito: {veredito}
---

# {formulario}.{handler}

## Entrada

O indice do time selecionado.

**Evidência:** observação de tela

## Saída

Enche os 23 campos de nome.

**Evidência:** diff medido

## Bytes tocados

nenhum

**Evidência:** diff medido

## Pré-condições

Nao checa nada.

**Evidência:** disassembly lido

## Comportamento de erro

Nao trata.

**Evidência:** disassembly lido
{extra}"""


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        raiz = Path(self._tmp.name)
        spec = raiz / "wte" / "re" / "spec"
        spec.mkdir(parents=True)
        self.spec = spec
        self.tsv = raiz / "wte" / "re" / "published_methods.tsv"
        self.indice = spec / "INDICE.md"

        self._antigo = (spec_index.RAIZ, spec_index.TSV, spec_index.SPEC,
                        spec_index.INDICE)
        spec_index.RAIZ = raiz
        spec_index.TSV = self.tsv
        spec_index.SPEC = spec
        spec_index.INDICE = self.indice

        self.escreve_tsv([
            ("0x00402b40", "BitBtn1Click", "ficha_dorsal", "BitBtn1",
             "OnClick", "auxiliar"),
            ("0x004120a4", "lista_equiposChange", "MainForm", "lista_equipos",
             "OnChange", "carga"),
        ])

    def tearDown(self):
        (spec_index.RAIZ, spec_index.TSV, spec_index.SPEC,
         spec_index.INDICE) = self._antigo
        self._tmp.cleanup()

    def escreve_tsv(self, linhas):
        corpo = [CABECALHO]
        for endereco, handler, form, comp, evento, grupo in linhas:
            corpo.append(f"{endereco}\t{handler}\t{form}\t{comp}\t{evento}\t"
                         f"{grupo}\tR1\t")
        self.tsv.write_text("\n".join(corpo) + "\n", encoding="utf-8")

    def escreve_spec(self, formulario, handler, endereco, veredito="aberto",
                     extra="", molde=SPEC_BOA):
        texto = molde.format(handler=handler, formulario=formulario,
                             endereco=endereco, veredito=veredito, extra=extra)
        alvo = self.spec / f"{formulario}.{handler}.md"
        alvo.write_text(texto, encoding="utf-8")
        return alvo


class TestIndice(Base):
    def test_sem_spec_nenhuma_todos_abertos(self):
        texto, contagem = spec_index.monta()
        self.assertEqual(contagem["total"], 2)
        self.assertEqual(contagem["aberto"], 2)
        self.assertEqual(contagem["com spec"], 0)
        self.assertIn("| `0x004120a4` | `MainForm` |", texto)

    def test_spec_valida_entra_com_o_veredito_e_com_link(self):
        self.escreve_spec("MainForm", "lista_equiposChange", "0x004120a4",
                          veredito="trivial")
        texto, contagem = spec_index.monta()
        self.assertEqual(contagem["trivial"], 1)
        self.assertEqual(contagem["aberto"], 1)
        self.assertEqual(contagem["com spec"], 1)
        self.assertIn("[lista_equiposChange](MainForm.lista_equiposChange.md)",
                      texto)

    def test_evento_repetido_vira_contagem_e_nao_barra(self):
        # `|` cru quebraria a tabela markdown.
        self.escreve_tsv([("0x00405e40", "barraChange", "ficha_color",
                           "barra_rojo|barra_verde|barra_azul",
                           "OnChange|OnChange|OnChange", "edicao")])
        texto, _ = spec_index.monta()
        linha = [l for l in texto.splitlines() if l.startswith("| `0x")][0]
        self.assertIn("OnChange x3", linha)
        self.assertEqual(linha.count("|"), 7)

    def test_evento_vazio_vira_travessao(self):
        self.escreve_tsv([("0x0040c9c4", "Button2Click", "MainForm", "", "",
                           "auxiliar")])
        texto, _ = spec_index.monta()
        linha = [l for l in texto.splitlines() if l.startswith("| `0x")][0]
        self.assertIn("| — |", linha)

    def test_check_reclama_quando_o_indice_esta_velho(self):
        # O `main` fala em stdout/stderr; calar os dois mantem a saida de
        # `make -C wte check` legivel -- um ERRO esperado no meio da bateria
        # ensina a ignorar vermelho.
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(spec_index.main(["spec_index.py"]), 0)
            self.escreve_spec("MainForm", "lista_equiposChange",
                              "0x004120a4", veredito="trivial")
            self.assertEqual(spec_index.main(["spec_index.py", "--check"]), 2)
            self.assertEqual(spec_index.main(["spec_index.py"]), 0)
            self.assertEqual(spec_index.main(["spec_index.py", "--check"]), 0)


class TestRecusa(Base):
    def erro(self, **kwargs):
        self.escreve_spec(**kwargs)
        with self.assertRaises(spec_index.SpecError) as ctx:
            spec_index.monta()
        return str(ctx.exception)

    def test_recusa_tsv_ausente(self):
        self.tsv.unlink()
        with self.assertRaises(spec_index.SpecError) as ctx:
            spec_index.monta()
        self.assertIn("nao existe", str(ctx.exception))
        self.assertIn("WTE-TASK-04", str(ctx.exception))

    def test_recusa_tsv_so_com_cabecalho(self):
        self.tsv.write_text(CABECALHO + "\n", encoding="utf-8")
        with self.assertRaises(spec_index.SpecError) as ctx:
            spec_index.monta()
        self.assertIn("nao tem nenhum handler", str(ctx.exception))

    def test_recusa_frontmatter_nao_fechado(self):
        molde = SPEC_BOA.replace("veredito: {veredito}\n---\n",
                                 "veredito: {veredito}\n", 1)
        msg = self.erro(formulario="MainForm", handler="lista_equiposChange",
                        endereco="0x004120a4", molde=molde)
        self.assertIn("frontmatter nao fechado", msg)

    def test_recusa_linha_de_frontmatter_sem_dois_pontos(self):
        molde = SPEC_BOA.replace("veredito: {veredito}\n",
                                 "veredito: {veredito}\nlixo sem dois pontos\n",
                                 1)
        msg = self.erro(formulario="MainForm", handler="lista_equiposChange",
                        endereco="0x004120a4", molde=molde)
        self.assertIn("sem ':'", msg)

    def test_recusa_chave_obrigatoria_ausente(self):
        # A rota que a primeira spec de verdade vai encontrar: esquecer o
        # `veredito`. Tem de sair com a mensagem propria, nao com KeyError.
        molde = SPEC_BOA.replace("veredito: {veredito}\n", "", 1)
        msg = self.erro(formulario="MainForm", handler="lista_equiposChange",
                        endereco="0x004120a4", molde=molde)
        self.assertIn("falta 'veredito' no frontmatter", msg)

    def test_recusa_bloco_de_codigo_c(self):
        msg = self.erro(formulario="MainForm", handler="lista_equiposChange",
                        endereco="0x004120a4",
                        extra="\n## Notas\n\n```c\nint i = 0;\n```\n")
        self.assertIn("decompilado colado", msg)

    def test_recusa_nomes_inventados_pelo_ghidra(self):
        for trecho in ("undefined4 x;", "iVar1 = 3;", "local_1c = 0;",
                       "param_1 + 4", "DAT_004231a0", "FUN_00401a2e",
                       "__fastcall algo(void)"):
            with self.subTest(trecho=trecho):
                msg = self.erro(formulario="MainForm",
                                handler="lista_equiposChange",
                                endereco="0x004120a4",
                                extra=f"\n## Notas\n\n{trecho}\n")
                self.assertIn("decompilado colado", msg)

    def test_recusa_o_cast_do_ghidra(self):
        # A marca que sobrevive a quem renomeia `uVar1`/`param_1` antes de
        # colar: cast para tipo C do deref de ponteiro para tipo C.
        for trecho in ("(int)*(int *)(param + 8)",
                       "(int)*(int *)(this + 8)",
                       "(int) * (int *) (this + 8)",
                       "(uint)*(ushort *)(p + 2)",
                       "(byte)*(undefined1 *)(p + 1)"):
            with self.subTest(trecho=trecho):
                msg = self.erro(formulario="MainForm",
                                handler="lista_equiposChange",
                                endereco="0x004120a4",
                                extra=f"\n## Notas\n\n{trecho}\n")
                self.assertIn("decompilado colado", msg)

    def test_o_cast_do_ghidra_nao_pega_prosa(self):
        # Falso positivo aqui torna o gabarito impossivel de cumprir: uma spec
        # legitima fala de tipo C e usa parenteses o tempo todo.
        prosa = ("O campo `cost` e `(int)` no C++ e `LongInt` no Pascal. "
                 "O time (int) e o jogador (char) sao lidos juntos, e a barra "
                 "(5) * (o peso do time) entra no preco. A lista (int) * 2 "
                 "posicoes fica no fim.")
        self.escreve_spec("MainForm", "lista_equiposChange", "0x004120a4",
                          extra=f"\n## Notas\n\n{prosa}\n")
        _, contagem = spec_index.monta()
        self.assertEqual(contagem["com spec"], 1)

    def test_aceita_pseudocodigo_em_bloco_text(self):
        self.escreve_spec("MainForm", "lista_equiposChange", "0x004120a4",
                          extra="\n## Notas\n\n```text\npara cada slot: "
                                "le o nome\n```\n")
        _, contagem = spec_index.monta()
        self.assertEqual(contagem["com spec"], 1)

    def test_recusa_veredito_fora_do_vocabulario(self):
        msg = self.erro(formulario="MainForm", handler="lista_equiposChange",
                        endereco="0x004120a4", veredito="quase pronto")
        self.assertIn("fora do vocabulario", msg)

    def test_recusa_secao_faltando(self):
        molde = SPEC_BOA.replace("## Comportamento de erro\n\nNao trata.\n\n"
                                 "**Evidência:** disassembly lido\n", "")
        self.escreve_spec("MainForm", "lista_equiposChange", "0x004120a4",
                          molde=molde)
        with self.assertRaises(spec_index.SpecError) as ctx:
            spec_index.monta()
        self.assertIn("Comportamento de erro", str(ctx.exception))

    def test_recusa_secao_sem_evidencia(self):
        molde = SPEC_BOA.replace("Nao checa nada.\n\n"
                                 "**Evidência:** disassembly lido",
                                 "Nao checa nada.")
        self.escreve_spec("MainForm", "lista_equiposChange", "0x004120a4",
                          molde=molde)
        with self.assertRaises(spec_index.SpecError) as ctx:
            spec_index.monta()
        self.assertIn("sem linha", str(ctx.exception))

    def test_recusa_evidencia_inventada(self):
        molde = SPEC_BOA.replace("**Evidência:** diff medido",
                                 "**Evidência:** achei que sim", 1)
        self.escreve_spec("MainForm", "lista_equiposChange", "0x004120a4",
                          molde=molde)
        with self.assertRaises(spec_index.SpecError) as ctx:
            spec_index.monta()
        self.assertIn("fora do", str(ctx.exception))

    def test_recusa_nao_portado_sem_justificativa(self):
        msg = self.erro(formulario="MainForm", handler="lista_equiposChange",
                        endereco="0x004120a4", veredito="nao portado")
        self.assertIn("Justificativa", msg)

    def test_aceita_nao_portado_com_justificativa(self):
        self.escreve_spec("MainForm", "lista_equiposChange", "0x004120a4",
                          veredito="nao portado",
                          extra="\n## Justificativa\n\nDepende do SoFIFA, "
                                "que esta desligado.\n")
        _, contagem = spec_index.monta()
        self.assertEqual(contagem["nao portado"], 1)

    def test_recusa_implementado_so_com_observacao_de_tela(self):
        molde = SPEC_BOA.replace("**Evidência:** diff medido",
                                 "**Evidência:** observação de tela")
        molde = molde.replace("**Evidência:** disassembly lido",
                              "**Evidência:** não medido")
        self.escreve_spec("MainForm", "lista_equiposChange", "0x004120a4",
                          veredito="implementado", molde=molde)
        with self.assertRaises(spec_index.SpecError) as ctx:
            spec_index.monta()
        self.assertIn("hipotese", str(ctx.exception))

    def test_recusa_frontmatter_que_discorda_do_tsv(self):
        msg = self.erro(formulario="MainForm", handler="lista_equiposChange",
                        endereco="0x00000000")
        self.assertIn("published_methods.tsv", msg)

    def test_recusa_spec_orfa(self):
        (self.spec / "MainForm.naoExiste.md").write_text("---\n---\n",
                                                         encoding="utf-8")
        with self.assertRaises(spec_index.SpecError) as ctx:
            spec_index.monta()
        self.assertIn("nao corresponde", str(ctx.exception))

    def test_ignora_os_reservados(self):
        for nome in ("GABARITO.md", "INDICE.md", "README.md"):
            (self.spec / nome).write_text("# nada\n", encoding="utf-8")
        _, contagem = spec_index.monta()
        self.assertEqual(contagem["total"], 2)

    def test_recusa_sem_frontmatter(self):
        (self.spec / "MainForm.lista_equiposChange.md").write_text(
            "# sem frontmatter\n", encoding="utf-8")
        with self.assertRaises(spec_index.SpecError) as ctx:
            spec_index.monta()
        self.assertIn("frontmatter", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
