---
id: CORR-WTE-030
title: "Correção: o `tipos.md` conta 38 `strcpy`, e o `Database.cpp` tem 40 — os dois que faltam são `std::strcpy`"
type: correção
category: dados
status: concluído
depends_on: []
---

# CORR-WTE-030: 38 `strcpy` é a contagem de dentro do `Load()`, não a do arquivo

## Problema identificado

A decisão 1 de [`wte/re/tipos.md`](../../wte/re/tipos.md) — a que manda o
gerador emitir cópia com semântica de C — sustenta o argumento num número:

> Isso não basta sozinho, porque a entrada tem **38 `strcpy` e 10 `strcat`** em
> `Database.cpp`.

O `Database.cpp` tem **40** chamadas a `strcpy`. As duas que a conta deixou de
fora estão escritas `std::strcpy`, em `CopyAllStarNames()` — que **não é função
morta**: o `Load()` a chama na linha 778, e o `TeamView.cpp:536` também.

O `strcat` bate: 10, todos dentro do `Load()`.

O erro importa por dois motivos, e nenhum é estético:

1. **O que falta é uma grafia diferente**, não mais do mesmo. Uma regra de
   substituição que case `strcpy(` sem qualificação atravessa as duas de
   `CopyAllStarNames` sem tocá-las — exatamente a classe de furo que a
   armadilha 3 da `progresso.md` registra (`[^x]` casando `\n` no
   `port_database.py`).
2. **O número é o gabarito de quem revisa a WTE-TASK-17/18.** Contar 38 na
   saída gerada e dar por conferido deixa duas cópias sem porte.

## Evidência

```
$ grep -c strcpy src/core/Database.cpp
40
$ grep -o '[^:]strcpy' src/core/Database.cpp | wc -l
38
$ grep -c 'std::strcpy' src/core/Database.cpp
2
$ grep -n 'std::strcpy' src/core/Database.cpp
98:        std::strcpy(players[462 + (54 * 23) + i].name, players[ResolveMlLink(&link_euro_allstar[i * 2])].name);
100:        std::strcpy(players[462 + (55 * 23) + i].name, players[ResolveMlLink(&link_world_allstar[i * 2])].name);
```

As duas moram em `Database::CopyAllStarNames()` (linhas 94-102), fora do
`Load()` (104-801) — e é por isso que a conta por função dá 38:

```
$ sed -n '104,801p' src/core/Database.cpp | grep -c strcpy
38
$ sed -n '803,1463p' src/core/Database.cpp | grep -c strcpy
0
$ sed -n '94,102p' src/core/Database.cpp | grep -c strcpy
2
$ grep -n 'CopyAllStarNames' src/core/Database.cpp
94:void Database::CopyAllStarNames() {
778:	CopyAllStarNames();
```

`strcat`, para registro, confere: 10 no arquivo e 10 no `Load()`.

## Causa raiz

A contagem foi feita sobre o corpo do `Load()` e escrita como se fosse do
arquivo; `CopyAllStarNames()`, que o `Load()` chama, usa a grafia qualificada e
escapou do padrão de busca.

## Correção

### Arquivo: `wte/re/tipos.md`

Na decisão 1, trocar a frase pela contagem do arquivo, dizendo as duas grafias,
e estender a exigência do gerador a ambas:

> Isso não basta sozinho, porque a entrada tem **40 `strcpy` e 10 `strcat`** em
> `Database.cpp` — 38 `strcpy` e os 10 `strcat` no corpo do `Load()`, mais duas
> `std::strcpy` em `CopyAllStarNames()` (linhas 98 e 100), que o `Load()` chama
> na linha 778. **A regra de cópia tem de casar as duas grafias**, qualificada e
> nua: uma substituição ancorada em `strcpy(` atravessa as duas últimas sem
> tocá-las.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/tipos.md` | modificar |
| `docs/tasks/15-mapeamento-de-tipo.md` | modificar (achado na varredura) |

## Verificação

- [x] `grep -c strcpy src/core/Database.cpp` dá 40, e o `tipos.md` afirma 40
- [x] O `tipos.md` nomeia `CopyAllStarNames` e a grafia `std::strcpy`
- [x] `python3 wte/tools/port_database_pas.py --check` continua verde
- [ ] A saída do transpilador não deixa `std::strcpy` cru — `grep -n 'std::strcpy' wte/src/*.pas` vazio quando a WTE-TASK-18 tiver rodado
      *(a WTE-TASK-18 não rodou: `wte/src/` só tem os esqueletos `ep2002_*` e as
      tabelas geradas, nenhuma unidade `we2002_database`. `grep -rn 'std::strcpy'
      wte/src/` dá 0 hoje porque não existe saída, não porque ela esteja limpa —
      o item fica aberto de propósito, para ser conferido lá)*
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

A decisão 1 do `tipos.md` passou a afirmar **40 `strcpy` e 10 `strcat`**, com a
repartição escrita: 38 `strcpy` e os 10 `strcat` no corpo do `Load()`, mais duas
`std::strcpy` em `CopyAllStarNames()` (linhas 98 e 100), que o `Load()` chama na
linha 778. Junto foi a instrução que o número existe para sustentar: **a regra
de cópia do gerador tem de casar as duas grafias**, porque uma substituição
ancorada em `strcpy(` atravessa as duas qualificadas sem tocá-las.

**Problemas encontrados:**

A varredura achou um segundo sítio que a CORR não listava:
`docs/tasks/15-mapeamento-de-tipo.md:120` repete "38 `strcpy` e 10 `strcat`" na
seção de precisões — e é o texto que o executor da WTE-TASK-17/18 lê antes de
escrever a regra de cópia, o pior lugar para o número velho sobreviver.
Corrigido na mesma invocação, com ponteiro para a decisão 1.

**Arquivos criados/modificados:**

- `wte/re/tipos.md`
- `docs/tasks/15-mapeamento-de-tipo.md`
