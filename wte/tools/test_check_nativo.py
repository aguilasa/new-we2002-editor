#!/usr/bin/env python3
"""Testes do `check_nativo.py` -- CORR-WTE-119.

As tres recusas plantadas, no molde do `test_check_divergencias.py`: espelho da
arvore em `tempfile`, caminhos do modulo repontados, sem `:98`, sem Wine e sem
imagem.

O que se protege aqui e o unico documento de fechamento que nao tinha quem o
defendesse. O `nativo.md` REPETE os sete valores do `nativo.tsv` numa tabela
propria; ate esta correcao, uma corrida futura podia mudar um valor no TSV e
deixar o `.md` afirmando o velho, em verde.
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
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

import check_nativo as C


class _aponta:
    """Troca atributos de modulo e devolve os originais ao sair."""

    def __init__(self, mod, **kw):
        self.mod, self.kw, self.velho = mod, kw, {}

    def __enter__(self):
        for k, v in self.kw.items():
            self.velho[k] = getattr(self.mod, k)
            setattr(self.mod, k, v)
        return self.mod

    def __exit__(self, *_):
        for k, v in self.velho.items():
            setattr(self.mod, k, v)
        return False


CAB = "medida\tvalor\tveredito\n"

# Duas medidas bastam para os casos, e a segunda e de proposito uma cujo `.md`
# ENFEITA o valor -- e o par que prova que a normalizacao existe e funciona.
TSV = (CAB
       + "ldd-wine\t0 de 56 bibliotecas\tok\n"
       + "janela\t522x475, titulo conferido\tok\n")

MD = """# nativo

| Caminho | Por que |
|---|---|
| `/var/lib/flatpak` | a tabela de mascaras, que NAO e a de medidas |

## As sete medidas

| Medida | Valor | Veredito |
|---|---|---|
| `ldd-wine` | 0 de 56 bibliotecas | ok |
| `janela` | 522×475, título conferido | ok |
"""


class Base(unittest.TestCase):
    def monta(self, tsv: str = TSV, md: str = MD) -> Path:
        d = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (d / "nativo.tsv").write_text(tsv, encoding="utf-8")
        (d / "nativo.md").write_text(md, encoding="utf-8")
        self.enterContext(_aponta(C, RAIZ=d, TSV=d / "nativo.tsv",
                                  MD=d / "nativo.md"))
        return d

    def problemas(self) -> list[str]:
        return C.mede()["problemas"]

    def codigo(self) -> int:
        """A saida do `main()` e engolida: sem isso o relatorio de uma recusa
        PLANTADA aparece no meio do `make -C wte check`."""
        with (contextlib.redirect_stderr(io.StringIO()),
              contextlib.redirect_stdout(io.StringIO())):
            return C.main([])


class TestEstadoDeHoje(Base):
    def test_a_arvore_real_passa(self) -> None:
        """Sem espelho: o modulo aponta para o `wte/re/` de verdade."""
        self.assertEqual(C.mede()["problemas"], [])

    def test_as_sete_medidas_estao_no_TSV(self) -> None:
        self.assertEqual(len(C.mede()["tsv"]), 7)

    def test_o_espelho_montado_passa(self) -> None:
        """Se este reprovar, o espelho e que esta errado, nao o gate."""
        self.monta()
        self.assertEqual(self.problemas(), [])


class TestNormalizacao(Base):
    """A comparacao aceita o `.md` mais bonito, e nao o `.md` que contradiz."""

    def test_x_multiplicacao_e_acento_passam(self) -> None:
        """`522x475, titulo` no TSV contra `522×475, título` no `.md`."""
        self.monta()
        self.assertEqual(self.problemas(), [])

    def test_crase_e_contexto_a_mais_passam(self) -> None:
        md = MD.replace("| `ldd-wine` | 0 de 56 bibliotecas |",
                        "| `ldd-wine` | **0** de 56 `bibliotecas`, medido |")
        self.monta(md=md)
        self.assertEqual(self.problemas(), [])

    def test_numero_diferente_NAO_passa(self) -> None:
        """O limite da tolerancia, e a razao de ela ser substring."""
        md = MD.replace("0 de 56 bibliotecas", "0 de 58 bibliotecas")
        self.monta(md=md)
        p = self.problemas()
        self.assertTrue(any("ldd-wine" in x and "58" in x for x in p), p)


class TestAsTresRecusas(Base):
    def test_1_valor_divergente_reprova(self) -> None:
        md = MD.replace("522×475", "640×480")
        self.monta(md=md)
        self.assertTrue(any("janela" in x for x in self.problemas()))
        self.assertEqual(self.codigo(), 2)

    def test_2_medida_no_md_que_o_TSV_nao_tem_reprova(self) -> None:
        md = MD + "| `inventada` | valor qualquer | ok |\n"
        self.monta(md=md)
        p = self.problemas()
        self.assertTrue(any("inventada" in x and "sem fonte" in x for x in p), p)
        self.assertEqual(self.codigo(), 2)

    def test_3_veredito_reprovou_no_TSV_derruba_o_gate(self) -> None:
        """Um `reprovou` que ficou no arquivo e RESULTADO -- a condicao 3 nao
        esta cumprida, e o gate nao pode ficar verde por cima."""
        tsv = TSV.replace("522x475, titulo conferido\tok",
                          "522x475, titulo conferido\treprovou")
        md = MD.replace("| `janela` | 522×475, título conferido | ok |",
                        "| `janela` | 522×475, título conferido | reprovou |")
        self.monta(tsv=tsv, md=md)
        p = self.problemas()
        self.assertTrue(any("nao esta cumprida" in x for x in p), p)
        self.assertEqual(self.codigo(), 2)

    def test_medida_do_TSV_ausente_do_md_reprova(self) -> None:
        """A quarta direcao, que a CORR nao numerou e o modulo cobre."""
        md = MD.replace("| `janela` | 522×475, título conferido | ok |\n", "")
        self.monta(md=md)
        p = self.problemas()
        self.assertTrue(any("janela" in x and "NAO na tabela" in x for x in p), p)


class TestLeitura(Base):
    def test_a_outra_tabela_do_md_nao_e_lida(self) -> None:
        """O `.md` tem a tabela de caminhos mascarados ANTES da de medidas, e o
        primeiro campo dela tambem vem entre crases. O que as separa e o numero
        de colunas -- se o leitor as confundisse, `/var/lib/flatpak` viraria uma
        medida sem fonte."""
        self.monta()
        self.assertEqual([x["medida"] for x in C.le_md(C.MD)],
                         ["ldd-wine", "janela"])

    def test_TSV_ausente_aborta(self) -> None:
        d = self.monta()
        (d / "nativo.tsv").unlink()
        with self.assertRaises(C.NativoError):
            C.mede()
        self.assertEqual(self.codigo(), 2)

    def test_cabecalho_errado_aborta(self) -> None:
        self.monta(tsv="medida\tvalor\n")
        with self.assertRaises(C.NativoError):
            C.mede()

    def test_linha_com_campo_faltando_aborta(self) -> None:
        self.monta(tsv=CAB + "janela\t522x475\n")
        with self.assertRaises(C.NativoError) as ctx:
            C.mede()
        self.assertIn("3 campos", str(ctx.exception))


class TestGuardaDoSemWine(unittest.TestCase):
    """As duas clausulas da guarda do `sem_wine.sh` -- CORR-WTE-120.

    A prosa creditava a recusa ao `command -v wine/wine64/wineserver/winecfg`, e
    **nesta maquina essa clausula nao pode disparar**: o Wine daqui e o runner
    do Bottles, em `~/.var/app/`, e nunca esteve no `PATH` -- ela e verdadeira
    antes de mascarar coisa nenhuma. Quem recusa de verdade e o laco que exige
    cada alvo VAZIO dentro do namespace.

    Nao e afirmacao falsa -- a guarda recusa. E credito na clausula errada, e o
    custo e concreto: quem simplificar o script achando que o `command -v` e a
    protecao pode apagar o laco de vazio, e o ambiente deixa de ser limpo sem
    que nada reclame.

    Os dois casos abaixo NAO dependem desta maquina: cada um fabrica o proprio
    alvo em `tempfile`. Precisam do `bwrap`, e pulam sem ele.
    """

    SCRIPT = C.RAIZ / "wte" / "tools" / "sem_wine.sh"

    def setUp(self) -> None:
        if not shutil.which("bwrap"):
            self.skipTest("sem bwrap -- a guarda NAO foi exercitada")
        # O modulo pode estar repontado por outro caso; o script mora na arvore.
        self.script = Path(__file__).resolve().parent / "sem_wine.sh"

    def roda(self, script: Path, ambiente: dict | None = None):
        env = dict(os.environ)
        env.update(ambiente or {})
        return subprocess.run([BASH, str(script), "--", "/bin/true"],
                              capture_output=True, text=True, env=env)

    def test_o_estado_de_hoje_passa(self) -> None:
        """O controle: sem plantar nada, a guarda deixa passar."""
        r = self.roda(self.script)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("guarda passou", r.stdout)

    def test_clausula_1_PATH_sujo_recusa(self) -> None:
        """Um `wine` falso no `PATH` -- a clausula que nesta maquina esta
        sempre satisfeita, exercitada fabricando o caso que ela existe para
        pegar."""
        with tempfile.TemporaryDirectory() as d:
            falso = Path(d) / "wine"
            falso.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            falso.chmod(0o755)
            r = self.roda(self.script, {"PATH": f"{d}:{os.environ['PATH']}"})
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("wine ainda responde dentro do namespace", r.stderr)

    def test_clausula_2_alvo_nao_vazio_recusa(self) -> None:
        """A clausula que trabalha nesta maquina.

        Um diretorio na lista da guarda e FORA das mascaras: dentro do
        namespace ele continua cheio, e o laco recusa com o nome dele. E
        exatamente o que aconteceria se alguem tirasse um alvo do `tmpfs` e
        esquecesse de tirar da guarda -- ou o contrario.
        """
        with tempfile.TemporaryDirectory() as d:
            alvo = Path(d) / "cheio"
            alvo.mkdir()
            (alvo / "algo").write_text("x", encoding="utf-8")

            fonte = self.script.read_text(encoding="utf-8")
            velho = "for d in '\"${ALVOS[*]}\"'; do"
            self.assertIn(velho, fonte, "o laco de vazio sumiu do script")
            fonte = fonte.replace(
                velho, f"for d in '\"${{ALVOS[*]}}\"' \"{alvo}\"; do", 1)
            espelho = Path(d) / "sem_wine.sh"
            espelho.write_text(fonte, encoding="utf-8")
            r = self.roda(espelho)
            esperado = f"ERRO: {alvo} nao ficou vazio"
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn(esperado, r.stderr)

    def test_apagar_a_clausula_2_DESLIGA_a_conferencia(self) -> None:
        """A afirmacao central da CORR-WTE-120, medida.

        Com o laco de vazio, um alvo cheio recusa. Sem ele -- e com a primeira
        clausula INTACTA -- o mesmo alvo cheio passa: o ambiente deixa de ser
        limpo e nada reclama. E por isso que creditar a guarda ao `command -v`
        e perigoso, e nao so impreciso.
        """
        with tempfile.TemporaryDirectory() as d:
            alvo = Path(d) / "cheio"
            alvo.mkdir()
            (alvo / "algo").write_text("x", encoding="utf-8")

            fonte = self.script.read_text(encoding="utf-8")
            velho = "for d in '\"${ALVOS[*]}\"'; do"
            com = fonte.replace(
                velho, f"for d in '\"${{ALVOS[*]}}\"' \"{alvo}\"; do", 1)
            i, j = com.index("for d in"), com.index("'\n\nexec bwrap")
            sem = com[:i] + com[j:]

            p_com, p_sem = Path(d) / "com.sh", Path(d) / "sem.sh"
            p_com.write_text(com, encoding="utf-8")
            p_sem.write_text(sem, encoding="utf-8")
            r_com, r_sem = self.roda(p_com), self.roda(p_sem)

        self.assertEqual(r_com.returncode, 1, "com o laco, tinha de recusar")
        self.assertEqual(r_sem.returncode, 0,
                         "sem o laco, o alvo cheio passa -- e e esse o ponto")
        self.assertIn("guarda passou", r_sem.stdout)

    def test_o_cabecalho_nomeia_as_duas_clausulas(self) -> None:
        """Prosa e o que esta correcao consertou; sem isto ela envelhece de
        novo na proxima leitura."""
        fonte = self.script.read_text(encoding="utf-8")
        self.assertIn("DUAS clausulas", fonte)
        self.assertIn("so a segunda tem trabalho", fonte)


if __name__ == "__main__":
    unittest.main()
