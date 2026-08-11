---
id: CORR-WTE-058
title: "Correção: o `visual.md` manda rodar o `capture_forms.sh`, que a WTE-TASK-25 removeu"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-058: documentos que a remoção do andaime deixou apontando para o vazio

## Problema identificado

A [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md) removeu, de propósito e com
razão escrita, o andaime `--show` do `wtemain.pas` e o
`wte/tools/capture_forms.sh`, que dependia dele. O Log da décima passagem
registra até como a dependência apareceu: *"Remover o `--show` quebrou o
`capture_forms.sh` em silêncio — nada apontava a dependência. Achado por `grep`,
não por teste."*

O `grep` não alcançou os markdowns. Ficaram três sítios apontando para coisa que
não existe mais:

1. **`wte/re/visual.md`, linha 12** — a seção "Reproduzir o lado port" traz um
   bloco de shell com `bash wte/tools/capture_forms.sh`. O arquivo foi deletado
   no mesmo commit; o comando falha com `No such file or directory`.
2. **`wte/re/visual.md`, linha 19** — a tabela de estado credita as 18 capturas
   do lado port ao `--show`, "o andaime da WTE-TASK-11", em presente.
3. **`wte/re/visual.md`, linha 293** — "o que o `capture_forms.sh` faz:
   `xdotool windowraise` e recorte de `-window root`" descreve uma ferramenta
   ausente como se estivesse na árvore.

O `visual.md` **é entrada do `check_fase2.py`**, não saída: o gerador o lê para
montar o `fase-2.md` e não confere se as ferramentas que ele cita existem. Por
isso o `make -C wte check` continua verde com o comando quebrado dentro.

Junto vai uma segunda desatualização, do mesmo commit e da mesma natureza: a
árvore "Estrutura de pastas (estado final esperado)" do
[`progresso.md`](/docs/tasks/progresso.md) lista quatro ferramentas da
WTE-TASK-25 (`dump_campos.py`, `dump_arranque.py`, `dump_auxiliares.py`,
`check_barras.py`) e **não** lista as outras que a mesma task criou, nem a casa
nova dos corpos escritos à mão.

## Evidência

```
$ ls wte/tools/capture_forms.sh
ls: cannot access 'wte/tools/capture_forms.sh': No such file or directory

$ grep -n 'capture_forms\|`--show`' wte/re/visual.md
12:bash wte/tools/capture_forms.sh
19:| App Lazarus | **18 de 18**, por `--show`, o andaime da WTE-TASK-11 |
293:`ed.exe`, com outra causa. A saída, e o que o `capture_forms.sh` faz:

$ grep -rn -- '--show' wte/src/wtemain.pas
121:// O `--show` FOI REMOVIDO na WTE-TASK-25, e ele tinha dono e prazo desde que
127:// ele o `AchaFormulario`, que so o servia.

$ make -C wte check   # verde, com o comando quebrado dentro do visual.md
>> check_fase2.py --check
1 arquivo em dia com os produtos da fase 2 (wte/src, wte/forms,
published_methods.tsv, visual.md, eventos.md)
```

Ausentes da árvore do `progresso.md`, todos produtos da WTE-TASK-25 e todos na
árvore de verdade:

| Caminho | Passagem que o criou |
|---|---|
| `wte/src/impl/` (os `.inc` e os `.aux.inc`) | 1ª e 5ª |
| `wte/src/we2002_estado.pas` | 1ª |
| `wte/tools/compara_tela.py`, `compara_tela.sh` | 8ª |
| `wte/tools/check_lcl_combo.py` | 5ª |

A mesma árvore ainda diz `wte/src/ep2002_*.pas ← WTE-TASK-10 (gerado) + 25-28
(corpos)`, e a decisão da 1ª passagem é justamente que **os corpos não moram
lá**: o `.pas` é gerado e diz NÃO EDITAR À MÃO; o corpo entra por
`{$I impl/<unidade>.<handler>.inc}`.

## Causa raiz

Remover uma ferramenta é mudança de árvore, e a varredura que a acompanhou foi
por código; o documento que ensina a reproduzi-la ficou fora do alcance.

## Correção

### Arquivo: `wte/re/visual.md`

Nas três linhas, dizer o que passou a valer:

- a reprodução do lado port não é mais um script — a WTE-TASK-25 pôs navegação
  de verdade no lugar do andaime, e quem dirige o app hoje é o
  [`compara_tela.sh`](../../wte/tools/compara_tela.sh) (e será a
  [WTE-TASK-37](/docs/tasks/37-reconferencia-de-ui.md), que reconfere a UI com a
  lógica ligada);
- as 18 capturas **estão commitadas** em `wte/re/visual/lazarus/` e continuam
  válidas: o que sumiu foi a maneira de refazê-las, não o resultado. Diga isso
  em vez de apagar a história — o `--show` e o `capture_forms.sh` explicam por
  que aquelas capturas existem;
- a nota das duas armadilhas de captura (`windowraise`, `-window root`) é
  conhecimento que sobrevive à ferramenta. Reescrever no passado, nomeando a
  task que a retirou.

### Arquivo: `docs/tasks/progresso.md`

Acrescentar à árvore, com a task de origem ao lado, como as demais linhas:
`src/impl/`, `src/we2002_estado.pas`, `tools/compara_tela.py`,
`tools/compara_tela.sh`, `tools/check_lcl_combo.py`. E corrigir a linha dos
`ep2002_*.pas`: gerado pela WTE-TASK-10, com os corpos das 25-28 **incluídos de
`src/impl/`**, não escritos dentro.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/visual.md` | modificar |
| `docs/tasks/progresso.md` | modificar |

## Verificação

- [x] `grep -rn 'capture_forms' wte/ docs/` só devolve `docs/tasks/` (história de
      task já concluída) e a linha do `visual.md` que **narra** a remoção — em
      `wte/` sobraram as duas linhas de narração, nas linhas 11 e 302
- [x] Todo comando em bloco de shell do `visual.md` existe e roda — sobraram
      dois blocos, o `wine we-team-editor.exe` e um Python inline; nenhum
      script da árvore é invocado
- [x] Cada arquivo da árvore do `progresso.md` existe no disco, e cada produto da
      WTE-TASK-25 aparece nela — os cinco acrescentados existem; o resto da
      árvore é **estado final esperado** e tem entrada de task não executada,
      por construção
- [x] `make -C wte check` verde
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-11

**Resumo do que foi feito:**

Os três sítios do `visual.md` foram reescritos no passado, nomeando a
WTE-TASK-25 como quem retirou o andaime, e **sem apagar a história**: as 22
capturas continuam commitadas e válidas, e o que sumiu foi a maneira de refazer
as 18. O destino ficou escrito — quem dirige o app hoje é o `compara_tela.sh`,
que alcança o `MainForm`; os outros 17 voltam com a WTE-TASK-37.

A nota das duas armadilhas de captura foi para o passado quanto à ferramenta e
ficou no presente quanto ao conhecimento: `-window root` mais recorte por
geometria é exatamente o que o `compara_tela.sh` faz, pela mesma razão.

Na árvore do `progresso.md`, cinco linhas novas e uma corrigida. A corrigida é a
que mais importa: `ep2002_*.pas` era `WTE-TASK-10 (gerado) + 25-28 (corpos)`, o
oposto da decisão da 1ª passagem — o `.pas` é gerado e diz NÃO EDITAR À MÃO, e o
corpo entra por `{$I impl/<unidade>.<handler>.inc}`.

**Problemas encontrados:**

Nenhum. O `make -C wte check` fica verde antes e depois, e é o ponto da
correção: o `visual.md` é **entrada** do `check_fase2.py`, não saída, então
nenhum gate olhava para dentro dele.

**Arquivos criados/modificados:**

- `wte/re/visual.md` — as três linhas, mais o destino (WTE-TASK-37) e o
  ponteiro para o `compara_tela.sh`
- `docs/tasks/progresso.md` — `src/impl/`, `src/we2002_estado.pas`,
  `tools/check_lcl_combo.py`, `tools/compara_tela.py`/`.sh` na árvore, e a
  linha dos `ep2002_*.pas` corrigida
