---
id: CORR-WTE-009
title: "Correção: a §8.8 e a pendência do progresso.md ainda tratam o binário espanhol como única rota para as mensagens decepadas"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-WTE-009: as mensagens que o tradutor decepou estão dentro do próprio `.exe`

## Problema identificado

A §8.8 do plano registra a armadilha das mensagens truncadas e aponta uma saída:

> 70 strings estão com padding, e pelo menos uma perdeu conteúdo
> (`somente na Mastere`). Se a spec de um handler depender de ler a mensagem de
> erro para entender a regra de validação, a mensagem pode estar incompleta.
> **Conseguir o binário original em espanhol resolveria isso** — mas não é
> bloqueante [...]

O `progresso.md` repete a mesma leitura na lista de pendências externas:

> **Binário original em espanhol seria bom ter, e não é bloqueante.** O `.exe` é
> a tradução PT-BR com 70 strings truncadas por padding. **Recuperar o original
> devolveria as mensagens inteiras** [...] (§1.5)

A WTE-TASK-05 mediu que, para as mensagens que interessam, **não é preciso o
binário espanhol**: o bloco de literais do app aparece **três vezes** em `.data`,
e as duas cópias altas — não referenciadas por ponteiro nenhum, portanto mortas —
preservam o texto que a viva perdeu. A mensagem que a própria §8.8 cita como
exemplo é uma das três que têm gêmea legível.

Nenhum dos dois documentos foi atualizado. Quem abrir a §8.8 na fase 4, ao
escrever a spec de `jugador.BitBtn3Click`, vai concluir que a regra de validação
não é recuperável sem um binário que ninguém tem — quando ela está a um `grep`
de distância, no arquivo que já está no disco.

**Fora de escopo aqui:** o número "70", que a
[WTE-TASK-09](/docs/tasks/09-fechamento-fase-1.md) já tem no seu quadro de
reconciliação (`70 strings com padding | dump_strings.py`). Esta correção trata
só da **conclusão** das duas seções, que a 09 não cobre.

## Evidência

Do `wte/re/strings.md`, seção "As cópias mortas preservam conteúdo que a viva
perdeu" — viva em `0x00424ac0`, referenciada de dentro de
`jugador.BitBtn3Click`:

```
Numero do uniforme invalido ([33 ... 99] somente na Mastere
```

Cópia morta em `0x0042d058`, mesmo bloco deslocado de `0x8598`:

```
Numero da camisa          r ([33 ... 99] somente na Master    )
```

O parêntese fecha e `Master` está inteiro — a regra de validação sai das duas.

As duas cópias, medidas pelo `dump_strings.py` (coluna `copia_de` do TSV, 371
das 765 strings com gêmea byte a byte):

```
| Cópia | Δ       | Strings | Origem                  | Cópia mora em           | Referenciadas |
| 1     | 0x8598  | 78      | 0x00424767…0x00424c6f   | 0x0042ccff…0x0042d207   | 0 |
| 2     | 0x9b80  | 47      | 0x00424767…0x00424b13   | 0x0042e2e7…0x0042e693   | 0 |
```

`Referenciadas: 0` nas duas é o que as classifica como mortas — e é o que
explica por que ninguém tinha lido o texto delas.

Três strings marcadas `gemea_difere` no TSV, isto é, com cópia de mesmo prefixo
e texto diferente:

```
$ awk -F'\t' 'NR>1 && $5 ~ /gemea_difere/' wte/re/strings.tsv | cut -f1,5
0x00424ac0   enchimento+truncada+gemea_difere
(mais duas)
```

## Causa raiz

A medição que derruba a premissa saiu na WTE-TASK-05 e ficou no relatório dela;
nenhuma tarefa ficou dona de levá-la à §8.8 e à lista de pendências.

## Correção

### Arquivo: `docs/PLAN-WTE-LAZARUS.md`

§8.8: manter a armadilha — mensagem truncada continua sendo risco para spec —, e
trocar a saída. Em vez de "conseguir o binário original em espanhol resolveria
isso", dizer que o próprio `.exe` carrega duas cópias mortas do bloco de
literais, que **três** mensagens têm gêmea com texto diferente, e que o
`wte/re/strings.tsv` marca essas com `gemea_difere` na coluna `suspeita_patch`.
O binário espanhol continua sendo bom ter, e continua não sendo bloqueante — só
deixa de ser a única rota.

### Arquivo: `docs/tasks/progresso.md`

A pendência externa "Binário original em espanhol seria bom ter" passa a citar a
rota interna: a frase "recuperar o original devolveria as mensagens inteiras"
vira "as três mensagens em que isso importa já têm cópia legível dentro do
`.exe` (WTE-TASK-05)". O item continua na lista — ele não deixa de ser desejável,
deixa de ser necessário.

**Só o texto da pendência.** Nenhuma célula de tabela do `progresso.md` é tocada
por esta correção — o número da linha "Strings com padding do tradutor | 70" é da
WTE-TASK-09.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-WTE-LAZARUS.md` | modificar — §8.8 |
| `docs/tasks/progresso.md` | modificar — texto da pendência externa |

## Verificação

- [ ] `grep -n "binário original em espanhol" docs/PLAN-WTE-LAZARUS.md
      docs/tasks/progresso.md` mostra as duas passagens já com a rota interna
- [ ] A §8.8 cita `gemea_difere` e o caminho do `strings.tsv`
- [ ] O número "70" continua onde estava, para a WTE-TASK-09 reconciliar
- [ ] `python3 wte/tools/dump_strings.py --check` verde (nenhum gerado tocado)
- [ ] Links de markdown conforme `.claude/rules/links.md`
- [ ] `roms/` intocada; `we-team-editor.exe` aberto só para leitura

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
