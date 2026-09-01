---
id: PES2-TASK-02
title: "`tools/pes2/poke.py` — gravação pelo conjunto de cópias"
type: ferramenta
category: verificação
phase: 2
depends_on: []
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §6.1"
status: concluído
---

# PES2-TASK-02: Gravação pelo conjunto de cópias

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §6.1 e §6.2, com a regra de fim da
  §1.13 e o esquema de registro da §1.10.
- **É o pré-requisito do `poke` de validação** (PES2-TASK-04), que é o único
  item que falta para fechar a Fase 2.

Hoje `tools/pes2/tables.py` **acha e conta** as tabelas de texto, e
`tools/pes2/iso.py inject` **grava** um arquivo inteiro de volta na imagem.
Falta o meio: alterar *uma entrada* de *uma tabela* em *todas as cópias que
lhe tocam*.

---

## Objetivo

`tools/pes2/poke.py`, que recebe uma entidade lógica (um time, pelo índice
canônico) e um valor novo, e grava em **todas** as cópias.

```
python3 tools/pes2/poke.py <track1.bin> --team 12 --name PIEMONTE2 --dry-run
python3 tools/pes2/poke.py <copia.bin>  --team 12 --name PIEMONTE2
```

### As quatro regras que o gravador não pode violar

| Regra | Onde está | O que custa violar |
|---|---|---|
| grava em **todas** as cópias | §6.1 | nome novo numa tela, velho na outra |
| a correspondência entre listas sai de **conteúdo**, nunca de índice | §6.1 | grava no time errado, e parece plausível em tela |
| **trunca**, nunca desloca | §6.2, §1.10 | a margem entre a última tabela e a próxima é **zero byte** |
| o esquema de registro é **propriedade da tabela** | §1.10 | terminar em `NUL` um nome de 10 B numa tabela de largura fixa corrompe o primeiro caractere do vizinho |

A última merece o exemplo: `SELECT.BIN` @5320 tem 463 registros de 10 B
fixos, preenchidos com `NUL` à direita e **sem terminador quando o nome
ocupa os 10** — no disco lê-se `NachtegallHeggem` corrido. As tabelas de
nome de time, essas, são string + terminador alinhada a 4.

### Correspondência entre as listas

`tools/pes2/team_map.py` já resolve isso e tem `--team N`. O `poke.py`
**reusa** essa resolução em vez de reimplementá-la — o time canônico 34 fica
no índice 34, 36, 32 e 60 de quatro listas e **não existe** noutras, e um
`poke` que não trate a ausência escreve fora do lugar.

**E o conjunto de listas não é o que este arquivo dizia.** Ver o Log: eram
cinco no papel, são **oito** no disco.

---

## Critério de conclusão

- [x] `--dry-run` imprime, por cópia: arquivo, offset relativo, offset
      absoluto, byte antigo e byte novo, **sem tocar na imagem**.
- [x] Recusa alta e legível quando o nome novo não cabe no slot alinhado, com
      o tamanho disponível no texto do erro.
- [x] Recusa quando o time não existe numa das listas — dizendo em qual, e
      seguindo nas outras só com `--allow-partial` explícito.
- [x] Gravar e reler devolve o valor novo em todas as cópias; gravar o valor
      antigo de volta devolve a imagem **byte a byte idêntica** ao original.
- [x] Registrado no `check_image.py` (`ctest -R pes2_image`), como *skipped*
      sem `WE2002_PES2_IMAGE`.
- [x] Roda sobre **cópia** — o Track 1 tem 466 MB e a gravação é in-place.

---

## Log de Execução

**Executado em:** 2026-09-01

**Resumo do que foi feito.** `tools/pes2/poke.py` grava um nome de time em
todas as cópias que o tocam, resolvendo a correspondência por
`team_map.where()` — por conteúdo, nunca por índice —, medindo o slot pela
distância até o registro seguinte, e recusando em vez de deslocar. Seis
recusas, cada uma exercitada pelo `--self-check` e conferida **pelo texto**
da recusa: nome que não cabe (com o tamanho disponível no texto), time
ausente de alguma lista, registro em que a regra de fim de uma tabela para,
registro que é o **último** da tabela, registro que um **marcador** ancora,
e nome com byte fora de 0x20..0x7E. Escrever em `roms/` é recusado sem
override.

> Esta frase dizia "cinco recusas, todas exercitadas" até a
> [CORR-PES2-005](/docs/tasks/CORR-PES2-005.md). Eram quatro guardas
> distintas: o caso da regra de fim escolhia o time 96 (`IRELAND`), que
> está fora de `team-names-select2`, e a guarda de time ausente respondia
> por ele; a de último registro não tinha caso nenhum. `_expect_refusal`
> passou a conferir a mensagem, e é isso que impede o engano de voltar.

**O achado que dominou a execução: o conjunto de cópias era cinco no papel
e é oito no disco.** A primeira corrida do `--self-check` gravou as cinco e
morreu ao reler, porque o time que ela escolheu — o canônico 2,
`PATAGONIA` — **é o marcador** que ancora `team-names-ending` e
`team-names-result`. Daí saiu a guarda de sobreposição de marcador. Corrigida
essa, a varredura de todo arquivo `form1` atrás do nome velho achou três
registros vivos que nenhuma tabela conhecia:

| arquivo | offset `(EsIt)` | o que é | entradas |
|---|---:|---|---:|
| `SELECT.BIN` | 33188 | uma **segunda** lista no mesmo arquivo, caixa mista, só os 32 clubes fictícios; termina em `Aragon` e emenda nas strings de interface localizadas | 32 |
| `SELECT3.BIN` | 9448 | a lista de 99 outra vez, **mesmo digest** de `SELECTC.BIN` | 99 |
| `SELFORM.BIN` | 460 | idem, no overlay de formação | 99 |

As três entraram em `tables.py` (11 tabelas → **14**), em `iso.py ANCHORS`
(8 pares → **11**) e em `team_map.py` (4 cópias → **7**), com `--check`
verde nas duas releases e digests idênticos entre elas. A varredura ficou
no `poke.py` como guarda permanente: ela roda depois do plano e **recusa** a
gravação se sobrar registro que nenhuma tabela descreve, porque um jogo com
o nome novo numa tela e o velho na outra é a §6.1 palavra por palavra.

**Resultado medido.** `--self-check` verde nas duas releases: 8 registros em
7 arquivos, varredura sem sobra, e a imagem de volta byte a byte ao gravar
o nome antigo de novo. Fim a fim sobre cópia da `(EsIt)`, `--team 14 --name
PIEMONTE2`: 8 ocorrências novas, **zero** de `PIEMONTE`/`Piemonte` no disco
inteiro, `iso.py roundtrip` idêntico. `ctest -R pes2` verde
(`pes2_selftest`, `pes2_image`).

**Arquivos criados/modificados**

- `tools/pes2/poke.py` — novo
- `tools/pes2/tables.py` — `resolve_full()` (o fim da tabela, que o
  gravador precisa e o leitor não) e as três tabelas novas
- `tools/pes2/team_map.py` — as três cópias novas, `EXPECT`, e a prosa do
  `--markdown`
- `tools/pes2/iso.py` — três pares em `ANCHORS`
- `tools/pes2/check_image.py` — o `poke.self_check` sob `WE2002_PES2_TMPDIR`
- `docs/samples/pes2-team-lists.md` — regerado
- `docs/PLAN-PES2-PSX.md` — §1.5, §1.6, §1.13, §6.1 e a tabela de
  ferramentas
- `docs/tasks/progresso.md`, `docs/prompts/perfil-pes2.md`, `CLAUDE.md` — as
  contagens e a armadilha nova
- `docs/tasks/04-poke-de-validacao.md` — o repasse: o conjunto é oito, já
  varrido no arquivo, **não** em tela

**Problemas encontrados.** Os dois acima — o marcador que é também um
registro, e as três cópias fora do mapa. `docs/PES2-AJUSTES.md` continua
dizendo "onze tabelas" e "as cinco listas" **de propósito**: é o registro
datado da revisão de 2026-08-30, e reescrevê-lo falsificaria o que se
media naquele dia.
