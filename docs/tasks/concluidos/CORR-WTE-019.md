---
id: CORR-WTE-019
title: "Correção: a reversão que versionou 816.880 bytes de arte do Obocaman só está registrada num README derivado"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-019: a reversão do versionamento dos blobs não chegou ao plano, ao `.gitignore` nem ao `progresso.md`

## Problema identificado

A WTE-TASK-10 versionou os 118 blobs binários do Obocaman — 816.880 bytes de
ícone, `Picture.Data` e `Glyph.Data` — como hex inline dentro dos 18
`wte/forms/*.lfm`, que o git rastreia. **Foi decisão do usuário e está
registrada**, em `wte/re/dfm/README.md` §"E os `.lfm` da WTE-TASK-10 **têm** o
hex, por decisão do usuário", com a razão certa: sem o hex a janela abre sem
ícone e sem glifo, e a WTE-TASK-12 compararia contra uma tela que não é a do
port. Isso **não é a discrepância**.

A discrepância é que os três documentos que governam a política continuam
dizendo o contrário, sem uma linha de ressalva e sem ponteiro para o README que
os reverte:

1. **`docs/PLAN-WTE-LAZARUS.md` §2** — a **fonte de verdade** do projeto — diz
   "binário de terceiro sem fonte e sem licença **não entra no repositório**",
   como razão do `.gitignore`. Hoje 816.880 bytes de arte de terceiro estão no
   repositório.
2. **`.gitignore`**, no bloco `wte/re/dfm/blobs/`, é o arquivo que **aplica** a
   política e afirma explicitamente que a codificação não muda nada: "Hex
   inline no `.dfm` seria a mesma coisa numa codificação diferente". É
   exatamente o que os `.lfm` fazem, e o bloco não sabe disso.
3. **`docs/tasks/concluidos/progresso.md`**, em "Pendências externas": "**Assets não
   redistribuídos.** Os 198 BMP e o `dat.bin` ficam com o usuário, como
   `roms/`." Os 118 blobs são da mesma população de arte e deixaram de ficar
   só com o usuário.

Quem ler o plano ou o `.gitignore` — que é o caminho normal, o README de
`wte/re/dfm/` não é linkado de nenhum dos dois — conclui que o repositório não
versiona arte do Obocaman, e conclui errado. E o argumento que a reversão
respondeu foi o de **utilidade** ("o `.lfm` é o formulário"); o argumento
original era de **licença**, e esse continua sem resposta escrita em lugar
nenhum.

## Evidência

Os bytes estão versionados:

```
$ git ls-files wte/forms/*.lfm | wc -l
18
$ python3 -c "..."      # soma dos 18 .lfm e das linhas só de hex
lfm bytes: 1960767 linhas de hex bytes: 1818756 pct 92.8
$ grep -E '^\| \*\*total\*\* \| \*\*118\*\*' wte/forms/conversao.md
| **total** | **118** | **816880** |
```

92,8% do peso versionado de `wte/forms/` é o hex dos blobs.

O que os três documentos dizem hoje:

```
$ sed -n '339,343p' docs/PLAN-WTE-LAZARUS.md
O `we-team-editor.exe` é obra do **Obocaman (2002)**, sem licença concedida,
igual ao código herdado do Moriero e do thyddralisk que o
[NOTICE.md](../NOTICE.md) já registra. O `we-team-editor/` está no `.gitignore`
justamente por isso: binário de terceiro sem fonte e sem licença não entra no
repositório.

$ sed -n '89,97p' .gitignore
# `wte/re/dfm/*.dfm` e documentacao e fica versionado. Os 118 blobs que ele
# referencia -- `Icon.Data`, `Picture.Data`, `Glyph.Data` -- nao: sao 798 KiB
# de arte do Obocaman, da mesma natureza dos 198 `.bmp` de `we-team-editor/`,
# que este arquivo ignora por serem binario de terceiro sem licenca. Hex inline
# no `.dfm` seria a mesma coisa numa codificacao diferente.

$ sed -n '305,306p' docs/tasks/progresso.md
- **Assets não redistribuídos.** Os 198 BMP e o `dat.bin` ficam com o usuário,
  como `roms/`. O app precisa falhar com mensagem clara sem eles.
```

E o que a reversão diz, no único lugar em que está:

```
$ sed -n '51,61p' wte/re/dfm/README.md
### E os `.lfm` da WTE-TASK-10 **têm** o hex, por decisão do usuário
[...] Isso parece contradizer a regra de cima, e a contradição é real: foi
posta na mesa em 2026-08-06 e **resolvida a favor de versionar**.
```

## Causa raiz

A reversão foi escrita onde ela nasceu — o README da pasta dos DFM — e não nos
documentos que declaram a política, que são outros três e nenhum deles aponta
para ali.

## Correção

A decisão **não muda**: os `.lfm` continuam com o hex. O que muda é o registro.

### Arquivo: `docs/PLAN-WTE-LAZARUS.md`

Na §2, depois do parágrafo do `we-team-editor/`, acrescentar a exceção medida,
com o número e o ponteiro:

> **Uma exceção, decidida em 2026-08-06.** Os 118 blobs de formulário
> (`Icon.Data`, `Picture.Data`, `Glyph.Data` — 816.880 bytes) **estão**
> versionados, como hex inline nos 18 `wte/forms/*.lfm`. O `.lfm` não é
> documentação, é o formulário: sem o hex a janela abre sem ícone e sem glifo,
> e a WTE-TASK-12 — o gate da fase 2 — compararia contra uma tela que não é a
> do port. O registro completo está em
> `[../wte/re/dfm/README.md](../wte/re/dfm/README.md)` — caminho relativo à
> raiz de `docs/`, que é onde o plano mora. O restante da arte (os 198 `.bmp`
> e o `dat.bin`) continua fora.

### Arquivo: `.gitignore`

No bloco `wte/re/dfm/blobs/`, emendar a frase que hoje afirma que a codificação
não muda nada, para que ela não seja lida como proibição geral:

```
# Hex inline no `.dfm` seria a mesma coisa numa codificacao diferente -- e por
# isso o `.dfm` nao o tem. Os `wte/forms/*.lfm` **tem**, por decisao de
# 2026-08-06 registrada em wte/re/dfm/README.md: ali o hex nao e documentacao,
# e o formulario. A regra deste bloco vale para `wte/re/`, nao para
# `wte/forms/`.
```

### Arquivo: `docs/tasks/concluidos/progresso.md`

Em "Pendências externas", qualificar o item para que ele diga o que ficou de
fora e o que entrou:

> - **Assets não redistribuídos, com uma exceção.** Os 198 BMP e o `dat.bin`
>   ficam com o usuário, como `roms/`. Os 118 blobs de formulário (816.880 B)
>   **estão** versionados em hex nos `wte/forms/*.lfm` — decisão de 2026-08-06,
>   em [`../../wte/re/dfm/README.md`](../../../wte/re/dfm/README.md).

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-WTE-LAZARUS.md` | modificar (§2) |
| `.gitignore` | modificar (bloco `wte/re/dfm/blobs/`) |
| `docs/tasks/concluidos/progresso.md` | modificar (Pendências externas) |

## Verificação

- [ ] `grep -n "816.880\|816880" docs/PLAN-WTE-LAZARUS.md .gitignore docs/tasks/concluidos/progresso.md`
      acha a exceção nos três
- [ ] `grep -n "wte/re/dfm/README" docs/PLAN-WTE-LAZARUS.md .gitignore docs/tasks/concluidos/progresso.md`
      — os três apontam para o registro da decisão
- [ ] `make -C wte check` continua verde (o `check_fase1.py` varre estes
      markdowns atrás de número velho)
- [ ] a conferência de links de `.claude/rules/links.md` sai vazia
- [ ] nenhum `.lfm` mudou: `python3 wte/tools/dfm2lfm.py --check` verde
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-09

**Resumo do que foi feito:** A exceção dos 118 blobs (816.880 B versionados como
hex inline nos 18 `wte/forms/*.lfm`) entrou nos três documentos que declaram a
política — §2 do plano, o bloco `wte/re/dfm/blobs/` do `.gitignore` e as
"Pendências externas" do `progresso.md` —, os três com o número e o ponteiro
para `wte/re/dfm/README.md`. A decisão não mudou e nenhum `.lfm` foi tocado.

**Problemas encontrados:** A varredura puxou um quarto sítio que a CORR não
previa: o problema 5 do Log da WTE-TASK-10 diz "isso tensiona a §2 do plano",
e a §2 deixou de tensionar no mesmo commit em que a exceção entrou. Ganhou uma
linha *Resolvido:* apontando para os três documentos e para esta correção.

**Arquivos criados/modificados:**

- `docs/PLAN-WTE-LAZARUS.md` (§2 — parágrafo da exceção)
- `.gitignore` (bloco `wte/re/dfm/blobs/`)
- `docs/tasks/concluidos/progresso.md` ("Pendências externas")
- `docs/tasks/concluidos/10-conversor-dfm-para-lfm.md` (Log, problema 5 — discrepância
  achada no caminho)
