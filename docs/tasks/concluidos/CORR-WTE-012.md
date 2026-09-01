---
id: CORR-WTE-012
title: "Correção: a §1 do plano diz 300 imports de rtl60/vcl60 (são 267) e chama o TBrowseURL de componente de terceiro, que a §5 do mesmo arquivo já desmente"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-012: duas afirmações da §1 que a WTE-TASK-07 mediu e ninguém propagou

## Problema identificado

A WTE-TASK-07 mediu duas coisas que contradizem a §1 do plano, registrou as duas
no Log e deixou as duas onde estavam — a instrução da tarefa delimitava a edição
do plano à §5. O resíduo é que a §1 continua afirmando o que já se sabe falso, e
num dos casos o **mesmo arquivo** afirma as duas coisas.

**1. `docs/PLAN-WTE-LAZARUS.md:117` (§1.2).**

> | Imports | 322, sendo **300** de `rtl60.bpl`/`vcl60.bpl` |

Medido: **267** (103 de `rtl60.bpl` + 164 de `vcl60.bpl`). Os outros 55 são
`KERNEL32` (51), `USER32` (3) e `OLEAUT32` (1). O total de 322 está certo.

Este número **não tem dono**: o quadro de reconciliação da
[WTE-TASK-09](/docs/tasks/concluidos/09-fechamento-fase-1.md) lista cinco afirmações da §1
para remedir, e a dos imports não está entre elas — nem podia estar pela
ferramenta ali indicada, já que `dump_units.py` é quem mede isso e só passou a
existir na WTE-TASK-07.

**2. `docs/PLAN-WTE-LAZARUS.md:251` (§1.6).**

> Vinte classes distintas. **Dezenove têm equivalente direto na LCL** — ver §5.
> `TBrowseURL` é **componente de terceiro** e é o único a substituir.

Medido na WTE-TASK-07: é a ação padrão da própria VCL, unidade `Extactns`,
disparada por método dinâmico dentro do `vcl60.bpl` — não é componente de
terceiro. A §5 do **mesmo arquivo**, linha 522, já foi corrigida pela tarefa e
diz o contrário:

> | **`TBrowseURL`** | **sem par** | ação padrão da VCL (unidade `Extactns`),
> **não componente de terceiro** — medido na WTE-TASK-07. […] |

Então hoje o plano se contradiz internamente. A substituição proposta
(`TLabel` + `OpenURL()` de `LCLIntf`) continua certa nos dois lugares — o que
muda é a justificativa, e ela importa: "componente de terceiro" sugere um
`.bpl` externo que não existe e que alguém pode sair procurando na WTE-TASK-10.

A reconciliação da §1.6 que a WTE-TASK-09 tem no quadro é `dfm_extract.py`, que
conta componentes — não julga a origem de uma classe. Este item também fica sem
dono.

## Evidência

Contagem de imports por DLL, com `objdump -x` (fonte independente do
`dump_units.py`):

```
$ objdump -x we-team-editor/we-team-editor.exe | awk '/DLL Name:/{d=$3} /^\t[0-9a-f]+\t/{c[d]++} END{...}'
KERNEL32.DLL     51
OLEAUT32.DLL     1
rtl60.bpl        103
USER32.DLL       3
vcl60.bpl        164
TOTAL            322
```

`103 + 164 = 267`, contra os 300 da §1.2. O `unidades-vcl.md` gerado diz o
mesmo:

> São 322 imports, 267 deles de `rtl60.bpl` e `vcl60.bpl`, distribuídos em 42
> unidades Borland nomeadas.

Para o `TBrowseURL`, as duas passagens do plano, hoje:

```
$ grep -n "TBrowseURL" docs/PLAN-WTE-LAZARUS.md
251:`TBrowseURL` é componente de terceiro e é o único a substituir.
522:| **`TBrowseURL`** | **sem par** | ação padrão da VCL (unidade `Extactns`),
     não componente de terceiro — medido na WTE-TASK-07. […]
```

E a razão medida, do `unidades-vcl.md`: `SHELL32.DLL` não está na tabela de
import — o que se confirma pela lista de DLLs acima, que tem cinco entradas e
nenhuma delas é `SHELL32` ou `ADVAPI32`.

## Causa raiz

A WTE-TASK-07 tinha mandato para editar só a §5, e o quadro de reconciliação da
WTE-TASK-09 foi escrito antes de existir ferramenta que medisse imports.

## Correção

### Arquivo: `docs/PLAN-WTE-LAZARUS.md`

- **§1.6, linha 251:** trocar "componente de terceiro" por "ação padrão da VCL
  (unidade `Extactns`)", alinhando com a linha 522 e mantendo "é o único a
  substituir", que continua verdade.
- **§1.2, linha 117:** deixar como está **se** a WTE-TASK-09 assumir o número
  (item abaixo); é ela quem reconcilia a §1, e corrigir aqui duplicaria a
  edição. O que não pode é o número ficar sem nenhum dos dois.

### Arquivo: `docs/tasks/concluidos/09-fechamento-fase-1.md`

Acrescentar a linha que falta ao quadro de reconciliação:

```markdown
| 322 imports, sendo 300 de `rtl60.bpl`/`vcl60.bpl` | `dump_units.py` |
```

A ferramenta já mede e já publica o valor certo; o que falta é a linha que
manda conferir. Sem ela, a §1.2 sai da fase 1 com um número que duas medições
independentes desmentem.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-WTE-LAZARUS.md` | modificar — §1.6, linha 251 |
| `docs/tasks/concluidos/09-fechamento-fase-1.md` | modificar — quadro de reconciliação |

## Verificação

- [x] `grep -n "componente de terceiro" docs/PLAN-WTE-LAZARUS.md` não devolve
      mais a linha 251, e as duas passagens do `TBrowseURL` concordam — as três
      ocorrências restantes (252, 523, 552) são todas a forma negada
- [x] O quadro da WTE-TASK-09 tem a linha dos imports, apontando para
      `dump_units.py`
- [x] O valor a reconciliar bate com o `unidades-vcl.md`: 322 no total, 267 dos
      dois `.bpl`
- [x] `python3 wte/tools/dump_units.py --check` verde (nenhum gerado tocado)
- [x] Links de markdown conforme `.claude/rules/links.md`
- [x] `roms/` intocada; `we-team-editor.exe` aberto só para leitura

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-06

**Resumo do que foi feito:**

A §1.6 parou de contradizer a §5 do mesmo arquivo: `TBrowseURL` passou de
"componente de terceiro" para "ação padrão da própria VCL (unidade
`Extactns`)", com a marca de onde isso foi medido. A substituição proposta não
muda — `TLabel` + `OpenURL()` de `LCLIntf` continua certa nos dois lugares —,
muda a justificativa, e ela importa: "componente de terceiro" manda alguém
procurar na WTE-TASK-10 um `.bpl` externo que não existe.

O número dos imports **não foi corrigido no plano**, de propósito, e sim ganhou
dono: a linha `| 322 imports, sendo 300 de rtl60.bpl/vcl60.bpl (§1.2) |
dump_units.py |` entrou no quadro de recontagem da WTE-TASK-09. É ela quem
reconcilia a §1, e corrigir aqui duplicaria a edição — o que não podia é o
número ficar sem nenhum dos dois. A ferramenta já mede e já publica o valor
certo (`unidades-vcl.md`: 322 no total, 267 dos dois `.bpl`).

**Problemas encontrados:**

A varredura pegou o efeito colateral da linha nova: o critério de conclusão da
WTE-TASK-09 dizia "os **cinco** números do plano remedidos". Passaram a ser
seis. Corrigido na mesma invocação — critério que conta errado é critério que
se cumpre sem cumprir.

A mesma afirmação aparece em `docs/tasks/concluidos/progresso.md:391`, na tabela "Estado
medido na criação destas tasks". Deixada como está, e não por omissão: aquela
seção abre dizendo que os números vêm de script descartável e que "a WTE-TASK-09
os remede com ferramenta versionada". Já tem dono, e é o mesmo.

**Arquivos criados/modificados:**

- `docs/PLAN-WTE-LAZARUS.md` — §1.6
- `docs/tasks/concluidos/09-fechamento-fase-1.md` — quadro de recontagem e o critério que
  contava cinco
- `docs/tasks/concluidos/correcoes-progresso.md`
