#!/usr/bin/env python3
"""Testes do check_golden.py -- WTE-TASK-34.

O que se mede aqui sao as duas guardas do gerador da bateria completa, e as
duas existem porque a alternativa e uma tabela que envelhece sozinha:

1. **`golden` sem `controle` na mesma ROM.** A bateria ja recusa rodar nessa
   ordem, mas o TSV e um arquivo de texto: quem o editasse a mao publicaria um
   `golden` verde sem a corrida que prova que o par roteiro+imagem e
   deterministico. Zero divergencia no `golden` pode ser paridade -- ou pode
   ser que nenhum dos dois lados gravou nada.
2. **Roteiro com par em disco e ausente do TSV.** E o defeito que a conta de
   gravacoes teve ate a WTE-TASK-31: a lista cresce, o numero nao, e ninguem
   repara porque o arquivo continua bem formado.

Os testes montam o TSV em memoria e apontam os caminhos do modulo para um
diretorio temporario: nao abrem o `.exe`, nao precisam de `DISPLAY` nem de
Wine, e rodam num clone sem a pasta `we-team-editor/`.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import check_golden as C

CAB = "roteiro\trom\tmodo\tveredito\tsegundos\tdata\n"


def linha(roteiro: str, rom: str, modo: str, veredito: str = "PASSOU") -> str:
    return f"{roteiro}\t{rom}\t{modo}\t{veredito}\t10\t2026-08-24\n"


class Base(unittest.TestCase):
    """Aponta o modulo para uma arvore temporaria e devolve tudo no fim."""

    def monta(self, tsv: str, roteiros: list[str]):
        d = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (d / "re").mkdir()
        (d / "roteiros").mkdir()
        (d / "re" / "golden.tsv").write_text(tsv, encoding="utf-8")
        for r in roteiros:
            (d / "roteiros" / f"{r}.txt").write_text("alvo: original\n")
            (d / "roteiros" / f"{r}.port.txt").write_text("alvo: port\n")
        self.enterContext(_aponta(C, TSV=d / "re" / "golden.tsv",
                                  OUT=d / "re" / "golden.md",
                                  ROTEIROS=d / "roteiros"))
        return d


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


class TestControleAntesDoTeste(Base):

    def test_golden_sem_controle_aborta(self) -> None:
        """A guarda 1: sem controle, verde e vermelho nao significam nada."""
        self.monta(CAB + linha("golden-01", "japonesa", "golden"), ["golden-01"])
        with self.assertRaises(C.CheckError) as e:
            C.mede()
        self.assertIn("sem o controle", str(e.exception))
        self.assertIn("golden-01/japonesa", str(e.exception))

    def test_par_completo_passa(self) -> None:
        self.monta(CAB
                   + linha("golden-01", "japonesa", "controle")
                   + linha("golden-01", "japonesa", "golden"), ["golden-01"])
        m = C.mede()
        self.assertEqual(len(m["corridas"]), 2)

    def test_controle_sozinho_passa(self) -> None:
        """Controle sem golden e legitimo: e o que a bateria registra quando o
        controle reprova e o golden vira NAO_APLICAVEL noutra linha."""
        self.monta(CAB + linha("golden-01", "japonesa", "controle", "SEM_ORACULO"),
                   ["golden-01"])
        self.assertEqual(len(C.mede()["corridas"]), 1)


class TestCobertura(Base):

    def test_roteiro_em_disco_e_ausente_do_tsv_aborta(self) -> None:
        """A guarda 2: bateria que cresce e tabela que nao acompanha."""
        self.monta(CAB
                   + linha("golden-01", "japonesa", "controle")
                   + linha("golden-01", "japonesa", "golden"),
                   ["golden-01", "golden-99"])
        with self.assertRaises(C.CheckError) as e:
            C.mede()
        self.assertIn("golden-99", str(e.exception))

    def test_tsv_citando_roteiro_que_sumiu_aborta(self) -> None:
        self.monta(CAB
                   + linha("golden-01", "japonesa", "controle")
                   + linha("golden-01", "japonesa", "golden")
                   + linha("golden-77", "japonesa", "controle")
                   + linha("golden-77", "japonesa", "golden"), ["golden-01"])
        with self.assertRaises(C.CheckError) as e:
            C.mede()
        self.assertIn("golden-77", str(e.exception))

    def test_roteiro_sem_par_nao_e_exigido(self) -> None:
        """Roteiro sem `.port` julga o oraculo contra ele mesmo e mais nada."""
        d = self.monta(CAB
                       + linha("golden-01", "japonesa", "controle")
                       + linha("golden-01", "japonesa", "golden"), ["golden-01"])
        (d / "roteiros" / "golden-02-so-oraculo.txt").write_text("alvo: original\n")
        self.assertEqual(C.mede()["disco"], ["golden-01"])


class TestVocabulario(Base):

    def test_veredito_desconhecido_aborta(self) -> None:
        """Palavra nova de veredito faria a distribuicao mentir em silencio."""
        self.monta(CAB + linha("golden-01", "japonesa", "controle", "QUASE"),
                   ["golden-01"])
        with self.assertRaises(C.CheckError) as e:
            C.mede()
        self.assertIn("QUASE", str(e.exception))

    def test_sem_oraculo_e_reprovou_sao_palavras_diferentes(self) -> None:
        """A distincao e a task inteira: uma acusa o port, a outra nao."""
        self.assertIn("SEM_ORACULO", C.VEREDITOS)
        self.assertIn("REPROVOU", C.VEREDITOS)

    def test_cabecalho_errado_aborta(self) -> None:
        self.monta("roteiro\tmodo\tveredito\n", ["golden-01"])
        with self.assertRaises(C.CheckError):
            C.mede()


class TestSaida(Base):

    def test_gera_tabela_com_as_duas_roms(self) -> None:
        self.monta(CAB
                   + linha("golden-01", "japonesa", "controle")
                   + linha("golden-01", "japonesa", "golden")
                   + linha("golden-01", "europeia", "controle", "SEM_ORACULO")
                   + linha("golden-01", "europeia", "golden", "NAO_APLICAVEL"),
                   ["golden-01"])
        texto = C.gera(C.mede())
        self.assertIn("| japonesa |", texto)
        self.assertIn("| europeia |", texto)
        self.assertIn("SEM_ORACULO / NAO_APLICAVEL", texto)
        self.assertIn("GERADO", texto)


class TestPremissaDaGravacaoDupla(unittest.TestCase):
    """A guarda da CORR-WTE-104: o roteiro tem de PODER medir o que diz medir.

    O `check_golden.py` ja recusa roteiro ausente do TSV. O que ele nao sabe e
    se um roteiro consegue distinguir os dois casos que ele existe para separar
    -- e isso nao se mecaniza em geral. Neste caso sim: a gravacao dupla so
    enxerga o vaivem do `Load`+`Save` num time em que `cobrador[0] !=
    cobrador[1]`. O `golden-24` usava o time 2, onde eles sao iguais e a troca e
    a identidade: o roteiro passaria com vaivem e sem ele.

    A guarda le o TIME DO PROPRIO ROTEIRO -- pela contagem de `Down` do bloco de
    selecao -- e nao um literal. Mexer no roteiro sem conferir a premissa
    reprova aqui, que e o unico lugar onde isso e barato.
    """

    ROM = C.ROOT / "roms" / "japanese-shift-jis.bin"
    ROTEIRO = C.ROTEIROS / "golden-24-gravacao-dupla.txt"

    @staticmethod
    def endereco(time: int) -> int:
        """`TATICA_COBRADOR_LOGICO + 6*time`, com os cabecalhos de setor.

        Setor MODE2/2352: 24 de cabecalho, 2048 de dados. O offset logico
        atravessa fronteira de setor e precisa pular os cabecalhos -- e a mesma
        aritmetica do `GravaTaticaNaImagem`.
        """
        setor_bytes, inicio, dados = 2352, 24, 2048
        logico = 0x46228 + 6 * time + 2 * (time // 95)
        return (850 * setor_bytes + inicio
                + (logico // dados) * setor_bytes + logico % dados)

    def time_do_roteiro(self) -> int:
        """Quantos `Down` ate o marcador `= SELECIONA_TIME`, menos um.

        O combo abre no time 0 e o primeiro `Down` leva ao 1, entao a contagem
        e `time + 1` -- e por isso que o roteiro chegava ao 2 com tres.
        """
        downs = 0
        for linha in self.ROTEIRO.read_text(encoding="utf-8").splitlines():
            if linha.strip() == "= SELECIONA_TIME":
                return downs - 1
            if linha.strip() == "! tecla Down":
                downs += 1
        self.fail("o roteiro nao tem marcador `= SELECIONA_TIME`")

    def cobradores(self, time: int) -> list[int]:
        with self.ROM.open("rb") as f:
            f.seek(self.endereco(time))
            return list(f.read(6))

    def test_a_aritmetica_bate_com_a_tabela_medida(self) -> None:
        """O endereco do `TERCEIRO_PONTO` sai da mesma conta, nao de um literal
        solto."""
        tp = C.TERCEIRO_PONTO
        self.assertEqual(self.endereco(tp["time"]), tp["endereco"])

    def test_o_roteiro_usa_o_time_da_tabela(self) -> None:
        """Roteiro e registro nao podem se soltar um do outro."""
        if not self.ROTEIRO.is_file():
            self.skipTest("roteiro ausente")
        self.assertEqual(self.time_do_roteiro(), C.TERCEIRO_PONTO["time"])

    def test_os_dois_primeiros_cobradores_diferem(self) -> None:
        """O ponto da guarda. Sem isto o gate e cego para o proprio criterio."""
        if not self.ROM.is_file():
            self.skipTest("ROM japonesa ausente (gitignored)")
        time = self.time_do_roteiro()
        b = self.cobradores(time)
        self.assertNotEqual(
            b[0], b[1],
            f"o golden-24 grava no time {time}, cujos cobradores sao {b}: "
            "`cobrador[0] == cobrador[1]` torna a troca do `Load`+`Save` "
            "invisivel, e o roteiro passa com vaivem e sem ele")

    def test_o_time_2_reprovaria(self) -> None:
        """O caso plantado -- guarda nunca exercitada e guarda ausente.

        E o estado real do roteiro antes da CORR-WTE-104.
        """
        if not self.ROM.is_file():
            self.skipTest("ROM japonesa ausente (gitignored)")
        b = self.cobradores(2)
        self.assertEqual(b[0], b[1], "o time 2 deixou de ser o contraexemplo")

    def test_a_leitura_da_rom_bate_com_a_tabela(self) -> None:
        """Os seis bytes registrados sao os da ROM, nao os que alguem lembrou."""
        if not self.ROM.is_file():
            self.skipTest("ROM japonesa ausente (gitignored)")
        tp = C.TERCEIRO_PONTO
        self.assertEqual(tuple(self.cobradores(tp["time"])),
                         tp["cobrador_virgem"])


class TestDecisaoDoTSV(unittest.TestCase):
    """A guarda da CORR-WTE-113: corrida parcial NAO apaga o registro.

    O `golden_suite.sh` reescrevia o cabecalho do TSV sempre que `--retomar`
    nao vinha, e ANTES de qualquer corrida. Com `--roteiro` isso nao filtrava:
    substituia. Aconteceu de verdade na WTE-TASK-37, levando as 92 corridas da
    WTE-TASK-34 -- 1,8 hora de relogio -- e so foi notado depois, pelo
    `check_golden.py --check`.

    O teste recorta o bloco marcado `TSV-DECISAO` do script e o roda com as
    variaveis postas a mao. E o unico jeito de exercitar a decisao sem levantar
    o Wine e ocupar o `:98` -- rodar o script inteiro dispararia a bateria, que
    e o oposto de um teste barato.
    """

    SCRIPT = C.WTE / "tools" / "golden_suite.sh"

    def bloco(self) -> str:
        fonte = self.SCRIPT.read_text(encoding="utf-8")
        i = fonte.index("# <<< TSV-DECISAO")
        j = fonte.index("# >>> TSV-DECISAO")
        return fonte[i:j]

    def roda(self, tsv: str, *, escolhidos: list[str], rom: str,
             retomar: int, registrar: tuple[str, ...] = ()) -> str:
        """Monta o TSV, roda o bloco, devolve o arquivo resultante."""
        with tempfile.TemporaryDirectory() as d:
            alvo = Path(d) / "golden.tsv"
            alvo.write_text(tsv, encoding="utf-8")
            decl = "\n".join([
                "set -euo pipefail",
                f"SAIDA={alvo}",
                f"RETOMAR={retomar}",
                f"ROM={rom}",
                "ESCOLHIDOS=({})".format(
                    " ".join(f'"{e}"' for e in escolhidos)),
            ])
            chamada = ("\n".join(f'registra {x}' for x in registrar)
                       if registrar else "")
            r = subprocess.run(["bash", "-c",
                                decl + "\n" + self.bloco() + "\n" + chamada],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            return alvo.read_text(encoding="utf-8")

    def tsv(self, *linhas: str) -> str:
        return CAB + "".join(linhas)

    def test_corrida_parcial_por_roteiro_preserva(self) -> None:
        """O defeito literal: 97 linhas entram, 97 tem de sair."""
        entrada = self.tsv(linha("golden-01-arranque", "japonesa", "controle"),
                           linha("golden-01-arranque", "japonesa", "golden"))
        saida = self.roda(entrada, escolhidos=["golden-25-retorno"],
                          rom="ambas", retomar=0)
        self.assertEqual(saida, entrada)

    def test_corrida_parcial_por_rom_preserva(self) -> None:
        """`--rom japonesa` tambem e parcial -- metade da bateria."""
        entrada = self.tsv(linha("golden-01-arranque", "europeia", "controle"))
        saida = self.roda(entrada, escolhidos=[], rom="japonesa", retomar=0)
        self.assertEqual(saida, entrada)

    def test_bateria_inteira_ainda_trunca(self) -> None:
        """O truncamento continua certo onde sempre foi: a corrida completa.

        Sem este caso, "preservar" viraria "nunca limpar", e o TSV acumularia
        corrida velha de roteiro que saiu do disco.
        """
        entrada = self.tsv(linha("golden-01-arranque", "japonesa", "controle"))
        saida = self.roda(entrada, escolhidos=[], rom="ambas", retomar=0)
        self.assertEqual(saida, CAB)

    def test_retomar_preserva_como_sempre(self) -> None:
        entrada = self.tsv(linha("golden-01-arranque", "japonesa", "controle"))
        saida = self.roda(entrada, escolhidos=[], rom="ambas", retomar=1)
        self.assertEqual(saida, entrada)

    def test_parcial_ATUALIZA_a_linha_em_vez_de_duplicar(self) -> None:
        """A outra metade do conserto, e a que a preservacao exige.

        Preservar sem substituir faria a segunda corrida do mesmo par deixar
        DUAS linhas para o mesmo trio, e o `check_golden.py` passaria a ler
        duas datas para a mesma coisa.
        """
        entrada = self.tsv(linha("golden-25-retorno", "japonesa", "controle"),
                           linha("golden-01-arranque", "japonesa", "golden"))
        saida = self.roda(entrada, escolhidos=["golden-25-retorno"],
                          rom="ambas", retomar=0,
                          registrar=("golden-25-retorno japonesa controle "
                                     "REPROVOU 42",))
        corpo = [l for l in saida.splitlines()[1:] if l]
        trio = [l for l in corpo if l.startswith("golden-25-retorno\tjaponesa\tcontrole\t")]
        self.assertEqual(len(trio), 1, saida)
        self.assertIn("REPROVOU", trio[0])
        self.assertEqual(len(corpo), 2, saida)

    def test_a_linha_de_outro_par_nao_e_tocada(self) -> None:
        """Substituir e por trio, nao por roteiro."""
        entrada = self.tsv(linha("golden-25-retorno", "japonesa", "controle"),
                           linha("golden-25-retorno", "japonesa", "golden"))
        saida = self.roda(entrada, escolhidos=["golden-25-retorno"],
                          rom="ambas", retomar=0,
                          registrar=("golden-25-retorno japonesa controle "
                                     "PASSOU 9",))
        corpo = [l for l in saida.splitlines()[1:] if l]
        self.assertEqual(len(corpo), 2, saida)
        self.assertTrue(any(l.startswith("golden-25-retorno\tjaponesa\tgolden\t")
                            for l in corpo), saida)


if __name__ == "__main__":
    unittest.main()
