---
id: LOOKS-TASK-04
title: "`section.py` — primitiva de 24 B, vértice de 8 B e o separador de zeros"
type: implementação
category: formato
phase: 1
depends_on: ["LOOKS-TASK-03"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §1.4"
status: concluído
---

# LOOKS-TASK-04: O formato de seção

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §1.4.
- O formato vem da §2.2 do
  [ANALISE-REPOS-WE3D-DBMANAGER.md](/docs/ANALISE-REPOS-WE3D-DBMANAGER.md), com
  **uma correção medida aqui**: a varredura contígua morre na seção 55 porque
  falta o par de zeros que separa grupos.
- **Não é arquivo TMD** — sem cabeçalho, sem tabela de objetos, sem passagem do
  `OpenTMD`. Tratar o arquivo como um desalinha tudo.

  > **A segunda metade deste bullet foi derrubada em 2026-09-14**, pela
  > [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md). Ele dizia
  > que a primitiva de 24 bytes é *gradation, no-texture*, "quatro cores e
  > quatro índices, **sem UV**" — a leitura do `we3d`. Ela **tem** UV: são
  > quatro pares `(u, v)` mais um CLUT id e uma página de textura, na ordem do
  > `POLY_FT4`. O Log abaixo fica como está, porque descreve o que esta task
  > mediu quando rodou; a leitura corrente é a §1.6 do plano.

---

## Objetivo

`tools/looks/section.py`: ler um cabeçalho de seção, suas primitivas e seus
vértices, e saber reconhecer o separador de grupo.

---

## Critério de conclusão

- [x] `numVertex`/`numPrimitive` lidos como `uint32` LE; tamanho calculado como
      `8 + nPrim*24 + nVert*8`.
- [x] Primitiva decodificada em **quatro cores (B,G,R,modo) e quatro índices**
      `v1,v0,v3,v2` — atenção à ordem, que não é `v0,v1,v2,v3`.
- [x] Vértice decodificado como `int16 x,y,z` mais um `uint16` de padding.
- [x] O par `numVertex == 0 && numPrimitive == 0` é reconhecido como
      **separador de grupo**, e não como fim de arquivo.
- [x] O byte de modo da primeira cor é **lido e registrado**, não descartado —
      é ele que decide a incógnita (d) na Fase 3.
- [x] `self_check()` contra seção sintética, com caso vermelho: trocar 24 por
      20 tem de ficar vermelho.

---

## Log de Execução

**Executado em:** 2026-09-14

### Resumo do que foi feito

`tools/looks/section.py` lê cabeçalho, primitivas e vértices, reconhece o
separador de grupo e devolve onde a passagem parou. Com ele, **os dois arquivos
varrem até o EOF exato**, com as contagens que o plano previa. Três coisas que
a execução mediu e que o plano dizia de outro jeito.

### 1. O separador é uma corrida de palavras zero, não "8 bytes"

A §1.4 dizia *"depois da última seção de um grupo vêm 8 bytes de zero"*. No
`MODEL.BIN` isso funciona — as seis folgas dele têm 8 bytes mesmo. No
`EDT_MOD.BIN` **não**: as folgas medidas são

```
[12, 12, 8, 8, 8, 8, 8, 8, 8, 8]   + 8 de cauda
```

Um varredor que consuma sempre 8 cai **4 bytes dentro** do próximo cabeçalho e
lê `nVert = 65.563` com `nPrim = 4.294.377.582`. Foi exatamente o que aconteceu
na primeira tentativa desta task, e o sintoma é o mesmo da seção 55: parece
formato errado, e é a regra do intervalo. Com a corrida de palavras:

```
/BIN/MODEL.BIN     106 secoes  2461 vert  1767 prim  grupos=[55, 1, 34, 7, 5, 4]  termina em 64800 (EOF=64800) EXATO
/BIN/EDT_MOD.BIN    11 secoes   690 vert   611 prim  grupos=[1]*11                termina em 36072 (EOF=36072) EXATO
```

> **Esta varredura começou no offset 15.704**, e o número acima é dela, não
> do arquivo. Do 216 — o menor alvo das **duas** listas de ponteiros — são
> **20 seções, 1.218 vértices, 1.074 primitivas**, fechando no mesmo EOF.
> Medido pela [`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md) em
> 2026-09-14; a transcrição acima fica como registro da corrida que a produziu.


Os dois lados batem com o plano, inclusive os grupos `[55, 1, 34, 7, 5, 4]`.

### 2. Isso muda o *motivo* de precisar da lista de ponteiros

A armadilha 3 do perfil diz que varrer o `EDT_MOD.BIN` sem a lista *"pega uma
seção e para"*. Com a regra certa, a varredura **acha as onze e termina no EOF
exato**. A lista continua indispensável — mas pela **ordem**, e ela é mesmo
outra:

```
lista:   19440 21832 24136 22984 26920 29704 33720 15704 31712 34896 17572
arquivo: 15704 17572 19440 21832 22984 24136 26920 29704 31712 33720 34896
```

Mesmo conjunto, sequência diferente: a primeira seção do arquivo é o **oitavo**
registro da lista. A §1.5 já dizia isso de um par de offsets; agora está medido
para os onze. Ordem errada aqui é peça trocada de lugar no boneco, sem sintoma
óbvio — a mesma armadilha do elenco de PES2. O `scan()` avisa no próprio
docstring que devolve **ordem de arquivo**, e manda quem precisa de ordem para
o `modelfile.py`.

**As duas correções de perfil foram escritas na
[`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md)**, que é
quem reconcilia o perfil — não só aqui no Log.

### 3. O quarto byte da cor não é `pad`: é modo, e só na cor 0

O `we3d` descreve a primitiva como `4 × cor (B,G,R,pad)`. Medido por posição de
cor, sobre todas as primitivas:

| | cor 0 | cores 1, 2, 3 |
| --- | --- | --- |
| `MODEL.BIN` (1.767) | `120`×1224, `121`×296, `122`×111, `127`×136 | `0` sempre |
| `EDT_MOD.BIN` (611) | `120`×70, `121`×112, `122`×429 | — |

Na cor 0 ele **nunca** é zero; nas outras três é **sempre**. É um byte de modo
**por primitiva**, guardado na primeira cor, e o `section.py` o preserva. É o
que a incógnita (d) usa na Fase 3, e um parser que o jogasse fora teria de ser
reescrito lá.

O `pad` do **vértice**, esse é pad mesmo: zero em 2.461 de 2.461. É o que o
distingue de uma quarta coordenada.

### 4. A cauda do `EDT_MOD.BIN`, e por que `scan()` existe

A última seção dele acaba em **36.064** e o arquivo tem **36.072**: há corrida
de zeros **depois** da última seção. Afirmar "termina no EOF" comparando o fim
da última seção erra por 8 bytes num arquivo lido perfeitamente — e manda
alguém procurar uma seção que não falta. Por isso o `scan()` devolve **onde a
passagem parou**, cauda consumida. No `MODEL.BIN` os dois valores coincidem, e
é por isso que medir só ele não mostraria a diferença.

### O controle 24 → 20

Em processo, a cada gate, e **sobre a varredura** e não sobre o span de uma
seção — porque uma primitiva menor ainda *parseia*, e o que quebra é o próximo
offset. Contra os arquivos reais:

```
/BIN/MODEL.BIN     recusado: section at 4440 claims 4293984282 vertices ... -> VERMELHO
/BIN/EDT_MOD.BIN   recusado: section at 17336 claims 4294901750 vertices ... -> VERMELHO
```

São sete casos no `self_check()`: o verde, o controle da varredura, seção
truncada, separador que não é seção, a corrida de 12 bytes que a regra fixa
erraria, a cauda que separa `scan().end` do fim da última seção, e o contador de
grupo subindo só no separador.

### A varredura da regra 1 ficou vermelha por prosa, e isso era defeito dela

O `layout.py --sweep` acusou **sete** linhas do `section.py`, das quais quatro
eram a **data `2026-09-14` dentro de docstring**. O stripper de aspas escrito na
task anterior não enxerga aspas triplas, então varria parágrafo de prosa como se
fosse código — e o gate ficava vermelho pela palavra "2026".

Anotar prosa com `# not-an-address:` teria sido o conserto errado: treinaria a
isenção sobre texto que nunca foi candidato, e a isenção precisa ser rara o
bastante para ser lida. O `sweep_addresses()` passou a usar **`tokenize`**, que
é o próprio Python dizendo o que é `NUMBER` e o que é `STRING`/`COMMENT`.
Conferido numa árvore de mentira:

```
arvore limpa (24, hex dentro de string, hex em comentario) -> []
com endereco plantado                                      -> dirty.py:1, dirty.py:2
com `# not-an-address:`                                    -> isento
arquivo que nao tokeniza                                   -> reportado na linha 1
```

O último é decisão: arquivo com erro de sintaxe é **reportado**, não pulado —
pular significaria a varredura parar de cobrir um arquivo exatamente enquanto
alguém o edita. Sobraram três isenções legítimas no `section.py`, todas o mesmo
byte de modo (`0x78`, `0x7A`), que é valor de formato e não endereço.

### Arquivos criados/modificados

- `tools/looks/section.py` — **novo**. `Primitive` (com `mode` e `corners`),
  `Vertex`, `Section`, `Scan`, `section_size()`, `read_header()`,
  `is_separator()`, `skip_gap()`, `read_primitive()`, `read_vertex()`,
  `read_section()`, `walk()`, `scan()`, `build_section()` e `self_check()`
- `tools/looks/layout.py` — o `sweep_addresses()` passou a ler tokens em vez de
  adivinhar aspas; saiu o `_strip_strings_and_comments()`, entrou o
  `_address_lines()`
- `docs/PLAN-LOOKS-PY.md` — §1.4 (a corrida de zeros no lugar dos 8 bytes, a
  cauda, o byte de modo, o pad do vértice) e §1.5 (a lista inteira contra a
  ordem de arquivo, e o motivo certo de a lista ser necessária)
- `docs/tasks/looks/20-reconciliacao-e-entregaveis.md` — as duas armadilhas do
  perfil com o conserto medido
- `docs/tasks/looks/progresso.md` — tabela e checklist da Fase 1
- `docs/tasks/looks/04-formato-de-secao.md` — este arquivo

### Problemas encontrados

Nenhum bloqueou. Fica registrado, do jeito que a task anterior registrou:
**`tools/pes2/selftest.py` continua sem rodar nesta máquina** (lê
`/proc/self/fd`), e nada aqui tocou aquele projeto.
