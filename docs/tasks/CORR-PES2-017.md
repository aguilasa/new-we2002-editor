---
id: CORR-PES2-017
title: "Correção: o perfil do ciclo não tem seção de Fase 7, e a Fase 7 já teve quatro tasks executadas"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-PES2-017: A Fase 7 não tem verificações escritas no perfil

## Problema identificado

O [`docs/prompts/perfil-pes2.md`](/docs/prompts/perfil-pes2.md) traz a seção
"Verificações específicas por fase" com entradas para as **Fases 2, 3, 4, 5 e
6**, e uma nota dizendo que as Fases 0 e 1 estão fechadas. **Não há entrada
para a Fase 7.**

A Fase 7 entrou no quadro em 2026-09-01 com seis tasks (26 a 31), e desde
então **quatro delas foram executadas** — 26, 27, 28 e 29 — e **três foram
revisadas** sem que o revisor tivesse um checklist escrito para a fase.

O [`docs/prompts/02-revisar.md`](/docs/prompts/02-revisar.md) manda,
literalmente: *"Se o perfil não tiver entrada para essa fase, **diga isso na
saída** em vez de improvisar — fase sem verificação escrita é achado, e vira
CORR."* Foi o que aconteceu nesta revisão.

## Evidência

```
$ sed -n '/## Verificações específicas por fase/,$p' docs/prompts/perfil-pes2.md \
    | grep -n '^\*\*Fase'
6:**Fases 0 e 1 — infra e diferencial barato — estão fechadas.**
12:**Fase 2 (tasks 02 a 04) — inventário de texto:**
24:**Fase 3 (tasks 05 a 10) — o registro de jogador:**
36:**Fase 4 (tasks 11 a 16) — o resto do banco:**
44:**Fase 5 (tasks 17 a 21) — mapa e leitor:**
52:**Fase 6 (tasks 22 a 25) — editor:**
```

E o quadro, no `progresso.md`:

```
| PES2-TASK-26 | O codec LZSS ...            | 7 | ✅ Concluído | revisada |
| PES2-TASK-27 | Cabeçalho de contêiner ...  | 7 | ✅ Concluído | revisada |
| PES2-TASK-28 | T_NAME ...                  | 7 | ⬜ Pendente  |          |
| PES2-TASK-29 | Gravação de asset ...       | 7 | ✅ Concluído | esta     |
```

## Causa raiz

A Fase 7 foi acrescentada ao `progresso.md` e ao plano sem que o perfil — que
é onde moram as verificações por fase desde a CORR-PES2-004 — ganhasse a
entrada correspondente.

## Correção

### Arquivo: `docs/prompts/perfil-pes2.md`

Acrescentar a seção da Fase 7 depois da Fase 6, com as perguntas que as quatro
tasks já executadas mostraram valer. Sugestão, a confirmar por quem executar:

- O codec/contêiner foi medido nos **quatro** discos — as duas releases de PES2
  e as duas imagens de WE2002 — ou só numa? (§1.14(e), (f))
- O que a ferramenta chama de índice é **o registro**, não a varredura de
  ressincronização? Onde as duas discordam, o registro ganha (§1.14(f))
- A profundidade veio da **largura do CLUT**, e não de um palpite por arquivo?
  `DAT2D.BIN` tem 261 paletas de 16 e 5 de 256 (CORR-PES2-016)
- Gravação: os **dois** orçamentos foram conferidos — o do extent e o da
  entrada — e o da entrada primeiro? (§1.14(g))
- EDC/ECC **preservado**, com a cauda de 280 B conferida byte a byte? (§6.7)
- O conjunto de cópias do asset foi **varrido por conteúdo**, nunca declarado
  por sufixo de nome? (§6.12)
- Quadro do jogo **fora** do git; o que entra é o comando e o número

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/prompts/perfil-pes2.md` | modificar |

## Verificação

- [ ] `sed -n '/Verificações específicas por fase/,$p' docs/prompts/perfil-pes2.md | grep '^\*\*Fase'` lista a Fase 7
- [ ] `python3 tools/check_tasks.py` verde
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-01

**Resumo do que foi feito:** o `perfil-pes2.md` ganhou a seção **Fase 7 (tasks
26 a 31) — os assets do disco**, depois da Fase 6. As nove perguntas saem do
que as quatro tasks já executadas mostraram valer, e cada uma cita a seção ou a
CORR que a originou: os quatro discos, o registro contra a varredura, a
profundidade pela largura do CLUT, os dois orçamentos, a validação de import,
o EDC/ECC, o conjunto de cópias por conteúdo, a guarda vista em vermelho, e o
quadro fora do git.

**Problemas encontrados:** nenhum. A seção era o único buraco; as Fases 2 a 6
já estavam escritas.

**Arquivos criados/modificados:** `docs/prompts/perfil-pes2.md`.
