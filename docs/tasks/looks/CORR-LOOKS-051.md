---
id: CORR-LOOKS-051
title: "Correção: o `looks_live` perde a sessão MCP no primeiro `pause`, uma vez em catorze corridas"
type: correção
category: verificação
status: pendente
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

- [ ] As duas hipóteses separadas por contagem, com o número no Log
- [ ] `ctest -R looks_live` em laço sem vermelho sem causa, com o número de
      corridas no Log

## Log de Execução

*(preencher ao executar)*
