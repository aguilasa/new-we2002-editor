---
id: CORR-LOOKS-027
title: "Correção: o cross-check contra os 50 JPGs é critério marcado e não existe comando que o rode"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-LOOKS-027: a metade do cross-check da tupla que não virou comando

## Problema identificado

O critério da task tem duas testemunhas para a tupla de texto, e marca as duas
como feitas:

> - [x] A tupla de texto do corpus (`A-I3-A-F-A`) é lida e escrita. Conferida
>   contra os nomes dos 50 JPGs: **49 parseiam e formatam de volta para o próprio
>   nome**, e o `0.jpg` recusa com a mensagem certa. E contra as 95 linhas do
>   `data/defaultlook.txt`, que têm as **mesmas cinco colunas** — fixture
>   versionada, então essa parte do gate roda em qualquer clone.

**A segunda está no gate; a primeira não está em lugar nenhum.** O `--check`
afirma as 95 nações, as cinco colunas e os rótulos — conferido, roda sem disco.
Já os 50 nomes de arquivo não são lidos por comando algum do ciclo:
`tools/looks/looks.py` tem `--check`, `--check-image` e `--report <tupla>`, e
nenhum deles recebe pasta. Uma varredura de `grep` pelos módulos não acha
`.jpg`, `parsed:` nem `refused:` em parte alguma de `tools/looks/`, e o
`looks.py` não lê variável de ambiente nenhuma.

Os números reproduzem — remedi todos, abaixo —, e é justamente por isso que o
conserto é barato e vale: o que falta é o comando, não o resultado. E eles não
ficam parados: a própria task **encaminha a cobertura** para a
[`LOOKS-TASK-18`](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md) como
medida — *"a cobertura já fica medida lá: nove dos trinta e dois cabelos"* —, e
lá ela vai ser o ponto de partida de quem for medir os 50 renders.

O ciclo já tropeçou nisto duas vezes, nos dois sentidos: a
[`CORR-LOOKS-019`](/docs/tasks/looks/CORR-LOOKS-019.md), onde o número estava
certo e não havia comando, e a
[`CORR-LOOKS-022`](/docs/tasks/looks/CORR-LOOKS-022.md), onde não havia comando
**e** o número não reproduzia. A diferença entre as duas é sorte, e é o que esta
CORR quer tirar do caminho.

Como o Superpack não entra no git, o comando tem o mesmo formato dos outros dois
gates de dado externo: **roda com a pasta e pula com 77 sem ela** — é o contrato
que o perfil escreve e que o `looks_image` e o `mcr_card` já cumprem.

## Evidência

O que existe de CLI:

```text
$ python tools/looks/looks.py --report "<pasta dos 50 JPGs>"
BadLooks: '<pasta>' has 2 part(s) and a tuple has 5: skin_colour,
  hair_style, hair_colour, beard_style, beard_colour
      (o --report recebe uma tupla, nao uma pasta)

$ grep -rn "jpg\|parsed:\|refused:" tools/looks/*.py
tools/looks/controls.py:268:  "refused: the sixteen entries it returns straddle ..."
      (nada sobre o corpus)
```

E os números, remedidos nesta revisão com um script sobre o `looks.parse_tuple`
e o `looks.format_tuple` commitados:

```text
   refused: 0.jpg -- '0' has 1 part(s) and a tuple has 5: skin_colour, ...
50 .jpg   parsed: 49   refused: 1   round-trip to its own name: 49
   skin_colour   4 value(s) covered
   hair_style    9 value(s) covered
   hair_colour   4 value(s) covered
   beard_style   6 value(s) covered
   beard_colour  2 value(s) covered
```

Idênticos ao Log, inclusive a mensagem de recusa do `0.jpg` — e o round-trip
para o próprio nome, que o Log afirma e que nenhum comando exercita, dá 49 de
49.

**O resto da task reproduz inteiro, e a parte medida é a maior.** Vale listar,
porque decide a criticidade: os 1.449 registros contados de duas formas
independentes (`PLAYERS_TOTAL - PLAYERS_NC` no header do core, e a altura que
deixa de ser plausível no disco, com o registro 1.449 todo zerado); o
`OFS_PLAYER_ATTR` resolvendo para 157.164 pelo `ofs_map.py`; os dez domínios com
os mesmos valores usados (`28 of 32`, `7 of 8`, `6 of 8`, `4 of 8`, `38 of 64`,
`155..202`, `18..40`); as 95 nações e as cinco colunas do `defaultlook.txt`; e a
decodificação campo a campo, que o `self_check()` roda **contra o texto do
`Player::Decode()`** com caso vermelho — dessas eu ainda conferi, por fora, que
os **seis** `Seek` do `Database::Load` caem exatamente onde a leitura contígua
prevê (157.692+4, 159.744, 161.784+8, 163.836+4, 165.888, 167.928+8), o que é o
que autoriza o `records()` a ler o bloco de uma vez.

## Causa raiz

O cross-check do corpus foi feito por script descartável na sessão da execução, e
só a metade que tinha fixture versionada virou asserção.

## Correção

### Arquivo: `tools/looks/looks.py`

Um comando `--corpus <pasta>` (ou `--check-corpus`, no feitio dos outros
`--check-*`) que:

1. varre os `*.jpg` da pasta, conta quantos parseiam, quantos recusam e quantos
   **formatam de volta para o próprio nome** — é o round-trip que o Log afirma e
   que nenhuma corrida exercita hoje;
2. imprime a cobertura por campo, que é o número que a LOOKS-TASK-18 vai herdar;
3. **exige a recusa**: um nome que não é tupla tem de ser recusado, e o comando
   falha se todos passarem — sem isso um parser permissivo devolve 50 de 50 e a
   linha parece melhor;
4. **pula com 77 sem a pasta**, com a mensagem dizendo o que falta, como o
   `looks_image` faz — o Superpack é pasta do usuário e não entra no git.

A pasta pode vir por argumento e por variável de ambiente, e a variável é o que
permite que a LOOKS-TASK-19 a registre como alvo de `ctest` junto com os outros.

### Caso vermelho

O `self_check()` não precisa do Superpack para exercitar a regra: uma lista de
nomes sintéticos — quatro válidos e um inválido — afirma as três contagens e a
recusa. O controle de catálogo que faz o `parse_tuple` aceitar qualquer número de
partes já deixa isto vermelho, e se não existir, é um controle a mais.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/looks.py` | modificar |
| `docs/tasks/looks/13-campos-e-dominios-de-looks.md` | modificar |
| `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md` | modificar |

## Verificação

- [x] `python tools/looks/looks.py --corpus <pasta>` imprime 50 / 49 / 1 e o
      round-trip, e a cobertura por campo
- [x] sem a pasta, o mesmo comando **pula com 77** e diz o que falta
- [x] o `self_check()` exercita a regra com nomes sintéticos, recusa incluída
- [x] o critério da LOOKS-TASK-13 aponta para o comando, e a LOOKS-TASK-18 herda
      a cobertura dele e não da prosa
- [x] `python tools/looks/looks.py --check` e `--check-image` continuam verdes
- [x] `python tools/looks/selftest.py` verde, 27 de 27 controles vermelhos
- [x] `roms/` intocada, e nada do Superpack entra no git

## Log de Execução

**Executado em:** 2026-09-15

### Resumo do que foi feito

A evidência bateu dos dois lados antes de qualquer edição: os números
reproduzem e o comando não existe. O `grep` por `jpg|parsed:|refused:` em
`tools/looks/*.py` só acha a palavra `refused:` dentro do texto de um controle
sobre outra coisa.

O conserto é o script descartável virando comando, com código de saída:

```text
$ python tools/looks/looks.py --corpus "<pasta dos 50 JPGs>"
the corpus of renders: <pasta>
   refused: 0.jpg -- '0' has 1 part(s) and a tuple has 5: skin_colour, ...
50 .jpg   parsed: 49   refused: 1   round-trip to its own name: 49
   skin_colour    4 of  4 value(s) covered
   hair_style     9 of 32 value(s) covered
   hair_colour    4 of  8 value(s) covered
   beard_style    6 of  8 value(s) covered
   beard_colour   2 of  8 value(s) covered
looks --corpus: ok
```

E sem a pasta, o contrato do perfil — **mediu e passou, ou pulou com 77**:

```text
$ python tools/looks/looks.py --corpus
looks: skipped -- no corpus folder: pass one, or point WE2002_LOOKS_CORPUS at
  the folder of renders named by tuple.  It is the third party's and is not in
  this tree
exit=77
```

A pasta vem por argumento **ou** por `WE2002_LOOKS_CORPUS`, que é o que
permite à LOOKS-TASK-19 registrá-la como alvo de `ctest` ao lado das outras.

### A recusa é o que o comando exige, e é onde a linha engana

`survey_problems()` **falha quando nada é recusado**. Um parser permissivo
imprime `50 parsed, 0 refused` — uma linha que lê **melhor** que a verdadeira —,
e é exatamente a forma de verde-pelo-motivo-errado que este ciclo já encontrou
duas vezes. O round-trip entrou na mesma conta: o Log afirmava que as 49
formatam de volta para o próprio nome e nenhuma corrida exercitava isso; agora
são 49 de 49, contadas.

Controle negativo novo, `looks-tuple-any-length`: o `parse_tuple` aceitando
qualquer número de partes. Vermelho.

O `self_check()` exercita a regra inteira com **cinco nomes sintéticos** —
quatro válidos e um inválido —, então ela roda em clone sem Superpack, que é
metade do motivo de o caso vermelho existir.

### Problemas encontrados

Nenhum. A varredura de discrepância puxou dois documentos que a lista da CORR
não previa: a tabela de gates do perfil, que lista cada comando e não tinha
linha para este, e a §5.4 do plano, que descreve o corpus sem dizer com o que
se mede. Reconciliados em commit próprio.

### Arquivos criados/modificados

- `tools/looks/looks.py` — `survey_tuples()`, `say_survey()`,
  `survey_problems()`, `corpus_names()`, o `--corpus` e o caso vermelho no
  `self_check()`
- `tools/looks/layout.py` — `ENV_CORPUS`
- `tools/looks/controls.py` — o controle `looks-tuple-any-length`
- `docs/tasks/looks/13-campos-e-dominios-de-looks.md` — o critério aponta para
  o comando
- `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md` — herda a cobertura do
  comando, com o aviso de rodar em vez de copiar
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-027.md` — este arquivo
