---
id: WTE-TASK-24
title: "Ghidra com a convenção Borland — e os VMTs da VCL"
type: infra
category: engenharia-reversa
phase: 4
depends_on: ["WTE-TASK-04", "WTE-TASK-06"]
status: pendente
---

# WTE-TASK-24: Ghidra configurado

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §8.1, §8.2 e §8.3.
- **A pior armadilha do projeto, e ela aparece na primeira função.**

C++Builder passa `this`/1º argumento em `EAX`, 2º em `EDX`, 3º em `ECX`. Ghidra
assume `__cdecl` por padrão e vai reportar **funções sem argumento** que
misteriosamente leem lixo, com as três primeiras variáveis fora da assinatura.

Sintoma já observado no disassembly real de `colorearClick` (`0x00410ea8`):

```asm
00410ea8:  push  ebx
00410ea9:  push  esi
00410eaa:  mov   ebx,eax        ; <-- 'this' chegando em EAX
```

**Sem a correção, a saída do decompilador é ruído convincente** — o pior tipo de
erro, porque parece certo.

---

## Objetivo

Projeto Ghidra pronto, versionável no que der, e as três facilidades ligadas.

### 1. Convenção de chamada customizada

Definir `EAX, EDX, ECX`, retorno em `EAX`, e aplicá-la a **todas** as funções —
não só às que se for ler. Escrever o procedimento, porque ele será refeito se o
projeto Ghidra se perder.

### 2. Nomear as 96 funções

Importar `published_methods.tsv` e aplicar os nomes. Um script de Ghidra
(Python/Jython) que lê o TSV é preferível a fazer à mão — 96 renomeações à mão
não sobrevivem a reimportar o binário.

### 3. Rotular a tabela de offsets

O bloco em `0x004231a0` (WTE-TASK-06) nomeado, com os nomes do `Offsets.hpp`.
Assim toda referência à tabela aparece já legível no decompilador — é o atalho
da §1.7 aplicado dentro da ferramenta.

### 4. Os imports já vêm nomeados — aproveitar

**Vantagem que compensa a §8.2:** os 322 imports de `rtl60.bpl`/`vcl60.bpl`
chegam com nome mangled, então
`call ds:[@Controls@TWinControl@CreateHandle$qqrv]` se lê direto. São 322 pontos
de referência gratuitos. Conferir que o Ghidra os resolveu, e não deixou como
endereço cru.

### 5. Chamada virtual (§8.2) — decidir a rota

```asm
mov   ecx,DWORD PTR [eax]
call  DWORD PTR [ecx+0xcc]
```

`+0xcc` é slot de VMT da VCL e o binário não diz de quem. Duas saídas:

1. **Reconstruir o VMT** a partir de `vcl60.bpl`, que está na pasta e exporta os
   nomes mangled. Trabalhoso, resolve de uma vez para todas as classes.
2. **Inferir pelo contexto** — o objeto veio de `[ebx+0x390]`, e o DFM diz qual
   componente é; `+0xcc` num `TLabel` é quase certamente `SetCaption`.

O plano recomenda começar por (2) e só investir em (1) se travar. Esta task
decide, com um teste: pegar cinco chamadas virtuais e ver se a inferência
resolve as cinco.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/ghidra/apply_names.py` | criar |
| `wte/tools/ghidra/borland_cc.md` | criar — o procedimento, para refazer |
| `wte/re/vmt.md` | criar — a rota escolhida e o teste das cinco chamadas |

---

## Critério de conclusão

- [ ] Convenção Borland aplicada a todas as funções, procedimento escrito
- [ ] Os 96 nomes aplicados por script, não à mão
- [ ] Tabela de offsets rotulada com os nomes do `Offsets.hpp`
- [ ] Imports da VCL resolvidos por nome, conferido
- [ ] Rota de VMT decidida com o teste das cinco chamadas
- [ ] `colorearClick` decompilado com a assinatura correta, como prova
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
