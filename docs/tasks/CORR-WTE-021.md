---
id: CORR-WTE-021
title: "Correção: o critério \"blobs visíveis na janela\" foi adiado para a WTE-TASK-11, que não o tem"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-WTE-021: o único critério aberto da WTE-TASK-10 foi entregue a uma tarefa que não o recebeu

## Problema identificado

A WTE-TASK-10 está `✅ Concluído` com um critério em aberto, e a anotação diz
para onde ele foi:

```markdown
- [ ] Blobs binários preservados e visíveis na janela — preservados e
      conferidos byte a byte; "visíveis" só na WTE-TASK-11
```

A metade "preservados" está provada (esta revisão conferiu os 118 blobs contra
o `.dfm` **e** contra os `.bin` de `wte/re/dfm/blobs/`: 118 conferidos, zero
divergentes). A metade "visíveis" foi adiada para a **WTE-TASK-11** — e a
WTE-TASK-11 está concluída sem nunca ter tido esse item: a palavra "blob" não
ocorre no arquivo dela, nem "bitmap", nem "visível". O critério caiu no vão.

O dono real é a **WTE-TASK-12**, que já tem a linha na sua própria tabela de
achados:

| Achado | Gravidade |
|---|---|
| bitmap não aparece | blob perdido na conversão |

Só que a WTE-TASK-12 não sabe que está herdando um critério aberto de outra
tarefa, e a WTE-TASK-10 aponta para o lugar errado. Quem for fechar a fase 2
lendo a 10 procura a resposta na 11 e não acha; quem ler só a 12 fecha os seis
critérios dela sem saber que um sétimo, de fora, dependia daquele mesmo olhar.

## Evidência

O critério e seu destino declarado:

```
$ sed -n '82,83p' docs/tasks/10-conversor-dfm-para-lfm.md
- [ ] Blobs binários preservados e visíveis na janela — preservados e
      conferidos byte a byte; "visíveis" só na WTE-TASK-11
```

O destino não tem o item:

```
$ grep -n -i "blob\|bitmap\|visív\|visiv" docs/tasks/11-app-com-a-casca-completa.md
(nenhuma saída)
```

O dono real tem:

```
$ grep -n "bitmap" docs/tasks/12-comparacao-visual.md
48:| bitmap não aparece | blob perdido na conversão |
```

A metade que estava sob a WTE-TASK-10, remedida nesta revisão:

```
blobs conferidos contra .dfm E contra blobs/*.bin: 118 divergentes: 0 []
```

## Causa raiz

O adiamento nomeou a tarefa seguinte em vez da tarefa que tem a conferência
visual no escopo, e ninguém aplicou a contrapartida do outro lado.

## Correção

### Arquivo: `docs/tasks/10-conversor-dfm-para-lfm.md`

Corrigir o destino do adiamento e dizer o que já está provado:

```markdown
- [ ] Blobs binários preservados e visíveis na janela — **preservados**:
      os 118 conferidos byte a byte contra o SHA-256 do `.dfm` e contra
      `wte/re/dfm/blobs/*.bin`, zero divergentes (revisão de 2026-08-09).
      **Visíveis** é da [WTE-TASK-12](/docs/tasks/12-comparacao-visual.md),
      que já tem "bitmap não aparece" na tabela de achados — não da
      WTE-TASK-11, que nunca teve o item.
```

### Arquivo: `docs/tasks/12-comparacao-visual.md`

Fechar o vão do outro lado, acrescentando o critério herdado:

```markdown
- [ ] Os 118 blobs aparecem na janela — critério herdado da
      [WTE-TASK-10](/docs/tasks/10-conversor-dfm-para-lfm.md), que provou a
      preservação byte a byte e não podia provar a exibição
```

E, em "O que procurar", trocar a linha `bitmap não aparece` por uma que diga
que a preservação já foi medida — se um bitmap sumir, o defeito é de exibição
(LCL/GTK2 ou pai do componente), não de conversão.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/10-conversor-dfm-para-lfm.md` | modificar |
| `docs/tasks/12-comparacao-visual.md` | modificar |

## Verificação

- [ ] `grep -n "WTE-TASK-11" docs/tasks/10-conversor-dfm-para-lfm.md` não
      aparece mais no critério dos blobs (a nota do `retrace` no Log continua)
- [ ] `grep -n "118" docs/tasks/12-comparacao-visual.md` acha o critério
      herdado
- [ ] a conferência de forma e de destino de link de `.claude/rules/links.md`
      sai vazia nos dois arquivos
- [ ] `make -C wte check` verde — nenhum número velho reintroduzido
- [ ] nenhum arquivo gerado tocado: `python3 wte/tools/dfm2lfm.py --check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
