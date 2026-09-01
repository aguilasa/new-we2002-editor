---
id: CORR-WTE-120
title: "Correção: a guarda do sem_wine.sh é creditada à metade que nesta máquina não pode disparar"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-120: a guarda tem duas metades, e a prosa credita a inerte

## Problema identificado

O Log da [WTE-TASK-40](/docs/tasks/concluidos/40-verificacao-final.md) explica por que o
ambiente fabricado é honesto:

> Por isso a guarda do `sem_wine.sh` **recusa** se `wine`/`wine64`/`wineserver`
> ainda responder lá dentro: ambiente que só *parece* limpo mede tão pouco
> quanto não medir.

O cabeçalho do [`sem_wine.sh`](../../../wte/tools/sem_wine.sh) diz o mesmo. Medido
nesta revisão: **essa metade não pode disparar nesta máquina.** O `command -v`
de `wine`, `wine64`, `wineserver` e `winecfg` já falha **fora** de qualquer
namespace — o Wine daqui é o runner do Bottles, em `~/.var/app/`, e nunca
esteve no `PATH`. O próprio Log registra o fato duas linhas acima (*"não há
pacote `wine` no apt desta máquina"*) sem notar que ele desarma a cláusula que
o parágrafo seguinte credita.

Quem recusa de verdade é a **segunda** metade, que a prosa não menciona: o laço
que exige que cada alvo mascarado fique **vazio** dentro do namespace.

Não é afirmação falsa — a guarda recusa. É crédito na metade errada, e o custo
é concreto: quem simplificar o script achando que o `command -v` é a proteção
pode apagar o laço de vazio, e aí o ambiente deixa de ser limpo **sem que nada
reclame** — que é exatamente o defeito contra o qual a guarda foi escrita.

## Evidência

A cláusula creditada, fora de qualquer namespace, nesta máquina:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
command -v wine wine64 wineserver winecfg; echo "EXIT=$?"
```

```text
EXIT=1
```

Nenhum dos quatro está no `PATH` **antes** de mascarar coisa nenhuma — então,
dentro do namespace, a cláusula é verdadeira por construção.

A cláusula que tem dentes, exercitada: uma cópia do script em `/tmp` com o alvo
do Bottles **fora** das máscaras e **dentro** da lista da guarda —

```text
ERRO: /home/ingmar/.var/app/com.usebottles.bottles nao ficou vazio
EXIT=1
```

E o controle, com o script como está: a guarda passa e as sete medidas do
`nativo_check.sh` saem `ok`, com o TSV idêntico ao commitado.

| Cláusula da guarda | Pode disparar aqui? | Mencionada na prosa |
|---|---|---|
| `command -v wine/wine64/wineserver/winecfg` | **não** — nunca estiveram no `PATH` | **sim**, é a creditada |
| cada alvo mascarado tem de ficar **vazio** | **sim** — recusa, medido | não |

## Causa raiz

A guarda foi escrita para as duas formas de Wine (pacote no `PATH` e runner em
`~/.var/app/`) e a prosa descreveu só a primeira, que é a que esta máquina não
tem.

## Correção

### Arquivos: `wte/tools/sem_wine.sh` e `docs/tasks/concluidos/40-verificacao-final.md`

Escrever as duas metades, e qual delas trabalha aqui:

> A guarda tem **duas** cláusulas, e nesta máquina só a segunda tem trabalho.
> A primeira recusa se `wine`/`wine64`/`wineserver`/`winecfg` responderem no
> `PATH` — é a que pega uma máquina com o pacote do apt, e aqui ela é
> verdadeira antes de mascarar qualquer coisa. A segunda exige que **cada
> alvo** fique vazio dentro do namespace, e é ela que prova que o runner do
> Bottles — o Wine desta máquina — sumiu. **Apagar a segunda desliga a
> conferência**, mesmo com a primeira intacta.

A primeira cláusula **fica**: ela custa quatro linhas e é o que faz o script
valer noutra máquina, que é justamente o caso que a condição 3 quer sobreviver.

### Guarda

O caso plantado desta correção — alvo fora das máscaras, dentro da lista — é o
teste que falta, e ele cabe no `test_check_nativo.py` que a
[CORR-WTE-119](/docs/tasks/concluidos/CORR-WTE-119.md) pede. Um caso por cláusula:
`PATH` sujo (fabricável com um `wine` falso num diretório do `PATH`) e alvo não
vazio.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/sem_wine.sh` | modificar — o cabeçalho |
| `docs/tasks/concluidos/40-verificacao-final.md` | modificar — o parágrafo do Log |
| `wte/tools/test_check_nativo.py` | modificar — os dois casos (ver a CORR-WTE-119) |

## Verificação

- [x] O cabeçalho do `sem_wine.sh` nomeia as duas cláusulas e diz qual trabalha
      nesta máquina — e há caso de teste cobrando essa prosa
- [x] Um alvo fora das máscaras faz o script recusar, com o nome do diretório
- [x] Um `wine` falso no `PATH` faz o script recusar pela primeira cláusula
- [x] `bash wte/tools/nativo_check.sh --imagem <cópia>` continua com **7 de 7**
      `ok`, e o `nativo.tsv` saiu idêntico ao commitado
- [x] `roms/` intocada — a corrida usou cópia no scratchpad, já removida

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-26

**Resumo do que foi feito:**

O cabeçalho do `sem_wine.sh` passou a nomear as **duas** cláusulas e a dizer
qual trabalha aqui: a primeira (`command -v wine…`) pega a máquina com o pacote
do apt e **é verdadeira antes de mascarar qualquer coisa** nesta, porque o Wine
daqui é o runner do Bottles e nunca esteve no `PATH`; a segunda — cada alvo
mascarado tem de ficar vazio — é a que recusa de verdade. A primeira **fica**:
custa quatro linhas e é o que faz o script valer noutra máquina, que é o caso
que a condição 3 quer sobreviver.

**A afirmação central foi medida, não repetida.** A CORR diz que apagar a
segunda desliga a conferência mesmo com a primeira intacta — medido em dois
espelhos: com o laço de vazio, um alvo cheio dá `EXIT=1` com o nome do
diretório; **sem** o laço, o mesmo alvo cheio passa com *"guarda passou"*. Está
como caso de teste, e é o que transforma a correção de precisão de prosa em
proteção.

Cinco casos entraram no `test_check_nativo.py` (que a
[CORR-WTE-119](/docs/tasks/concluidos/CORR-WTE-119.md) criou uma correção antes): o
controle, uma recusa por cláusula, a demonstração acima, e um que cobra a
própria prosa do cabeçalho — sem ele, esta correção envelhece na próxima
leitura. Os dois casos de recusa **fabricam o próprio alvo** em `tempfile`, e
não dependem de esta máquina ter o Bottles.

**Problemas encontrados:**

**A prosa estava em seis sítios, e a CORR previa dois.** Além do `sem_wine.sh`
e da task 40 (em **duas** passagens, o Log e o resumo), creditavam a cláusula
inerte: o `PLAN-WTE-LAZARUS.md:1472`, o `progresso.md:681`, o `wte/re/nativo.md:34`
e o `wte/tools/README.md:42`. Todos corrigidos.

**O que eu não toquei, e quase toquei:** a linha 64 do `nativo.md` —
`` | `guarda` | `wine`/`wine64`/`wineserver` ausentes no namespace | ok | `` —
não é prosa: é o **valor medido**, que o `nativo_check.sh` escreve no TSV.
Reescrevê-la derrubaria o `check_nativo.py` criado na correção anterior, e com
razão: o `.md` não pode contradizer o que a ferramenta mede. A prosa que
descreve a guarda mudou; o valor que a mede, não.

Desconfiei dos testes por serem rápidos demais — 4 casos em 66 ms, com três
invocações de `bwrap`. Medido à mão: um `sem_wine.sh -- /bin/true` leva **13 a
28 ms**. Namespace custa milissegundos e as máscaras são `tmpfs`; a suspeita era
infundada, e fica registrada porque a próxima pessoa vai desconfiar igual.

**Arquivos criados/modificados:**

- `wte/tools/sem_wine.sh` — o cabeçalho, com as duas cláusulas
- `wte/tools/test_check_nativo.py` — `TestGuardaDoSemWine`, 5 casos
- `docs/tasks/concluidos/40-verificacao-final.md` — o Log e o resumo
- `docs/PLAN-WTE-LAZARUS.md`, `docs/tasks/concluidos/progresso.md`, `wte/re/nativo.md`,
  `wte/tools/README.md`, `wte/tools/nativo_check.sh` — a varredura
