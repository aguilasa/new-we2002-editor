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

import unittest

import analisar_io as A

IMG = "dd-run.bin"
CAM = f"16</home/x/work/{IMG}>"


def linha(s: str) -> str:
    return "1234 " + s


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

    def test_faixas_vizinhas_se_unem(self) -> None:
        evs = [("R", 0, 10), ("R", 10, 10), ("R", 100, 5)]
        self.assertEqual(A.unir(evs, "R"), [(0, 20), (100, 105)])

    def test_unir_separa_leitura_de_escrita(self) -> None:
        evs = [("R", 0, 10), ("W", 0, 10)]
        self.assertEqual(A.unir(evs, "W"), [(0, 10)])


class TestEvidencia(unittest.TestCase):
    """Contra o `io-medido.tsv` commitado."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.medido = A.ler_medido()
        cls.faixas = [f for f in cls.medido if f["op"] in ("R", "W")]

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

    def test_ha_faixa_fora_do_que_o_newWe2002_conhece(self) -> None:
        """O achado que a task existe para produzir.

        Se isto virar vazio, ou a sessão deixou de exercitar a tela, ou alguém
        acrescentou o offset ao `Offsets.hpp` sem reconferir o limite das duas
        tabelas -- que é exatamente o aviso escrito no `offsets.md`.
        """
        conhecidos = A.ler_offsets_hpp()
        teto = max(conhecidos.values())
        self.assertTrue([f for f in self.faixas if int(f["inicio"]) > teto])


if __name__ == "__main__":
    unittest.main()
