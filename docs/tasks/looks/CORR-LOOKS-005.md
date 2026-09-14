---
id: CORR-LOOKS-005
title: "Correção: a guarda dos dois discos não tem quem a chame, e nada obriga a 03 a chamá-la"
type: correção
category: comportamento
status: pendente
depends_on: []
---

# CORR-LOOKS-005: a guarda dos dois discos não tem quem a chame, e nada obriga a 03 a chamá-la

## Problema identificado

A LOOKS-TASK-02 fez o que o critério pedia: `layout.require()` existe, recusa
conteúdo que não bata, tem três casos vermelhos sintéticos e foi vista ficando
vermelha contra os dois discos reais. **O que falta é o outro lado da regra —
ninguém é obrigado a passar por ela.**

Hoje o único chamador de `require()` no repositório é o `_check_discs()` do
próprio `layout.py`, que é a demonstração. Quando a LOOKS-TASK-03 escrever o
`iso_source.py`, que é a fachada por onde **toda** leitura vai passar, nada no
critério dela manda rotear a leitura pela guarda:

```
- [ ] `iso_source.py` abre a imagem por `tools/pes2/iso.py` e entrega
      `/BIN/EDT_MOD.BIN`, `/BIN/MODEL.BIN` e `/BIN/DAT2D.BIN`.
```

"Abre e entrega" é exatamente o que um leitor sem guarda faz. O item seguinte
manda tirar o I/O do `layout.py` — o que **remove** o único chamador que existe
hoje — sem pôr nenhum no lugar. Fechada a 03 ao pé da letra, o ciclo fica com
uma guarda completa, testada, e **inalcançável**: ler paleta do disco inglês
volta a não levantar nada.

É a falha que a própria task 02 nomeia, um nível acima: *"uma regra que só vive
na prosa não impede ninguém de ler paleta do disco errado"*. A regra saiu da
prosa e virou função; o **caminho de leitura** é que continua não sabendo dela.

Pelo critério deste ciclo, isso é **Alta**: *"qualquer guarda que fique verde
lendo o disco errado, porque esse erro não tem sintoma."* Uma guarda que
ninguém chama fica verde por construção.

## Evidência

Chamadores de `require()` na árvore inteira:

```
$ grep -rn "require(" tools/ --include=*.py
tools/looks/layout.py:113:def require(disc_path: str, data: bytes, ...
tools/looks/layout.py:214:                require(path, image.read_file(path), japanese)
tools/looks/layout.py:225:                require(path, image.read_file(path), english)
```

As duas chamadas estão dentro do `_check_discs()`, que a
[`LOOKS-TASK-03`](/docs/tasks/looks/03-fonte-de-disco-e-layout.md) tem por
critério **mover** — e o `iso_source.py` que herda a leitura não tem, em
critério nenhum, a obrigação de chamar a guarda.

Que a guarda funciona quando chamada, esta revisão remediu:

```
$ python tools/looks/layout.py --check
layout: self_check ok
$ python tools/looks/layout.py --check-discs roms/japanese-shift-jis.bin \
    C:/games/ps1/work/we2002-english.bin
...
  refused  /BIN/DAT2D.BIN       (wanted refused) ok
layout --check-discs: ok
```

O defeito não é a guarda. É não haver contrato que a torne inevitável.

## Causa raiz

A task plantou a recusa e não plantou a obrigação de passar por ela; o critério
da task que escreve o leitor descreve a leitura sem mencionar a guarda.

## Correção

### Arquivo: `docs/tasks/looks/03-fonte-de-disco-e-layout.md`

Acrescentar ao `## Critério de conclusão`, como item próprio:

- **Toda leitura de arquivo do disco no `iso_source.py` passa por
  `layout.require()`** — não é opção do chamador. Um arquivo cujo digest não
  bate não chega a virar bytes na mão de ninguém.
- **Caso vermelho vivo:** ler `/BIN/DAT2D.BIN` do disco **inglês** pelo
  `iso_source.py` levanta `WrongDisc`, e o teste exige isso. É o mesmo estímulo
  do `--check-discs`, agora pelo caminho que o resto do projeto usa.
- Se algum ponto legítimo precisar dos bytes sem conferência (comparar dois
  discos, por exemplo, que é o que o `--check-discs` faz), que seja uma função
  **nomeada e separada** — `read_unchecked()` ou equivalente —, para o desvio
  aparecer no `grep`.

### Arquivo: `docs/PLAN-LOOKS-PY.md` §4.5

A seção diz que a regra mora no `layout.py`. Acrescentar a outra metade: a
guarda só vale porque **o `iso_source.py` é o único caminho de leitura e chama
a guarda em todo arquivo**. Sem essa frase a §4.5 descreve uma função, não uma
garantia.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/looks/03-fonte-de-disco-e-layout.md` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |

## Verificação

- [ ] a 03 tem item de critério exigindo que a leitura passe por
      `layout.require()`, e outro exigindo o caso vermelho pelo `iso_source.py`
- [ ] a §4.5 do plano diz quem chama a guarda, e não só que ela existe
- [ ] `python tools/looks/layout.py --check` continua verde
- [ ] `python tools/check_tasks.py` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
