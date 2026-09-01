#!/usr/bin/env python3
"""Transpila a camada de dados do we2002_core para Object Pascal -- WTE-TASK-17/18.

## O limite duro, e ele e a razao de este arquivo existir

**Este transpilador digere APENAS codigo deste repositorio.** A entrada e o
`src/core/` -- `Database.cpp`, `Player.cpp`, `CdImage.cpp`, `TextCodec.cpp`,
`Team.cpp` e os cabecalhos --, que ja e byte-identico ao `ed.exe` nas duas ROMs
e esta sob teste golden.

**Nunca aponte-o para saida de decompilador.** (PLAN-WTE-LAZARUS §8.10.) A
tentacao aparece quando a fase 4 fica cara: o decompilador cospe C++, o
transpilador engole C++, parece que fecha. Nao fecha. O `FORBIDDEN` abaixo so
segura porque a entrada e um subconjunto conhecido e pequeno, escrito por nos;
contra saida de decompilador -- que tem aritmetica de ponteiro, `undefined4`,
variaveis sinteticas e fluxo reconstruido -- ele deixa de recusar o que importa
e o gerador passa a emitir Pascal que compila, passa em teste unitario e grava
bytes errados. Codigo quebrado com cara de certo e o pior resultado possivel
deste projeto.

## As tres camadas

1. **`aplicar_subs()`** -- expressao e operador. Substituicao textual, na ordem.
2. **O passe estrutural** (WTE-TASK-18) -- bloco, laco, `switch`, assinatura,
   declaracao de campo. Regex nenhuma alcanca isso: C++ e Pascal nao tem forma
   comum para chave, cabecalho de `for` nem hoisting de variavel local.
3. **O porte a mao**, em `MANUAIS` e `TRECHOS_MANUAIS` -- o que o
   `wte/re/tipos.md` ja decidiu que NAO e transpilacao (o `CdImage` sobre
   `TFileStream`, o bitfield de `SquadNumbers` por mascara, o sidecar `_url.txt`
   byte a byte). Cada peca vai marcada na saida e registrada em
   `wte/re/recusas.md`.

## Os dois guards

**`FORBIDDEN`** recusa emitir se sobrar construcao sem traducao Pascal decidida.
No `tools/port_database.py` -- o precedente direto, que fez MFC -> C++ portavel
-- ele pegou dois erros na fase 2 do port Qt.

**`check_seeks()`** conta seek absoluto e relativo na entrada e na saida e
recusa se nao baterem. Existe por um bug real: uma regex com `[^,]` atravessou
uma quebra de linha e trocou um `Seek(begin)` por um `SeekCurrent`. Compilava,
passava nos testes, passava no ASan -- so o confronto com o `ed.exe` mostrou.
**Ele vale MAIS aqui, nao menos:** `Seek(x, soBeginning)` e `Seek(x, soCurrent)`
tem a mesma cara, e o mesmo erro e igualmente silencioso.

Lembrete que o precedente carrega e vale aqui: ao escrever regra nova em `SUBS`,
**`[^x]` casa `\\n`**. Use `[^x\\n]` sempre que a regra nao puder atravessar
linha.

## O terceiro guard, novo na WTE-TASK-18: nada sai em silencio

`itens_reivindicados()` cruza TODO item de topo de cada entrada -- funcao,
classe, constante -- com o que foi transpilado ou reivindicado por um porte a
mao. Item que ninguem reivindica **recusa**. A ausencia silenciosa ja custou
uma revisao humana inteira (CORR-WTE-034): o `UNITS` esquecia `Team.hpp` e nada
no `--check` acusava.

Uso:
    python3 wte/tools/port_database_pas.py            # escreve
    python3 wte/tools/port_database_pas.py --check    # confere
    python3 wte/tools/port_database_pas.py --report   # so lista as recusas
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
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

FORBIDDEN: list[tuple[str, str]] = [
    # -- conteiner e abstracao da STL -------------------------------------
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
    (r"\bcontinue\b",
     "continue: o passe estrutural traduz `for` de passo != 1 para `while` com "
     "o incremento no FIM do corpo. Um `continue` pularia esse incremento e "
     "faria laco infinito -- silencioso, e so contra a imagem apareceria"),
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

    # -- estrutura que sobrou -----------------------------------------------
    #
    # O passe estrutural da WTE-TASK-18 consome bloco, `for`, assinatura e
    # `struct`. Se algum chegar ate a emissao, o passe deixou de reconhecer a
    # forma -- e o `.pas` sairia com corpo em C++: um artefato que parece
    # camada de dados, nao compila, e convida alguem a "so ajustar a mao"
    # exatamente o que o §4.4 proibe.
    (r"^\s*\{\s*$|^\s*\}\s*;?\s*$",
     "bloco `{ }` sobrou: o passe estrutural nao reconheceu a forma"),
    (r"\bfor\s*\([^;\n]*;[^;\n]*;[^)\n]*\)",
     "cabecalho de `for` no estilo C sobrou: o passe estrutural nao "
     "reconheceu a forma"),
    (r"^\s*(?:void|LongInt|Boolean|Byte|Word|LongWord|Int64|Double)\s+"
     r"[\w:]+\s*\([^)\n]*\)\s*$",
     "assinatura de funcao sobrou: o passe estrutural nao reconheceu a forma"),
    (r"^\s*struct\s+\w+\s*\{?",
     "declaracao de `struct` sobrou: o passe estrutural nao reconheceu a "
     "forma"),
    (r"\bswitch\s*\(", "`switch` sobrou: o passe estrutural nao reconheceu a "
                       "forma"),

    # Sobra de C++ que so aparece se uma regra de SUBS falhou em casar.
    (r"->", "'->' sobrou: alguma regra de SUBS nao casou"),
    (r"\bstd::", "'std::' sobrou: alguma regra de SUBS nao casou"),
    (r"(?<![<>=!+\-*/%&|^])==(?![=])", "'==' sobrou: regra de comparacao falhou"),
    (r"!=", "'!=' sobrou: regra de comparacao falhou"),
    (r"&&|\|\|", "'&&'/'||' sobrou: regra booleana falhou"),
    (r"&",
     "'&' sobrou: nem endereco-de com rotina classificada nem bit-a-bit. "
     "Classifique a rotina em CALLEE_VAR_SEM_TIPO ou CALLEE_PONTEIRO"),
    (r"\b0[xX][0-9a-fA-F]+", "literal hexadecimal em forma de C sobrou"),
]

# Recusa que so vale ANTES da traducao -- depois da traducao o token some ou
# muda de sentido. Separada porque conferir `==` antes da traducao acusaria a
# entrada inteira.
FORBIDDEN_ENTRADA: list[tuple[str, str]] = [
    (r"\bstd::(?:vector|map|unordered_map|set|list|deque)\b",
     "conteiner da STL na entrada"),
    (r"\bgoto\b", "goto na entrada"),
    (r"\btemplate\s*<", "template na entrada"),
    (r"\breinterpret_cast\b", "reinterpret_cast na entrada"),
]


def mascarar(texto: str, pascal: bool = False) -> str:
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

    # Ordem: bloco, linha, chave (comentario do Pascal), literal de string,
    # literal de caractere.
    texto = re.sub(r"/\*.*?\*/", branco, texto, flags=re.S)
    texto = re.sub(r"//[^\n]*", branco, texto)
    if pascal:
        # Comentario `{ }` do Pascal atravessa linha. Na entrada C++ `{` e `}`
        # sao BLOCO, entao mascarar em varias linhas apagaria corpo de funcao
        # inteiro -- dai o parametro.
        texto = re.sub(r"\{[^{}]*\}", branco, texto, flags=re.S)
    texto = re.sub(r'"(?:[^"\\\n]|\\.)*"', branco, texto)
    texto = re.sub(r"'(?:[^'\n]|'')*'", branco, texto)
    return texto


def conferir(padroes: list[tuple[str, str]], texto: str,
             arquivo: str, pascal: bool = False) -> list[Nota]:
    """Recusas encontradas em `texto`, com a linha de cada ocorrencia.

    Varre o texto **mascarado**: comentario e literal nao sao codigo.
    """
    alvo = mascarar(texto, pascal=pascal)
    notas: list[Nota] = []
    for padrao, motivo in padroes:
        for m in re.finditer(padrao, alvo, flags=re.M):
            linha = alvo.count("\n", 0, m.start()) + 1
            notas.append(Nota(arquivo, linha, motivo))
    return sorted(set(notas), key=lambda n: (n.arquivo, n.linha, n.motivo))


# ====================================== 2. endereco-de, por rotina chamada ==
#
# `&x` em argumento nao tem UMA traducao: depende do que a rotina espera.
#
#   image_file.Read(&teams[i].flag_colours, 32)  -> parametro `var` sem tipo,
#                                                   o `&` SOME
#   ResolveMlLink(&link_euro_allstar[i * 2])     -> parametro PByte,
#                                                   o `&` vira `@`
#
# A regra unica que a WTE-TASK-17 tinha (apagar todo `&` depois de `(` ou `,`)
# acertava o primeiro caso e **quebrava o segundo em silencio**: passaria um
# Byte onde a rotina espera um ponteiro. Dai a tabela, e dai o `&` na lista do
# FORBIDDEN -- rotina nao classificada nao emite nada.

CALLEE_VAR_SEM_TIPO = {
    "Read", "Write",            # TCdImage, parametros `var Buffer` sem tipo
    "CStrCopy", "CStrCat", "CStrLen",
}

CALLEE_PONTEIRO = {
    "ResolveMlLink",            # lk: PByte
    "KanjiToAscii", "AsciiToKanji",
}


def _callee_de(texto: str, pos: int) -> str:
    """Nome da rotina cuja lista de argumentos contem a posicao `pos`."""
    profundidade = 0
    i = pos - 1
    while i >= 0:
        c = texto[i]
        if c == ")":
            profundidade += 1
        elif c == "(":
            if profundidade == 0:
                j = i - 1
                while j >= 0 and texto[j].isspace():
                    j -= 1
                fim = j + 1
                while j >= 0 and (texto[j].isalnum() or texto[j] in "_"):
                    j -= 1
                return texto[j + 1:fim]
            profundidade -= 1
        i -= 1
    return ""


def traduzir_enderecos(texto: str) -> str:
    """`&` unario em argumento: some ou vira `@`, conforme a rotina."""
    fora: list[str] = []
    i = 0
    while i < len(texto):
        c = texto[i]
        if c != "&" or texto[i:i + 2] == "&&" or (fora and fora[-1] == "&"):
            fora.append(c)
            i += 1
            continue
        # Unario so quando o que vem antes abre argumento ou operador.
        anterior = "".join(fora).rstrip()
        unario = anterior.endswith(("(", ",")) and texto[i + 1:i + 2].isidentifier()
        if not unario:
            fora.append(c)
            i += 1
            continue
        callee = _callee_de(texto, i)
        if callee in CALLEE_VAR_SEM_TIPO:
            pass                      # o `&` some: Pascal ja passa por `var`
        elif callee in CALLEE_PONTEIRO:
            fora.append("@")
        else:
            fora.append(c)            # nao classificada: o FORBIDDEN recusa
        i += 1
    return "".join(fora)


# =============================================== 3. precedencia de booleano ==
#
# Em C `==` liga mais forte que `&&`; em Pascal `and` liga mais forte que `=`.
# Traduzir `a == 1 && b > 2` literalmente da `a = 1 and b > 2`, que o FPC le
# como `a = (1 and b) > 2`. Nao e erro de compilacao em todos os casos -- e a
# forma mais perigosa de divergencia, porque compila e muda o resultado.

_COMPARACOES = ("==", "!=", "<=", ">=", "<", ">")


def _tem_comparacao_no_topo(s: str) -> bool:
    profundidade = 0
    i = 0
    while i < len(s):
        c = s[i]
        if c == "(":
            profundidade += 1
        elif c == ")":
            profundidade -= 1
        elif profundidade == 0:
            for op in _COMPARACOES:
                if s.startswith(op, i):
                    return True
        i += 1
    return False


def _partir_booleano(seg: str) -> list[str] | None:
    """Divide `seg` nos `&&`/`||` de profundidade zero. None se nao houver."""
    partes: list[str] = []
    ops: list[str] = []
    profundidade = 0
    inicio = 0
    i = 0
    while i < len(seg):
        c = seg[i]
        if c == "(":
            profundidade += 1
        elif c == ")":
            profundidade -= 1
        elif profundidade == 0 and seg[i:i + 2] in ("&&", "||"):
            partes.append(seg[inicio:i])
            ops.append(seg[i:i + 2])
            inicio = i + 2
            i += 2
            continue
        i += 1
    if not ops:
        return None
    partes.append(seg[inicio:])
    fora: list[str] = []
    for k, parte in enumerate(partes):
        nucleo = parte.strip()
        if nucleo and _tem_comparacao_no_topo(nucleo):
            esq = parte[:len(parte) - len(parte.lstrip())]
            dir_ = parte[len(parte.rstrip()):]
            parte = f"{esq}({nucleo}){dir_}"
        fora.append(parte)
        if k < len(ops):
            fora.append(ops[k])
    return fora


def parentizar_booleanos(texto: str) -> str:
    """Poe parenteses nos operandos de `&&`/`||` que contem comparacao."""
    fora: list[str] = []
    for seg in re.split(r"(;|\n)", texto):
        if seg in (";", "\n"):
            fora.append(seg)
            continue
        partes = _partir_booleano(seg)
        fora.append("".join(partes) if partes else seg)
    return "".join(fora)


# =============================================================== 4. os SUBS ==
#
# (padrao, substituto, razao), aplicados NA ORDEM. A ordem e significativa: as
# regras de comparacao tem de rodar antes da regra de atribuicao, senao `==`
# vira `:==`; e as compostas bit-a-bit (`&=`) antes de `&` virar `and`.
#
# ARMADILHA que o precedente pagou e que vale aqui: `[^x]` casa `\n`. Toda
# regra que nao pode atravessar linha escreve `[^x\n]`.

SUBS: list[tuple[str, str, str]] = [
    # --- comparacao, ANTES da atribuicao ----------------------------------
    (r"(?<![<>=!+\-*/%&|^])==(?!=)", "\x00EQ\x00", "== -> = (marcado)"),
    (r"!=", "<>", "!= -> <>"),
    (r"<=", "\x00LE\x00", "<= (protegido de <)"),
    (r">=", "\x00GE\x00", ">= (protegido de >)"),

    # --- booleano ---------------------------------------------------------
    (r"&&", " and ", "&& -> and"),
    (r"\|\|", " or ", "|| -> or"),
    # `[^\S\n]*` -- espaco horizontal, nunca a quebra. Com `\s*` a regra
    # atravessava o `\n`: onde um `!` termina a linha ela engolia o statement
    # de baixo. Nos seis sitios do Database.cpp que tem essa forma o `!` esta
    # dentro de comentario (`//kit preview !!!!`, `// i 9!!`), e `_proteger()`
    # mascara comentario ANTES do SUBS -- por isso a saida nunca saiu errada, e
    # ancorar a regra nao muda um byte do Pascal. O que se conserta e a regra:
    # ela dependia de um mascaramento a montante para nao apagar codigo.
    (r"!(?=[^\S\n]*[\w(])", "not ", "! -> not"),

    # --- deslocamento -----------------------------------------------------
    # Sem lookbehind: a versao da WTE-TASK-17 exigia que o caractere anterior
    # nao fosse `\w`, e por isso `hair_style<<4` (Player.cpp) atravessava
    # intacto. Template e `std::cout <<` sao recusa do FORBIDDEN, entao nao ha
    # o que proteger.
    (r"<<", " shl ", "<< -> shl"),
    (r">>", " shr ", ">> -> shr"),
    (r"(?<=\w)\s*%\s*(?=\w)", " mod ", "% -> mod"),

    # --- membro -----------------------------------------------------------
    (r"->", ".", "-> -> ."),

    # --- literal hexadecimal ----------------------------------------------
    (r"\b0[xX]([0-9a-fA-F]+)\b", r"$\1", "0x.. -> $.."),

    # --- atribuicao composta bit-a-bit, ANTES de `&` virar `and` ----------
    # O parenteses no lado direito nao e enfeite: `x |= defence-12` significa
    # `x or (defence-12)`, e em Pascal `or` e `-` tem a MESMA precedencia --
    # sem o parenteses viraria `(x or defence) - 12`.
    (r"(\w+(?:\[[^\]\n]*\])?)\s*&=\s*([^;\n]+);", r"\1 := \1 and (\2);", "&="),
    (r"(\w+(?:\[[^\]\n]*\])?)\s*\|=\s*([^;\n]+);", r"\1 := \1 or (\2);", "|="),
    (r"(\w+(?:\[[^\]\n]*\])?)\s*\^=\s*([^;\n]+);", r"\1 := \1 xor (\2);", "^="),

    # --- bit a bit --------------------------------------------------------
    # O endereco-de ja foi resolvido por traduzir_enderecos(); o que sobra de
    # `&` e conjuncao de bits.
    (r"(?<![&\w])&(?![&])", " and ", "& -> and (bit a bit)"),
    (r"(?<![|\w])\|(?![|])", " or ", "| -> or (bit a bit)"),

    # --- cast, ANTES das regras de tipo ------------------------------------------------------------
    (r"static_cast<\s*int\s*>\s*\(", "LongInt(", "static_cast<int>"),
    (r"static_cast<\s*unsigned int\s*>\s*\(", "LongWord(",
     "static_cast<unsigned int>"),
    # `(unsigned char*)x` vira `@x`: com {$T-} o `@` devolve ponteiro sem tipo,
    # que serve a qualquer parametro de ponteiro. A versao da WTE-TASK-17
    # apagava o cast e passava o ARRAY onde a rotina espera PByte.
    (r"\(unsigned char\s*\*\)\s*", "@", "cast para unsigned char* -> @"),
    (r"\(char\)\s*", "", "cast (char): o ShortInt ja tem sinal"),
    # `std::ceil` devolve Double em C++ e o `(int)` arredonda; o `Ceil` da
    # unidade Math do FPC ja devolve inteiro, entao o cast some junto.
    (r"\(int\)\s*std::ceil\b", "Ceil", "(int)std::ceil -> Ceil (unidade Math)"),

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
    # de registro.
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
    # `Report(report, ...)`: o Pascal NAO distingue caixa, entao o parametro
    # `report` esconderia a rotina `Report` e a chamada deixaria de compilar --
    # com erro que nao menciona caixa nenhuma. A rotina portada a mao se chama
    # `Reportar`.
    (r"\bReport\s*\(", "Reportar(", "Report -> Reportar (colisao de caixa)"),
    (r"\bstd::strcpy\b", "CStrCopy", "strcpy -> CStrCopy"),
    (r"\bstrcpy\b", "CStrCopy", "strcpy -> CStrCopy"),
    (r"\bstd::strcat\b", "CStrCat", "strcat -> CStrCat"),
    (r"\bstrcat\b", "CStrCat", "strcat -> CStrCat"),
    (r"\bstd::strlen\b", "CStrLen", "strlen -> CStrLen"),
    (r"\bstrlen\b", "CStrLen", "strlen -> CStrLen"),

    # --- atribuicao (DEPOIS das comparacoes) ------------------------------
    (r"(?<![<>=!+\-*/%&|^:])=(?![=])", ":=", "= -> :="),

    # --- chamada sem argumento --------------------------------------------
    (r"(\w)\(\s*\)", r"\1", "chamada sem argumento: o Pascal dispensa `()`"),

    # --- desmarcar o que foi protegido ------------------------------------
    (r"\x00EQ\x00", "=", "restaura ="),
    (r"\x00LE\x00", "<=", "restaura <="),
    (r"\x00GE\x00", ">=", "restaura >="),

    # --- incremento e decremento -----------------------------------------
    (r"(\w+(?:\[[^\]\n]*\])?)\s*\+=\s*([^;\n]+);", r"\1 := \1 + (\2);", "+="),
    (r"(\w+(?:\[[^\]\n]*\])?)\s*-=\s*([^;\n]+);", r"\1 := \1 - (\2);", "-="),
    (r"(\w+(?:\[[^\]\n]*\])?)\s*\+\+\s*;", r"Inc(\1);", "x++"),
    (r"\+\+\s*(\w+(?:\[[^\]\n]*\])?)\s*;", r"Inc(\1);", "++x"),
    (r"(\w+(?:\[[^\]\n]*\])?)\s*--\s*;", r"Dec(\1);", "x--"),
    (r"--\s*(\w+(?:\[[^\]\n]*\])?)\s*;", r"Dec(\1);", "--x"),
]

_GUARDA = "\x02%d\x02"


def _proteger(texto: str) -> tuple[str, list[str]]:
    """Tira comentario e literal do caminho das SUBS.

    Achado da WTE-TASK-18: a versao anterior aplicava as SUBS sobre o texto
    cru, e a mensagem `"Error ! Impossible to open CD image !"` do
    `Database.cpp` saia como `'Error not Impossible ...'` -- a regra `!` -> `not`
    comia dentro do literal. O mesmo valia para `//` com `->` ou `==`.
    """
    guardados: list[str] = []

    def guardar(m: re.Match[str]) -> str:
        guardados.append(m.group(0))
        return _GUARDA % (len(guardados) - 1)

    texto = re.sub(r"//[^\n]*", guardar, texto)
    texto = re.sub(r'"(?:[^"\\\n]|\\.)*"', guardar, texto)
    texto = re.sub(r"'(?:[^'\\\n]|\\.)*'", guardar, texto)
    return texto, guardados


def _restaurar(texto: str, guardados: list[str]) -> str:
    def repor(m: re.Match[str]) -> str:
        bruto = guardados[int(m.group(1))]
        if bruto.startswith("//"):
            return bruto                       # `//` ja e comentario no Pascal
        if bruto.startswith('"'):
            corpo = bruto[1:-1].replace("\\n", "").replace("\\t", "")
            return "'" + corpo.replace("'", "''") + "'"
        # literal de caractere de C: vira o codigo, que e o que o Pascal aceita
        # em contexto numerico.
        return bruto.replace("'", "'", 1)

    return re.sub("\x02(\\d+)\x02", repor, texto)


def aplicar_subs(texto: str,
                 renomeados: dict[str, str] | None = None
                 ) -> tuple[str, dict[str, int]]:
    texto, guardados = _proteger(texto)
    # Identificador que colide com palavra reservada do Pascal. Feito DEPOIS de
    # `_proteger` de proposito: `as` dentro de comentario ou literal nao e
    # identificador. Sem isto o corpo de AsciiToKanji sai com `as[i]`, e `as` e
    # o operador de type-cast -- o erro do FPC nao menciona o nome.
    for velho, novo in (renomeados or {}).items():
        texto = re.sub(rf"\b{re.escape(velho)}\b", novo, texto)
    texto = parentizar_booleanos(texto)
    texto = traduzir_enderecos(texto)
    contagem: dict[str, int] = {}
    for padrao, repl, razao in SUBS:
        texto, n = re.subn(padrao, repl, texto, flags=re.M)
        if n:
            contagem[razao] = contagem.get(razao, 0) + n
    return _restaurar(texto, guardados), contagem


# ============================================================ 5. check_seeks ==

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


# =============================================== 6. o mapeamento de tipo =====
#
# wte/re/tipos.md, tabela e decisoes 1 e 4. `char` NAO tem traducao unica:
# texto vira `AnsiChar` (decisao 1, para que o truncamento do `strcpy` continue
# visivel), numero vira `ShortInt` (decisao 4, porque o `char` do x86 tem sinal
# e a UI alarga com static_cast<int> -- 200 tem de chegar como -56).
#
# A classificacao e por nome, e nao por heuristica, de proposito: heuristica
# erra em silencio e o erro so aparece na tela do usuario.

ESCALARES = {
    "int": "LongInt",
    "unsigned int": "LongWord",
    "unsigned short": "Word",
    "unsigned char": "Byte",
    "bool": "Boolean",
    "double": "Double",
    "Offset": "TOffset",
}

# Registro C++ -> registro Pascal. O prefixo `T` segue o `TOffset` que o
# gen_tables_pas.py (WTE-TASK-16) ja emite.
REGISTROS = {
    "SquadNumbers": "TSquadNumbers",
    "Team": "TTeam",
    "MlTeam": "TMlTeam",
    "Formation": "TFormation",
    "Player": "TPlayer",
    "Database": "TDatabase",
    "CdImage": "TCdImage",
    "SectorPosition": "TSectorPosition",
}

# Campo `char` com semantica NUMERICA (decisao 4). O que nao esta aqui e texto
# (decisao 1). Os dois sentidos sao conferidos: campo `char` que nao aparece em
# nenhuma das duas listas recusa.
CHAR_NUMERICO: dict[str, set[str]] = {
    "Team": {"bar_attack", "bar_defence", "bar_power", "bar_speed",
             "bar_technique", "kick_long_fk", "kick_short_fk",
             "kick_left_corner", "kick_right_corner", "kick_penalty",
             "captain", "slot_role", "slot_x", "slot_y", "flag_shape",
             "raw_strategy"},
    "MlTeam": {"bar_attack", "bar_defence", "bar_power", "bar_speed",
               "bar_technique", "kick_long_fk", "kick_short_fk",
               "kick_left_corner", "kick_right_corner", "kick_penalty",
               "captain", "slot_role", "slot_x", "slot_y", "flag_shape",
               "raw_numbers", "raw_strategy"},
    "Formation": {"roles", "x", "y"},
    "Player": {"raw_attributes"},
}

CHAR_TEXTO: dict[str, set[str]] = {
    "Team": {"names", "mixed_case_name", "abbreviations", "kanji_name",
             "raw_kanji_name", "raw_formation"},
    "MlTeam": {"names", "mixed_case_name", "abbreviations", "kanji_name",
               "raw_kanji_name", "raw_formation"},
    "Formation": {"name"},
    "Player": {"url", "name"},
}

# Locais `char` de corpo de funcao, mesma decisao e mesma exigencia de estar
# escrita. Sao quatro no core inteiro.
CHAR_LOCAL: dict[tuple[str, str], str] = {
    ("Database::Load", "buf"): "AnsiChar",
    ("Database::Load", "buf1"): "AnsiChar",
    ("Database::Load", "name_buf"): "AnsiChar",
    ("Database::Save", "buf"): "AnsiChar",
    ("Database::Save", "buf1"): "AnsiChar",
    # `aux` guarda codigo de caractere e so sai por `as[i] := aux[i*2]`, para
    # um Byte. Numerico pela decisao 4.
    ("KanjiToAscii", "aux"): "ShortInt",
}

# Palavra reservada do Object Pascal que colide com identificador da entrada.
# `as` e parametro de AsciiToKanji/KanjiToAscii e e operador de type-cast no
# Pascal: sem renomear, o corpo inteiro deixa de compilar com erro que nao
# menciona o nome.
RESERVADAS = {
    "and", "array", "as", "asm", "begin", "case", "const", "constructor",
    "destructor", "div", "do", "downto", "else", "end", "except", "exports",
    "file", "finally", "for", "function", "goto", "if", "implementation", "in",
    "inherited", "initialization", "inline", "interface", "is", "label",
    "library", "mod", "nil", "not", "object", "of", "on", "operator", "or",
    "packed", "procedure", "program", "property", "raise", "record", "repeat",
    "resourcestring", "self", "set", "shl", "shr", "string", "then",
    "threadvar", "to", "try", "type", "unit", "until", "uses", "var", "while",
    "with", "xor", "result",
}

RENOMEIA = {"as": "as_"}


@dataclass
class TipoPas:
    """Tipo Pascal de uma expressao: base mais as dimensoes que faltam indexar."""
    base: str
    dims: list[str] = field(default_factory=list)

    @property
    def escalar(self) -> bool:
        return not self.dims

    def indexado(self) -> "TipoPas":
        return TipoPas(self.base, self.dims[1:])

    def declaracao(self) -> str:
        texto = self.base
        for d in reversed(self.dims):
            texto = f"array[0..{d}] of {texto}"
        return texto


INTEIROS = {"Byte", "ShortInt", "Word", "SmallInt", "LongInt", "LongWord",
            "Int64", "SizeInt", "TOffset"}

# Inteiros de um byte. Recebendo de `AnsiChar`, os bits sao os mesmos com ou
# sem sinal, e `Ord` basta. Todo o resto de `INTEIROS` e "largo": ali a
# diferenca aparece, e a conversao tem de estender sinal como o C++ estende.
UM_BYTE = {"Byte", "ShortInt"}


# ======================================== 7. o passe estrutural (TASK-18) ====

@dataclass
class Item:
    """Item de topo de uma entrada C++: funcao, classe ou constante."""
    tipo: str          # "func" | "classe" | "const" | "default" | "proto" | ...
    nome: str
    linha: int
    texto: str
    doc: str = ""      # o comentario que vinha logo antes, preservado


def _sem_comentario(linha: str) -> str:
    return re.sub(r"//.*$", "", linha).strip()


def normalizar(corpo: str) -> list[tuple[int, str]]:
    """Quebra um corpo de funcao em uma construcao por linha.

    Devolve (linha_original, texto). Depois disto cada elemento e exatamente um
    de: comentario, `{`, `}`, cabecalho de controle, rotulo de `case`, ou um
    statement terminado em `;`.

    Sem esta etapa o parser teria de lidar com `{i=p;}` numa linha so
    (Database.cpp:1313) e com `if(k<1) k = 1;` (:1700) -- as duas formas
    existem na entrada.
    """
    fora: list[tuple[int, str]] = []
    pendente = ""
    linha = 1
    inicio = 1
    profundidade = 0
    i = 0
    n = len(corpo)

    def despejar() -> None:
        nonlocal pendente, inicio
        if pendente.strip():
            fora.append((inicio, pendente.strip()))
        pendente = ""
        inicio = linha

    while i < n:
        c = corpo[i]
        if c == "\n":
            linha += 1
            if not pendente.strip():
                inicio = linha
            pendente += " "
            i += 1
            continue
        if corpo.startswith("//", i):
            fim = corpo.find("\n", i)
            fim = n if fim < 0 else fim
            comentario = corpo[i:fim]
            if pendente.strip():
                despejar()
            fora.append((linha, comentario))
            inicio = linha
            i = fim
            continue
        if c == '"':
            j = i + 1
            while j < n and corpo[j] != '"':
                j += 2 if corpo[j] == "\\" else 1
            pendente += corpo[i:j + 1]
            i = j + 1
            continue
        if c == "(":
            profundidade += 1
        elif c == ")":
            profundidade -= 1
            pendente += c
            i += 1
            if profundidade == 0:
                cabeca = pendente.strip()
                if re.match(r"^(?:\}\s*)?(?:else\s+)?(?:for|if|while|switch)\b",
                            cabeca):
                    despejar()
            continue
        if c in "{}":
            despejar()
            fora.append((linha, c))
            i += 1
            continue
        if c == ";" and profundidade == 0:
            pendente += c
            despejar()
            i += 1
            continue
        # `case 30 :` e `default :` -- com espaco antes do `:`, que e como o
        # Database.cpp escreve os dois `switch`.
        if c == ":" and profundidade == 0 and re.match(
                r"^\s*(?:case\b[^:]*|default\s*)$", pendente):
            pendente += c
            despejar()
            i += 1
            continue
        pendente += c
        i += 1
    despejar()
    return [(ln, t) for ln, t in fora if t]


class Transpilador:
    """Traduz um par .hpp/.cpp do we2002_core para uma unidade Pascal."""

    def __init__(self, unidade: str, fontes: list[tuple[str, str]]) -> None:
        self.unidade = unidade
        self.fontes = fontes
        self.notas: list[Nota] = []
        self.arquivo = fontes[0][0]
        self.campos: dict[str, dict[str, TipoPas]] = {}
        self.escopo: dict[str, TipoPas] = {}
        self.constantes: dict[str, TipoPas] = {}
        self.parametros: dict[str, TipoPas] = {}
        self.renomeados: dict[str, str] = {}
        # Statements que o `[[fallthrough]]` obrigou a DUPLICAR. Ficam
        # contados para que o teste de paridade de I/O saiba de quantos
        # `Read`/`Write` a mais a saida tem -- duplicacao deliberada nao pode
        # se confundir com regra que se multiplicou sozinha.
        self.duplicados: list[str] = []
        self.classe_atual = ""
        self.funcao_atual = ""
        self.manuais_usados: set[str] = set()

    # ---------------------------------------------------------------- notas --
    def recusar(self, linha: int, motivo: str) -> None:
        self.notas.append(Nota(self.arquivo, linha, motivo))

    # -------------------------------------------------------------- tipos ----
    def tipo_de(self, expr: str) -> TipoPas | None:
        """Tipo Pascal de uma expressao C++ do subconjunto, ou None."""
        e = expr.strip()
        while e.startswith("(") and e.endswith(")") and _balanceado(e[1:-1]):
            e = e[1:-1].strip()
        if not e:
            return None
        if re.fullmatch(r"\d+", e):
            return TipoPas("LongInt")
        if e.endswith("]"):
            corte = _abre_de(e, len(e) - 1)
            if corte is None:
                return None
            base = self.tipo_de(e[:corte])
            if base is None or not base.dims:
                return None
            return base.indexado()
        if "." in e and not e.endswith("."):
            prefixo, _, campo = e.rpartition(".")
            dono = self.tipo_de(prefixo)
            if dono is None:
                return None
            tabela = self.campos.get(dono.base)
            if not tabela or campo not in tabela:
                return None
            return tabela[campo]
        if re.fullmatch(r"\w+", e):
            if e in self.escopo:
                return self.escopo[e]
            if self.classe_atual:
                tabela = self.campos.get(REGISTROS.get(self.classe_atual, ""))
                if tabela and e in tabela:
                    return tabela[e]
        return None

    def ajustar_atribuicao(self, alvo: str, valor: str) -> str:
        """Insere o cast que o C++ fazia sozinho (AnsiChar <-> inteiro)."""
        ta = self.tipo_de(alvo)
        tv = self.tipo_de(valor)
        if ta is None or not ta.escalar:
            return valor
        if ta.base == "AnsiChar" and (tv is None or tv.base != "AnsiChar"):
            return f"AnsiChar({valor})"
        if ta.base in INTEIROS and tv is not None and tv.base == "AnsiChar":
            # Decisao 4 do tipos.md, aplicada tambem a conversao local->campo:
            # onde o C++ estende sinal, o Pascal estende sinal. O `char` do
            # x86 TEM sinal, entao `int c = buf[0]` com `buf[0] == 0xC8` da
            # -56 -- e `Ord` daria 200. Para destino de UM byte os bits sao os
            # mesmos nas duas formas e `Ord` continua certo (e e o que o
            # `link[j]`, de destino `Byte`, precisa).
            if ta.base in UM_BYTE:
                return f"Ord({valor})"
            return f"ShortInt({valor})"
        return valor

    # ---------------------------------------------------------- expressao ----
    def expr(self, texto: str) -> str:
        pascal, _ = aplicar_subs(texto, self.renomeados)
        return pascal.strip()


def _balanceado(s: str) -> bool:
    d = 0
    for c in s:
        if c == "(":
            d += 1
        elif c == ")":
            d -= 1
            if d < 0:
                return False
    return d == 0


def _abre_de(s: str, fecha: int) -> int | None:
    """Indice do `[` que casa com o `]` em `fecha`."""
    d = 0
    for i in range(fecha, -1, -1):
        if s[i] == "]":
            d += 1
        elif s[i] == "[":
            d -= 1
            if d == 0:
                return i
    return None


# ============================================ 8. o que NAO e transpilacao ====
#
# `wte/re/tipos.md` ja decidiu, na WTE-TASK-15, que tres pecas NAO tem forma
# transpilavel: o `CdImage` (std::fstream -> TFileStream, decisao 3), o bitfield
# de `SquadNumbers` (decisao 2) e o sidecar `_url.txt` (decisao 5). Traduzir
# `std::fstream` por regra textual produziria Pascal que compila e le errado.
#
# Elas entram como Pascal escrito a mao, AQUI, dentro do gerador -- nunca no
# arquivo de saida, que continua sendo gerado por inteiro. Cada peca reivindica
# os itens C++ que substitui: item nao reivindicado por ninguem recusa.


@dataclass
class Manual:
    itens: dict[str, str]                  # item C++ -> razao
    interface: str = ""
    implementacao: str = ""
    metodos: dict[str, list[str]] = field(default_factory=dict)
    corpos: str = ""                       # implementacao dos metodos extra


MANUAL_TYPES = Manual(
    itens={
        "SquadNumbers": "bitfield: a ordem de bit do `bitpacked record` do FPC "
                        "e definida pelo compilador e nao e obrigada a casar "
                        "com o que o MSVC fez em 2002 (tipos.md, decisao 2)",
        "SquadNumberAt": "acessor por mascara e deslocamento, idem",
        "SetSquadNumberAt": "acessor por mascara e deslocamento, idem",
        "static_assert": "sem equivalente no Pascal; virou teste "
                         "(test_port_database_pas.TestUnidadesCompilam)",
    },
    interface="""\
  { PORTE A MAO (rota 3) -- wte/re/tipos.md, decisao 2.

    O C++ declara 23 bitfields de 5 bits. O FPC tem `bitpacked record`, mas a
    ordem de bit dele e definida pelo compilador e pelo endianness, e nao e
    obrigada a casar com o que o MSVC fez em 2002. O layout abaixo e o que o
    TestSquadNumbersLayout do newWe2002 fixou: quatro unidades de 32 bits
    little-endian, campos alocados do bit menos significativo para cima, 5 bits
    cada; `numero[k]` mora na unidade `k div 6`, deslocado `5 * (k mod 6)`. }
  TSquadNumbers = packed record
    groups: array[0..3] of LongWord;
  end;
""",
    implementacao="""\
{ PORTE A MAO (rota 3) -- indice fora de 0..22 devolve 0 e ignora escrita, como
  o SquadNumberAt do C++, em vez de alcancar o campo vizinho. }
function SquadNumberAt(const n: TSquadNumbers; slot: LongInt): LongWord;
begin
  if (slot < 0) or (slot > 22) then
  begin
    Result := 0;
    Exit;
  end;
  Result := (n.groups[slot div 6] shr (5 * (slot mod 6))) and $1F;
end;

procedure SetSquadNumberAt(var n: TSquadNumbers; slot: LongInt; v: LongWord);
var
  grupo, deslocamento: LongInt;
begin
  if (slot < 0) or (slot > 22) then
    Exit;
  grupo := slot div 6;
  deslocamento := 5 * (slot mod 6);
  n.groups[grupo] := (n.groups[grupo] and not (LongWord($1F) shl deslocamento))
                     or ((v and $1F) shl deslocamento);
end;

{ PORTE A MAO (rota 3) -- wte/re/tipos.md, decisao 1.

  Semantica de C: copia ATE o #0 inclusive, SEM checar limite. Nao usar
  StrPCopy/StrLCopy, que truncam de outro jeito -- o truncamento do original
  pode ser load-bearing no formato, e o newWe2002 mediu um destes estourando um
  byte em TODA imagem aberta (raw_formation recebendo 30 bytes + terminador). A
  correcao la foi alargar o destino para 31, nao silenciar a copia; o Pascal
  herda os dois. }
procedure CStrCopy(var dest; const src);
var
  d, s: PByte;
begin
  d := @dest;
  s := @src;
  while s^ <> 0 do
  begin
    d^ := s^;
    Inc(d);
    Inc(s);
  end;
  d^ := 0;
end;

procedure CStrCat(var dest; const src);
var
  d, s: PByte;
begin
  d := @dest;
  while d^ <> 0 do
    Inc(d);
  s := @src;
  while s^ <> 0 do
  begin
    d^ := s^;
    Inc(d);
    Inc(s);
  end;
  d^ := 0;
end;

function CStrLen(const s): SizeInt;
var
  p: PByte;
begin
  p := @s;
  Result := 0;
  while p^ <> 0 do
  begin
    Inc(p);
    Inc(Result);
  end;
end;
""",
)

MANUAL_TYPES_DECL = """\
function SquadNumberAt(const n: TSquadNumbers; slot: LongInt): LongWord;
procedure SetSquadNumberAt(var n: TSquadNumbers; slot: LongInt; v: LongWord);

{ Copia com semantica de C -- ver o corpo. }
procedure CStrCopy(var dest; const src);
procedure CStrCat(var dest; const src);
function CStrLen(const s): SizeInt;
"""

MANUAL_CDIMAGE = Manual(
    itens={
        "CdImage": "std::fstream -> TFileStream: wte/re/tipos.md decisao 3 ja "
                   "fixou um desenho que NAO e transpilacao (Read e nunca "
                   "ReadBuffer, fmOpenReadWrite e nunca fmCreate, Seek de "
                   "Int64)",
        "SectorPosition": "registro de retorno com inicializacao por chaves; "
                          "sai junto com o Locate",
        "Locate": "idem SectorPosition",
    },
    interface="""\
  { PORTE A MAO (rota 3) -- wte/re/tipos.md, decisao 3.

    Tres propriedades do CFile do MFC sao load-bearing e o newWe2002 as
    preservou de proposito; o Pascal as preserva de novo:

      1. ponteiro de arquivo unico;
      2. LEITURA CURTA NAO E ERRO -- por isso `Read` e nunca `ReadBuffer`, que
         levanta EReadError no fim do arquivo;
      3. EDC/ECC NAO e recalculado na gravacao.

    E `fmOpenReadWrite`, nunca `fmCreate`: `fmCreate` truncaria uma imagem de
    474 MB. }
  TSectorPosition = record
    sector: TOffset;
    byte_in_sector: TOffset;
    in_data_region: Boolean;   { true quando byte_in_sector cai em [24, 2072) }
  end;

  TCdImage = record
  private
    FStream: TFileStream;
    FPath: string;
  public
    { Registro local nao e zerado pelo FPC; o `CdImage image_file;` do C++ vira
      declaracao + esta chamada. }
    procedure Init;
    function OpenRead(const path: string): Boolean;
    function OpenReadWrite(const path: string): Boolean;
    procedure Close;
    function IsOpen: Boolean;
    function Path: string;
    procedure Seek(position: TOffset; origin: TSeekOrigin);
    function Tell: TOffset;
    function Read(var buffer; count: SizeInt): SizeInt;
    procedure Write(const buffer; count: SizeInt);
    function Size: TOffset;
  end;
""",
    implementacao="""\
{ PORTE A MAO (rota 3) -- ver o comentario do tipo, na interface. }
procedure TCdImage.Init;
begin
  FStream := nil;
  FPath := '';
end;

function TCdImage.OpenRead(const path: string): Boolean;
begin
  Close;
  try
    FStream := TFileStream.Create(path, fmOpenRead or fmShareDenyNone);
  except
    on EStreamError do
    begin
      FStream := nil;
      Result := False;
      Exit;
    end;
  end;
  FPath := path;
  Result := True;
end;

function TCdImage.OpenReadWrite(const path: string): Boolean;
begin
  Close;
  try
    { fmOpenReadWrite e NUNCA fmCreate: a imagem e editada no lugar. }
    FStream := TFileStream.Create(path, fmOpenReadWrite or fmShareDenyNone);
  except
    on EStreamError do
    begin
      FStream := nil;
      Result := False;
      Exit;
    end;
  end;
  FPath := path;
  Result := True;
end;

procedure TCdImage.Close;
begin
  FreeAndNil(FStream);
  FPath := '';
end;

function TCdImage.IsOpen: Boolean;
begin
  Result := FStream <> nil;
end;

function TCdImage.Path: string;
begin
  Result := FPath;
end;

procedure TCdImage.Seek(position: TOffset; origin: TSeekOrigin);
begin
  if FStream <> nil then
    FStream.Seek(Int64(position), origin);
end;

function TCdImage.Tell: TOffset;
begin
  if FStream = nil then
    Result := -1
  else
    Result := FStream.Position;
end;

function TCdImage.Read(var buffer; count: SizeInt): SizeInt;
begin
  if FStream = nil then
  begin
    Result := 0;
    Exit;
  end;
  { TStream.Read, NUNCA ReadBuffer: leitura curta e fato, nao falha. }
  Result := FStream.Read(buffer, count);
end;

procedure TCdImage.Write(const buffer; count: SizeInt);
begin
  { WriteBuffer e aceitavel: escrita curta AQUI e erro. E nada de EDC/ECC. }
  if FStream <> nil then
    FStream.WriteBuffer(buffer, count);
end;

function TCdImage.Size: TOffset;
begin
  if FStream = nil then
    Result := -1
  else
    Result := FStream.Size;
end;

function Locate(absolute: TOffset): TSectorPosition;
var
  b: TOffset;
begin
  b := absolute mod SECTOR_SIZE;
  Result.sector := absolute div SECTOR_SIZE;
  Result.byte_in_sector := b;
  Result.in_data_region := (b >= SECTOR_DATA_BEGIN) and (b < SECTOR_DATA_END);
end;
""",
)

MANUAL_CDIMAGE_DECL = """\
function Locate(absolute: TOffset): TSectorPosition;
"""

MANUAL_DATABASE = Manual(
    itens={
        "Reporter": "std::function -> `procedure(const msg: string) of object` "
                    "(tipos.md); a assinatura nao se transpila",
        "Report": "o `if (report)` do C++ testa um std::function vazio; em "
                  "Pascal e `Assigned()`",
        "UrlSidecarPath": "std::filesystem::path::string_type e "
                          "String::replace nao tem forma transpilavel",
    },
    metodos={"Database": [
        "    // PORTE A MAO (rota 3) -- tipos.md decisao 5; substitui o bloco",
        "    // de std::ofstream do OnWriteCD.",
        "    procedure WriteUrlSidecar(const image: string);"]},
    implementacao="""\
{ PORTE A MAO (rota 3) -- o `if (report)` do C++ testa um std::function vazio. }
procedure Reportar(const report: TReporter; const msg: string);
begin
  if Assigned(report) then
    report(msg);
end;

{ PORTE A MAO (rota 3) -- caminho do sidecar "<imagem>_url.txt".

  O original montava isto com CString::Replace(".bin", "_url.txt"), que troca
  TODA ocorrencia e nao so a extensao. Reproduzido como e: um diretorio chamado
  "foo.bin" tambem seria reescrito, e mudar isso mudaria qual arquivo o editor
  le de volta. }
function UrlSidecarPath(const image: string): string;
const
  DE = '.bin';
  PARA = '_url.txt';
var
  at_: SizeInt;
begin
  Result := image;
  at_ := Pos(DE, Result);
  while at_ > 0 do
  begin
    Delete(Result, at_, Length(DE));
    Insert(PARA, Result, at_);
    at_ := PosEx(DE, Result, at_ + Length(PARA));
  end;
end;

{ PORTE A MAO (rota 3) -- wte/re/tipos.md, decisao 5.

  Byte a byte, e por isso NAO e TStringList: o SaveToFile dele usa o LineEnding
  da plataforma e tem WriteBOM, e este arquivo e do usuario. Uma linha por
  jogador, terminador #10, sem #13 e sem BOM. }
procedure TDatabase.WriteUrlSidecar(const image: string);
var
  arquivo: TFileStream;
  i: LongInt;
  linha: string;
  lf: Byte;
begin
  lf := 10;
  arquivo := TFileStream.Create(UrlSidecarPath(image), fmCreate);
  try
    for i := 0 to PLAYERS_TOTAL - 1 do
    begin
      linha := PAnsiChar(@players[i].url[0]);
      if linha <> '' then
        arquivo.WriteBuffer(linha[1], Length(linha));
      arquivo.WriteBuffer(lf, 1);
    end;
  finally
    arquivo.Free;
  end;
end;
""",
)

MANUAL_DATABASE_DECL = """\
type
  { `using Reporter = std::function<void(const std::string&)>` do Database.hpp.
    Pode ser nil, como o std::function vazio. }
  TReporter = procedure(const msg: string) of object;
"""

MANUAIS: dict[str, Manual] = {
    "we2002_types": MANUAL_TYPES,
    "we2002_cdimage": MANUAL_CDIMAGE,
    "we2002_database": MANUAL_DATABASE,
}

# Trecho DENTRO de um corpo que nao se transpila. O texto e casado exatamente e
# trocado por uma chamada; se ele nao existir mais na entrada, o gerador recusa
# -- porte a mao que apodrece calado e pior que porte a mao nenhum.
TRECHOS_MANUAIS: list[tuple[str, str, str, str]] = [
    (
        "Database.cpp",
        '\t\tstd::ofstream url_file;\n'
        '\turl_file.open(UrlSidecarPath(image), std::ios::trunc);\n'
        '\tfor(i=0;i<PLAYERS_TOTAL;i++)\n'
        '\t{\n'
        '\t\turl_file << players[i].url << std::endl;\n'
        '\t}\n'
        '\turl_file.close();',
        '\tWriteUrlSidecar(image);',
        "std::ofstream com operator<< e std::endl: tipos.md decisao 5 manda "
        "escrever o sidecar byte a byte, com #10 explicito. Virou a chamada "
        "TDatabase.WriteUrlSidecar, portada a mao",
    ),
]

# Item de topo sem contraparte em Pascal, com o motivo escrito.
IGNORADOS: dict[str, str] = {
    "pragma": "`#pragma once`: o Pascal tem unidade",
    "include": "`#include`: vira `uses`",
    "namespace": "`namespace we2002`: o Pascal tem unidade",
}

# Diretiva e `uses` por unidade.
DIRETIVAS = "{$mode objfpc}{$H+}\n{$modeswitch advancedrecords}\n"
POINTERMATH = "{$POINTERMATH ON}  { `lk[0]` sobre PByte, como no C++ }\n"

USES: dict[str, tuple[list[str], list[str]]] = {
    "we2002_types": ([], []),
    "we2002_team": (["we2002_types"], []),
    "we2002_cdimage": (["Classes", "we2002_offsets"], ["SysUtils"]),
    "we2002_textcodec": ([], []),
    "we2002_player": ([], []),
    "we2002_database": (["we2002_types", "we2002_team", "we2002_player",
                         "we2002_cdimage", "we2002_offsets", "we2002_tables"],
                        ["Classes", "SysUtils", "StrUtils", "Math",
                         "we2002_textcodec"]),
}

EXTRA_DIRETIVAS = {"we2002_textcodec": POINTERMATH,
                   "we2002_database": POINTERMATH}


# Texto que entra DENTRO do bloco `type` da interface, antes dos registros
# gerados, e as declaracoes de rotina que vem depois dele.
MANUAL_TIPOS: dict[str, str] = {
    "we2002_types": MANUAL_TYPES.interface,
    "we2002_cdimage": MANUAL_CDIMAGE.interface,
    "we2002_database": """\
  { `using Reporter = std::function<void(const std::string&)>` do Database.hpp.
    PORTE A MAO (rota 3): pode ser nil, como o std::function vazio. }
  TReporter = procedure(const msg: string) of object;
""",
}

MANUAL_DECLS: dict[str, str] = {
    "we2002_types": MANUAL_TYPES_DECL,
    "we2002_cdimage": MANUAL_CDIMAGE_DECL,
    "we2002_database": "procedure Reportar(const report: TReporter; "
                       "const msg: string);\n"
                       "function UrlSidecarPath(const image: string): string;\n",
}

# Item reivindicado sem codigo: fica FORA da camada de dados, com razao.
MANUAL_PLAYER = Manual(itens={
    "FifaPlayer": "a classe do import do SoFIFA, desligado no newWe2002 desde "
                  "2026-08-05; usa std::vector e std::string e nao tem "
                  "consumidor no editor do Obocaman",
    "SofifaRules": "declaracao adiantada da classe de regras do SoFIFA, idem",
})
MANUAIS["we2002_player"] = MANUAL_PLAYER

# Rota escolhida por item reivindicado -- o que a WTE-TASK-18 tinha de decidir.
ROTAS: dict[str, str] = {
    "SquadNumbers": "3 (porte a mao)",
    "SquadNumberAt": "3 (porte a mao)",
    "SetSquadNumberAt": "3 (porte a mao)",
    "static_assert": "1 (virou teste)",
    "CdImage": "3 (porte a mao)",
    "SectorPosition": "3 (porte a mao)",
    "Locate": "3 (porte a mao)",
    "Reporter": "3 (porte a mao)",
    "Report": "3 (porte a mao)",
    "UrlSidecarPath": "3 (porte a mao)",
    "FifaPlayer": "fora da camada de dados",
    "SofifaRules": "fora da camada de dados",
}


# ======================================== 9. varredura dos itens de topo =====

def _mascara_c(linha: str) -> str:
    """Apaga comentario e literal de UMA linha, para contar chave com seguranca."""
    linha = re.sub(r"//.*$", "", linha)
    linha = re.sub(r'"(?:[^"\\]|\\.)*"', '""', linha)
    linha = re.sub(r"'(?:[^'\\]|\\.)*'", "''", linha)
    return linha


def partir_topo(texto: str) -> list[Item]:
    """Um item de topo por elemento: funcao, classe, constante, `using`."""
    linhas = texto.split("\n")
    itens: list[Item] = []
    buf: list[str] = []
    doc: list[str] = []
    inicio = 0
    prof = 0
    for i, ln in enumerate(linhas, 1):
        s = ln.strip()
        if not buf:
            if s.startswith("//"):
                doc.append(s)
                continue
            if not s:
                doc = []
                continue
            if (s.startswith("#") or s.startswith("}")
                    or re.match(r"^namespace\b", s)):
                doc = []
                continue
            inicio = i
        buf.append(ln)
        limpa = _mascara_c(ln)
        prof += limpa.count("{") - limpa.count("}")
        corpo = "\n".join(buf).strip()
        codigo = "\n".join(_mascara_c(x).rstrip() for x in buf).strip()
        if prof <= 0 and (codigo.endswith(";") or codigo.endswith("}")):
            itens.append(Item("?", "", inicio, corpo, "\n".join(doc)))
            buf = []
            doc = []
            prof = 0
    if buf:
        itens.append(Item("?", "", inicio, "\n".join(buf).strip(),
                          "\n".join(doc)))
    return itens


RE_CONST = re.compile(
    r"^inline\s+constexpr\s+(?P<tipo>[\w:]+)\s+(?P<nome>\w+)\s*=\s*"
    r"(?P<valor>[^;\n]+);[ \t]*(?P<nota>//[^\n]*)?\s*$")
RE_USING = re.compile(r"^using\s+(?P<nome>\w+)\s*=")
RE_CLASSE = re.compile(
    r"^(?:struct|class)\s+(?P<nome>\w+)\s*\{(?P<corpo>.*)\}\s*;\s*$", re.S)
RE_FWD = re.compile(r"^(?:struct|class)\s+(?P<nome>\w+)\s*;\s*$")
RE_DEFAULT = re.compile(
    r"^(?P<classe>\w+)::(?P<nome>~?\w+)\s*\(\s*\)\s*=\s*default\s*;\s*$")
RE_STATIC_ASSERT = re.compile(r"^static_assert\s*\(", re.S)
RE_FUNC = re.compile(
    r"^(?:constexpr\s+)?(?P<ret>(?:const\s+)?[\w:]+\s*[&*]?)\s+"
    r"(?:(?P<classe>\w+)::)?(?P<nome>~?\w+)\s*\((?P<args>[^)]*)\)\s*"
    r"(?:const\s*)?\{(?P<corpo>.*)\}\s*$", re.S)
RE_DTOR = re.compile(
    r"^(?P<classe>\w+)::~(?P<nome>\w+)\s*\(\s*\)\s*\{", re.S)
RE_PROTO = re.compile(
    r"^(?P<ret>(?:const\s+)?[\w:]+\s*[&*]?)\s+(?P<nome>\w+)\s*"
    r"\((?P<args>[^)]*)\)\s*;[ \t]*(?://[^\n]*)?\s*$", re.S)


def classificar(it: Item) -> Item:
    t = it.texto
    for regex, tipo, grupo in (
        (RE_CONST, "const", "nome"),
        (RE_USING, "using", "nome"),
        (RE_CLASSE, "classe", "nome"),
        (RE_FWD, "fwd", "nome"),
        (RE_DEFAULT, "default", "classe"),
    ):
        m = regex.match(t)
        if m:
            return Item(tipo, m.group(grupo), it.linha, t, it.doc)
    m = RE_DTOR.match(t)
    if m:
        return Item("dtor", m.group("classe"), it.linha, t, it.doc)
    if RE_STATIC_ASSERT.match(t):
        return Item("static_assert", "static_assert", it.linha, t, it.doc)
    m = RE_FUNC.match(t)
    if m:
        return Item("func", m.group("nome"), it.linha, t, it.doc)
    m = RE_PROTO.match(t)
    if m:
        return Item("proto", m.group("nome"), it.linha, t, it.doc)
    return Item("?", "", it.linha, t, it.doc)


# ============================================ 10. campos, tipos e assinatura ==

RE_DECL_CAMPO = re.compile(
    r"^(?P<tipo>(?:unsigned\s+)?[\w:]+)\s+(?P<decls>[\w\s,\[\]\*&]+)$")


def _dim_bound(expr: str) -> str:
    """`[6]` -> `5`; `[PLAYERS_TOTAL]` -> `PLAYERS_TOTAL - 1`."""
    e = expr.strip()
    if re.fullmatch(r"\d+", e):
        return str(int(e) - 1)
    return f"{e} - 1"


class ErroDeCampo(RuntimeError):
    pass


def tipo_de_campo(classe: str, tipo_c: str, nome: str,
                  dims: list[str]) -> TipoPas:
    tipo_c = re.sub(r"\s+", " ", tipo_c.strip())
    if tipo_c == "char":
        numericos = CHAR_NUMERICO.get(classe, set())
        textos = CHAR_TEXTO.get(classe, set())
        if nome in numericos:
            base = "ShortInt"
        elif nome in textos:
            base = "AnsiChar"
        else:
            raise ErroDeCampo(
                f"campo `char {classe}::{nome}` sem classificacao: a decisao 4 "
                f"de wte/re/tipos.md separa `char` de TEXTO (AnsiChar) de "
                f"`char` NUMERICO (ShortInt, com sinal, porque a UI alarga com "
                f"static_cast<int> e 200 tem de chegar como -56). Escreva o "
                f"campo em CHAR_TEXTO ou em CHAR_NUMERICO")
        return TipoPas(base, dims)
    if tipo_c in ESCALARES:
        return TipoPas(ESCALARES[tipo_c], dims)
    if tipo_c in REGISTROS:
        return TipoPas(REGISTROS[tipo_c], dims)
    raise ErroDeCampo(f"tipo `{tipo_c}` sem mapeamento em wte/re/tipos.md")


def partir_membros(corpo: str) -> list[tuple[int, str, str]]:
    """Membros de uma classe: (linha, texto, comentario que o precedia)."""
    fora: list[tuple[int, str, str]] = []
    doc: list[str] = []
    buf = ""
    linha = 1
    inicio = 1
    prof = 0
    i = 0
    while i < len(corpo):
        c = corpo[i]
        if c == "\n":
            linha += 1
            buf += " "
            i += 1
            if not buf.strip():
                inicio = linha
            continue
        if corpo.startswith("//", i):
            fim = corpo.find("\n", i)
            if not buf.strip():
                doc.append(corpo[i:fim if fim >= 0 else len(corpo)].strip())
            i = fim if fim >= 0 else len(corpo)
            continue
        if c in "{(":
            prof += 1
        elif c in "})":
            prof -= 1
        elif c == ";" and prof == 0:
            if buf.strip():
                fora.append((inicio, buf.strip(), "\n".join(doc)))
            doc = []
            buf = ""
            inicio = linha
            i += 1
            continue
        buf += c
        i += 1
    if buf.strip():
        fora.append((inicio, buf.strip(), "\n".join(doc)))
    return fora


def renomear(nome: str) -> str:
    if nome.lower() in RESERVADAS:
        return RENOMEIA.get(nome, nome + "_")
    return nome


def traduzir_param(bruto: str) -> tuple[str, str, TipoPas] | None:
    """`const unsigned char* lk` -> ('lk: PByte', 'lk', TipoPas('Byte', ['?']))."""
    p = bruto.strip()
    if not p:
        return None
    p = re.sub(r"\s*=\s*(?:\{\s*\})?\s*$", "", p)      # default `= {}` some
    const = bool(re.match(r"^const\b", p))
    p = re.sub(r"^const\s+", "", p)
    ponteiro = "*" in p
    referencia = "&" in p
    p = p.replace("*", " ").replace("&", " ")
    partes = p.split()
    nome = renomear(partes[-1])
    tipo_c = re.sub(r"\s+", " ", " ".join(partes[:-1]))
    if ponteiro:
        if tipo_c not in ("unsigned char", "char"):
            return None
        base = "Byte" if tipo_c == "unsigned char" else "ShortInt"
        return (f"{nome}: P{base}", nome, TipoPas(base, ["?"]))
    if tipo_c in ("std::filesystem::path", "std::string"):
        return (f"const {nome}: string", nome, TipoPas("string"))
    if tipo_c == "Reporter":
        return (f"const {nome}: TReporter", nome, TipoPas("TReporter"))
    if tipo_c in REGISTROS:
        pref = "const " if (const and referencia) else ""
        return (f"{pref}{nome}: {REGISTROS[tipo_c]}", nome,
                TipoPas(REGISTROS[tipo_c]))
    if tipo_c in ESCALARES:
        return (f"{nome}: {ESCALARES[tipo_c]}", nome, TipoPas(ESCALARES[tipo_c]))
    return None


# ============================================== 11. o corpo, statement a statement ==

RE_ROTULO = re.compile(r"^(?:case\b.*|default\s*):$")
TIPOS_LOCAIS = (r"unsigned\s+(?:char|short|int)|int|char|double|bool|CdImage")
RE_DECL_LOCAL = re.compile(
    rf"^(?:const\s+)?(?P<tipo>{TIPOS_LOCAIS})\s+(?P<decls>[^;]+);$")
RE_ATRIB_COMPOSTA = re.compile(r"[+\-*/%&|^]=|<<=|>>=")


def _pos_atribuicoes(t: str) -> list[int]:
    """Posicoes dos `=` de atribuicao simples, em profundidade zero."""
    fora: list[int] = []
    prof = 0
    i = 0
    while i < len(t):
        c = t[i]
        if c in "([":
            prof += 1
        elif c in ")]":
            prof -= 1
        elif c == "=" and prof == 0:
            antes = t[i - 1] if i else " "
            depois = t[i + 1] if i + 1 < len(t) else " "
            if depois != "=" and antes not in "=!<>+-*/%&|^":
                fora.append(i)
        i += 1
    return fora


class Corpo:
    """Parser e emissor de um corpo de funcao ja normalizado."""

    def __init__(self, tp: "Transpilador", linhas: list[tuple[int, str]],
                 funcao: str, retorno: str | None) -> None:
        self.tp = tp
        self.linhas = linhas
        self.funcao = funcao
        self.retorno = retorno
        self.vars: list[str] = []
        self.pre: list[str] = []          # init de local de tipo registro

    # ------------------------------------------------------------ util ------
    @staticmethod
    def ind(n: int) -> str:
        return "  " * n

    def recusar(self, ln: int, motivo: str) -> None:
        self.tp.recusar(ln, motivo)

    def texto_restante(self, i: int) -> str:
        return " ".join(t for _, t in self.linhas[i:])

    # -------------------------------------------------------- statements ----
    def statements(self, i: int, nivel: int) -> tuple[list[str], int]:
        fora: list[str] = []
        while i < len(self.linhas):
            t = self.linhas[i][1]
            if t == "}":
                return fora, i
            if RE_ROTULO.match(t):
                return fora, i
            linhas, i = self.um(i, nivel)
            fora += linhas
        return fora, i

    def corpo_de(self, i: int, nivel: int) -> tuple[list[str], int]:
        """Corpo de um `if`/`for`, sempre entre begin/end (o `end` vem sem `;`)."""
        if self.linhas[i][1] == "{":
            miolo, j = self.statements(i + 1, nivel + 1)
            if j < len(self.linhas) and self.linhas[j][1] == "}":
                j += 1
        else:
            miolo, j = self.um(i, nivel + 1)
        return [self.ind(nivel) + "begin"] + miolo + [self.ind(nivel) + "end"], j

    def um(self, i: int, nivel: int) -> tuple[list[str], int]:
        ln, t = self.linhas[i]
        ind = self.ind(nivel)

        if t.startswith("//"):
            return [ind + t], i + 1
        if t == "{":
            miolo, j = self.statements(i + 1, nivel + 1)
            if j < len(self.linhas) and self.linhas[j][1] == "}":
                j += 1
            return [ind + "begin"] + miolo + [ind + "end;"], j
        if re.match(r"^for\s*\(", t):
            return self.laco(i, nivel)
        if re.match(r"^if\s*\(", t):
            return self.condicional(i, nivel)
        if re.match(r"^switch\s*\(", t):
            return self.escolha(i, nivel)
        if t == "break;":
            return [ind + "Break;"], i + 1
        if t.startswith("return"):
            return self.retornar(i, nivel)
        decl = self.declaracao(t)
        if decl is not None:
            return [ind + s for s in decl], i + 1
        return [ind + s for s in self.expressao(ln, t)], i + 1

    # ------------------------------------------------------------ formas ----
    def declaracao(self, t: str) -> list[str] | None:
        m = RE_DECL_LOCAL.match(t)
        if not m:
            return None
        tipo_c = re.sub(r"\s+", " ", m.group("tipo"))
        inits: list[str] = []
        for bruto in _partir_virgula(m.group("decls")):
            nome, dims, valor = _declarador(bruto)
            base = self._base_local(tipo_c, nome)
            tipo = TipoPas(base, dims)
            self.tp.escopo[nome] = tipo
            self.vars.append(f"{renomear(nome)}: {tipo.declaracao()};")
            if tipo_c == "CdImage":
                # Registro local nao e zerado pelo FPC; o construtor do C++ era.
                inits.append(f"{renomear(nome)}.Init;")
            elif valor is not None:
                inits.append(f"{renomear(nome)} := {self.tp.expr(valor)};")
        return inits

    def _base_local(self, tipo_c: str, nome: str) -> str:
        if tipo_c == "char":
            escolha = CHAR_LOCAL.get((self.funcao, nome))
            if escolha is None:
                self.recusar(0, f"local `char {self.funcao}::{nome}` sem "
                                f"classificacao em CHAR_LOCAL (tipos.md, "
                                f"decisoes 1 e 4)")
                return "AnsiChar"
            return escolha
        if tipo_c == "CdImage":
            return "TCdImage"
        if tipo_c in ESCALARES:
            return ESCALARES[tipo_c]
        self.recusar(0, f"tipo local `{tipo_c}` sem mapeamento")
        return "LongInt"

    def condicional(self, i: int, nivel: int) -> tuple[list[str], int]:
        ln, t = self.linhas[i]
        cond = _entre_parenteses(t)
        fora = [self.ind(nivel) + f"if {self.tp.expr(cond)} then"]
        corpo, j = self.corpo_de(i + 1, nivel)
        if j < len(self.linhas) and self.linhas[j][1].startswith("else"):
            resto = self.linhas[j][1][4:].strip()
            fora += corpo
            fora.append(self.ind(nivel) + "else")
            if resto:
                self.linhas[j] = (self.linhas[j][0], resto)
                senao, j = self.corpo_de(j, nivel)
            else:
                senao, j = self.corpo_de(j + 1, nivel)
            fora += senao
        else:
            fora += corpo
        fora[-1] += ";"
        return fora, j

    def laco(self, i: int, nivel: int) -> tuple[list[str], int]:
        ln, t = self.linhas[i]
        cabeca = _entre_parenteses(t)
        partes = _partir_ponto_e_virgula(cabeca)
        if len(partes) != 3:
            self.recusar(ln, "cabecalho de `for` fora do subconjunto "
                             "(init; cond; passo)")
            return [], i + 1
        init, cond, passo = (p.strip() for p in partes)

        m_init = re.match(r"^(?:(?:const\s+)?(?:int|unsigned\s+int)\s+)?"
                          r"(?P<var>\w+)\s*=\s*(?P<valor>.+)$", init)
        m_cond = re.match(r"^(?P<var>\w+)\s*(?P<op><=?)\s*(?P<lim>.+)$", cond)
        if not m_init or not m_cond or m_init.group("var") != m_cond.group("var"):
            self.recusar(ln, "cabecalho de `for` fora do subconjunto "
                             "(a variavel do init tem de ser a da condicao)")
            return [], i + 1
        var = m_init.group("var")
        if var not in self.tp.escopo:
            self.tp.escopo[var] = TipoPas("LongInt")
            self.vars.append(f"{renomear(var)}: LongInt;")
        valor = self.tp.expr(m_init.group("valor"))
        limite = self.tp.expr(m_cond.group("lim"))

        m_um = re.fullmatch(rf"(?:\+\+\s*{var}|{var}\s*\+\+)", passo)
        corpo, j = self.corpo_de(i + 1, nivel)
        miolo = "\n".join(corpo)
        atribui = re.search(rf"\b{var}\s*:=", miolo) is not None
        depois = self.linhas[j:]
        contador = self._passo_de(passo, var)
        if contador is None:
            self.recusar(ln, f"passo `{passo}` do `for` fora do subconjunto")
            return [], j

        # `for..to..do` so quando o Pascal e equivalente. Em Pascal o valor da
        # variavel de controle DEPOIS do laco e indefinido, e atribuir a ela
        # dentro do corpo e proibido -- as duas coisas acontecem na entrada
        # (TextCodec.cpp:42 le `i` depois; Database.cpp:762 faz `i = 1750`).
        pode_for = bool(m_um) and not atribui and not _le_depois(var, depois)
        if pode_for:
            if m_cond.group("op") == "<":
                fim = _menos_um(limite)
            else:
                fim = limite
            cab = self.ind(nivel) + f"for {renomear(var)} := {valor} to {fim} do"
            corpo[-1] += ";"
            return [cab] + corpo, j

        fora = [self.ind(nivel) + f"{renomear(var)} := {valor};"]
        op = "<=" if m_cond.group("op") == "<=" else "<"
        fora.append(self.ind(nivel) + f"while {renomear(var)} {op} {limite} do")
        corpo.insert(len(corpo) - 1, self.ind(nivel + 1) + contador)
        corpo[-1] += ";"
        return fora + corpo, j

    @staticmethod
    def _passo_de(passo: str, var: str) -> str | None:
        if re.fullmatch(rf"(?:\+\+\s*{var}|{var}\s*\+\+)", passo):
            return f"Inc({renomear(var)});"
        m = re.fullmatch(rf"{var}\s*\+=\s*(.+)", passo)
        if m:
            return f"Inc({renomear(var)}, {m.group(1).strip()});"
        m = re.fullmatch(rf"{var}\s*-=\s*(.+)", passo)
        if m:
            return f"Dec({renomear(var)}, {m.group(1).strip()});"
        if re.fullmatch(rf"(?:--\s*{var}|{var}\s*--)", passo):
            return f"Dec({renomear(var)});"
        return None

    def escolha(self, i: int, nivel: int) -> tuple[list[str], int]:
        ln, t = self.linhas[i]
        seletor = self.tp.expr(_entre_parenteses(t))
        j = i + 1
        if j >= len(self.linhas) or self.linhas[j][1] != "{":
            self.recusar(ln, "`switch` sem bloco: fora do subconjunto")
            return [], j
        j += 1
        grupos: list[tuple[list[str], list[str], list[str], bool]] = []
        padrao: tuple[list[str], list[str]] | None = None
        # Comentario que separa um ramo do proximo (`//goalkeeper`, `//defender`
        # em ComputePlayerCost) documenta o ramo SEGUINTE. Ele viaja como
        # prefixo, e nao como statement de ramo nenhum -- sem isso ele virava um
        # ramo vazio sem rotulo, e o `break;` do ramo anterior deixava de ser
        # reconhecido porque nao era mais a ultima linha.
        pendentes: list[str] = []
        while j < len(self.linhas):
            while j < len(self.linhas) and self.linhas[j][1].startswith("//"):
                pendentes.append(self.ind(nivel + 1) + self.linhas[j][1])
                j += 1
            if j >= len(self.linhas) or self.linhas[j][1] == "}":
                break
            rotulos: list[str] = []
            ehdefault = False
            while j < len(self.linhas):
                r = self.linhas[j][1]
                m = re.fullmatch(r"case\s+(.+?)\s*:", r)
                if m:
                    rotulos.append(self.tp.expr(m.group(1)))
                    j += 1
                    continue
                if re.fullmatch(r"default\s*:", r):
                    ehdefault = True
                    j += 1
                    continue
                break
            corpo, j = self.statements(j, nivel + 2)
            arrasto: list[str] = []
            while corpo and corpo[-1].strip().startswith("//"):
                arrasto.insert(0, self.ind(nivel + 1) + corpo.pop().strip())
            corpo, cai = _cortar_break(corpo)
            prefixo, pendentes = pendentes, arrasto
            if ehdefault:
                padrao = (prefixo, corpo)
                if cai:
                    self.recusar(ln, "`[[fallthrough]]` no ramo `default`: nao "
                                     "ha proximo ramo para duplicar")
            elif rotulos:
                grupos.append((prefixo, rotulos, corpo, cai))
            elif corpo:
                self.recusar(ln, "statement dentro de `switch` fora de qualquer "
                                 "`case`: fora do subconjunto")
        if j < len(self.linhas) and self.linhas[j][1] == "}":
            j += 1

        # `[[fallthrough]]`: o `case` do Pascal NAO cai para o proximo ramo, e
        # traduzir literalmente mudaria em silencio quantos bytes se le da
        # imagem. Rota 1 -- o ramo seguinte e DUPLICADO aqui, com marca.
        seguintes = [g[2] for g in grupos] + ([padrao[1]] if padrao else [])
        resolvidos: list[tuple[list[str], list[str], list[str]]] = []
        for k, (prefixo, rotulos, corpo, cai) in enumerate(grupos):
            if cai:
                proximo = seguintes[k + 1] if k + 1 < len(seguintes) else []
                corpo = corpo + [
                    self.ind(nivel + 2) + "// PORTE A MAO (rota 1): o ramo "
                    "seguinte foi DUPLICADO aqui porque o",
                    self.ind(nivel + 2) + "// `case` do Pascal nao cai para o "
                    "proximo. Ver wte/re/recusas.md.",
                ] + list(proximo)
                self.tp.duplicados += list(proximo)
            resolvidos.append((prefixo, rotulos, corpo))

        fora = [self.ind(nivel) + f"case {seletor} of"]
        for prefixo, rotulos, corpo in resolvidos:
            fora += prefixo
            fora.append(self.ind(nivel + 1) + ", ".join(rotulos) + ":")
            if corpo:
                fora.append(self.ind(nivel + 1) + "begin")
                fora += corpo
                fora.append(self.ind(nivel + 1) + "end;")
            else:
                fora.append(self.ind(nivel + 1) + "  ;")
        if padrao is not None:
            fora += padrao[0]
            fora.append(self.ind(nivel) + "else")
            fora.append(self.ind(nivel + 1) + "begin")
            fora += padrao[1]
            fora.append(self.ind(nivel + 1) + "end;")
        fora += pendentes
        fora.append(self.ind(nivel) + "end;")
        return fora, j

    def retornar(self, i: int, nivel: int) -> tuple[list[str], int]:
        ln, t = self.linhas[i]
        m = re.fullmatch(r"return\s*(.*);", t)
        if not m:
            self.recusar(ln, "`return` fora do subconjunto")
            return [], i + 1
        valor = m.group(1).strip()
        ind = self.ind(nivel)
        if not valor:
            return [ind + "Exit;"], i + 1
        return [ind + f"Result := {self.tp.expr(valor)};", ind + "Exit;"], i + 1

    def expressao(self, ln: int, t: str) -> list[str]:
        nucleo = t[:-1] if t.endswith(";") else t
        if RE_ATRIB_COMPOSTA.search(nucleo):
            return [self.tp.expr(t)]
        pos = _pos_atribuicoes(nucleo)
        if not pos:
            return [self.tp.expr(t)]
        alvos = [nucleo[:pos[0]]]
        for a, b in zip(pos, pos[1:]):
            alvos.append(nucleo[a + 1:b])
        valor = nucleo[pos[-1] + 1:]
        fora: list[str] = []
        # Cadeia `a = b = 0;` do C++, decomposta da direita para a esquerda --
        # e a ordem em que o C++ avalia.
        anterior = valor
        for alvo in reversed(alvos):
            ajustado = self.tp.ajustar_atribuicao(alvo.strip(), anterior.strip())
            fora.append(f"{self.tp.expr(alvo)} := {self.tp.expr(ajustado)};")
            anterior = alvo
        return fora


def _cortar_break(corpo: list[str]) -> tuple[list[str], bool]:
    cai = False
    while corpo and corpo[-1].strip() in ("Break;", "[[fallthrough]];"):
        if corpo[-1].strip() == "[[fallthrough]];":
            cai = True
        corpo.pop()
    return corpo, cai


def _le_depois(var: str, linhas: list[tuple[int, str]]) -> bool:
    """`var` e LIDA depois do laco?

    Em Pascal o valor da variavel de controle DEPOIS de um `for` e indefinido,
    entao um `for..to..do` so pode substituir o `for` de C quando ninguem le a
    variavel depois. `for(i = 0; ...)` mais adiante NAO conta: ali ela e
    reinicializada, e reinicializacao e escrita.

    A conferencia e por STATEMENT, e nao por posicao de caractere: a condicao
    `i < 63` do proprio `for` seguinte le `i`, e uma varredura de caractere a
    tomava por uso -- o que jogava metade dos lacos do Load para a forma
    `while` sem necessidade.
    """
    padrao = re.compile(rf"\b{re.escape(var)}\b")
    reinicia = re.compile(
        rf"^for\s*\(\s*(?:(?:const\s+)?(?:int|unsigned\s+int)\s+)?"
        rf"{re.escape(var)}\s*=[^=]")
    for _, t in linhas:
        if t.startswith("//") or not padrao.search(t):
            continue
        return not reinicia.match(t)
    return False


def _menos_um(expr: str) -> str:
    e = expr.strip()
    if re.fullmatch(r"\d+", e):
        return str(int(e) - 1)
    if re.fullmatch(r"[\w\.\[\]]+", e):
        return f"{e} - 1"
    return f"({e}) - 1"


def _entre_parenteses(t: str) -> str:
    inicio = t.index("(")
    prof = 0
    for i in range(inicio, len(t)):
        if t[i] == "(":
            prof += 1
        elif t[i] == ")":
            prof -= 1
            if prof == 0:
                return t[inicio + 1:i]
    return t[inicio + 1:]


def _partir_ponto_e_virgula(t: str) -> list[str]:
    fora: list[str] = []
    prof = 0
    atual = ""
    for c in t:
        if c in "([":
            prof += 1
        elif c in ")]":
            prof -= 1
        if c == ";" and prof == 0:
            fora.append(atual)
            atual = ""
            continue
        atual += c
    fora.append(atual)
    return fora


def _partir_virgula(t: str) -> list[str]:
    fora: list[str] = []
    prof = 0
    atual = ""
    for c in t:
        if c in "([{":
            prof += 1
        elif c in ")]}":
            prof -= 1
        if c == "," and prof == 0:
            fora.append(atual)
            atual = ""
            continue
        atual += c
    if atual.strip():
        fora.append(atual)
    return fora


def _declarador(bruto: str) -> tuple[str, list[str], str | None]:
    """`buf[50]` -> ('buf', ['49'], None); `k = 16` -> ('k', [], '16')."""
    d = bruto.strip().rstrip("{}").strip()
    valor = None
    if "=" in d:
        nome_parte, _, valor = d.partition("=")
        d = nome_parte.strip()
        valor = valor.strip()
    dims = [_dim_bound(x) for x in re.findall(r"\[([^\]]*)\]", d)]
    nome = re.sub(r"\[.*$", "", d).strip()
    return nome, dims, valor


# ============================================== 12. montagem da unidade =====

CABECALHO = """\
{{ GERADO por wte/tools/port_database_pas.py -- NAO editar a mao.

  Transpilado de {fontes}, que ja e byte-identico ao `ed.exe` nas duas ROMs.
  A entrada do transpilador e SEMPRE codigo deste repositorio -- nunca saida de
  decompilador (PLAN-WTE-LAZARUS §8.10).

  Os seeks, os comprimentos de leitura e os limites de laco estao intocados:
  eles codificam o layout MODE2/2352 da imagem, inclusive os saltos manuais
  sobre cabecalho de setor.

  Os trechos marcados PORTE A MAO nao sao transpilacao: sao decisao ja escrita
  em wte/re/tipos.md, com a rota registrada em wte/re/recusas.md.

  Regenerar:  python3 wte/tools/port_database_pas.py
  Conferir:   python3 wte/tools/port_database_pas.py --check }}

unit {unit};

{diretivas}
interface
"""


def _doc_pascal(doc: str, recuo: str) -> list[str]:
    return [recuo + ln for ln in doc.split("\n") if ln.strip()]


def _doc_partido(doc: str) -> tuple[str, str]:
    """`///<` documenta o membro ANTERIOR; o resto documenta o seguinte."""
    linhas = [ln for ln in doc.split("\n") if ln.strip()]
    antes = [ln for ln in linhas if ln.startswith("///<")]
    depois = [ln for ln in linhas if not ln.startswith("///<")]
    return " ".join(antes), "\n".join(depois)


def _rodar(tp: "Transpilador") -> str:
    manual = MANUAIS.get(tp.unidade, Manual(itens={}))
    consts: list[str] = []
    tipos: list[str] = []
    decls: list[str] = []
    corpos: list[str] = []

    for nome, texto in tp.fontes:
        tp.arquivo = nome
        for it in (classificar(x) for x in partir_topo(texto)):
            _item(tp, it, manual, consts, tipos, decls, corpos)

    diretivas = DIRETIVAS + EXTRA_DIRETIVAS.get(tp.unidade, "")
    fora = [CABECALHO.format(fontes=", ".join(n for n, _ in tp.fontes),
                             unit=tp.unidade, diretivas=diretivas)]
    usa_ifc, usa_impl = USES[tp.unidade]
    if usa_ifc:
        fora.append("\nuses\n  " + ", ".join(usa_ifc) + ";\n")
    if consts:
        fora.append("\nconst\n" + "\n".join(consts) + "\n")
    manual_tipos = MANUAL_TIPOS.get(tp.unidade, "")
    if tipos or manual_tipos:
        fora.append("\ntype\n" + manual_tipos + "\n".join(tipos) + "\n")
    manual_decls = MANUAL_DECLS.get(tp.unidade, "")
    if manual_decls:
        fora.append("\n" + manual_decls)
    if decls:
        fora.append("\n" + "\n".join(decls) + "\n")

    fora.append("\nimplementation\n")
    if usa_impl:
        fora.append("\nuses\n  " + ", ".join(usa_impl) + ";\n")
    if manual.implementacao:
        fora.append("\n" + manual.implementacao)
    if corpos:
        fora.append("\n" + "\n".join(corpos))
    fora.append("\nend.\n")
    return "".join(fora)


def _reivindicado(manual: Manual, it: Item) -> bool:
    if it.nome and it.nome in manual.itens:
        return True
    m = RE_FUNC.match(it.texto)
    if m and m.group("classe") and m.group("classe") in manual.itens:
        return True
    m = re.match(r"^[\w:<>&*\s]*?\b(\w+)::", it.texto)
    return bool(m and m.group(1) in manual.itens)


def _item(tp: "Transpilador", it: Item, manual: Manual, consts: list[str],
          tipos: list[str], decls: list[str], corpos: list[str]) -> None:
    if _reivindicado(manual, it):
        tp.manuais_usados.add(it.nome)
        m = re.match(r"^[\w:<>&*\s]*?\b(\w+)::", it.texto)
        if m:
            tp.manuais_usados.add(m.group(1))
        return
    for nota in conferir(FORBIDDEN_ENTRADA, it.texto, tp.arquivo):
        tp.recusar(it.linha + nota.linha - 1, nota.motivo)
    if it.tipo == "const":
        m = RE_CONST.match(it.texto)
        assert m
        consts += _doc_pascal(it.doc, "  ")
        valor = tp.expr(m.group("valor"))
        nota = f"  {m.group('nota')}" if m.group("nota") else ""
        consts.append(f"  {m.group('nome')} = {valor};{nota}")
        tp.constantes[m.group("nome")] = TipoPas(
            ESCALARES.get(m.group("tipo"), "LongInt"))
        return
    if it.tipo == "classe":
        _registro(tp, it, manual, tipos)
        return
    if it.tipo == "default":
        m = RE_DEFAULT.match(it.texto)
        assert m
        pas = REGISTROS.get(m.group("classe"))
        if not pas:
            tp.recusar(it.linha, f"classe `{m.group('classe')}` sem registro")
            return
        corpos.append(
            f"{{ `{m.group('classe')}::{m.group('classe')}() = default` mais os\n"
            f"  inicializadores de membro do cabecalho: o objeto sai zerado.\n"
            f"  Registro local NAO e zerado pelo FPC -- dai o Default(). }}\n"
            f"procedure {pas}.Init;\nbegin\n  Self := Default({pas});\nend;\n")
        return
    if it.tipo == "proto":
        m = RE_PROTO.match(it.texto)
        assert m
        cab = _assinatura(tp, m.group("ret"), None, m.group("nome"),
                          m.group("args"), it.linha)
        if cab:
            decls += _doc_pascal(it.doc, "")
            decls.append(cab + ";")
        return
    if it.tipo == "func":
        _funcao(tp, it, corpos)
        return
    tp.recusar(it.linha,
               f"item de topo nao reconhecido pelo passe estrutural "
               f"({it.texto.splitlines()[0][:60]!r}); nem transpilado nem "
               f"reivindicado por um porte a mao")


def _registro(tp: "Transpilador", it: Item, manual: Manual,
              tipos: list[str]) -> None:
    m = RE_CLASSE.match(it.texto)
    assert m
    classe = m.group("nome")
    pas = REGISTROS.get(classe)
    if not pas:
        tp.recusar(it.linha, f"classe `{classe}` sem entrada em REGISTROS")
        return
    campos: dict[str, TipoPas] = {}
    linhas = _doc_pascal(it.doc, "  ")
    linhas.append(f"  {pas} = record")
    metodos: list[str] = []
    for ln, membro, doc in partir_membros(m.group("corpo")):
        limpo = re.sub(r"\{[^{}]*\}", "", membro).strip()
        limpo = re.sub(r"^(?:public|private|protected)\s*:\s*", "", limpo)
        limpo = re.sub(r"\s*=\s*$", "", limpo).strip()
        if not limpo:
            continue
        if "(" in limpo:
            anterior, doc = _doc_partido(doc)
            if anterior and linhas:
                linhas[-1] += "  " + anterior
            metodos += _membro_metodo(tp, classe, limpo, doc, it.linha + ln)
            continue
        d = RE_DECL_CAMPO.match(limpo)
        if not d:
            tp.recusar(it.linha + ln, f"membro `{limpo[:50]}` fora do "
                                      f"subconjunto do passe estrutural")
            continue
        anterior, doc = _doc_partido(doc)
        if anterior and linhas:
            linhas[-1] += "  " + anterior
        linhas += _doc_pascal(doc, "    ")
        for bruto in _partir_virgula(d.group("decls")):
            nome, dims, _ = _declarador(bruto)
            if not nome:
                continue
            try:
                tipo = tipo_de_campo(classe, d.group("tipo"), nome, dims)
            except ErroDeCampo as exc:
                tp.recusar(it.linha + ln, str(exc))
                continue
            campos[nome] = tipo
            linhas.append(f"    {renomear(nome)}: {tipo.declaracao()};")
    metodos += manual.metodos.get(classe, [])
    if metodos:
        linhas.append("")
        linhas += metodos
    linhas.append("  end;")
    tp.campos[pas] = campos
    tipos.append("\n".join(linhas))


def _membro_metodo(tp: "Transpilador", classe: str, limpo: str, doc: str,
                   linha: int) -> list[str]:
    if limpo.startswith("~"):
        tp.recusar(linha, f"destrutor `{limpo}` sem contraparte: registro "
                          f"Pascal nao tem destrutor")
        return []
    m = re.match(r"^(?P<nome>\w+)\s*\((?P<args>[^)]*)\)$", limpo)
    if m and m.group("nome") == classe:
        return _doc_pascal(doc, "    ") + ["    procedure Init;"]
    m = re.match(r"^(?P<ret>(?:const\s+)?[\w:]+\s*[&*]?)\s+(?P<nome>\w+)\s*"
                 r"\((?P<args>[^)]*)\)$", limpo)
    if not m:
        tp.recusar(linha, f"membro `{limpo[:50]}` fora do subconjunto")
        return []
    cab = _assinatura(tp, m.group("ret"), None, m.group("nome"),
                      m.group("args"), linha)
    if not cab:
        return []
    return _doc_pascal(doc, "    ") + ["    " + cab + ";"]


def _assinatura(tp: "Transpilador", ret: str, classe: str | None, nome: str,
                args: str, linha: int) -> str | None:
    ret = re.sub(r"\s+", " ", ret.strip())
    if ret == "void":
        palavra, sufixo = "procedure", ""
    elif ret in ESCALARES:
        palavra, sufixo = "function", f": {ESCALARES[ret]}"
    elif ret in REGISTROS:
        palavra, sufixo = "function", f": {REGISTROS[ret]}"
    else:
        tp.recusar(linha, f"tipo de retorno `{ret}` sem mapeamento em "
                          f"wte/re/tipos.md")
        return None
    params: list[str] = []
    tp.parametros = {}
    tp.renomeados = {}
    for bruto in _partir_virgula(args):
        p = traduzir_param(bruto)
        if p is None:
            tp.recusar(linha, f"parametro `{bruto.strip()}` fora do "
                              f"subconjunto de wte/re/tipos.md")
            return None
        params.append(p[0])
        tp.parametros[p[1]] = p[2]
        original = bruto.strip().replace("*", " ").replace("&", " ").split()[-1]
        if original != p[1]:
            tp.renomeados[original] = p[1]
    lista = f"({'; '.join(params)})" if params else ""
    dono = f"{classe}." if classe else ""
    return f"{palavra} {dono}{renomear(nome)}{lista}{sufixo}"


def _funcao(tp: "Transpilador", it: Item, corpos: list[str]) -> None:
    m = RE_FUNC.match(it.texto)
    assert m
    classe = m.group("classe")
    nome = m.group("nome")
    pas_classe = REGISTROS.get(classe) if classe else None
    if classe and not pas_classe:
        tp.recusar(it.linha, f"classe `{classe}` sem entrada em REGISTROS")
        return
    tp.classe_atual = classe or ""
    tp.escopo = dict(tp.constantes)
    cab = _assinatura(tp, m.group("ret"), pas_classe, nome, m.group("args"),
                      it.linha)
    if cab is None:
        return
    tp.escopo.update(tp.parametros)
    qualificado = f"{classe}::{nome}" if classe else nome
    linhas = normalizar(m.group("corpo"))
    c = Corpo(tp, linhas, qualificado, m.group("ret"))
    stmts, _ = c.statements(0, 1)
    fora = _doc_pascal(it.doc, "") + [cab + ";"]
    if c.vars:
        fora.append("var")
        fora += ["  " + v for v in c.vars]
    fora.append("begin")
    fora += [s for s in stmts if s.strip() or True]
    fora.append("end;")
    corpos.append("\n".join(fora) + "\n")


# ======================================== 14. wte/re/transpilador.md ========

OUT_DOC = ROOT / "wte" / "re" / "transpilador.md"


def emitir_doc(notas: list[Nota],
               saidas: dict[str, str] | None = None) -> str:
    """`wte/re/transpilador.md`: a tabela, os guards e o que ficou a mao.

    Gerado, e nao escrito a mao, para que nenhum numero aqui venha de contagem
    de olho -- a armadilha 11 do `progresso.md`.
    """
    L: list[str] = []

    def w(s: str = "") -> None:
        L.append(s)

    w("# O transpilador da camada de dados \u2014 a tabela, os guards e o que "
      "ficou a m\u00e3o")
    w()
    w("**GERADO por `wte/tools/port_database_pas.py` \u2014 n\u00e3o editar "
      "\u00e0 m\u00e3o.**")
    w("Regenerar: `python3 wte/tools/port_database_pas.py`.")
    w()
    w("Produto da [WTE-TASK-17](../../docs/tasks/concluidos/"
      "17-transpilador-da-camada-de-dados.md) (tabela e guards) e da")
    w("[WTE-TASK-18](../../docs/tasks/concluidos/18-camada-de-dados-gerada.md) (passe "
      "estrutural e portes a m\u00e3o).")
    w("A rota escolhida para cada recusa est\u00e1 em "
      "[`recusas.md`](recusas.md).")
    w()
    w("---")
    w()
    w("## O limite duro")
    w()
    w("**A entrada \u00e9 sempre c\u00f3digo deste reposit\u00f3rio.** Nunca "
      "sa\u00edda de decompilador \u2014")
    w("[`PLAN-WTE-LAZARUS.md`](../../docs/PLAN-WTE-LAZARUS.md) \u00a78.10. O "
      "`FORBIDDEN` s\u00f3 segura porque")
    w("a entrada \u00e9 um subconjunto conhecido e pequeno; contra decompilado "
      "ele deixa de")
    w("recusar o que importa e o gerador passa a emitir Pascal que compila, "
      "passa em teste")
    w("unit\u00e1rio e **grava bytes errados**.")
    w()
    w("## Entrada e sa\u00edda")
    w()
    w("| Unidade Pascal | Origem em `src/core/` | Linhas C++ | Linhas Pascal |")
    w("|---|---|---|---|")
    total = 0
    total_pas = 0
    for unit, arquivos in UNITS:
        n = sum(len((CORE / a).read_text(encoding="utf-8").splitlines())
                for a in arquivos)
        total += n
        # Medido no texto que ACABOU de sair do gerador, e nao no arquivo em
        # disco: ler do disco faria o `--check` depender de o `.pas` ja
        # existir, e um clone sem eles acusaria divergencia falsa.
        m = len((saidas or {}).get(unit, "").splitlines())
        total_pas += m
        w(f"| `{unit}.pas` | " + ", ".join(f"`{a}`" for a in arquivos)
          + f" | {n} | {m or '\u2014'} |")
    w(f"| **Total** | | **{total}** | **{total_pas or '\u2014'}** |")
    w()
    w("### O que fica de fora, e por qu\u00ea")
    w()
    w("Lista fechada: o `test_nenhuma_entrada_do_core_fica_de_fora` cruza-a com "
      "o que")
    w("existe em `src/core/` e **reprova** se sobrar arquivo que ningu\u00e9m "
      "reivindicou \u2014")
    w("nos dois sentidos, ent\u00e3o motivo escrito para arquivo que sumiu "
      "tamb\u00e9m reprova.")
    w()
    w("| Arquivo | Motivo |")
    w("|---|---|")
    for nome, motivo in sorted(FORA_DO_TRANSPILADOR.items()):
        w(f"| `{nome}` | {motivo} |")
    w()
    w("A guarda existe porque a aus\u00eancia **j\u00e1 aconteceu**: a "
      "primeira vers\u00e3o do")
    w("`UNITS` esqueceu `Team.hpp` e `Team.cpp` \u2014 que declaram `Team`, "
      "`MlTeam` e")
    w("`Formation`, os tr\u00eas registros que `Database.hpp:45-48` usa como "
      "campo \u2014 e nada")
    w("no `--check` acusou. Quem apanhou foi revis\u00e3o humana "
      "([CORR-WTE-034](../../docs/tasks/concluidos/CORR-WTE-034.md)).")
    w()
    w("---")
    w()
    w(f"## A tabela de substitui\u00e7\u00e3o \u2014 {len(SUBS)} regras, "
      f"aplicadas em ordem")
    w()
    w("A ordem \u00e9 significativa: as regras de compara\u00e7\u00e3o rodam "
      "**antes** da regra de")
    w("atribui\u00e7\u00e3o, sen\u00e3o `==` viraria `:==`; e as compostas "
      "bit-a-bit (`&=`) antes de")
    w("`&` virar `and`.")
    w()
    w("Antes das regras rodam tr\u00eas passes que nenhuma regex faz sozinha:")
    w()
    w("1. **`_proteger()`** tira coment\u00e1rio e literal do caminho. Sem "
      "isso a mensagem")
    w("   `\"Error ! Impossible to open CD image !\"` saia como "
      "`'Error not Impossible \u2026'`")
    w("   \u2014 a regra `!` \u2192 `not` comia dentro do literal. Achado da "
      "WTE-TASK-18.")
    w("2. **`parentizar_booleanos()`** p\u00f5e par\u00eanteses nos operandos "
      "de `&&`/`||`. Em C `==`")
    w("   liga mais forte que `&&`; em Pascal `and` liga mais forte que `=`, e "
      "sem os")
    w("   par\u00eanteses `a = 1 and b > 2` vira `a = (1 and b) > 2`.")
    w("3. **`traduzir_enderecos()`** decide `&` por rotina chamada: some em "
      "par\u00e2metro `var`")
    w("   sem tipo (`Read`/`Write`/`CStrCopy`), vira `@` em par\u00e2metro de "
      "ponteiro")
    w("   (`ResolveMlLink`, `KanjiToAscii`). Rotina n\u00e3o classificada "
      "**recusa**.")
    w()
    w("| # | Raz\u00e3o | Padr\u00e3o |")
    w("|---|---|---|")
    for i, (padrao, _, razao) in enumerate(SUBS, 1):
        pp = padrao.replace("|", "\\|").replace("\x00", "\\0")
        w(f"| {i} | {razao} | `{pp}` |")
    w()
    w("### A armadilha que o precedente pagou")
    w()
    w("**`[^x]` casa `\\n`.** Foi assim que um `Seek(begin)` virou "
      "`SeekCurrent` no")
    w("`tools/port_database.py`: compilava, passava nos testes, passava no "
      "ASan, e s\u00f3 o")
    w("confronto com o `ed.exe` mostrou. Toda regra que n\u00e3o pode "
      "atravessar linha escreve")
    w("`[^x\\n]`, e h\u00e1 um teste que reprova regra nova sem isso "
      "(`test_port_database_pas.py`).")
    w()
    w("---")
    w()
    w(f"## O que o `FORBIDDEN` recusa \u2014 {len(FORBIDDEN)} "
      f"constru\u00e7\u00f5es")
    w()
    w("Recusa n\u00e3o \u00e9 falha: \u00e9 **trabalho identificado**. Cada "
      "uma tem tr\u00eas sa\u00eddas, e a")
    w("decis\u00e3o vai escrita em [`recusas.md`](recusas.md) \u2014 estender "
      "a tabela, ajustar a")
    w("entrada, ou portar o trecho \u00e0 m\u00e3o.")
    w()
    w("| Constru\u00e7\u00e3o | Por que n\u00e3o h\u00e1 "
      "tradu\u00e7\u00e3o decidida |")
    w("|---|---|")
    for padrao, motivo in FORBIDDEN:
        pp = padrao.replace("|", "\\|")
        w(f"| `{pp}` | {motivo} |")
    w()
    w("Coment\u00e1rio e literal s\u00e3o **mascarados** antes da varredura. "
      "Sem isso o coment\u00e1rio")
    w("`// the new national sides are elsewhere` do `Database.cpp` era acusado "
      "como uso de")
    w("`new` \u2014 e recusa falsa manda investigar trabalho que n\u00e3o "
      "existe.")
    w()
    w("---")
    w()
    w("## O segundo guard: `check_seeks()`")
    w()
    w("Conta seek absoluto e relativo na entrada e na sa\u00edda e recusa se "
      "n\u00e3o baterem. O")
    w("`FORBIDDEN` n\u00e3o v\u00ea isto: uma regra que troca a "
      "dire\u00e7\u00e3o de um seek n\u00e3o deixa token")
    w("nenhum para tr\u00e1s, e o resultado compila.")
    w()
    w("**Ele vale mais em Pascal, n\u00e3o menos.** `Seek(x, soBeginning)` e "
      "`Seek(x, soCurrent)`")
    w("diferem por uma palavra no meio da chamada, e n\u00e3o por um nome de "
      "m\u00e9todo.")
    w()
    w("Estado medido nesta execu\u00e7\u00e3o:")
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
    w("## O terceiro guard: nada sai em sil\u00eancio")
    w()
    w("Todo item de topo de cada entrada \u2014 fun\u00e7\u00e3o, classe, "
      "constante, `using` \u2014 tem de")
    w("ser transpilado **ou** reivindicado por um porte \u00e0 m\u00e3o. "
      "Item que ningu\u00e9m")
    w("reivindica recusa, e reivindica\u00e7\u00e3o de item que sumiu da "
      "entrada tamb\u00e9m.")
    w()
    w("| Unidade | Item C++ | Rota | Raz\u00e3o |")
    w("|---|---|---|---|")
    for unit, _ in UNITS:
        manual = MANUAIS.get(unit)
        if not manual:
            continue
        for item, razao in sorted(manual.itens.items()):
            w(f"| `{unit}` | `{item}` | {ROTAS.get(item, '?')} | {razao} |")
    for arquivo, _alvo, troca, razao in TRECHOS_MANUAIS:
        w(f"| `{arquivo}` | trecho `{troca.strip()}` | 3 (porte a m\u00e3o) "
          f"| {razao} |")
    w()
    w("---")
    w()
    w("## Recusas em aberto")
    w()
    if not notas:
        w("**Nenhuma.** As seis unidades saem sem recusa em aberto.")
    else:
        por_motivo: dict[str, list[Nota]] = {}
        for n in notas:
            por_motivo.setdefault(n.motivo, []).append(n)
        w(f"**{len(notas)}** recusa(s), em {len(por_motivo)} motivo(s). "
          f"Enquanto houver qualquer uma,")
        w("**nada \u00e9 emitido** \u2014 o transpilador n\u00e3o produz "
          "unidade parcial.")
        w()
        w("| Ocorr\u00eancias | Onde | Motivo |")
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



# ==================================================================== 13. main ==

def ler_fontes(unit: str, arquivos: list[str]) -> list[tuple[str, str]]:
    fora = []
    for rel in arquivos:
        p = CORE / rel
        if not p.exists():
            raise Refusal(f"{rel}: entrada nao existe")
        fora.append((f"src/core/{rel}", p.read_text(encoding="utf-8")))
    return fora


def aplicar_trechos(nome: str, texto: str) -> tuple[str, list[str]]:
    """Troca os trechos portados a mao pela chamada equivalente."""
    faltando: list[str] = []
    base = nome.split("/")[-1]
    for arquivo, alvo, troca, _razao in TRECHOS_MANUAIS:
        if arquivo != base:
            continue
        if texto.count(alvo) != 1:
            faltando.append(arquivo)
            continue
        texto = texto.replace(alvo, troca)
    return texto, faltando


# O transpilador da ultima unidade processada, para o teste alcancar os
# contadores (statements duplicados pelo `[[fallthrough]]`) sem que eles virem
# retorno de `transpilar_unidade`.
ULTIMO_TRANSPILADOR: "Transpilador | None" = None


def mapear_campos() -> dict[str, dict[str, TipoPas]]:
    """Campos de TODOS os registros, de todas as unidades.

    `Database.teams[i].bar_attack` mora em `we2002_database`, mas o tipo do
    campo esta em `we2002_team`. Sem o mapa completo o transpilador nao sabe
    que `bar_attack` e ShortInt e deixa de inserir o `Ord()` que o C++ fazia
    sozinho -- e ai o FPC reprova com "got Char expected ShortInt", longe da
    causa.
    """
    fora: dict[str, dict[str, TipoPas]] = {}
    for unit, arquivos in UNITS:
        manual = MANUAIS.get(unit, Manual(itens={}))
        for rel in arquivos:
            caminho = CORE / rel
            if not caminho.exists():
                continue
            texto = caminho.read_text(encoding="utf-8")
            for it in (classificar(x) for x in partir_topo(texto)):
                if it.tipo != "classe" or _reivindicado(manual, it):
                    continue
                m = RE_CLASSE.match(it.texto)
                pas = REGISTROS.get(it.nome)
                if not m or not pas:
                    continue
                campos: dict[str, TipoPas] = {}
                for _ln, membro, _doc in partir_membros(m.group("corpo")):
                    limpo = re.sub(r"\{[^{}]*\}", "", membro).strip()
                    limpo = re.sub(r"^(?:public|private|protected)\s*:\s*", "",
                                   limpo)
                    if not limpo or "(" in limpo:
                        continue
                    d = RE_DECL_CAMPO.match(limpo)
                    if not d:
                        continue
                    for bruto in _partir_virgula(d.group("decls")):
                        nome, dims, _ = _declarador(bruto)
                        if not nome:
                            continue
                        try:
                            campos[nome] = tipo_de_campo(
                                it.nome, d.group("tipo"), nome, dims)
                        except ErroDeCampo:
                            pass
                fora[pas] = campos
    return fora


def transpilar_unidade(unit: str, arquivos: list[str]) -> tuple[str, list[Nota]]:
    """Devolve (pascal, recusas). Com recusa, o Pascal NAO deve ser gravado."""
    brutas = ler_fontes(unit, arquivos)
    notas: list[Nota] = []
    fontes: list[tuple[str, str]] = []
    for nome, texto in brutas:
        trocado, faltando = aplicar_trechos(nome, texto)
        for arquivo in faltando:
            notas.append(Nota(nome, 0, f"trecho portado a mao de `{arquivo}` "
                                       f"nao foi encontrado na entrada: o "
                                       f"porte a mao apodreceu"))
        fontes.append((nome, trocado))

    tp = Transpilador(unit, fontes)
    tp.campos = mapear_campos()
    global ULTIMO_TRANSPILADOR
    ULTIMO_TRANSPILADOR = tp
    pascal = _rodar(tp)
    notas += tp.notas
    notas += conferir(FORBIDDEN, pascal, f"{unit}.pas", pascal=True)
    entrada = "\n".join(t for _, t in fontes)
    notas += check_seeks(entrada, pascal, f"{unit}.pas")
    nao_usados = sorted(set(MANUAIS.get(unit, Manual({})).itens)
                        - tp.manuais_usados)
    for item in nao_usados:
        notas.append(Nota(f"{unit}.pas", 0,
                          f"porte a mao reivindica `{item}`, que nao existe "
                          f"mais na entrada"))
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
    saidas: dict[str, str] = {}
    for unit, arquivos in UNITS:
        try:
            pascal, notas = transpilar_unidade(unit, arquivos)
        except Refusal as exc:
            print(f"port_database_pas: RECUSA: {exc}", file=sys.stderr)
            return 1
        todas += notas
        if not notas:
            produzido[OUT_DIR / f"{unit}.pas"] = pascal
            saidas[unit] = pascal

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

    produzido[OUT_DOC] = emitir_doc(todas, saidas)

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
    if todas and not args.check:
        rc = 2
    return rc


if __name__ == "__main__":
    sys.exit(main())
