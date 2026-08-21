---
id: CORR-WTE-080
title: "Correção: o golden-14-uniforme falha por tempo em boa parte das corridas"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-080: o `golden-14-uniforme` falha por tempo em boa parte das corridas

## Problema identificado

O gate do `grabar_camisetaClick` — o
[`golden-14-uniforme`](../../wte/tests/roteiros/golden-14-uniforme.txt), da
[WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md) — **não fecha de forma
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
[`roteiro.sh`](../../wte/tools/roteiro.sh):

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

- [ ] `bash wte/tools/golden_check.sh wte/tests/roteiros/golden-14-uniforme.txt
      --modo controle --artefato saida.bin` verde em **três** corridas
      seguidas, sem intervenção
- [ ] o modo `golden` continua verde, com artefato de 30.956 B nos dois lados
- [ ] uma falha de "app não subiu" e uma de "diálogo não veio" produzem
      mensagens distintas
- [ ] `golden-01-arranque` continua verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
