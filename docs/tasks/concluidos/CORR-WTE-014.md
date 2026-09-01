---
id: CORR-WTE-014
title: "Correção: o 197 bitmaps ficou sem dono — não está no quadro de reconciliação da WTE-TASK-09 e sobrevive em nove lugares"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-014: são 198, e o número errado não tem quem o conserte

## Problema identificado

A WTE-TASK-08 mediu **198** bitmaps e registrou que a §1.8 do plano soma errado:

> **198 é o número certo**; a §1.8 do plano lista as cinco linhas corretas e erra
> a soma na prosa ("197 bitmaps"). Reconciliação é da WTE-TASK-09.

O encaminhamento é o certo — reconciliar a §1 é da
[WTE-TASK-09](/docs/tasks/concluidos/09-fechamento-fase-1.md). Só que o **quadro de
reconciliação da 09 não tem a linha dos assets**:

| Afirmação do plano | Onde remedir |
|---|---|
| 18 formulários, ~430 componentes | `dfm_extract.py` |
| 96 handlers | `dump_published.py` |
| 19 de 69 offsets | `dump_offsets.py` |
| 70 strings com padding | `dump_strings.py` |
| 13 unidades `Tep2002_*` | `objdump -x` |
| 322 imports, sendo 300 de `rtl60.bpl`/`vcl60.bpl` (§1.2) | `dump_units.py` |

Seis linhas, nenhuma sobre bitmap. A última entrou pela
[CORR-WTE-012](/docs/tasks/concluidos/CORR-WTE-012.md), aberta na revisão da WTE-TASK-07
pela mesma razão: número medido, encaminhado para a 09, e ausente do quadro que
a 09 executa. É a segunda ocorrência do mesmo buraco de processo.

Enquanto isso o número errado está em **nove** lugares, incluindo dois dentro do
próprio plano — um deles a três linhas do bloco que lista as cinco pastas somando
198:

```
docs/PLAN-WTE-LAZARUS.md:123  | Bitmaps externos em `image/` | 197 |
docs/PLAN-WTE-LAZARUS.md:301  197 bitmaps e um blob, todos em formato aberto
docs/tasks/progresso.md:23    | Convenção dos 197 bitmaps e do `dat.bin` |
docs/tasks/progresso.md:179   - [x] Convenção de nome dos 197 bitmaps resolvida
docs/tasks/progresso.md:305   Os 197 BMP e o `dat.bin` ficam com o usuário
docs/tasks/progresso.md:397   | Assets externos | 197 `.bmp` + `dat.bin` … |
docs/tasks/09-fechamento-fase-1.md:35  parte dos 197 pode ser irrelevante
docs/tasks/38-nome-e-linhagem.md:60    sem os 197 BMP o app não desenha camisa
docs/tasks/39-empacotamento.md:53      Os 197 BMP e o `dat.bin` não são redistribuídos
```

As duas últimas são tarefas da fase 7 ainda por executar: elas vão pedir
mensagem de erro e regra de empacotamento sobre uma contagem que não existe.

## Evidência

O total, e a soma das cinco linhas que o próprio plano lista:

```
$ find we-team-editor -iname '*.bmp' | wc -l
198

$ for d in banderas uniformes2d pelo barba; do
    printf "%-14s %s\n" "$d" "$(find we-team-editor/image/$d -iname '*.bmp' | wc -l)"; done
banderas       53
uniformes2d    105
pelo           32
barba          7
$ ls we-team-editor/image/*.bmp
we-team-editor/image/careto_base.bmp
```

`53 + 105 + 32 + 7 + 1 = 198`. O bloco da §1.8 traz exatamente esses cinco
números; só a frase seguinte diz 197.

A divergência não é nova — a WTE-TASK-02 já a tinha medido e registrado no
`wte/README.md` ("**198, não 197**. A §1 do plano registra 197 `.bmp`;
`find -iname '*.bmp'` acha **198**"). Ela sobreviveu a duas tarefas que a
mediram porque nenhuma tinha mandato para corrigir a §1, e a tarefa que tem não
sabe que precisa.

## Causa raiz

O quadro de reconciliação da WTE-TASK-09 foi escrito com cinco linhas de
exemplo, e não é revisado quando uma tarefa nova mede um número da §1 que não
está nele.

## Correção

### Arquivo: `docs/tasks/concluidos/09-fechamento-fase-1.md`

Acrescentar a linha que falta ao quadro:

```markdown
| 197 bitmaps + `dat.bin` (§1.2 e §1.8) | `find -iname '*.bmp'` — ver [`assets.md`](../../wte/re/assets.md) |
```

Não há gerador para assets (a WTE-TASK-08 decidiu rota inline, com o comando ao
lado de cada número), então a coluna "onde remedir" aponta o comando e o
documento que o executa.

Acrescentar também, ao texto da tarefa, a instrução de **varrer** os sítios: a
09 corrige o plano, mas os quatro do `progresso.md` e os dois das tarefas 38 e
39 continuariam errados. O `grep -rn "197" docs/` é o comando.

### Arquivo: `docs/prompts/01-executar.md`

Uma linha na seção de fechamento: quando uma tarefa medir um número da §1 do
plano que o quadro da WTE-TASK-09 não lista, acrescentar a linha ao quadro em
vez de só registrar no Log. É o que impede a terceira ocorrência — esta é a
segunda, depois da CORR-WTE-012.

**Fora de escopo:** corrigir os nove sítios aqui. Quem corrige é a WTE-TASK-09,
que é a dona da reconciliação; esta correção só garante que ela saiba.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/concluidos/09-fechamento-fase-1.md` | modificar |
| `docs/prompts/01-executar.md` | modificar |

## Verificação

- [ ] O quadro da WTE-TASK-09 tem a linha dos bitmaps, com o comando que os conta
- [ ] O texto da 09 manda varrer os sítios, não só a §1
- [ ] `find we-team-editor -iname '*.bmp' | wc -l` continua devolvendo 198, e as
      cinco linhas da §1.8 somam esse valor
- [ ] `grep -rn "197" docs/ | wc -l` registrado na 09 como o alvo a zerar
- [ ] O `01-executar.md` diz o que fazer quando a medição achar número da §1 fora
      do quadro
- [ ] `roms/` intocada; `we-team-editor.exe` aberto só para leitura

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-06

**Resumo do que foi feito:**

O quadro de reconciliação da WTE-TASK-09 ganhou a sétima linha — "197 bitmaps +
`dat.bin` (§1.2 e §1.8)", remedida por `find -iname '*.bmp'` com o
[`assets.md`](../../../wte/re/assets.md) ao lado, já que a WTE-TASK-08 decidiu rota
inline e não há gerador de assets. O critério de conclusão passou de "os seis
números" para "os sete".

A 09 também ganhou a seção "Varrer os sítios, não só a §1": corrigir a §1 do
plano não fecha um número errado, ele se espalha. O comando é
`grep -rn "<o número velho>" docs/ wte/re/`, e o alvo é zerar a saída **fora**
dos documentos que narram a correção — `correcoes-progresso.md`, os
`CORR-WTE-*.md` e os Logs de Execução citam o número velho por necessidade
histórica. O `wc -l` de antes e de depois vai para o `wte/re/fase-1.md`.

No `01-executar.md`, a regra que impede a terceira ocorrência entrou na seção
"4) Atualizar progresso", com as duas anteriores nomeadas
([CORR-WTE-012](/docs/tasks/concluidos/CORR-WTE-012.md) e esta): medir número da §1 que o
quadro não lista obriga a acrescentar a linha ao quadro, não só a registrar no
Log. O padrão que falhou duas vezes é o mesmo — a tarefa que mede não tem
mandato para corrigir a §1, encaminha para a 09, e a 09 executa um quadro que
não sabe do número.

**Problemas encontrados:**

Nenhum que bloqueasse. Duas observações:

- A linha 35 da própria 09 ("parte dos **197** pode ser irrelevante") é um dos
  nove sítios, e continua errada de propósito: a seção "Fora de escopo" desta
  correção reserva os nove para a WTE-TASK-09, que agora tem o comando para
  achá-los. Corrigir um aqui só moveria o alvo do `grep` sem fechar nada.
- O `grep -rn "197" docs/ | wc -l` devolve **42**, não nove: a maioria são as
  citações dentro dos próprios `CORR-WTE-*.md` e do `correcoes-progresso.md`,
  que ficam. Os nove sítios reais continuam sendo os que a seção "Problema
  identificado" lista.

**Arquivos criados/modificados:**

- `docs/tasks/concluidos/09-fechamento-fase-1.md` — linha dos bitmaps no quadro, seção de
  varredura, critério de conclusão
- `docs/prompts/01-executar.md` — a regra que impede a terceira ocorrência
