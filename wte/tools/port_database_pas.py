#!/usr/bin/env python3
"""Transpila a camada de dados do we2002_core para Object Pascal -- WTE-TASK-17.

## O limite duro, e ele e a razao de este arquivo existir

**Este transpilador digere APENAS codigo deste repositorio.** A entrada e o
`src/core/` -- `Database.cpp`, `Player.cpp`, `CdImage.cpp`, `TextCodec.cpp` e
`Types.hpp` --, que ja e byte-identico ao `ed.exe` nas duas ROMs e esta sob
teste golden.

**Nunca aponte-o para saida de decompilador.** (PLAN-WTE-LAZARUS §8.10.) A
tentacao aparece quando a fase 4 fica cara: o decompilador cospe C++, o
transpilador engole C++, parece que fecha. Nao fecha. O `FORBIDDEN` abaixo so
segura porque a entrada e um subconjunto conhecido e pequeno, escrito por nos;
contra saida de decompilador -- que tem aritmetica de ponteiro, `undefined4`,
variaveis sinteticas e fluxo reconstruido -- ele deixa de recusar o que importa
e o gerador passa a emitir Pascal que compila, passa em teste unitario e grava
bytes errados. Codigo quebrado com cara de certo e o pior resultado possivel
deste projeto.

## Os dois guards

**`FORBIDDEN`** recusa emitir se sobrar construcao sem traducao Pascal decidida.
No `tools/port_database.py` -- o precedente direto, que fez MFC -> C++ portavel
-- ele pegou dois erros na fase 2 do port Qt. Aqui a lista muda de conteudo:
em vez de construcao MFC, e construcao C++ que o mapeamento de
`wte/re/tipos.md` nao cobre.

**`check_seeks()`** conta seek absoluto e relativo na entrada e na saida e
recusa se nao baterem. Existe por um bug real: uma regex com `[^,]` atravessou
uma quebra de linha e trocou um `Seek(begin)` por um `SeekCurrent`. Compilava,
passava nos testes, passava no ASan -- so o confronto com o `ed.exe` mostrou.
**Ele vale MAIS aqui, nao menos:** `Seek(x, soBeginning)` e `Seek(x, soCurrent)`
tem a mesma cara, e o mesmo erro e igualmente silencioso.

Lembrete que o precedente carrega e vale aqui: ao escrever regra nova em `SUBS`,
**`[^x]` casa `\\n`**. Use `[^x\\n]` sempre que a regra nao puder atravessar
linha.

## O que ele NAO faz

Nao e um compilador de C++. Ele cobre o subconjunto medido na entrada -- laco de
contagem fixa, `if`/`else`, `switch` sem fallthrough, atribuicao, aritmetica
inteira, indexacao de array, chamada de metodo. Qualquer coisa fora disso vira
recusa com arquivo, linha e motivo, e a recusa e **trabalho identificado**, nao
falha: a WTE-TASK-18 decide, para cada uma, entre estender a tabela, ajustar a
entrada ou portar aquele trecho a mao.

Uso:
    python3 wte/tools/port_database_pas.py            # escreve
    python3 wte/tools/port_database_pas.py --check    # confere
    python3 wte/tools/port_database_pas.py --report   # so lista as recusas
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "src" / "core"
OUT_DIR = ROOT / "wte" / "src"

# Entrada -> unidade, em ordem de dependencia.
UNITS: list[tuple[str, list[str]]] = [
    ("we2002_types", ["include/we2002/Types.hpp"]),
    ("we2002_team", ["include/we2002/Team.hpp", "Team.cpp"]),
    ("we2002_cdimage", ["include/we2002/CdImage.hpp", "CdImage.cpp"]),
    ("we2002_textcodec", ["include/we2002/TextCodec.hpp", "TextCodec.cpp"]),
    ("we2002_player", ["include/we2002/Player.hpp", "Player.cpp"]),
    ("we2002_database", ["include/we2002/Database.hpp", "Database.cpp"]),
]

# O que fica DE FORA do transpilador, cada um com o motivo. Nao e comentario
# solto: o `test_nenhuma_entrada_do_core_fica_de_fora` cruza esta lista com o
# que existe em `src/core/`, e reprova se sobrar arquivo que ninguem reivindicou.
#
# A guarda existe porque a ausencia ja aconteceu: a primeira versao do UNITS
# esquecia `Team.hpp` e `Team.cpp` -- que declaram `Team`, `MlTeam` e
# `Formation`, os tres registros que `Database.hpp:45-48` usa como campo -- e
# NADA no `--check` acusou. Quem apanhou foi a revisao humana da WTE-TASK-15
# (CORR-WTE-034). Arquivo esquecido em silencio e pior que recusa alta: a
# camada de dados sairia incompleta com todos os gates verdes.
FORA_DO_TRANSPILADOR: dict[str, str] = {
    "Sofifa.cpp": (
        "o import do SoFIFA esta desligado no newWe2002 desde 2026-08-05, o "
        "editor do Obocaman nao tem nada equivalente, e as linhas nao teriam "
        "consumidor. Decisao registrada na WTE-TASK-18."
    ),
    "include/we2002/Sofifa.hpp": "idem Sofifa.cpp",
    "Tables.cpp": "e do gen_tables_pas.py (WTE-TASK-16), nao deste gerador",
    "include/we2002/Tables.hpp": "idem Tables.cpp",
    "include/we2002/Offsets.hpp": "idem Tables.cpp",
}


class Refusal(RuntimeError):
    """Recusa do transpilador. Sempre com arquivo, linha e motivo."""


@dataclass(frozen=True)
class Nota:
    arquivo: str
    linha: int
    motivo: str

    def __str__(self) -> str:
        return f"{self.arquivo}:{self.linha}: {self.motivo}"


# ============================================================== 1. FORBIDDEN ==
#
# Construcao que NAO pode sobreviver ate a emissao. Cada uma com o motivo pelo
# qual nao ha traducao Pascal decidida -- a mensagem e o que a WTE-TASK-18 le
# para escolher a rota, entao ela diz o problema, nao so o nome.
#
# A ordem importa so para a legibilidade do relatorio; todas sao conferidas.

FORBIDDEN: list[tuple[str, str]] = [
    # -- contêiner e abstracao da STL -------------------------------------
    (r"\bstd::(?:vector|map|unordered_map|set|list|deque|array)\b",
     "conteiner da STL: wte/re/tipos.md manda RECUSAR em vez de improvisar "
     "equivalente Pascal (a decisao 'o que nao entra na camada de dados')"),
    (r"\bstd::function\b",
     "std::function: so o Reporter usa, e ele vira "
     "`TReporter = procedure(const Msg: string) of object`. Se aparecer "
     "noutro lugar, o mapeamento nao cobre"),
    (r"\bstd::(?:sort|find|copy|fill|max|min|transform|accumulate)\b",
     "<algorithm>: sem equivalente decidido; a entrada nao deveria usar"),
    (r"\[\s*[&=]?\s*\]\s*\(", "lambda: sem traducao decidida"),
    (r"\btemplate\s*<", "template: fora do subconjunto"),

    # -- ponteiro ----------------------------------------------------------
    (r"\breinterpret_cast\b",
     "reinterpret_cast: reinterpretar memoria por regra textual e como o "
     "bitfield embaralhou numero de camisa no newWe2002. Porte a mao"),
    (r"\bconst_cast\b", "const_cast: sem traducao decidida"),
    (r"\bdynamic_cast\b", "dynamic_cast: fora do subconjunto"),
    (r"\bnew\b\s+\w", "new: a camada de dados nao aloca"),
    (r"\bdelete\b", "delete: a camada de dados nao aloca"),
    (r"(?<![\w>\]\)])\w+\s*\+\+?\s*\+\s*\d+\s*\)\s*\+\+",
     "aritmetica de ponteiro"),

    # -- fluxo -------------------------------------------------------------
    (r"\bgoto\b", "goto: nao ha rotulo no Pascal gerado"),
    (r"\[\[fallthrough\]\]",
     "fallthrough de switch: o `case` do Pascal NAO cai para o proximo ramo. "
     "Traduzir literalmente muda o comportamento em silencio -- e este e um "
     "`case` que decide QUANTOS bytes ler da imagem. Duplique o ramo ou "
     "reescreva como if/else, e registre em wte/re/recusas.md"),
    (r"\?[^;\n]*:[^;\n]*;",
     "operador ternario: sem traducao textual segura (o `:` colide com a "
     "sintaxe de rotulo e de tipo)"),

    # -- resto -------------------------------------------------------------
    (r"\bsizeof\b",
     "sizeof: o SizeOf do FPC existe, mas o tamanho pode DIVERGIR do C++ "
     "(alinhamento e packing). Cada uso precisa de decisao escrita"),
    (r"\bstatic_assert\b", "static_assert: sem equivalente; vira teste"),
    (r"\bunion\b", "union: sem traducao decidida"),
    (r"\bstd::(?:cout|cerr|cin)\b", "iostream: a camada de dados nao imprime"),
    (r"\bprintf\b|\bsprintf\b", "printf: sem traducao decidida"),
    (r"\b_itoa\b", "_itoa: CRT so do MSVC"),
    (r"#\s*(?:ifdef|ifndef|if)\b",
     "compilacao condicional: a saida seria dependente de plataforma, que e "
     "exatamente o que a regra zero de wte/re/tipos.md proibe"),
    # -- estrutura: o passe que AINDA NAO EXISTE -----------------------------
    #
    # Achado da WTE-TASK-17, e o item que re-dimensiona a 18: o
    # `tools/port_database.py` pode ser substituicao textual pura porque a
    # fonte e o alvo dele sao a MESMA linguagem (C++ MFC -> C++ portavel).
    # C++ -> Pascal nao pode: bloco, cabecalho de laco, assinatura de funcao e
    # declaracao de variavel nao tem forma comum, e nenhuma regex os alcanca
    # sem uma passagem estrutural com casamento de chave.
    #
    # Enquanto esse passe nao existir, a estrutura e RECUSA -- e nao "sai como
    # esta". A alternativa seria emitir um arquivo com extensao .pas, cabecalho
    # de unidade e corpo em C++: um artefato que parece camada de dados, nao
    # compila, e convida alguem a "so ajustar a mao" exatamente o que o §4.4
    # proibe.
    (r"^\s*\{\s*$|^\s*\}\s*;?\s*$",
     "bloco `{ }`: o passe estrutural (begin/end) nao esta implementado -- "
     "WTE-TASK-18"),
    (r"\bfor\s*\([^;\n]*;[^;\n]*;[^)\n]*\)",
     "cabecalho de `for` no estilo C: vira `for .. to .. do` (passo 1) ou "
     "`while` (passo != 1), e isso e passe estrutural -- WTE-TASK-18"),
    (r"^\s*(?:void|LongInt|Boolean|Byte|Word|LongWord|Int64|Double)\s+"
     r"[\w:]+\s*\([^)\n]*\)\s*$",
     "assinatura de funcao: vira `procedure`/`function` com `var` hoisted -- "
     "WTE-TASK-18"),
    (r"^\s*struct\s+\w+\s*\{?",
     "declaracao de `struct`: vira `record`, com a decisao de `packed` por "
     "campo (tipos.md) -- WTE-TASK-18"),

    # Sobra de C++ que so aparece se uma regra de SUBS falhou em casar.
    (r"->", "'->' sobrou: alguma regra de SUBS nao casou"),
    (r"\bstd::", "'std::' sobrou: alguma regra de SUBS nao casou"),
    (r"(?<![<>=!+\-*/%&|^])==(?![=])", "'==' sobrou: regra de comparacao falhou"),
    (r"!=", "'!=' sobrou: regra de comparacao falhou"),
    (r"&&|\|\|", "'&&'/'||' sobrou: regra booleana falhou"),
]

# Recusa que so vale ANTES da traducao -- depois da traducao o token some ou
# muda de sentido. Separada porque conferir `==` antes da traducao acusaria a
# entrada inteira.
FORBIDDEN_ENTRADA: list[tuple[str, str]] = [
    (r"\bstd::(?:vector|map|unordered_map|set|list|deque)\b",
     "conteiner da STL na entrada"),
    (r"\[\[fallthrough\]\]", "fallthrough de switch na entrada"),
    (r"\bgoto\b", "goto na entrada"),
    (r"\btemplate\s*<", "template na entrada"),
    (r"\breinterpret_cast\b", "reinterpret_cast na entrada"),
]


def mascarar(texto: str) -> str:
    """Apaga comentario e literal, preservando posicao e numero de linha.

    Sem isto o `FORBIDDEN` acusa o comentario `// the new national sides are
    elsewhere` como uso de `new` -- o que ja aconteceu, duas vezes, na primeira
    execucao contra o `Database.cpp`. Recusa falsa e pior que ruido: ela manda a
    WTE-TASK-18 investigar trabalho que nao existe, e ensina a ignorar o guard.

    Cada caractere apagado vira espaco, e a quebra de linha fica -- a linha
    reportada continua sendo a linha real do arquivo.
    """
    def branco(m: re.Match[str]) -> str:
        return "".join("\n" if c == "\n" else " " for c in m.group(0))

    # Ordem: bloco, linha, literal de string, literal de caractere.
    texto = re.sub(r"/\*.*?\*/", branco, texto, flags=re.S)
    texto = re.sub(r"//[^\n]*", branco, texto)
    texto = re.sub(r'"(?:[^"\\\n]|\\.)*"', branco, texto)
    texto = re.sub(r"'(?:[^'\\\n]|\\.)*'", branco, texto)
    return texto


def conferir(padroes: list[tuple[str, str]], texto: str,
             arquivo: str) -> list[Nota]:
    """Recusas encontradas em `texto`, com a linha de cada ocorrencia.

    Varre o texto **mascarado**: comentario e literal nao sao codigo.
    """
    alvo = mascarar(texto)
    notas: list[Nota] = []
    for padrao, motivo in padroes:
        for m in re.finditer(padrao, alvo, flags=re.M):
            linha = alvo.count("\n", 0, m.start()) + 1
            notas.append(Nota(arquivo, linha, motivo))
    return sorted(set(notas), key=lambda n: (n.arquivo, n.linha, n.motivo))


# =============================================================== 2. os SUBS ==
#
# (padrao, substituto, razao), aplicados NA ORDEM. A ordem e significativa: as
# regras de comparacao tem de rodar antes da regra de atribuicao, senao `==`
# vira `:==`.
#
# ARMADILHA que o precedente pagou e que vale aqui: `[^x]` casa `\n`. Toda
# regra que nao pode atravessar linha escreve `[^x\n]`.

SUBS: list[tuple[str, str, str]] = [
    # --- comentario: `//` ja e valido no Object Pascal ---------------------
    # Nada a fazer, e isso e um ganho de fidelidade: os comentarios do
    # we2002_core -- que explicam CADA salto de setor -- atravessam intactos.

    # --- comparacao, ANTES da atribuicao ----------------------------------
    (r"(?<![<>=!+\-*/%&|^])==(?!=)", "\x00EQ\x00", "== -> = (marcado)"),
    (r"!=", "<>", "!= -> <>"),
    (r"<=", "\x00LE\x00", "<= (protegido de <)"),
    (r">=", "\x00GE\x00", ">= (protegido de >)"),

    # --- booleano ---------------------------------------------------------
    (r"&&", " and ", "&& -> and"),
    (r"\|\|", " or ", "|| -> or"),
    (r"!\s*(?=\w|\()", "not ", "! -> not"),

    # --- bit a bit --------------------------------------------------------
    (r"(?<![\w\s])\s*<<\s*", " shl ", "<< -> shl"),
    (r"(?<![\w\s])\s*>>\s*", " shr ", ">> -> shr"),
    (r"(?<=\w)\s*%\s*(?=\w)", " mod ", "% -> mod"),

    # --- membro e endereco ------------------------------------------------
    (r"->", ".", "-> -> ."),
    # `&x` como argumento de Read/Write vira parametro `var` sem tipo: o
    # Pascal ja passa por referencia, e o `&` nao tem equivalente.
    (r"(?<=[(,])\s*&(?=\w)", "", "& de argumento (Pascal passa por var)"),

    # --- tipo, conforme wte/re/tipos.md ------------------------------------
    # Largura FIXA em tudo que toca a imagem, e a regra existe por um bug real:
    # `DWORD` virou 64-bit no Linux LP64 e embaralhou todos os numeros de
    # camisa do newWe2002.
    #
    # Proibidos por serem de largura VARIAVEL em FPC: `Integer` (16 bits em
    # {$mode tp}), `Cardinal`, `PtrInt`, `PtrUInt` e `NativeInt` (seguem o
    # ponteiro). `LongInt` e `LongWord` NAO estao nessa lista -- sao 32 bits
    # por definicao do FPC, e e por isso que a tabela abaixo os emite.
    #
    # `SizeInt` e o unico caso com ressalva: ele segue o ponteiro, entao so
    # aparece na FRONTEIRA do CdImage (contagem de bytes lidos), nunca em campo
    # de registro. A regra 8 abaixo e a que o coloca la, e so la.
    #
    # A "regra zero" do tipos.md enuncia isso listando `SizeInt` e `LongInt`
    # entre os proibidos e usando os dois na tabela logo abaixo -- contradicao
    # que a CORR-WTE-032 registra. Este comentario diz a versao que o codigo
    # aqui de fato aplica; quem reconcilia o tipos.md e aquela correcao.
    #
    # Estas rodam DEPOIS de `->` e ANTES da atribuicao, e cada uma tem `\b` nas
    # duas pontas para nao comer prefixo (`unsigned char` antes de `char`).
    (r"\bstd::uint8_t\b", "Byte", "uint8_t -> Byte"),
    (r"\bstd::uint16_t\b", "Word", "uint16_t -> Word"),
    (r"\bstd::uint32_t\b", "LongWord", "uint32_t -> LongWord (nunca Cardinal)"),
    (r"\bstd::int32_t\b", "LongInt", "int32_t -> LongInt"),
    (r"\bstd::int64_t\b", "Int64", "int64_t -> Int64"),
    (r"\bstd::size_t\b", "SizeInt", "size_t -> SizeInt (so na fronteira)"),
    (r"\bunsigned\s+short\b", "Word", "unsigned short -> Word"),
    (r"\bunsigned\s+char\b", "Byte", "unsigned char -> Byte"),
    (r"\bunsigned\s+int\b", "LongWord", "unsigned int -> LongWord"),
    (r"\bbool\b", "Boolean", "bool -> Boolean"),
    (r"\bdouble\b", "Double", "double -> Double"),

    # `= delete` nas copias: em C++ e uma declaracao que APAGA uma operacao, e
    # nao ha comportamento para traduzir. Some da saida; o `TObject` do Pascal
    # nao e copiavel por valor de qualquer jeito, entao a intencao se preserva
    # sozinha. Registrado em wte/re/transpilador.md.
    (r"^\s*\w[\w:&<>\s\*]*\([^;\n]*\)\s*=\s*delete\s*;\s*$\n?", "",
     "= delete (operacao apagada, sem comportamento)"),

    # --- cast -------------------------------------------------------------
    (r"static_cast<\s*int\s*>\s*\(", "LongInt(", "static_cast<int>"),
    (r"static_cast<\s*unsigned int\s*>\s*\(", "LongWord(",
     "static_cast<unsigned int>"),
    (r"\(unsigned char\s*\*\)\s*", "", "cast para unsigned char* (var sem tipo)"),
    (r"\(char\)\s*", "", "cast (char): o ShortInt ja tem sinal"),

    # --- CdImage ----------------------------------------------------------
    # As duas regras de seek: cada uma casa a forma JA produzida pelo core, e
    # o check_seeks() confere a contagem das duas nas duas pontas.
    (r"\.Seek\(([^;\n]+?)\);", r".Seek(\1, soBeginning);", "Seek -> soBeginning"),
    (r"\.SeekCurrent\(([^;\n]+?)\);", r".Seek(\1, soCurrent);",
     "SeekCurrent -> soCurrent"),

    # --- cadeia com semantica de C ---------------------------------------
    # `strcpy`/`strcat` copiam ATE o NUL inclusive, sem checar limite. O
    # equivalente Pascal e emitido pelo preambulo (CStrCopy/CStrCat); nao usar
    # StrPCopy/StrLCopy, que truncam de outro jeito. Ver tipos.md, decisao 1.
    (r"\bstd::strcpy\b", "CStrCopy", "strcpy -> CStrCopy"),
    (r"\bstrcpy\b", "CStrCopy", "strcpy -> CStrCopy"),
    (r"\bstd::strcat\b", "CStrCat", "strcat -> CStrCat"),
    (r"\bstrcat\b", "CStrCat", "strcat -> CStrCat"),
    (r"\bstd::strlen\b", "CStrLen", "strlen -> CStrLen"),
    (r"\bstrlen\b", "CStrLen", "strlen -> CStrLen"),

    # --- literal ----------------------------------------------------------
    (r'"([^"\n]*)"', r"'\1'", "literal de string"),

    # --- atribuicao (DEPOIS das comparacoes) ------------------------------
    (r"(?<![<>=!+\-*/%&|^:])=(?![=])", ":=", "= -> :="),

    # --- desmarcar o que foi protegido ------------------------------------
    (r"\x00EQ\x00", "=", "restaura ="),
    (r"\x00LE\x00", "<=", "restaura <="),
    (r"\x00GE\x00", ">=", "restaura >="),

    # --- incremento e decremento -----------------------------------------
    (r"(\w+(?:\[[^\]\n]*\])?)\s*\+=\s*([^;\n]+);", r"\1 := \1 + \2;", "+="),
    (r"(\w+(?:\[[^\]\n]*\])?)\s*-=\s*([^;\n]+);", r"\1 := \1 - \2;", "-="),
    (r"(\w+(?:\[[^\]\n]*\])?)\s*\+\+\s*;", r"Inc(\1);", "x++"),
    (r"\+\+\s*(\w+(?:\[[^\]\n]*\])?)\s*;", r"Inc(\1);", "++x"),
    (r"(\w+(?:\[[^\]\n]*\])?)\s*--\s*;", r"Dec(\1);", "x--"),
    (r"--\s*(\w+(?:\[[^\]\n]*\])?)\s*;", r"Dec(\1);", "--x"),
]


def aplicar_subs(texto: str) -> tuple[str, dict[str, int]]:
    contagem: dict[str, int] = {}
    for padrao, repl, razao in SUBS:
        texto, n = re.subn(padrao, repl, texto, flags=re.M)
        if n:
            contagem[razao] = contagem.get(razao, 0) + n
    return texto, contagem


# ============================================================ 3. check_seeks ==

def check_seeks(antes: str, depois: str, onde: str) -> list[Nota]:
    """Cada seek tem de manter a direcao que tinha na entrada.

    O `FORBIDDEN` nao ve isto: uma regra que troca seek absoluto por relativo
    nao deixa token nenhum para tras, e o resultado compila. Ja aconteceu no
    `tools/port_database.py` -- a regex com `[^,]` atravessando a quebra de
    linha -- e custou uma tabela de custo corrompida que so o `ed.exe`
    denunciou.

    Em Pascal o risco e MAIOR: `Seek(x, soBeginning)` e `Seek(x, soCurrent)`
    diferem por uma palavra no meio da chamada, e nao por um nome de metodo.
    """
    notas: list[Nota] = []
    for entrada_pat, saida_pat, direcao in (
        (r"\.Seek\(", r"\.Seek\([^;\n]*soBeginning\s*\)", "absoluto"),
        (r"\.SeekCurrent\(", r"\.Seek\([^;\n]*soCurrent\s*\)", "relativo"),
    ):
        quer = len(re.findall(entrada_pat, antes))
        tem = len(re.findall(saida_pat, depois))
        if quer != tem:
            notas.append(Nota(
                onde, 0,
                f"{quer} seek(s) {direcao} na entrada e {tem} na saida -- "
                f"uma regra de SUBS trocou a direcao de um seek, que e "
                f"exatamente o bug que este guard existe para pegar"))
    return notas


# ================================================================ 4. emissao ==

CABECALHO = """\
{{ GERADO por wte/tools/port_database_pas.py -- NAO editar a mao.

  Transpilado de {fontes}, que ja e byte-identico ao `ed.exe` nas duas ROMs.
  A entrada do transpilador e SEMPRE codigo deste repositorio -- nunca saida de
  decompilador (PLAN-WTE-LAZARUS §8.10).

  Os seeks, os comprimentos de leitura e os limites de laco estao intocados:
  eles codificam o layout MODE2/2352 da imagem, inclusive os saltos manuais
  sobre cabecalho de setor.

  Regenerar:  python3 wte/tools/port_database_pas.py
  Conferir:   python3 wte/tools/port_database_pas.py --check }}

unit {unit};

{{$mode objfpc}}{{$H+}}

interface
"""


def emitir_cabecalho(unit: str, fontes: list[str]) -> str:
    return CABECALHO.format(unit=unit, fontes=", ".join(fontes))


OUT_DOC = ROOT / "wte" / "re" / "transpilador.md"


def emitir_doc(notas: list[Nota]) -> str:
    """`wte/re/transpilador.md`: a tabela de substituição e o que ela recusa.

    Gerado, e não escrito à mão, para que nenhum número aqui venha de contagem
    de olho — a armadilha 11 do `progresso.md`. Ele é também o worklist da
    WTE-TASK-18: cada recusa com arquivo, linha e o porquê de não haver
    tradução decidida.
    """
    por_motivo: dict[str, list[Nota]] = {}
    for n in notas:
        por_motivo.setdefault(n.motivo, []).append(n)

    L: list[str] = []
    def w(s: str = "") -> None:
        L.append(s)

    w("# O transpilador da camada de dados — a tabela e as recusas")
    w()
    w("**GERADO por `wte/tools/port_database_pas.py` — não editar à mão.**")
    w("Regenerar: `python3 wte/tools/port_database_pas.py`.")
    w()
    w("Produto da [WTE-TASK-17](../../docs/tasks/"
      "17-transpilador-da-camada-de-dados.md). A lista de recusas abaixo é o")
    w("worklist da [WTE-TASK-18](../../docs/tasks/18-camada-de-dados-gerada.md).")
    w()
    w("---")
    w()
    w("## O limite duro")
    w()
    w("**A entrada é sempre código deste repositório.** Nunca saída de "
      "decompilador —")
    w("[`PLAN-WTE-LAZARUS.md`](../../docs/PLAN-WTE-LAZARUS.md) §8.10. O `FORBIDDEN` "
      "só segura porque")
    w("a entrada é um subconjunto conhecido e pequeno; contra decompilado ele "
      "deixa de")
    w("recusar o que importa e o gerador passa a emitir Pascal que compila, "
      "passa em teste")
    w("unitário e **grava bytes errados**.")
    w()
    w("## Entrada")
    w()
    w("| Unidade Pascal | Origem em `src/core/` | Linhas |")
    w("|---|---|---|")
    total = 0
    for unit, arquivos in UNITS:
        n = sum(len((CORE / a).read_text(encoding="utf-8").splitlines())
                for a in arquivos)
        total += n
        w(f"| `{unit}.pas` | " + ", ".join(f"`{a}`" for a in arquivos)
          + f" | {n} |")
    w(f"| **Total** | | **{total}** |")
    w()
    w("### O que fica de fora, e por quê")
    w()
    w("Lista fechada: o `test_nenhuma_entrada_do_core_fica_de_fora` cruza-a com "
      "o que")
    w("existe em `src/core/` e **reprova** se sobrar arquivo que ninguém "
      "reivindicou —")
    w("nos dois sentidos, então motivo escrito para arquivo que sumiu também "
      "reprova.")
    w()
    w("| Arquivo | Motivo |")
    w("|---|---|")
    for nome, motivo in sorted(FORA_DO_TRANSPILADOR.items()):
        w(f"| `{nome}` | {motivo} |")
    w()
    w("A guarda existe porque a ausência **já aconteceu**: a primeira versão do")
    w("`UNITS` esqueceu `Team.hpp` e `Team.cpp` — que declaram `Team`, "
      "`MlTeam` e")
    w("`Formation`, os três registros que `Database.hpp:45-48` usa como campo — "
      "e nada")
    w("no `--check` acusou. Quem apanhou foi revisão humana "
      "([CORR-WTE-034](../../docs/tasks/CORR-WTE-034.md)).")
    w("Arquivo esquecido em silêncio é o pior modo de falha aqui: a camada de "
      "dados")
    w("sairia incompleta com todos os gates verdes.")
    w()
    w("---")
    w()
    w(f"## A tabela de substituição — {len(SUBS)} regras, aplicadas em ordem")
    w()
    w("A ordem é significativa: as regras de comparação rodam **antes** da "
      "regra de")
    w("atribuição, senão `==` viraria `:==`.")
    w()
    w("| # | Razão | Padrão |")
    w("|---|---|---|")
    for i, (padrao, _, razao) in enumerate(SUBS, 1):
        p = padrao.replace("|", "\\|").replace("\x00", "\\0")
        w(f"| {i} | {razao} | `{p}` |")
    w()
    w("### A armadilha que o precedente pagou")
    w()
    w("**`[^x]` casa `\\n`.** Foi assim que um `Seek(begin)` virou "
      "`SeekCurrent` no")
    w("`tools/port_database.py`: compilava, passava nos testes, passava no "
      "ASan, e só o")
    w("confronto com o `ed.exe` mostrou. Toda regra que não pode atravessar "
      "linha escreve")
    w("`[^x\\n]`, e há um teste que reprova regra nova sem isso "
      "(`test_port_database_pas.py`).")
    w()
    w("---")
    w()
    w(f"## O que o `FORBIDDEN` recusa — {len(FORBIDDEN)} construções")
    w()
    w("Recusa não é falha: é **trabalho identificado**. Cada uma tem três "
      "saídas, e a")
    w("decisão vai escrita em `wte/re/recusas.md` (WTE-TASK-18) — estender a "
      "tabela,")
    w("ajustar a entrada, ou portar o trecho à mão.")
    w()
    w("| Construção | Por que não há tradução decidida |")
    w("|---|---|")
    for padrao, motivo in FORBIDDEN:
        p = padrao.replace("|", "\\|")
        w(f"| `{p}` | {motivo} |")
    w()
    w("Comentário e literal são **mascarados** antes da varredura. Sem isso o "
      "comentário")
    w("`// the new national sides are elsewhere` do `Database.cpp` era acusado "
      "como uso de")
    w("`new` — e recusa falsa manda a WTE-TASK-18 investigar trabalho que não "
      "existe.")
    w()
    w("---")
    w()
    w("## O segundo guard: `check_seeks()`")
    w()
    w("Conta seek absoluto e relativo na entrada e na saída e recusa se não "
      "baterem. O")
    w("`FORBIDDEN` não vê isto: uma regra que troca a direção de um seek não "
      "deixa token")
    w("nenhum para trás, e o resultado compila.")
    w()
    w("**Ele vale mais em Pascal, não menos.** `Seek(x, soBeginning)` e "
      "`Seek(x, soCurrent)`")
    w("diferem por uma palavra no meio da chamada, e não por um nome de "
      "método — a")
    w("diferença que em C++ era `Seek` contra `SeekCurrent`.")
    w()
    w("Estado medido nesta execução:")
    w()
    w("| Origem | `Seek` absoluto | `SeekCurrent` relativo |")
    w("|---|---|---|")
    for unit, arquivos in UNITS:
        for nome, texto in ler_fontes(unit, arquivos):
            a = len(re.findall(r"\.Seek\(", texto))
            r = len(re.findall(r"\.SeekCurrent\(", texto))
            if a or r:
                w(f"| `{nome}` | {a} | {r} |")
    w()
    w("---")
    w()
    w("## Recusas em aberto — o worklist da WTE-TASK-18")
    w()
    if not notas:
        w("**Nenhuma.** O transpilador emite as cinco unidades sem recusa.")
    else:
        w(f"**{len(notas)}** recusa(s), em {len(por_motivo)} motivo(s). "
          f"Enquanto houver qualquer uma,")
        w("**nada é emitido** — o transpilador não produz unidade parcial.")
        w()
        w("| Ocorrências | Onde | Motivo |")
        w("|---|---|---|")
        for motivo, ns in sorted(por_motivo.items(),
                                 key=lambda kv: (-len(kv[1]), kv[0])):
            locais = ", ".join(f"`{n.arquivo.split('/')[-1]}:{n.linha}`"
                               for n in ns[:5])
            if len(ns) > 5:
                locais += f" (+{len(ns) - 5})"
            w(f"| {len(ns)} | {locais} | {motivo} |")
    w()
    return "\n".join(L) + "\n"


# ==================================================================== 5. main ==

def ler_fontes(unit: str, arquivos: list[str]) -> list[tuple[str, str]]:
    fora = []
    for rel in arquivos:
        p = CORE / rel
        if not p.exists():
            raise Refusal(f"{rel}: entrada nao existe")
        fora.append((f"src/core/{rel}", p.read_text(encoding="utf-8")))
    return fora


def transpilar_unidade(unit: str, arquivos: list[str]) -> tuple[str, list[Nota]]:
    """Devolve (pascal, recusas). Com recusa, o Pascal NAO deve ser gravado."""
    fontes = ler_fontes(unit, arquivos)
    notas: list[Nota] = []

    for nome, texto in fontes:
        notas += conferir(FORBIDDEN_ENTRADA, texto, nome)

    corpo_partes = []
    for nome, texto in fontes:
        traduzido, _ = aplicar_subs(texto)
        notas += conferir(FORBIDDEN, traduzido, nome)
        notas += check_seeks(texto, traduzido, nome)
        corpo_partes.append(traduzido)

    pascal = emitir_cabecalho(unit, [n for n, _ in fontes])
    pascal += "\n" + "\n".join(corpo_partes) + "\nimplementation\n\nend.\n"
    return pascal, sorted(set(notas), key=lambda n: (n.arquivo, n.linha))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="nao escreve; sai 2 se a saida divergir do commitado")
    ap.add_argument("--report", action="store_true",
                    help="so lista as recusas, agrupadas por motivo")
    args = ap.parse_args(argv)

    todas: list[Nota] = []
    produzido: dict[Path, str] = {}
    for unit, arquivos in UNITS:
        try:
            pascal, notas = transpilar_unidade(unit, arquivos)
        except Refusal as exc:
            print(f"port_database_pas: RECUSA: {exc}", file=sys.stderr)
            return 1
        todas += notas
        if not notas:
            produzido[OUT_DIR / f"{unit}.pas"] = pascal

    if args.report or todas:
        por_motivo: dict[str, list[Nota]] = {}
        for n in todas:
            por_motivo.setdefault(n.motivo, []).append(n)
        print(f"port_database_pas: {len(todas)} recusa(s) em "
              f"{len(por_motivo)} motivo(s):", file=sys.stderr)
        for motivo, ns in sorted(por_motivo.items(),
                                 key=lambda kv: (-len(kv[1]), kv[0])):
            locais = ", ".join(f"{n.arquivo}:{n.linha}" for n in ns[:4])
            resto = f" (+{len(ns) - 4})" if len(ns) > 4 else ""
            print(f"  {len(ns):4}x {motivo}", file=sys.stderr)
            print(f"       {locais}{resto}", file=sys.stderr)

    if args.report:
        return 0

    # O `transpilador.md` sai SEMPRE, com recusa ou sem. Ele descreve o estado
    # do transpilador -- a tabela, o que ela recusa, e o worklist da
    # WTE-TASK-18 --, e esse estado existe mesmo com zero unidade emitida. E o
    # que da a `--check` algo real para medir enquanto a camada de dados nao
    # existe, em vez de um alvo verde sem nada medido.
    produzido[OUT_DOC] = emitir_doc(todas)

    rc = 0
    for path, texto in sorted(produzido.items()):
        rel = path.relative_to(ROOT)
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != texto:
                print(f"port_database_pas: {rel}: DIVERGE do gerador",
                      file=sys.stderr)
                rc = 2
            else:
                print(f"port_database_pas: {rel}: ok")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(texto, encoding="utf-8")
            print(f"port_database_pas: {rel}: {len(texto)} B")
    return rc


if __name__ == "__main__":
    sys.exit(main())
