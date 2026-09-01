---
id: CORR-WTE-116
title: "Correção: o controle do `trace.log` diz \"mkdir re ao lado da cópia\", e ao lado da cópia não funciona"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-116: o `re/` vai um nível **acima** do binário, não ao lado dele

## Problema identificado

A [WTE-TASK-38](/docs/tasks/concluidos/38-nome-e-linhagem.md) achou um defeito real — o
binário copiado para fora de `wte/build/` morre num diálogo da LCL antes de
qualquer janela, porque o `Rewrite` do log de trace levanta `EInOutError` — e
registrou o **controle** que separa essa causa da hipótese errada ("é a pasta
de assets"). O controle está escrito em **três** lugares, com a mesma frase:

> **Controle:** `mkdir re` **ao lado da cópia**, e o mesmo binário abre a
> janela principal (522×475) e escreve o `trace.log` ali.

*(Log da WTE-TASK-38 linha 154, e os repasses na
[WTE-TASK-39](/docs/tasks/concluidos/39-empacotamento.md) linha 153 e na
[WTE-TASK-40](/docs/tasks/concluidos/40-verificacao-final.md) linha 111 — e a 39 é
justamente quem vai consertar o defeito.)*

**Ao lado da cópia não funciona.** O caminho que o
[`retrace.pas`](../../../wte/src/retrace.pas) monta é

```pascal
Dir := ExtractFilePath(ParamStr(0));
Result := IncludeTrailingPathDelimiter(Dir) + '../re/trace.log';
```

— ou seja, `re/` tem de ser **irmão do diretório do executável**, não irmão do
executável. O comentário três linhas acima diz exatamente isso (*"o binário
vive em `wte/build/`; o log vai para `wte/re/`"*), então a frase do controle
contradiz o código que ela mesma cita.

Quem seguir a receita ao pé da letra cria o diretório no lugar errado, vê o
mesmo diálogo, e conclui que a causa **não** era o trace — que é a hipótese
errada de volta, pela porta que o controle existia para fechar. A
[WTE-TASK-39](/docs/tasks/concluidos/39-empacotamento.md) é a dona do conserto e a
[WTE-TASK-40](/docs/tasks/concluidos/40-verificacao-final.md) tem a condição 3 esperando
por ele: as duas leem essa frase.

## Evidência

Medido em 2026-08-25, com o binário de `wte/build/wte` copiado para um
diretório limpo em `/tmp` e o `:98` vazio antes de cada corrida.

**Sem `re/` nenhum** — o diálogo da LCL, e nenhuma janela principal:

```text
0x20009c "WE2002 - Lazarus Editor": ("wte" "Wte")  362x144+459+440
```

**Com `re/` ao lado da cópia** (`$D/wte` e `$D/re/`), que é a receita como está
escrita — **o mesmo diálogo**, e o `re/` continua vazio:

```text
0x40009c "WE2002 - Lazarus Editor": ("wte" "Wte")  362x144+459+440
```

**Com `re/` um nível acima** (`$D/sub/wte` e `$D/re/`), que é o que o código
pede:

```text
0x200166 " W11 Team Editor PT by chagas_michel! [Lazarus]": ("wte" "Wte")  522x475+132+72
-rw-rw-r-- 1 ingmar ingmar  605 ago 25 19:21 trace.log
```

| Layout | Janela que aparece | `trace.log` |
|---|---|---|
| só o binário | diálogo 362×144 | não |
| `re/` **ao lado** do binário | diálogo 362×144 | não |
| `re/` **um nível acima** | principal **522×475** | **605 B** |

O diagnóstico da task está certo; o que erra é a receita de reproduzi-lo.

## Causa raiz

A frase do controle descreve o `re/` pela posição do **arquivo** (`ao lado da
cópia`) e o código o resolve pela posição do **diretório** (`<dir>/../re`).

## Correção

### Arquivos: `docs/tasks/concluidos/38-nome-e-linhagem.md`, `39-empacotamento.md` e `40-verificacao-final.md`

Trocar a frase nos três pelo layout, que não admite leitura dupla:

> **Controle:** com o binário em `<algum>/sub/wte`, criar `<algum>/re/` — o
> `retrace.pas` resolve `<dir do executável>/../re/trace.log`, então o `re/`
> é irmão **do diretório** do binário, como `wte/re/` é irmão de `wte/build/`.
> Feito isso, o mesmo binário abre a janela principal (522×475) e escreve o
> `trace.log` lá.

Vale acrescentar a alternativa de uma linha, que é a que alguém usaria na
prática e não depende de layout nenhum:

```sh
WTE_TRACE_FILE=/tmp/trace.log ./wte
```

Ela existe no `ResolveArquivo` como primeira opção e responde à mesma pergunta
sem criar diretório — e serve de segunda evidência, porque isola o trace de
qualquer coisa relacionada a assets.

### O conserto continua sendo da WTE-TASK-39

Esta correção é só da receita. O defeito — binário que não abre depois de
movido — é da 39, que é dona da resolução em runtime, e a linha já está lá.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/concluidos/38-nome-e-linhagem.md` | modificar |
| `docs/tasks/concluidos/39-empacotamento.md` | modificar |
| `docs/tasks/concluidos/40-verificacao-final.md` | modificar |

## Verificação

- [x] `grep -rn "ao lado da cópia" docs/tasks/` sai vazio — fora deste arquivo
      e do índice, que a citam para a descrever
- [x] A receita nova, seguida ao pé da letra, abre a janela **522×475** e
      escreve o `trace.log` (**605 B**)
- [x] `WTE_TRACE_FILE=/tmp/trace.log ./wte` abre a janela sem criar diretório —
      medido, mesma janela e mesmos 605 B
- [x] `make -C wte check` verde (858 testes)
- [x] `roms/` intocada; nada foi copiado para `work/`

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-25

**Resumo do que foi feito:**

A frase do controle foi trocada nos três sítios pelo **layout**, que não admite
leitura dupla: com o binário em `<algum>/sub/wte`, criar `<algum>/re/` — o
`re/` é irmão **do diretório** do binário, como `wte/re/` é irmão de
`wte/build/`. Nos três entrou também a versão de uma linha,
`WTE_TRACE_FILE=/tmp/trace.log ./wte`, que não depende de layout nenhum e serve
de segunda evidência porque isola o trace de qualquer coisa de assets.

Reproduzido antes de corrigir, nos **quatro** layouts:

| Layout | Janela | `trace.log` |
|---|---|---|
| só o binário | diálogo 362×144 | não |
| `re/` irmão do **arquivo** — a receita como estava | diálogo 362×144 | não |
| `re/` irmão do **diretório** | principal **522×475** | **605 B** |
| `WTE_TRACE_FILE`, sem `re/` | principal **522×475** | **605 B** |

E a receita nova foi seguida **ao pé da letra**, como se fosse a primeira vez:
janela 522×475 e os mesmos 605 B. É o que a correção existe para garantir — uma
receita que não se reproduz não é controle, é hipótese com aparência de método.

**Problemas encontrados:**

**As notas históricas quase deixaram o grep de verificação vermelho.** Escrevi
primeiro *"a frase daqui dizia `mkdir re` ao lado da cópia até…"*, que é a forma
que este repositório usa para não reescrever história — e ela deixa a string
viva em três lugares, contra o item de verificação que pede o grep vazio.

Reescritas nomeando o **engano** em vez de repetir a frase: *"punha o `re/`
irmão do **arquivo**, e o código o resolve irmão do **diretório**"*. Satisfaz o
grep e diz mais — quem lê aprende qual é a distinção, que é justamente o que a
frase velha escondia.

O conserto do defeito continua sendo da
[WTE-TASK-39](/docs/tasks/concluidos/39-empacotamento.md), dona da resolução em runtime;
esta correção é só da receita.

**Arquivos criados/modificados:**

- `docs/tasks/concluidos/38-nome-e-linhagem.md` — o controle, com o layout e a alternativa
- `docs/tasks/concluidos/39-empacotamento.md` — idem, no repasse
- `docs/tasks/concluidos/40-verificacao-final.md` — idem, na condição 3
