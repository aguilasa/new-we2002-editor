---
id: CORR-LOOKS-003
title: "Correção: `superpack_count.py` descarta entrada ilegível em silêncio"
type: correção
category: verificação
status: pendente
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

- [ ] `python tools/looks/superpack_count.py --check` verde, com o caso de pulo
      dentro dele
- [ ] a mesma chamada duas vezes dá bytes iguais (`cmp` das duas saídas)
- [ ] `python tools/looks/superpack_count.py "C:/games/we2002/Superpackv6"`
      continua imprimindo 31.790 / 4.830.420.054 B, agora com `skipped: 0`
- [ ] rodar contra uma pasta com subpasta ilegível sai com código != 0
- [ ] nenhum endereço de disco e nada em português no módulo (§3.5 do plano)
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
