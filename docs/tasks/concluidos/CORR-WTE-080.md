---
id: CORR-WTE-080
title: "Correção: o golden-14-uniforme falha por tempo em boa parte das corridas"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-080: o `golden-14-uniforme` falha por tempo em boa parte das corridas

## Problema identificado

O gate do `grabar_camisetaClick` — o
[`golden-14-uniforme`](../../../wte/tests/roteiros/golden-14-uniforme.txt), da
[WTE-TASK-29](/docs/tasks/concluidos/29-camisa-e-bandeira-2d.md) — **não fecha de forma
repetível**. Nesta revisão foram quatro tentativas do modo `controle` na mesma
máquina, sem mudar uma linha da árvore: **três falharam por espera de janela e
uma passou.** A que passou deu `PASSOU: byte-identico`, com artefato de 30.956
bytes dos dois lados — o resultado que a task afirma. O modo `golden` passou de
primeira, também byte-idêntico.

O problema não é o veredito: é que o veredito custa repetição. Gate que precisa
ser rodado de novo até ficar verde deixa de separar "o port diverge" de "a
janela demorou", e é justamente essa separação que faz o golden valer alguma
coisa.

Duas assinaturas diferentes apareceram, e vale registrar as duas porque
provavelmente têm causas distintas:

1. **`ERRO: janela 'Extrair Uni do jogo' nao apareceu em 30s`** — o app estava
   de pé, o roteiro clicou o botão em `(412,292)` e o diálogo não veio no
   limite. É o passo desta task;
2. **`ERRO: janela 'Abre' nao apareceu em 30s`** — o app não chegou a mostrar o
   primeiro diálogo. Aconteceu nas duas corridas lançadas logo depois de uma
   anterior ter sido morta, e o log do Wine daquela corrida mostra os serviços
   do prefixo subindo (`wineusb`, `winebus`, `mountmgr`) — cheiro de prefixo
   ainda ocupado pela corrida anterior, e portanto do harness, não do roteiro.

Que o `golden-01-arranque` tenha passado de primeira no meio da série ajuda a
localizar: o harness sobe, e o que falha é tempo.

## Evidência

Quatro corridas de `--modo controle --artefato saida.bin`, em sequência:

| # | resultado |
|---|---|
| 1 | `ERRO: janela 'Extrair Uni do jogo' nao apareceu em 30s` |
| 2 | `ERRO: janela 'Abre' nao apareceu em 30s` |
| 3 | `ERRO: janela 'Abre' nao apareceu em 30s` |
| 4 | `PASSOU: byte-identico`; `artefato do lado a: 30956 bytes` |

No meio da série, o roteiro mais curto do gate fechou sem repetição:

```text
>> modo controle, roteiro golden-01-arranque.txt, imagem japanese-shift-jis.bin
>> oraculo: fim, sem violacao de acesso
>> comparando
PASSOU: byte-identico
```

E o `golden` do próprio 14, rodado depois:

```text
>> artefato do lado b: 30956 bytes
>> comparando o artefato
   saida.bin: byte-identico nos dois lados
>> comparando
PASSOU: byte-identico
```

O limite de espera é o default do
[`roteiro.sh`](../../../wte/tools/roteiro.sh):

```bash
espera_janela() {
  local nome="$1" limite="${2:-30}" i=0 r
```

## Causa raiz

Espera de janela dimensionada para a máquina descarregada, e nenhuma folga
entre o fim de uma corrida e o início da seguinte no mesmo prefixo Wine.

## Correção

Duas frentes, e a segunda é a que serve para todos os roteiros.

### Arquivo: `wte/tests/roteiros/golden-14-uniforme.txt`

O passo do `Extrair Uni do jogo` vem logo depois da troca de time, que é a ação
mais cara do roteiro (`~ 6`). Subir a espera daquele ponto — e **anotar por
quê**, como os outros roteiros já fazem — custa segundos e tira a falha #1.

### Arquivo: `wte/tools/roteiro.sh` (ou `golden_run_wte.sh`)

Para a falha #2, o conserto é do harness e vale para todo roteiro:

- esperar o `wineserver` do prefixo sumir antes de lançar o lado seguinte, em
  vez de lançar logo após o `-k`; e
- quando `espera_janela` estourar **na primeira janela do roteiro**, dizer que
  o app não subiu — hoje a mensagem é a mesma de um diálogo que não veio, e as
  duas mandam procurar em lugares diferentes.

Se em vez disso a decisão for aceitar a repetição, então ela tem de ser
**explícita**: uma tentativa extra automática, anunciada em uma linha
(`>> tentativa 2 de 2`), para que a flutuação apareça no log em vez de sumir
na memória de quem rodou.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tests/roteiros/golden-14-uniforme.txt` | modificar |
| `wte/tools/roteiro.sh` | modificar |
| `wte/tools/golden_run_wte.sh` | modificar |

## Verificação

- [x] `bash wte/tools/golden_check.sh wte/tests/roteiros/golden-14-uniforme.txt
      --modo controle --artefato saida.bin` verde em **três** corridas
      seguidas, sem intervenção — artefato de 30.956 B nos dois lados nas três.
      **Ressalva:** as três corridas de reprodução, ANTES de qualquer conserto,
      também deram verde (3 de 3), com a máquina descarregada
- [x] o modo `golden` continua verde, com artefato de 30.956 B nos dois lados
- [x] uma falha de "app não subiu" e uma de "diálogo não veio" produzem
      mensagens distintas — medido pelo `test_roteiro.py`, com dublê de janela
- [x] `golden-01-arranque` continua verde
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-21

**Resumo do que foi feito:**

**A intermitência não reproduziu.** Três corridas de `--modo controle
--artefato saida.bin` antes de tocar em qualquer arquivo deram
`PASSOU: byte-identico`, com artefato de 30.956 B nos dois lados — 3 de 3,
contra as 3 falhas em 4 que a revisão mediu. A máquina estava descarregada, que
é justamente a condição para a qual a espera de 30s foi dimensionada. Por isso
a correção **não** foi tratada como envelhecida: falha por tempo é
probabilística, e "não apareceu hoje" não é "não existe". O que foi feito é a
parte que vale independente do sorteio, e as três frentes que o enunciado pede:

1. **`espera: <seg>`, diretiva nova do dialeto de roteiro.** Sobe o limite da
   **próxima** janela e volta ao default depois. Vale só para a próxima de
   propósito: espera longa em todo passo esconde app que não subiu. O default
   virou `ROTEIRO_ESPERA_PADRAO` (30s), variável para o teste poder encurtá-lo
   — medir que a diretiva vale só para a próxima custaria 30s de bateria com o
   valor de produção;
2. **`golden-14-uniforme.txt`** ganhou `espera: 90` no passo do
   `Extrair Uni do jogo`, com o comentário do porquê: ele vem logo depois da
   troca de time, a ação mais cara do roteiro (`~ 6`);
3. **`golden_run_wte.sh`** passou a **esperar** o `wineserver` sair, e não só
   pedir. O `-k` pede; o `-w` volta quando o servidor do prefix realmente saiu.
   Sem ele o lado B era lançado sobre um prefix ainda em desmontagem — a
   explicação mais provável para as duas falhas de `Abre`. Com `timeout 30`
   para o gate não pendurar se o servidor travar;
4. **As duas falhas de espera passaram a dizer coisas diferentes.** Se a
   **primeira** janela do roteiro nunca aparece, quem não subiu foi o app, e o
   log a olhar é o do Wine ou o da LCL; se já havia janela achada, o app está
   vivo e o que não veio foi o diálogo daquele passo.

O `test_roteiro.py` é novo e mede as duas coisas com dublê de janela — não
precisa de `DISPLAY`, de Wine nem do `.exe`, e roda em 7s. Nada media o
`roteiro.sh` até aqui, que é como o dialeto podia mudar em silêncio.

**Problemas encontrados:**

A varredura de discrepância puxou duas linhas do `wte/tools/README.md` que
descreviam comportamento corrente e estavam falsas: a do `roteiro.sh` dizia "a
fixacao do `:99`" (é `WTE_DISPLAY`, `:98` de default, desde a WTE-TASK-28), e a
do `golden_run_laz.sh` dizia que ele reprova roteiro com `! tecla`/`! texto` —
recusa que saiu na WTE-TASK-26, quando o `xdotool windowfocus` mostrou que a
tecla chega ao GTK2 sem window manager. As duas foram reescritas, a segunda
como história.

**Arquivos criados/modificados:**

- criados: `wte/tools/test_roteiro.py`
- modificados: `wte/tools/roteiro.sh`, `wte/tools/golden_run_wte.sh`,
  `wte/tests/roteiros/golden-14-uniforme.txt`,
  `wte/tests/roteiros/README.md`, `wte/tools/README.md`
