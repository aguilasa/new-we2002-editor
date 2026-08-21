#!/usr/bin/env python3
"""Testes do dump_render2d.py -- WTE-TASK-29.

Tres grupos, e o do meio e a razao de o arquivo existir:

1. **O que se le do `.exe` bate com o que o markdown afirma.** Cada assinatura
   da tabela `ASSINATURAS` e um padrao de instrucao; se algum deixar de
   aparecer, o gerador tem de recusar em vez de emitir prosa que caducou.
2. **As recusas foram VISTAS.** Guard que nunca foi visto recusar e guard que
   se supoe funcionar -- a mesma politica do `test_dump_mcr.py`. Aqui a
   plantacao e no proprio blob em memoria, porque o `.exe` e leitura pura e
   nao se edita nem em teste.
3. **A aritmetica que o markdown descreve, executada.** O documento afirma como
   o gradiente e o escurecer se comportam; o teste reimplementa as duas contas
   em Python e prova o que elas produzem -- inclusive o caso em que truncar e
   arredondar DIVERGEM, que e o risco nomeado da §9 do plano.
"""

from __future__ import annotations

import math
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

import dump_render2d as R


def f32(x: float) -> float:
    """O mesmo valor, depois de passar por um `Single`.

    O gradiente do original guarda passo e acumulador com `fstp DWORD PTR`, que
    e precisao simples. O `float` do Python e duplo, entao emular exige o
    ida-e-volta -- sem ele a referencia Python e o Pascal divergiriam por um
    motivo que nao existe no binario.
    """
    return struct.unpack("<f", struct.pack("<f", x))[0]


def rampa_referencia(inicio: int, fim: int, distancia: int) -> list[int]:
    """A rampa do `gradienteClick`, em Python, para confrontar com o Pascal.

    Duas implementacoes independentes da mesma conta. Se concordarem, o erro
    tem de estar nas duas -- e a mesma politica do confronto de `.mcr` da
    WTE-TASK-28.
    """
    def canais5(p: int) -> list[int]:
        return [(p >> (5 * c)) & 0x1F for c in range(3)]

    a, b = canais5(inicio), canais5(fim)
    passo = [f32(f32(b[c] - a[c]) / f32(distancia)) for c in range(3)]
    acumulado = [0.0, 0.0, 0.0]
    saida = []
    for _ in range(distancia - 1):
        for c in range(3):
            acumulado[c] = f32(acumulado[c] + passo[c])
        saida.append((inicio + math.trunc(acumulado[0])
                      + (math.trunc(acumulado[1]) << 5)
                      + (math.trunc(acumulado[2]) << 10)) & 0xFFFF)
    return saida


class TestAssinaturas(unittest.TestCase):
    """Cada afirmacao do markdown, contra o `.text`."""

    def setUp(self) -> None:
        if not R.EXE.is_file():
            self.skipTest(f"sem {R.REL_EXE} -- as assinaturas NAO foram "
                          "conferidas")
        self.blob = R.EXE.read_bytes()

    def test_todas_as_assinaturas_aparecem(self) -> None:
        provas = R.confere_assinaturas(self.blob)
        self.assertEqual(len(provas), len(R.ASSINATURAS))

    def test_a_expansao_e_deslocamento_e_o_teto_confirma(self) -> None:
        """`shl 3` e `cmp 0xf8` sao a mesma afirmacao, vista de dois lados.

        Se a expansao fosse `v * 255 / 31`, o teto do clarear seria `0xFF`. E
        `0xF8`, entao e deslocamento. Os dois padroes tem de coexistir.
        """
        decodifica = R.le_bytes(self.blob, R.VA_DECODIFICA, 0x9A)
        clarear = R.le_bytes(self.blob, R.VA_CLAREAR, 0x45)
        self.assertIn(bytes.fromhex("c02203"), decodifica)
        self.assertIn(bytes.fromhex("807d00f8"), clarear)
        self.assertEqual(31 << 3, 0xF8)

    def test_o_arredondador_trunca(self) -> None:
        """RC = `11` nos bits 10-11 do control word e *round toward zero*."""
        corpo = R.le_bytes(self.blob, R.VA_TRUNCA, 0x2C)
        self.assertIn(bytes.fromhex("814dfc010c0000"), corpo)
        # 0xc01 = 0b1100_0000_0001: PC em `11` (extendido) e RC em `11`.
        self.assertEqual((0xC01 >> 10) & 0b11, 0b11)

    def test_os_tres_passos_sao_os_tres_campos(self) -> None:
        """`1`, `0x20` e `0x400` sao um degrau em cada campo de 5 bits."""
        self.assertEqual(1, 1 << 0)
        self.assertEqual(0x20, 1 << 5)
        self.assertEqual(0x400, 1 << 10)

    def test_o_exportador_pula_o_resto_do_setor(self) -> None:
        self.assertEqual(R.SETOR_PAYLOAD + R.SETOR_RESTO, R.SETOR_BYTES)


class TestRecusa(unittest.TestCase):
    """As recusas, vistas. O `.exe` nao se edita -- planta-se no blob."""

    def setUp(self) -> None:
        if not R.EXE.is_file():
            self.skipTest(f"sem {R.REL_EXE}")
        self.blob = R.EXE.read_bytes()

    def _planta(self, va: int, quantos: int) -> bytes:
        """Zera `quantos` bytes a partir de `va`, no blob em memoria."""
        for sec_va, tam, roff in R.secoes(self.blob):
            ini = 0x00400000 + sec_va
            if ini <= va < ini + tam:
                pos = roff + (va - ini)
                return (self.blob[:pos] + bytes(quantos)
                        + self.blob[pos + quantos:])
        raise AssertionError(f"{va:#x} fora de toda secao")

    def test_assinatura_apagada_recusa(self) -> None:
        plantado = self._planta(R.VA_TRUNCA, 0x2C)
        with self.assertRaises(R.RenderError) as ctx:
            R.confere_assinaturas(plantado)
        self.assertIn(f"{R.VA_TRUNCA:#010x}", str(ctx.exception))

    def test_desenhista_alterado_recusa(self) -> None:
        plantado = self._planta(R.VA_UNIFORME, 0x40A)
        with self.assertRaises(R.RenderError) as ctx:
            R.confere_desenhistas(plantado)
        self.assertIn(f"{R.VA_UNIFORME:#010x}", str(ctx.exception))

    def test_va_fora_de_secao_recusa(self) -> None:
        with self.assertRaises(R.RenderError):
            R.le_bytes(self.blob, 0x7FFFFFFF, 4)


class TestDesenhistas(unittest.TestCase):
    """A assimetria entre bandeira e uniforme -- o achado desta passagem."""

    def setUp(self) -> None:
        if not R.EXE.is_file():
            self.skipTest(f"sem {R.REL_EXE}")
        self.blob = R.EXE.read_bytes()

    def test_bandeira_e_uniforme_nao_reescrevem_o_mesmo_tanto(self) -> None:
        achados = {papel: (entradas, arquivos)
                   for _, papel, entradas, arquivos
                   in R.confere_desenhistas(self.blob)}
        self.assertEqual(achados["bandeira do titular"], (16, 1))
        self.assertEqual(achados["camisa e calcao"], (15, 2))

    def test_o_seek_cai_no_fim_do_cabecalho(self) -> None:
        """`0x36` so e a primeira entrada de paleta se o cabecalho tiver 54."""
        self.assertEqual(R.BMP_CABECALHO, 0x36)


class TestBitmaps(unittest.TestCase):
    def setUp(self) -> None:
        if not R.IMAGEM.is_dir():
            self.skipTest("sem we-team-editor/image -- os bitmaps NAO foram "
                          "contados")
        self.contas = R.bitmaps()

    def test_nenhum_bitmap_foge_de_oito_bpp(self) -> None:
        # Um so de 24 bpp quebraria o `0x36` -- o cabecalho teria outro
        # tamanho e o seek cairia no meio do pixel.
        self.assertEqual(self.contas["fora"], 0)

    def test_as_familias_do_render_estao_todas_la(self) -> None:
        for chave in ("bandeiras", "camisas", "calcoes"):
            self.assertGreater(self.contas[chave], 0, chave)


class TestAritmetica(unittest.TestCase):
    """A conta que o markdown descreve, executada.

    Nao le o `.exe`: prova que a DESCRICAO e coerente e que a forma errada de
    escreve-la produz outro resultado. Sem isto, "trunca em vez de arredondar"
    seria uma frase.
    """

    @staticmethod
    def expande(v5: int) -> int:
        return v5 << 3

    @staticmethod
    def decodifica(palavra: int) -> tuple[int, int, int]:
        return ((palavra >> 0) & 0x1F, (palavra >> 5) & 0x1F,
                (palavra >> 10) & 0x1F)

    def escurece(self, palavra: int) -> int:
        r, g, b = (self.expande(c) for c in self.decodifica(palavra))
        if r > 0:
            palavra -= 1
        if g > 0:
            palavra -= 0x20
        if b > 0:
            palavra -= 0x400
        return palavra

    def clareia(self, palavra: int) -> int:
        r, g, b = (self.expande(c) for c in self.decodifica(palavra))
        if r < 0xF8:
            palavra += 1
        if g < 0xF8:
            palavra += 0x20
        if b < 0xF8:
            palavra += 0x400
        return palavra

    def test_um_degrau_mexe_num_campo_de_cada_vez(self) -> None:
        palavra = (10 << 10) | (20 << 5) | 30
        self.assertEqual(self.decodifica(self.escurece(palavra)), (29, 19, 9))
        self.assertEqual(self.decodifica(self.clareia(palavra)), (31, 21, 11))

    def test_o_piso_segura_e_nao_da_a_volta(self) -> None:
        """Sem a guarda, `0 - 1` viraria `31` no campo vizinho."""
        self.assertEqual(self.escurece(0), 0)
        self.assertEqual(self.decodifica(self.escurece(1 << 5)), (0, 0, 0))

    def test_o_teto_satura_em_trinta_e_um(self) -> None:
        cheio = (31 << 10) | (31 << 5) | 31
        self.assertEqual(self.clareia(cheio), cheio)

    @staticmethod
    def rampa(inicio: tuple[int, int, int], fim: tuple[int, int, int],
              n: int, arredonda) -> list[int]:
        """A rampa do `gradienteClick`, com o conversor recebido de fora.

        A soma e sobre a PALAVRA de partida, e nao canal a canal -- e assim que
        o original faz, e a diferenca aparece quando o conversor muda.
        """
        palavra_inicial = inicio[0] | (inicio[1] << 5) | (inicio[2] << 10)
        passo = [(fim[c] - inicio[c]) / n for c in range(3)]
        acumulado = [0.0, 0.0, 0.0]
        saida = []
        for _ in range(n):
            for c in range(3):
                acumulado[c] += passo[c]
            saida.append(palavra_inicial + arredonda(acumulado[0])
                         + (arredonda(acumulado[1]) << 5)
                         + (arredonda(acumulado[2]) << 10))
        return saida

    def test_truncar_e_arredondar_divergem_na_rampa(self) -> None:
        """O risco nomeado da §9, executado.

        Se as duas formas dessem sempre o mesmo, a escolha nao importaria e o
        plano teria errado ao chamar isso de risco. Elas divergem.
        """
        truncada = self.rampa((0, 0, 0), (7, 0, 0), 5, math.trunc)
        arredondada = self.rampa((0, 0, 0), (7, 0, 0), 5,
                                 lambda x: int(x + 0.5))
        self.assertNotEqual(truncada, arredondada)
        # E a divergencia e de um degrau, exatamente o que o plano previu.
        for a, b in zip(truncada, arredondada):
            self.assertLessEqual(abs(a - b), 1)

    def test_a_rampa_chega_na_ponta(self) -> None:
        n = 8
        rampa = self.rampa((0, 0, 0), (24, 0, 0), n, math.trunc)
        self.assertEqual(rampa[-1] & 0x1F, 24)


class TestGuardDoPascal(unittest.TestCase):
    """O `we2002_render.pas` e escrito a mao; este e o guard dele."""

    def setUp(self) -> None:
        if not R.EXE.is_file() or not R.PASCAL.is_file():
            self.skipTest(f"sem {R.REL_EXE} ou {R.REL_PASCAL}")
        self.blob = R.EXE.read_bytes()
        self.original = R.PASCAL.read_text(encoding="utf-8")

    def test_os_imediatos_saem_do_exe(self) -> None:
        do_exe = R.imediatos_do_exe(self.blob)
        self.assertEqual(do_exe["RENDER_EXPANSAO"], 3)
        self.assertEqual(do_exe["RENDER_MAXIMO"], 0xF8)
        self.assertEqual(do_exe["RENDER_PASSO_G"], 0x20)
        self.assertEqual(do_exe["RENDER_PASSO_B"], 0x400)
        self.assertEqual(do_exe["PALETA_BANDEIRA"], 16)
        self.assertEqual(do_exe["PALETA_UNIFORME"], 15)

    def test_o_pascal_bate(self) -> None:
        R.confere_pascal(R.imediatos_do_exe(self.blob))
        R.confere_seek_da_paleta(self.blob,
                                 R.constantes_do_pascal()["BMP_CABECALHO"])

    def test_constante_plantada_recusa(self) -> None:
        try:
            R.PASCAL.write_text(
                self.original.replace("  RENDER_EXPANSAO = 3;",
                                      "  RENDER_EXPANSAO = 4;"),
                encoding="utf-8")
            with self.assertRaises(R.RenderError) as ctx:
                R.confere_pascal(R.imediatos_do_exe(self.blob))
            self.assertIn("RENDER_EXPANSAO", str(ctx.exception))
        finally:
            R.PASCAL.write_text(self.original, encoding="utf-8")

    def test_round_no_lugar_de_trunc_recusa(self) -> None:
        """O risco nomeado, guardado por grep -- e barato."""
        try:
            R.PASCAL.write_text(
                self.original.replace("Trunc(acumulado[0])",
                                      "Round(acumulado[0])"),
                encoding="utf-8")
            with self.assertRaises(R.RenderError) as ctx:
                R.confere_pascal(R.imediatos_do_exe(self.blob))
            self.assertIn("TRUNCA", str(ctx.exception))
        finally:
            R.PASCAL.write_text(self.original, encoding="utf-8")

    def test_seek_de_paleta_errado_recusa(self) -> None:
        with self.assertRaises(R.RenderError) as ctx:
            R.confere_seek_da_paleta(self.blob, 0x40)
        self.assertIn("push", str(ctx.exception))


class TestPascalConcorda(unittest.TestCase):
    """O `we2002_render` compila, e a rampa dele bate com a do Python."""

    PROGRAMA = R.ROOT / "wte" / "tests" / "test_render.pas"
    FONTES = R.ROOT / "wte" / "src"

    def _roda(self, ambiente: dict) -> str:
        fpc = shutil.which("fpc")
        if not fpc:
            self.skipTest("sem fpc -- o we2002_render NAO foi compilado nesta "
                          "execucao")
        with tempfile.TemporaryDirectory() as td:
            binario = Path(td) / "test_render"
            r = subprocess.run(
                [fpc, f"-Fu{self.FONTES}", f"-FU{td}", f"-o{binario}",
                 str(self.PROGRAMA)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            env = dict(os.environ)
            env.update(ambiente)
            r = subprocess.run([str(binario)], capture_output=True, text=True,
                               env=env)
        self.assertEqual([ln for ln in r.stdout.splitlines()
                          if ln.startswith("FALHA")], [], r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def test_os_invariantes_sem_confronto(self) -> None:
        saida = self._roda({"WTE_TEST_RENDER_RAMPA": ""})
        self.assertIn("PULADO\trampa contra o Python", saida)
        # Numero medido: caso que sumir do programa Pascal sumiria em silencio
        # e o teste seguiria verde.
        self.assertIn("CASOS\t31", saida)

    def test_a_rampa_bate_com_a_do_python(self) -> None:
        """A terceira ponta, e ela precisa de um caso onde truncar MORDE.

        Uma rampa que divida certinho nao distingue `Trunc` de `Round`, e o
        confronto passaria com o port errado.
        """
        inicio, fim, distancia = 0, 7, 5
        esperado = rampa_referencia(inicio, fim, distancia)
        arredondada = [(inicio + round(f32((i + 1) * f32(7 / 5)))) & 0xFFFF
                       for i in range(distancia - 1)]
        self.assertNotEqual(esperado, arredondada,
                            "o caso escolhido nao distingue truncar de "
                            "arredondar -- troque os numeros")
        saida = self._roda({
            "WTE_TEST_RENDER_INICIO": str(inicio),
            "WTE_TEST_RENDER_FIM": str(fim),
            "WTE_TEST_RENDER_DISTANCIA": str(distancia),
            "WTE_TEST_RENDER_RAMPA": ",".join(str(v) for v in esperado),
        })
        self.assertIn("OK\ta rampa bate com a do dump_render2d.py", saida)

    def test_a_rampa_de_um_canal_cheio_tambem_bate(self) -> None:
        inicio = 0
        fim = 31 << 10          # so o canal B
        distancia = 9
        esperado = rampa_referencia(inicio, fim, distancia)
        saida = self._roda({
            "WTE_TEST_RENDER_INICIO": str(inicio),
            "WTE_TEST_RENDER_FIM": str(fim),
            "WTE_TEST_RENDER_DISTANCIA": str(distancia),
            "WTE_TEST_RENDER_RAMPA": ",".join(str(v) for v in esperado),
        })
        self.assertIn("OK\ta rampa bate com a do dump_render2d.py", saida)


if __name__ == "__main__":
    unittest.main()
