---
id: CORR-LOOKS-051
title: "Correção: o `looks_live` perde a sessão MCP no primeiro `pause`, uma vez em catorze corridas"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-LOOKS-051: `missing or invalid MCP-Session-Id` logo depois de o emulador subir

## Problema identificado

A [`LOOKS-TASK-19`](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md) registrou o
`oracle.py --check-live` como o alvo `looks_live`. Na primeira corrida pelo
`ctest`, logo depois do `looks_ui`, o emulador subiu, o servidor MCP respondeu
ao `initialize`, a janela saiu da tela — e a **primeira** chamada de ferramenta,
o `pause` do `Oracle.__enter__`, voltou HTTP 400 com a sessão recusada.

Nas outras treze corridas, as mesmas duas variáveis e a mesma máquina, o alvo
passou: dez diretas (`oracle.py --check-live`, uma antes e nove depois) e três
pelo `ctest`, estas em 8,3 s cada. **Um vermelho em catorze, e não
reproduzido.**

O defeito é de sentido único: o alvo fica **vermelho à toa**, nunca verde à
toa. Mas um gate que falha sem causa uma vez em catorze ensina quem o lê a
rodar de novo até passar, e esse hábito é o que deixa passar o vermelho de
verdade.

**Um segundo defeito saiu da mesma corrida, e já está consertado** no commit do
LOOKS-TASK-19: a exceção dentro do `__enter__` não passa pelo `__exit__`, e o
emulador ficou rodando depois de o `ctest` terminar. Ele agora é derrubado ali
mesmo — conferido plantando uma falha no `pause`, com zero processos
DuckStation depois. O que esta correção trata é só a sessão perdida.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=<japonesa> WE2002_LOOKS_DRIVE_IMAGE=<inglesa .cue> \
    ctest --test-dir <build> -R looks
4/4 Test #13: looks_live .......................***Failed    3.04 sec

  fork 25468 on this desktop, log C:\games\ps1\work\duckstation-fork.log
  window 855082
  duckstation-mcp 1.0.0 answering
  window moved off the visible desktop
Traceback (most recent call last):
  ...
  File "C:\github\new-we2002-editor\tools\looks\oracle.py", line 564, in pause
    self.client.call("pause")
  File "C:\github\new-we2002-editor\tools\pes2\mcp.py", line 117, in _post
    raise ToolError(f"HTTP {e.code} from the server: {detail}") from None
mcp.ToolError: HTTP 400 from the server: {"jsonrpc":"2.0","id":2,"error":{"code":-32600,"message":"Bad Request: missing or invalid MCP-Session-Id"}}
```

O `id` 2 é a primeira chamada depois do `initialize`: o servidor aceitou o
handshake e, um pedido depois, não reconhecia mais a sessão. O
`duckstation-fork.log` daquela subida tem só a linha de `=== launch ===`.

## Causa raiz

**Não medida.** Duas hipóteses, e nenhuma foi separada da outra:

1. **Outro cliente na mesma porta.** Esta máquina tem um servidor MCP
   `duckstation` configurado no editor, apontado para a mesma porta do fork,
   que tenta reconectar sozinho. Se o servidor guarda uma sessão só, o
   `initialize` de outro cliente entre o nosso `initialize` e o `pause`
   invalida a nossa — e isso casa com a raridade.
2. **O servidor reinicia a sessão na subida**, por exemplo quando o
   `Automatic Updater` é dispensado depois de a porta já ter aberto — que o
   `CLAUDE.md` registra como a ordem medida em 2026-09-03.

## Correção

### Arquivo: `tools/looks/oracle.py` (e, se a causa for a 1, a receita do perfil)

Primeiro **separar as hipóteses**: repetir o `--check-live` em laço com o
cliente MCP do editor desligado e depois ligado, e contar. Se a causa for outro
cliente, a correção é de ambiente e se escreve como armadilha no
[`perfil-looks.md`](/docs/prompts/perfil-looks.md) — e o `Oracle` pode refazer o
`initialize` **uma vez** diante de `invalid MCP-Session-Id`, dizendo que o
fez. Se for a subida, a espera do `fork.launch` precisa terminar depois do
diálogo, e aí o arquivo é o `tools/pes2/fork.py`, de outro projeto, com o
`pes2_selftest` verde no critério.

Refazer a chamada em laço até passar **não** é correção: é o hábito que este
arquivo existe para não criar.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/oracle.py` | a nova tentativa de sessão, se a medição a justificar |
| `docs/prompts/perfil-looks.md` | a armadilha, se a causa for de ambiente |

## Verificação

- [x] As duas hipóteses separadas por contagem, com o número no Log
- [x] `ctest -R looks_live` em laço sem vermelho sem causa, com o número de
      corridas no Log

## Log de Execução

**Executado em:** 2026-09-17

### Resumo do que foi feito

O vermelho não se reproduz por leitura — uma vez em catorze —, então a evidência
desta correção é a medição que ela pede.

**Separar as hipóteses.** Em vez de ligar e desligar o cliente MCP do editor e
esperar a coincidência, o mecanismo da hipótese 1 foi **provocado**: um
`Oracle` de pé, três chamadas, um segundo cliente (`mcp.Client`) faz
`initialize` na mesma porta, e o primeiro chama de novo. Três corridas:

```text
== run 1
A session e29560d8c8ee2259fd540d6b73fc023e
A alone, 1st ok
A alone, 2nd ok
A alone, 3rd ok
B session 6c7f54fb8756ece581379f5f5084929c same as A: False
A after B FAILED HTTP 400 from the server: {"jsonrpc":"2.0","id":6,"error":{"code":-32600,"message":"Bad Request: missing or invalid MCP-
B ok
A again FAILED HTTP 400 from the server: {"jsonrpc":"2.0","id":7,"error":{"code":-32600,"message":"Bad Request: missing or invalid MCP-
== run 2   (idêntico: A ok x3, A depois de B FAILED, B ok, A de novo FAILED)
== run 3   (idêntico)
```

- **Hipótese 1, medida: 3 de 3.** O servidor guarda **uma** sessão; o
  `initialize` de outro cliente invalida a anterior com **exatamente** o erro da
  corrida vermelha, e toda chamada seguinte falha. O `.mcp.json` do repositório
  registra o fork na porta 2346 no escopo do projeto, e é essa a entrada que o
  editor tenta conectar — nesta sessão ela aparece como servidor `duckstation`
  que falhou ao conectar.
- **Hipótese 2, sem sustentação:** nas três subidas, as três primeiras chamadas
  logo depois do `fork.launch` passaram, e nas quinze corridas do laço abaixo
  nenhuma perdeu a sessão. A subida não reinicia a sessão por conta própria.

**O conserto** é o que a CORR previa para a causa 1: `oracle.OneSession`
embrulha o cliente do fork no `Oracle.__enter__`; diante de
`invalid MCP-Session-Id` refaz o `initialize` **uma vez**, imprime
`MCP session taken by another client on the port -- initialised again before
<chamada>`, e repete **a mesma** chamada — que o servidor recusou antes de
executar. Perder de novo logo depois do novo handshake **falha**. Qualquer outra
recusa passa direto. `tools/pes2/fork.py` e `mcp.py` não foram tocados.

Ao vivo, com um segundo cliente de propósito:

```text
A alone ok
B took the port
  MCP session taken by another client on the port -- initialised again before pause (1 time(s) this run)
A after B ok, renewed 1
A again ok, renewed 1
no DuckStation is running
```

### Gates

```text
# 15 x ctest --test-dir <build-looks19> -R looks_live   (aponta para esta árvore)
run 1 exit=0 looks_live .......................   Passed    8.53 sec renewed=0
run 2 exit=0 looks_live .......................   Passed    8.67 sec renewed=0
run 3 exit=0 looks_live .......................   Passed    8.40 sec renewed=0
run 4 exit=0 looks_live .......................   Passed    8.44 sec renewed=0
run 5 exit=0 looks_live .......................   Passed    8.38 sec renewed=0
run 6 exit=0 looks_live .......................   Passed    8.84 sec renewed=0
run 7 exit=0 looks_live .......................   Passed    8.28 sec renewed=0
run 8 exit=0 looks_live .......................   Passed    8.26 sec renewed=0
run 9 exit=0 looks_live .......................   Passed    8.57 sec renewed=0
run 10 exit=0 looks_live .......................   Passed    8.48 sec renewed=0
run 11 exit=0 looks_live .......................   Passed    8.37 sec renewed=0
run 12 exit=0 looks_live .......................   Passed    8.39 sec renewed=0
run 13 exit=0 looks_live .......................   Passed    8.40 sec renewed=0
run 14 exit=0 looks_live .......................   Passed    8.36 sec renewed=0
run 15 exit=0 looks_live .......................   Passed    8.45 sec renewed=0
no DuckStation is running

$ python tools/looks/oracle.py --check
oracle.py: 0 failure(s)
$ python tools/looks/controls.py --only oracle-session-never-renewed
  RED    oracle-session-never-renewed oracle.py :: OneSession.call
$ python tools/looks/selftest.py --quiet
  ..... 64 of 64 controls red
looks_selftest: 0 failure(s)
```

`roms/` intocada; os dois save states só carregados; nenhum DuckStation de pé
depois de cada corrida.

### Problemas encontrados

- **O laço não reproduz o vermelho, e isso é esperado:** o segundo cliente só
  aparece quando o editor tenta reconectar. O que prova a causa é a sonda
  provocada, 3 de 3; o laço prova que o conserto não pinta vermelho à toa nem
  renova sem motivo (`renewed=0` em 15).
- A verificação pedia "cliente do editor desligado e depois ligado". Ligar e
  desligar o cliente do editor é configuração da máquina do usuário; a sonda
  com um segundo cliente de propósito isola o mesmo mecanismo sem mexer nela.

### Arquivos criados/modificados

- `tools/looks/oracle.py` — `SESSION_LOST`, `OneSession`, o embrulho no
  `__enter__`, quatro casos no `self_check()` com servidor falso
- `tools/looks/controls.py` — `oracle-session-never-renewed`
- `docs/prompts/perfil-looks.md` — armadilha 32
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
