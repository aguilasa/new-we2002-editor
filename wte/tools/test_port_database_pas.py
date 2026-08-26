#!/usr/bin/env python3
"""Testes do port_database_pas.py -- WTE-TASK-17 e 18.

O criterio da 17 e explicito: **"recusa testada com entrada plantada, nao so
com a entrada boa"**. Um guard que nunca foi visto recusar e um guard que se
supoe funcionar. A 18 acrescenta o passe estrutural, e com ele o unico gate que
mede de verdade: **o fpc compila as seis unidades**, e um programa Pascal prova
as cinco decisoes de `wte/re/tipos.md` contra a camada gerada.

Grupos:

1. `FORBIDDEN` -- cada construcao sem traducao decidida recusa, com a linha
   certa.
2. `check_seeks()` -- uma regra de `SUBS` que troca a direcao de um seek e
   pega, mesmo produzindo Pascal que compilaria. Este guard existe por causa de
   um bug real, e o teste reproduz o bug.
3. O que **nao** pode recusar: comentario e literal nao sao codigo.
4. O passe estrutural -- bloco, `for`, `switch`, `[[fallthrough]]`, hoisting.
5. As seis unidades compilando, e as decisoes de tipo provadas em execucao.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import port_database_pas as P


def motivos(notas) -> str:
    return " | ".join(n.motivo for n in notas)


class TestForbidden(unittest.TestCase):
    """Entrada plantada: cada construcao proibida tem de aparecer."""

    def conferir(self, fonte: str):
        traduzido, _ = P.aplicar_subs(fonte)
        return P.conferir(P.FORBIDDEN, traduzido, "plantado.cpp")

    def test_conteiner_da_stl(self) -> None:
        notas = self.conferir("std::vector<int> v;\n")
        self.assertIn("conteiner da STL", motivos(notas))

    def test_lambda(self) -> None:
        self.assertIn("lambda", motivos(self.conferir("auto f = [](int x) {};\n")))

    def test_reinterpret_cast(self) -> None:
        notas = self.conferir("auto* p = reinterpret_cast<char*>(q);\n")
        self.assertIn("reinterpret_cast", motivos(notas))

    def test_goto(self) -> None:
        self.assertIn("goto", motivos(self.conferir("goto fim;\n")))

    def test_fallthrough(self) -> None:
        notas = self.conferir("case 1:\n\tf();\n\t[[fallthrough]];\ndefault:\n")
        self.assertIn("fallthrough", motivos(notas))

    def test_sizeof(self) -> None:
        self.assertIn("sizeof", motivos(self.conferir("int n = sizeof(T);\n")))

    def test_ternario(self) -> None:
        notas = self.conferir("int n = a ? b : c;\n")
        self.assertIn("ternario", motivos(notas))

    def test_compilacao_condicional(self) -> None:
        notas = self.conferir("#ifdef _WIN32\nint x;\n#endif\n")
        self.assertIn("compilacao condicional", motivos(notas))

    def test_a_linha_reportada_e_a_real(self) -> None:
        notas = self.conferir("int a;\nint b;\ngoto fim;\n")
        self.assertEqual([n.linha for n in notas if "goto" in n.motivo], [3])

    def test_seta_que_sobrou_e_recusa(self) -> None:
        # `->` depois da traducao so existe se uma regra de SUBS falhou. E uma
        # rede: sem ela, `p->campo` viraria `p->campo` no Pascal, que nao
        # compila -- mas so descobriríamos no fpc, longe daqui.
        notas = P.conferir(P.FORBIDDEN, "x := p->campo;\n", "plantado.cpp")
        self.assertIn("'->' sobrou", motivos(notas))

    def test_statement_traduzivel_nao_recusa(self) -> None:
        # Um statement dentro do subconjunto passa limpo. Estrutura (`for`,
        # chaves) e outra conversa -- ver TestEstruturaAindaRecusa.
        fonte = "\timage_file.Read(&teams[i].flag_shape, 1);\n"
        self.assertEqual(self.conferir(fonte), [])


class TestPasseEstrutural(unittest.TestCase):
    """O passe da WTE-TASK-18: bloco, laco, `switch`, hoisting.

    Achado da WTE-TASK-17 que redimensionou a 18: o `tools/port_database.py`
    pode ser substituicao textual pura porque fonte e alvo sao a MESMA
    linguagem. C++ -> Pascal nao pode -- bloco, cabecalho de laco, assinatura e
    declaracao de variavel nao tem forma comum.
    """

    def traduzir(self, corpo: str, funcao: str = "F", ret: str = "void"):
        tp = P.Transpilador("u", [("x.cpp", "")])
        tp.campos = {}
        c = P.Corpo(tp, P.normalizar(corpo), funcao, ret)
        linhas, _ = c.statements(0, 0)
        return "\n".join(linhas), c.vars, tp.notas

    def test_bloco_vira_begin_end(self) -> None:
        pas, _, notas = self.traduzir("{\n\tf(1);\n}\n")
        self.assertIn("begin", pas)
        self.assertIn("end;", pas)
        self.assertEqual(notas, [])

    def test_for_de_passo_um_vira_for_to_do(self) -> None:
        pas, _, _ = self.traduzir("for(i = 0;i < 32;i ++)\n{\n\tf(i);\n}\n")
        self.assertIn("for i := 0 to 31 do", pas)

    def test_o_limite_nao_literal_sai_menos_um(self) -> None:
        pas, _, _ = self.traduzir("for(i=0;i<PLAYERS_NC;i++)\n\tf(i);\n")
        self.assertIn("for i := 0 to PLAYERS_NC - 1 do", pas)

    def test_for_vira_while_quando_o_corpo_atribui_a_variavel(self) -> None:
        # Database.cpp:762 faz `i = 1750;` dentro do laco. Em Pascal atribuir a
        # variavel de controle de um `for` e PROIBIDO -- e o `for..to..do`
        # ignoraria o salto, lendo 46 custos que o original pula.
        pas, _, _ = self.traduzir(
            "for(i=0;i<10;i++)\n{\n\tif(i == 3)\n\t{\n\t\ti = 7;\n\t}\n"
            "\tf(i);\n}\n")
        self.assertIn("while i < 10 do", pas)
        self.assertIn("Inc(i);", pas)
        self.assertNotIn("for i :=", pas)

    def test_for_vira_while_quando_a_variavel_e_lida_depois(self) -> None:
        # TextCodec.cpp:42 le `i` DEPOIS do laco. Em Pascal o valor da variavel
        # de controle depois de um `for` e indefinido pela linguagem.
        pas, _, _ = self.traduzir(
            "for(i = 0;i < l;i++)\n{\n\tf(i);\n}\nkj[i] = 0;\n")
        self.assertIn("while i < l do", pas)

    def test_for_seguinte_reinicializando_nao_conta_como_leitura(self) -> None:
        # A condicao `i < 63` do proximo `for` LE `i`, mas o init reinicializa
        # antes. Sem esta distincao metade dos lacos do Load viraria `while`.
        pas, _, _ = self.traduzir(
            "for(i = 0;i < 32;i++)\n\tf(i);\nfor(i = 0;i < 63;i++)\n\tg(i);\n")
        self.assertNotIn("while", pas)
        self.assertEqual(pas.count("for i :="), 2)

    def test_passo_diferente_de_um_vira_while(self) -> None:
        pas, _, _ = self.traduzir("for (i = 0; i < l; i += 2)\n\tf(i);\n")
        self.assertIn("while i < l do", pas)
        self.assertIn("Inc(i, 2);", pas)

    def test_declaracao_vira_bloco_var(self) -> None:
        _, variaveis, _ = self.traduzir(
            "int i,j;\nunsigned short colour_buf[16];\n",
            funcao="Database::Load")
        self.assertIn("i: LongInt;", variaveis)
        self.assertIn("j: LongInt;", variaveis)
        self.assertIn("colour_buf: array[0..15] of Word;", variaveis)

    def test_char_local_sem_classificacao_recusa(self) -> None:
        # A decisao 4 de tipos.md separa `char` de TEXTO de `char` NUMERICO, e
        # heuristica erra em silencio: o erro so apareceria na tela do usuario.
        _, _, notas = self.traduzir("char scratch[8];\n", funcao="Naoexiste")
        self.assertIn("CHAR_LOCAL", " ".join(n.motivo for n in notas))

    def test_switch_vira_case(self) -> None:
        pas, _, _ = self.traduzir(
            "switch(i)\n{\n\tcase 1:\n\t\tf();\n\t\tbreak;\n"
            "\tdefault:\n\t\tg();\n}\n")
        self.assertIn("case i of", pas)
        self.assertIn("1:", pas)
        self.assertIn("else", pas)
        self.assertNotIn("Break;", pas)   # `break;` de switch nao e Break

    def test_fallthrough_duplica_o_ramo_seguinte(self) -> None:
        # O `case` do Pascal NAO cai para o proximo ramo. Traduzir literalmente
        # mudaria em silencio QUANTOS bytes se le da imagem.
        pas, _, _ = self.traduzir(
            "switch(i)\n{\n\tcase 1:\n\t\tSeekCurrent(32);\n"
            "\t[[fallthrough]];\n\tdefault:\n\t\tRead(x, 32);\n}\n")
        self.assertNotIn("fallthrough]];", pas)
        self.assertEqual(pas.count("Read(x, 32);"), 2, pas)
        self.assertIn("PORTE A MAO (rota 1)", pas)

    def test_atribuicao_encadeada_e_decomposta(self) -> None:
        pas, _, _ = self.traduzir("buf[0] = buf[1] = 0;\n")
        self.assertIn("buf[1] := 0;", pas)
        self.assertIn("buf[0] := buf[1];", pas)

    def test_return_vira_result_e_exit(self) -> None:
        pas, _, _ = self.traduzir("return false;\n", ret="bool")
        self.assertIn("Result := false;", pas)
        self.assertIn("Exit;", pas)


class TestSaidaReal(unittest.TestCase):
    """As seis unidades saem, sem recusa, e com a forma que o Pascal exige."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.saida = {}
        cls.notas = {}
        cls.duplicados = {}
        for unit, arquivos in P.UNITS:
            pas, notas = P.transpilar_unidade(unit, arquivos)
            cls.saida[unit] = pas
            cls.notas[unit] = notas
            cls.duplicados[unit] = list(P.ULTIMO_TRANSPILADOR.duplicados)

    def test_nenhuma_recusa_em_aberto(self) -> None:
        for unit, notas in self.notas.items():
            self.assertEqual([str(n) for n in notas], [], unit)

    def test_as_seis_unidades_existem_no_disco(self) -> None:
        for unit, _ in P.UNITS:
            self.assertTrue((P.OUT_DIR / f"{unit}.pas").exists(), unit)

    def test_nada_de_c_sobrou(self) -> None:
        for unit, pas in self.saida.items():
            for proibido in ("std::", "->", "&&", "0x", "static_cast"):
                self.assertNotIn(proibido, P.mascarar(pas, pascal=True), unit)

    def test_a_contagem_de_io_bate_com_a_entrada(self) -> None:
        """`Read`/`Write`/`strcpy` nao podem sumir nem se multiplicar.

        O `check_seeks()` ja cuida dos seeks. Estes tres sao o resto do que
        toca a imagem: um `Read` a menos e um campo que nunca se carrega, e um
        a mais desalinha TODO o resto do fluxo -- os offsets sao relativos.
        """
        fonte = (P.CORE / "Database.cpp").read_text(encoding="utf-8")
        pas = self.saida["we2002_database"]
        extra = "\n".join(self.duplicados["we2002_database"])
        self.assertTrue(extra, "nenhum ramo duplicado: o [[fallthrough]] sumiu")
        for c, p in ((r"\.Read\(", r"\.Read\("),
                     (r"\.Write\(", r"\.Write\("),
                     (r"\bstrcpy\b", r"\bCStrCopy\b"),
                     (r"\bstrcat\b", r"\bCStrCat\b")):
            # O `[[fallthrough]]` DUPLICA o ramo seguinte de proposito -- e a
            # rota 1 da WTE-TASK-18. A diferenca tem de ser exatamente essa.
            self.assertEqual(len(re.findall(c, fonte)) + len(re.findall(p, extra)),
                             len(re.findall(p, pas)), f"{c} nao bate")

    def test_o_literal_de_erro_atravessa_intacto(self) -> None:
        """A regra `!` -> `not` NAO pode entrar em literal.

        Achado da WTE-TASK-18: sem `_proteger()`, a mensagem
        `"Error ! Impossible to open CD image !"` saia como
        `'Error not Impossible to open CD image !'` -- texto que o usuario le,
        corrompido por uma regra de operador.
        """
        pas = self.saida["we2002_database"]
        self.assertIn("'Error ! Impossible to open CD image !'", pas)
        self.assertNotIn("Error not Impossible", pas)

    def test_o_trecho_portado_a_mao_virou_chamada(self) -> None:
        pas = self.saida["we2002_database"]
        self.assertIn("WriteUrlSidecar(image);", pas)
        # Mascarado: o comentario do porte a mao CITA o std::ofstream que ele
        # substitui, e citacao nao e codigo.
        self.assertNotIn("ofstream", P.mascarar(pas, pascal=True))

    def test_o_parametro_reservado_foi_renomeado(self) -> None:
        # `as` e operador de type-cast no Object Pascal. Sem renomear, o corpo
        # inteiro do AsciiToKanji deixa de compilar com erro que nao menciona o
        # nome.
        pas = self.saida["we2002_textcodec"]
        self.assertIn("as_: PByte", pas)
        self.assertNotIn("as[i]", pas)


class TestCheckSeeks(unittest.TestCase):
    """O guard que existe por causa de um bug medido."""

    def test_entrada_boa_bate(self) -> None:
        antes = ("f.Seek(OFS_A);\n"
                 "f.SeekCurrent(2);\n"
                 "f.Seek(OFS_B);\n")
        depois, _ = P.aplicar_subs(antes)
        self.assertEqual(P.check_seeks(antes, depois, "x.cpp"), [])
        self.assertEqual(depois.count("soBeginning"), 2)
        self.assertEqual(depois.count("soCurrent"), 1)

    def test_seek_absoluto_virando_relativo_e_pego(self) -> None:
        # Reproducao do bug real: a regra atravessa a quebra de linha e engole
        # o seek seguinte, trocando a direcao. Em C++ isso corrompeu a tabela
        # de custo e so o ed.exe mostrou; aqui o guard pega antes de emitir.
        antes = "f.Seek(OFS_A);\n\tf.SeekCurrent(2);\n"
        ruim = "f.Seek(OFS_A, soCurrent);\n\tf.Seek(2, soCurrent);\n"
        notas = P.check_seeks(antes, ruim, "x.cpp")
        self.assertTrue(notas, "o guard nao pegou a troca de direcao")
        self.assertIn("absoluto", motivos(notas))

    def test_seek_que_sumiu_e_pego(self) -> None:
        antes = "f.Seek(OFS_A);\nf.Seek(OFS_B);\n"
        notas = P.check_seeks(antes, "f.Seek(OFS_A, soBeginning);\n", "x.cpp")
        self.assertTrue(notas)

    def test_a_regra_de_seek_nao_come_seekcurrent(self) -> None:
        # `\.Seek\(` NAO pode casar `.SeekCurrent(`. Se casasse, todo seek
        # relativo viraria absoluto de uma vez -- silenciosamente.
        depois, _ = P.aplicar_subs("f.SeekCurrent(2);\n")
        self.assertIn("soCurrent", depois)
        self.assertNotIn("soBeginning", depois)


class TestMascara(unittest.TestCase):
    """Comentario e literal nao sao codigo.

    Sem a mascara o `FORBIDDEN` acusava o comentario `// the new national sides
    are elsewhere` do Database.cpp como uso de `new`. Recusa falsa manda a
    WTE-TASK-18 investigar trabalho que nao existe, e ensina a ignorar o guard.
    """

    def test_palavra_proibida_em_comentario_de_linha(self) -> None:
        notas = P.conferir(P.FORBIDDEN, "// the new national sides\nint x;\n",
                           "x.cpp")
        self.assertEqual(notas, [])

    def test_palavra_proibida_em_comentario_de_bloco(self) -> None:
        notas = P.conferir(P.FORBIDDEN, "/* usa goto\n   e template<> */\n",
                           "x.cpp")
        self.assertEqual(notas, [])

    def test_palavra_proibida_em_literal(self) -> None:
        notas = P.conferir(P.FORBIDDEN, 'Report(r, "cannot delete file");\n',
                           "x.cpp")
        self.assertEqual(notas, [])

    def test_a_mascara_preserva_o_numero_da_linha(self) -> None:
        fonte = "/* um\n   dois */\ngoto fim;\n"
        notas = P.conferir(P.FORBIDDEN, fonte, "x.cpp")
        self.assertEqual([n.linha for n in notas], [3])

    def test_a_mascara_nao_apaga_codigo(self) -> None:
        self.assertIn("goto", P.mascarar("goto fim; // comentario\n"))


class TestSubs(unittest.TestCase):
    """Forma das regras, e as armadilhas que o precedente pagou."""

    def test_nenhuma_regra_usa_construcao_que_atravessa_a_quebra(self) -> None:
        # `[^x]` casa `\n`. Foi assim que um Seek(begin) virou SeekCurrent no
        # port_database.py: compilava, passava nos testes, passava no ASan, e
        # so o ed.exe mostrou. A regra vale para toda regra nova.
        #
        # `[\s\S]` e `.` sob DOTALL sao a mesma armadilha escrita de outro
        # jeito, e nenhuma regra deste gerador tem razao para usa-las: a
        # traducao e linha a linha. `\s` sozinho NAO entra nesta lista --
        # 20 regras o usam para adjacencia de token (`unsigned\s+char`,
        # `Report\s*\(`), onde bani-lo seria alarme falso. O que importa nele
        # e se a regra CONSOME a quebra na entrada real, e isso e medido por
        # `test_nenhuma_regra_reduz_a_contagem_de_linhas`.
        maus: list[tuple[str, str]] = []
        for padrao, _, razao in P.SUBS:
            if re.search(r"\[\^[^\]]*\]", padrao) and "\\n" not in padrao:
                maus.append((razao, "[^...] sem \\n"))
            if "[\\s\\S]" in padrao:
                maus.append((razao, "[\\s\\S]"))
            if re.search(r"\(\?s\)", padrao):
                maus.append((razao, "(?s) -- DOTALL"))
        self.assertEqual(
            maus, [],
            "regra com construcao que atravessa quebra de linha: " +
            "; ".join(f"{r} ({c})" for r, c in maus))

    def test_nenhuma_regra_reduz_a_contagem_de_linhas(self) -> None:
        # O invariante que vale para valer: aplicada em ordem sobre as seis
        # unidades reais **cruas**, nenhuma regra pode mudar quantas linhas o
        # arquivo tem. Cruas de proposito: `aplicar_subs` roda `_proteger()`
        # antes, e o mascaramento de comentario escondia o defeito. A regra 7
        # (`! -> not`) reduzia Database.cpp de 1704 para 1698 assim medida,
        # engolindo seis statements -- dois deles
        # `image_file.Seek(OFS_KIT_PREVIEW)` -- para dentro do comentario que
        # termina em `!`. O Pascal gerado nunca saiu errado; a regra e que nao
        # podia depender do mascaramento a montante para nao apagar codigo.
        maus: list[str] = []
        for _unit, rels in P.UNITS:
            for rel in rels:
                texto = (P.CORE / rel).read_text(encoding="utf-8")
                atual = texto
                for padrao, repl, razao in P.SUBS:
                    novo = re.sub(padrao, repl, atual, flags=re.M)
                    antes = len(atual.splitlines())
                    depois = len(novo.splitlines())
                    if antes != depois:
                        maus.append(f"{rel}: {razao} ({antes} -> {depois})")
                    atual = novo
        self.assertEqual(maus, [], "regra que consome a quebra: " + "; ".join(maus))

    def test_o_statement_nao_entra_no_comentario_que_termina_em_bang(self) -> None:
        saida, _ = P.aplicar_subs("\t//kit preview !!!!\n\timage_file.Seek(1);\n")
        linhas = saida.splitlines()
        self.assertEqual(len(linhas), 2, saida)
        self.assertNotIn("Seek", linhas[0])
        self.assertIn("Seek", linhas[1])

    def test_comparacao_antes_de_atribuicao(self) -> None:
        razoes = [r for _, _, r in P.SUBS]
        self.assertLess(razoes.index("== -> = (marcado)"),
                        razoes.index("= -> :="),
                        "a regra de atribuicao rodando antes da comparacao "
                        "transformaria `==` em `:==`")

    def test_igualdade_e_atribuicao(self) -> None:
        saida, _ = P.aplicar_subs("if (a == b)\n\tx = 1;\n")
        self.assertIn("a = b", saida)
        self.assertIn("x := 1;", saida)
        self.assertNotIn(":==", saida)

    def test_tipos_de_largura_fixa(self) -> None:
        saida, _ = P.aplicar_subs("std::uint32_t a;\nunsigned char b;\n")
        self.assertIn("LongWord", saida)
        self.assertIn("Byte", saida)
        # A regra zero de tipos.md: nada cujo tamanho dependa da plataforma.
        for proibido in ("Cardinal", "Integer", "PtrInt", "NativeInt"):
            self.assertNotIn(proibido, saida)

    def test_unsigned_char_antes_de_char(self) -> None:
        # Sem `\b` nas duas pontas, a regra de `char` comeria o sufixo de
        # `unsigned char` e sobraria `unsigned <algo>`.
        saida, _ = P.aplicar_subs("unsigned char b;\n")
        self.assertNotIn("unsigned", saida)

    def test_strcpy_vira_a_copia_com_semantica_de_c(self) -> None:
        saida, _ = P.aplicar_subs("std::strcpy(a, b);\nstrcat(c, d);\n")
        self.assertIn("CStrCopy(a, b);", saida)
        self.assertIn("CStrCat(c, d);", saida)
        # StrPCopy/StrLCopy truncam de outro jeito -- tipos.md, decisao 1.
        self.assertNotIn("StrPCopy", saida)
        self.assertNotIn("StrLCopy", saida)

    def test_endereco_de_argumento_some(self) -> None:
        saida, _ = P.aplicar_subs("f.Read(&teams[i].flag_shape, 1);\n")
        self.assertNotIn("&", saida)

    def test_saida_e_deterministica(self) -> None:
        fonte = "for (i = 0; i < 3; i++)\n\tf.Read(&a[i], 1);\n"
        self.assertEqual(P.aplicar_subs(fonte), P.aplicar_subs(fonte))


class TestCharParaInteiro(unittest.TestCase):
    """Decisao 4 do tipos.md na conversao local->campo (CORR-WTE-043).

    O `char` do x86 tem sinal: `int c = buf[0]` com `buf[0] == 0xC8` da -56.
    `Ord` daria 200, e a divergencia e silenciosa -- o `Save` grava so o byte
    baixo, entao um round-trip devolve a imagem identica de qualquer jeito.
    """

    def conversao(self, tipo_destino: str) -> str:
        tp = P.Transpilador.__new__(P.Transpilador)
        tp.escopo = {"buf1": P.TipoPas("AnsiChar", ["50"]),
                     "alvo": P.TipoPas(tipo_destino)}
        tp.campos = {}
        tp.classe_atual = ""
        tp.constantes = {}
        return tp.ajustar_atribuicao("alvo", "buf1[0]")

    def test_destino_largo_estende_o_sinal(self) -> None:
        for tipo in ("LongInt", "SmallInt", "Int64"):
            with self.subTest(tipo=tipo):
                self.assertEqual(self.conversao(tipo), "ShortInt(buf1[0])")

    def test_destino_de_um_byte_continua_com_ord(self) -> None:
        # `ml_teams[...].link[j]` tem destino Byte: os bits sao os mesmos e um
        # `ShortInt` ali seria sinal que o C++ nao tem.
        for tipo in ("Byte", "ShortInt"):
            with self.subTest(tipo=tipo):
                self.assertEqual(self.conversao(tipo), "Ord(buf1[0])")

    def test_a_saida_real_estende_o_sinal_so_no_custo(self) -> None:
        pas = (P.ROOT / "wte" / "src" / "we2002_database.pas").read_text(
            encoding="utf-8")
        self.assertIn("players[i].cost := ShortInt(buf1[0]);", pas)
        self.assertNotIn("players[i].cost := Ord(", pas)
        # Os demais continuam `Ord`: destino de um byte.
        self.assertIn("ml_teams[i].link[j] := Ord(buf[j]);", pas)
        self.assertEqual(pas.count("ShortInt(buf"), 1)


class TestEntradaReal(unittest.TestCase):
    """Contra o we2002_core de verdade -- sem compilar nada."""

    def test_as_unidades_estao_mapeadas(self) -> None:
        nomes = [u for u, _ in P.UNITS]
        self.assertEqual(len(nomes), len(set(nomes)), "unidade repetida")
        self.assertNotIn("we2002_sofifa", nomes)
        for _, arquivos in P.UNITS:
            for rel in arquivos:
                self.assertTrue((P.CORE / rel).exists(), rel)

    def test_nenhuma_entrada_do_core_fica_de_fora(self) -> None:
        """Todo `.hpp`/`.cpp` de `src/core/` esta num UNITS ou tem motivo escrito.

        ESTE e o teste que faltava. A primeira versao do `UNITS` esquecia
        `Team.hpp` e `Team.cpp` -- os tres registros que `Database.hpp` usa como
        campo -- e **nada** no `--check` acusou: o gerador rodava, recusava por
        outros motivos e ninguem via o buraco. Quem apanhou foi revisao humana
        (CORR-WTE-034).

        Arquivo esquecido em silencio e o pior modo de falha deste projeto: a
        camada de dados sairia incompleta com todos os gates verdes.
        """
        mapeados = {rel for _, arquivos in P.UNITS for rel in arquivos}
        no_disco = set()
        for p in list(P.CORE.glob("*.cpp")) + list(
                (P.CORE / "include/we2002").glob("*.hpp")):
            no_disco.add(p.relative_to(P.CORE).as_posix())

        orfaos = sorted(no_disco - mapeados - set(P.FORA_DO_TRANSPILADOR))
        self.assertEqual(
            orfaos, [],
            "arquivo(s) de src/core/ que nem entram no transpilador nem estao "
            "em FORA_DO_TRANSPILADOR com motivo: " + ", ".join(orfaos))

        # E o inverso: motivo escrito para arquivo que nao existe mais e lixo
        # que engana a proxima leitura.
        fantasmas = sorted(set(P.FORA_DO_TRANSPILADOR) - no_disco)
        self.assertEqual(fantasmas, [],
                         "FORA_DO_TRANSPILADOR cita arquivo inexistente: "
                         + ", ".join(fantasmas))

    def test_os_tres_registros_de_team_entram(self) -> None:
        # Regressao direta da CORR-WTE-034: `Database.hpp` declara `teams[]`,
        # `ml_teams[]` e `preset_formations[]`, e os tipos vem do `Team.hpp`.
        mapeados = {rel for _, arquivos in P.UNITS for rel in arquivos}
        self.assertIn("include/we2002/Team.hpp", mapeados)
        self.assertIn("Team.cpp", mapeados)

    def test_todos_os_strcpy_do_database_sao_cobertos(self) -> None:
        """Os 40 `strcpy` viram `CStrCopy`, inclusive os 2 com `std::`.

        Numero medido, nao suposto -- e ele importa: o `tipos.md` afirma 38
        porque contou so a grafia sem `std::` (CORR-WTE-030). Se a regra de
        `std::strcpy` sumisse ou trocasse de ordem, dois `strcpy` chegariam
        intactos ao Pascal, e `strcpy` nao existe em FPC.
        """
        fonte = (P.CORE / "Database.cpp").read_text(encoding="utf-8")
        antes = len(re.findall(r"\bstrcpy\b", fonte))
        antes_std = len(re.findall(r"\bstd::strcpy\b", fonte))
        self.assertEqual(antes, 40)
        self.assertEqual(antes_std, 2)

        saida, _ = P.aplicar_subs(fonte)
        self.assertEqual(len(re.findall(r"\bCStrCopy\b", saida)), antes)
        self.assertNotIn("strcpy", saida)
        self.assertNotIn("strcat", saida)

    def test_a_direcao_dos_seeks_do_core_se_preserva(self) -> None:
        for unit, arquivos in P.UNITS:
            for nome, texto in P.ler_fontes(unit, arquivos):
                traduzido, _ = P.aplicar_subs(texto)
                self.assertEqual(P.check_seeks(texto, traduzido, nome), [],
                                 f"{nome}: check_seeks reprovou")

    def test_o_relatorio_de_recusa_nomeia_arquivo_e_linha(self) -> None:
        """Com entrada plantada -- a real nao tem mais recusa desde a 18.

        Um guard que nunca foi visto recusar e um guard que se supoe
        funcionar. O que se mede aqui e a FORMA da recusa: arquivo e linha,
        para que a proxima leitura saiba onde ir.
        """
        fonte = "int f()\n{\n\tint x;\n\tgoto fim;\n\treturn 0;\n}\n"
        notas = P.conferir(P.FORBIDDEN_ENTRADA, fonte, "src/core/plantado.cpp")
        self.assertTrue(notas, "o guard parou de olhar")
        for n in notas:
            self.assertTrue(n.arquivo.startswith("src/core/"))
            self.assertEqual(n.linha, 4)

    def test_trecho_portado_a_mao_que_sumiu_recusa(self) -> None:
        """Porte a mao que apodrece calado e pior que porte a mao nenhum."""
        _, faltando = P.aplicar_trechos("src/core/Database.cpp",
                                        "// sem o bloco do ofstream\n")
        self.assertEqual(faltando, ["Database.cpp"])

    def test_item_de_topo_nao_reivindicado_recusa(self) -> None:
        """A ausencia silenciosa e o pior modo de falha deste gerador.

        Regressao da CORR-WTE-034 no nivel de ITEM: uma funcao nova em
        `src/core/` que o passe estrutural nao reconheca nao pode simplesmente
        nao sair na unidade.
        """
        tp = P.Transpilador("we2002_types", [("src/core/x.hpp", "")])
        tp.campos = {}
        it = P.classificar(P.Item("?", "", 7, "struct Novo { int a; };"))
        consts: list[str] = []
        tipos: list[str] = []
        P._item(tp, it, P.Manual(itens={}), consts, tipos, [], [])
        self.assertTrue(any("REGISTROS" in n.motivo for n in tp.notas),
                        [str(n) for n in tp.notas])


class TestUnidadesCompilam(unittest.TestCase):
    """O gate da WTE-TASK-18, e o unico que mede de verdade.

    Grupo 1: o `fpc` compila as seis unidades. Grupo 2: um programa Pascal
    (`wte/tests/test_camada_dados.pas`) exercita a camada gerada e prova as
    cinco decisoes de `wte/re/tipos.md` -- layout de bit, sinal de `char`,
    semantica da copia, leitura curta e o terminador do sidecar.

    Sem `fpc` os dois **pulam** e dizem que nada foi medido, como o
    `test_gen_tables_pas.py` faz.
    """

    PROGRAMA = P.ROOT / "wte" / "tests" / "test_camada_dados.pas"

    def _fpc(self) -> str:
        fpc = shutil.which("fpc")
        if not fpc:
            self.skipTest("sem fpc -- as seis unidades NAO foram compiladas "
                          "nesta execucao")
        return fpc

    def test_as_seis_unidades_compilam(self) -> None:
        fpc = self._fpc()
        with tempfile.TemporaryDirectory() as td:
            r = subprocess.run(
                [fpc, f"-Fu{P.OUT_DIR}", f"-FU{td}",
                 str(P.OUT_DIR / "we2002_database.pas")],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            # Aviso conta: "Comment level 2" ja apareceu quando um comentario
            # gerado tinha `{}` dentro, e o proximo pode ser um de verdade.
            self.assertNotIn("Warning:", r.stdout, r.stdout)
            produzidas = {f.stem for f in Path(td).glob("*.ppu")}
            for unit, _ in P.UNITS:
                self.assertIn(unit, produzidas)

    def test_as_decisoes_de_tipo_valem_em_execucao(self) -> None:
        fpc = self._fpc()
        with tempfile.TemporaryDirectory() as td:
            binario = Path(td) / "test_camada_dados"
            r = subprocess.run(
                [fpc, f"-Fu{P.OUT_DIR}", f"-FU{td}", f"-o{binario}",
                 str(self.PROGRAMA)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            r = subprocess.run([str(binario)], capture_output=True, text=True)
        linhas = [ln for ln in r.stdout.splitlines() if ln.strip()]
        falhas = [ln for ln in linhas if ln.startswith("FALHA")]
        self.assertEqual(falhas, [], r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout)
        # Numero medido, e nao suposto: um caso que some do programa Pascal
        # some em silencio, e o teste continuaria verde sem medir nada.
        self.assertEqual(len(linhas), 26, r.stdout)


if __name__ == "__main__":
    unittest.main()
