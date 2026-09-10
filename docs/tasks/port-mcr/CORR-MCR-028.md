---
id: CORR-MCR-028
title: "Correção: o mapa diz que três imagens de roms/ declaram SLPM-87056, e são cinco"
type: correção
category: dados
status: pendente
depends_on: []
---

# CORR-MCR-028: são cinco as imagens que declaram `SLPM-87056`

## Problema identificado

[`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md):3 abre dizendo que a
medição é

> sobre a release japonesa `SLPM-87056` (as três imagens de `roms/` declaram
> esse código)

São **cinco** arquivos em `roms/` que declaram o código, e a lista importa
porque é ela que diz sobre qual imagem um resultado vale: a European Deluxe —
que os golden tests do `newWe2002` usam como imagem canônica — é uma delas, e
não é intuitivo.

## Evidência

```
roms/golden-european-deluxe.bin            SLPM_870.56
roms/japanese-shift-jis.bin                SLPM_870.56
roms/we2002-pt-br.bin                      SLPM_870.56
roms/ptbr-remaster.bin                     SLPM_870.56
roms/we2002-english/we2002-english.bin     SLPM_870.56
```

(`head -c 400000 <img> | strings -n 8 | grep -oE 'SLPM_?[0-9._]{5,}'`, leitura
pura.)

## Causa raiz

A frase contou as imagens que a task usou — a inglesa e as duas PT-BR — como se
fossem todas as que carregam o código.

## Correção

### Arquivo: `docs/MCR-DESBLOQUEIOS.md`

Dizer **cinco**, ou — melhor — nomear as duas que a medição usou
(`we2002-english/we2002-english.bin` e `we2002-pt-br.bin`) e deixar o código
como o que elas declaram, sem afirmar quantas mais o declaram.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/MCR-DESBLOQUEIOS.md` | modificar |

## Verificação

- [ ] a varredura de `SLPM_870.56` sobre `roms/` e a frase do doc dizem o mesmo
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
