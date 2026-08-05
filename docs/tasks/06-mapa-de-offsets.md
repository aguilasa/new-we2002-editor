---
id: WTE-TASK-06
title: "re/offsets.md — a tabela em .data cruzada com Offsets.hpp"
type: extração
category: engenharia-reversa
phase: 1
depends_on: ["WTE-TASK-02"]
status: concluído
---

# WTE-TASK-06: Mapa de offsets

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §1.7 e Fase 1 item 4.
- **É o atalho do projeto inteiro.** Nenhum trabalho de RE começa sabendo o
  formato do arquivo-alvo; este começa.

Medido: **19 dos 69 `OFS_*`** de
[`Offsets.hpp`](../../src/core/include/we2002/Offsets.hpp) aparecem literalmente
no binário do Obocaman, quase todos num bloco contíguo de `.data` a partir de
`0x004231a0`:

```
va 0x004231a0  =  2002316   OFS_TEAM_NAME_KANJI
va 0x004231a4  =  4598596   OFS_TEAM_MIXED_CASE_NAME
va 0x004231b8  =  2003996   OFS_TEAM_NAME_3
va 0x004231bc  =  1012640   OFS_TEAM_NAME_1
...
va 0x004231d8  =  5651068   OFS_TEAM_ABBREV_2
```

Consequência: **qualquer instrução que indexe `0x004231a0` está mexendo em nome
de time**, e isso se sabe sem decompilar.

---

## Objetivo

`wte/re/offsets.md` respondendo três coisas.

### 1. Onde a tabela começa e onde termina

Medido no protótipo: o bloco tem buracos (`= 0`) e é seguido de dados que **não
são offsets** — `1869507948` é ASCII `l,km`. Achar o limite superior e o
inferior, com critério escrito.

**Esta é a armadilha §8.7 do plano.** Tratar como array algo que termina antes
do que se pensa é exatamente o bug do slot 64 num array de 63 que o `newWe2002`
já documentou. O limite tem de ser medido, não estimado pelo olho.

### 2. Quais dos 69 batem, e o que os outros 50 são

Os 50 restantes não aparecem como literal. Duas hipóteses, e o mapa deve dizer
qual vale para cada um: aritmética (`base + constante`, com a base na tabela),
ou região que o Moriero nomeou e o Obocaman não.

Não é preciso resolver os 50 aqui — a WTE-TASK-19 faz isso por diff dirigido.
Aqui basta **classificar** e deixar a lista de alvos.

### 3. Que offsets o Obocaman tem e nós não

O caminho inverso, e é o mais valioso: varrer `.data` e `.text` por dword
plausível (entre 1.000.000 e 8.000.000, alinhado, referenciado por código) que
**não** esteja em `Offsets.hpp`. Cada um é uma região do formato que este
repositório ainda não nomeou.

O `ed.exe` não edita camisa 2D nem lê `.mcr`; então os offsets dessas regiões,
se existirem, só existem do lado do Obocaman.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_offsets.py` | criar |
| `wte/re/offsets.md` | criar |
| `wte/re/offsets.tsv` | criar |

---

## Critério de conclusão

- [x] Limite da tabela medido, com o critério escrito (§8.7)
- [x] Os 19 confirmados, com VA e nome nosso
- [x] Os 50 restantes classificados por hipótese
- [x] Candidatos a offset que **não** estão em `Offsets.hpp` listados
- [x] Nenhum número no doc veio de contagem à mão
- [x] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-05

- **Resumo do que foi feito:**

  `wte/tools/dump_offsets.py` lê o `.exe` e o `Offsets.hpp` e gera
  `wte/re/offsets.tsv` (dados) e `wte/re/offsets.md` (prosa). Os dois são
  **inteiramente gerados** — inclusive o texto corrido do markdown, que mora
  como literal no script —, então o `--check` compara o markdown byte a byte e
  não sobra número não medido. Leitor de PE em stdlib pura, como o
  `dfm_extract.py`; nenhuma dependência nova.

  **Limite da tabela.** São duas tabelas: `0x004231a0`…`0x004231e8` (72 bytes,
  18 slots, 11 preenchidos, 7 buracos) e `0x00423634`…`0x00423648` (20 bytes,
  5 slots). Três medidas independentes concordam no limite superior da
  primeira: o conteúdo (primeiro dword que não é plausível nem zero), o
  próximo endereço de `.data` referenciado por `.text`, e o laço em
  `0x0040cbc8`, que percorre 3 linhas × 6 colunas com passo de linha `0x18`.
  O script **aborta** se os dois primeiros discordarem. **Zero é buraco, não
  terminador** — o `je` em `0x0040cbee` pula o slot vazio e continua; tratar
  zero como fim cortaria a tabela no slot 2 e perderia 9 offsets. O limite
  *inferior* é o endereço-base referenciado por código, e isso não é
  decoração: o dword logo abaixo é numericamente plausível (é o `xyz` + NUL
  que fecha a tabela de alfabeto vizinha).

  A tabela aparece **4 vezes** em `.data`, byte a byte igual; só a cópia
  canônica é referenciada por código. Candidato tem de ser contado por valor.

  **Os 69.** 19 confirmados, o mesmo número da §1.7 — mas só com varredura
  **desalinhada**: 2 dos 19 (`OFS_COST_NC`, `OFS_LINK_ML`) só existem como
  imediato de instrução, e uma varredura alinhada acha 17. Os 50 restantes
  saem classificados por busca em largura a partir das bases que o Obocaman
  comprovadamente tem: **H1 = 15** (base confirmada), **H2 = 26** (base é um
  candidato desta mesma execução), **H3 = 9** (`OFS_KIT_PREVIEW*`,
  `OFS_TEAM_NAME_5`/`_5_A`, `OFS_FLAG_COLOURS`/`_A`/`_B`). 5 candidatos
  ancoram uma família H2 inteira e são os alvos que valem primeiro na
  WTE-TASK-19.

  **Candidatos novos: 90**, todos pela rota `.text`. A rota `.data` devolveu
  **zero**, e isso é resultado: todo dword plausível que mora nas tabelas ao
  lado de um offset confirmado já está no `Offsets.hpp`.

- **Arquivos criados/modificados:**
  - `wte/tools/dump_offsets.py` (criado)
  - `wte/re/offsets.tsv` (criado, gerado)
  - `wte/re/offsets.md` (criado, gerado)
  - `docs/tasks/06-mapa-de-offsets.md` (este log)

- **Problemas encontrados:**

  1. **O filtro sugerido pela tarefa não sobrevive à medição.** "Entre
     1.000.000 e 8.000.000, alinhado" descarta **15 dos 69** offsets
     conhecidos (9 abaixo de 1.000.000, 4 acima de 8.000.000, 4 com valor não
     múltiplo de 4). Foi trocado por quatro cortes derivados de medida: faixa
     `[min, max]` do próprio header, geometria do setor
     (`24 <= v % 2352 < 2072`, que os 69 satisfazem), "não é texto", e **não é
     alvo de realocação base**. Este último é o que faz o trabalho — sem ele a
     varredura de `.text` devolve mais de 1.500 candidatos, quase todos VAs do
     próprio módulo.

  2. **Descartar por janela de VA seria pior.** 5 dos 69 offsets conhecidos
     caem dentro de `[ImageBase, ImageBase+SizeOfImage)` por coincidência
     numérica (`OFS_TEAM_ABBREV_3` = 4234484 = `0x409CF4`). A `.reloc` separa
     endereço de constante sem heurística; a janela de VA não separa.

  3. **A §8.7 do plano erra o lado.** Ela diz que o bloco "é **seguido** de
     dados que não são offsets" e cita 1869507948 (ASCII). Medido, esse dword
     está em `0x00423190`, **16 bytes abaixo** da tabela — é `lmno`, pedaço da
     tabela de alfabeto. A conclusão da §8.7 continua válida (o bloco é
     cercado de não-offset dos dois lados), mas quem obriga a medir é o limite
     *inferior*, não o superior. Registrado no `offsets.md`; a §8.7 do plano
     **não foi editada** — é decisão do thread principal.

  4. **`wte/tools/README.md` não lista o `dump_offsets.py`.** Não foi editado
     por restrição do processo.

  5. A rota `.text` é varredura de padrão de byte, não desmontagem: produz
     falso positivo em posição que um decodificador linear nunca visitaria. O
     `offsets.md` nomeia um caso real (2204904, ocorrência única em
     `0x0042013f`, que cai no meio de `mov DWORD PTR fs:0x0,ecx`) e ordena os
     candidatos por número de ocorrências para calibrar confiança.
