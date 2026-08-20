#!/usr/bin/env python3
"""Testes do conta_ml.py -- WTE-TASK-33.

Quatro grupos:

1. **A tabela fecha.** A soma dos 120 tem de dar o `PLAYERS_NC` do
   `we2002_core`, e o prefixo do `wte.exe` tem de bater com o `START_LINK[]`
   do `ed.exe` em todo time que tenha algum NC.
2. **Os guards recusam com entrada plantada.** Guard que nunca foi visto
   recusar e guard que se supoe funcionar -- e a regra da WTE-TASK-17.
3. **A conta sobre imagem sintetica.** O par de enchimento, o corte por
   `b1 < 23` e a repeticao do mesmo bloco, cada um plantado e conferido em
   separado. Sem isso, os tres so seriam exercitados por ROM de 300 MB.
4. **O Pascal concorda com o Python.** O `fpc` compila o `we2002_ml` e roda o
   `wte/tests/test_ml.pas`; havendo copia de imagem em `work/`, os dois contam
   a MESMA copia e o numero tem de ser o mesmo. Sem `fpc` o grupo PULA e diz
   que nada foi medido.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import conta_ml as C


def imagem_sintetica(pares: list[tuple[int, int]]) -> bytearray:
    """Uma imagem so com a regiao de vinculo preenchida, ja com o salto.

    Escreve `pares` a partir de `OFS_LINK_ML` respeitando a fronteira de
    setor, que e como o original os leria. O resto e zero -- e zero e
    `b1 = 0 < 23`, ou seja vinculo, que a conta ignora.
    """
    tam = C.OFS_LINK_ML + C.PARES * 2 + 2 * C.SETOR
    img = bytearray(tam)
    pos = C.OFS_LINK_ML
    for b0, b1 in pares:
        if pos % C.SETOR == C.DADOS_INICIO + C.DADOS:
            pos += C.SETOR - C.DADOS
        img[pos] = b0
        img[pos + 1] = b1
        pos += 2
    return img


class TestTabela(unittest.TestCase):
    def setUp(self) -> None:
        if not C.EXE.is_file():
            self.skipTest(f"sem {C.REL_EXE} -- a tabela NAO foi conferida")
        blob = C.EXE.read_bytes()
        self.contagem = C.le_dwords(blob, C.VA_CONTAGEM, C.TIMES)
        self.pref = C.prefixos(self.contagem)
        self.core = C.start_link_do_core()

    def test_soma_e_o_players_nc(self) -> None:
        self.assertEqual(sum(self.contagem), C.TOTAL)

    def test_os_dois_oraculos_concordam_onde_a_tabela_existe(self) -> None:
        ruins = [t for t in range(C.TIMES)
                 if self.contagem[t] and self.pref[t] != self.core[t]]
        self.assertEqual(ruins, [])

    def test_onde_divergem_e_sempre_time_sem_nc(self) -> None:
        for t in range(C.TIMES):
            if self.pref[t] != self.core[t]:
                self.assertEqual(self.contagem[t], 0, f"time {t}")

    def test_o_contador_mora_no_indice_seguinte_ao_ultimo_bloco(self) -> None:
        # 0x004335c0 e exatamente 0x00433224 + 2*462. E o que faz o estouro
        # atingir o proprio contador antes de qualquer outra coisa.
        self.assertEqual(C.VA_OCUPACAO + 2 * C.TOTAL, C.VA_CONTADOR)


class TestGuards(unittest.TestCase):
    """Entrada plantada: cada recusa tem de aparecer."""

    def test_tabela_que_nao_soma_recusa(self) -> None:
        contagem = [0] * C.TIMES
        contagem[0] = C.TOTAL - 1
        with self.assertRaises(C.ContaError) as ctx:
            C.confere(contagem, C.prefixos(contagem), [0] * C.TIMES)
        self.assertIn("soma", str(ctx.exception))

    def test_divergencia_com_o_core_recusa(self) -> None:
        # O time 1 TEM um NC, entao o prefixo dele e dado definido: os dois
        # oraculos discordarem ali e erro, nao lacuna.
        contagem = [0] * C.TIMES
        contagem[0] = C.TOTAL - 1
        contagem[1] = 1
        core = C.prefixos(contagem)
        core[1] = 999
        with self.assertRaises(C.ContaError) as ctx:
            C.confere(contagem, C.prefixos(contagem), core)
        self.assertIn("divergem", str(ctx.exception))

    def test_divergencia_em_time_sem_nc_nao_recusa(self) -> None:
        contagem = [0] * C.TIMES
        contagem[0] = C.TOTAL
        core = C.prefixos(contagem)
        core[5] = 0                        # contagem[5] == 0: nao e erro
        C.confere(contagem, C.prefixos(contagem), core)


class TestConta(unittest.TestCase):
    """A rotina sobre imagem plantada -- cada regra em separado."""

    def setUp(self) -> None:
        if not C.EXE.is_file():
            self.skipTest(f"sem {C.REL_EXE} -- a conta NAO foi conferida")
        self.pref = C.prefixos(C.le_dwords(C.EXE.read_bytes(),
                                           C.VA_CONTAGEM, C.TIMES))

    def test_imagem_toda_de_vinculo_nao_gasta_bloco(self) -> None:
        # b1 = 0 < 23 em todo par: nenhum bloco proprio.
        r = C.conta(imagem_sintetica([]), self.pref)
        self.assertEqual(r["livres"], C.TOTAL)
        self.assertEqual(r["proprios"], 0)

    def test_um_bloco_proprio_gasta_um(self) -> None:
        pares = [(0, 0)] * C.PARES
        pares[0] = (0, 23)                 # time 0, primeiro NC -> indice 0
        r = C.conta(imagem_sintetica(pares), self.pref)
        self.assertEqual(r["proprios"], 1)
        self.assertEqual(r["livres"], C.TOTAL - 1)

    def test_o_mesmo_bloco_duas_vezes_gasta_um_so(self) -> None:
        pares = [(0, 0)] * C.PARES
        pares[0] = (0, 23)
        pares[1] = (0, 23)
        r = C.conta(imagem_sintetica(pares), self.pref)
        self.assertEqual(r["proprios"], 2)
        self.assertEqual(r["distintos"], 1)
        self.assertEqual(r["livres"], C.TOTAL - 1)

    def test_o_par_de_enchimento_e_ignorado(self) -> None:
        pares = [(0, 0)] * C.PARES
        pares[C.PAR_FILLER] = (0, 23)      # so ele, e no lugar do enchimento
        r = C.conta(imagem_sintetica(pares), self.pref)
        self.assertEqual(r["proprios"], 0, "o par 23 nao pode contar")
        self.assertEqual(r["livres"], C.TOTAL)

    def test_indice_alem_do_vetor_e_reportado(self) -> None:
        # Time 20 nao tem NC nenhum: o prefixo dele e alto e `b1` grande passa
        # de 461. E o caso da ROM europeia, e a causa do 0x004335e4.
        pares = [(0, 0)] * C.PARES
        pares[0] = (20, 189)
        r = C.conta(imagem_sintetica(pares), self.pref)
        self.assertEqual(list(r["fora"]), [480])
        self.assertEqual(C.VA_OCUPACAO + 2 * 480, 0x004335E4)

    def test_time_alem_da_tabela_nao_e_modelado(self) -> None:
        pares = [(0, 0)] * C.PARES
        pares[0] = (200, 30)
        r = C.conta(imagem_sintetica(pares), self.pref)
        self.assertEqual(len(r["nao_modelado"]), 1)
        self.assertEqual(r["livres"], C.TOTAL)

    def test_o_maior_b0_e_medido_e_nao_afirmado(self) -> None:
        # A coluna `max_b0` do ml-slots-medido.tsv, que e o que justifica nao
        # modelar `b0 >= 120`. Ficou tres meses como `43` em comentario --
        # numero tirado da lista de pares FORA DO VETOR, que e um recorte.
        pares = [(0, 0)] * C.PARES
        pares[0] = (0, 23)
        pares[1] = (7, 30)                 # o maior que CHEGA a formula
        pares[2] = (99, 5)                 # b1 < 23: descartado antes
        r = C.conta(imagem_sintetica(pares), self.pref)
        self.assertEqual(r["max_b0"], 7,
                         "b0 de par descartado nao pode entrar no maximo")

    def test_sem_par_proprio_o_maior_b0_e_menos_um(self) -> None:
        r = C.conta(imagem_sintetica([]), self.pref)
        self.assertEqual(r["max_b0"], -1)

    def test_a_fronteira_de_setor_cai_entre_pares(self) -> None:
        # 352 bytes de OFS_LINK_ML ate o fim do payload: 176 pares exatos. Se
        # fosse impar, o segundo byte de um par viria do EDC/ECC.
        ate_o_fim = (C.DADOS_INICIO + C.DADOS) - (C.OFS_LINK_ML % C.SETOR)
        self.assertEqual(ate_o_fim % 2, 0)


class TestPascalConcorda(unittest.TestCase):
    """O `we2002_ml` compila e conta o mesmo que o Python."""

    PROGRAMA = C.ROOT / "wte" / "tests" / "test_ml.pas"
    FONTES = C.ROOT / "wte" / "src"
    # Copia de trabalho, nunca `roms/`. Gitignorada: onde nao existir, o caso
    # PULA em vez de fingir.
    COPIA = C.ROOT / "work" / "ml-jp.bin"

    def _fpc(self) -> str:
        fpc = shutil.which("fpc")
        if not fpc:
            self.skipTest("sem fpc -- o we2002_ml NAO foi compilado nesta "
                          "execucao")
        return fpc

    def _roda(self, ambiente: dict | None = None) -> str:
        fpc = self._fpc()
        import os
        with tempfile.TemporaryDirectory() as td:
            binario = Path(td) / "test_ml"
            r = subprocess.run(
                [fpc, f"-Fu{self.FONTES}", f"-FU{td}", f"-o{binario}",
                 str(self.PROGRAMA)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            env = dict(os.environ)
            env.update(ambiente or {})
            r = subprocess.run([str(binario)], capture_output=True, text=True,
                               env=env)
        self.assertEqual([ln for ln in r.stdout.splitlines()
                          if ln.startswith("FALHA")], [], r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def test_invariantes_sem_imagem(self) -> None:
        import os
        saida = self._roda({"WTE_TEST_IMAGEM": "", "WTE_TEST_LIVRES": ""})
        self.assertIn("PULADO\tconta na imagem", saida)
        # Numero medido, e nao suposto: um caso que some do programa Pascal
        # sumiria em silencio e o teste seguiria verde. Subiu de 7 para 19 na
        # CORR-WTE-069, que cobriu `IndiceDoBlocoMl`, `ParDoIndiceLinearMl` e
        # `PrimeiroBlocoLivreMl` -- ate ali as tres so eram exercitadas pelo
        # golden-11-descarte-ml, e num bloco so.
        self.assertIn("CASOS\t19", saida)

    def test_a_conta_bate_com_a_do_python(self) -> None:
        if not self.COPIA.is_file():
            self.skipTest(f"sem {self.COPIA.relative_to(C.ROOT)} -- a conta "
                          "das duas implementacoes NAO foi confrontada. "
                          "Crie a copia com "
                          "`cp --reflink=auto roms/japanese-shift-jis.bin "
                          "work/ml-jp.bin`")
        pref = C.prefixos(C.le_dwords(C.EXE.read_bytes(),
                                      C.VA_CONTAGEM, C.TIMES))
        dados = C.ArquivoFatiavel(self.COPIA)
        try:
            esperado = C.conta(dados, pref)["livres"]
        finally:
            dados.close()
        saida = self._roda({"WTE_TEST_IMAGEM": str(self.COPIA),
                            "WTE_TEST_LIVRES": str(esperado)})
        self.assertIn("OK\ta conta bate com a do conta_ml.py", saida)


if __name__ == "__main__":
    unittest.main()
