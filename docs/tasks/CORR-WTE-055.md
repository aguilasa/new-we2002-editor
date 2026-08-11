---
id: CORR-WTE-055
title: "Correção: a WTE-TASK-24 chama de 322 os imports de `rtl60`/`vcl60`, e eles são 267"
type: correção
category: engenharia-reversa
status: pendente
depends_on: []
---

# CORR-WTE-055: 322 é o total de imports, não o das duas BPLs — e o Log da própria task diz 267

## Problema identificado

A seção **"4. Os imports já vêm nomeados — aproveitar"** do enunciado da
[WTE-TASK-24](/docs/tasks/24-ghidra-convencao-borland.md) diz:

> **Vantagem que compensa a §8.2:** os **322 imports** de `rtl60.bpl`/`vcl60.bpl`
> chegam com nome mangled […] São **322** pontos de referência gratuitos.

322 é o total de imports do `.exe` — as duas BPLs são **267**. O restante são
55 das DLLs do Windows (`KERNEL32.DLL` 51, `USER32.DLL` 3, `OLEAUT32.DLL` 1),
que não vêm com nome mangled da VCL e não são "ponto de referência gratuito" no
sentido que a seção quer dizer.

A distinção não é nova: a **WTE-TASK-09** já a fixou ao remedir a fase 1 — a
linha do `progresso.md` diz *"Imports | 322, sendo 267 de `rtl60.bpl`/`vcl60.bpl`
— corrigido"*. E o **Log desta mesma task** traz o valor certo:

> | Imports `rtl60.bpl` + `vcl60.bpl` | 103 + 164 = **267**, 1 sem nome legível |

Ou seja: o arquivo se contradiz entre o enunciado e o Log, e o enunciado repete
a atribuição que a fase 1 já tinha corrigido.

## Evidência

Medido nesta revisão, rodando `run_headless.sh` do zero:

```
apply_names: imports de KERNEL32.DLL: 51
apply_names: imports de OLEAUT32.DLL: 1
apply_names: imports de RTL60.BPL: 103
apply_names: imports de USER32.DLL: 3
apply_names: imports de VCL60.BPL: 164
apply_names: imports sem nome legivel: 1
```

`103 + 164 = 267` das duas BPLs; `51 + 3 + 1 = 55` do Windows; `267 + 55 = 322`
no total — o que explica de onde veio a confusão.

## Causa raiz

O enunciado foi escrito antes da WTE-TASK-09 e atribuiu o total às duas BPLs;
a execução mediu certo e não voltou para corrigir a seção 4.

## Correção

### Arquivo: `docs/tasks/24-ghidra-convencao-borland.md`

Trocar, na seção 4, `322` por `267` nas duas ocorrências, dizendo que 322 é o
total e que 55 são das DLLs do Windows. O argumento da seção não muda — 267
pontos de referência gratuitos continuam sendo a vantagem que ela descreve.

Vale conferir de passagem se o número aparece com a mesma atribuição em outro
lugar:

```bash
grep -rn "322" docs/ wte/re/ | grep -i import
```

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/24-ghidra-convencao-borland.md` | modificar |

## Verificação

- [ ] a seção 4 diz 267 para as duas BPLs, e 322 só como total
- [ ] enunciado e Log da mesma task dizem o mesmo número
- [ ] `python3 wte/tools/check_fase1.py --check` verde
- [ ] `make -C wte check` verde

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
