---
id: CORR-WTE-129
title: "Correção: o Log da PAR-TASK-04 põe o CMD_SKILLS1 em dlu (392,36); o controle está em (382,32)"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-WTE-129: a coordenada que o Log deixou para quem retomar está errada

## Problema identificado

O Log da [PAR-TASK-04](/docs/tasks/PAR-TASK-04.md), na seção "O que se aprendeu,
e vale para quem retomar" — a que existe justamente para poupar a próxima
pessoa —, diz:

> `CMD_SKILLS1` fica em dlu **(392,36)** no `MainDialog` e `Escape` fecha o
> diálogo.

O controle está em **(382,32)**. O número certo aparece nos outros dois lugares
que a mesma task escreveu — a §8.4 do
[/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) e o
`tools/par/8.4-prelude.sh` —, então o Log é o único fora de passo.

Não quebra nada hoje: o roteiro versionado é quem clica, e ele usa o valor
certo. Quebra quem **ler o Log** para escrever o roteiro seguinte, que é
exatamente o público da seção. Em px o erro são 15 para a direita e 6 para
baixo, sobre um botão de 30×14 px — cai fora dele.

## Evidência

Os três sítios, lado a lado:

```text
$ grep -n '392,36\|382,32' docs/tasks/PAR-TASK-04.md docs/PARIDADE-FUNCIONAL.md \
      tools/par/8.4-prelude.sh
docs/tasks/PAR-TASK-04.md:  `CMD_SKILLS1` fica em dlu (392,36) no `MainDialog`
docs/PARIDADE-FUNCIONAL.md: `CMD_SKILLS1` fica em dlu (382,32) e `Escape` fecha.
tools/par/8.4-prelude.sh:47:# CMD_SKILLS1 (382,32,20,9) abre o diálogo do 1º jogador.
```

E a fonte, que é gerada do `ed.rc`:

```text
$ python3 -c "import json;d=json.load(open('src/app/ui/controls.json'));
  print([ (c['object'],c['dlu'],c['px']) for c in d['dialogs']['MainDialog']['controls']
          if c['object']=='CMD_SKILLS1' ])"
[('CMD_SKILLS1', [382, 32, 20, 9], [573, 52, 30, 14])]
```

`382,32,20,9` em DLU, `573,52,30,14` em px.

## Causa raiz

Transcrição errada ao redigir o Log; os dois artefatos que a task produziu no
mesmo dia carregam o valor certo.

## Correção

### Arquivo: `docs/tasks/PAR-TASK-04.md`

Trocar `(392,36)` por `(382,32)` na frase do Log. Vale acrescentar de onde ele
sai — `src/app/ui/controls.json`, gerado do `ed.rc` —, que é o que impede a
próxima transcrição de errar de novo.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/PAR-TASK-04.md` | modificar |

## Verificação

- [ ] `grep -rn '392,36' docs/` não devolve nada
- [ ] O Log, a §8.4 e o `8.4-prelude.sh` dizem os mesmos `382,32`
- [ ] `python3 tools/check_tasks.py` continua `ok`

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
