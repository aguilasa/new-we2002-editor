---
id: PES2-TASK-24
title: "O editor — gravação"
type: implementação
category: ui
phase: 6
depends_on: ["PES2-TASK-23"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §6 (armadilhas)"
status: pendente
---

# PES2-TASK-24: O editor, lado da gravação

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §6 inteira — as armadilhas são a
  especificação do gravador —, e §0 (objetivo).
- **É o caminho que corrompe imagem de 466 MB.** Toda a §6 do plano existe
  por causa desta task; ela é a leitura obrigatória antes da primeira linha.

---

## Objetivo

Gravar in-place, pelo mapa, com as sete regras da §6 respeitadas — e cada
uma verificável.

| Regra | §  | O que o editor faz |
|---|---|---|
| toda gravação é para o **conjunto de cópias** | 6.1 | grava as N cópias, ou nenhuma |
| a correspondência entre listas sai de **conteúdo** | 6.1 | reusa o `team_map.py`; nunca casa por índice |
| registro variável **não aceita nome maior** — trunca | 6.2 | recusa ou trunca, e diz qual |
| a **fronteira de setor** salta 304 bytes | 6.3 | trabalha em offset relativo; converte só ao gravar |
| o offset é **dentro do Track 1** | 6.4 | nunca concatena trilhas |
| o diretório ISO nomeia arquivo fora do Track 1 | 6.5 | `OutsideTrack`, como o `iso.py` já levanta |
| **não recalcular EDC/ECC** | 6.7 | preserva os 280 B de cauda |

### A regra que não está na §6 e devia estar

**Nunca apontar para `roms/`.** É o que o `CLAUDE.md` cobra dos três
editores do repositório, e vale igual aqui: os originais são ~571 MiB por
release, e um `poke` errado sem cópia custa um novo download. O editor
recusa gravar num caminho sob `roms/`, e diz por quê.

### Confirmar antes de gravar

Gravação in-place é irreversível sem cópia. O editor confirma antes do
primeiro byte, mostrando o que vai mudar: entidade, quantas cópias, quantos
bytes. É a versão de interface do `--dry-run` da PES2-TASK-02.

### E se a PES2-TASK-08 achou índice

Se houver índice reconstruível para o bloco de nomes, a regra de truncar
afrouxa — e a §6.2 diz "até que exista prova". Nesse caso o editor pode
crescer um nome **e reescrever o índice**, e isso é caminho de escrita novo,
com round-trip próprio. Se não houver, truncar fica.

---

## Critério de conclusão

- [ ] As sete regras da tabela verificadas, uma a uma, com o teste que as
      mede.
- [ ] Round-trip pela interface: abrir, gravar sem editar, `cmp` zero.
- [ ] Editar um campo de cada família e ver o resultado no emulador — texto,
      numérico, campo de bits, cor.
- [ ] Recusa de gravar em `roms/`, exercitada.
- [ ] Confirmação antes de gravar, mostrando o que muda.
- [ ] Nenhuma imagem de `roms/` tocada em nenhum momento do desenvolvimento.

---

## Log de Execução

*(a preencher)*
