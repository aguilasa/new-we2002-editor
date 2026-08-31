---
id: CORR-WTE-135
title: "Correção: o item 5 da §8.7 (`.t2002`) foi fechado sem veredito de golden"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-135: o `.t2002` fechou por prosa, não por comparação

## Problema identificado

A [PAR-TASK-06](/docs/tasks/PAR-TASK-06.md) diz, na própria seção **Método**,
que o critério da série é "fazer a mesma coisa nos dois lados, gravar as duas
cópias e comparar com `tools/golden_compare.py`", e a **Definição de pronto**
exige "cada item com evidência: o comando, a faixa que saiu do
`golden_compare.py`, e o veredito".

O item 5 — o que a própria task chama de "o mais valioso da série inteira" — é
o único fechado **sem esse veredito**. O que existe é:

- tamanhos de arquivo e dois hexdumps (52 × 56 bytes);
- a leitura do fonte que mostra que o formato é de 52
  (`legacy/mfc/tattDlg.cpp:701`), fechando a
  [CORR-WTE-132](/docs/tasks/CORR-WTE-132.md);
- as faixas de **um lado só** — o `ed.exe` importando o arquivo do port,
  comparado contra a imagem original.

E a perna "importar de volta", marcada `[x]` nos dois documentos, tem como
único registro **um comentário dentro do roteiro**:

```text
$ grep -rn "aceita o próprio arquivo" docs/ tools/par/
tools/par/8.7-t2002-importar.sh:8:# teste, aceita o próprio arquivo. Ver CORR-WTE-132.
```

Não há faixa, não há veredito, e o `golden_compare.py` nunca correu entre os
dois lados para este item.

## Evidência

Os dois roteiros do item existem e são parametrizados por `PAR_T2002`
(caminho Windows no oráculo, POSIX no port), mas **não estão entre os que
foram re-rodados**. O Log da quarta passagem lista os seis:
`8.7-clamp-xy.sh`, `8.7-troca-papel.sh`, `8.7-presets-16.sh`,
`8.7-preset-renomear.sh`, `8.7-escape-papel.sh`,
`8.7-escape-papel-sem-navegar.sh` — o `8.7-t2002-exportar.sh` e o
`8.7-t2002-importar.sh` ficaram de fora.

A medição **está disponível desde a CORR-WTE-132**, que é o que torna esta
lacuna corrigível: os dois lados aceitam o arquivo de 52 bytes do port. Logo o
estímulo simétrico existe — **os dois importando o mesmo `.t2002`** — e é
exatamente a forma que o resto da série usa.

O próprio `8.7-t2002-importar.sh` avisa por que a lacuna é perigosa:

```text
# Ao usar este roteiro, SEMPRE conferir o controle positivo contra a imagem
# original: um import recusado grava só as não-idempotências conhecidas, e duas
# recusas produzem imagens idênticas -- o que se lê como "os dois lados
# concordam" quando na verdade os dois falharam.
```

## Causa raiz

O item foi dado por fechado quando a **explicação** ficou correta (o port grava
52, o oráculo x64 é que está torto). Explicação correta não é veredito: o que
a série mede é o que sai no disco quando os dois lados fazem a mesma coisa.

## Correção

### Medir, em duas corridas de `golden_check.sh` em modo `gui`

1. **Exportar dos dois lados** (`8.7-t2002-exportar.sh`), guardando os dois
   arquivos, e registrar os dois tamanhos e o `cmp` do corpo — é o que já se
   sabe, e passa a ficar versionado como evidência.
2. **Importar o mesmo arquivo de 52 bytes nos dois lados**
   (`8.7-t2002-importar.sh`, com `PAR_T2002` em caminho Windows para o oráculo
   e POSIX para o port — os dois hooks recebem textos diferentes, que é o que o
   `GOLDEN_EDIT`/`GOLDEN_GUI_EDIT` permite), gravar e comparar. **Com controle
   positivo em cada lado**, pela armadilha que o cabeçalho do roteiro descreve.

O veredito esperado é `OK`; se não for, é achado e vira CORR nova.

### Registrar

O item 5 da §8.7 e o da PAR-TASK-06 passam a trazer a faixa e o veredito, como
os outros quatro. Se o `.t2002` do **oráculo** (56 bytes) continuar não sendo
importável por lado nenhum, isso fica escrito como resultado — assimetria do
oráculo, já explicada pela CORR-WTE-132 —, não como item conferido.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PARIDADE-FUNCIONAL.md` | modificar — o item 5 da §8.7, com faixa e veredito |
| `docs/tasks/PAR-TASK-06.md` | modificar — o item 5 e o Log |
| `tools/par/8.7-t2002-importar.sh` | modificar, se a corrida exigir ajuste de caminho |

## Verificação

- [ ] Existe uma corrida de `golden_check.sh` para o import do `.t2002`, com
      saída citada
- [ ] Cada lado tem controle positivo contra a imagem original, e ele **não**
      sai vazio nem só com as não-idempotências conhecidas
- [ ] O item 5 dos dois documentos cita comando, faixa e veredito
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
