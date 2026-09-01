---
id: CORR-WTE-056
title: "Correção: três sítios ainda mandam rodar `apply_names.py`, e o script é `.java`"
type: correção
category: engenharia-reversa
status: concluído
depends_on: []
---

# CORR-WTE-056: o procedimento para refazer o projeto Ghidra cita um arquivo que não existe

## Problema identificado

A WTE-TASK-24 trocou os scripts de Ghidra de Python para Java, com razão medida
(o Ghidra 12 largou o Jython; `.py` exigiria `pip install pyghidra` mais JPype),
e o enunciado foi corrigido. **Três sítios ficaram para trás**, os dois piores
no documento cuja função é justamente permitir refazer tudo:

```
$ grep -rn "apply_names\.py" wte/tools/ghidra/
wte/tools/ghidra/borland_cc.md:94:   Directories*, e rodar `apply_names.py` com a raiz do repositório como
wte/tools/ghidra/borland_cc.md:107:O `apply_names.py` **aborta** se o cspec não for `borlandcpp`:
wte/tools/ghidra/run_headless.sh:7:# `apply_names.py`, que juntos reconstroem o projeto inteiro em um comando.
```

O arquivo é `wte/tools/ghidra/apply_names.java`. Não existe `apply_names.py` na
árvore.

O `borland_cc.md` é *"o procedimento, para refazer"* — a task o criou porque o
banco do Ghidra não é versionado e o projeto tem de poder ser remontado do zero.
Quem seguir o passo 94 na GUI procura um `.py` que não está lá, e a linha 107
descreve a guarda do cspec — que **existe e funciona**, verificada nesta revisão
— apontando para o arquivo errado.

## Evidência

O que existe:

```
$ ls wte/tools/ghidra/
apply_names.java  borland_cc.md  decompile_one.java  run_headless.sh  vmt_probe.java
```

A guarda citada na linha 107 é real, e foi exercitada nesta revisão importando o
`.exe` com o cspec errado:

```
$ analyzeHeadless … -cspec borlanddelphi … -postScript apply_names.java …
apply_names.java> apply_names: ABORTADO: cspec e 'borlanddelphi', nao 'borlandcpp'.
  Com outro cspec o Ghidra assume __cdecl, e o C++Builder
  Reimporte com: -processor x86:LE:32:default -cspec borlandcpp
```

Ou seja: o comportamento descrito está certo; o nome do arquivo é que não.

## Causa raiz

A troca de `.py` por `.java` alcançou o enunciado da task e os arquivos, e não a
prosa do `borland_cc.md` nem o cabeçalho do `run_headless.sh`.

## Correção

### Arquivos: `wte/tools/ghidra/borland_cc.md` e `wte/tools/ghidra/run_headless.sh`

Trocar `apply_names.py` por `apply_names.java` nos três sítios. No
`borland_cc.md`, o passo da GUI merece a frase que o Log da task já tem: o
`analyzeHeadless` **compila GhidraScript em Java sozinho**, com o JDK do
`launch.properties`, e é por isso que não há dependência nova — quem for refazer
pela GUI precisa saber que o `.java` roda igual.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/ghidra/borland_cc.md` | modificar |
| `wte/tools/ghidra/run_headless.sh` | modificar |

## Verificação

- [ ] `grep -rn "apply_names\.py" .` não devolve nada fora de documento que
      **narre** a troca (o Log da WTE-TASK-24 e esta CORR)
- [ ] todo script citado nos dois arquivos existe em `wte/tools/ghidra/`
- [ ] `bash wte/tools/ghidra/run_headless.sh` continua reconstruindo o projeto
- [ ] `make -C wte check` verde

## Log de Execução

**Executado em:** 2026-08-11

**Resumo do que foi feito:**

`apply_names.py` → `apply_names.java` nos três sítios: o passo 5 da GUI e a
seção da guarda de cspec, no `borland_cc.md`, e o cabeçalho do
`run_headless.sh`. No passo da GUI entrou a frase que faltava — o
`analyzeHeadless` **compila GhidraScript em Java sozinho**, com o JDK do
`launch.properties`, então `.java` não pede instalação nenhuma; era o argumento
que justificou a troca e que quem refizesse pela GUI não tinha.

O procedimento foi exercitado inteiro, não só relido:

```
$ bash wte/tools/ghidra/run_headless.sh
REPORT: Analysis succeeded for file: …/we-team-editor.exe
apply_names: cspec=borlandcpp, convencao default=__fastcall
apply_names: handlers -- 42 criada(s), 54 renomeada(s), 0 ja ok
apply_names: tabela de offsets -- 80 rotulo(s) em dados, 6 comentario(s) em codigo
apply_names: ok
```

E o `vmt_probe.java` foi rodado **contra esse banco recém-reconstruído**: 217
chamadas, 189 com campo, e a votação da [CORR-WTE-054](/docs/tasks/concluidos/CORR-WTE-054.md)
devolvendo os mesmos 108 votos, 69 candidatos e 4 votos no primeiro colocado.
O `borland_cc.md` promete "refazer do zero", e é isso que refazer do zero
significa.

`grep -rn "apply_names\.py" .` só devolve documento que **narra** a troca — os
"Problemas encontrados" da WTE-TASK-24 e esta CORR —, como a verificação pede.

**Problemas encontrados:** Nenhum.

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `wte/tools/ghidra/borland_cc.md` | modificado — os dois sítios, mais o porquê de `.java` bastar |
| `wte/tools/ghidra/run_headless.sh` | modificado — o cabeçalho |
| `docs/tasks/concluidos/CORR-WTE-056.md` | `status: concluído` e este Log |
| `docs/tasks/concluidos/correcoes-progresso.md` | `[x]` na tabela e no checklist |
