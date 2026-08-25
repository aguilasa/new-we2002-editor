---
id: CORR-WTE-105
title: "Correção: a pendência que a WTE-TASK-34 encaminhou para a 35 não existe na 35"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-105: pendência encaminhada para a WTE-TASK-35 e ausente dela

## Problema identificado

A [WTE-TASK-34](/docs/tasks/34-bateria-golden-completa.md) fecha com uma
pendência nomeada, na seção *"O que ficou pendente"*:

> **O vaivém dos cobradores não foi provado, só coberto.** Encaminhado para a
> [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md), que é quem registra
> divergência deliberada com evidência.

A WTE-TASK-35 **não sabe disso**. O markdown dela tem uma seção
*"Candidatas já conhecidas antes de a task rodar"* com nove entradas — o sufixo
` [Lazarus]`, a tolerância de cor, os cinco glifos, o preço do 23º jogador,
o limite do `edit_nombre1`, e outras — e nenhuma é esta.

Quem executar a 35 lê o arquivo dela, não o Log da 34. Pendência encaminhada
por prosa de uma task para outra, sem entrada no destino, é a mesma classe que
a [CORR-WTE-081](/docs/tasks/CORR-WTE-081.md) pagou para descobrir na
WTE-TASK-30 — *"elas precisam de dono nomeado antes que a 31 rode, porque a 31 é
fechamento e não implementa"* — e que a terceira passagem da
[WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) batizou de **prosa vencida**:
documento que envelhece sozinho enquanto outro o lê como estado corrente.

A 35 está `⬜ Pendente` e é a próxima da fase 6. A janela para consertar isto
antes de custar alguma coisa é agora.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -n "Encaminhado para a" docs/tasks/34-bateria-golden-completa.md
grep -cn "vaivém\|vaivem\|cobrador\|OFS_KICKER\|idempot" docs/tasks/35-divergencias-deliberadas.md
grep -n "^- \*\*" docs/tasks/35-divergencias-deliberadas.md
```

```text
docs/tasks/34-bateria-golden-completa.md:193:  **O vaivém dos cobradores não foi provado, só coberto.** Encaminhado para a

0

15:- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 6 item 2 e §0.
54:- **Sufixo ` [Lazarus]` no `Caption` dos 18**
69:- **Tolerância de cor do render 2D** (WTE-TASK-29), se a igualdade exata não
71:- **Cinco glifos que não acinzentam** — medido pela
101:- **Cara, cabelo e barba da ficha não redesenham** — decidido pela
171:- **O limite do `edit_nombre1` na European Deluxe** — medido pela
199:- **O preço do 23º jogador nunca é gravado** — medido pela
245:- **`TStaticText` no GTK2** (§8.9), se o fundo não puder ficar idêntico.
246:- **Rótulos cortados por fonte substituta** — acontece nos dois lados, e talvez
248:- **Comportamento de truncamento de campo** (WTE-TASK-36), se o Pascal não
```

Zero ocorrências de `vaivém`, `cobrador`, `OFS_KICKER` ou `idempot` no arquivo
da task que deveria recebê-los. O único outro registro fora da 34 é o
`progresso.md`, na linha do critério — que também é da 34.

## Causa raiz

O encaminhamento foi escrito no Log da task que fechava, e não na task que
recebe.

## Correção

### Arquivo: `docs/tasks/35-divergencias-deliberadas.md`

Acrescentar a entrada à seção *"Candidatas já conhecidas antes de a task
rodar"*, no formato das outras — e ela é **candidata de tipo diferente das
nove**, o que vale dizer: as outras já foram medidas e esperam decisão; esta
espera **medição**, e a medição está especificada.

Esboço do que a entrada precisa dizer:

> - **O vaivém dos cobradores na segunda gravação** — encaminhado pela
>   [WTE-TASK-34](/docs/tasks/34-bateria-golden-completa.md).
>   *Natureza:* a medir. A não-idempotência que o plano cita é do **`ed.exe`**
>   (`Load`+`Save` trocando `cobrador[0]`/`[1]` de clube de ML); o `wte.exe` é
>   outro binário e o comportamento dele nesse caminho **não foi medido**.
>   *Como medir:* o terceiro ponto — a imagem depois de **uma** gravação de
>   tática contra a de **duas**, pelo par `golden-17-tatica` ×
>   `golden-24-gravacao-dupla`, num time em que `cobrador[0] != cobrador[1]`
>   (ver a [CORR-WTE-104](/docs/tasks/CORR-WTE-104.md), que é pré-requisito:
>   hoje o roteiro usa o time 2, onde os dois são iguais e a troca é invisível).
>   *Decisão:* se as imagens diferirem, entra aqui como divergência com o offset
>   medido; se não, é **resultado negativo** e o que entra é a correção do
>   enunciado da fase 6, que hoje atribui ao `wte.exe` um comportamento herdado
>   de outro binário.

### E o hábito, se valer fechar a porta

Esta é a segunda vez que uma task encaminha item por prosa
([CORR-WTE-086](/docs/tasks/CORR-WTE-086.md) foi a primeira, com o dono errado).
O remédio barato é de processo: o `01-executar.md` pedir que
*"encaminhado para a WTE-TASK-NN"* só valha quando a linha existir **na NN** —
e o `/revisar` já confere, porque é o que esta correção acabou de fazer à mão.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/35-divergencias-deliberadas.md` | modificar |
| `docs/prompts/01-executar.md` | modificar (opcional — a regra de encaminhamento) |

## Verificação

- [x] `grep -c "cobrador" docs/tasks/35-divergencias-deliberadas.md` maior que
      zero — são **5**
- [x] A entrada nomeia a CORR-WTE-104 — não mais como pré-requisito da medição,
      e sim como quem a fez; ver os Problemas encontrados
- [x] `make -C wte check` verde (789 testes)
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-25

**Resumo do que foi feito:**

A entrada entrou na seção *"Candidatas já conhecidas antes de a task rodar"* da
WTE-TASK-35, no formato das outras (*O que se afirmava / Natureza / Decisão /
Evidência / Onde o teste sabe*). De 0 para 5 ocorrências de `cobrador` no
arquivo.

E entrou o remédio de processo, que a CORR marcava como opcional e a segunda
reincidência tornou barato: o `01-executar.md` ganhou um bloco irmão do que já
existia para o quadro da WTE-TASK-09 — *"pendência encaminhada só vale com a
linha escrita NA task de destino"* —, e o wrapper
`.claude/commands/executar.md` reafirma o mesmo, porque é ele que enumera o
fechamento com outras palavras.

**Problemas encontrados:**

**A entrada mudou de natureza entre a abertura da CORR e a execução, e para
melhor.** A CORR escreveu o esboço com *"Natureza: a medir"* e a
[CORR-WTE-104](/docs/tasks/CORR-WTE-104.md) como **pré-requisito** da medição.
A 104 rodou primeiro neste mesmo lote e **mediu**: uma gravação e duas dão a
mesma imagem, com os cobradores intactos. Escrever a entrada como "a medir"
teria produzido prosa vencida no ato — exatamente o defeito que esta correção
existe para consertar.

A entrada foi escrita no estado pós-104: **resultado negativo**, com os números
e o motivo de o time importar. O que fica para a WTE-TASK-35 decidir não é uma
divergência a reproduzir — é o enunciado da fase 6, que atribui ao editor um
comportamento do `ed.exe`. A própria CORR previa o desfecho ("*se não, é
resultado negativo e o que entra é a correção do enunciado da fase 6*"), então
o esboço não estava errado; só foi resolvido um degrau adiante do que ele
esperava.

**Arquivos criados/modificados:**

- `docs/tasks/35-divergencias-deliberadas.md` — a entrada
- `docs/prompts/01-executar.md` — a regra de encaminhamento
- `.claude/commands/executar.md` — o mesmo rito no wrapper
