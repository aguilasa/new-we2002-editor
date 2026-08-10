#!/usr/bin/env python3
"""Testes do port_database_pas.py -- WTE-TASK-17.

O criterio da task e explicito: **"recusa testada com entrada plantada, nao so
com a entrada boa"**. Um guard que nunca foi visto recusar e um guard que se
supoe funcionar.

Tres grupos:

1. `FORBIDDEN` -- cada construcao sem traducao decidida recusa, e a recusa traz
   a linha certa.
2. `check_seeks()` -- uma regra de `SUBS` que troca a direcao de um seek e
   pega, mesmo produzindo Pascal que compilaria. Este e o guard que existe por
   causa de um bug real, e o teste reproduz o bug.
3. O que **nao** pode recusar: comentario e literal nao sao codigo.
"""

from __future__ import annotations

import re
import unittest

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


class TestEstruturaAindaRecusa(unittest.TestCase):
    """O passe estrutural nao existe, e o tool nao pode fingir que existe.

    Achado da WTE-TASK-17: o `tools/port_database.py` pode ser substituicao
    textual pura porque fonte e alvo sao a MESMA linguagem. C++ -> Pascal nao
    pode. Enquanto o passe estrutural nao existir, emitir um `.pas` com corpo em
    C++ seria produzir um artefato que parece camada de dados, nao compila, e
    convida alguem a "so ajustar a mao" o que a §4.4 proibe.
    """

    def conferir(self, fonte: str):
        traduzido, _ = P.aplicar_subs(fonte)
        return P.conferir(P.FORBIDDEN, traduzido, "plantado.cpp")

    def test_bloco(self) -> None:
        self.assertIn("passe estrutural", motivos(self.conferir("{\n}\n")))

    def test_cabecalho_de_for(self) -> None:
        notas = self.conferir("for (i = 0; i < 63; i++)\n")
        self.assertIn("`for` no estilo C", motivos(notas))

    def test_struct(self) -> None:
        self.assertIn("struct", motivos(self.conferir("struct SquadNumbers {\n")))

    def test_nenhuma_unidade_e_emitida_enquanto_houver_recusa(self) -> None:
        for unit, arquivos in P.UNITS:
            pascal, notas = P.transpilar_unidade(unit, arquivos)
            self.assertTrue(notas, f"{unit}: sem recusa, mas o passe "
                                   f"estrutural nao existe -- guard furado")
            self.assertFalse((P.OUT_DIR / f"{unit}.pas").exists(),
                             f"{unit}.pas nao pode existir ainda")


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

    def test_nenhuma_regra_usa_classe_negada_sem_excluir_a_quebra(self) -> None:
        # `[^x]` casa `\n`. Foi assim que um Seek(begin) virou SeekCurrent no
        # port_database.py: compilava, passava nos testes, passava no ASan, e
        # so o ed.exe mostrou. A regra vale para toda regra nova.
        maus = [(p, r) for p, _, r in P.SUBS
                if "[^" in p and "\\n" not in p]
        self.assertEqual(
            maus, [],
            "regra com classe negada que atravessa quebra de linha: " +
            "; ".join(r for _, r in maus))

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
            no_disco.add(str(p.relative_to(P.CORE)))

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
        _, notas = P.transpilar_unidade(*P.UNITS[-1])
        self.assertTrue(notas, "a WTE-TASK-18 existe porque ha recusas; "
                               "zero aqui significa que o guard parou de olhar")
        for n in notas:
            self.assertTrue(n.arquivo.startswith("src/core/"))
            self.assertGreater(n.linha, 0)


if __name__ == "__main__":
    unittest.main()
