#!/usr/bin/env python3
"""Testes do analisar_io.py -- WTE-TASK-19.

O que se mede aqui e o **parser do trace**, com linha plantada. Ele e a regua
inteira da task: se ele ler offset errado, o `offsets-novos.md` sai com faixa
errada e ninguem percebe -- o numero continua parecendo medido.

Tres grupos:

1. reconstrucao de posicao -- `_llseek` seguido de `read`/`write`, que e como o
   Wine de 32 bits fala com o arquivo;
2. o que NAO pode entrar: fd de outro arquivo, syscall que devolveu 0 ou -1;
3. a evidencia real -- o `io-medido.tsv` commitado bate com o `Offsets.hpp` e
   com a geometria de setor.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import analisar_io as A

IMG = "dd-run.bin"
CAM = f"16</home/x/work/{IMG}>"


def linha(s: str, pid: str = "1234", hora: str = "10:00:00.000001") -> str:
    return f"{pid} {hora} {s}"


class TestParser(unittest.TestCase):

    def evs(self, *linhas):
        return list(A.eventos([linha(l) for l in linhas], IMG))

    def test_seek_mais_read(self) -> None:
        evs = self.evs(f'_llseek({CAM}, 387792, [387792], SEEK_SET) = 0',
                       f'read({CAM}, "abc"..., 512) = 512')
        self.assertEqual(evs, [("R", 387792, 512)])

    def test_read_sequencial_avanca_a_posicao(self) -> None:
        # Sem isto, duas leituras seguidas sem seek entre elas seriam contadas
        # no mesmo offset -- e a segunda faixa apontaria para o lugar errado.
        evs = self.evs(f'_llseek({CAM}, 1000, [1000], SEEK_SET) = 0',
                       f'read({CAM}, "x"..., 512) = 512',
                       f'read({CAM}, "y"..., 512) = 512')
        self.assertEqual(evs, [("R", 1000, 512), ("R", 1512, 512)])

    def test_write_e_marcado_como_escrita(self) -> None:
        evs = self.evs(f'_llseek({CAM}, 11784, [11784], SEEK_SET) = 0',
                       f'write({CAM}, "A"..., 2048) = 2048')
        self.assertEqual(evs, [("W", 11784, 2048)])

    def test_pread_traz_o_proprio_offset(self) -> None:
        # `pread64` nao mexe na posicao do arquivo; o offset esta no argumento.
        evs = self.evs(f'pread64({CAM}, "..."..., 23, 0) = 23',
                       f'read({CAM}, "z"..., 8) = 8')
        self.assertEqual(evs[0], ("R", 0, 23))

    def test_leitura_curta_conta_o_que_veio(self) -> None:
        evs = self.evs(f'_llseek({CAM}, 100, [100], SEEK_SET) = 0',
                       f'read({CAM}, "x"..., 512) = 30')
        self.assertEqual(evs, [("R", 100, 30)])

    def test_outro_arquivo_nao_entra(self) -> None:
        outro = "8</home/x/work/wineprefix-wte/reg.tmp>"
        evs = self.evs(f'_llseek({outro}, 5, [5], SEEK_SET) = 0',
                       f'write({outro}, "x"..., 4096) = 4096')
        self.assertEqual(evs, [])

    def test_syscall_que_falhou_nao_entra(self) -> None:
        evs = self.evs(f'_llseek({CAM}, 10, [10], SEEK_SET) = 0',
                       f'read({CAM}, ""..., 512) = -1 EAGAIN')
        self.assertEqual(evs, [])

    def test_syscall_partida_em_duas_linhas(self) -> None:
        """`<unfinished ...>` + `<... resumed>`, que e a MAIORIA delas.

        O `strace -f` corta toda syscall que bloqueia. Sobre a imagem isso
        aconteceu com 1.529 syscalls numa sessao so; ignorar o par perdia
        escrita inteira em silencio, e quem mostrou foi o confronto com o
        `cmp` -- duas faixas mudavam no arquivo sem aparecer no trace.
        """
        evs = self.evs(
            f'_llseek({CAM}, 16488, [16488], SEEK_SET) = 0',
            f'write({CAM}, "\\377"... <unfinished ...>',
            '<... write resumed>) = 2048')
        self.assertEqual(evs, [("W", 16488, 2048)])

    def test_o_par_e_por_pid(self) -> None:
        # Duas threads com syscall aberta ao mesmo tempo e o caso normal; casar
        # o `resumed` errado poria a faixa noutra posicao.
        evs = list(A.eventos([
            linha(f'_llseek({CAM}, 100, [100], SEEK_SET) = 0', pid="11"),
            linha(f'read({CAM}, "x"... <unfinished ...>', pid="11"),
            linha('read(9<pipe:[1]>,  <unfinished ...>', pid="22"),
            linha('<... read resumed>"y", 64) = 64', pid="22"),
            linha('<... read resumed>"x"..., 512) = 512', pid="11"),
        ], IMG))
        self.assertEqual(evs, [("R", 100, 512)])

    def test_pread64_partido_traz_o_offset_na_retomada(self) -> None:
        evs = self.evs(f'pread64({CAM},  <unfinished ...>',
                       '<... pread64 resumed>"MZ"..., 96, 0) = 96')
        self.assertEqual(evs, [("R", 0, 96)])

    def test_seek_relativo_nao_vira_offset_absoluto(self) -> None:
        """`SEEK_CUR` tem argumento RELATIVO; o `[N]` e a posicao resultante.

        Ler o argumento como absoluto punha a faixa no offset 0 -- e offset 0
        e o cabecalho do setor 0, que passaria pelo corte de geometria como se
        fosse sondagem de formato.
        """
        evs = self.evs(f'_llseek({CAM}, 0, [405228], SEEK_CUR) = 0',
                       f'read({CAM}, "z"..., 8) = 8')
        self.assertEqual(evs, [("R", 405228, 8)])

    def test_faixas_vizinhas_se_unem(self) -> None:
        evs = [("R", 0, 10), ("R", 10, 10), ("R", 100, 5)]
        self.assertEqual(A.unir(evs, "R"), [(0, 20), (100, 105)])

    def test_unir_separa_leitura_de_escrita(self) -> None:
        evs = [("R", 0, 10), ("W", 0, 10)]
        self.assertEqual(A.unir(evs, "W"), [(0, 10)])

    def test_unir_faixas_junta_encostadas(self) -> None:
        """`(a,b)` e `(b+1,c)` sao uma faixa so.

        E o caso real: o `wte.exe` grava nome byte a byte, e a marca do
        roteiro corta a sequencia no meio.
        """
        self.assertEqual(A.unir_faixas([(3067404, 3067425), (3067426, 3067426)]),
                         [(3067404, 3067426)])
        self.assertEqual(A.unir_faixas([]), [])
        self.assertEqual(A.unir_faixas([(100, 110), (5, 7), (10, 20), (21, 25)]),
                         [(5, 7), (10, 25), (100, 110)])

    def test_unir_faixas_nao_junta_com_buraco(self) -> None:
        """Um byte de intervalo ainda separa -- senao a conferencia perdoaria
        escrita que o trace realmente nao viu."""
        self.assertEqual(A.unir_faixas([(10, 20), (22, 25)]),
                         [(10, 20), (22, 25)])


class TestConferirReguas(unittest.TestCase):
    """A conferencia das duas reguas, com faixa plantada.

    Ela e o que autoriza qualquer numero desta task: se o `cmp` mostra byte
    mudado que o trace nao viu escrever, o trace perdeu syscall e a atribuicao
    por acao nao vale nada.
    """

    def escreve(self, tmp, nome: str, cab: str, linhas: list[str]):
        p = tmp / nome
        p.write_text("\n".join([cab, *linhas]) + "\n", encoding="utf-8")
        return p

    def roda(self, escritas: list[str], mudou: list[str]) -> int:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            io = self.escreve(tmp, "io.tsv",
                              "imagem\tacao\top\tinicio\tfim\ttamanho", escritas)
            cmp_ = self.escreve(tmp, "cmp.tsv",
                                "inicio\tfim\ttamanho", mudou)
            return A.conferir_reguas(io, cmp_)

    def test_faixa_do_cmp_partida_em_duas_acoes_fecha(self) -> None:
        """O caso que produziu o falso alarme na medicao das seis areas."""
        self.assertEqual(
            self.roda(["i\tCALCULA_PRECO\tW\t3067404\t3067425\t22",
                       "i\tABRE_JOGADOR\tW\t3067426\t3067426\t1"],
                      ["3067404\t3067426\t23"]), 0)

    def test_faixa_do_cmp_sem_escrita_no_trace_reprova(self) -> None:
        self.assertEqual(
            self.roda(["i\tA\tW\t100\t199\t100"], ["500\t509\t10"]), 3)

    def test_buraco_no_meio_reprova(self) -> None:
        """Duas escritas com um byte de intervalo nao cobrem a faixa inteira."""
        self.assertEqual(
            self.roda(["i\tA\tW\t100\t109\t10", "i\tB\tW\t111\t120\t10"],
                      ["100\t120\t21"]), 3)


class TestEvidencia(unittest.TestCase):
    """Contra o `io-medido.tsv` commitado."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.medido = A.ler_medido()
        cls.faixas = [f for f in cls.medido if f["op"] in ("R", "W")]
        cls.conteudo = A.ler_conteudo()

    def test_tem_evidencia(self) -> None:
        self.assertTrue(self.faixas, "io-medido.tsv sem faixa nenhuma")

    def test_o_controle_esta_registrado(self) -> None:
        """O diff de controle vem primeiro, e sem ele nada significa nada.

        `ARRANQUE` e a acao que abre a imagem sem tocar em nada. Se ela sumir
        do TSV, toda faixa das outras acoes passa a incluir ruido de fundo sem
        que ninguem note.
        """
        arranque = [f for f in self.faixas if f["acao"] == "ARRANQUE"]
        self.assertTrue(arranque)
        self.assertTrue([f for f in arranque if f["op"] == "W"],
                        "o wte.exe grava na carga; zero escrita aqui significa "
                        "que a medicao perdeu syscall")

    def test_acao_exercitada_sem_io_fica_registrada(self) -> None:
        # "Nao gravou" e resultado. Sem a linha `.`, ele seria indistinguivel
        # de "nao foi exercitada".
        self.assertTrue([f for f in self.medido if f["op"] == "."])

    def test_toda_faixa_cai_na_regiao_de_dados_do_setor(self) -> None:
        """Mesmo corte da WTE-TASK-06, agora sobre syscall real.

        Offset de imagem MODE2/2352 mora entre os bytes 24 e 2071 de um setor.
        Uma faixa fora disso significa que o parser somou errado.

        Uma excecao, e ela e real: a leitura de 23 bytes no offset 0. Aquilo
        nao e dado -- e o sync mais o cabecalho do setor 0, que o editor le
        para reconhecer o formato. Cabecalho de setor fica, por definicao,
        FORA da regiao de dados.
        """
        for f in self.faixas:
            if int(f["inicio"]) == 0:
                self.assertEqual(int(f["tamanho"]), 23,
                                 "a leitura no offset 0 e a sondagem do "
                                 "cabecalho do setor 0; outro tamanho ali "
                                 "quer dizer outra coisa")
                continue
            resto = int(f["inicio"]) % A.SETOR
            self.assertTrue(A.DADOS_INI <= resto < A.DADOS_FIM,
                            f"{f['acao']} {f['inicio']}: byte {resto}")

    def test_a_execucao_confirma_offsets_que_o_estatico_ja_confirmava(self) -> None:
        """Sanidade cruzada: as duas réguas têm de concordar onde se cruzam.

        Um `OFS_*` que o `.exe` traz literal e que a execução também endereça é
        o caso fácil; se nenhum deles aparecesse, o casamento estaria quebrado.
        """
        conhecidos = A.ler_offsets_hpp()
        tocado = A.casar(self.faixas, conhecidos)
        self.assertIn("OFS_TEAM_NAME_1", tocado)
        self.assertIn("OFS_TEAM_NAME_KANJI", tocado)

    def test_o_corte_de_150_setores_nao_muda_o_mapa(self) -> None:
        """A refutação da hipótese do tamanho, presa em teste.

        Truncar a cópia para os 474.431.328 bytes exatos que o editor pede faz
        o aviso sumir e **não** muda uma faixa sequer. Se um dia mudar, ou a
        medição foi refeita com outro roteiro, ou a hipótese volta a estar em
        aberto -- e o `offsets-novos.md` afirma o contrário.
        """
        imagens = []
        for r in self.medido:
            if r["imagem"] not in imagens:
                imagens.append(r["imagem"])
        if len(imagens) < 2:
            self.skipTest("só uma sessão no io-medido.tsv")
        def mapa(img):
            return [tuple(r[c] for c in ("acao", "op", "inicio", "fim"))
                    for r in self.medido if r["imagem"] == img]
        self.assertEqual(mapa(imagens[0]), mapa(imagens[1]))

    def test_ha_faixa_fora_do_que_o_newWe2002_conhece(self) -> None:
        """O achado que a task existe para produzir.

        Se isto virar vazio, ou a sessão deixou de exercitar a tela, ou alguém
        acrescentou o offset ao `Offsets.hpp` sem reconferir o limite das duas
        tabelas -- que é exatamente o aviso escrito no `offsets.md`.
        """
        conhecidos = A.ler_offsets_hpp()
        teto = max(conhecidos.values())
        self.assertTrue([f for f in self.faixas if int(f["inicio"]) > teto])


    def test_a_faixa_do_travamento_esta_vazia_nesta_release(self) -> None:
        """A pista que sobrou depois de a hipótese do tamanho cair.

        A última leitura antes do `SIGSEGV` é em 14368636, e ali a imagem está
        praticamente zerada — enquanto toda outra faixa lida tem dado. **Não é
        a causa**: essa foi medida no `analisar_crash.py` e é um `TFont` nulo
        dentro do `vcl60.bpl`. É pista da causa da causa, e é nessa condição
        que o `offsets-novos.md` a apresenta; se ela parar de valer, aquele
        texto perde o fundamento.
        """
        if not self.conteudo:
            self.skipTest("io-conteudo.tsv ausente")
        alvo = self.conteudo.get(14368636)
        self.assertIsNotNone(alvo, "a faixa do travamento sumiu da amostra")
        outras = [int(c["nao_zero"]) for o, c in self.conteudo.items()
                  if o != 14368636 and int(c["bytes_amostrados"]) >= 64]
        self.assertLess(int(alvo["nao_zero"]), min(outras))


if __name__ == "__main__":
    unittest.main()
