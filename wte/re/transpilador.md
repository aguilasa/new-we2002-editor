# O transpilador da camada de dados — a tabela, os guards e o que ficou a mão

**GERADO por `wte/tools/port_database_pas.py` — não editar à mão.**
Regenerar: `python3 wte/tools/port_database_pas.py`.

Produto da [WTE-TASK-17](../../docs/tasks/concluidos/17-transpilador-da-camada-de-dados.md) (tabela e guards) e da
[WTE-TASK-18](../../docs/tasks/concluidos/18-camada-de-dados-gerada.md) (passe estrutural e portes a mão).
A rota escolhida para cada recusa está em [`recusas.md`](recusas.md).

---

## O limite duro

**A entrada é sempre código deste repositório.** Nunca saída de decompilador —
[`PLAN-WTE-LAZARUS.md`](../../docs/PLAN-WTE-LAZARUS.md) §8.10. O `FORBIDDEN` só segura porque
a entrada é um subconjunto conhecido e pequeno; contra decompilado ele deixa de
recusar o que importa e o gerador passa a emitir Pascal que compila, passa em teste
unitário e **grava bytes errados**.

## Entrada e saída

| Unidade Pascal | Origem em `src/core/` | Linhas C++ | Linhas Pascal |
|---|---|---|---|
| `we2002_types.pas` | `include/we2002/Types.hpp` | 147 | 151 |
| `we2002_team.pas` | `include/we2002/Team.hpp`, `Team.cpp` | 107 | 147 |
| `we2002_cdimage.pas` | `include/we2002/CdImage.hpp`, `CdImage.cpp` | 166 | 182 |
| `we2002_textcodec.pas` | `include/we2002/TextCodec.hpp`, `TextCodec.cpp` | 95 | 163 |
| `we2002_player.pas` | `include/we2002/Player.hpp`, `Player.cpp` | 225 | 194 |
| `we2002_database.pas` | `include/we2002/Database.hpp`, `Database.cpp` | 1764 | 2147 |
| **Total** | | **2504** | **2984** |

### O que fica de fora, e por quê

Lista fechada: o `test_nenhuma_entrada_do_core_fica_de_fora` cruza-a com o que
existe em `src/core/` e **reprova** se sobrar arquivo que ninguém reivindicou —
nos dois sentidos, então motivo escrito para arquivo que sumiu também reprova.

| Arquivo | Motivo |
|---|---|
| `Sofifa.cpp` | o import do SoFIFA esta desligado no newWe2002 desde 2026-08-05, o editor do Obocaman nao tem nada equivalente, e as linhas nao teriam consumidor. Decisao registrada na WTE-TASK-18. |
| `Tables.cpp` | e do gen_tables_pas.py (WTE-TASK-16), nao deste gerador |
| `include/we2002/Offsets.hpp` | idem Tables.cpp |
| `include/we2002/Sofifa.hpp` | idem Sofifa.cpp |
| `include/we2002/Tables.hpp` | idem Tables.cpp |

A guarda existe porque a ausência **já aconteceu**: a primeira versão do
`UNITS` esqueceu `Team.hpp` e `Team.cpp` — que declaram `Team`, `MlTeam` e
`Formation`, os três registros que `Database.hpp:45-48` usa como campo — e nada
no `--check` acusou. Quem apanhou foi revisão humana ([CORR-WTE-034](../../docs/tasks/concluidos/CORR-WTE-034.md)).

---

## A tabela de substituição — 53 regras, aplicadas em ordem

A ordem é significativa: as regras de comparação rodam **antes** da regra de
atribuição, senão `==` viraria `:==`; e as compostas bit-a-bit (`&=`) antes de
`&` virar `and`.

Antes das regras rodam três passes que nenhuma regex faz sozinha:

1. **`_proteger()`** tira comentário e literal do caminho. Sem isso a mensagem
   `"Error ! Impossible to open CD image !"` saia como `'Error not Impossible …'`
   — a regra `!` → `not` comia dentro do literal. Achado da WTE-TASK-18.
2. **`parentizar_booleanos()`** põe parênteses nos operandos de `&&`/`||`. Em C `==`
   liga mais forte que `&&`; em Pascal `and` liga mais forte que `=`, e sem os
   parênteses `a = 1 and b > 2` vira `a = (1 and b) > 2`.
3. **`traduzir_enderecos()`** decide `&` por rotina chamada: some em parâmetro `var`
   sem tipo (`Read`/`Write`/`CStrCopy`), vira `@` em parâmetro de ponteiro
   (`ResolveMlLink`, `KanjiToAscii`). Rotina não classificada **recusa**.

| # | Razão | Padrão |
|---|---|---|
| 1 | == -> = (marcado) | `(?<![<>=!+\-*/%&\|^])==(?!=)` |
| 2 | != -> <> | `!=` |
| 3 | <= (protegido de <) | `<=` |
| 4 | >= (protegido de >) | `>=` |
| 5 | && -> and | `&&` |
| 6 | || -> or | `\\|\\|` |
| 7 | ! -> not | `!(?=[^\S\n]*[\w(])` |
| 8 | << -> shl | `<<` |
| 9 | >> -> shr | `>>` |
| 10 | % -> mod | `(?<=\w)\s*%\s*(?=\w)` |
| 11 | -> -> . | `->` |
| 12 | 0x.. -> $.. | `\b0[xX]([0-9a-fA-F]+)\b` |
| 13 | &= | `(\w+(?:\[[^\]\n]*\])?)\s*&=\s*([^;\n]+);` |
| 14 | |= | `(\w+(?:\[[^\]\n]*\])?)\s*\\|=\s*([^;\n]+);` |
| 15 | ^= | `(\w+(?:\[[^\]\n]*\])?)\s*\^=\s*([^;\n]+);` |
| 16 | & -> and (bit a bit) | `(?<![&\w])&(?![&])` |
| 17 | | -> or (bit a bit) | `(?<![\|\w])\\|(?![\|])` |
| 18 | static_cast<int> | `static_cast<\s*int\s*>\s*\(` |
| 19 | static_cast<unsigned int> | `static_cast<\s*unsigned int\s*>\s*\(` |
| 20 | cast para unsigned char* -> @ | `\(unsigned char\s*\*\)\s*` |
| 21 | cast (char): o ShortInt ja tem sinal | `\(char\)\s*` |
| 22 | (int)std::ceil -> Ceil (unidade Math) | `\(int\)\s*std::ceil\b` |
| 23 | uint8_t -> Byte | `\bstd::uint8_t\b` |
| 24 | uint16_t -> Word | `\bstd::uint16_t\b` |
| 25 | uint32_t -> LongWord (nunca Cardinal) | `\bstd::uint32_t\b` |
| 26 | int32_t -> LongInt | `\bstd::int32_t\b` |
| 27 | int64_t -> Int64 | `\bstd::int64_t\b` |
| 28 | size_t -> SizeInt (so na fronteira) | `\bstd::size_t\b` |
| 29 | unsigned short -> Word | `\bunsigned\s+short\b` |
| 30 | unsigned char -> Byte | `\bunsigned\s+char\b` |
| 31 | unsigned int -> LongWord | `\bunsigned\s+int\b` |
| 32 | bool -> Boolean | `\bbool\b` |
| 33 | double -> Double | `\bdouble\b` |
| 34 | Seek -> soBeginning | `\.Seek\(([^;\n]+?)\);` |
| 35 | SeekCurrent -> soCurrent | `\.SeekCurrent\(([^;\n]+?)\);` |
| 36 | Report -> Reportar (colisao de caixa) | `\bReport\s*\(` |
| 37 | strcpy -> CStrCopy | `\bstd::strcpy\b` |
| 38 | strcpy -> CStrCopy | `\bstrcpy\b` |
| 39 | strcat -> CStrCat | `\bstd::strcat\b` |
| 40 | strcat -> CStrCat | `\bstrcat\b` |
| 41 | strlen -> CStrLen | `\bstd::strlen\b` |
| 42 | strlen -> CStrLen | `\bstrlen\b` |
| 43 | = -> := | `(?<![<>=!+\-*/%&\|^:])=(?![=])` |
| 44 | chamada sem argumento: o Pascal dispensa `()` | `(\w)\(\s*\)` |
| 45 | restaura = | `\x00EQ\x00` |
| 46 | restaura <= | `\x00LE\x00` |
| 47 | restaura >= | `\x00GE\x00` |
| 48 | += | `(\w+(?:\[[^\]\n]*\])?)\s*\+=\s*([^;\n]+);` |
| 49 | -= | `(\w+(?:\[[^\]\n]*\])?)\s*-=\s*([^;\n]+);` |
| 50 | x++ | `(\w+(?:\[[^\]\n]*\])?)\s*\+\+\s*;` |
| 51 | ++x | `\+\+\s*(\w+(?:\[[^\]\n]*\])?)\s*;` |
| 52 | x-- | `(\w+(?:\[[^\]\n]*\])?)\s*--\s*;` |
| 53 | --x | `--\s*(\w+(?:\[[^\]\n]*\])?)\s*;` |

### A armadilha que o precedente pagou

**`[^x]` casa `\n`.** Foi assim que um `Seek(begin)` virou `SeekCurrent` no
`tools/port_database.py`: compilava, passava nos testes, passava no ASan, e só o
confronto com o `ed.exe` mostrou. Toda regra que não pode atravessar linha escreve
`[^x\n]`, e há um teste que reprova regra nova sem isso (`test_port_database_pas.py`).

---

## O que o `FORBIDDEN` recusa — 34 construções

Recusa não é falha: é **trabalho identificado**. Cada uma tem três saídas, e a
decisão vai escrita em [`recusas.md`](recusas.md) — estender a tabela, ajustar a
entrada, ou portar o trecho à mão.

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
| `\bcontinue\b` | continue: o passe estrutural traduz `for` de passo != 1 para `while` com o incremento no FIM do corpo. Um `continue` pularia esse incremento e faria laco infinito -- silencioso, e so contra a imagem apareceria |
| `\[\[fallthrough\]\]` | fallthrough de switch: o `case` do Pascal NAO cai para o proximo ramo. Traduzir literalmente muda o comportamento em silencio -- e este e um `case` que decide QUANTOS bytes ler da imagem. Duplique o ramo ou reescreva como if/else, e registre em wte/re/recusas.md |
| `\?[^;\n]*:[^;\n]*;` | operador ternario: sem traducao textual segura (o `:` colide com a sintaxe de rotulo e de tipo) |
| `\bsizeof\b` | sizeof: o SizeOf do FPC existe, mas o tamanho pode DIVERGIR do C++ (alinhamento e packing). Cada uso precisa de decisao escrita |
| `\bstatic_assert\b` | static_assert: sem equivalente; vira teste |
| `\bunion\b` | union: sem traducao decidida |
| `\bstd::(?:cout\|cerr\|cin)\b` | iostream: a camada de dados nao imprime |
| `\bprintf\b\|\bsprintf\b` | printf: sem traducao decidida |
| `\b_itoa\b` | _itoa: CRT so do MSVC |
| `#\s*(?:ifdef\|ifndef\|if)\b` | compilacao condicional: a saida seria dependente de plataforma, que e exatamente o que a regra zero de wte/re/tipos.md proibe |
| `^\s*\{\s*$\|^\s*\}\s*;?\s*$` | bloco `{ }` sobrou: o passe estrutural nao reconheceu a forma |
| `\bfor\s*\([^;\n]*;[^;\n]*;[^)\n]*\)` | cabecalho de `for` no estilo C sobrou: o passe estrutural nao reconheceu a forma |
| `^\s*(?:void\|LongInt\|Boolean\|Byte\|Word\|LongWord\|Int64\|Double)\s+[\w:]+\s*\([^)\n]*\)\s*$` | assinatura de funcao sobrou: o passe estrutural nao reconheceu a forma |
| `^\s*struct\s+\w+\s*\{?` | declaracao de `struct` sobrou: o passe estrutural nao reconheceu a forma |
| `\bswitch\s*\(` | `switch` sobrou: o passe estrutural nao reconheceu a forma |
| `->` | '->' sobrou: alguma regra de SUBS nao casou |
| `\bstd::` | 'std::' sobrou: alguma regra de SUBS nao casou |
| `(?<![<>=!+\-*/%&\|^])==(?![=])` | '==' sobrou: regra de comparacao falhou |
| `!=` | '!=' sobrou: regra de comparacao falhou |
| `&&\|\\|\\|` | '&&'/'||' sobrou: regra booleana falhou |
| `&` | '&' sobrou: nem endereco-de com rotina classificada nem bit-a-bit. Classifique a rotina em CALLEE_VAR_SEM_TIPO ou CALLEE_PONTEIRO |
| `\b0[xX][0-9a-fA-F]+` | literal hexadecimal em forma de C sobrou |

Comentário e literal são **mascarados** antes da varredura. Sem isso o comentário
`// the new national sides are elsewhere` do `Database.cpp` era acusado como uso de
`new` — e recusa falsa manda investigar trabalho que não existe.

---

## O segundo guard: `check_seeks()`

Conta seek absoluto e relativo na entrada e na saída e recusa se não baterem. O
`FORBIDDEN` não vê isto: uma regra que troca a direção de um seek não deixa token
nenhum para trás, e o resultado compila.

**Ele vale mais em Pascal, não menos.** `Seek(x, soBeginning)` e `Seek(x, soCurrent)`
diferem por uma palavra no meio da chamada, e não por um nome de método.

Estado medido nesta execução:

| Origem | `Seek` absoluto | `SeekCurrent` relativo |
|---|---|---|
| `src/core/Database.cpp` | 142 | 16 |

---

## O terceiro guard: nada sai em silêncio

Todo item de topo de cada entrada — função, classe, constante, `using` — tem de
ser transpilado **ou** reivindicado por um porte à mão. Item que ninguém
reivindica recusa, e reivindicação de item que sumiu da entrada também.

| Unidade | Item C++ | Rota | Razão |
|---|---|---|---|
| `we2002_types` | `SetSquadNumberAt` | 3 (porte a mao) | acessor por mascara e deslocamento, idem |
| `we2002_types` | `SquadNumberAt` | 3 (porte a mao) | acessor por mascara e deslocamento, idem |
| `we2002_types` | `SquadNumbers` | 3 (porte a mao) | bitfield: a ordem de bit do `bitpacked record` do FPC e definida pelo compilador e nao e obrigada a casar com o que o MSVC fez em 2002 (tipos.md, decisao 2) |
| `we2002_types` | `static_assert` | 1 (virou teste) | sem equivalente no Pascal; virou teste (test_port_database_pas.TestUnidadesCompilam) |
| `we2002_cdimage` | `CdImage` | 3 (porte a mao) | std::fstream -> TFileStream: wte/re/tipos.md decisao 3 ja fixou um desenho que NAO e transpilacao (Read e nunca ReadBuffer, fmOpenReadWrite e nunca fmCreate, Seek de Int64) |
| `we2002_cdimage` | `Locate` | 3 (porte a mao) | idem SectorPosition |
| `we2002_cdimage` | `SectorPosition` | 3 (porte a mao) | registro de retorno com inicializacao por chaves; sai junto com o Locate |
| `we2002_player` | `FifaPlayer` | fora da camada de dados | a classe do import do SoFIFA, desligado no newWe2002 desde 2026-08-05; usa std::vector e std::string e nao tem consumidor no editor do Obocaman |
| `we2002_player` | `SofifaRules` | fora da camada de dados | declaracao adiantada da classe de regras do SoFIFA, idem |
| `we2002_database` | `Report` | 3 (porte a mao) | o `if (report)` do C++ testa um std::function vazio; em Pascal e `Assigned()` |
| `we2002_database` | `Reporter` | 3 (porte a mao) | std::function -> `procedure(const msg: string) of object` (tipos.md); a assinatura nao se transpila |
| `we2002_database` | `UrlSidecarPath` | 3 (porte a mao) | std::filesystem::path::string_type e String::replace nao tem forma transpilavel |
| `Database.cpp` | trecho `WriteUrlSidecar(image);` | 3 (porte a mão) | std::ofstream com operator<< e std::endl: tipos.md decisao 5 manda escrever o sidecar byte a byte, com #10 explicito. Virou a chamada TDatabase.WriteUrlSidecar, portada a mao |

---

## Recusas em aberto

**Nenhuma.** As seis unidades saem sem recusa em aberto.

