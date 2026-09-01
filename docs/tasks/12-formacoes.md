---
id: PES2-TASK-12
title: "Formações — a tabela tática por time"
type: engenharia-reversa
category: formato
phase: 4
depends_on: ["PES2-TASK-11"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §5 (Fase 4)"
status: pendente
---

# PES2-TASK-12: Formações

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §5, Fase 4, e §1.4 (o empréstimo
  do WE2002 como índice de onde procurar).
- **Há uma âncora forte:** `SELFORM.BIN`, LBA 2050, 96.224 B, "overlay de
  formação" — e é onde três dos 69 `OFS_*` do WE2002 caem (§1.4), a começar
  por `OFS_TEAM_NAME_5`.
- **E há um cartão:** o slot 3 do memory card é `BESLES-03957PES-D4A`, 8 KiB,
  *"uma formação salva"* (§3.3). Mesmo ciclo de diferencial da
  PES2-TASK-05, aplicado a outro save.

---

## Objetivo

A estrutura de formação: posição de cada jogador em campo, papel, e o
conjunto de presets que o jogo oferece.

### O que o WE2002 diz para procurar

Não como resposta — como perguntas, na ordem em que o `Formation` do core as
guarda: coordenada X e Y por vaga, papel por vaga, e o `raw_formation` de 30
bytes que o `Load` lê. Se a engine é a mesma, a **forma** do registro tende
a ser a mesma; as larguras e a origem, não.

Uma nota do próprio core que vale de aviso: `raw_formation[30]` recebendo 30
bytes + terminador foi o `strcpy` que derrubava o editor em Release. O campo
é apertado por natureza; não presumir folga.

### Duas fontes de rótulo

| Fonte | O que dá | Custo |
|---|---|---|
| `PES-D4A` do cartão, com diferencial | rótulo exato: move-se um jogador na tela e vê-se o byte | ciclo de emulador por medida |
| `SELFORM.BIN`, por estrutura | a tabela inteira de uma vez | precisa de rótulo vindo da primeira |

Começar pela primeira, e usá-la para reconhecer a segunda.

---

## Critério de conclusão

- [ ] Estrutura do registro de formação: campo, deslocamento, largura,
      domínio.
- [ ] A tabela por time localizada em `SELFORM.BIN` (ou onde estiver), com
      âncora e contagem, e a contagem batendo com uma contagem de time
      conhecida.
- [ ] Verificado por `poke`: mover uma vaga no disco muda o campinho na tela.
- [ ] Os presets do jogo enumerados, se existirem como tabela.
- [ ] Ferramenta versionada, registrada no `check_image.py`.

---

## Log de Execução

*(a preencher)*
