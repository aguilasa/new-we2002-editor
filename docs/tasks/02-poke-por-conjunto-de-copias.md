---
id: PES2-TASK-02
title: "`tools/pes2/poke.py` — gravação pelo conjunto de cópias"
type: ferramenta
category: verificação
phase: 2
depends_on: []
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §6.1"
status: pendente
---

# PES2-TASK-02: Gravação pelo conjunto de cópias

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §6.1 e §6.2, com a regra de fim da
  §1.13 e o esquema de registro da §1.10.
- **É o pré-requisito do `poke` de validação** (PES2-TASK-04), que é o único
  item que falta para fechar a Fase 2.

Hoje `tools/pes2/tables.py` **acha e conta** as onze tabelas de texto, e
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

### Correspondência entre as cinco listas

`tools/pes2/team_map.py` já resolve isso e tem `--team N`. O `poke.py`
**reusa** essa resolução em vez de reimplementá-la — o time canônico 34 fica
no índice 34, 36, 32 e 60 de quatro listas e **não existe** na quinta, e um
`poke` que não trate a ausência escreve fora do lugar.

---

## Critério de conclusão

- [ ] `--dry-run` imprime, por cópia: arquivo, offset relativo, offset
      absoluto, byte antigo e byte novo, **sem tocar na imagem**.
- [ ] Recusa alta e legível quando o nome novo não cabe no slot alinhado, com
      o tamanho disponível no texto do erro.
- [ ] Recusa quando o time não existe numa das listas — dizendo em qual, e
      seguindo nas outras só com `--allow-partial` explícito.
- [ ] Gravar e reler devolve o valor novo em todas as cópias; gravar o valor
      antigo de volta devolve a imagem **byte a byte idêntica** ao original.
- [ ] Registrado no `check_image.py` (`ctest -R pes2_image`), como *skipped*
      sem `WE2002_PES2_IMAGE`.
- [ ] Roda sobre **cópia** — o Track 1 tem 466 MB e a gravação é in-place.

---

## Log de Execução

*(a preencher)*
