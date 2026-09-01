---
id: CORR-WTE-077
title: "Correção: a §5.3 do plano ainda manda varrer pixel, e a WTE-TASK-29 mediu que é paleta"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-077: a §5.3 do plano ainda manda varrer pixel, e a WTE-TASK-29 mediu que é paleta

## Problema identificado

A §5.3 do [`docs/PLAN-WTE-LAZARUS.md`](/docs/PLAN-WTE-LAZARUS.md) descreve o
algoritmo do render 2D assim:

> A renderização usa os 105 `uniformes2d/*.bmp` como base e aplica cor. Em
> Pascal isso é `TBitmap` + **varredura de pixel**; a LCL dá `TLazIntfImage`
> para acesso rápido.

A [WTE-TASK-29](/docs/tasks/concluidos/29-camisa-e-bandeira-2d.md) mediu e **refutou**: o
original não varre pixel nenhum. As três rotinas de desenho posicionam o
arquivo em `0x36` — a primeira entrada de paleta, logo depois dos 54 bytes de
cabeçalho — e reescrevem as primeiras entradas. É o primeiro critério de
conclusão da task, e o `wte/re/render2d.md` traz o disassembly.

A task registrou a correção **dentro dela mesma**, num aviso em bloco de
citação. O plano continua dizendo o contrário — e o
[`progresso.md`](/docs/tasks/concluidos/progresso.md) diz, na abertura, que
"divergência entre os dois se resolve **a favor do plano**". Hoje essa regra
aponta para a versão errada.

É a mesma forma da [CORR-WTE-072](/docs/tasks/concluidos/CORR-WTE-072.md): documento que
guardou uma previsão depois de a medição ter chegado.

## Evidência

O que o plano diz (linha 939):

```text
isso é `TBitmap` + varredura de pixel; a LCL dá `TLazIntfImage` para acesso
```

O que a ferramenta lê do `.exe` (`wte/re/render2d.tsv`, gerado pelo
`dump_render2d.py`, `--check` verde):

```text
desenhista	0x00405270	16	bandeira do titular; arquivos=1
desenhista	0x00405468	16	bandeira do reserva; arquivos=1
```

E o `wte/re/render2d.md`, na seção das três rotinas:

> **A bandeira reescreve 16 entradas e o uniforme reescreve 15.** O laço do
> uniforme para em `cmp esi,0xf`, o da bandeira em `cmp esi,0x10`, e o uniforme
> roda o bloco inteiro duas vezes — uma para `camiseta<n>.bmp` e outra para
> `pantalon<n>.bmp`, cada uma com o seu `push 0x36`.

`0x36` = 54 = o fim do cabeçalho BMP; nenhuma das três toca área de pixel. O
`TLazIntfImage` continua sendo a escolha certa no port, mas por outro motivo —
o port precisa do **índice** de cada pixel, e o leitor de BMP da LCL entrega o
bitmap já convertido para 32 bpp com a paleta consumida.

## Causa raiz

Hipótese de projeto escrita em 2026-08-05 e mantida no plano depois de a
WTE-TASK-29 medir o contrário em 2026-08-20.

## Correção

### Arquivo: `docs/PLAN-WTE-LAZARUS.md`

Reescrever o trecho da §5.3 com o resultado medido, mantendo a hipótese
antiga como história — é a forma que este repositório já usa para previsão
derrubada por medição. Algo como:

```markdown
A renderização usa os 105 `uniformes2d/*.bmp` como base e aplica cor **na
paleta**: as três rotinas de desenho posicionam o arquivo em `0x36`, a
primeira entrada, e reescrevem as primeiras — 16 na bandeira, 15 no uniforme,
duas vezes. **Nenhuma varre pixel.** (Esta seção supunha `TBitmap` +
varredura de pixel até 2026-08-20, quando a WTE-TASK-29 mediu; o
`wte/re/render2d.md` traz o disassembly.) O `TLazIntfImage` continua sendo o
certo no port, por outro motivo: ele precisa do **índice** de cada pixel, e o
leitor de BMP da LCL entrega o bitmap já convertido para 32 bpp, com a paleta
consumida — daí a `wte/src/we2002_bmp.pas`.
```

O aviso equivalente que já existe na WTE-TASK-29 pode então apontar para a
§5.3 em vez de contradizê-la.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-WTE-LAZARUS.md` | modificar |

## Verificação

- [x] `grep -n 'varredura de pixel' docs/PLAN-WTE-LAZARUS.md` devolve uma linha
      só, e é a menção histórica marcada como tal (linha 944)
- [x] A §5.3 e o `wte/re/render2d.md` dizem a mesma coisa sobre paleta — `0x36`
      como primeira entrada, 16 na bandeira, 15 no uniforme, o uniforme duas
      vezes, nenhuma varredura
- [x] `make -C wte check` verde — 695 testes, `OK (skipped=1)`, rc=0
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-21

**Resumo do que foi feito:**

A §5.3 passou a descrever o algoritmo medido: cor na paleta, arquivo
posicionado em `0x36`, 16 entradas na bandeira e 15 no uniforme, o bloco do
uniforme rodando duas vezes (`camiseta<n>.bmp` e `pantalon<n>.bmp`), e nenhuma
varredura de pixel. A hipótese antiga ficou como história, entre parênteses e
datada, que é a forma que este repositório já usa para previsão derrubada por
medição — e aponta para o `wte/re/render2d.md`, onde está o disassembly.

O `TLazIntfImage` continua recomendado, agora pelo motivo certo: o port precisa
do **índice** de cada pixel, e o leitor de BMP da LCL entrega o bitmap
convertido para 32 bpp com a paleta consumida. Daí a `we2002_bmp.pas`.

**Problemas encontrados:**

Nenhum. O aviso equivalente da WTE-TASK-29 não precisou de conserto: ele se
refere ao parágrafo do próprio arquivo, logo acima dele, e não à §5.3 — não
havia contradição a desfazer.

**Arquivos criados/modificados:**

- `docs/PLAN-WTE-LAZARUS.md`
