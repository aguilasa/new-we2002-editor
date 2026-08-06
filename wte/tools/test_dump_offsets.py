#!/usr/bin/env python3
"""Testes do `dump_offsets.py` -- o critério de limite da tabela em `.data`.

    python3 -m unittest discover wte/tools -p 'test_*.py'
    make -C wte test

Por que este arquivo existe
---------------------------

O limite da tabela de offsets do Obocaman e medido por dois criterios
independentes -- conteudo e quem referencia --, e o tratamento da discordancia
entre eles **e assimetrico**: um sentido aborta, o outro avisa. Hoje as duas
tabelas concordam, entao nenhum dos dois caminhos e exercitado por rodar o
gerador sobre o `.exe`: `--check` verde nao diz nada sobre eles.

E sao eles que sustentam a armadilha §8.7 do plano. Uma tabela medida a mais
publica como offset um slot que ninguem referencia; e a assimetria e
justamente o tipo de regra que uma refatoracao "simplifica" sem querer.

O segundo alvo e a **acoplagem** entre este projeto e o `newWe2002`: a faixa de
plausibilidade e o `[min, max]` dos valores do nosso `Offsets.hpp`, e a
WTE-TASK-19 vai acrescentar valores la. Um valor fora da faixa atual alarga a
janela e move o limite medido da tabela do Obocaman. Aqui isso fica fixado como
propriedade, nao como observacao de quem leu o codigo uma vez.

A bateria padrao **nao abre o `.exe`** -- monta as estruturas em memoria. A
medida real das duas tabelas fica sob `skipUnless`, como no
`test_dump_strings.py`. Ver `wte/tools/README.md`.

Isto NAO e um gerador: nao aceita `--check`, e o Makefile filtra
`tools/test_*.py` de `GENERATORS`.
"""

from __future__ import annotations

import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dump_offsets as d  # noqa: E402


class FakeMeasurement:
    """O mínimo que `check_table_bounds()` toca.

    Chamar o método desligado da classe (`d.Measurement.check_table_bounds`)
    evita montar a medição inteira — que precisaria do `.exe`. O que está sob
    teste é a regra de confronto, e ela só lê `tables` e `data_refs`.
    """

    def __init__(self, tables, data_refs):
        self.tables = tables
        self.data_refs = data_refs

    def run(self) -> str:
        """Roda o confronto e devolve o que foi para a saída padrão."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            d.Measurement.check_table_bounds(self)
        return buf.getvalue()


def table(va: int, slots: int, referenced: int = 1) -> d.Run:
    return d.Run(va, va + 4 * slots, [1] * slots, referenced)


class TestLimiteDaTabela(unittest.TestCase):
    """Os dois sentidos da discordância, que o `.exe` não exercita."""

    def test_criterios_concordam_nao_diz_nada(self):
        t = table(0x00423000, 4)                      # termina em 0x423010
        m = FakeMeasurement([t], {0x00423010})
        self.assertEqual(m.run(), "")
        self.assertEqual(m.bounds, [(t, 0x00423010, True)])

    def test_referencia_antes_do_fim_aborta(self):
        # A armadilha §8.7: o conteúdo estica a tabela além do que o código
        # sustenta. Publicar isso daria como offset um slot que ninguém aponta.
        t = table(0x00423000, 8)                      # termina em 0x423020
        m = FakeMeasurement([t], {0x00423010})
        with self.assertRaises(d.DumpError) as ctx:
            m.run()
        msg = str(ctx.exception)
        self.assertIn("0x423000", msg)
        self.assertIn("vai ate 0x423020 pelo conteudo", msg)
        self.assertIn("referencia 0x423010 antes disso", msg)
        self.assertIn("8.7", msg)

    def test_referencia_depois_do_fim_avisa_e_segue(self):
        # Aqui não há número errado a emitir: o intervalo publicado continua
        # sendo o do conteúdo. O que há é um vizinho que talvez pertença à
        # tabela, e ele não pode sumir dentro de `self.bounds`.
        t = table(0x00423000, 4)                      # termina em 0x423010
        m = FakeMeasurement([t], {0x00423018})
        saida = m.run()
        self.assertIn("AVISO:", saida)
        self.assertIn("0x423010", saida)
        self.assertIn("0x423018", saida)
        self.assertIn("8 bytes adiante", saida)
        self.assertEqual(m.bounds, [(t, 0x00423018, False)])

    def test_sem_referencia_alguma_depois_nao_aborta(self):
        t = table(0x00423000, 4)
        m = FakeMeasurement([t], set())
        self.assertEqual(m.run(), "")
        self.assertEqual(m.bounds, [(t, None, False)])

    def test_referencia_a_base_nao_conta_como_proxima(self):
        # `after` filtra por `> table.va`: a referência à própria base é o que
        # torna a corrida uma tabela, e contá-la abortaria toda vez.
        t = table(0x00423000, 4)
        m = FakeMeasurement([t], {0x00423000, 0x00423010})
        self.assertEqual(m.run(), "")
        self.assertTrue(m.bounds[0][2])

    def test_duas_tabelas_a_segunda_ainda_e_conferida(self):
        boa = table(0x00423000, 4)                    # termina em 0x423010
        ma = table(0x00424000, 8)                     # termina em 0x424020
        m = FakeMeasurement([boa, ma], {0x00423010, 0x00424010})
        with self.assertRaises(d.DumpError) as ctx:
            m.run()
        self.assertIn("0x424000", str(ctx.exception))


class TestFaixaDePlausibilidade(unittest.TestCase):
    """A acoplagem com o `Offsets.hpp` do `newWe2002`, como propriedade."""

    def test_a_faixa_e_o_min_max_dos_valores_declarados(self):
        p = d.Plausible([1000, 5000, 200])
        self.assertEqual((p.lo, p.hi), (200, 5000))

    def test_valor_novo_fora_da_faixa_alarga_a_janela(self):
        # É isto que a WTE-TASK-19 vai fazer ao acrescentar offsets, e é por
        # isso que quem acrescentar tem de reconferir o limite das tabelas: a
        # janela que decide onde a corrida para acabou de mudar.
        base = [1_000_000, 2_000_000]
        antes = d.Plausible(base)
        depois = d.Plausible(base + [9_000_000])
        self.assertEqual(antes.hi, 2_000_000)
        self.assertEqual(depois.hi, 9_000_000)
        self.assertGreater(depois.hi, antes.hi)

    def test_a_guarda_de_100_por_cento_e_tautologica_na_faixa(self):
        # Nenhum valor da lista pode reprovar *por faixa* no filtro construído
        # a partir dela — é a mesma lista dos dois lados. A guarda de
        # `Measurement.__init__` morde nos cortes 2 e 3, não neste.
        for valores in ([1, 2, 3], [7], [10**9, 1]):
            p = d.Plausible(valores)
            for v in valores:
                with self.subTest(valores=valores, v=v):
                    self.assertTrue(p.lo <= v <= p.hi)

    def test_fora_da_faixa_reprova(self):
        p = d.Plausible([1000, 2000])
        self.assertFalse(p(999))
        self.assertFalse(p(2001))

    def test_geometria_de_setor_reprova_dentro_da_faixa(self):
        # O corte que **não** vem do Offsets.hpp: um valor dentro da faixa mas
        # que cai no cabeçalho ou no ECC de um setor MODE2/2352 não é offset.
        p = d.Plausible([0, 10 * d.SECTOR_SIZE])
        self.assertFalse(p(d.SECTOR_SIZE * 3))                 # resto 0
        self.assertFalse(p(d.SECTOR_SIZE * 3 + d.SECTOR_DATA_BEGIN - 1))
        self.assertFalse(p(d.SECTOR_SIZE * 3 + d.SECTOR_DATA_END))


REAL = d.EXE.is_file() and d.HPP.is_file()


@unittest.skipUnless(REAL, "precisa do we-team-editor.exe e do Offsets.hpp")
class TestMedidaReal(unittest.TestCase):
    """A medida publicada, para que o teste falhe se ela mudar sem aviso."""

    @classmethod
    def setUpClass(cls):
        img = d.Image(d.EXE.read_bytes())
        declared = d.read_offsets_hpp(d.HPP.read_text(encoding="utf-8"))
        cls.m = d.Measurement(img, declared)

    def test_as_duas_tabelas_concordam_nos_dois_criterios(self):
        medido = [(f"0x{t.va:x}", f"0x{t.end_va:x}",
                   f"0x{nxt:x}" if nxt else None, ok)
                  for t, nxt, ok in self.m.bounds]
        self.assertEqual(medido, [
            ("0x4231a0", "0x4231e8", "0x4231e8", True),
            ("0x423634", "0x423648", "0x423648", True),
        ])

    def test_o_vizinho_de_baixo_e_lmno(self):
        # A evidência da §8.7, do lado certo: 16 bytes abaixo da tabela 1.
        off = self.m.img.va_to_offset(0x00423190)
        self.assertEqual(self.m.img.data[off:off + 4], b"lmno")
        self.assertFalse(self.m.plausible(
            int.from_bytes(b"lmno", "little")))

    def test_a_faixa_sai_do_offsets_hpp(self):
        valores = [v for _n, v in self.m.declared]
        self.assertEqual(self.m.plausible.lo, min(valores))
        self.assertEqual(self.m.plausible.hi, max(valores))


if __name__ == "__main__":
    unittest.main()
