---
id: LOOKS-TASK-06
title: "`harness.py`, `controls.py` e `selftest.py` — o gate e os primeiros casos vermelhos"
type: implementação
category: verificação
phase: 1
depends_on: ["LOOKS-TASK-05"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §5.5"
status: concluído
---

# LOOKS-TASK-06: O gate e o controle negativo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §5.5 e
  §3.3.
- Molde pronto em `tools/mcr/`: `harness.Checker` e o `controls.Control` que
  planta **substituição literal no fonte** numa cópia da árvore e exige
  vermelho.
- *Guarda que nunca ficou vermelha é decoração.*

---

## Objetivo

`tools/looks/selftest.py` roda sem imagem, sem venv e sem display, e é o alvo
`looks_selftest`.

---

## Critério de conclusão

- [x] `harness.py` com `Checker`: `ok` / `attempt` / `refuses` / `skip` /
      `report`.
- [x] **O harness não se confere com ele mesmo.** O ramo de falha do `ok` é
      exercitado por um caminho que não passa pelo próprio `ok` — foi assim que
      o ciclo do `.mcr` pegou o `harness-counts-nothing`.
- [x] `controls.py` com, no mínimo, os três controles da §5.5: trocar 24 por 20
      no tamanho de primitiva; inverter a ordem da lista de montagem; e
      (quando a Fase 3 existir) trocar uma paleta por outra.
- [x] Substituição que casa 0 ou mais de 1 vez é control **quebrado**, não
      vermelho, e o relatório diz isso.
- [x] As três regras de desenho da §3.3 varridas mecanicamente, com
      `os.walk` — e não `os.listdir`, que não enxerga `ui/`.
- [x] **A regra 1 reusa o `layout.sweep_addresses()`**, que já existe desde a
      [`LOOKS-TASK-03`](/docs/tasks/looks/03-fonte-de-disco-e-layout.md) — o
      agregador não escreve um segundo varredor de endereço. Dois varredores
      da mesma regra divergem em silêncio, e o que ficar sem chamador vira
      código morto que ninguém percebe apodrecer
      ([`CORR-LOOKS-009`](/docs/tasks/looks/CORR-LOOKS-009.md)).
- [x] O `looks_selftest` **falha** se a varredura da regra 1 achar alguma
      coisa, e o Log copia a linha com a contagem que ela imprime — `(N
      file(s), M line(s) swept)`. Varredura que não abriu arquivo nenhum tem
      de ser visível na saída, não dedutível.
- [x] A contagem de controles é **impressa pela ferramenta**, nunca escrita em
      prosa.

---

## Log de Execução

**Executado em:** 2026-09-14

### Resumo do que foi feito

O ciclo ganhou o gate obrigatório: `harness.py`, `controls.py` e `selftest.py`,
mais o alvo `looks_selftest` no `tests/CMakeLists.txt`. Ele roda **sem imagem,
sem venv e sem display**, e derruba a variável `WE2002_LOOKS_IMAGE` do próprio
ambiente — com ela posta, um módulo poderia tomar um caminho que não existe
numa máquina limpa, e o gate ficaria verde aqui e vermelho lá.

```
modules: 0 failure(s)
rules:   0 failure(s)      ..... rule 1 swept 7 file(s), 2206 line(s)
controls: 0 failure(s)     ..... 8 of 8 controls red
looks_selftest: 0 failure(s)
```

O que a task ensinou está quase todo do lado vermelho: **três dos oito
controles ficaram verdes na primeira corrida, e nenhum por culpa do controle.**
Cada um apontou um buraco real no `self_check` que ele deveria derrubar. É
exatamente para isso que o controle negativo existe, e é a primeira vez neste
ciclo que ele paga.

### Os três buracos que os controles acharam

**1. `modelfile-list-order` — o `read_models()` podia ordenar os alvos e
ninguém via.** O `self_check()` da LOOKS-TASK-05 construía um `Model` invertido
**à mão** e comparava com ele mesmo; nunca perguntava se o `read_models()`
tinha preservado a ordem da lista. Agora pergunta contra o `layout`:

```python
declared = layout.record_lists(data)
assert [one.targets for one in models] == declared
```

E isso destravou um segundo defeito, na mesma linha: **as listas do arquivo
sintético estavam em ordem crescente**, iguais à ordem de arquivo. Ordená-las
seria invisível. O `_build_file()` passou a emitir cada lista na ordem
**inversa** da colocação, que é a propriedade que o módulo inteiro existe para
preservar.

**2. `layout-empty-slot` — a ramificação do par `(0, 0)` nunca era executada.**
O sintético não tinha nenhum. Plantar um resolveu, mas só na segunda tentativa:
posto **no começo** da lista, ele é engolido pela heurística do
`[contagem][pad]`, que lê qualquer segunda palavra não-ponteiro como preâmbulo.
O slot vazio tem de ficar **no meio** para exercitar o que se quer.

**3. `section-gap-fixed` — o `modelfile` não via um `skip_gap` quebrado**,
porque o arquivo sintético colocava as seções **coladas**. Com folgas de 12 e 8
bytes entre elas — como o `EDT_MOD.BIN` real — ele vê. E aqui houve um erro
meu de indexação: as folgas eram escolhidas por `len(bodies) % 2`, e como cada
folga é ela mesma acrescentada a `bodies`, o índice era sempre ímpar e **toda
folga saía 8**; o caso de 12 nunca existiu. Passou a indexar por seções
colocadas.

O quarto verde era do controle: `section-separator-is-eof` casava **duas**
vezes, porque `walk()` e `scan()` carregam a mesma linha. O `scan()` ganhou uma
grafia distinguível. **Casar 0 ou 2 vezes é controle quebrado, e o relatório
diz isso** — foi o `--check` do catálogo que pegou, antes de qualquer sandbox.

### E o gate quase ficou verde por não medir nada

A varredura de idioma (§3.5) foi escrita através de heredoc de shell, e o `\b`
dentro de uma string Python **não-raw** virou um **byte de backspace**. O padrão
compilado era `<BS>vertice<BS>`, que não casa com nada — e a varredura passou a
imprimir árvore limpa. Dois bytes `0x08` invisíveis no arquivo, e o `sed`
mostrando a linha como normal.

É a forma exata contra a qual este módulo inteiro é escrito, e aconteceu com
ele primeiro. O conserto foi em dois tempos: os padrões passaram a ser
construídos por `_word_patterns()`, com âncora de verdade, **e a varredura
ganhou caso vermelho plantado** — uma árvore temporária com `# o ponteiro para
o arquivo` dentro, que ela tem de achar, mais um `clean.py` com `2,461
vertices` que ela **não** pode acusar.

A âncora também não é enfeite: sem ela, `vertice` casa dentro do inglês
`vertices` — **quinze falsos positivos** na primeira corrida honesta, e
varredura que grita à toa tem a lista de palavras podada até não pegar mais
nada.

### O gate visto ficando vermelho

Não basta o `0 failure(s)`. Com `PLANTED = 0x8016E800` acrescentado ao
`section.py` numa cópia da árvore (nada commitado):

```
FAIL  Rule 1: no address outside layout.py  [('section.py', 484, 'PLANTED = 0x8016E800')]
..... rule 1 swept 7 file(s), 2208 line(s)
looks_selftest: 1 failure(s)                                            (exit 1)
```

A contagem de arquivos e linhas é **impressa**, não deduzida: varredura que não
abriu arquivo nenhum e varredura que leu tudo imprimem a mesma frase, e é essa
frase que um leitor toma por "a regra 1 vale".

### O que ficou registrado como pulado, e por quê

Duas linhas de `skip`, e nenhuma delas é buraco escondido:

- **Regra 2** (byte cru é normativo) não é varredura: é a varredura de seção
  fechando no EOF exato contra o arquivo real, e isso mora no
  `modelfile --check-image`, que é o `looks_image`. Dito em voz alta para a
  conta de regras conferidas ser honesta.
- **Regra 3, primeira metade** (a UI não conhece endereço) não tem `ui/` ainda
  — LOOKS-TASK-15. A **segunda** metade roda: `PySide6 not in sys.modules`
  depois de importar o núcleo inteiro, que é o que impede o gate obrigatório de
  passar a exigir venv no dia em que alguém importar Qt acima do núcleo.

### O controle da paleta, que é da Fase 3

A §5.5 nomeia três controles, e o terceiro — trocar uma paleta por outra — não
tem o que derrubar enquanto não houver leitura de paleta. Os oito de hoje
cobrem os outros dois e mais seis. A linha está escrita **na**
[`LOOKS-TASK-12`](/docs/tasks/looks/12-pele-paleta-ou-vertice.md), que é quem
decide se a pele é paleta ou vértice, e não só aqui.

### Arquivos criados/modificados

- `tools/looks/harness.py` — **novo**. `Checker` (`ok`/`attempt`/`refuses`/
  `skip`/`report`), `run()` com a guarda externa, e o `self_check()` cujo
  `raise` nu é o único caminho que não passa pelo `ok`
- `tools/looks/controls.py` — **novo**. `Control`, os **8** do catálogo, o
  sandbox (que leva o `tools/pes2/` junto, senão a falha é de import e não do
  defeito), `plant()`, `run_all()` e um `--check` que exige casamento único
- `tools/looks/selftest.py` — **novo**. O agregador: `self_check` de cada
  módulo sob a guarda, as três regras de desenho, a varredura de idioma com
  caso vermelho, e os controles
- `tools/looks/layout.py` — o sintético ganhou par `(0, 0)` **no meio** de uma
  lista, com o red 11
- `tools/looks/modelfile.py` — folgas entre as seções do sintético, listas
  emitidas em ordem inversa da colocação, e a asserção de que a ordem entregue
  é a que o `layout` declara
- `tools/looks/section.py` — o `scan()` com grafia própria do teste de
  separador, para o controle poder nomear uma ocorrência
- `tests/CMakeLists.txt` — o alvo `looks_selftest`
- `docs/tasks/looks/12-pele-paleta-ou-vertice.md` — o controle de paleta
- `docs/tasks/looks/progresso.md` — tabela e checklist da Fase 1
- `docs/tasks/looks/06-harness-controles-e-selftest.md` — este arquivo

### Problemas encontrados

Um que vale para quem rodar o `ctest` aqui, e não é desta task:

**`ctest -R looks` nesta máquina responde `No tests were found!!!` e sai
`0`.** O `build/` do worktree foi gerado no Linux (`/usr/bin/cmake`,
`/home/ingmar/...`) e não corresponde a esta árvore. É a mesma armadilha que a
[`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md) mediu — saída que lê
como verde —, agora pela outra causa. O registro dos dois alvos foi conferido
**textualmente** no `tests/CMakeLists.txt`, e cada um foi rodado pela linha de
comando; quem reconfigurar o build no Linux fecha o `ctest -R looks`.

> **A última frase estava incompleta**, e a
> [`CORR-LOOKS-015`](/docs/tasks/looks/CORR-LOOKS-015.md) a remediu no mesmo
> dia: **fecha aqui também**, num build fora da árvore configurado com
> `-G Ninja` e o toolchain do vcpkg — `1 passed, 1 skipped`. Sem o toolchain,
> o `find_package(CURL REQUIRED)` do `src/core` derruba a configuração e leva
> os dez testes Python junto. A receita está na tabela de gates do
> [`perfil-looks.md`](/docs/prompts/perfil-looks.md).

E o de sempre: **`tools/pes2/selftest.py` continua sem rodar aqui** (lê
`/proc/self/fd`). O sandbox dos controles copia `tools/pes2/`, mas nunca o
executa — só o `iso_source.py` precisa dele para importar.
