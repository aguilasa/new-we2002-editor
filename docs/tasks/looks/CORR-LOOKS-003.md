---
id: CORR-LOOKS-003
title: "Correção: `superpack_count.py` descarta entrada ilegível em silêncio"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-LOOKS-003: `superpack_count.py` descarta entrada ilegível em silêncio

## Problema identificado

`tools/looks/superpack_count.py` é a ferramenta que produz o número que o
`NOTICE.md` guarda como registro legal do tamanho da coletânea. Ela **emite
parcial sem dizer**, em três lugares:

```python
        try:
            total += os.path.getsize(path)
        except OSError:
            continue          # arquivo ilegivel some da conta, sem contagem
```

```python
        else:
            try:
                rows.append((entry, 1, os.path.getsize(path)))
            except OSError:
                pass          # entrada de topo some da repartição inteira
```

E a terceira, que é a pior porque não tem `try` nenhum: `os.walk(root,
followlinks=False)` roda com `onerror=None`, que é o **default de engolir**
erro de diretório. Uma subpasta sem permissão de leitura desaparece com toda a
sua subárvore, e a saída sai formatada, somada e com aparência de completa.

A pergunta que o `02-revisar.md` faz de toda ferramenta — *"ela falha alto no
que não reconhece, ou emite parcial? Saída truncada que 'parece completa' é o
furo mais caro de achar"* — se responde aqui com "emite parcial". O contrato
do perfil deste ciclo é o mesmo, uma linha acima: **mediu e passou, ou pulou
alto.**

O docstring diz *"unreadable entries are skipped, so the count is of what this
machine can actually see"*, o que **documenta** o comportamento mas não o
salva: quem lê a saída não lê o docstring, e a saída não distingue "31.790" de
"31.790 dos que deu para ver".

O `self_check()` não alcança nada disso — os quatro arquivos que ele planta são
todos legíveis, e o caso vermelho dele é sobre a repartição não somar, não
sobre entrada perdida.

## Evidência

A medição desta revisão reproduziu a da task byte a byte (31.790 arquivos,
4.830.420.054 B), então **hoje o número está certo** — o achado é sobre a
garantia, não sobre o valor. O buraco se demonstra em três linhas:

```
$ python -c "import os; \
print([n for _,_,ns in os.walk('C:/nao/existe') for n in ns])"
[]
```

`os.walk` sobre uma raiz que não pode ser lida devolve zero entrada e **nenhum
erro** — que é exatamente o que uma subpasta protegida faz dentro de uma
varredura maior, com a diferença de que ali o total sai grande e plausível.

## Causa raiz

Os três caminhos de erro tratam "não deu para ler" como "não existe", e a
ferramenta não tem por onde reportar a diferença.

## Correção

### Arquivo: `tools/looks/superpack_count.py`

1. `walk_count()` passa a devolver também a contagem de entradas puladas, e
   `os.walk` recebe `onerror=` que registre (nunca `pass`) o erro de diretório.
2. `breakdown()` propaga o mesmo, e entrada de topo ilegível vira linha com
   marca, não sumiço.
3. `main()` imprime `skipped: N` **e sai com código diferente de zero** quando
   `N > 0`. Número que vai para o `NOTICE.md` não pode sair de corrida
   incompleta e verde.
4. `self_check()` ganha o caso vermelho correspondente: uma raiz inexistente
   dentro da árvore de teste — ou um `os.walk` com `onerror` forçado — tem de
   ser **contada como pulo**, e o `assert` exige `skipped == 1`. Sem esse caso,
   o conserto vira prosa.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/superpack_count.py` | modificar |

## Verificação

- [x] `python tools/looks/superpack_count.py --check` verde, com o caso de pulo
      dentro dele
- [x] a mesma chamada duas vezes dá bytes iguais (`cmp` das duas saídas)
- [x] `python tools/looks/superpack_count.py "C:/games/we2002/Superpackv6"`
      continua imprimindo 31.790 / 4.830.420.054 B, agora com `skipped: 0`
- [x] rodar contra uma pasta com subpasta ilegível sai com código != 0
- [x] nenhum endereço de disco e nada em português no módulo (§3.5 do plano)
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-14

**Resumo do que foi feito:**

Os três caminhos de erro passaram a **contar** em vez de descartar, e a
ferramenta passou a dizer o que não viu:

1. `walk_count()` devolve `(arquivos, bytes, pulados)` e recebe
   `onerror=` — o default `None` do `os.walk` era o buraco sem `try`, o que
   fazia uma subpasta protegida sumir com a subárvore inteira.
2. `breakdown()` devolve `(entrada, arquivos, bytes, pulados)` e **mantém a
   linha** da entrada ilegível, com `0 files 0 B  skipped 1`, em vez de omiti-la
   de uma listagem que se apresenta como exaustiva. O `os.listdir` da raiz
   também ganhou `try`.
3. `main()` imprime `skipped: N` sempre, e **sai 1** quando `N > 0`, com uma
   linha em stderr dizendo que os totais são piso e não podem ser citados.
   Número que vai para o `NOTICE.md` não sai mais de corrida incompleta e verde.
4. `self_check()` ganhou o caso vermelho da CORR, mais a asserção de soma dos
   pulos por linha.

O caso vermelho é uma **raiz ilegível**, que é a forma que a subpasta protegida
toma dentro de uma varredura maior, e é portátil (nada de `chmod`, que não vale
no Windows): `walk_count(<inexistente>)` tem de dar `(0, 0, 1)` e anunciar em
stderr — antes dava `(0, 0)` sem uma palavra. O stderr do caso é capturado por
`redirect_stderr` para o `--check` continuar imprimindo os mesmos bytes em toda
corrida, já que a mensagem traz o caminho do temporário.

Uma decisão de desenho que o conserto exigiu: o `main()` varre a árvore
**duas vezes** de propósito — uma por entrada de topo, uma inteira —, e é esse
par que faz as linhas e o `TOTAL` serem conferência aritmética um do outro. As
duas varreduras topam com a mesma entrada ilegível, e as duas **contam**, porque
o total de cada uma está curto por ela; o **nome** é impresso uma vez só, porque
quem lê está sendo avisado de uma entrada, não de uma travessia. O
`self_check()` exige isso (`noise.count("skipped (") == 1`).

Verificações, nesta máquina:

```
$ python tools/looks/superpack_count.py --check
superpack_count: self_check ok                       (exit 0; stderr vazio)

$ python tools/looks/superpack_count.py "C:/games/we2002/Superpackv6"
...
TOTAL                           31790 files     4830420054 B  (4.50 GiB)
skipped: 0                                           (exit 0)
```

Duas corridas seguidas de cada uma dão bytes iguais em stdout **e** em stderr
(`cmp` das quatro saídas). E o caso vermelho de verdade, com uma pasta negada
por `icacls /deny` no scratchpad da sessão:

```
skipped (Access is denied): ...\denytest\locked
incomplete: 1 entry could not be read, so the totals above are a lower bound
locked                              0 files              0 B  skipped 1
ok                                  1 files             10 B
--------------------------------------------------------------
TOTAL                               1 files             10 B  (0.00 GiB)
skipped: 1                                           (exit 1)
```

Antes do conserto a **mesma** árvore saía como `locked 1 files 999 B` /
`TOTAL 2 files 1009 B`, exit 0 — medido na mesma sessão, com a negação ainda
não aplicada. Era exatamente o sintoma: somado, formatado e com cara de
completo.

Módulo conferido contra a §3.5 do plano: sem acento e sem endereço de disco.
A pasta de teste foi removida e a ACE de negação desfeita.

**Problemas encontrados:**

A saída da ferramenta ganhou a linha `skipped: 0`, que a transcrição do Log da
[`LOOKS-TASK-01`](/docs/tasks/looks/01-base-legal-e-linhagem.md) não tem. A
transcrição **fica como está**: é registro fiel da corrida que a produziu.
Nenhum documento afirma o contrato de código de saída da ferramenta, então não
houve o que reconciliar além disso.

**Arquivos criados/modificados:**

- `tools/looks/superpack_count.py` — `_note()` novo, `walk_count()`,
  `breakdown()`, `self_check()` e `main()`
- `docs/tasks/looks/CORR-LOOKS-003.md` — este Log
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
