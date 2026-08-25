#!/usr/bin/env python3
"""Testes do `compara_tela.py`: a deteccao de banda e a comparacao.

A deteccao erra em silencio de dois jeitos, e os dois ja aconteceram na
setima passagem da WTE-TASK-25: banda de sobra (o icone laranja do botao
"Sobre..." entrou na lista) e banda a menos. Nos dois casos o alinhamento entre
os cinco valores muda e a comparacao passa a confrontar barras diferentes --
divergencia falsa, ou pior, coincidencia que passa.

Tudo aqui roda contra imagens montadas em memoria: nao precisa do `.exe`, nem
do `:98`, nem de captura nenhuma.
"""

from __future__ import annotations

import unittest

import compara_tela as C

try:
    from PIL import Image
    TEM_PIL = True
except ImportError:                 # pragma: no cover
    TEM_PIL = False


def tela(bandas, altura_da_banda=12, x0=None, extras=()):
    """Imagem com as bandas pedidas, mais `extras` de `(y, largura, altura)`."""
    x0 = C.FAIXA_X[0] if x0 is None else x0
    alt = 10 + len(bandas) * 20 + 40
    img = Image.new("RGB", (C.FAIXA_X[1] + 20, alt), (0, 0, 128))
    for i, larg in enumerate(bandas):
        topo = 10 + i * 20
        for y in range(topo, topo + altura_da_banda):
            for x in range(x0, x0 + larg):
                img.putpixel((x, y), (255, 160, 0))
    for y0, larg, altura in extras:
        for y in range(y0, y0 + altura):
            for x in range(x0, x0 + larg):
                img.putpixel((x, y), (255, 160, 0))
    return img


@unittest.skipUnless(TEM_PIL, "sem PIL/Pillow")
class TestBandas(unittest.TestCase):
    def test_mede_as_cinco(self):
        img = tela([9, 20, 64, 75, 141])
        self.assertEqual(C.larguras(img, "x"), [9, 20, 64, 75, 141])

    def test_banda_baixa_demais_e_ignorada(self):
        """Artefato de 1 px de altura nao e barra."""
        img = tela([9, 20, 64, 75, 141], extras=[(0, 60, 1)])
        self.assertEqual(C.larguras(img, "x"), [9, 20, 64, 75, 141])

    def test_banda_estreita_demais_e_ignorada(self):
        """O icone do botao `Sobre...`: alto o bastante, estreito demais.

        Foi o que fez a primeira medicao achar seis bandas onde ha cinco.
        """
        img = tela([9, 20, 64, 75, 141], extras=[(0, 3, 8)])
        self.assertEqual(C.larguras(img, "x"), [9, 20, 64, 75, 141])

    def test_barra_vazia_de_9px_conta(self):
        """9 px e `11*0 + 9` -- barra zerada, nao ruido. O limite e >=, e a
        diferenca entre medir o time sem forca e nao o medir."""
        img = tela([9, 9, 9, 9, 9])
        self.assertEqual(C.larguras(img, "x"), [9, 9, 9, 9, 9])

    def test_camisa_encostando_na_faixa_nao_engorda_a_barra(self):
        """A camisa do `ml_teams[22]` entrava na conta da barra `equipe`.

        Para `indice > 62` o `home1` vai para `Left = 7, Width = 100` e comeca
        em `x = 223`, dentro da `FAIXA_X`. Medido em 2026-08-23, a faixa
        diagonal da camisa do `EMILIA` toca `x = 229` em tres linhas da banda
        da terceira barra, e a soma por linha devolvia 76 -- que nao e
        `11*v + 9` para nenhum `v`. Medindo o trecho contiguo, sao os 75 px da
        barra, e o oraculo volta para a grade.
        """
        img = tela([9, 20, 64, 75, 141])
        alvo = 10 + 3 * 20                      # o topo da quarta banda, de 75
        for y in range(alvo + 4, alvo + 7):
            img.putpixel((C.FAIXA_X[1] - 1, y), (255, 160, 0))
        self.assertEqual(C.larguras(img, "x"), [9, 20, 64, 75, 141])

    def test_contagem_errada_aborta(self):
        img = tela([64, 75, 75])
        with self.assertRaises(C.TelaError) as e:
            C.larguras(img, "oraculo")
        self.assertIn("achei 3 banda(s)", str(e.exception))


@unittest.skipUnless(TEM_PIL, "sem PIL/Pillow")
class TestCompara(unittest.TestCase):
    def test_iguais_passam(self):
        a = tela([64, 53, 75, 75, 75])
        m = C.compara(a, tela([64, 53, 75, 75, 75]), 2)
        self.assertEqual(m["diferencas"], [])

    def test_diferenca_e_nomeada_pela_barra(self):
        m = C.compara(tela([64, 53, 75, 75, 75]),
                      tela([64, 53, 75, 86, 75]), 2)
        self.assertEqual(len(m["diferencas"]), 1)
        self.assertEqual(m["diferencas"][0]["barra"], "velocidade")
        self.assertEqual(m["diferencas"][0]["oraculo"], 75)
        self.assertEqual(m["diferencas"][0]["port"], 86)

    def test_valor_do_jogo_e_a_inversa_da_largura(self):
        self.assertEqual(C.valor_da_barra(9), 0)
        self.assertEqual(C.valor_da_barra(64), 5)
        self.assertEqual(C.valor_da_barra(141), 12)

    def test_largura_que_nao_fecha_em_inteiro_nao_vira_valor(self):
        """104 px e o caso real do time 63. Barra do jogo e inteira, entao
        `8,64` seria afirmar o que nao se mediu -- devolve None."""
        self.assertIsNone(C.valor_da_barra(104))

    def test_autoteste_do_check_passa(self):
        self.assertEqual(C.autoteste(), 0)


def janela(mudam=(), off=(0, 0), altura=475, largura=522):
    """Uma janela de mentira, com a ancora `barra0` no lugar certo.

    `mudam` sao nomes de `CONTROLES` cujo retangulo sai pintado de outra cor --
    e assim que se planta "este controle mudou de aparencia".
    """
    img = Image.new("RGB", (largura + off[0], altura + off[1]), (200, 200, 200))
    ax, ay = C.ANCORA[0] + off[0], C.ANCORA[1] + off[1]
    for y in range(ay, ay + 13):                    # a ancora: barra0, 64 px
        for x in range(ax, ax + 64):
            img.putpixel((x, y), (255, 160, 0))
    for nome in mudam:
        x, y, w, h, _g = C.CONTROLES[nome]
        for yy in range(y + off[1], y + off[1] + h):
            for xx in range(x + off[0], x + off[0] + w):
                img.putpixel((xx, yy), (10, 10, 10))
    return img


@unittest.skipUnless(TEM_PIL, "sem PIL/Pillow")
class TestCalibracao(unittest.TestCase):
    def test_oraculo_sem_deslocamento(self):
        self.assertEqual(C.calibra(janela(), "x"), (0, 0))

    def test_port_deslocado_de_seis(self):
        """O caso real: o gtk2 desenha uma borda que o Wine nao desenha."""
        self.assertEqual(C.calibra(janela(off=(6, 6)), "x"), (6, 6))

    def test_sem_ancora_aborta(self):
        img = Image.new("RGB", (522, 475), (200, 200, 200))
        with self.assertRaises(C.TelaError) as e:
            C.calibra(img, "port")
        self.assertIn("ancora", str(e.exception))


@unittest.skipUnless(TEM_PIL, "sem PIL/Pillow")
class TestCobertura(unittest.TestCase):
    def test_janela_inteira_cobre_os_dorsais(self):
        C.confere_cobertura(janela(), "x", (0, 0))      # nao levanta

    def test_recorte_de_240_reprova(self):
        """O defeito da CORR-WTE-057: dois dos cinco grupos fora do recorte."""
        with self.assertRaises(C.TelaError) as e:
            C.confere_cobertura(janela(altura=240), "oraculo", (0, 0))
        self.assertIn("dorsal1..23", str(e.exception))

    def test_o_deslocamento_do_port_entra_na_conta(self):
        """452 px de altura bastam sem deslocamento e nao bastam com ele."""
        C.confere_cobertura(janela(altura=452), "oraculo", (0, 0))
        with self.assertRaises(C.TelaError):
            C.confere_cobertura(janela(altura=446, off=(6, 6)), "port", (6, 6))


@unittest.skipUnless(TEM_PIL, "sem PIL/Pillow")
class TestHabilitacao(unittest.TestCase):
    SEGUE = [n for n, r in C.CONTROLES.items() if r[4] == "segue_nacional"]
    # Os tres do render 2D. Ate 2026-08-25 esta lista se derivava do grupo
    # `pendente_32`, que os isentava de reprovar; com o grupo removido ela
    # virou vazia em silencio, e o teste da bandeira passou a nao medir
    # nada. Lista derivada da tabela sob teste nao guarda a tabela --
    # agora os nomes vem do `RENDER` do modulo, que e o proprio conjunto.
    P32 = list(C.RENDER)
    CINZA = [n for n, r in C.CONTROLES.items() if r[4] == "glifo_cinza"]

    def r(self, muda_orac, muda_port, off_port=(6, 6)):
        return C.compara_habilitacao(
            janela(), janela(off=off_port),
            janela(mudam=muda_orac), janela(mudam=muda_port, off=off_port))

    def test_os_dois_lados_mudando_o_mesmo_conjunto_passam(self):
        r = self.r(self.SEGUE + self.P32, self.SEGUE + self.P32)
        self.assertEqual(r["erros"], [])
        self.assertEqual(C.relata_habilitacao(r), 0)

    def test_port_que_esquece_um_controle_reprova(self):
        r = self.r(self.SEGUE + self.P32,
                   [n for n in self.SEGUE if n != "colorear"] + self.P32)
        self.assertEqual(len(r["erros"]), 1)
        self.assertIn("colorear", r["erros"][0])

    def test_rotulo_que_segue_o_campo_reprova(self):
        """`etiq_nombre1..3` ficam ligados SEMPRE -- assimetria medida."""
        r = self.r(self.SEGUE + self.P32 + ["etiq_nombre1"],
                   self.SEGUE + self.P32 + ["etiq_nombre1"])
        self.assertEqual(len(r["erros"]), 1)
        self.assertIn("etiq_nombre1", r["erros"][0])
        self.assertIn("incondicional", r["erros"][0])

    def test_glifo_invariante_muda_so_no_oraculo_e_nao_reprova(self):
        """CORR-WTE-060: a LCL nao consegue acinzentar glifo preto-e-branco.

        O `.Enabled := nacional` roda dos dois lados; o que nao aparece e o
        desenho, porque `gdeDisabled` e grayscale e pixel com R=G=B e ponto
        fixo dela. Divergencia deliberada da WTE-TASK-35, e por isso a regua
        relata sem reprovar -- como ja fazia com a bandeira.
        """
        r = self.r(self.SEGUE + self.P32 + self.CINZA, self.SEGUE + self.P32)
        self.assertEqual(r["erros"], [])
        v = {l["nome"]: l["veredito"] for l in r["linhas"]}
        self.assertEqual(v["iguala_nombres"],
                         "divergencia deliberada (WTE-TASK-35)")

    def test_glifo_invariante_mudando_dos_dois_lados_tambem_passa(self):
        """Se um dia a LCL passar a acinzentar, o relato vira `bate`."""
        r = self.r(self.SEGUE + self.P32 + self.CINZA,
                   self.SEGUE + self.P32 + self.CINZA)
        self.assertEqual(r["erros"], [])
        v = {l["nome"]: l["veredito"] for l in r["linhas"]}
        self.assertEqual(v["iguala_nombres"], "bate")

    def test_bandeira_so_de_um_lado_REPROVA(self):
        """O contrario do que este teste exigia ate 2026-08-25.

        Ele travava a isencao `pendente_32`, com a premissa escrita no proprio
        docstring: *"desenhar a bandeira e da WTE-TASK-29, e ela ainda nao
        chegou"*. Ela chegou -- e as CORR-WTE-083/-084 ainda consertaram a
        bandeira preta de dez times. Medido pela WTE-TASK-35 em 2026-08-25, os
        tres controles do grupo BATEM, com numeros identicos dos dois lados:
        3840/3840, 2328/2328 e 1012/1012.

        Isencao que sobrevive a propria causa nao protege nada -- ela esconde a
        regressao seguinte. Entao o grupo saiu, os tres voltaram para
        `segue_nacional`, e o que este teste prende agora e a direcao oposta:
        bandeira que mude de um lado so REPROVA.
        """
        # `SEGUE` passou a CONTER os tres, entao "so de um lado" agora se
        # escreve tirando-os do lado port -- somar `P32` de um lado so
        # nao muda mais nada.
        so_port = [n for n in self.SEGUE if n not in self.P32]
        r = self.r(self.SEGUE, so_port)
        self.assertTrue(r["erros"], "bandeira divergindo tem de reprovar")
        self.assertTrue(any("bandera" in e for e in r["erros"]), r["erros"])
        v = {l["nome"]: l["veredito"] for l in r["linhas"]}
        self.assertEqual(v["bandera"], "DIVERGE")

    def test_campo_de_texto_nao_e_medido(self):
        r = self.r(self.SEGUE + self.P32, self.SEGUE + self.P32)
        v = {l["nome"]: l["veredito"] for l in r["linhas"]}
        self.assertEqual(v["edit_nombre1"], "olho humano")

    def test_controle_abaixo_da_faixa_nao_e_medido(self):
        """A deriva do port chega a 21 px em y 432 -- ali a regua nao vale."""
        r = self.r(self.SEGUE + self.P32, self.SEGUE + self.P32)
        v = {l["nome"]: l["veredito"] for l in r["linhas"]}
        self.assertEqual(v["mostrar_jugador_1"], "olho humano (deriva do port)")

    def test_medir_abaixo_da_faixa_aborta(self):
        rect = C.CONTROLES["parriba"]
        C.CONTROLES["parriba"] = rect[:4] + ("sempre_ligado",)
        self.addCleanup(C.CONTROLES.__setitem__, "parriba", rect)
        with self.assertRaises(C.TelaError) as e:
            C.confere_faixa()
        self.assertIn("parriba", str(e.exception))

    def test_nenhum_lado_mudando_reprova_contra_a_spec(self):
        """Os tres do render entraram na conta em 2026-08-25.

        Enquanto eram `pendente_32` ficavam fora: o grupo nunca reprovava. Como
        `segue_nacional`, um `bandera` que nao muda de lado nenhum passou a
        contrariar a spec como qualquer outro -- e a contagem subiu de 9 para
        12 sozinha, que e o sinal de que a isencao de fato saiu.
        """
        nada = []
        r = self.r(nada, nada)
        self.assertEqual(len(r["erros"]), len(self.SEGUE))
        self.assertEqual(len(self.SEGUE), 12)
        self.assertIn("a spec diz", r["erros"][0])


if __name__ == "__main__":
    unittest.main()


@unittest.skipUnless(TEM_PIL, "sem PIL/Pillow")
class TestContraODump(unittest.TestCase):
    """A terceira ponta: tela -> valor -> camada de dados."""

    def dump(self, valores, indice=2, tmp=None):
        import tempfile, os
        prefixo = ("teams[%d]." % indice if indice < C.TIMES_NACIONAIS
                   else "ml_teams[%d]." % (indice - C.TIMES_NACIONAIS))
        linhas = [f"{prefixo}{c} = {v}"
                  for c, v in zip(C.CHAVES_DA_BARRA, valores)]
        fd, caminho = tempfile.mkstemp(suffix=".txt")
        os.write(fd, ("\n".join(linhas) + "\n").encode())
        os.close(fd)
        self.addCleanup(os.unlink, caminho)
        from pathlib import Path as P
        return P(caminho)

    def test_bate_com_o_dado(self):
        larg = [11 * v + 9 for v in (5, 4, 6, 6, 6)]
        m = C.compara(tela(larg), tela(larg), 2)
        r = C.confere_contra_dump(m, self.dump([5, 4, 6, 6, 6]))
        self.assertEqual(r, {"erros": [], "curtas": []})

    def test_dado_diferente_reprova(self):
        larg = [11 * v + 9 for v in (5, 4, 6, 6, 6)]
        m = C.compara(tela(larg), tela(larg), 2)
        r = C.confere_contra_dump(m, self.dump([5, 4, 6, 6, 7]))
        self.assertEqual(r["curtas"], [])
        self.assertEqual(len(r["erros"]), 1)
        self.assertIn("tecnica", r["erros"][0])

    def test_curta_dentro_da_folga_nao_e_erro(self):
        """O caso real do time 63: dado 9 previa 108 px, os dois medem 104.

        E a cauda do degrade fora do teste de cor, nao o port errando -- e
        reprovar seria acusar o port de um limite que o original tem igual.
        """
        larg = [104, 75, 97, 97, 97]
        m = C.compara(tela(larg), tela(larg), 63)
        r = C.confere_contra_dump(m, self.dump([9, 6, 8, 8, 8], indice=63))
        self.assertEqual(r["erros"], [])
        self.assertEqual(len(r["curtas"]), 1)
        self.assertIn("cauda do degrade", r["curtas"][0])

    def test_menor_que_o_previsto_mas_diferente_entre_os_lados_e_erro(self):
        """A folga so vale quando os dois lados medem o MESMO menor."""
        m = C.compara(tela([104, 75, 97, 97, 97]),
                      tela([97, 75, 97, 97, 97]), 63)
        r = C.confere_contra_dump(m, self.dump([9, 6, 8, 8, 8], indice=63))
        self.assertEqual(len(r["erros"]), 1)
        self.assertEqual(r["curtas"], [])

    def test_indice_de_ml_le_o_vetor_certo(self):
        caminho = self.dump([9, 6, 8, 8, 8], indice=63)
        self.assertEqual(C.le_dump(caminho, 63), [9, 6, 8, 8, 8])

    def test_dump_sem_a_chave_aborta(self):
        caminho = self.dump([5, 4, 6, 6, 6], indice=2)
        with self.assertRaises(C.TelaError) as e:
            C.le_dump(caminho, 7)
        self.assertIn("nao traz", str(e.exception))


def com_nomes(larguras, off=(0, 0)):
    """Uma janela de mentira com tinta de largura dada em cada campo de nome.

    A tinta e desenhada DENTRO da borda, no mesmo recuo que a medicao aplica --
    caso contrario o teste passaria medindo a moldura, que foi exatamente o
    defeito da primeira versao da regua.
    """
    img = janela(off=off)
    rects = C.retangulos_do_lfm(C.CAMPOS_DE_NOME)
    for nome, w in zip(C.CAMPOS_DE_NOME, larguras):
        x, y, cw, ch = rects[nome]
        x += off[0] + C.BORDA
        y += off[1] + C.BORDA
        for yy in range(y, y + ch - 2 * C.BORDA):      # o fundo do campo
            for xx in range(x, x + cw - 2 * C.BORDA):
                img.putpixel((xx, yy), (255, 253, 240))
        # A tinta e desenhada esparsa, como glifo de verdade: uma coluna a
        # cada tres. Bloco solido faria o preto ser a cor mais frequente do
        # campo estreito e a medida se inverteria -- que e o modo de falha que
        # o `tinta()` agora recusa.
        for yy in range(y + 2, y + 12):
            for xx in range(x, x + w):
                if xx in (x, x + w - 1) or (xx - x) % 3 == 0:
                    img.putpixel((xx, yy), (0, 0, 0))
    return img


@unittest.skipUnless(TEM_PIL, "sem PIL/Pillow")
class TestNomes(unittest.TestCase):
    def test_os_retangulos_saem_do_lfm(self):
        """Lidos, nao digitados -- e o `edit_nombre3` prova por que.

        Ele tem 33 px de largura contra os 113 dos outros dois. A primeira
        versao trazia os quatro numeros de cada campo escritos a mao, com 113
        nos tres, e a regua media a moldura de um campo que nao existia daquele
        tamanho.
        """
        r = C.retangulos_do_lfm(C.CAMPOS_DE_NOME)
        self.assertEqual(r["edit_nombre1"][2], 113)
        self.assertEqual(r["edit_nombre3"][2], 33)

    def test_mede_a_tinta_e_nao_a_moldura(self):
        m = C.compara_nomes(com_nomes((31, 41, 22)), com_nomes((31, 41, 22)))
        larg = [m["medida"]["port"][n][0] for n in C.CAMPOS_DE_NOME]
        self.assertEqual(larg, [31, 41, 22])
        self.assertEqual(m["erros"], [])

    def test_diferenca_de_um_glifo_reprova(self):
        """10 px e um caractere a mais: foi a divergencia real de 2026-08-18."""
        m = C.compara_nomes(com_nomes((31, 41, 22)), com_nomes((41, 41, 22)))
        self.assertTrue(any("edit_nombre1" in e for e in m["erros"]), m["erros"])

    def test_tremor_de_renderizacao_passa(self):
        """1 px de diferenca e fonte, nao filtro -- foi o que os dois lados
        deram quando concordavam."""
        m = C.compara_nomes(com_nomes((31, 41, 22)), com_nomes((32, 41, 22)))
        self.assertEqual(m["erros"], [])

    def test_campo_vazio_reprova(self):
        m = C.compara_nomes(com_nomes((0, 41, 22)), com_nomes((0, 41, 22)))
        self.assertTrue(any("sem texto" in e for e in m["erros"]), m["erros"])

    def test_tinta_em_toda_a_largura_reprova(self):
        """A guarda que faltava: moldura contada como tinta da largura cheia.

        Sem ela os tres campos saiam com largura igual a do proprio campo, nos
        dois lados, e o veredito lia isso como concordancia.
        """
        r = C.retangulos_do_lfm(C.CAMPOS_DE_NOME)
        cheio = r["edit_nombre1"][2] - 2 * C.BORDA
        m = C.compara_nomes(com_nomes((cheio, 41, 22)), com_nomes((cheio, 41, 22)))
        self.assertTrue(any("largura util" in e for e in m["erros"]), m["erros"])

    def test_a_calibracao_e_aplicada(self):
        """Com o port deslocado, a medida tem de ser a mesma."""
        m = C.compara_nomes(com_nomes((31, 41, 22)),
                            com_nomes((31, 41, 22), off=(6, 6)))
        self.assertEqual(m["erros"], [])



# ------------------------------------------------- a grade de cores (29) --
# O modo `--grade` mede DEPOIS de editar, e por isso ele tem uma pre-condicao
# que os outros modos nao tem: a cor precisa ter mudado. Estes testes exercitam
# essa guarda -- que e a que separa "os dois lados concordam" de "os dois lados
# ficaram parados e portanto concordam".

def com_amostras(cores, off=(0, 0)):
    """A janela do MODAL de mentira, com as 16 amostras pintadas de `cores`.

    Ela nao passa pela `janela()` acima por dois motivos: o `ficha_color` tem
    542x225 de cliente, mais largo que a janela principal de mentira, e a
    comparacao de amostra NAO calibra por ancora -- a captura ja e a janela do
    editor, e o `.lfm` dele da as coordenadas relativas a ela.

    O recorte da medida encolhe `AMOSTRA_MARGEM` de cada lado, entao a tinta e
    desenhada no retangulo inteiro: assim a margem tira moldura de verdade e
    nao a propria cor.
    """
    img = Image.new("RGB", (560 + off[0], 240 + off[1]), (200, 200, 200))
    rects = C.retangulos_do_lfm(C.AMOSTRAS, C.LFM_COLOR)
    for nome, cor in zip(C.AMOSTRAS, cores):
        x, y, w, h = rects[nome]
        for yy in range(y + off[1], y + off[1] + h):
            for xx in range(x + off[0], x + off[0] + w):
                img.putpixel((xx, yy), cor)
    return img


def rampa(n=16, base=0):
    """16 cores distintas, para a guarda de "todas iguais" nao disparar."""
    return [(base + 8 * i, base + 8 * i, base + 8 * i) for i in range(n)]


@unittest.skipUnless(TEM_PIL, "sem PIL/Pillow")
class TestGrade(unittest.TestCase):
    def test_mudou_acha_a_amostra_trocada(self):
        rects = C.retangulos_do_lfm(C.AMOSTRAS, C.LFM_COLOR)
        antes = com_amostras(rampa())
        cores = rampa()
        cores[4] = (1, 2, 3)
        depois = com_amostras(cores)
        self.assertEqual(
            C.mudou(antes, depois, C.AMOSTRAS, rects, C.AMOSTRA_MARGEM),
            ["color5"])

    def test_mudou_nao_ve_a_moldura(self):
        """A margem tem de tirar a borda: uma diferenca so nela nao e cor."""
        rects = C.retangulos_do_lfm(C.AMOSTRAS, C.LFM_COLOR)
        antes = com_amostras(rampa())
        depois = com_amostras(rampa())
        x, y, w, h = rects["color3"]
        for xx in range(x, x + w):                     # a linha de cima inteira
            depois.putpixel((xx, y), (255, 0, 0))
        self.assertEqual(
            C.mudou(antes, depois, C.AMOSTRAS, rects, C.AMOSTRA_MARGEM), [])

    def test_tela_parada_nao_e_concordancia(self):
        """A guarda central: sem edicao, os dois lados batem e o veredito e
        REPROVOU, e nao PASSOU.

        Este e o modo de falha que o `--cor` sozinho nao pega -- se os cliques
        nao chegarem em botao nenhum, as duas capturas ficam identicas e a
        comparacao pixel a pixel sai verde sem ter medido conta nenhuma.
        """
        rects = C.retangulos_do_lfm(C.AMOSTRAS, C.LFM_COLOR)
        parada = com_amostras(rampa())
        self.assertEqual(
            len(C.mudou(parada, parada, C.AMOSTRAS, rects, C.AMOSTRA_MARGEM)),
            0)
        self.assertLess(0, C.GRADE_MINIMO,
                        "o piso tem de ser maior que zero, senao a guarda "
                        "aceita a tela parada")

    def test_a_guarda_de_cores_distintas_continua_valendo(self):
        """Heranca do `--cor`: 16 amostras da mesma cor reprovam."""
        r = C.compara_cor(com_amostras([(9, 9, 9)] * 16),
                          com_amostras([(9, 9, 9)] * 16))
        self.assertEqual(C.relata_cor(r, 2), 1)

    def test_amostras_distintas_e_iguais_dos_dois_lados_passa(self):
        r = C.compara_cor(com_amostras(rampa()), com_amostras(rampa()))
        self.assertEqual(C.relata_cor(r, 2), 0)
