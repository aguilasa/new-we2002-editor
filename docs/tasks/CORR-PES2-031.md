---
id: CORR-PES2-031
title: "Correção: o fluxo A, que é a razão de o fork existir, não tem ferramenta versionada"
type: correção
category: ferramental
status: pendente
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

- [ ] `python3 tools/pes2/who_writes.py --self-check` verde, com o caso
      vermelho do prazo aparecendo
- [ ] contra o jogo vivo, `who_writes.py 0x8007151B --width 2` reproduz o
      resultado de 2026-09-03: instrução em `0x80083574`, `v0 = 0x80071301`,
      `ra = 0x800834C0`
- [ ] `ctest --test-dir build -R pes2_selftest` verde
- [ ] a espera distingue "caiu" de "não está rodando"
- [ ] `roms/` intocada; nada do fork versionado

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
