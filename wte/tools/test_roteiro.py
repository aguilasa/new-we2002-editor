#!/usr/bin/env python3
"""Testes do roteiro.sh -- CORR-WTE-080.

O driver de roteiro e `source`ado pelos dois lados do gate golden, e nada o
media. Aqui se medem as duas coisas que a CORR-WTE-080 acrescentou, e as duas
sao sobre FALHA -- que e o caso em que ninguem esta olhando:

1. `espera: <seg>` sobe o limite da PROXIMA janela, e volta ao default depois.
   Espera curta demais num passo que vem logo depois de acao cara e o que fazia
   o `golden-14-uniforme` reprovar por tempo;
2. espera estourada na PRIMEIRA janela diz "o app nao subiu", e nas demais diz
   que o dialogo nao veio. As duas mandam procurar em lugares diferentes, e ate
   a WTE-TASK-29 a mensagem era a mesma.

A busca de janela e substituida por um duble (`janela`), entao nada disto
precisa de `DISPLAY`, de Wine ou do `.exe`.
"""

from __future__ import annotations

import subprocess
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROTEIRO_SH = ROOT / "wte" / "tools" / "roteiro.sh"

# O duble conta as chamadas num arquivo, e nao numa variavel: `espera_janela`
# roda dentro de `$(...)`, e o que um subshell incrementa nao volta.
PROLOGO = """
set -uo pipefail
export ROTEIRO_ESPERA_PADRAO=3
source "{sh}"
roteiro_foca() {{ :; }}
janela() {{
  echo x >> "{cnt}"
  [ "$(wc -l < "{cnt}")" -le {achadas} ] && {{ echo "111 10 20"; return 0; }}
  return 1
}}
"""


def roda(roteiro: str, achadas: int) -> tuple[int, str]:
    """Executa `roteiro` com um duble que acha as `achadas` primeiras janelas."""
    with tempfile.TemporaryDirectory() as td:
        alvo = Path(td) / "r.txt"
        alvo.write_text(roteiro, encoding="utf-8")
        script = PROLOGO.format(sh=ROTEIRO_SH, cnt=Path(td) / "cnt",
                                achadas=achadas)
        script += f'roteiro_executa "{alvo}"\n'
        r = subprocess.run(["bash", "-c", script], capture_output=True,
                           text=True)
        return r.returncode, r.stdout + r.stderr


class TestDiagnostico(unittest.TestCase):
    def test_primeira_janela_diz_que_o_app_nao_subiu(self) -> None:
        rc, saida = roda("espera: 1\n> Abre\n", achadas=0)
        self.assertNotEqual(rc, 0)
        self.assertIn("o app nao subiu", saida)
        self.assertIn("PRIMEIRA janela", saida)

    def test_janela_seguinte_diz_que_o_dialogo_nao_veio(self) -> None:
        rc, saida = roda("> Abre\nespera: 1\n> Extrair\n", achadas=1)
        self.assertNotEqual(rc, 0)
        self.assertNotIn("o app nao subiu", saida)
        self.assertIn("dialogo deste passo nao veio", saida)

    def test_a_janela_achada_nao_dispara_diagnostico(self) -> None:
        rc, saida = roda("> Abre\n", achadas=1)
        self.assertEqual(rc, 0, saida)
        self.assertNotIn("ERRO", saida)


class TestEspera(unittest.TestCase):
    def test_o_limite_da_proxima_janela_vem_do_espera(self) -> None:
        ini = time.monotonic()
        rc, saida = roda("espera: 2\n> Abre\n", achadas=0)
        gasto = time.monotonic() - ini
        self.assertNotEqual(rc, 0)
        self.assertIn("nao apareceu em 2s", saida)
        # O default e 30s: se o `espera:` fosse ignorado, isto levaria 30.
        self.assertLess(gasto, 15)

    def test_o_espera_vale_so_para_a_proxima(self) -> None:
        # A primeira janela e achada; a segunda estoura, e tem de estourar com
        # o DEFAULT -- espera longa em todo passo esconde app que nao subiu.
        # O default aqui e 3s (`ROTEIRO_ESPERA_PADRAO` do prologo), e nao os 30
        # do gate: medir isto com o valor de producao custaria meio minuto de
        # bateria e nao mediria nada a mais.
        rc, saida = roda("espera: 1\n> Abre\n> Extrair\n", achadas=1)
        self.assertNotEqual(rc, 0)
        self.assertIn("nao apareceu em 3s", saida)


if __name__ == "__main__":
    unittest.main()
