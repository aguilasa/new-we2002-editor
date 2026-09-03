---
id: CORR-PES2-027
title: "Correção: o `pes2_boot` nunca roda pela receita documentada — ele quer `PES2_IMAGE`, e os docs só dão `WE2002_PES2_*`"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-PES2-027: o gate de boot se reporta *skipped* na única receita escrita

## Problema identificado

O [`CLAUDE.md`](../../CLAUDE.md) e o
[`perfil-pes2.md`](/docs/prompts/perfil-pes2.md) descrevem os três alvos assim:

> **`pes2_image`**, que precisa de `WE2002_PES2_IMAGE`; e **`pes2_boot`**, que
> precisa do DuckStation e do `:98` e leva ~90 s. Os dois últimos se reportam
> *skipped* sem o que precisam

e dão uma receita:

```sh
WE2002_PES2_IMAGE="…(Track 1).bin" \
WE2002_PES2_IMAGE_B="…(Track 1).bin" \
WE2002_PES2_CARD="…_1.mcd" \
WE2002_PES2_TMPDIR=<~450 MiB livres> \
  ctest --test-dir build -R pes2
```

O `boot_check.sh` não lê nenhuma dessas. A primeira coisa que ele faz é:

```sh
[ -n "${PES2_IMAGE:-}" ] || skip "PES2_IMAGE is not set"
```

Então a receita documentada **sempre** pula o `pes2_boot`, e o pula com o
mesmo `Skipped` que uma máquina sem emulador produz. Quem roda `ctest -R pes2`
com tudo o que os docs mandam vê `100% tests passed` e acredita que o boot foi
julgado. Ele não foi.

O `pes2_boot` é o único gate deste ciclo que **põe o jogo na tela**. Um gate
que só existe fora da receita é um gate que não corre.

Isto foi visto na execução da própria PES2-TASK-32, e o Log dela escreveu:

> 3. **O `pes2_boot` do `ctest` se reporta *skipped* com `WE2002_PES2_IMAGE`
>    sozinho** — ele quer `PES2_IMAGE` apontando para o `.cue`. Foi rodado à
>    parte com as duas, e passou. Não é defeito, é uma variável a mais que a
>    linha do perfil não mostra.

O diagnóstico está certo e a conclusão não: "uma variável que a linha não
mostra" é precisamente o defeito, porque a linha é a única instrução que
existe. A correção nunca foi feita.

## Evidência

Com exatamente a variável que os docs mandam:

```
$ WE2002_PES2_IMAGE="roms/…(EsIt)/…(Track 1).bin" \
    ctest --test-dir build -R pes2_boot
1/1 Test #9: pes2_boot ........................***Skipped   0.01 sec
100% tests passed, 0 tests failed out of 1
```

0,01 s — ele nem chegou a procurar o emulador. Com a variável certa, o mesmo
gate corre e fecha:

```
$ PES2_IMAGE="<copia>/….cue" tools/pes2/boot_check.sh
BOOT OK: the fork (/home/ingmar/Applications/duckstation-mcp/bin/duckstation-qt),
window 4194311, 800x655, two live frames in /tmp/pes2-boot-hdr1z3
```

E as duas famílias de nome convivem sem que nada as relacione:

```
$ grep -rn "PES2_IMAGE" tools/pes2/boot_check.sh | head -2
14:#   PES2_IMAGE     .cue of a working copy (required)
56:[ -n "${PES2_IMAGE:-}" ] || skip "PES2_IMAGE is not set"

$ grep -n "WE2002_PES2_IMAGE" CLAUDE.md docs/prompts/perfil-pes2.md
CLAUDE.md:600, CLAUDE.md:606, perfil-pes2.md:171
```

## Causa raiz

Duas famílias de variável coexistem — `WE2002_PES2_*` para as ferramentas de
disco e `PES2_*` para as de emulador — e a receita de `ctest` só ganhou a
primeira, porque o `pes2_boot` entrou depois e ninguém a reescreveu.

## Correção

Duas frentes, e a segunda é a que impede a reincidência.

### Arquivo: `CLAUDE.md` e `docs/prompts/perfil-pes2.md`

Pôr `PES2_IMAGE` na receita, apontando para o **`.cue`** — que é outro
arquivo do que o `(Track 1).bin` das demais:

```sh
WE2002_PES2_IMAGE="<copia>/…(Track 1).bin" \
WE2002_PES2_IMAGE_B="…" \
WE2002_PES2_CARD="…" \
WE2002_PES2_TMPDIR=<~450 MiB livres> \
PES2_IMAGE="<copia>/….cue" \
  ctest --test-dir build -R pes2
```

e trocar "precisa do DuckStation e do `:98`" por "precisa de `PES2_IMAGE`
apontando o **`.cue`** de uma cópia, do DuckStation e do `:98`".

### Arquivo: `tools/pes2/boot_check.sh`

Fazer a mensagem de skip distinguir "faltou a variável" de "esta máquina não
roda isso". Hoje as duas saem iguais, e é por isso que o furo sobreviveu:

```sh
if [ -z "${PES2_IMAGE:-}" ]; then
    if [ -n "${WE2002_PES2_IMAGE:-}" ]; then
        skip "PES2_IMAGE is not set -- WE2002_PES2_IMAGE is, but this gate
wants the .cue of a working copy, not the Track 1 .bin"
    fi
    skip "PES2_IMAGE is not set"
fi
```

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `CLAUDE.md` | modificar |
| `docs/prompts/perfil-pes2.md` | modificar |
| `tools/pes2/boot_check.sh` | modificar |

## Verificação

- [ ] a receita do `CLAUDE.md`, copiada e colada com as quatro variáveis, faz
      o `pes2_boot` **correr** — `Passed`, ~90 s, não `Skipped` em 0,01 s
- [ ] com só `WE2002_PES2_IMAGE`, o skip diz que a variável trocada é a causa
- [ ] `PES2_IMAGE` apontando para o `(Track 1).bin` em vez do `.cue` também
      diz o que fazer
- [ ] `roms/` intocada — a receita aponta para cópia

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
