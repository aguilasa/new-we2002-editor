---
id: CORR-LOOKS-027
title: "Correção: o cross-check contra os 50 JPGs é critério marcado e não existe comando que o rode"
type: correção
category: verificação
status: pendente
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

- [ ] `python tools/looks/looks.py --corpus <pasta>` imprime 50 / 49 / 1 e o
      round-trip, e a cobertura por campo
- [ ] sem a pasta, o mesmo comando **pula com 77** e diz o que falta
- [ ] o `self_check()` exercita a regra com nomes sintéticos, recusa incluída
- [ ] o critério da LOOKS-TASK-13 aponta para o comando, e a LOOKS-TASK-18 herda
      a cobertura dele e não da prosa
- [ ] `python tools/looks/looks.py --check` e `--check-image` continuam verdes
- [ ] `python tools/looks/selftest.py` verde, com todos os controles vermelhos
- [ ] `roms/` intocada, e nada do Superpack entra no git

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
