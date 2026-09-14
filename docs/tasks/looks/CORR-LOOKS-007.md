---
id: CORR-LOOKS-007
title: "Correção: o `layout.py` diz que não faz I/O, e faz"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-LOOKS-007: o `layout.py` diz que não faz I/O, e faz

## Problema identificado

O docstring de topo do `tools/looks/layout.py` afirma sem ressalva:

```
It knows no file format and imports no Qt.  It also does no I/O -- callers
hand it bytes or digests and it answers questions about them, which is what
lets its self_check() run on a machine with no disc image at all.
```

Cento e cinquenta linhas abaixo, no mesmo arquivo, o `_check_discs()` abre duas
imagens de CD e lê quatro arquivos de dentro de cada uma:

```python
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pes2"))
    import iso
    ...
    with iso.Image(japanese) as image:
        for path in paths:
            require(path, image.read_file(path), japanese)
```

A metade que **importa** — o `self_check()` roda sem imagem — continua
verdadeira, e o desvio é conhecido: o docstring do `_check_discs()` diz que é
temporário, e a
[`LOOKS-TASK-03`](/docs/tasks/looks/03-fonte-de-disco-e-layout.md) tem por
critério movê-lo para trás do `iso_source.py`. **O que está errado é só o
docstring de topo, que afirma como propriedade do arquivo hoje algo que é
propriedade do arquivo depois da 03.**

Vale consertar porque é o cabeçalho do módulo que a regra 1 do plano
singulariza, e porque ele é a primeira coisa que quem executar a 03 vai ler —
já contendo a afirmação de que o trabalho dela está feito.

## Evidência

```
$ grep -n "does no I/O" tools/looks/layout.py
7:bytes or digests and it answers questions about them, which is what lets its

$ grep -n "iso.Image\|import iso" tools/looks/layout.py
205:    import iso  # noqa: E402  (deliberately late -- see the docstring)
216:    with iso.Image(japanese) as image:
223:    with iso.Image(english) as image:
```

Mesmo arquivo, as duas coisas.

## Causa raiz

O docstring descreve o contrato pretendido do módulo e não o estado dele
enquanto a dívida da `_check_discs()` não é paga.

## Correção

### Arquivo: `tools/looks/layout.py`

Uma frase no docstring de topo, com a data e o destino da dívida: o módulo não
faz I/O **exceto** o `--check-discs`, que é a demonstração viva contra os dois
discos reais e passa para trás do `iso_source.py` na LOOKS-TASK-03. O que
sustenta o `self_check()` sem imagem continua dito como está.

Quando a 03 mover a função, a ressalva sai junto — e aí o docstring volta a
ser verdadeiro por inteiro. Vale acrescentar isso à linha que a 03 já tem sobre
o `_check_discs()`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/layout.py` | modificar |
| `docs/tasks/looks/03-fonte-de-disco-e-layout.md` | modificar |

## Verificação

- [x] nenhuma frase do módulo afirma propriedade que o arquivo não tem hoje
- [x] `python tools/looks/layout.py --check` verde
- [x] a linha da 03 sobre o `_check_discs()` manda tirar a ressalva junto com a
      função
- [x] `python tools/check_tasks.py` verde

## Log de Execução

**Executado em:** 2026-09-14

**Resumo do que foi feito:**

O docstring de topo do `layout.py` parou de afirmar o que o arquivo ainda não
é. A frase *"It also does no I/O"* saiu de onde estava — junto com as
propriedades que valem hoje, e que continuam ditas como estavam — e virou
parágrafo próprio, com a exceção **datada** e o destino dela:

```
It does no I/O with one exception, and the exception is dated.  `--check-discs`
opens both real discs, because a guard nobody has watched go red on the real
thing is a guard nobody has tested; it arrived with LOOKS-TASK-02 on 2026-09-14
and it is LOOKS-TASK-03's debt to clear.  When the `iso_source.py` facade
exists, _check_discs() moves behind it and this paragraph goes with it, leaving
the no-I/O claim true of the whole file.
```

A metade que importa ficou intacta: o `self_check()` roda numa máquina sem
imagem, e é isso que o parágrafo de cima continua dizendo.

E a dívida ganhou a outra ponta: o item de critério da
[`LOOKS-TASK-03`](/docs/tasks/looks/03-fonte-de-disco-e-layout.md) que manda
tirar o I/O agora manda **tirar a ressalva junto com a função**. Sem isso o
conserto se pagaria com uma ressalva permanente, que é outra forma do mesmo
defeito.

```
$ python tools/looks/layout.py --check
layout: self_check ok
$ python tools/check_tasks.py
check_tasks: 123 task(s), ok
```

**Problemas encontrados:**

A varredura por "sem I/O" / "no I/O" achou mais três menções, e as três estão
**certas** como estão: as duas da 03 e a do Log da LOOKS-TASK-02 falam do
contrato **depois** da 03 (*"deixando o `layout.py` sem I/O"*), que é
exatamente a distinção que esta CORR abriu. Nenhuma delas afirma propriedade de
hoje.

**Arquivos criados/modificados:**

- `tools/looks/layout.py` — o docstring de topo
- `docs/tasks/looks/03-fonte-de-disco-e-layout.md` — o item do `_check_discs()`
- `docs/tasks/looks/CORR-LOOKS-007.md` — este Log
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
