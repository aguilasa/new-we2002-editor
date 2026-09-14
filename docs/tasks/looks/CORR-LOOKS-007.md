---
id: CORR-LOOKS-007
title: "Correção: o `layout.py` diz que não faz I/O, e faz"
type: correção
category: processo
status: pendente
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

- [ ] nenhuma frase do módulo afirma propriedade que o arquivo não tem hoje
- [ ] `python tools/looks/layout.py --check` verde
- [ ] a linha da 03 sobre o `_check_discs()` manda tirar a ressalva junto com a
      função
- [ ] `python tools/check_tasks.py` verde

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
