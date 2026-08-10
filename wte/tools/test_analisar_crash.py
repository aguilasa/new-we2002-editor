#!/usr/bin/env python3
"""Testes do analisar_crash.py -- WTE-TASK-19.

Dois grupos, pelo mesmo criterio do `test_analisar_io.py`:

1. **parser do log**, com linha plantada. Ele decide qual excecao localiza e
   qual e cascata, e decide o endereco de carga de cada modulo. Errar ali
   aponta o travamento para a funcao errada -- e a saida continua parecendo
   medida.
2. **a evidencia real**, contra os TSV commitados e o `.exe`. Essa parte fica
   sob `skipUnless`, porque `we-team-editor/` nao e versionada.
"""

from __future__ import annotations

import unittest

import analisar_crash as C

MOD = ('0024:trace:loaddll:build_module Loaded '
       r'L"Z:\\x\\vcl60.bpl" at 005F0000: native')
BUILTIN = ('002c:trace:loaddll:build_module Loaded '
           r'L"C:\\windows\\system32\\kernel32.dll" at 7BEC0000: builtin')
EXC = ("0024:trace:seh:dispatch_exception code=c0000005 flags=0 "
       "addr=005F5EA0 ip=005f5ea0")
I0 = "0024:trace:seh:dispatch_exception  info[0]=00000000"
I1 = "0024:trace:seh:dispatch_exception  info[1]=0000001c"
R1 = ("0024:trace:seh:dispatch_exception  eax=00000000 ebx=00000000 "
      "ecx=0031e3e8 edx=00000008 esi=00000008 edi=01644d3c")
R2 = ("0024:trace:seh:dispatch_exception  ebp=0031e3c8 esp=0031e388 "
      "cs=0023 ss=002b ds=002b es=002b fs=0063 gs=006b flags=00010202")


class TestParser(unittest.TestCase):

    def test_excecao_completa(self) -> None:
        exc, mods = C.ler_log([EXC, I0, I1, "ruido", R1, R2])
        self.assertEqual(len(exc), 1)
        e = exc[0]
        self.assertEqual(e["addr"], "0x005f5ea0")
        self.assertEqual(e["info1"], "0x0000001c")
        self.assertEqual(e["eax"], "0x00000000")
        self.assertEqual(e["edx"], "0x00000008")
        self.assertEqual(e["esp"], "0x0031e388")

    def test_so_violacao_de_acesso_entra(self) -> None:
        """`6ba` (RPC_S_SERVER_UNAVAILABLE) aparece na subida de QUALQUER
        corrida -- inclusive na que nao trava. Contar essa como falha faria a
        sessao de controle registrar excecao e destruiria a comparacao."""
        outra = ("00cc:trace:seh:dispatch_exception code=6ba flags=0 "
                 "addr=7BC12517 ip=7bc12517")
        exc, _ = C.ler_log([outra, I0, I1, R1, R2, EXC, I0, I1, R1, R2])
        self.assertEqual(len(exc), 1)
        self.assertEqual(exc[0]["code"], "c0000005")

    def test_registros_nao_vazam_para_a_excecao_seguinte(self) -> None:
        # Sem fechar o registro no `esp`, a segunda excecao herdaria os
        # registros da primeira e o `edx` apontaria para o sitio errado.
        segunda = ("0024:trace:seh:dispatch_exception code=c0000005 flags=0 "
                   "addr=00000000 ip=00000000")
        exc, _ = C.ler_log([EXC, I0, I1, R1, R2, segunda])
        self.assertEqual(len(exc), 2)
        self.assertEqual(exc[1]["addr"], "0x00000000")
        self.assertNotIn("edx", exc[1])

    def test_so_modulo_nativo_entra(self) -> None:
        # As builtin do Wine sao dezenas e nenhuma e do autor; deixa-las
        # entrar faria o casamento por base escolher uma DLL do Wine.
        _, mods = C.ler_log([MOD, BUILTIN, MOD])
        self.assertEqual(mods, [{"modulo": "vcl60.bpl", "base": "0x005f0000",
                                 "tipo": "native"}])

    def test_prologo_acha_o_inicio_da_rotina(self) -> None:
        # push ebp; mov ebp,esp; ... ; o alvo esta depois
        codigo = b"\x90\x90\x55\x8b\xec\x90\x90\x90"
        self.assertEqual(C._prologo(codigo, 0x401000, 0x401006), 0x401002)

    def test_prologo_devolve_nada_sem_prologo(self) -> None:
        self.assertIsNone(C._prologo(b"\x90" * 8, 0x401000, 0x401006))

    def test_chamada_relativa_e_resolvida(self) -> None:
        # E8 com deslocamento negativo: call para tras, que e o caso real.
        codigo = bytearray(b"\x90" * 16)
        codigo[8] = 0xE8
        codigo[9:13] = (-13).to_bytes(4, "little", signed=True)
        self.assertEqual(C._chamadas_para(bytes(codigo), 0x401000, 0x401000),
                         [0x401008])


ROTEIROS = C.ROOT / "wte" / "tests" / "roteiros"


class TestParDeRoteiros(unittest.TestCase):
    """O par 07/08 e o que torna a atribuicao uma medida, e nao uma impressao.

    O texto gerado afirma que os dois sao iguais ate `= ARRANQUE`. Se alguem
    editar um dos dois sem o outro, a afirmacao continua sendo escrita e passa
    a ser falsa -- este teste e o que impede isso.
    """

    def cabeca(self, nome: str) -> list[str]:
        linhas = []
        for ln in (ROTEIROS / nome).read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            linhas.append(ln)
            if ln == "= ARRANQUE":
                return linhas
        self.fail(f"{nome}: sem a marca ARRANQUE")

    def test_o_par_e_identico_ate_o_arranque(self) -> None:
        self.assertEqual(self.cabeca("07-controle-sem-time.txt"),
                         self.cabeca("08-so-troca-de-time.txt"))

    def test_so_o_08_troca_de_time(self) -> None:
        def resto(nome: str) -> str:
            t = (ROTEIROS / nome).read_text(encoding="utf-8")
            return t.split("= ARRANQUE", 1)[1]
        self.assertIn("tecla Down", resto("08-so-troca-de-time.txt"))
        self.assertNotIn("tecla Down", resto("07-controle-sem-time.txt"))


REAL = C.EXE.is_file() and C.TSV_SEH.exists()


@unittest.skipUnless(REAL, "precisa do we-team-editor.exe e da evidencia")
class TestEvidencia(unittest.TestCase):

    def test_a_sessao_de_controle_nao_tem_excecao(self) -> None:
        """O controle e o que torna a atribuicao uma medida.

        Sem uma sessao que faz a mesma abertura e NAO seleciona time, dizer
        "quem mata e a troca de time" seria leitura de tela.
        """
        sessoes = C._ler_tsv(C.TSV_SESSOES)
        sem = [s for s in sessoes if s["seleciona_time"] == "nao"]
        com = [s for s in sessoes if s["seleciona_time"] == "sim"]
        self.assertTrue(sem, "sem sessao de controle")
        self.assertTrue(com)
        self.assertEqual([s["excecoes"] for s in sem], ["0"] * len(sem))
        self.assertTrue(all(int(s["excecoes"]) > 0 for s in com))

    def test_o_endereco_de_falha_cai_num_modulo_registrado(self) -> None:
        seh = C._ler_tsv(C.TSV_SEH)
        mods = C._ler_tsv(C.TSV_MODULOS)
        addr = int(seh[0]["addr"], 16)
        bases = [int(m["base"], 16) for m in mods]
        self.assertTrue(any(b <= addr for b in bases),
                        "nenhum modulo nativo abaixo do endereco de falha; "
                        "faltou +loaddll na medicao")

    def test_o_simbolo_resolvido_e_o_esperado(self) -> None:
        """Se isto mudar, ou a medicao foi refeita com outro binario, ou o
        parser de exportacao quebrou -- e o `crash.md` afirma um nome de
        funcao que ninguem mediu."""
        seh = C._ler_tsv(C.TSV_SEH)
        mods = {m["modulo"]: int(m["base"], 16) for m in C._ler_tsv(C.TSV_MODULOS)}
        addr = int(seh[0]["addr"], 16)
        nome, base = max(((n, b) for n, b in mods.items() if b <= addr),
                         key=lambda x: x[1])
        pe = C.Pe((C.BPL / nome).read_bytes(), nome)
        exp = C.exportacao_que_contem(pe, addr - base)
        self.assertIsNotNone(exp)
        self.assertIn("TFont", exp[1])

    def test_o_sitio_da_falha_e_unico(self) -> None:
        # A escolha do sitio depende do imediato em EDX. Dois sitios com o
        # mesmo imediato tornariam a identificacao ambigua, e o texto gerado
        # diz "so um dos sitios carrega".
        linhas = [l for l in C.gerar().splitlines()
                  if l.startswith("| `0x") and l.endswith("| sim |")]
        self.assertEqual(len(linhas), 1, linhas)

    def test_o_gerado_esta_em_dia(self) -> None:
        self.assertEqual(C.OUT_MD.read_text(encoding="utf-8"), C.gerar())


if __name__ == "__main__":
    unittest.main()
