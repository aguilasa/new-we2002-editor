---
id: CORR-WTE-022
title: "Correção: o comando publicado da ordem de auto-create devolve 17 das 18 classes, e a que ele perde é TMainForm"
type: correção
category: engenharia-reversa
status: pendente
depends_on: []
---

# CORR-WTE-022: a receita de reprodução da ordem de auto-create perde o primeiro formulário

## Problema identificado

A WTE-TASK-11 sustenta a decisão mais estrutural que tomou — a ordem em que
`CriaFormularios` cria os 18 formulários — numa medida do binário, e publica o
comando que a reproduz. O comando está em **dois** lugares, palavra por palavra:
o Log da task (linhas 115-118) e o cabeçalho de
[`wte/src/wtemain.pas`](../../wte/src/wtemain.pas) (linhas 21-22), sob o título
"Reproduzir a medida".

```sh
objdump -d -M intel we-team-editor/we-team-editor.exe \
  | sed -n '/401a2e:/,/401bc6:/p' | grep -E 'mov +(ecx|edx),DWORD PTR ds:'
```

Ele **não reproduz a medida**. Devolve 17 classes, não 18, e a que falta é a
primeira: `TMainForm`.

A causa é o começo da faixa. `0x401a2e` é o endereço da **chamada** do primeiro
`CreateForm`; os dois `mov` que carregam os operandos desse sítio estão
**antes**, em `0x401a22` e `0x401a28`. A faixa `401a2e..401bc6` cobre as 18
chamadas — a prosa "chama `Application->CreateForm` 18 vezes entre `0x401a2e` e
`0x401bc6`" está certa —, mas cobre só 17 pares de operandos, porque corta o
primeiro pelo meio.

A ordem escrita em `CriaFormularios` **está correta**: esta revisão resolveu as
17 pelo `vmtClassName` e elas são exatamente os itens 2 a 18 da lista do código,
na mesma sequência. O defeito é da receita, não do resultado — e é o pior tipo,
porque quem reexecutar o comando vai achar 17, não achar `TMainForm`, e concluir
que a lista do código tem um item a mais que o binário não justifica.

## Evidência

O que o comando publicado devolve:

```
$ objdump -d -M intel we-team-editor/we-team-editor.exe \
  | sed -n '/401a2e:/,/401bc6:/p' | grep -cE 'mov +edx,DWORD PTR ds:'
17
```

Resolvendo cada `edx` pelo `vmtClassName` (o mesmo `-44` do `dump_published.py`):

```
   1 Testrategia              10 Tficha_about
   2 Tjugador                 11 Tficha_error2
   3 Tficha_dorsal            12 Tficha_salida
   4 Tficha_enlaza            13 Tficha_info4
   5 Tficha_color             14 Tficha_info3
   6 Tficha_info              15 Tficha_movertodos
   7 Tficha_warning           16 Tficha_creditos_equipo
   8 Tficha_error             17 Tficha_warning_2
   9 Tficha_info2
```

São os itens **2 a 18** de `CriaFormularios`. O sítio que a faixa corta:

```
  401a22:	8b 0d d0 2d 43 00    	mov    ecx,DWORD PTR ds:0x432dd0
  401a28:	8b 15 88 7d 42 00    	mov    edx,DWORD PTR ds:0x427d88
  401a2e:	e8 8d 0c 02 00       	call   0x4226c0        <-- a faixa comeca AQUI
```

e `ds:0x427d88`, resolvido, é `TMainForm`.

Com a faixa começando um sítio antes, fecha:

```
$ objdump -d -M intel we-team-editor/we-team-editor.exe \
  | sed -n '/401a22:/,/401bc6:/p' | grep -cE 'mov +edx,DWORD PTR ds:'
18
```

E a contagem de chamadas, que a prosa afirma, confere na faixa original:

```
$ objdump -d -M intel we-team-editor/we-team-editor.exe \
  | sed -n '/401a2e:/,/401bc6:/p' | grep -cE 'call +0x4226c0'
18
```

## Causa raiz

A faixa do `sed` foi escrita com o endereço da **chamada** do primeiro
`CreateForm`, e o `grep` seguinte procura os **operandos**, que num sítio de
`call` vêm antes dela.

## Correção

### Arquivo: `wte/src/wtemain.pas`

No cabeçalho, trocar `401a2e` por `401a22` na faixa do `sed` e dizer por que os
dois endereços são diferentes — senão o próximo leitor "corrige" de volta:

```
    objdump -d -M intel we-team-editor/we-team-editor.exe \
      | sed -n '/401a22:/,/401bc6:/p' | grep -E 'mov +(ecx|edx),DWORD PTR ds:'

  A faixa comeca em 0x401a22, nao em 0x401a2e: as 18 CHAMADAS de CreateForm
  vao de 0x401a2e a 0x401bc6, mas os dois `mov` que carregam os operandos de
  cada sitio vem ANTES da chamada dele. Comecando na chamada, o primeiro par
  fica de fora e a saida traz 17 classes, sem TMainForm.
```

### Arquivo: `docs/tasks/11-app-com-a-casca-completa.md`

Mesma correção no bloco do Log, com a mesma justificativa em uma linha.

**Verificar antes de fechar** se o mesmo padrão aparece em outro lugar: qualquer
faixa de `sed` escrita a partir de endereço de `call` e consumida por `grep` de
operando tem o mesmo defeito.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/src/wtemain.pas` | modificar (cabeçalho) |
| `docs/tasks/11-app-com-a-casca-completa.md` | modificar (Log) |

## Verificação

- [ ] o comando corrigido devolve 18 pares:
      `objdump -d -M intel we-team-editor/we-team-editor.exe | sed -n '/401a22:/,/401bc6:/p' | grep -cE 'mov +edx,DWORD PTR ds:'`
- [ ] as 18 classes resolvidas pelo `vmtClassName` batem, **na ordem**, com os
      18 `Application.CreateForm` de `CriaFormularios`
- [ ] `grep -n "401a2e" wte/src/wtemain.pas docs/tasks/11-app-com-a-casca-completa.md`
      só acha o endereço onde ele é o das chamadas, nunca o do `sed`
- [ ] `lazbuild -B wte/wte.lpi` compila (a mudança é de comentário, mas o
      arquivo é fonte)
- [ ] `python3 wte/tools/dfm2lfm.py --check` verde — `wtemain.pas` não é gerado
      e a correção não pode ter tocado em nada que seja
- [ ] `we-team-editor.exe` e `roms/` intocados

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
