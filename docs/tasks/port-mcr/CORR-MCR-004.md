---
id: CORR-MCR-004
title: "Correção: o cache do WebView2 não mora todo em `bin/`/`obj/` — um terço dele é a linha `packages/`"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-MCR-004: a atribuição do WebView2 contradiz a tabela que ela anota

## Problema identificado

O inventário do upstream, no Log da
[MCR-TASK-02](/docs/tasks/port-mcr/02-base-legal-e-linhagem.md), traz a linha:

> | `bin/` e `obj/` | 2586 | 363.366.917 | saída de build — **é aqui que mora
> todo o cache do WebView2**, 1820 arquivos e 319.637.837 B |

O par `1820 / 319.637.837` é o cache do WebView2 **da árvore inteira**, e está
certo como total. Errado é a atribuição: **164 desses arquivos, 100.938.946 B —
32% dos bytes — estão fora de `bin/`/`obj/`**, sob `packages/` e
`lite/packages/`. Como as categorias da tabela são disjuntas por construção,
esses 164 são exatamente a **outra linha** da mesma tabela (`packages/ | 164 |
100.938.946`), e a nota afirma que eles estão dentro da linha de cima.

A própria task previu esse tropeço e declarou tê-lo evitado, no
`Problemas encontrados` §2:

> **`packages/` some do inventário se o WebView2 for descontado primeiro.** …
> A tabela acima desconta na ordem prefixo → extensão, e diz explicitamente que
> o cache do WebView2 está dentro de `bin/`/`obj/`.

A ordem de desconto está certa e a tabela fecha; o que ficou errado é a frase
que ela cita como conserto.

**Segundo item, mesma tabela.** As linhas `.vs/` (20) e `packages/` (164) só
fecham se o prefixo casar em **qualquer profundidade** — no topo há 13 e 82,
respectivamente, e o resto está em `lite/.vs/` e `lite/packages/`. A legenda diz
apenas "filtrado por prefixo e extensão", e sem a profundidade a tabela não é
reproduzível: quem repetir a medição com `^packages/` acha 82 e conclui que a
nossa está errada.

## Evidência

Medido contra o SHA fixado, com a mesma classificação disjunta e na mesma ordem
da tabela:

```sh
git -C work/easy-mcr ls-tree -r -l HEAD | awk '{
  size=$4; path=""; for(i=5;i<=NF;i++) path = path (i>5?" ":"") $i;
  if (path ~ /(^|\/)(bin|obj)\// && tolower(path) ~ /webview2/) {n++; s+=size}
} END {print n, s}'
# 1656 218698891

git -C work/easy-mcr ls-tree -r -l HEAD | awk '{
  size=$4; path=""; for(i=5;i<=NF;i++) path = path (i>5?" ":"") $i;
  if (tolower(path) ~ /webview2/) {n++; s+=size}
} END {print n, s}'
# 1820 319637837
```

| onde | arquivos | bytes |
| --- | ---: | ---: |
| WebView2 dentro de `bin/`/`obj/` | 1.656 | 218.698.891 |
| WebView2 fora dele (todo o `packages/`) | **164** | **100.938.946** |
| total, que é o número afirmado | 1.820 | 319.637.837 |

A segunda linha é, byte a byte, a linha `packages/` da tabela do Log — o
`packages/` do upstream é **inteiramente** WebView2:

```sh
git -C work/easy-mcr ls-tree -r --name-only HEAD | grep -i webview2 \
  | awk -F/ '{print $1"/"$2}' | sort | uniq -c | sort -rn
#   1647 lite/fifatomcr
#     82 lite/packages
#     82 packages/Microsoft.Web.WebView2.1.0.2420.47
#      9 fifatomcr/bin
```

E a profundidade do prefixo:

| linha da tabela | só no topo | em qualquer profundidade (o que a tabela usa) |
| --- | ---: | ---: |
| `.vs/` | 13 / 1.928.312 | **20 / 3.996.160** |
| `packages/` | 82 / 50.469.473 | **164 / 100.938.946** |

O restante do inventário remede exato: 2.853 arquivos / 476.688.515 B no total;
`lite/` 2170 / 319.101.497; `fifatomcr/` 583 / 104.998.529; `packages/` 82 /
50.469.473; `.vs/` 13 / 1.928.312; raiz 5 / 190.704; `bin`+`obj` 2586 /
363.366.917; `BD.accdb` 1 / 2.543.616; `.bmp` 6 / 996.032; `.png` 2 / 92.204;
`.pfx` 2 / 3.304; soma excluída 2.781 / 471.937.179; resto 72 / 4.751.336.

## Causa raiz

A frase foi escrita para explicar por que `packages/` não sumia de vez ao
descontar o WebView2, e acabou afirmando o inverso do que a ordem de desconto
faz: o WebView2 **atravessa** as duas linhas, e por isso não pode ser atribuído
a nenhuma delas.

## Correção

### Arquivo: `docs/tasks/port-mcr/02-base-legal-e-linhagem.md`

Na tabela "O que não entra, e por quê", trocar a célula de razão da linha
`bin/` e `obj/`:

```markdown
| `bin/` e `obj/` | 2586 | 363.366.917 | saída de build — inclui **1.656
arquivos e 218.698.891 B** do cache do WebView2, que é a maior parte dele mas
não o todo |
```

e acrescentar, na legenda logo acima da tabela, a profundidade do prefixo e o
atravessamento:

```markdown
Categorias disjuntas, na ordem em que foram descontadas
(`git ls-tree -r -l HEAD` filtrado por prefixo e extensão; **o prefixo casa em
qualquer profundidade** — `.vs/` e `packages/` também aparecem sob `lite/`, e é
por isso que somam 20 e 164 contra os 13 e 82 do topo). O cache do WebView2
**atravessa duas linhas** e por isso não é linha: são 1.820 arquivos e
319.637.837 B ao todo, 1.656 / 218.698.891 sob `bin/`+`obj/` e os outros 164 /
100.938.946 sob `packages/`, que é inteiramente ele.
```

No `Problemas encontrados` §2, a última oração passa a dizer o que a tabela de
fato faz — que o WebView2 atravessa `bin/obj` e `packages/`, e por isso foi
descontado por prefixo em vez de por nome.

`NOTICE.md` **não precisa de conserto**: lá o WebView2 aparece numa lista de
naturezas, sem atribuição a diretório, e os totais (2.781 / 471.937.179) estão
certos.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/port-mcr/02-base-legal-e-linhagem.md` | modificar |

## Verificação

- [ ] os dois `awk` da seção Evidência devolvem `1656 218698891` e
      `1820 319637837`, e o doc cita os dois pares
- [ ] a legenda da tabela diz que o prefixo casa em qualquer profundidade
- [ ] as somas da tabela continuam fechando: 2.781 + 72 = 2.853 e
      471.937.179 + 4.751.336 = 476.688.515
- [ ] `python3 tools/check_tasks.py` verde e `ctest -R tasks` verde
- [ ] `work/easy-mcr/` e `roms/` intocados; `git status --short` sem nada de
      `work/`

## Log de Execução

**Executado em:** 2026-09-07

**Resumo do que foi feito:**

A célula de razão de `bin/`+`obj/` passou a trazer os números medidos —
**1.656 arquivos e 218.698.891 B** do cache do WebView2 —, e a legenda da tabela
ganhou as duas coisas que faltavam: que o prefixo casa em **qualquer
profundidade** (o que explica 20 contra 13 e 164 contra 82) e que o WebView2
**atravessa** duas linhas, com a repartição 1.656/218.698.891 sob `bin/`+`obj/`
e 164/100.938.946 sob `packages/`. O `Problemas encontrados` §2 deixou de citar
a frase errada e passou a dizer o que a ordem de desconto de fato implica.

Os dois `awk` da Evidência remedem exato: `1656 218698891` e
`1820 319637837`. As profundidades também: `.vs/` 13→20, `packages/` 82→164.

**Problemas encontrados:**

Uma discrepância que o conserto revelou, na mesma tabela: a célula de
`packages/` dizia "NuGet restaurado, **inclusive** o WebView2", o que ficou mais
fraco que a legenda logo acima, que agora afirma que aquela linha é
inteiramente ele. Trocado por "é **inteiramente** o WebView2".

`NOTICE.md` conferido e intocado, como a CORR previu: lá o WebView2 aparece
numa lista de naturezas, sem atribuição a diretório.

**Arquivos criados/modificados:**

- `docs/tasks/port-mcr/02-base-legal-e-linhagem.md` — legenda da tabela, as
  células de `bin/`+`obj/` e de `packages/`, e o `Problemas encontrados` §2
