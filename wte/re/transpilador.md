# O transpilador da camada de dados — a tabela e as recusas

**GERADO por `wte/tools/port_database_pas.py` — não editar à mão.**
Regenerar: `python3 wte/tools/port_database_pas.py`.

Produto da [WTE-TASK-17](../../docs/tasks/17-transpilador-da-camada-de-dados.md). A lista de recusas abaixo é o
worklist da [WTE-TASK-18](../../docs/tasks/18-camada-de-dados-gerada.md).

---

## O limite duro

**A entrada é sempre código deste repositório.** Nunca saída de decompilador —
[`PLAN-WTE-LAZARUS.md`](../../docs/PLAN-WTE-LAZARUS.md) §8.10. O `FORBIDDEN` só segura porque
a entrada é um subconjunto conhecido e pequeno; contra decompilado ele deixa de
recusar o que importa e o gerador passa a emitir Pascal que compila, passa em teste
unitário e **grava bytes errados**.

## Entrada

| Unidade Pascal | Origem em `src/core/` | Linhas |
|---|---|---|
| `we2002_types.pas` | `include/we2002/Types.hpp` | 147 |
| `we2002_cdimage.pas` | `include/we2002/CdImage.hpp`, `CdImage.cpp` | 166 |
| `we2002_textcodec.pas` | `include/we2002/TextCodec.hpp`, `TextCodec.cpp` | 95 |
| `we2002_player.pas` | `include/we2002/Player.hpp`, `Player.cpp` | 225 |
| `we2002_database.pas` | `include/we2002/Database.hpp`, `Database.cpp` | 1764 |
| **Total** | | **2397** |

`Sofifa.cpp` fica **fora**: o import do SoFIFA está desligado no `newWe2002` desde
2026-08-05, o editor do Obocaman não tem nada equivalente, e as linhas não teriam
consumidor.

---

## A tabela de substituição — 47 regras, aplicadas em ordem

A ordem é significativa: as regras de comparação rodam **antes** da regra de
atribuição, senão `==` viraria `:==`.

| # | Razão | Padrão |
|---|---|---|
| 1 | == -> = (marcado) | `(?<![<>=!+\-*/%&\|^])==(?!=)` |
| 2 | != -> <> | `!=` |
| 3 | <= (protegido de <) | `<=` |
| 4 | >= (protegido de >) | `>=` |
| 5 | && -> and | `&&` |
| 6 | || -> or | `\\|\\|` |
| 7 | ! -> not | `!\s*(?=\w\|\()` |
| 8 | << -> shl | `(?<![\w\s])\s*<<\s*` |
| 9 | >> -> shr | `(?<![\w\s])\s*>>\s*` |
| 10 | % -> mod | `(?<=\w)\s*%\s*(?=\w)` |
| 11 | -> -> . | `->` |
| 12 | & de argumento (Pascal passa por var) | `(?<=[(,])\s*&(?=\w)` |
| 13 | uint8_t -> Byte | `\bstd::uint8_t\b` |
| 14 | uint16_t -> Word | `\bstd::uint16_t\b` |
| 15 | uint32_t -> LongWord (nunca Cardinal) | `\bstd::uint32_t\b` |
| 16 | int32_t -> LongInt | `\bstd::int32_t\b` |
| 17 | int64_t -> Int64 | `\bstd::int64_t\b` |
| 18 | size_t -> SizeInt (so na fronteira) | `\bstd::size_t\b` |
| 19 | unsigned short -> Word | `\bunsigned\s+short\b` |
| 20 | unsigned char -> Byte | `\bunsigned\s+char\b` |
| 21 | unsigned int -> LongWord | `\bunsigned\s+int\b` |
| 22 | bool -> Boolean | `\bbool\b` |
| 23 | double -> Double | `\bdouble\b` |
| 24 | = delete (operacao apagada, sem comportamento) | `^\s*\w[\w:&<>\s\*]*\([^;\n]*\)\s*=\s*delete\s*;\s*$\n?` |
| 25 | static_cast<int> | `static_cast<\s*int\s*>\s*\(` |
| 26 | static_cast<unsigned int> | `static_cast<\s*unsigned int\s*>\s*\(` |
| 27 | cast para unsigned char* (var sem tipo) | `\(unsigned char\s*\*\)\s*` |
| 28 | cast (char): o ShortInt ja tem sinal | `\(char\)\s*` |
| 29 | Seek -> soBeginning | `\.Seek\(([^;\n]+?)\);` |
| 30 | SeekCurrent -> soCurrent | `\.SeekCurrent\(([^;\n]+?)\);` |
| 31 | strcpy -> CStrCopy | `\bstd::strcpy\b` |
| 32 | strcpy -> CStrCopy | `\bstrcpy\b` |
| 33 | strcat -> CStrCat | `\bstd::strcat\b` |
| 34 | strcat -> CStrCat | `\bstrcat\b` |
| 35 | strlen -> CStrLen | `\bstd::strlen\b` |
| 36 | strlen -> CStrLen | `\bstrlen\b` |
| 37 | literal de string | `"([^"\n]*)"` |
| 38 | = -> := | `(?<![<>=!+\-*/%&\|^:])=(?![=])` |
| 39 | restaura = | `\x00EQ\x00` |
| 40 | restaura <= | `\x00LE\x00` |
| 41 | restaura >= | `\x00GE\x00` |
| 42 | += | `(\w+(?:\[[^\]\n]*\])?)\s*\+=\s*([^;\n]+);` |
| 43 | -= | `(\w+(?:\[[^\]\n]*\])?)\s*-=\s*([^;\n]+);` |
| 44 | x++ | `(\w+(?:\[[^\]\n]*\])?)\s*\+\+\s*;` |
| 45 | ++x | `\+\+\s*(\w+(?:\[[^\]\n]*\])?)\s*;` |
| 46 | x-- | `(\w+(?:\[[^\]\n]*\])?)\s*--\s*;` |
| 47 | --x | `--\s*(\w+(?:\[[^\]\n]*\])?)\s*;` |

### A armadilha que o precedente pagou

**`[^x]` casa `\n`.** Foi assim que um `Seek(begin)` virou `SeekCurrent` no
`tools/port_database.py`: compilava, passava nos testes, passava no ASan, e só o
confronto com o `ed.exe` mostrou. Toda regra que não pode atravessar linha escreve
`[^x\n]`, e há um teste que reprova regra nova sem isso (`test_port_database_pas.py`).

---

## O que o `FORBIDDEN` recusa — 30 construções

Recusa não é falha: é **trabalho identificado**. Cada uma tem três saídas, e a
decisão vai escrita em `wte/re/recusas.md` (WTE-TASK-18) — estender a tabela,
ajustar a entrada, ou portar o trecho à mão.

| Construção | Por que não há tradução decidida |
|---|---|
| `\bstd::(?:vector\|map\|unordered_map\|set\|list\|deque\|array)\b` | conteiner da STL: wte/re/tipos.md manda RECUSAR em vez de improvisar equivalente Pascal (a decisao 'o que nao entra na camada de dados') |
| `\bstd::function\b` | std::function: so o Reporter usa, e ele vira `TReporter = procedure(const Msg: string) of object`. Se aparecer noutro lugar, o mapeamento nao cobre |
| `\bstd::(?:sort\|find\|copy\|fill\|max\|min\|transform\|accumulate)\b` | <algorithm>: sem equivalente decidido; a entrada nao deveria usar |
| `\[\s*[&=]?\s*\]\s*\(` | lambda: sem traducao decidida |
| `\btemplate\s*<` | template: fora do subconjunto |
| `\breinterpret_cast\b` | reinterpret_cast: reinterpretar memoria por regra textual e como o bitfield embaralhou numero de camisa no newWe2002. Porte a mao |
| `\bconst_cast\b` | const_cast: sem traducao decidida |
| `\bdynamic_cast\b` | dynamic_cast: fora do subconjunto |
| `\bnew\b\s+\w` | new: a camada de dados nao aloca |
| `\bdelete\b` | delete: a camada de dados nao aloca |
| `(?<![\w>\]\)])\w+\s*\+\+?\s*\+\s*\d+\s*\)\s*\+\+` | aritmetica de ponteiro |
| `\bgoto\b` | goto: nao ha rotulo no Pascal gerado |
| `\[\[fallthrough\]\]` | fallthrough de switch: o `case` do Pascal NAO cai para o proximo ramo. Traduzir literalmente muda o comportamento em silencio -- e este e um `case` que decide QUANTOS bytes ler da imagem. Duplique o ramo ou reescreva como if/else, e registre em wte/re/recusas.md |
| `\?[^;\n]*:[^;\n]*;` | operador ternario: sem traducao textual segura (o `:` colide com a sintaxe de rotulo e de tipo) |
| `\bsizeof\b` | sizeof: o SizeOf do FPC existe, mas o tamanho pode DIVERGIR do C++ (alinhamento e packing). Cada uso precisa de decisao escrita |
| `\bstatic_assert\b` | static_assert: sem equivalente; vira teste |
| `\bunion\b` | union: sem traducao decidida |
| `\bstd::(?:cout\|cerr\|cin)\b` | iostream: a camada de dados nao imprime |
| `\bprintf\b\|\bsprintf\b` | printf: sem traducao decidida |
| `\b_itoa\b` | _itoa: CRT so do MSVC |
| `#\s*(?:ifdef\|ifndef\|if)\b` | compilacao condicional: a saida seria dependente de plataforma, que e exatamente o que a regra zero de wte/re/tipos.md proibe |
| `^\s*\{\s*$\|^\s*\}\s*;?\s*$` | bloco `{ }`: o passe estrutural (begin/end) nao esta implementado -- WTE-TASK-18 |
| `\bfor\s*\([^;\n]*;[^;\n]*;[^)\n]*\)` | cabecalho de `for` no estilo C: vira `for .. to .. do` (passo 1) ou `while` (passo != 1), e isso e passe estrutural -- WTE-TASK-18 |
| `^\s*(?:void\|LongInt\|Boolean\|Byte\|Word\|LongWord\|Int64\|Double)\s+[\w:]+\s*\([^)\n]*\)\s*$` | assinatura de funcao: vira `procedure`/`function` com `var` hoisted -- WTE-TASK-18 |
| `^\s*struct\s+\w+\s*\{?` | declaracao de `struct`: vira `record`, com a decisao de `packed` por campo (tipos.md) -- WTE-TASK-18 |
| `->` | '->' sobrou: alguma regra de SUBS nao casou |
| `\bstd::` | 'std::' sobrou: alguma regra de SUBS nao casou |
| `(?<![<>=!+\-*/%&\|^])==(?![=])` | '==' sobrou: regra de comparacao falhou |
| `!=` | '!=' sobrou: regra de comparacao falhou |
| `&&\|\\|\\|` | '&&'/'||' sobrou: regra booleana falhou |

Comentário e literal são **mascarados** antes da varredura. Sem isso o comentário
`// the new national sides are elsewhere` do `Database.cpp` era acusado como uso de
`new` — e recusa falsa manda a WTE-TASK-18 investigar trabalho que não existe.

---

## O segundo guard: `check_seeks()`

Conta seek absoluto e relativo na entrada e na saída e recusa se não baterem. O
`FORBIDDEN` não vê isto: uma regra que troca a direção de um seek não deixa token
nenhum para trás, e o resultado compila.

**Ele vale mais em Pascal, não menos.** `Seek(x, soBeginning)` e `Seek(x, soCurrent)`
diferem por uma palavra no meio da chamada, e não por um nome de método — a
diferença que em C++ era `Seek` contra `SeekCurrent`.

Estado medido nesta execução:

| Origem | `Seek` absoluto | `SeekCurrent` relativo |
|---|---|---|
| `src/core/Database.cpp` | 142 | 16 |

---

## Recusas em aberto — o worklist da WTE-TASK-18

**493** recusa(s), em 13 motivo(s). Enquanto houver qualquer uma,
**nada é emitido** — o transpilador não produz unidade parcial.

| Ocorrências | Onde | Motivo |
|---|---|---|
| 283 | `Types.hpp:76`, `Types.hpp:115`, `Types.hpp:116`, `Types.hpp:144`, `Types.hpp:145` (+278) | bloco `{ }`: o passe estrutural (begin/end) nao esta implementado -- WTE-TASK-18 |
| 160 | `TextCodec.cpp:13`, `TextCodec.cpp:49`, `TextCodec.cpp:70`, `Database.cpp:96`, `Database.cpp:120` (+155) | cabecalho de `for` no estilo C: vira `for .. to .. do` (passo 1) ou `while` (passo != 1), e isso e passe estrutural -- WTE-TASK-18 |
| 33 | `CdImage.cpp:7`, `CdImage.cpp:9`, `CdImage.cpp:17`, `CdImage.cpp:20`, `CdImage.cpp:40` (+28) | 'std::' sobrou: alguma regra de SUBS nao casou |
| 4 | `Player.cpp:17`, `Player.cpp:51`, `Database.cpp:103`, `Database.cpp:801` | assinatura de funcao: vira `procedure`/`function` com `var` hoisted -- WTE-TASK-18 |
| 2 | `Types.hpp:33`, `CdImage.hpp:65` | declaracao de `struct`: vira `record`, com a decisao de `packed` por campo (tipos.md) -- WTE-TASK-18 |
| 2 | `Database.cpp:450`, `Database.cpp:1258` | fallthrough de switch na entrada |
| 2 | `Database.cpp:450`, `Database.cpp:1256` | fallthrough de switch: o `case` do Pascal NAO cai para o proximo ramo. Traduzir literalmente muda o comportamento em silencio -- e este e um `case` que decide QUANTOS bytes ler da imagem. Duplique o ramo ou reescreva como if/else, e registre em wte/re/recusas.md |
| 2 | `Types.hpp:78`, `Types.hpp:81` | static_assert: sem equivalente; vira teste |
| 1 | `Player.hpp:41` | conteiner da STL na entrada |
| 1 | `Player.hpp:41` | conteiner da STL: wte/re/tipos.md manda RECUSAR em vez de improvisar equivalente Pascal (a decisao 'o que nao entra na camada de dados') |
| 1 | `CdImage.hpp:33` | delete: a camada de dados nao aloca |
| 1 | `Types.hpp:78` | sizeof: o SizeOf do FPC existe, mas o tamanho pode DIVERGIR do C++ (alinhamento e packing). Cada uso precisa de decisao escrita |
| 1 | `Database.hpp:15` | std::function: so o Reporter usa, e ele vira `TReporter = procedure(const Msg: string) of object`. Se aparecer noutro lugar, o mapeamento nao cobre |

