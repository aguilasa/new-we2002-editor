#!/usr/bin/env python3
"""Testes do roteiro.sh -- CORR-WTE-080, e a convencao de display -- CORR-WTE-088.

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

import os
import re
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

# O interpretador bash, e por que ele nao e a cadeia literal `"bash"`.
#
# No Windows a busca do `CreateProcess` olha `C:\Windows\System32` ANTES do
# `PATH`, e la mora o `bash.exe` da Microsoft -- o atalho do WSL. Com WSL sem
# distribuicao instalada ele sai 1 dizendo "Windows Subsystem for Linux has no
# installed distributions", e por PATH nenhum se chega ao bash do Git for
# Windows: pos-lo na frente do PATH nao adianta, porque o System32 vem antes.
#
# `WTE_BASH` da o caminho completo. Sem ela nada muda -- no Linux `bash` e o
# que sempre foi.
BASH = os.environ.get("WTE_BASH", "bash")

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
        # `newline` e `as_posix` pelo mesmo motivo do `test_check_golden.py`: o
        # `roteiro.sh` le este arquivo linha a linha (CRLF entraria no ultimo
        # campo de cada uma) e o caminho vai para dentro de um script bash, que
        # trataria a contrabarra do Windows como escape.
        alvo.write_text(roteiro, encoding="utf-8", newline="\n")
        script = PROLOGO.format(sh=ROTEIRO_SH.as_posix(),
                                cnt=(Path(td) / "cnt").as_posix(),
                                achadas=achadas)
        script += f'roteiro_executa "{alvo.as_posix()}"\n'
        r = subprocess.run([BASH, "-c", script], capture_output=True,
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


# ------------------------------------------- a convencao de display (CORR-088) --
#
# **`:99` em ferramenta viva so vale como data medida; o alvo e o `:98`.** O
# display dos gates mudou em 2026-08-20 e o CLAUDE.md e explicito sobre o que
# fica: registro historico continua dizendo `:99`, texto que descreve o
# comportamento de hoje, nao. A CORR-WTE-073 varreu o codigo executavel; a
# CORR-WTE-088 varreu os comentarios, e achou catorze linhas vivas -- cinco a
# mais do que a propria correcao tinha enumerado, porque o `grep` dela cobria
# cinco arquivos e o residuo estava em sete.
#
# **A lista abaixo e allowlist, e nao regra.** Tentou-se primeiro a regra que a
# CORR-088 sugeriu -- "linha sem ano nem `WTE-TASK`/`CORR-` ao lado reprova" --
# e ela da sete falsos positivos: metade destas linhas e continuacao de um
# paragrafo cujo ano esta duas linhas acima. Uma lista explicita e o que este
# repositorio ja usa para o mesmo problema (`NARRACAO`, no `check_fase1.py`):
# custa uma linha por sitio e nunca erra. Editar o texto de uma delas reprova
# aqui, e a reprovacao e o pedido para reclassificar.
HISTORICO_99 = {
    ("golden_run_laz.sh", 'o port nao recebe teclado no `:99`'),
    ("roteiro.sh", "O ALVO E O `:98` DESDE 2026-08-20, e antes era o `:99`"),
    ("roteiro.sh", "mantem uma janela de 1024x768 no `:99`"),
    ("roteiro.sh", "No `:99` o `ficha_dorsal` do port ficava"),
    ("compara_tela.sh", "`we-team-editor.exe` no `:99` depois de uma medicao"),
    ("compara_tela.sh", "Medidas no `:99`, nos dois lados, em 2026-08-12"),
    ("compara_tela.py", "Medido no `:99`: 544x495"),
    ("conta_ml.py", "`:99`, lido da captura"),
    ("check_lcl_combo.py", "a forma que o repositorio adotou quando saiu do `:99`"),
    ("check_bitfields.py",
     "medido no `:99`, o `TScrollBar` do gtk2 desenha mais alto"),
    ("check_bitfields.py",
     "nenhuma regua de tela pega isso: medido no `:99`"),
    ("check_fase2.py", "Teclado não chega ao app LCL no `:99`"),
}

# Este arquivo fica de fora da propria varredura: a `HISTORICO_99` cita as
# doze linhas verbatim, e cada citacao casaria como sitio novo.
ESTE = Path(__file__).name

FERRAMENTAS = sorted(
    p for padrao in ("*.sh", "*.py")
    for p in (ROOT / "wte" / "tools").glob(padrao) if p.name != ESTE)


class TestConvencaoDeDisplay(unittest.TestCase):
    """Nenhum `:99` novo em `wte/tools/`, e o alvo declarado e o `:98`."""

    def test_todo_99_vivo_esta_declarado_como_historico(self) -> None:
        residuo = []
        for caminho in FERRAMENTAS:
            for i, linha in enumerate(
                    caminho.read_text(encoding="utf-8").splitlines(), 1):
                if ":99" not in linha:
                    continue
                if any(caminho.name == arq and trecho in linha
                       for arq, trecho in HISTORICO_99):
                    continue
                residuo.append(f"{caminho.name}:{i}: {linha.strip()}")
        self.assertEqual(residuo, [], "\n".join(
            ["`:99` em linha nao declarada como historica -- ou e o "
             "comportamento de hoje (troque por `:98`), ou e medicao "
             "antiga (acrescente a HISTORICO_99):"] + residuo))

    def test_a_allowlist_nao_tem_entrada_morta(self) -> None:
        """Entrada que nao casa mais e texto reescrito, e precisa ser revista."""
        textos = {p.name: p.read_text(encoding="utf-8") for p in FERRAMENTAS}
        mortas = [f"{arq}: {trecho!r}" for arq, trecho in sorted(HISTORICO_99)
                  if trecho not in textos.get(arq, "")]
        self.assertEqual(mortas, [], "\n".join(
            ["entrada da HISTORICO_99 que nao casa com nenhuma linha:"] + mortas))

    def test_o_default_declarado_e_o_98(self) -> None:
        """O numero mora numa variavel por ferramenta, com `:98` de default."""
        for arq, var in (("roteiro.sh", "WTE_DISPLAY"),
                         ("compara_tela.sh", "WTE_DISPLAY")):
            texto = (ROOT / "wte" / "tools" / arq).read_text(encoding="utf-8")
            self.assertRegex(texto, rf'\$\{{{var}:-:98\}}',
                             f"{arq}: o default de {var} deixou de ser `:98`")


