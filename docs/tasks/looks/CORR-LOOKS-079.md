---
id: CORR-LOOKS-079
title: "A seta esquerda está em x 384 em nove linhas, não oito"
origin: LOOKS-TASK-38
severity: low
files: [docs/tasks/looks/38-o-alinhamento-dos-valores.md, docs/PLAN-LOOKS-PY.md, docs/tasks/looks/36-os-sprites-estaticos.md]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-22
done_commit: 8d920cde
---

# CORR-LOOKS-079 — A seta esquerda está em x 384 em nove linhas, não oito

Origin: [LOOKS-TASK-38](/docs/tasks/looks/38-o-alinhamento-dos-valores.md)

## Problema identificado

As Notas da LOOKS-TASK-38 e o plano dizem que a `◀` fica em "384 nas outras
**oito**" linhas. Contadas no `screen.json`, são **nove** as linhas que a têm em
384 — o `DEFAUL` incluído, desde que a
[CORR-LOOKS-067](/docs/tasks/looks/CORR-LOOKS-067.md) lhe deu seta de valor.

## Evidência

```text
$ python -c "import json;d=json.load(open('tools/looks/screen.json'));from collections import Counter;\
c=Counter(a['point'][0] for r in d['rows'].values() for v in r['arrows'].values() if v for a in v if a['side']=='left');print(c)"
Counter({384: 9, 424: 1, 416: 1, 302: 1})

$ python -c "import json;print(json.load(open('tools/looks/screen.json'))['rows']['DEFAUL']['arrows']['arrival'])"
[{'point': [384, 43], 'side': 'left'}]
```

## Causa raiz

Herdado da [LOOKS-TASK-36](/docs/tasks/looks/36-os-sprites-estaticos.md), que
listou as oito linhas pelo nome antes de se saber que o `DEFAUL` tinha setas;
nunca revisto depois da CORR-LOOKS-067. A nota irmã do cursor ("396 nas outras
nove") está certa, e é o que torna a divergência visível.

## Correção

Dizer "nove" nos dois lugares. Sem mudança de código.

## Arquivos

- docs/tasks/looks/38-o-alinhamento-dos-valores.md (linha 58)
- docs/PLAN-LOOKS-PY.md (linha 3177)
- docs/tasks/looks/36-os-sprites-estaticos.md (linha 147, a lista de oito)

## Verificação

O comando `Counter` acima e a prosa concordam em nove.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `edb4dbfa`: **reproduzida**.

```text
$ python -c "... Counter(a['point'][0] ...)"
Counter({384: 20, 424: 3, 416: 2, 302: 2})   # o screen.json de 19bcdf0a guarda uma entrada por chave de valor
# por LINHA distinta: AGE 424, FOOT 416, NAT 302; BODY, BOOTS, DEFAUL, FACE, H.COL, H.F.COL., HAIR, HEIG, SKIN em 384 -> nove
$ python -c "... ['rows']['DEFAUL']['arrows']['arrival']"
[{'point': [384, 43], 'side': 'left'}]
# a prosa ainda diz "oito": 38-...:58, PLAN-LOOKS-PY.md:3177, 36-...:147
```

**Executado em:** 2026-09-22

### A recontagem, de novo

O `Counter` cru da Evidência conta **entradas**, não linhas: o `screen.json`
de `19bcdf0a` guarda uma entrada de seta por chave de valor (chegada, pontas,
entre), e por isso ele agora soma 20 em 384. A conta que a prosa faz é **por
linha distinta**, e dá nove:

```text
$ python -c "
import json
from collections import Counter
d=json.load(open('tools/looks/screen.json'))
c=Counter(a['point'][0] for r in d['rows'].values() for v in r['arrows'].values() if v for a in v if a['side']=='left')
print('raw Counter:', c)
rows={}
for name,r in d['rows'].items():
    xs={a['point'][0] for v in r['arrows'].values() if v for a in v if a['side']=='left'}
    if xs: rows[name]=sorted(xs)
bycol=Counter()
for name,xs in rows.items():
    for x in xs: bycol[x]+=1
print('by distinct row:', dict(sorted(bycol.items())))
print('rows at 384:', sorted(n for n,xs in rows.items() if xs==[384]))
"
raw Counter: Counter({384: 20, 424: 3, 416: 2, 302: 2})
by distinct row: {302: 1, 384: 9, 416: 1, 424: 1}
rows at 384: ['BODY', 'BOOTS', 'DEFAUL', 'FACE', 'H.COL', 'H.F.COL.', 'HAIR', 'HEIG', 'SKIN']
```

Nenhuma linha tem o ◀ em dois x diferentes, então a lista de nove é a resposta
inteira. `NAT` em 302, `AGE` em 424 e `FOOT` em 416 fecham as doze.

### O que foi corrigido

Três frases, todas de narrativa já fechada, então cada uma **guarda o que dizia
antes**, com a data e a referência — a forma que o resto destes arquivos usa
(`docs/tasks/looks/09-nomear-as-onze-pecas.md:176`,
`docs/PLAN-LOOKS-PY.md:978`).

- **`38-o-alinhamento-dos-valores.md`** (Notas, a nota da LOOKS-TASK-36):
  *"384 nas outras oito"* → *"384 nas outras nove"*, com a linha velha
  registrada. A nota irmã do cursor, logo abaixo, já dizia "outras nove".
- **`PLAN-LOOKS-PY.md`** (§10.3, o parágrafo das setas): a frase contava
  dentro das **onze linhas de valores**, onde 3 + 8 = 11 fecha — e o `DEFAUL`,
  a décima segunda, ficava de fora da conta e aparecia só na frase seguinte.
  Trocar "oito" por "nove" ali quebraria a aritmética das onze; a frase ganhou
  o `DEFAUL` explicitamente e o total de **nove linhas em 384**.
- **`36-os-sprites-estaticos.md`** (Log de Execução, a frase depois do trecho
  do `--screen --write`): a lista de oito nomes passou a lista de nove, com o
  `DEFAUL` — que o **próprio trecho acima** já mostra com `<(384,43)`. O
  trecho não foi tocado: é transcrição.

### Verificação

A prosa dos três arquivos e a recontagem concordam em nove:

```text
$ grep -n "outras nove\|nove\*\* linhas em 384\|em nove linhas" \
    docs/tasks/looks/38-o-alinhamento-dos-valores.md docs/PLAN-LOOKS-PY.md \
    docs/tasks/looks/36-os-sprites-estaticos.md | grep -v "396 nas outras nove"
docs/tasks/looks/38-o-alinhamento-dos-valores.md:58:  em `FOOT`, 384 nas outras nove, gravado no `screen.json` pelo walk) e não
docs/PLAN-LOOKS-PY.md:2007:a 9 e a 17. As outras nove **nunca pararam aquela instrução**, então quem as
docs/PLAN-LOOKS-PY.md:3178:> `DEFAUL`, também em 384, o que faz **nove** linhas em 384 no `screen.json`.
docs/tasks/looks/36-os-sprites-estaticos.md:147:O ◀ fica em x 384 em nove linhas: SKIN, HAIR, H.COL, FACE, H.F.COL., HEIG,
```

(A linha 2007 do plano é outro "outras nove", das paradas do GTE, e não tem
relação com as setas; o `396 nas outras nove` excluído é a nota irmã do
cursor, que já estava certa.)

Sem mudança de código: o `screen.json` e o `sprites.py` sempre disseram nove.

### Varredura

`oito`/`eight` e `384` em `docs/**` e no `CLAUDE.md`. Fora dos três arquivos,
nenhuma outra afirmação viva sobre a contagem do ◀ — a armadilha 92 do
`perfil-looks.armadilhas.md` lista os x sem contar linhas (`302, 384, 416,
424`) e já diz que o `DEFAUL` mostra o ◀, então está certa e não foi tocada. O
`CLAUDE.md` não fala das setas.

### Gates

```text
$ sh <rite> check --quick --cycle looks
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```
- **Closed** — commit `8d920cde` (2026-09-22): docs(looks): the left arrow sits at x 384 in nine rows, not eight
  - Files (`git show --name-status 8d920cde`):
    - `M docs/PLAN-LOOKS-PY.md`
    - `M docs/tasks/looks/36-os-sprites-estaticos.md`
    - `M docs/tasks/looks/38-o-alinhamento-dos-valores.md`
    - `M docs/tasks/looks/CORR-LOOKS-079.md`
