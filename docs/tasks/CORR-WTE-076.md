---
id: CORR-WTE-076
title: "Correção: o plano e a task dizem 758 linhas de DFM no ficha_color, e o extrator dá 866"
type: correção
category: engenharia-reversa
status: pendente
depends_on: []
---

# CORR-WTE-076: o plano e a task dizem 758 linhas de DFM no `ficha_color`, e o extrator dá 866

## Problema identificado

A §5.3 do [`docs/PLAN-WTE-LAZARUS.md`](/docs/PLAN-WTE-LAZARUS.md) e a seção
"Alvos" da [WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md) dimensionam o
formulário do editor de cor pelo tamanho do DFM:

> `lista_col0..3Change`, e o formulário `ficha_color` (**758 linhas de DFM**).

O artefato versionado — `wte/re/dfm/ficha_color.dfm`, saída do
`dfm_extract.py`, com o `--check` verde — tem **866**. A diferença é 108
linhas, 14% a mais do que o afirmado.

É o caso que o `02-revisar.md` nomeia: número de doc que veio de script
descartável em 2026-08-05 e nunca foi remedido contra a ferramenta versionada,
como já aconteceu com componentes (`~430` → 441), strings com enchimento
(70 → 13) e bitmaps (197 → 198).

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
wc -l wte/re/dfm/ficha_color.dfm
```

```text
866 wte/re/dfm/ficha_color.dfm
```

O arquivo nunca teve 758 linhas — nasceu com 866 no commit que extraiu os 18:

```bash
git log --format=%h -- wte/re/dfm/ficha_color.dfm | tail -1   # 7f8fcb0
git show "7f8fcb0:wte/re/dfm/ficha_color.dfm" | wc -l          # 866
```

E não há empate com nenhum outro formulário — os quatro maiores são:

```text
   866 wte/re/dfm/ficha_color.dfm
  1385 wte/re/dfm/estrategia.dfm
  1619 wte/re/dfm/jugador.dfm
  1941 wte/re/dfm/MainForm.dfm
```

## Causa raiz

Número medido pelo protótipo de 2026-08-05, antes do extrator versionado, e
copiado do plano para a task sem remedição.

## Correção

### Arquivo: `docs/PLAN-WTE-LAZARUS.md`

§5.3, a linha do `ficha_color`: `758 linhas de DFM` → `866 linhas de DFM`. Como
a §5.3 já carrega outros números que hoje têm ferramenta (os 105
`uniformes2d/*.bmp`, conferidos e corretos), vale anotar a fonte no mesmo
movimento — `wte/re/dfm/ficha_color.dfm` — para a próxima leitura não precisar
adivinhar de onde saiu.

### Arquivo: `docs/tasks/29-camisa-e-bandeira-2d.md`

A linha "Formulário `ficha_color`: 758 linhas de DFM" recebe o mesmo conserto.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-WTE-LAZARUS.md` | modificar |
| `docs/tasks/29-camisa-e-bandeira-2d.md` | modificar |

## Verificação

- [ ] `wc -l wte/re/dfm/ficha_color.dfm` e o número do plano são o mesmo
- [ ] `grep -rn '758 linhas' docs/` não devolve nada
- [ ] `make -C wte check` verde (o `check_fase1.py` varre o perímetro de docs)
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
