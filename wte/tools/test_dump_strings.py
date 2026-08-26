#!/usr/bin/env python3
"""Testes do `dump_strings.py` -- o decodificador de comprimento x86-32.

    python3 -m unittest discover wte/tools -p 'test_*.py'
    make -C wte test

Por que este arquivo existe
---------------------------

A coluna `handler` do `strings.tsv` nao sai de tabela nenhuma do binario: sai
de medir **onde cada um dos 96 handlers termina**, e isso depende de um
decodificador de comprimento de instrucao escrito a mao (`decode()`,
`extent()`, ~200 linhas de mapa de opcode).

Errar o comprimento de uma instrucao desloca todas as fronteiras depois dela
**em silencio**: cai junto a coluna `handler` das 474 referencias, os 122 pares
string-handler, a cobertura da `.text` e as duas tabelas que dependem dela.
Nada disso parece errado ao olhar.

A conferencia existia -- contra o `objdump`, com resultado certo -- mas era um
paragrafo, nao um arquivo. Reproduzi-la exigia remontar o arranjo de
comparacao, e a armadilha estava justamente ai (ver `TestContraObjdump`).

Duas metades
------------

1. **Comprimento por caso**, sem o `.exe` e sem o `objdump`: roda em qualquer
   maquina, e e a que pega regressao de mapa de opcode.
2. **A conferencia externa**, `skipUnless(objdump e .exe)`: a unica medida
   independente que o projeto tem do decodificador. Fica versionada em vez de
   viver na memoria de quem a rodou uma vez.

O `skipUnless` e o que mantem de pe a regra do `test_dfm_extract.py` -- a
bateria padrao nao depende do binario do Obocaman -- sem jogar fora a
conferencia.

Isto NAO e um gerador: nao aceita `--check`, e o Makefile filtra
`tools/test_*.py` de `GENERATORS`. Ver `wte/tools/README.md`.
"""

from __future__ import annotations

import difflib
import inspect
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dump_strings as d  # noqa: E402
import dump_units as u  # noqa: E402

# O `dump_units.py` carrega uma copia **verbatim** de `_fill`, `decode` e
# `extent`. A duplicacao e deliberada -- cada gerador de `wte/tools/` roda
# sozinho, decisao registrada no `wte/README.md`, e vale igual para o leitor de
# PE. O preco e que as duas podem divergir em silencio, e a copia do
# `dump_units.py` sustenta o unico veredito nao trivial da WTE-TASK-07: o corpo
# dos 96 handlers e o que separa "chamada dentro de handler" de "chamada em
# codigo de RTL".
#
# Dois testes pagam esse preco: a tabela de comprimento roda contra os dois
# modulos, e `TestCopiaVerbatim` falha se o texto-fonte das tres funcoes
# divergir. Isto **nao** reabre a decisao de duplicar -- poe uma guarda sobre
# ela.
DECODERS = (("dump_strings", d), ("dump_units", u))


def b(*vals: int) -> bytes:
    return bytes(vals)


# ------------------------------------------------------- comprimento a caso --
#
# (rotulo, bytes, comprimento esperado, classe de fluxo). O limite passado ao
# decode() e sempre len(bytes): assim um comprimento maior do que o esperado
# bate no aborto de "atravessa o limite" em vez de ler lixo -- o caso errado
# falha alto, nao baixo.

LENGTH_CASES: list[tuple[str, bytes, int, str]] = [
    # -- sem ModRM, sem imediato
    ("nop", b(0x90), 1, ""),
    ("ret", b(0xC3), 1, "ret"),
    ("leave", b(0xC9), 1, ""),
    ("push ebp", b(0x55), 1, ""),
    ("cdq", b(0x99), 1, ""),
    ("ret imm16", b(0xC2, 0x08, 0x00), 3, "ret"),
    ("retf", b(0xCB), 1, "ret"),
    ("retf imm16", b(0xCA, 0x04, 0x00), 3, "ret"),

    # -- imediato que segue o prefixo de tamanho de operando
    ("mov eax, imm32", b(0xB8, 0x78, 0x56, 0x34, 0x12), 5, ""),
    ("66 mov ax, imm16", b(0x66, 0xB8, 0x34, 0x12), 4, ""),
    ("mov al, imm8", b(0xB0, 0x7F), 2, ""),
    ("push imm32", b(0x68, 0x00, 0x10, 0x40, 0x00), 5, ""),
    ("push imm8", b(0x6A, 0x08), 2, ""),
    ("add eax, imm32", b(0x05, 0x01, 0x00, 0x00, 0x00), 5, ""),
    ("66 add ax, imm16", b(0x66, 0x05, 0x01, 0x00), 4, ""),
    ("add al, imm8", b(0x04, 0x01), 2, ""),
    ("test al, imm8", b(0xA8, 0x01), 2, ""),
    ("test eax, imm32", b(0xA9, 0x01, 0x00, 0x00, 0x00), 5, ""),

    # -- ModRM: os quatro modos, com e sem SIB
    ("mod=3 (add eax, ecx)", b(0x01, 0xC8), 2, ""),
    ("mod=0 rm=0 (add [eax], ecx)", b(0x01, 0x08), 2, ""),
    ("mod=0 rm=5 (disp32 absoluto)", b(0x01, 0x0D, 0x00, 0x20, 0x42, 0x00),
     6, ""),
    ("mod=1 (disp8)", b(0x8B, 0x45, 0xFC), 3, ""),
    ("mod=2 (disp32)", b(0x8B, 0x85, 0x00, 0xFF, 0xFF, 0xFF), 6, ""),
    ("mod=0 rm=4 SIB simples", b(0x8B, 0x04, 0x08), 3, ""),
    ("mod=0 rm=4 SIB base=5 (disp32)",
     b(0x8B, 0x04, 0x8D, 0x00, 0x20, 0x42, 0x00), 7, ""),
    ("mod=1 rm=4 SIB + disp8", b(0x8B, 0x44, 0x08, 0x04), 4, ""),
    ("mod=2 rm=4 SIB + disp32",
     b(0x8B, 0x84, 0x08, 0x00, 0x01, 0x00, 0x00), 7, ""),
    ("lea com SIB e disp8", b(0x8D, 0x44, 0x24, 0x10), 4, ""),

    # -- ModRM mais imediato: os dois se somam
    ("mov [ebp-4], imm32", b(0xC7, 0x45, 0xFC, 0x01, 0x00, 0x00, 0x00), 7, ""),
    ("66 mov [ebp-4], imm16", b(0x66, 0xC7, 0x45, 0xFC, 0x01, 0x00), 6, ""),
    ("cmp [ebp-8], imm8", b(0x83, 0x7D, 0xF8, 0x00), 4, ""),
    ("cmp [ebp-8], imm32", b(0x81, 0x7D, 0xF8, 0x00, 0x01, 0x00, 0x00), 7, ""),
    ("imul r, r/m, imm32", b(0x69, 0xC0, 0x10, 0x00, 0x00, 0x00), 6, ""),
    ("imul r, r/m, imm8", b(0x6B, 0xC0, 0x10), 3, ""),
    ("shift r/m, imm8", b(0xC1, 0xE0, 0x02), 3, ""),

    # -- grupo 3: imediato so no /0 e no /1
    ("f7 /0 test r/m32, imm32",
     b(0xF7, 0xC0, 0x01, 0x00, 0x00, 0x00), 6, ""),
    ("f7 /3 neg (sem imediato)", b(0xF7, 0xD8), 2, ""),
    ("f6 /0 test r/m8, imm8", b(0xF6, 0xC0, 0x01), 3, ""),
    ("f6 /4 mul (sem imediato)", b(0xF6, 0xE0), 2, ""),
    ("66 f7 /0 test r/m16, imm16", b(0x66, 0xF7, 0xC0, 0x01, 0x00), 5, ""),

    # -- prefixos
    ("f3 rep movs", b(0xF3, 0xA4), 2, ""),
    ("f2 repne scas", b(0xF2, 0xAE), 2, ""),
    ("lock add", b(0xF0, 0x01, 0x08), 3, ""),
    ("segmento fs", b(0x64, 0x8B, 0x0D, 0x00, 0x00, 0x00, 0x00), 7, ""),
    ("dois prefixos", b(0xF3, 0x66, 0xA5), 3, ""),

    # -- desvios
    ("jmp rel8", b(0xEB, 0x10), 2, "jmp"),
    ("jmp rel32", b(0xE9, 0x00, 0x01, 0x00, 0x00), 5, "jmp"),
    ("jcc rel8", b(0x74, 0x05), 2, "jcc"),
    ("0f jcc rel32", b(0x0F, 0x84, 0x00, 0x01, 0x00, 0x00), 6, "jcc"),
    ("call rel32", b(0xE8, 0x00, 0x01, 0x00, 0x00), 5, "call"),
    ("loop rel8", b(0xE2, 0xFE), 2, "jcc"),
    ("jmp indireto (ff /4)", b(0xFF, 0x20), 2, "jmp"),
    ("call indireto (ff /2)", b(0xFF, 0x10), 2, ""),
    ("inc r/m (ff /0) nao encerra", b(0xFF, 0x00), 2, ""),
    ("call far", b(0x9A, 0, 0, 0, 0, 0, 0), 7, ""),
    ("jmp far", b(0xEA, 0, 0, 0, 0, 0, 0), 7, ""),
    ("66 jmp far (2+2)", b(0x66, 0xEA, 0, 0, 0, 0), 6, ""),

    # -- escape 0f
    ("0f setcc", b(0x0F, 0x94, 0xC0), 3, ""),
    ("0f movzx", b(0x0F, 0xB6, 0x45, 0xFC), 4, ""),
    ("0f imul", b(0x0F, 0xAF, 0xC1), 3, ""),
    ("0f bt imm8", b(0x0F, 0xBA, 0xE0, 0x01), 4, ""),
    ("0f bswap", b(0x0F, 0xC8), 2, ""),
    ("0f cpuid", b(0x0F, 0xA2), 2, ""),
    ("0f shld imm8", b(0x0F, 0xA4, 0xC1, 0x02), 4, ""),

    # -- x87 e outros de um byte com ModRM
    ("x87 fld", b(0xD9, 0x45, 0xFC), 3, ""),
    ("enter", b(0xC8, 0x00, 0x00, 0x00), 4, ""),
    ("int3", b(0xCC), 1, ""),
    ("int imm8", b(0xCD, 0x21), 2, ""),
    ("mov eax, moffs32", b(0xA1, 0x00, 0x20, 0x42, 0x00), 5, ""),
]


class TestComprimento(unittest.TestCase):
    """O mapa de opcodes, caso a caso. Nao abre o `.exe`."""

    def test_cada_caso(self):
        # Contra os **dois** módulos: a tabela é barata, e é o que pega uma
        # correção aplicada só numa das cópias.
        for modulo, mod in DECODERS:
            for label, data, length, kind in LENGTH_CASES:
                with self.subTest(modulo=modulo, caso=label):
                    got_len, got_kind, _target = mod.decode(data, 0, len(data))
                    self.assertEqual(got_len, length,
                                     f"comprimento de {label} em {modulo}")
                    self.assertEqual(got_kind, kind,
                                     f"classe de fluxo de {label} em {modulo}")

    def test_decodifica_em_sequencia(self):
        # Um comprimento errado no meio desloca tudo depois dele -- que e o
        # modo de falha que este arquivo existe para pegar. Aqui em miniatura.
        seq = b(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x08, 0xC7, 0x45, 0xFC,
                0x01, 0x00, 0x00, 0x00, 0xC9, 0xC3)
        pos, bounds = 0, []
        while pos < len(seq):
            bounds.append(pos)
            pos += d.decode(seq, pos, len(seq))[0]
        self.assertEqual(bounds, [0, 1, 3, 6, 13, 14])
        self.assertEqual(pos, len(seq))

    def test_alvo_de_desvio_relativo(self):
        # `extent()` decide onde a funcao acaba pelo teto dos alvos, entao um
        # alvo errado encurta ou estica o corpo.
        self.assertEqual(d.decode(b(0xEB, 0x05), 0, 2)[2], 7)
        # `eb fe` e o autoloop: o deslocamento -2 aponta para a propria
        # instrucao, entao o alvo e 0, nao 1.
        self.assertEqual(d.decode(b(0xEB, 0xFE), 0, 2)[2], 0)
        self.assertEqual(d.decode(b(0x74, 0x10), 0, 2)[2], 18)
        self.assertEqual(
            d.decode(b(0xE9, 0x00, 0x01, 0x00, 0x00), 0, 5)[2], 261)
        self.assertEqual(
            d.decode(b(0x0F, 0x84, 0x00, 0x01, 0x00, 0x00), 0, 6)[2], 262)
        # call nao tem alvo: `extent` nao segue chamada.
        self.assertIsNone(d.decode(b(0xE8, 0x00, 0x01, 0x00, 0x00), 0, 5)[2])


class TestCopiaVerbatim(unittest.TestCase):
    """As duas cópias do decodificador têm de andar juntas.

    O Log da WTE-TASK-07 escreveu "os dois têm de andar juntos se um dia
    mudarem". Comentário não segura ninguém: quem corrigir um comprimento no
    módulo testado sairia com a bateria verde e a outra cópia errada.
    """

    FUNCOES = ("_fill", "decode", "extent")

    def fonte(self, mod, nome: str) -> str:
        return inspect.getsource(getattr(mod, nome))

    def test_as_tres_funcoes_sao_identicas(self):
        for nome in self.FUNCOES:
            with self.subTest(nome):
                a, b = self.fonte(d, nome), self.fonte(u, nome)
                if a == b:
                    continue
                diff = "\n".join(difflib.unified_diff(
                    a.splitlines(), b.splitlines(),
                    fromfile=f"dump_strings.py:{nome}",
                    tofile=f"dump_units.py:{nome}", lineterm=""))
                self.fail(
                    f"`{nome}` divergiu entre os dois geradores.\n"
                    f"Uma das duas cópias mudou e a outra precisa da MESMA "
                    f"mudança -- a do\n`dump_units.py` sustenta a fronteira "
                    f"dos 96 corpos, que decide o veredito\ndo `Comobj` na "
                    f"WTE-TASK-07.\n{diff}")

    def test_as_tabelas_de_opcode_sao_identicas(self):
        # `_fill` idêntico não basta: o mapa é montado por dezenas de chamadas
        # fora de função, que `inspect.getsource` não alcança.
        self.assertEqual(d._MAP1, u._MAP1)
        self.assertEqual(d._MAP2, u._MAP2)
        self.assertEqual(d.PREFIXES, u.PREFIXES)


class TestAbortos(unittest.TestCase):
    """Aborto e o comportamento correto: chutar comprimento falsifica tudo."""

    def assertAborta(self, data: bytes, limit: int, trecho: str):
        with self.assertRaises(d.DumpError) as ctx:
            d.decode(data, 0, limit)
        self.assertIn(trecho, str(ctx.exception))

    def test_opcode_fora_do_mapa(self):
        self.assertAborta(b(0x0F, 0x0F, 0x00), 3,
                          "opcode 0f0f em 0x0 nao esta no mapa")

    def test_instrucao_atravessa_o_limite(self):
        self.assertAborta(b(0xB8, 0x01), 2, "atravessa o limite 0x2")

    def test_modrm_fora_do_limite(self):
        self.assertAborta(b(0x8B), 1, "ModRM fora do limite")

    def test_sib_fora_do_limite(self):
        self.assertAborta(b(0x8B, 0x04), 2, "SIB fora do limite")

    def test_escape_0f_sem_segundo_byte(self):
        self.assertAborta(b(0x0F), 1, "0x0F sem segundo byte")

    def test_so_prefixos_ate_o_limite(self):
        self.assertAborta(b(0xF3, 0x66), 2, "so prefixos ate o limite")

    def test_prefixo_67_aborta(self):
        # Endereco de 16 bits muda a forma do ModRM inteiro. Adivinhar dali
        # em diante embaralharia a varredura.
        self.assertAborta(b(0x67, 0x8B, 0x00), 3, "prefixo 0x67")

    def test_ff_ff_nao_aborta(self):
        # O `objdump` chama isto de `(bad)`; aqui volta com comprimento 2 e
        # sem classe de fluxo. Nao ocorre dentro dos 96 corpos, entao nao
        # contamina medida nenhuma -- mas o silencio fica fixado, para que
        # mudar isso seja uma decisao e nao um acidente.
        self.assertEqual(d.decode(b(0xFF, 0xFF), 0, 2), (2, "", None))


class TestExtent(unittest.TestCase):
    """`extent()` sobre corpos sinteticos: o teto de alvos e a regra toda."""

    def corpo(self, data: bytes) -> int:
        return d.extent(data, 0, len(data), "corpo de teste")

    def test_ret_encerra(self):
        self.assertEqual(self.corpo(b(0x90, 0xC3, 0x90)), 2)

    def test_jmp_para_frente_nao_encerra_antes_do_alvo(self):
        # jmp +1 pula o nop; o ret depois dele e que encerra. Um `extent` que
        # parasse no primeiro jmp cortaria o corpo pela metade.
        self.assertEqual(self.corpo(b(0xEB, 0x01, 0x90, 0xC3)), 4)

    def test_jcc_estende_o_corpo_ate_o_alvo(self):
        # je +2 salta o `nop nop`; o ret so vale depois deles.
        self.assertEqual(self.corpo(b(0x74, 0x02, 0x90, 0x90, 0xC3)), 5)

    def test_ret_antes_do_alvo_nao_encerra(self):
        # ret no meio, mas ha desvio apontando alem dele.
        self.assertEqual(self.corpo(b(0x74, 0x03, 0xC3, 0x90, 0x90, 0xC3)), 6)


EXE_E_OBJDUMP = (d.EXE.is_file() and shutil.which("objdump") is not None
                 and d.PUB.is_file() and d.DFM.is_dir())

_OBJDUMP_LINE = re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*(\S*)')


@unittest.skipUnless(EXE_E_OBJDUMP,
                     "precisa do we-team-editor.exe e do objdump")
class TestContraObjdump(unittest.TestCase):
    """A unica medida independente do decodificador que o projeto tem.

    Compara fronteira a fronteira os 96 corpos contra `objdump -D -b binary`.

    **A armadilha:** o `objdump` emite linhas de continuacao para instrucao
    longa -- endereco e bytes, mnemonico vazio. Conta-las como instrucao da 48
    "divergencias" que nao existem, e foi exatamente o que custou uma iteracao
    a quem refez esta conferencia sabendo a resposta. Elas sao descartadas
    aqui, e o teste **afirma** que sao 48: se virarem outro numero, o recorte
    mudou e a comparacao merece um olhar.
    """

    @classmethod
    def setUpClass(cls):
        img = d.Image(d.EXE.read_bytes())
        handlers = d.read_published(d.PUB.read_text(encoding="utf-8"))
        cls.m = d.Measurement(img, handlers, sorted(d.DFM.glob("*.dfm"), key=lambda p: p.as_posix()))
        cls.img = img
        text = cls.m.text
        cls.text_va = img.image_base + text.rva
        cls.text_bytes = img.data[text.raw_ptr:text.raw_ptr + text.raw_size]

    def fronteiras_do_script(self) -> set[int]:
        out = set()
        for h in self.m.handlers:
            pos = self.img.va_to_offset(h.addr)
            end = self.img.va_to_offset(h.end - 1) + 1
            while pos < end:
                out.add(self.img.offset_to_va(pos))
                pos += d.decode(self.img.data, pos, end)[0]
        return out

    def fronteiras_do_objdump(self, carved: Path) -> tuple[set[int], int]:
        out, continuacao = set(), 0
        for h in self.m.handlers:
            proc = subprocess.run(
                ["objdump", "-D", "-b", "binary", "-m", "i386", "-M", "intel",
                 f"--adjust-vma={self.text_va:#x}",
                 f"--start-address={h.addr:#x}",
                 f"--stop-address={h.end:#x}", str(carved)],
                capture_output=True, text=True, check=True)
            for line in proc.stdout.splitlines():
                g = _OBJDUMP_LINE.match(line)
                if not g:
                    continue
                if not g.group(3):
                    continuacao += 1      # linha de continuacao: nao e instr.
                    continue
                out.add(int(g.group(1), 16))
        return out, continuacao

    def test_fronteiras_coincidem(self):
        import tempfile
        self.assertEqual(len(self.m.handlers), 96)
        with tempfile.TemporaryDirectory() as tmp:
            carved = Path(tmp) / "text.bin"
            carved.write_bytes(self.text_bytes)
            meu = self.fronteiras_do_script()
            deles, continuacao = self.fronteiras_do_objdump(carved)
        self.assertEqual(len(meu), 10416, "instrucoes contadas pelo script")
        self.assertEqual(continuacao, 48,
                         "linhas de continuacao do objdump descartadas")
        self.assertEqual(meu - deles, set(), "fronteiras so no script")
        self.assertEqual(deles - meu, set(), "fronteiras so no objdump")

    def test_os_corpos_medidos(self):
        tamanhos = [self.img.va_to_offset(h.end - 1) + 1
                    - self.img.va_to_offset(h.addr) for h in self.m.handlers]
        self.assertEqual(sum(tamanhos), 36983)
        self.assertEqual((min(tamanhos), max(tamanhos)), (1, 2378))


if __name__ == "__main__":
    unittest.main()
