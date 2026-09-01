---
id: CORR-WTE-143
title: "Correção: `8.10-return-nao-dispara.sh` é chamado de hook de golden, mas `golden_check.sh` com ele sempre reprova"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-143: o roteiro do item 4 só serve para um dos dois lados

## Problema identificado

A §8.10 diz:

```text
Dois roteiros são hooks de golden (`tools/par/8.10-reload-descarta.sh` e
`8.10-return-nao-dispara.sh`) e dois rodam sozinhos
```

Os dois são hooks, mas só **um** deles pode ser rodado pelo
`tools/golden_check.sh`. Com o `8.10-return-nao-dispara.sh` o oráculo
**encerra** ao receber o `Return` — que é exatamente o achado do item 4 —, então
o `golden_run.sh` morre antes de gravar e a corrida reprova **sempre**, por
motivo conhecido e esperado.

O cabeçalho do roteiro não diz isso. Ele explica o risco do `autoDefault`, o
porquê do ponteiro no meio do diálogo, e nada sobre o lado do oráculo. Quem
re-rodar os roteiros da §8.10 — que é o procedimento que esta série usa a cada
mudança — recebe um vermelho e não tem como distinguir "a divergência de ciclo
de vida já conhecida" de "regressão nova", sem ir ler a
[CORR-WTE-141](/docs/tasks/concluidos/CORR-WTE-141.md).

## Evidência

A própria CORR-WTE-141 registra o resultado do lado do oráculo:

```text
tools/golden_run.sh: nao consegui focar a janela 0xe00001
$ python3 tools/golden_compare.py roms/ptbr-remaster.bin ora.bin
IDENTICAL
```

E o cabeçalho do roteiro, na íntegra do que diz sobre execução:

```text
# NÃO carrega prelúdio: o item é sobre a janela principal recém-carregada, sem
# time selecionado nem campo em edição. Qualquer clique antes mudaria o foco e
# com ele o destino da tecla.
```

Medido nesta revisão pelo lado do port, que é o que o item afirma e que
**passa**: com o roteiro em `GOLDEN_GUI_EDIT`, a cópia gravada é
byte-idêntica à de um `Load`+`Save` sem tecla nenhuma, e acusa contra a imagem
original só as 5 faixas / 41 bytes das não-idempotências conhecidas.

```text
$ cmp ret.bin plain.bin && echo IDENTICOS
IDENTICOS
$ python3 tools/golden_compare.py roms/ptbr-remaster.bin ret.bin
5 run(s), 41 byte(s) differ
```

## Causa raiz

O roteiro mede um comportamento em que os dois lados **não podem** fazer a
mesma coisa, e o cabeçalho não separa o que é para o port do que é para o
oráculo.

## Correção

### Arquivo: `tools/par/8.10-return-nao-dispara.sh`

Acrescentar ao cabeçalho, no mesmo tom dos outros roteiros que carregam
armadilha (o `8.7-t2002-importar.sh` é o modelo — ele abre com
`>>> NO ORÁCULO ESTE ROTEIRO NÃO IMPORTA NADA, E ISSO É UM ACHADO. <<<`):

- este roteiro é **só do lado do port** (`GOLDEN_GUI_EDIT`);
- com `GOLDEN_EDIT` o oráculo encerra e o `golden_run.sh` sai
  `nao consegui focar a janela`, o que é **o resultado esperado**, não
  regressão — CORR-WTE-141;
- o veredito do item é `cmp` contra uma corrida de controle sem tecla nenhuma,
  não o `OK` do `golden_check.sh`.

### Arquivo: `docs/PARIDADE-FUNCIONAL.md`

Na frase que classifica os quatro roteiros, dizer que o do item 4 é hook de
**um** lado só, e como se lê o resultado dele.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/par/8.10-return-nao-dispara.sh` | modificar |
| `docs/PARIDADE-FUNCIONAL.md` | modificar — a frase dos quatro roteiros na §8.10 |

## Verificação

- [ ] O cabeçalho diz qual hook usar e o que esperar do outro lado
- [ ] A §8.10 não chama de "hook de golden" um roteiro cujo `golden_check.sh`
      reprova por construção
- [ ] O veredito do item 4 continua reproduzível: `cmp` entre a corrida com
      `Return` e a de controle sem tecla dá arquivos iguais
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-31

**Resumo do que foi feito:**

O cabeçalho do roteiro abre agora com `>>> ESTE ROTEIRO É HOOK DE UM LADO SÓ:
GOLDEN_GUI_EDIT, o port. <<<`, no modelo do `8.7-t2002-importar.sh`, e diz o que
acontece do outro lado — o oráculo encerra, o `golden_run.sh` sai
`nao consegui focar a janela 0xe00001`, e a reprovação é o resultado esperado
(CORR-WTE-141). O veredito do item ficou escrito com o comando que o produz:
`cmp` entre a corrida com `Return` e a de controle sem tecla nenhuma.

Na §8.10, a frase que dizia "dois roteiros são hooks de golden" virou tabela dos
quatro, com **como se roda** e **qual é o veredito** de cada um — que é a
distinção que faltava.

**Problemas encontrados:** nenhum.

A sequência que o cabeçalho novo prescreve foi rodada como está escrita, e
fecha:

```text
$ cmp "$SCRATCH/ret.bin" "$SCRATCH/ctl.bin" && echo "cmp: IGUAIS"
cmp: IGUAIS
$ python3 tools/golden_compare.py roms/ptbr-remaster.bin "$SCRATCH/ret.bin"
5 run(s), 41 byte(s) differ
```

**Arquivos criados/modificados:**

- `tools/par/8.10-return-nao-dispara.sh` — o cabeçalho
- `docs/PARIDADE-FUNCIONAL.md` — a tabela dos quatro roteiros na §8.10
- `docs/tasks/concluidos/PAR-TASK-09.md` — nota posterior
