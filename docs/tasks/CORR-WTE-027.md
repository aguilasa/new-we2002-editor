---
id: CORR-WTE-027
title: "Correção: o `fase-2.md` emite link `/docs/...` de dentro de `wte/re/`, fora do perímetro da regra"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-WTE-027: seis links do `fase-2.md` usam a forma que a regra reserva a `docs/`

## Problema identificado

O [`wte/re/fase-2.md`](../../wte/re/fase-2.md), gerado pelo
`wte/tools/check_fase2.py` (WTE-TASK-14), escreve seis links para `docs/` na
forma absoluta `/docs/tasks/...`:

- linha 3 — `[WTE-TASK-14](/docs/tasks/14-fechamento-fase-2.md)`
- linhas 135-139 — as cinco entradas da tabela "Pendências que a fase 2
  entrega", apontando para as tasks 22, 25 e 37

`.claude/rules/links.md` restringe essa forma a markdown **dentro** de `docs/`
("Fora de `docs/`, a regra não vale… ali link relativo comum é o certo").
`wte/re/` está fora. Os vizinhos versionados usam `../../docs/…`, inclusive o
arquivo que o próprio `fase-2.md` toma por modelo, o `fase-1.md`.

Este erro **já foi cometido e corrigido uma vez neste projeto**, no gerador
irmão: o Log da [CORR-WTE-007](/docs/tasks/CORR-WTE-007.md) registra
"O link que escrevi no parágrafo novo saiu como `/docs/tasks/...`. Errado:
`.claude/rules/links.md` restringe essa forma a markdown **dentro** de `docs/`,
e `wte/re/published_methods.md` está fora — os vizinhos dele usam
`../../docs/tasks/`. Corrigido no gerador antes do commit."

## Evidência

```
$ grep -rnoE '\]\((/docs/[^)]*|[^)]*docs/[^)]*)\)' wte/re/*.md
wte/re/fase-1.md:3:](../../docs/tasks/09-fechamento-fase-1.md)
wte/re/fase-1.md:114:](../../docs/tasks/CORR-WTE-017.md)
wte/re/fase-1.md:188:](../../docs/tasks/CORR-WTE-012.md)
...
wte/re/fase-2.md:3:](/docs/tasks/14-fechamento-fase-2.md)
wte/re/fase-2.md:135:](/docs/tasks/22-harness-golden.md)
wte/re/fase-2.md:136:](/docs/tasks/22-harness-golden.md)
wte/re/fase-2.md:137:](/docs/tasks/22-harness-golden.md)
wte/re/fase-2.md:138:](/docs/tasks/25-handlers-de-carga.md)
wte/re/fase-2.md:139:](/docs/tasks/37-reconferencia-de-ui.md)
wte/re/offsets.md:3:](../../docs/tasks/06-mapa-de-offsets.md)
wte/re/published_methods.md:3:](../../docs/tasks/04-mapa-de-handlers.md)
wte/re/strings.md:3:](../../docs/tasks/05-inventario-de-strings.md)
```

Os dois lados da divergência, no mesmo diretório: `fase-1.md:3` usa
`../../docs/tasks/09-…`, `fase-2.md:3` usa `/docs/tasks/14-…`.

A mesma forma aparece em `wte/re/eventos.md:186,214` (WTE-TASK-13) e
`wte/re/tipos.md:10` (WTE-TASK-15), que são escritos à mão. Não são desta
correção — a origem aqui é a WTE-TASK-14 —, mas cabem na mesma passada, e a
lista existe para não obrigar a redescoberta.

## Causa raiz

O `montar()` do `check_fase2.py` foi escrito copiando a forma de link dos
markdowns de `docs/tasks/`, que é onde a forma `/docs/` vale, sem notar que a
saída dele mora em `wte/re/`.

## Correção

### Arquivo: `wte/tools/check_fase2.py`

Trocar `/docs/` por `../../docs/` nos seis links de `montar()` — linha 274 (o
`Produto da [WTE-TASK-14]`) e linhas 430-440 (a tabela de pendências). Depois,
regerar o `wte/re/fase-2.md`:

```sh
python3 wte/tools/check_fase2.py
python3 wte/tools/check_fase2.py --check
```

Opcional, na mesma passada: `wte/re/eventos.md` (linhas 186 e 214) e
`wte/re/tipos.md` (linha 10), que são escritos à mão e têm o mesmo defeito.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/check_fase2.py` | modificar |
| `wte/re/fase-2.md` | modificar (regerado) |
| `wte/re/eventos.md` | modificar (opcional, mesma passada) |
| `wte/re/tipos.md` | modificar (opcional, mesma passada) |

## Verificação

- [ ] `grep -rnoE '\]\(/docs/' wte/re/*.md` sai vazio
- [ ] `python3 wte/tools/check_fase2.py --check` verde
- [ ] `make -C wte check` verde
- [ ] a conferência de forma e de destino de link de `.claude/rules/links.md`
      continua vazia para `docs/`
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
