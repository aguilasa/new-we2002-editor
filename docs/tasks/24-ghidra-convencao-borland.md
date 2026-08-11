---
id: WTE-TASK-24
title: "Ghidra com a convenção Borland — e os VMTs da VCL"
type: infra
category: engenharia-reversa
phase: 4
depends_on: ["WTE-TASK-04", "WTE-TASK-06"]
status: concluído
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

> **Medido na execução: não é preciso definir nada.** O Ghidra 12.1.2 traz
> `x86borland.cspec`, onde `__fastcall` `EAX/EDX/ECX` é o `<default_proto>`.
> Basta importar com `-cspec borlandcpp`. Ver o Log e `borland_cc.md`.

### 2. Nomear as 96 funções

Importar `published_methods.tsv` e aplicar os nomes. Um script de Ghidra que lê
o TSV é preferível a fazer à mão — 96 renomeações à mão não sobrevivem a
reimportar o binário.

> **Medido na execução: o script é `.java`, não Python.** O Ghidra 12 largou o
> Jython, e `.py` exigiria `pip install pyghidra` + JPype. Ver o Log.

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
| `wte/tools/ghidra/apply_names.java` | criar — **Java**, não Python; ver o Log |
| `wte/tools/ghidra/decompile_one.java` | criar — a prova da assinatura |
| `wte/tools/ghidra/vmt_probe.java` | criar — a medida da §8.2 |
| `wte/tools/ghidra/run_headless.sh` | criar — refaz o projeto num comando |
| `wte/tools/ghidra/borland_cc.md` | criar — o procedimento, para refazer |
| `wte/re/vmt.md` | criar — a rota escolhida e o teste das cinco chamadas |

---

## Critério de conclusão

- [x] Convenção Borland aplicada a todas as funções, procedimento escrito
- [x] Os 96 nomes aplicados por script, não à mão
- [x] Tabela de offsets rotulada com os nomes do `Offsets.hpp`
- [x] Imports da VCL resolvidos por nome, conferido
- [x] Rota de VMT decidida com o teste das cinco chamadas
- [x] `colorearClick` decompilado com a assinatura correta, como prova
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-09

- **Resumo do que foi feito:**

  Projeto Ghidra reconstruível em um comando (`run_headless.sh`), com os nomes e
  rótulos da fase 1 aplicados por script, e a §8.2 medida em vez de suposta.
  Resultados, todos de ferramenta:

  | Medida | Valor |
  |---|---|
  | `cspec` / convenção default | `borlandcpp` / `__fastcall` |
  | Handlers nomeados | 96 — 42 funções criadas, 54 renomeadas |
  | Tabela de offsets | 80 rótulos em dados + 6 comentários em código |
  | Imports `rtl60.bpl` + `vcl60.bpl` | 103 + 164 = **267**, 1 sem nome legível |
  | `colorearClick` | `__fastcall`, **1 parâmetro** |
  | Chamadas virtuais no `MainForm` | 217, **189** com o campo de objeto recuperado |

  **Achado 1 — não é preciso construir convenção nenhuma.** A §8.1 descreve
  criar uma convenção customizada `EAX, EDX, ECX` e aplicá-la a todas as
  funções. O Ghidra 12.1.2 já traz `x86borland.cspec`, e lá o `__fastcall`
  `EAX/EDX/ECX` é o **`<default_proto>`** — escolher o compiler spec
  `borlandcpp` na importação já vale para todas as funções, que é literalmente
  o critério. O que a task pedia como trabalho é uma linha de linha de comando.
  Procedimento em `wte/tools/ghidra/borland_cc.md`, com a distinção
  `borlandcpp` × `borlanddelphi`, que é o engano fácil aqui.

  **Achado 2 — a inferência da §8.2 resolve metade, e a metade que falta não é
  a que o plano supunha.** Detalhe em `wte/re/vmt.md` — o campo do
  objeto sai do contexto em 189 de 217 chamadas, e dez slots de VMT cobrem as
  217. O que **não** fecha é ir do campo ao componente: a premissa era que os
  campos publicados formam corrida contígua na ordem do DFM, e a corrida existe
  (`+0x2f0` a `+0x4b0` = 113 slots de 4 bytes contra 115 componentes filhos),
  mas a **âncora** não. Tentou-se ancorar pelo dono de cada handler; o candidato
  mais votado teve 4 votos entre 108 referências, e são 69 candidatos — número
  que a CORR-WTE-054 devolveu ao `vmt_probe.java`, que agora vota sozinho
  (o `~150` desta linha era estimativa de conta feita fora) —, porque handler
  não toca
  necessariamente o próprio componente (`colorearClick` não lê `colorear`) e
  porque o aninhamento em `TGroupBox` desloca a ordem. Rota escolhida mesmo
  assim: **2**, porque a rota 1 resolveria a classe e não é a classe que falta —
  componentes da mesma classe compartilham VMT. Consequência escrita: **spec de
  handler cita `campo +0xNNN` e `slot +0xNN`, nunca nome de componente
  inferido** — nome inferido sem âncora é o ruído convincente da §8.1 uma camada
  acima.

- **Arquivos criados/modificados:**

  - `wte/tools/ghidra/run_headless.sh`, `apply_names.java`,
    `decompile_one.java`, `vmt_probe.java` — criados
  - `wte/tools/ghidra/borland_cc.md`, `wte/re/vmt.md` — criados
  - O banco do Ghidra fica em `work/ghidra/`, coberto pelo `.gitignore`

- **Problemas encontrados:**

  1. **Script de Ghidra em Python custaria uma instalação.** O enunciado pedia
     `apply_names.py`. O Ghidra 12 largou o Jython, e `.py` agora exige
     PyGhidra, que exige `pip install pyghidra` mais JPype no Python da máquina.
     O `analyzeHeadless` compila GhidraScript em **Java** sozinho, com o JDK já
     fixado no `launch.properties` — zero dependência nova, e roda igual na GUI.
     Os scripts são `.java`; o enunciado foi corrigido. A primeira tentativa em
     `.py` falhou com `Ghidra was not started with PyGhidra`, e é o que
     documenta a escolha.
  2. **Rotular só a primeira cópia da tabela deixaria 3/4 ilegível.** A tabela
     aparece **quatro vezes** na `.data` (`0x4231a0`, `0x42b750`, `0x42d244`,
     `0x42e6d4`), e três offsets confirmados só existem como imediato na
     `.text`. Rotular apenas `tabela_slot` dava 16 sítios; passar por todas as
     ocorrências de `confirmado` dá 86 — rótulo onde é dado, comentário onde é
     código, porque rótulo no meio de instrução suja a listagem. Isso também
     explica o 16 contra os 19 `confirmado`: três não moram na tabela.
  3. **A guarda do `cspec` não é zelo.** O `apply_names.java` aborta se o cspec
     não for `borlandcpp`. Aplicar os 96 nomes sobre assinaturas inferidas como
     `__cdecl` seria o pior resultado: nome bonito em cima de ruído, e quem ler
     depois confia.
