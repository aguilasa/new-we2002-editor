---
id: CORR-WTE-068
title: "Correção: três specs de gravação ainda dizem que o gate passa \"só as duas faixas do arranque\", e hoje ele é byte-idêntico"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-068: a régua escrita nas specs envelheceu na própria task

## Problema identificado

A oitava passagem da WTE-TASK-27 portou os dois remendos de arranque
(`PatchDeVinculoDeArranque`, `PatchDeByteSoltoDeArranque`), tirou as doze
declarações `conhecida:` dos roteiros e registrou isso no
`wte/tests/roteiros/README.md`, na spec do `boton_dialogo_weClick` e no
`ml-slots.md`. **Três specs de gravação ficaram para trás** e continuam
afirmando, no presente, o resultado antigo:

| arquivo | linha | o que diz |
|---|---|---|
| `wte/re/spec/MainForm.boton_barras2isoClick.md` | 119-120 | `\| golden-03-barras \| gravar sem editar \| passou — só as duas faixas do arranque \|` e `golden-04-barras-editada … passou — idem` |
| `wte/re/spec/MainForm.boton_nombres2isoClick.md` | 207-209 | "`golden_check.sh` sobre `golden-05-nomes` / `.port`: **passou**, só as duas faixas do arranque divergem" |
| `wte/re/spec/MainForm.boton_tex2isoClick.md` | 105-106 | "`golden_check.sh` sobre `golden-06-textura` / `.port`: **passou**, só as duas faixas do arranque divergem" |

Rodados hoje, os três gates dão **byte-idêntico**, sem faixa nenhuma. As
frases não são só velhas: elas descrevem uma divergência que **não existe
mais**, e são a superfície de evidência que a
[WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md) vai colher. Colhida
assim, entra no registro central um fantasma.

## Evidência

Os gates, medidos em 2026-08-20 nesta revisão:

```text
golden-01-arranque  golden      PASSOU: byte-identico
golden-01-arranque  positivo    OK: o gate DETECTOU o byte plantado (405228)
golden-03-barras    golden      PASSOU: byte-identico
golden-05-nomes     golden      PASSOU: byte-identico
golden-06-textura   golden      PASSOU: byte-identico   (com WTE_TEXTURA=work/t.bin)
golden-11-descarte  controle    PASSOU: byte-identico
golden-11-descarte  golden      PASSOU: byte-identico
```

E nenhum roteiro declara faixa:

```text
>> golden_veredito.py --check
golden_veredito: 21 roteiro(s), 0 declaracao(oes) legivel(eis)
```

Contra o que as três specs afirmam:

| fonte | resultado do gate |
|---|---|
| `boton_barras2isoClick.md:119`, `boton_nombres2isoClick.md:208`, `boton_tex2isoClick.md:105` | "só as duas faixas do arranque" |
| `golden_check.sh`, hoje | **byte-idêntico, zero faixas** |

Uma quarta ocorrência **não** é discrepância e deve ficar como está:
`grabar_memoryClick.md:191` fala do `cmp` da **sonda** `27-mcr` contra a cópia
limpa, e ali as duas faixas continuam aparecendo — o oráculo grava os remendos
e a cópia limpa não os tem. A distinção é gate (dois lados) × sonda (um lado
contra o original).

## Causa raiz

A passagem que tirou as declarações varreu os roteiros e os documentos de
processo, e não as seções "a régua desta task" das specs escritas nas passagens
anteriores.

## Correção

### Arquivo: `wte/re/spec/MainForm.boton_barras2isoClick.md`

Trocar as duas células de resultado por **`passou — byte-idêntico`**, com a
data da medição, e uma linha dizendo que até 2026-08-20 as duas faixas do
arranque apareciam ali, e por quê (os remendos passaram a ser portados —
WTE-TASK-27, oitava passagem).

### Arquivo: `wte/re/spec/MainForm.boton_nombres2isoClick.md`

Idem na seção "O que a régua desta task mediu". O parágrafo seguinte, o do
lado port sozinho contra a ROM limpa, está correto e fica.

### Arquivo: `wte/re/spec/MainForm.boton_tex2isoClick.md`

Idem na seção "A régua", preservando a nota do `WTE_TEXTURA`.

**Não mexer** em `grabar_memoryClick.md:191` — ver acima.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/MainForm.boton_barras2isoClick.md` | modificar |
| `wte/re/spec/MainForm.boton_nombres2isoClick.md` | modificar |
| `wte/re/spec/MainForm.boton_tex2isoClick.md` | modificar |

## Verificação

- [x] `grep -rn 'faixas do arranque' wte/re/spec/` só devolve
      `boton_dialogo_weClick.md` (histórico, já reescrito) e
      `grabar_memoryClick.md` (sonda, correto)
- [x] Cada uma das três specs cita a corrida que sustenta a frase nova, com data
- [x] `bash wte/tools/golden_check.sh wte/tests/roteiros/golden-03-barras.txt
      --modo golden --roteiro-port …` continua **byte-idêntico**
- [x] `make -C wte check` rc 0 (o `spec_index.py` lê estes arquivos)
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-20

**Resumo do que foi feito:**

As três células de resultado passaram a dizer **byte-idêntico**, com a data da
corrida que as sustenta, e cada spec ganhou a nota do que mudou: até 2026-08-20
o oráculo gravava os dois remendos de arranque e o port não, e a oitava
passagem da WTE-TASK-27 portou os dois. Não foi troca de palavra — os quatro
gates foram rodados hoje, um por afirmação:

| corrida | modo | resultado |
|---|---|---|
| `golden-03-barras` | controle | PASSOU: byte-idêntico |
| `golden-03-barras` | golden | PASSOU: byte-idêntico |
| `golden-04-barras-editada` | golden | PASSOU: byte-idêntico |
| `golden-05-nomes` | golden | PASSOU: byte-idêntico |
| `golden-06-textura` (`WTE_TEXTURA=$PWD/work/t.bin`) | golden | PASSOU: byte-idêntico |

O controle é o que dá sentido aos outros quatro: zero divergência também é o
que se veria se nenhum dos dois lados gravasse.

**Problemas encontrados:**

Nenhum. A varredura por `faixas do arranque` em `wte/re/spec/` devolve agora,
além das três notas históricas que esta correção escreveu, só o
`boton_dialogo_weClick.md` (que já narra o fechamento das duas faixas, em
2026-08-20) e o `grabar_memoryClick.md`. Este último a CORR mandou não tocar, e
está certo: ali a medição é a **sonda** contra a cópia limpa — um lado só —, e
o oráculo grava os remendos que a cópia limpa não tem. A distinção gate (dois
lados) × sonda (um lado) é o que separa as duas frases.

**Arquivos criados/modificados:**

- `wte/re/spec/MainForm.boton_barras2isoClick.md`
- `wte/re/spec/MainForm.boton_nombres2isoClick.md`
- `wte/re/spec/MainForm.boton_tex2isoClick.md`
