---
id: CORR-PES2-032
title: "Correção: o fork morre calado durante execução livre, e toda ferramenta relata isso como \"não está rodando\""
type: correção
category: ferramental
status: pendente
depends_on: []
---

# CORR-PES2-032: a queda intermitente do emulador de trabalho não está escrita em lugar nenhum

## Problema identificado

O fork é o **emulador de trabalho** deste projeto desde 2026-09-03, e ele
**cai sozinho durante execução livre**. Medido nesta revisão: **quatro mortes
em seis corridas**, entre 15 s e 90 s de jogo rodando, sem uma linha de log,
sem core dump e sem entrada no journal. O controle — 75 s de execução livre
**sem nenhuma chamada MCP** — sobreviveu.

Nada disso está registrado: as trinta e quatro armadilhas da §6.11 não têm
entrada para isso, o perfil não menciona, e a
[PES2-TASK-33](/docs/tasks/33-compilar-e-validar-o-mcp.md), que certificou o
binário, não viu.

**Por que isso importa mais do que "um emulador instável".** O fluxo A — a
única razão pela qual o fork foi adotado, depois que a PES2-TASK-32 entregou
C e D em Python puro — é justamente *"arme um breakpoint de escrita e deixe o
jogo correr até ele disparar"*. Execução livre é o modo em que a queda
acontece. A capacidade que a task certifica é a que o defeito atinge.

**E a mensagem esconde o defeito.** Quando o processo morre, todas as
ferramentas dizem a mesma coisa:

```
no MCP server at http://127.0.0.1:2346/mcp -- the DuckStation fork is not
running. Start it with tools/pes2/fork.py launch (the official AppImage has
no MCP server).
```

A frase está factualmente certa e diagnosticamente errada: ela descreve o
esquecimento de lançar o emulador, não a queda de um que estava rodando há um
minuto. Nesta revisão ela custou três interpretações erradas antes de a queda
ser reconhecida — foi preciso um `pgrep` para ver que o processo tinha
sumido.

## Evidência

Seis corridas, todas sobre a mesma cópia e o mesmo `:98`, nesta revisão:

| corrida | o que fazia | resultado |
|---|---|---|
| 1 | `tools/list` + `get_status` avulsos | morreu no meio |
| 2 | estado de partida carregado, `get_status` a cada 5 s | **morreu em ~15 s** |
| 3 | só o boot, `get_status` a cada 5 s | **morreu em ~45 s** |
| 4 | **controle: 75 s sem nenhuma chamada** | **sobreviveu**; morreu logo após as duas primeiras chamadas |
| 5 | `get_status` a cada 2 s | **morreu após 44 chamadas, 89 s** |
| 6 | `get_status` a cada 2 s | sobreviveu 60 chamadas em 120 s |

A queda **não é determinística** — a corrida 6 não caiu —, e é isso que a
torna cara: ela não reprova nada, só interrompe.

O que o log guarda depois das seis corridas:

```
$ cat <copia>/duckstation-fork.log
XDG_SESSION_DESKTOP=zorin:GNOME
Enabling xdg-desktop-portal platform theme.
Wayland not detected, not applying workarounds.
```

Três linhas de Qt. E nada em nenhum outro lugar:

```
$ coredumpctl list ; journalctl --user -n 20 | grep -i duckstation ; dmesg | grep -i duckstation
(vazio nos três)
$ ls ~/.local/share/duckstation/*.log
zsh: no matches found
```

Que as rotas do `mcp_drive.py` não tropeçam nisso é consistente e vale
registrar: elas **pausam** o emulador e andam por `frame_step`, então quase
não há execução livre. As corridas de rota desta sessão e a anterior fecharam
todas.

## Causa raiz

Não identificada — é um defeito do binário de terceiro, e o diagnóstico exige
o build de debug que não temos. O que **é** nosso e está errado: nada avisa
que isso acontece, e a mensagem de servidor ausente não distingue "nunca
subiu" de "caiu agora".

## Correção

Três coisas, e a primeira é a única indispensável.

### Arquivo: `docs/PLAN-PES2-PSX.md` §6.11 (e a contagem da seção)

Armadilha nova, com os números medidos, e a contagem **recontada** por
`awk`, não incrementada:

```markdown
35. **O fork cai sozinho em execução livre, e não escreve nada.** Medido em
    2026-09-03: quatro mortes em seis corridas, entre 15 s e 90 s de jogo
    rodando; um controle de 75 s sem nenhuma chamada MCP sobreviveu. Não é
    determinístico. Nada aparece no log que o `fork.py` captura (três linhas
    de Qt), nem em `coredumpctl`, `journalctl` ou `dmesg`. As rotas do
    `mcp_drive.py` quase não sentem porque pausam e andam por `frame_step`;
    quem sente é o **fluxo A**, que é esperar de breakpoint armado com o
    jogo correndo. Reabra o emulador e repita — e nunca leia "the fork is
    not running" como esquecimento sem antes conferir com `pgrep -x
    duckstation-qt`.
```

### Arquivo: `tools/pes2/mcp.py`

A mensagem de servidor ausente passa a distinguir os dois casos, que é
barato porque o `fork.py` já sabe listar processos:

```python
try:
    import fork
    alive = bool(fork.running_pids())
except Exception:
    alive = None
if alive:
    raise NotRunning(f"no MCP server at {url} -- but duckstation-qt IS "
                     f"running: the emulator is up and the server is not "
                     f"answering")
if alive is False:
    raise NotRunning(f"no MCP server at {url} -- and no DuckStation process "
                     f"either. It was never started, or it died mid-run "
                     f"(pitfall 35). Start it with tools/pes2/fork.py launch")
```

### Arquivo: `tools/pes2/fork.py`

O `launch` **acrescenta** ao log em vez de truncá-lo, para a corrida seguinte
não apagar a evidência da anterior, e imprime o caminho do log na mensagem de
morte. Hoje ele abre com `"wb"`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-PES2-PSX.md` | modificar |
| `docs/prompts/perfil-pes2.md` | modificar (a armadilha 12 cita a contagem) |
| `tools/pes2/mcp.py` | modificar |
| `tools/pes2/fork.py` | modificar |

## Verificação

- [ ] a §6.11 tem a armadilha, e a contagem do título bate com
      `awk '/^### 6\.11/,/^### 6\.12/' docs/PLAN-PES2-PSX.md | grep -cE '^[0-9]+\. '`
- [ ] com o emulador morto, `mcp.py --status` diz que **não há processo**, e
      cita a armadilha
- [ ] com o emulador vivo e o servidor derrubado, a outra mensagem aparece —
      exercitado, não presumido
- [ ] `python3 tools/pes2/mcp.py --self-check` e
      `python3 tools/pes2/fork.py --self-check` verdes
- [ ] `ctest --test-dir build -R pes2_selftest` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
