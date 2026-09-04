---
id: CORR-PES2-031
title: "Correção: o fluxo A, que é a razão de o fork existir, não tem ferramenta versionada"
type: correção
category: ferramental
status: concluído
depends_on: []
---

# CORR-PES2-031: o procedimento do fluxo A mora num Log, não em `tools/pes2/`

## Problema identificado

A [PES2-TASK-33](/docs/tasks/33-compilar-e-validar-o-mcp.md) reduziu o escopo
do fork a dois fluxos, e disse por quê:

> Como a TASK-32 entregou C e D em Python puro (`tools/pes2/savestate.py`), o
> MCP só precisa provar o que o save state **não** dá: **A — quem escreve** e
> **E — verificar ASM**.

O fluxo A fechou, e o resultado é bom — `sb zero, 0x21a(v0)` em `0x80083574`,
`v0 = 0x80071301`, a rotina de limpeza em `0x80083560`. Mas **o procedimento
que produziu isso não virou ferramenta.** Nada em `tools/pes2/` sabe armar um
breakpoint:

```
$ grep -rln "breakpoint\|read_registers\|disassemble" tools/pes2/
tools/pes2/savestate.py

$ grep -rn "breakpoint" tools/pes2/*.py
tools/pes2/savestate.py:40:    A -- who writes    ->  no. Needs a write breakpoint.
```

A única menção é um comentário dizendo que o fluxo A **precisa** de um
breakpoint. Refazê-lo hoje significa escrever à mão a sequência de
`mcp.py --call breakpoint action=add type=write address=…`, esperar,
`read_registers`, `disassemble` — que é exatamente o que esta revisão teve de
fazer, e foi nesse caminho que a queda da
[CORR-PES2-032](/docs/tasks/CORR-PES2-032.md) apareceu.

A lista de Fase 0 do [`perfil-pes2.md`](/docs/prompts/perfil-pes2.md) pergunta
isto em uma linha:

> - Toda asserção nova foi vista **ficando vermelha**, e existe um comando
>   versionado que a leva ao estado em que ela pode ser exercitada?

Para o fluxo A a resposta é não. E o custo não é teórico: as fases 3 e 4
inteiras — `PES2-TASK-07` (dump de RAM e casamento com o bloco do disco) e o
laço disco↔RAM que a §4.2 chama de "último recurso" — são fluxo A repetido
sobre outros endereços.

Comparação que deixa a lacuna clara: o fluxo **C** virou
`savestate.py scan`, com `selftest`, casos vermelhos e lugar no
`pes2_selftest`. O fluxo **A** tem um parágrafo de prosa.

## Evidência

O que reproduz hoje, e o que não:

```
# reproduz -- leitura estatica, com o emulador pausado
$ python3 tools/pes2/mcp.py --call disassemble address=0x80083560 count=16
  0x80083574  0xA040021A  sb zero, 0x21a(v0)      <- o placar
  0x80083578  0xA040005F  sb zero, 0x5f(v0)       <- onde o PC parou

# nao reproduz por comando versionado -- o disparo
(nenhuma ferramenta de tools/pes2/ arma breakpoint; a sequencia foi
 escrita a mao nesta revisao, e o emulador caiu duas vezes durante a
 espera -- CORR-PES2-032)
```

Os três sub-resultados do fluxo A **foram** reconferidos estaticamente nesta
revisão e batem: a rotina em `0x80083560` é um bloco de `sb zero` em
sequência, o `sb zero, 0x21a(v0)` está em `0x80083574`, `0x80083578` é a
instrução seguinte (que é onde um watchpoint de escrita para), e
`0x80071300 + 0x21B = 0x8007151B`. O que não se reconfere por comando é o
disparo.

## Causa raiz

A TASK-33 era task de **decisão**, e entregou a decisão. O procedimento ficou
no Log porque nenhum critério pedia ferramenta — e o fluxo A passou a ser a
justificativa inteira do fork sem ganhar o tratamento que o fluxo C ganhou.

## Correção

### Arquivo: `tools/pes2/who_writes.py` (novo), ou um subcomando de `mcp_drive.py`

Uma ferramenta pequena, com a forma das outras deste ciclo:

```
python3 tools/pes2/who_writes.py 0x8007151B --width 2 [--timeout 180]
```

que faz, contra o emulador já rodando:

1. limpa os breakpoints, arma um de escrita no endereço;
2. retoma e **espera** o disparo — conferindo a cada intervalo se o
   processo ainda existe, e dizendo "o emulador caiu" em vez de "não está
   rodando" quando ele sumir (armadilha 35, CORR-PES2-032);
3. no disparo, coleta `read_registers` e `disassemble` em volta do `PC`, e
   imprime a leitura pronta: o endereço da instrução, o registrador-base, o
   deslocamento e o `ra`;
4. `--self-check` sem emulador, cobrindo o que dá: a montagem dos argumentos,
   o cálculo `base + deslocamento == alvo`, e o caso vermelho de disparo que
   não chega dentro do prazo — que tem de **falhar**, não devolver vazio.

Entra no `pes2_selftest` como as outras.

### Arquivo: `docs/PLAN-PES2-PSX.md` §6.14

A seção do fluxo A passa a apontar para o comando, e não só para o resultado
de 2026-09-03 — como a do fluxo C aponta para `savestate.py scan`.

### Arquivo: `docs/prompts/perfil-pes2.md`

Uma linha na tabela de gates:

```markdown
| endereço de RAM atribuído a um escritor | `who_writes.py --self-check` verde,
e o disparo reproduzido no endereço em questão; sem o disparo é conjectura |
```

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/pes2/who_writes.py` | criar |
| `tools/pes2/selftest.py` | modificar |
| `docs/PLAN-PES2-PSX.md` | modificar |
| `docs/prompts/perfil-pes2.md` | modificar |

## Verificação

- [x] `python3 tools/pes2/who_writes.py --self-check` verde, com o caso
      vermelho do prazo aparecendo
- [x] contra o jogo vivo, `who_writes.py 0x8007151B --width 2` reproduz o
      resultado de 2026-09-03: instrução em `0x80083574`, `v0 = 0x80071301`,
      `ra = 0x800834C0`
- [x] `ctest --test-dir build -R pes2_selftest` verde
- [x] a espera distingue "caiu" de "não está rodando"
- [x] `roms/` intocada; nada do fork versionado

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-09-03 (parcial) e **2026-09-04 (fechada)**

**Resumo do que foi feito:** `tools/pes2/who_writes.py` existe, com a forma
das outras ferramentas do ciclo: limpa os breakpoints, arma o watchpoint de
escrita, retoma, espera, e no disparo lê os registradores e desmonta em volta
do `PC`, imprimindo instrução, registrador-base, deslocamento, a conferência
`base + deslocamento == alvo`, e o `ra`. `--self-check` roda sem emulador e
entrou no `pes2_selftest`.

**O que ficou em aberto: a reprodução da leitura de 2026-09-03.** O watchpoint
nunca disparou nas seis janelas tentadas. **Não é a ferramenta**, e a medição
que separa as duas coisas foi feita:

- o watchpoint **arma e conta** — `hit_count` foi de 0 a **9** ao longo de
  400 s de partida sob `pad.py run`, que é quem dá os saques;
- um breakpoint de **execução** no `PC` corrente **para** a CPU
  (`status: paused`, `pc` parado, `hit_count: 1`), então o mecanismo serve;
- **60 s de partida livre sem interferência nenhuma** deixaram o watchpoint
  de escrita em `hit_count: 0`.

O endereço não é escrito continuamente: ele é escrito no **reinício de
partida**, precondição que a própria §6.14 registra ("o jogo dirigido até uma
partida nova"). Nenhuma das janelas — 150, 180, 200, 280 s, partindo do meio
da partida e do `team-select`, no endereço virtual `0x8007151B` e no físico
`0x0007151B` — chegou a encenar esse reinício. **Falta o comando versionado
que leva o jogo até lá**, que é o mesmo tipo de lacuna que a CORR-PES2-024
fechou para o `--measure-menu` com o `--keep-alive`.

**Problemas encontrados — três, e os três viraram asserção:**

1. **`wait_for_pause` responde em `status`, não em `paused` nem `state`.**
   Medido contra o servidor vivo: rodando dá
   `{"status": "running", "poll_after_ms": 50, …}`, parado dá
   `{"status": "paused", "pc": "0x80019DE8"}`. A primeira versão adivinhou os
   dois nomes óbvios, leu toda resposta como "ainda rodando", e **duas
   corridas foram creditadas ao jogo quando a culpa era do parser**. As
   quatro formas estão fixadas no `--self-check`.
2. **`press_button` retoma a máquina para entregar a tecla**, então cutucar
   às cegas desfaz a parada que se espera. A espera passou a olhar **antes**
   de cutucar, e outra vez logo depois.
3. **Sessões MCP não convivem.** Rodar `pad.py` ao lado invalida a sessão do
   `who_writes` (`missing or invalid MCP-Session-Id`), então o cutucão tem de
   sair **deste** cliente — é por isso que `--nudge` existe em vez de
   "rode o `pad.py` junto".

E o `--self-check` ficou vermelho dentro do `pes2_selftest` enquanto passava
sozinho, porque dependia de o emulador estar vivo — exatamente o que a lista
de Fase 0 do perfil proíbe. O `alive()` virou parâmetro injetado, e os dois
caminhos de falha são dirigidos sem emulador nenhum.

**Gates:**

```
$ python3 tools/pes2/who_writes.py --self-check      # com o emulador MORTO
SELF-CHECK OK: addresses, stores, registers, both waits      exit 0
$ ctest --test-dir build -R pes2_selftest
1/1 Test #7: pes2_selftest .......... Passed  9.33 sec
```

26 asserções, três delas vermelhas por construção: o prazo que expira, a
morte no meio da espera (que cita a armadilha 35 em vez de "não está
rodando"), e o cutucão que só sai quando pedido. `roms/` intocada, nada do
fork versionado.

---

## Fechamento, 2026-09-04

**A leitura foi reproduzida, e os quatro valores batem.** O rito são dois
comandos versionados, sobre cópia:

```sh
python3 tools/pes2/mcp_drive.py "<copia.cue>" --screen team-select --keep-alive
python3 tools/pes2/who_writes.py 0x8007151B --width 2 --nudge Cross
```

```
  the watchpoint fired after 42.9s

address      0x8007151B  (width 2)
stopped at   0x80083578
written by   0x80083574  sb zero, 0x0000021A(v0)
             v0 = 0x80071301, 0x80071301 + 0x0000021A = 0x8007151B
called from  ra = 0x800834C0

  0x80083568  sb zero, 0x21d(a3)
  0x8008356C  sb zero, 0x21c(a3)
  0x80083570  sb zero, 0x224(v0)
  0x80083574  sb zero, 0x21a(v0) <-
  0x80083578  sb zero, 0x5f(v0)
```

Instrução, `v0`, ponto de parada e `ra` idênticos aos de 2026-09-03, e a
janela em volta mostra o mesmo bloco de `sb zero` em sequência.

**A causa das seis falhas de ontem não era o reinício de partida — era o
botão preso.** `press_button` **sem `duration_frames`** responde
`{"state": "pressed"}` e deixa o pad apertado: o primeiro cutucão prendia o
Cross e todos os seguintes eram inócuos, o que na tela é indistinguível de um
jogo que se recusa a avançar. O `mcp_drive.press` sempre passou a duração; o
`--nudge` não passava. O `NUDGE_FRAMES = 6` entrou, e o `--self-check` passou
a **exigir** que o cutucão carregue a duração — sem essa asserção o defeito
volta calado.

Duas hipóteses foram medidas e descartadas no caminho, e as duas valia
descartar:

- **`press_button` não apaga breakpoint.** Armado, `continue`, `press_button`
  e `pause`: a lista continua com `hit_count` intacto nos quatro momentos. A
  lista vazia observada ontem era o `finally` do próprio `who_writes`.
- **O endereço físico não era o problema.** `0x0007151B` e `0x8007151B` se
  comportam igual; o que faltava era o jogo andar.

**Gates:**

```
$ python3 tools/pes2/who_writes.py --self-check     # 27 asserções
SELF-CHECK OK: addresses, stores, registers, both waits      exit 0
$ ctest --test-dir build -R pes2_selftest
1/1 Test #7: pes2_selftest .......... Passed  9.38 sec
```

`roms/` intocada — tudo correu sobre cópia da release `(EsIt)` no scratchpad.

**Arquivos do fechamento:**

| Arquivo | Ação |
|---|---|
| `tools/pes2/who_writes.py` | modificado (`NUDGE_FRAMES`, a duração no cutucão, a asserção) |
| `docs/PLAN-PES2-PSX.md` | modificado (§6.14: a reprodução, e a causa das falhas) |
| `docs/prompts/perfil-pes2.md` | modificado (o rito de dois comandos na tabela de gates) |

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `tools/pes2/who_writes.py` | criado |
| `tools/pes2/selftest.py` | modificado (entra no `pes2_selftest`) |
| `docs/PLAN-PES2-PSX.md` | modificado (§6.14, fluxo A: o comando e o que falta) |
| `docs/prompts/perfil-pes2.md` | modificado (bloco de gates e uma linha na tabela) |
