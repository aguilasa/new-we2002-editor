---
id: CORR-LOOKS-059
title: "Correção: o plano diz que o `derive_base()` responde `0x8017EE60` para o `ANIME.BIN`, e ele recusa o arquivo"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-LOOKS-059: a base errada não é o que a regra responde, é o que sobra dela

## Problema identificado

O veredito da §10.3 (j), escrito pela
[`LOOKS-TASK-24`](/docs/tasks/looks/24-de-onde-vem-a-pose.md), diz por que a
base do `ANIME.BIN` foi medida por conteúdo e não derivada:

```text
docs/PLAN-LOOKS-PY.md §10.3 (j)
> ... a corrida de ponteiros é reconhecida por "bit alto", e o payload deste
> arquivo abre com `0x9000040A`; e o ponteiro mais baixo mira o offset 912,
> não o 816 que a regra supõe. Ele responde `0x8017EE60`, 96 bytes alto, e
> contra essa base **279.034 bytes diferem** — é o controle vermelho deste
> comando.
```

**Ele não responde `0x8017EE60`: ele recusa o arquivo.** As duas razões citadas
são sequenciais, não paralelas — a primeira faz a função levantar `WrongBase`
antes de chegar à segunda, e o `0x8017EE60` só existe na hipótese de a corrida
ser cortada em 204 palavras.

O `layout.ANIME_BASE` conta isso certo (*"even with the run cut at 204 words …
the base it computes is 0x8017EE60"*); o plano, que é a fonte de verdade da
incógnita, e o Log da task (*"erra este arquivo por 96 bytes"*) descrevem uma
resposta que ninguém obtém. Quem for conferir chama a função, recebe uma
exceção e não sabe se o plano está velho ou se a árvore quebrou.

## Evidência

Na árvore de `8a32160`, com a imagem japonesa apontada:

```text
$ python -c "... layout.derive_base(iso_source.read_file(img, layout.ANIME))"
layout.WrongBase: base 0x8017ee2c puts header pointer 204 (0x9000040a) at
266868190, outside the file's 396804 bytes
```

E o resto do veredito reproduz, o que localiza o erro nesta frase e em nenhuma
outra:

```text
$ python tools/looks/oracle.py --pose            # arvore de 8a32160
  /BIN/ANIME.BIN at 0x8017ee00: 396804 of 396804 byte(s) equal   (nos dois slots)
oracle --pose: 0 problem(s)

$ python <copia com ANIME_BASE = 0x8017EE60>/tools/looks/oracle.py --pose 2
  /BIN/ANIME.BIN at 0x8017ee60: 117770 of 396804 byte(s) equal
  FAIL  slot 2: 279034 of 396804 bytes of /BIN/ANIME.BIN differ at 0x8017ee60
  FAIL  slot 2: none of the 204 header entries of /BIN/ANIME.BIN was read
oracle --pose: 2 problem(s)
```

A base plantada do controle é escrita à mão na cópia — não sai da função.

## Causa raiz

A frase resume duas razões independentes numa resposta só, e a segunda só vale
depois de a primeira ser contornada à mão.

## Correção

### Arquivo: `docs/PLAN-LOOKS-PY.md` (§10.3 (j)), `docs/prompts/perfil-looks.md` (armadilha 44) e `docs/tasks/looks/24-de-onde-vem-a-pose.md`

Dizer o que acontece: o `derive_base()` **recusa** o `ANIME.BIN` com
`WrongBase`, porque lê o `0x9000040A` do payload como ponteiro; e **cortada a
corrida em 204 palavras**, a regra ainda erra — daria `0x8017EE60`, 96 bytes
alto, que é a base plantada no controle vermelho. É o que o `ANIME_BASE` já
diz, com as duas metades separadas.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `docs/prompts/perfil-looks.md` | modificar (a armadilha 44 diz a mesma coisa) |
| `docs/tasks/looks/24-de-onde-vem-a-pose.md` | modificar |

## Verificação

- [x] chamar `layout.derive_base()` sobre o `ANIME.BIN` e conferir que o texto
      do plano descreve o que se vê
- [x] o `0x8017EE60` continua explicado como a base do controle, com a
      condição que a produz
- [x] `python tools/check_tasks.py` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-18

### Resumo do que foi feito

A evidência reproduz em `cf98bb9`: chamado sobre o `ANIME.BIN`, o
`derive_base()` **recusa o arquivo** — não responde base nenhuma.

```text
$ python -c "... layout.derive_base(iso_source.read_file(img, layout.ANIME))"
WrongBase: base 0x8017ee2c puts header pointer 204 (0x9000040a) at 266868190,
outside the file's 396804 bytes
```

As três frases passaram a contar as duas razões **em sequência**, que é como
elas acontecem:

1. a corrida de ponteiros é reconhecida por "bit alto", o payload abre com
   `0x9000040A`, a corrida não para no fim do cabeçalho e a função **levanta
   `WrongBase`** — é o que se vê ao chamá-la;
2. **cortada a corrida em 204 palavras**, a segunda metade da regra ainda erra
   (o ponteiro mais baixo mira o offset 912, não o 816) e daí sairia
   `0x8017EE60`, 96 bytes alto — a base **escrita à mão** na cópia da árvore
   que dá o controle vermelho: 279.034 de 396.804 bytes diferentes e nenhuma
   das 204 entradas lida.

- §10.3 (j) do plano: o item 1 virou os dois marcadores acima, com a data e o
  que a frase dizia antes;
- perfil, armadilha 44: "erra por 96 bytes" era o que a regra **faria** se
  chegasse lá; o que ela faz é recusar;
- LOOKS-TASK-24: o bloco do vermelho passou a dizer que a base é escrita à mão,
  com a condição que a produziria.

**Uma discrepância que o conserto revelou, e que a CORR não listava:** o
docstring do `layout.ANIME_BASE` contava as duas razões certas — é dele que a
CORR tira a separação —, mas fechava com *"every byte compared against it
differs"*, e o medido é **279.034 de 396.804** (117.770 batem). Corrigido junto,
por ser a mesma afirmação a uma linha de distância.

### Gates

```text
$ python -c "... layout.derive_base(...)"     # depois, o texto do plano bate
WrongBase: base 0x8017ee2c puts header pointer 204 (0x9000040a) at 266868190,
outside the file's 396804 bytes

$ python tools/looks/layout.py --check
layout: self_check ok
$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
$ python tools/looks/selftest.py --quiet
  ..... 75 of 75 controls red
looks_selftest: 0 failure(s)
```

O `0x8017EE60` continua explicado nos quatro lugares, sempre com a condição que
o produz. `roms/` intocada (leitura pura); nenhum emulador subiu nesta correção.

### Problemas encontrados

Nenhum.

### Arquivos criados/modificados

- `docs/PLAN-LOOKS-PY.md` §10.3 (j)
- `docs/prompts/perfil-looks.md` — armadilha 44
- `docs/tasks/looks/24-de-onde-vem-a-pose.md` — o bloco do controle vermelho
- `tools/looks/layout.py` — o fecho do docstring do `ANIME_BASE`
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
