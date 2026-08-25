#!/usr/bin/env python3
"""Testes do gravacao_controle.py -- WTE-TASK-27.

O que se mede aqui e a **leitura da evidencia**, com TSV plantado. O gerador
nao mede nada sozinho: ele cruza duas reguas ja versionadas, e a unica maneira
de ele mentir e cruzando errado.

Dois grupos:

1. a aritmetica das duas colunas -- `escreveu` e syscall, `mudou` e `cmp`, e a
   diferenca entre elas e gravacao de valor IGUAL. Confundi-las devolveria
   "nao gravou" para uma acao que gravou;
2. a evidencia real -- a sessao commitada existe, e o quadro dela bate com o
   `Offsets.hpp` e com a geometria de setor.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import gravacao_controle as G

IO_CAB = "imagem\tsessao\tacao\top\tinicio\tfim\ttamanho\tsetor\tbyte_no_setor"
CMP_CAB = "imagem\tsessao\tinicio\tfim\ttamanho\tsetor\tbyte_no_setor"


class TestCruzamento(unittest.TestCase):
    """`cmp` dentro da escrita, e o que sobra fora dela."""

    def montar(self, io: str, cmp_: str):
        d = tempfile.TemporaryDirectory()
        tmp = Path(d.name)
        (tmp / "io.tsv").write_text(IO_CAB + "\n" + io, encoding="utf-8")
        (tmp / "cmp.tsv").write_text(CMP_CAB + "\n" + cmp_, encoding="utf-8")
        self.addCleanup(d.cleanup)
        a, b = G.IO_TSV, G.CMP_TSV
        G.IO_TSV, G.CMP_TSV = tmp / "io.tsv", tmp / "cmp.tsv"

        def voltar():
            G.IO_TSV, G.CMP_TSV = a, b
        self.addCleanup(voltar)

    def test_gravou_igual_conta_como_escrita_e_nao_como_mudanca(self) -> None:
        """O achado da passagem: 57 bytes escritos, 21 diferentes."""
        s = G.SESSAO
        self.montar(f"a.bin\t{s}\tGRAVA_NOMES\tW\t100\t111\t12\t0\t100\n",
                    f"a.bin\t{s}\t100\t106\t7\t0\t100\n")
        txt = G.gerar()
        self.assertIn("| `GRAVA_NOMES` | 1 | 12 | 7 |", txt)

    def test_acao_sem_escrita_e_resultado_e_nao_lacuna(self) -> None:
        s = G.SESSAO
        self.montar(f"a.bin\t{s}\tGRAVA_BARRAS\t.\t\t\t0\t\t\n", "")
        txt = G.gerar()
        self.assertIn("| `GRAVA_BARRAS` | 0 | 0 | 0 |", txt)
        self.assertIn("**Não tocou a imagem.**", txt)

    def test_faixa_do_cmp_fora_da_escrita_nao_e_creditada(self) -> None:
        """Creditar cmp de outra ação inflaria a coluna sem ninguém ver."""
        s = G.SESSAO
        self.montar(f"a.bin\t{s}\tGRAVA_NOMES\tW\t100\t111\t12\t0\t100\n",
                    f"a.bin\t{s}\t500\t509\t10\t0\t500\n")
        txt = G.gerar()
        self.assertIn("| `GRAVA_NOMES` | 1 | 12 | 0 |", txt)

    def test_sessao_ausente_falha_em_vez_de_gerar_quadro_vazio(self) -> None:
        self.montar("a.bin\toutra\tGRAVA_NOMES\tW\t1\t2\t2\t0\t1\n", "")
        with self.assertRaises(SystemExit):
            G.gerar()


class TestParDeSondas(unittest.TestCase):
    """O par `-sem`/`-com` só é medida enquanto tiver UMA variável de diferença.

    Mesma guarda que o `test_analisar_crash.py` põe no par 07/08: editar um dos
    dois sem o outro não quebra nada visivelmente -- a afirmação simplesmente
    deixa de ser sustentada, e o doc gerado continua a fazendo.
    """

    ROTEIROS = G.ROOT / "wte" / "tests" / "roteiros"

    def corpo(self, nome: str) -> list[str]:
        txt = (self.ROTEIROS / nome).read_text(encoding="utf-8")
        return [l for l in txt.splitlines()
                if l.strip() and not l.lstrip().startswith("#")]

    def test_a_sonda_com_e_a_sem_mais_a_descarga(self) -> None:
        sem = self.corpo("27-descarga-sem.txt")
        com = self.corpo("27-descarga-com.txt")
        self.assertEqual(sem[:-1], com[:len(sem) - 1],
                         "os dois deixaram de ser o mesmo roteiro")
        self.assertEqual(com[len(sem) - 1:],
                         ["! clique 50 46", "~ 1", "! tecla Down", "~ 6",
                          "= GRAVA_BARRAS"])

    def test_o_resultado_medido_e_oposto(self) -> None:
        io = G.ler_tsv(G.IO_TSV)

        def escritas(sessao: str) -> list[dict]:
            return [r for r in io if r["sessao"] == sessao
                    and r["acao"] == "GRAVA_BARRAS" and r["op"] == "W"]

        self.assertEqual(escritas(G.SONDA_SEM), [],
                         "sem descarga o clique nao pode ter gravado")
        self.assertEqual(len(escritas(G.SONDA_COM)), 1,
                         "com descarga os 5 bytes tem de aparecer")
        self.assertEqual(escritas(G.SONDA_COM)[0]["tamanho"], "5")


class TestRotulo(unittest.TestCase):
    """Nomear a região pelo `OFS_*` anterior afirma POSIÇÃO, não semântica."""

    def test_exato_nao_ganha_deslocamento(self) -> None:
        self.assertEqual(G.rotulo(10, {"OFS_A": 10}), "OFS_A")

    def test_entre_dois_escolhe_o_anterior(self) -> None:
        self.assertEqual(G.rotulo(15, {"OFS_A": 10, "OFS_B": 20}), "OFS_A+5")

    def test_antes_do_primeiro(self) -> None:
        self.assertEqual(G.rotulo(1, {"OFS_A": 10}), "antes do primeiro offset")


class TestEvidencia(unittest.TestCase):
    """A sessão commitada, não uma inventada."""

    def test_a_sessao_da_task_esta_versionada(self) -> None:
        io, _ = G.faixas_da_sessao()
        acoes = {r["acao"] for r in io}
        self.assertIn("GRAVA_NOMES", acoes)
        self.assertIn("GRAVA_BARRAS", acoes)

    def test_toda_faixa_do_cmp_cabe_numa_escrita_do_trace(self) -> None:
        """Se não coubesse, o trace teria perdido syscall -- já aconteceu."""
        io, cmp_ = G.faixas_da_sessao()
        escritas = [(int(r["inicio"]), int(r["fim"]))
                    for r in io if r["op"] == "W"]
        for r in cmp_:
            i, j = int(r["inicio"]), int(r["fim"])
            self.assertTrue(any(a <= i and j <= b for a, b in escritas),
                            f"faixa {i}..{j} fora de toda escrita")

    def test_o_setor_declarado_bate_com_a_geometria(self) -> None:
        io, _ = G.faixas_da_sessao()
        for r in io:
            if r["op"] == ".":
                continue
            self.assertEqual(int(r["setor"]), int(r["inicio"]) // G.SETOR)


class TestPayload(unittest.TestCase):
    """A conta de EDC/ECC. Ela nao mede nada sozinha -- afirma sobre o TSV."""

    def test_nenhuma_faixa_medida_toca_edc_ecc(self) -> None:
        self.assertEqual(G.fora_do_payload(), [],
                         "faixa medida fora dos 2048 B de payload")

    def test_as_sessoes_saem_do_tsv_e_nao_de_lista_a_mao(self) -> None:
        sess = G.sessoes_da_task()
        self.assertIn(G.SESSAO, sess)
        for nome in sess:
            self.assertTrue(nome.startswith("27-"), nome)

    def test_o_limite_do_payload_e_a_geometria_mode2(self) -> None:
        # 24 + 2048 + 280 = 2352. Se um dos tres mudar, a conta inteira muda.
        self.assertEqual(G.PAYLOAD_INICIO, 24)
        self.assertEqual(G.PAYLOAD_FIM, 24 + 2048 - 1)
        self.assertEqual(G.SETOR, 2352)

    def test_detecta_faixa_plantada_no_edc(self) -> None:
        # Sem esta, "nenhuma fora" poderia significar "a conta nao ve nada".
        ruim = [("x", 24 + 2048, 24 + 2048)]
        pos = ruim[0][1] % G.SETOR
        self.assertFalse(G.PAYLOAD_INICIO <= pos <= G.PAYLOAD_FIM)


class TestIdempotencia(unittest.TestCase):
    """A guarda da CORR-WTE-109: a prosa nao pode reatribuir o sujeito.

    *"O `Load`+`Save` do editor original nao e idempotente"* e verdadeira no
    `newWe2002`, onde o oraculo E o `ed.exe`. Migrada para este projeto ela
    trocou de sujeito sem trocar de palavras -- aqui "o original" e o `wte.exe`
    do Obocaman, que nem tem ciclo `Load`+`Save` de banco inteiro.

    Nao da para remedir isso em `--check`: os numeros saem de corrida de golden,
    com `:98`, Wine e ~600 MB de temporario. O que da e cobrar COERENCIA entre a
    tabela e a prosa que ela gera -- e e essa a forma de a frase voltar, escrita
    por alguem que nao leu a tabela.
    """

    def texto(self) -> str:
        return G.gerar()

    def test_a_prosa_nao_atribui_a_nao_idempotencia_ao_editor_original(self) -> None:
        """O defeito literal, no texto GERADO."""
        for forma in ("do editor original não é idempotente",
                      "do original não é idempotente"):
            self.assertNotIn(forma, self.texto())

    def test_a_prosa_nomeia_o_ed_exe_como_dono_da_frase(self) -> None:
        """Nao basta tirar: sem o sujeito certo a frase volta pela mesma porta."""
        self.assertIn("`ed.exe`", self.texto())

    def test_os_numeros_da_prosa_saem_da_tabela(self) -> None:
        """Literal em prosa nao envelhece com a medida."""
        i, texto = G.IDEMPOTENCIA, self.texto()
        for chave in ("tatica_virgem_x_uma", "mcr2iso_virgem_x_uma",
                      "times_com_par_desigual"):
            with self.subTest(chave=chave):
                self.assertIn(str(i[chave]), texto)

    def test_a_tabela_afirma_idempotencia_nos_dois_caminhos(self) -> None:
        """Se um dia um caminho trocar, a tabela muda e este caso reprova --
        e a prosa acima deixa de poder dizer o que diz."""
        i = G.IDEMPOTENCIA
        self.assertEqual(i["tatica_uma_x_duas"], 0)
        self.assertEqual(i["mcr2iso_uma_x_duas"], 0)
        self.assertEqual(i["times_que_trocaram"], 0)

    def test_o_zero_nao_e_cego(self) -> None:
        """Zero so vale se houvesse onde a troca aparecer.

        E a licao da CORR-WTE-104: o `golden-24` gravava num time onde os dois
        cobradores eram iguais, e ali o zero nao distinguia nada.
        """
        self.assertGreater(G.IDEMPOTENCIA["times_com_par_desigual"], 0)

    def test_a_gravacao_aconteceu_nos_dois(self) -> None:
        """O outro jeito de o zero ser trivial: nenhum dos lados gravar."""
        i = G.IDEMPOTENCIA
        self.assertGreater(i["tatica_virgem_x_uma"], 0)
        self.assertGreater(i["mcr2iso_virgem_x_uma"], 0)


if __name__ == "__main__":
    unittest.main()
