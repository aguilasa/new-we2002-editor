---
id: CORR-MCR-008
title: "Correção: destino faltando mata o `layout.py` no import, e o `--self-check` não chega a rodar"
type: correção
category: núcleo
status: pendente
depends_on: []
---

# CORR-MCR-008: o harness do `layout.py` morre antes de começar

## Problema identificado

Os módulo-nível `_required(...)` do `tools/mcr/layout.py` levantam `LayoutError`
**no import**. Consequência: nos dois controles negativos que tiram um destino
da tabela — apagar `0x63D5` e mover `0x5404` para `0x5405` —, o
`python3 layout.py --self-check` sai por **traceback**, e **nenhuma** das 29
asserções roda.

O caso vermelho pedido pelo critério da
[MCR-TASK-05](/docs/tasks/port-mcr/05-layout-e-cross-check.md) está atendido: o
`--check` falha e diz qual destino sumiu, com mensagem boa. O que ficou por
dizer é o **efeito colateral**, e ele é da família que a
[MCR-TASK-04](/docs/tasks/port-mcr/04-conteiner-do-cartao.md) já pagou e
registrou em letras:

> **um harness que morre no primeiro susto mede o primeiro defeito e esconde o
> resto.** Vale para as tasks 05 a 10.

A MCR-TASK-05 aplicou metade da lição: o `_required()` trocou o
`KeyError: 25557` cru por um `LayoutError` que nomeia a vista e o endereço —
mensagem muito melhor. Mas a corrida continua morrendo no import, e a tabela de
controles do Log registra o resultado como *"🔴 `LayoutError` nomeando
`FORMATION_ROLES` e o `0x63d5`"* sem dizer que, naquela corrida, o
`--self-check` reportou **zero** asserções.

**O risco real é adiante.** A
[MCR-TASK-10](/docs/tasks/port-mcr/10-selftest-cli-e-gate.md) monta o
`mcr_selftest`, que o perfil declara **obrigatório** e que roda sem fixture e
sem Qt. Se ele importar `layout` no escopo do módulo, uma tabela de endereço
quebrada derruba o gate inteiro por traceback, em vez de reportar uma falha
nomeada entre as demais — exatamente o que o `attempt()` do `card.py` existe
para impedir.

## Evidência

Controle replantado numa cópia dentro da árvore (a cópia foi apagada depois):

```
$ python3 l.py --self-check          # com a linha do destino 0x63D5 removida
Traceback (most recent call last):
  File ".../l.py", line 189, in <module>
    FORMATION_ROLES = _required(0x63D5, "FORMATION_ROLES")
  File ".../l.py", line 156, in _required
    raise LayoutError(
LayoutError: FORMATION_ROLES needs the destination 0x63d5, which is not in
DESTINATIONS. A row was removed or its address was changed; `--check` says
which side disagrees with wte/re/mcr.md.
rc=1
```

Os seis controles, replantados nesta revisão, com a contagem de falhas do
`--self-check`:

| defeito plantado | `--check` | `--self-check` |
|---|---|---|
| apagar `0x63D5` | 🔴 `LayoutError` nomeando a vista | **traceback, 0 asserções** |
| 18º destino `0x6600` no fim | 🔴 `1 problem(s)` | 🔴 3 falhas |
| `0x5404` → `0x5405` | 🔴 `LayoutError` nomeando a vista | **traceback, 0 asserções** |
| cobradores crescentes | verde (não é o papel dele) | 🔴 1 falha |
| deslocamentos `(0,1,2,3,4,5)` | verde | 🔴 1 falha |
| `PLAYER_STRIDE = 22` | verde | 🔴 3 falhas |

**6/6 vermelhos, `rc=1` nos seis** — o Log está certo no veredito. As contagens
3, 1, 1, 3 batem exatamente; só o 18º destino precisa ser **acrescentado no
fim** da lista para dar 3 (inserido no meio dá 4, porque a asserção de ordem
crescente também cai — detalhe que vale registrar para a próxima replantação).

O que a tabela do Log não diz é a coluna da direita nas linhas 1 e 3.

## Causa raiz

As vistas nomeadas são resolvidas no escopo do módulo, então um destino
faltando é erro de import — e um erro de import não tem como ser reportado
pelo harness que ele impede de carregar.

## Correção

Duas coisas pequenas; nenhuma muda o comportamento medido.

### Arquivo: `docs/tasks/port-mcr/05-layout-e-cross-check.md`

Acrescentar à tabela dos seis controles a coluna que falta, ou uma frase
abaixo dela:

```markdown
Nos dois controles que **tiram** um destino da tabela, o `LayoutError` é de
**import**: o `--self-check` sai por traceback e nenhuma das 29 asserções roda.
É o veredito certo — módulo com tabela de endereço quebrada não deve importar —,
mas quem lê a tabela precisa saber que ali o `0 failure(s)` não aparece porque
o harness não chegou a começar, e não porque estava tudo bem.
```

E registrar o detalhe da replantação: o 18º destino tem de ser acrescentado
**no fim** para reproduzir as 3 falhas; no meio da lista dá 4.

### Arquivo: `docs/tasks/port-mcr/10-selftest-cli-e-gate.md`

Uma linha no critério, ao lado das duas que a MCR-TASK-05 já deixou lá:

```markdown
- [ ] **O `selftest` importa `layout` dentro do `attempt()`**, não no escopo do
      módulo: as vistas nomeadas do `layout.py` levantam `LayoutError` no
      import quando um destino some, e o `mcr_selftest` é o gate **obrigatório**
      — uma tabela quebrada tem de virar uma falha nomeada entre as demais, não
      um traceback que derruba a corrida inteira. É a mesma lição que a
      MCR-TASK-04 pagou e que vale para as tasks 05 a 10.
```

**O `layout.py` não precisa mudar.** Falhar no import é o comportamento certo
para um módulo cuja única razão de existir é a tabela de endereços; o que falta
é o consumidor saber disso.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/port-mcr/05-layout-e-cross-check.md` | modificar |
| `docs/tasks/port-mcr/10-selftest-cli-e-gate.md` | modificar |

## Verificação

- [ ] `python3 tools/mcr/layout.py --self-check` continua **29 asserções, 0
      falhas**, e duas corridas dão bytes iguais
- [ ] `python3 tools/mcr/layout.py --check` continua `17/17`, e `--rule1`
      continua `0 address(es) outside layout.py`
- [ ] os seis controles continuam 🔴, com `--self-check` dando 3, 1, 1, 3 nos
      quatro que carregam, e traceback nomeado nos dois que não
- [ ] a tabela de controles da MCR-TASK-05 diz o que acontece com o
      `--self-check` nas linhas 1 e 3
- [ ] a MCR-TASK-10 carrega o critério do `attempt()` em volta do import
- [ ] `roms/` e `work/entrada.mcr` intocados

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
