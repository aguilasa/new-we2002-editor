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

import re
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


class TestSegundaRegua(unittest.TestCase):
    """A segunda regua tem de deixar rastro versionado, nao so passar na tela.

    O `--conferir` roda no fim de cada corrida e imprime o veredito no
    terminal; o `cmp.tsv` fica em `/tmp` e some. Das cinco primeiras sessoes,
    uma so teve o numero registrado -- em prosa, no Log de uma passagem
    (CORR-WTE-047). Aqui se mede a fusao e o veredito derivado dela.
    """

    def test_fundir_substitui_a_sessao_e_preserva_as_outras(self) -> None:
        """Rodar a mesma corrida duas vezes nao pode duplicar faixa."""
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            alvo = tmp / "cmp-medido.tsv"
            origem = tmp / "cmp.tsv"
            antigo = A.CMP_MEDIDO_TSV
            try:
                A.CMP_MEDIDO_TSV = alvo
                origem.write_text(
                    "inicio\tfim\ttamanho\tsetor\tbyte_no_setor\n"
                    "100\t120\t21\t0\t100\n", encoding="utf-8")
                A.fundir_cmp(origem, "a.bin", "S1")
                A.fundir_cmp(origem, "b.bin", "S2")
                A.fundir_cmp(origem, "a.bin", "S1")   # de novo
                linhas = A.ler_cmp_medido()
            finally:
                A.CMP_MEDIDO_TSV = antigo
        self.assertEqual([r["sessao"] for r in linhas], ["S2", "S1"])
        self.assertEqual(linhas[1]["imagem"], "a.bin")

    def test_fundir_io_substitui_a_sessao_e_preserva_as_outras(self) -> None:
        """A PRIMEIRA regua tinha a mesma doenca, e ficou sem conserto.

        A CORR-WTE-047 deu porta automatica ao `cmp`; o trace continuou
        entrando a mao, o que e indistinguivel de nao entrar quando alguem
        esquece. Medido na WTE-TASK-27.
        """
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            alvo = tmp / "io-medido.tsv"
            origem = tmp / "io.tsv"
            antigo = A.MEDIDO_TSV
            try:
                A.MEDIDO_TSV = alvo
                alvo.write_text("\t".join(A.IO_CABECALHO) + "\n",
                                encoding="utf-8")
                origem.write_text(
                    "\t".join(A.IO_CABECALHO) + "\n"
                    "a.bin\tS1\tGRAVA\tW\t100\t120\t21\t0\t100\n",
                    encoding="utf-8")
                A.fundir_io(origem, "S1")
                origem.write_text(
                    "\t".join(A.IO_CABECALHO) + "\n"
                    "b.bin\tS2\tGRAVA\tW\t200\t220\t21\t0\t200\n",
                    encoding="utf-8")
                A.fundir_io(origem, "S2")
                origem.write_text(
                    "\t".join(A.IO_CABECALHO) + "\n"
                    "a.bin\tS1\tGRAVA\tW\t100\t120\t21\t0\t100\n",
                    encoding="utf-8")
                A.fundir_io(origem, "S1")          # de novo
                linhas = A.ler_medido()
            finally:
                A.MEDIDO_TSV = antigo
        self.assertEqual([r["sessao"] for r in linhas], ["S2", "S1"])

    def test_fundir_io_preserva_a_acao_que_nao_gravou(self) -> None:
        """`op` = `.` e resultado: distingue "nao gravou" de "nao rodou"."""
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            alvo = tmp / "io-medido.tsv"
            origem = tmp / "io.tsv"
            antigo = A.MEDIDO_TSV
            try:
                A.MEDIDO_TSV = alvo
                alvo.write_text("\t".join(A.IO_CABECALHO) + "\n",
                                encoding="utf-8")
                origem.write_text(
                    "\t".join(A.IO_CABECALHO) + "\n"
                    "a.bin\tS1\tGRAVA_BARRAS\t.\t\t\t0\t\t\n",
                    encoding="utf-8")
                A.fundir_io(origem, "S1")
                linhas = A.ler_medido()
            finally:
                A.MEDIDO_TSV = antigo
        self.assertEqual(len(linhas), 1)
        self.assertEqual(linhas[0]["acao"], "GRAVA_BARRAS")
        self.assertEqual(linhas[0]["op"], ".")

    def test_veredito_ignora_sessao_que_nao_escreveu(self) -> None:
        io = [{"sessao": "S", "op": "R", "inicio": "10", "fim": "20"}]
        self.assertEqual(A.veredito_das_reguas(io, []), [])

    def test_veredito_marca_sessao_sem_cmp_versionado(self) -> None:
        """O caso que a CORR-WTE-047 achou: escreveu, e a regua sumiu."""
        io = [{"sessao": "S", "op": "W", "inicio": "10", "fim": "20"}]
        v = A.veredito_das_reguas(io, [])[0]
        self.assertFalse(v["tem_cmp"])
        self.assertEqual((v["cmp"], v["dentro"], v["escritas"]), (0, 0, 1))

    def test_veredito_conta_faixa_do_cmp_fora_das_escritas(self) -> None:
        io = [{"sessao": "S", "op": "W", "inicio": "10", "fim": "20"}]
        cmp_ = [{"sessao": "S", "inicio": "12", "fim": "15"},
                {"sessao": "S", "inicio": "500", "fim": "509"}]
        v = A.veredito_das_reguas(io, cmp_)[0]
        self.assertEqual((v["cmp"], v["dentro"]), (2, 1))


class TestPapelNoLegado(unittest.TestCase):
    """O classificador que responde por um `OFS_*` sem evidencia dinamica.

    Ele le o `Database.cpp` do `newWe2002` e diz se o offset e endereco de
    campo ou artefato do jeito de LER do Moriero. E a segunda regua da
    WTE-TASK-19, e a unica que nao depende de tela.
    """

    def papel(self, fonte: str):
        return A.papel_no_legado(fonte)

    def test_seek_dentro_de_case_e_retomada(self) -> None:
        p = self.papel("\n".join([
            "    switch(i)", "    {", "      case 44+PLAYERS_NC :",
            "        image_file.Read(buf1, 4);",
            "        image_file.Seek(OFS_PLAYER_ATTR_1);"]))
        self.assertEqual(p["OFS_PLAYER_ATTR_1"],
                         A.Papel("retomada", "44+PLAYERS_NC", "case", 5,
                                 "case 44+PLAYERS_NC :"))

    def test_seek_dentro_de_if_tambem_e_retomada(self) -> None:
        """O legado usa as duas formas para a mesma coisa."""
        p = self.papel("\n".join([
            "    if(i == 57)", "    {",
            "      image_file.Seek(OFS_TEAM_NAME_5_A);"]))
        self.assertEqual(p["OFS_TEAM_NAME_5_A"],
                         A.Papel("retomada", "57", "if", 3, "if(i == 57)"))

    def test_a_construcao_que_casou_nao_e_descartada(self) -> None:
        """CORR-WTE-046: a prova dizia `case N` para os dois gatilhos.

        Com o mesmo gatilho nas duas formas, a unica coisa que distingue as
        duas linhas e o campo `forma`. Se ele voltar a ser jogado fora, os dois
        vereditos ficam identicos e este teste reprova.
        """
        com_case = self.papel("\n".join([
            "      case 30 :", "        image_file.Seek(OFS_A);"]))
        com_if = self.papel("\n".join([
            "      if(i == 30)", "        image_file.Seek(OFS_A);"]))
        self.assertEqual(com_case["OFS_A"].forma, "case")
        self.assertEqual(com_if["OFS_A"].forma, "if")
        self.assertEqual(com_case["OFS_A"].gatilho, com_if["OFS_A"].gatilho)
        self.assertNotEqual(com_case["OFS_A"], com_if["OFS_A"])

    def test_a_linha_do_seek_e_1_based(self) -> None:
        """A linha e o que torna a citacao conferivel por `grep` quando o
        gatilho se repete no arquivo -- `case 30 :` existe em dois blocos sem
        relacao com o `if(i == 30)` que a prova quer citar."""
        p = self.papel("\n".join([
            "// a", "// b", "      if(i == 30)",
            "        image_file.Seek(OFS_A);"]))
        self.assertEqual(p["OFS_A"].linha, 4)

    def test_seek_seguido_de_for_e_varredura(self) -> None:
        p = self.papel("\n".join([
            "  image_file.Seek(OFS_TEAM_NAME_5);",
            "  for(i = 0;i < 32;i ++)", "  {"]))
        self.assertEqual(p["OFS_TEAM_NAME_5"][0], "varredura")

    def test_seek_solto_nao_vira_nem_um_nem_outro(self) -> None:
        """Sem `case` atras nem `for` na frente, o veredito e `direto`.

        Importa que exista: `direto` e o unico papel que NAO explica ausencia
        no trace, e e ele que mantem a linha "sem veredito" possivel.
        """
        p = self.papel("  image_file.Seek(OFS_LINK_ML);\n  x = 1;")
        self.assertEqual(p["OFS_LINK_ML"][0], "direto")

    def test_case_longe_demais_nao_conta(self) -> None:
        """A janela e curta de proposito, para nao atravessar o `case` anterior."""
        fonte = ["      case 9 :"] + ["        x();"] * 12 + [
            "        image_file.Seek(OFS_X);"]
        self.assertEqual(A.papel_no_legado("\n".join(fonte))["OFS_X"][0],
                         "direto")

    def test_o_legado_de_verdade_classifica_todo_offset_que_ele_le(self) -> None:
        p = A.papel_no_legado()
        self.assertGreater(len(p), 60, "o Database.cpp deixou de ser lido")
        self.assertEqual(p["OFS_PLAYER_ATTR_9"][0], "retomada")
        self.assertEqual(p["OFS_ML_PLAYER_ATTR"][0], "varredura")


class TestSecaoAreas(unittest.TestCase):
    """A secao das seis areas nomeia a IMAGEM, nunca o rotulo da sessao.

    `09-areas-com-time` e o diretorio de saida do `diff_dirigido.sh`; a imagem
    e `japanese-shift-jis.bin`. Interpolar a constante produzia
    `roms/09-areas-com-time`, caminho que nao existe (CORR-WTE-045) -- e o
    paragrafo seguinte, que fala da europeia travar, so fecha com a japonesa.
    """

    def linhas(self, imagem: str) -> list[dict[str, str]]:
        def r(acao, op, ini, tam):
            return {"imagem": imagem, "sessao": A.AREAS, "acao": acao,
                    "op": op, "inicio": str(ini), "fim": str(ini + tam - 1),
                    "tamanho": str(tam), "setor": str(ini // A.SETOR),
                    "byte_no_setor": str(ini % A.SETOR)}
        return [r("ARRANQUE", "R", 11796, 512),
                r("SELECIONA_TIME", "W", 1012641, 64)]

    def render(self, imagem: str) -> str:
        fora: list[str] = []
        A.secao_areas(fora.append, self.linhas(imagem), A.ler_offsets_hpp())
        return "\n".join(fora)

    def test_o_nome_vem_da_evidencia_e_nao_da_constante(self) -> None:
        texto = self.render("plantada.bin")
        self.assertIn("`roms/plantada.bin`", texto)
        self.assertNotIn(f"roms/{A.AREAS}", texto)


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


    def test_toda_linha_diz_de_que_sessao_veio(self) -> None:
        """A imagem nao basta como chave, e ja nao bastava.

        `06-diff-dirigido` e `06-truncada` rodam o mesmo roteiro com uma
        variavel trocada, e as sessoes 10 e 11 rodam sobre a MESMA imagem da
        09. Sem a coluna, as tres viram uma tabela so e a secao das areas passa
        a somar clique que ela nao mediu.
        """
        for r in self.medido:
            self.assertTrue(r.get("sessao"), f"linha sem sessao: {r}")
        sessoes = {r["sessao"] for r in self.medido}
        self.assertIn(A.AREAS, sessoes)
        for s in A.PASSAGEM_5:
            self.assertIn(s, sessoes)

    def test_toda_rom_citada_no_gerado_e_uma_imagem_medida(self) -> None:
        """Nome de ROM no `offsets-novos.md` tem de ser arquivo, nao rotulo.

        A conferencia e contra a coluna `imagem` do TSV, que e versionada --
        `roms/` e gitignored e pode nao estar no disco de quem roda a bateria.
        Quando ela esta, o arquivo tambem e conferido.
        """
        citadas = set(re.findall(r"`roms/([^`]+)`",
                                 A.OUT_MD.read_text(encoding="utf-8")))
        self.assertTrue(citadas, "o gerado deixou de citar imagem nenhuma")
        medidas = {r["imagem"] for r in self.medido}
        for nome in sorted(citadas):
            self.assertIn(nome, medidas,
                          f"`roms/{nome}` nao e imagem de sessao nenhuma")
            alvo = A.ROOT / "roms" / nome
            if (A.ROOT / "roms").is_dir() and not nome.startswith("truncada"):
                self.assertTrue(alvo.exists(), f"{alvo} nao existe")

    def test_toda_sessao_que_escreveu_tem_a_segunda_regua(self) -> None:
        """Escrita medida sem `cmp` versionado é evidência pela metade.

        A conferência das duas réguas é o que denunciou, três vezes, defeito
        silencioso do instrumento. Sem o TSV, um terceiro não a reconfere — e
        foi assim que as sessões 10 e 11, que levaram os endereçados de 15
        para 33, ficaram sem o número (CORR-WTE-047).
        """
        cmp_medido = A.ler_cmp_medido()
        self.assertTrue(cmp_medido, "cmp-medido.tsv vazio ou ausente")
        gerado = A.OUT_MD.read_text(encoding="utf-8")
        for v in A.veredito_das_reguas(self.medido, cmp_medido):
            self.assertTrue(v["tem_cmp"],
                            f"{v['sessao']} escreveu e não tem `cmp` "
                            f"versionado")
            self.assertEqual(v["dentro"], v["cmp"],
                             f"{v['sessao']}: {v['cmp'] - v['dentro']} faixa(s) "
                             f"do cmp fora das escritas do trace")
            self.assertIn(f"| `{v['sessao']}` | {v['cmp']} |", gerado,
                          f"{v['sessao']} não tem linha das duas réguas no "
                          f"markdown gerado")

    def test_toda_prova_de_retomada_casa_no_Database_cpp(self) -> None:
        """A coluna **prova** dos 50 tem de levar ao sitio certo.

        Ela dizia `case N` para os dois gatilhos, e em 3 das 14 linhas o fonte
        tem `if(i == N)`; num deles existia um `case 30 :` de verdade, noutro
        bloco (CORR-WTE-046). Aqui se confere o que o markdown afirma contra o
        fonte: a construcao citada esta na linha que ele diz, e o `Seek` do
        `OFS_*` esta na linha que ele diz.
        """
        fonte = A.DATABASE_CPP.read_text(encoding="utf-8").splitlines()
        linhas_md = A.OUT_MD.read_text(encoding="utf-8").splitlines()
        alvo = re.compile(
            r"^\| `(OFS_\w+)` \| \d+ \| retomada de fronteira "
            r"\| `([^`]+)` no `Database\.cpp`, `Seek` em :(\d+) \|")
        achados = [m for m in (alvo.match(l) for l in linhas_md) if m]
        self.assertEqual(len(achados), 14, "as 14 retomadas sumiram da tabela")
        for m in achados:
            nome, constr, n = m.group(1), m.group(2), int(m.group(3))
            self.assertIn(f"Seek({nome})", fonte[n - 1],
                          f"{nome}: a linha :{n} nao tem o Seek citado")
            janela = fonte[max(0, n - 1 - A.JANELA_BLOCO):n]
            self.assertTrue(any(constr in l for l in janela),
                            f"{nome}: `{constr}` nao esta nas {A.JANELA_BLOCO} "
                            f"linhas acima de :{n}")

    def test_todo_offset_ausente_tem_veredito(self) -> None:
        """O critério da WTE-TASK-19, preso em teste.

        Os 50 `ausente` da WTE-TASK-06 têm de estar todos resolvidos: ou o
        `wte.exe` os endereçou, ou o `Database.cpp` explica que eles não são
        endereço de campo. Um `OFS_*` que não caia em nenhum dos dois reabre a
        task — e é assim que se percebe, em vez de descobrir lendo o markdown.
        """
        conhecidos = A.ler_offsets_hpp()
        tocado = A.casar(self.faixas, conhecidos)
        papeis = A.papel_no_legado()
        ausentes = [r["nome"] for r in A.ler_offsets_tsv()
                    if r["registro"] == "ausente"]
        self.assertEqual(len(ausentes), 50)
        sem = [n for n in ausentes
               if n not in tocado
               and papeis.get(n, A.Papel("direto")).papel == "direto"]
        self.assertEqual(sem, [], f"sem veredito: {sem}")

    def test_a_regiao_do_uniforme_foi_medida(self) -> None:
        """O achado maior da 5ª passagem, e o insumo da WTE-TASK-29.

        Extrair a camisa lê 16 setores contíguos a 8 MB acima do maior offset
        que o `Offsets.hpp` conhece. Se isto sumir, ou a sessão 10 saiu da
        evidência, ou alguém nomeou a região sem reconferir o limite das duas
        tabelas — que é o aviso escrito no `offsets.md`.
        """
        teto = max(A.ler_offsets_hpp().values())
        uni = [f for f in self.faixas
               if f["acao"] == "EXTRAI_UNI" and int(f["inicio"]) > teto]
        self.assertGreaterEqual(len(uni), 16)

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
