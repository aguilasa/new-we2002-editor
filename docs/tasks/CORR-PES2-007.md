---
id: CORR-PES2-007
title: "Correção: três textos vivos ainda dizem cinco listas, e a tabela de testes do plano não conhece o `poke`"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-PES2-007: o "cinco → oito" parou antes de três textos vivos

## Problema identificado

A [PES2-TASK-02](/docs/tasks/02-poke-por-conjunto-de-copias.md) atualizou a
§1.5, a §1.6, a §1.13 e a §6.1 do plano, o `CLAUDE.md` e o `progresso.md`.
Sobraram **três** trechos que não são registro datado — são instrução viva — e
um deles descreve um teste que mudou nesta mesma task:

1. `docs/PLAN-PES2-PSX.md:1048`, a tabela do §5.1 que diz o que o `pes2_image`
   faz: *"o alinhamento das **cinco** listas de time (§6.1)"*, e **sem
   mencionar o `poke`**, que a task acrescentou ao mesmo teste.
2. `docs/PLAN-PES2-PSX.md:1140-1141`, o estado da Fase 2: *"a correspondência
   entre as **cinco** listas de nome de time está em …"*.
3. `docs/prompts/perfil-pes2.md:197`, a verificação de Fase 2 que o `/revisar`
   carrega: *"**As cinco cópias de nome de time não são a mesma lista**"* — no
   mesmo arquivo cuja armadilha nº 2 já diz oito.

O item 3 é o mais caro: é o texto pelo qual a próxima revisão de uma task de
Fase 2 vai conferir o conjunto de cópias, e ele manda conferir cinco.

## Evidência

O que o disco e as ferramentas dizem:

```
$ python3 tools/pes2/team_map.py "<track1.bin>" --check
canonical  /SELECT.BIN    106 entries
  team-names-selectc  … 99   team-names-ending  … 95   team-names-result … 94
  team-names-replays  …123   team-names-select2 … 32   team-names-select3 … 99
  team-names-selform  … 99                                   → 1 + 7 = 8 listas

$ grep -n "eight\|poke" tools/pes2/check_image.py
66:    print("\n== the eight team-name lists, aligned (plan 6.1) ==")
93:        print("\n== the poke, over the whole copy set (plan 6.1) ==")
94:        bad += poke.self_check(image, tmpdir)
```

O que os três textos dizem:

```
$ grep -n "cinco listas" docs/PLAN-PES2-PSX.md
1048:| `pes2_image` | … o alinhamento das cinco listas de time (§6.1) …
1141:  cinco listas de nome de time está em

$ sed -n '197p' docs/prompts/perfil-pes2.md
- O texto foi escrito na tabela certa? **As cinco cópias de nome de time não são
```

E, no mesmo perfil, a armadilha que já está certa:

```
$ sed -n '48,50p' docs/prompts/perfil-pes2.md
2. **"Cópia" de tabela não quer dizer mesma lista.** As oito cópias de nome de
   time têm 106, 99, 95, 94, 123, 32, 99 e 99 entradas …
```

## Causa raiz

A atualização foi feita por seção citada no Log e não por varredura do termo:
`grep -rn "cinco listas\|cinco cópias"` acha os três em um comando.

## Correção

### Arquivo: `docs/PLAN-PES2-PSX.md`

- Linha 1048: "cinco listas de time" → "oito listas de time", e a célula do
  `pes2_image` passa a citar também **o `poke` da §6.1** entre o que o teste
  faz com `_TMPDIR` — hoje ela só menciona o controle negativo, e o teste roda
  os dois.
- Linha 1140-1141: "cinco listas de nome de time" → "oito", com o ponteiro para
  a §6.1, que já traz a tabela das oito.

### Arquivo: `docs/prompts/perfil-pes2.md`

- Linha 197: "As cinco cópias" → "As oito cópias", alinhando a verificação de
  Fase 2 com a armadilha nº 2 do mesmo arquivo.

### O que **não** se toca

`docs/PES2-AJUSTES.md` continua dizendo "onze tabelas" e "as cinco listas": é
o registro datado da revisão de 2026-08-30, e reescrevê-lo falsificaria o que
se media naquele dia. Mesma razão pela qual a linha 51 do perfil
(*"Eram cinco no papel até 2026-09-01"*) está correta como está.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-PES2-PSX.md` | modificar |
| `docs/prompts/perfil-pes2.md` | modificar |

## Verificação

- [ ] `grep -rn "cinco listas\|cinco cópias" docs/ CLAUDE.md` só devolve
      `PES2-AJUSTES.md`, os Logs de task e as frases datadas ("eram cinco
      até…", "gravou as cinco conhecidas")
- [ ] `python3 tools/check_tasks.py` verde
- [ ] a conferência de link de `.claude/rules/links.md` sem quebrado novo
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
