---
id: CORR-WTE-120
title: "Correção: a guarda do sem_wine.sh é creditada à metade que nesta máquina não pode disparar"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-120: a guarda tem duas metades, e a prosa credita a inerte

## Problema identificado

O Log da [WTE-TASK-40](/docs/tasks/40-verificacao-final.md) explica por que o
ambiente fabricado é honesto:

> Por isso a guarda do `sem_wine.sh` **recusa** se `wine`/`wine64`/`wineserver`
> ainda responder lá dentro: ambiente que só *parece* limpo mede tão pouco
> quanto não medir.

O cabeçalho do [`sem_wine.sh`](../../wte/tools/sem_wine.sh) diz o mesmo. Medido
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

### Arquivos: `wte/tools/sem_wine.sh` e `docs/tasks/40-verificacao-final.md`

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
[CORR-WTE-119](/docs/tasks/CORR-WTE-119.md) pede. Um caso por cláusula:
`PATH` sujo (fabricável com um `wine` falso num diretório do `PATH`) e alvo não
vazio.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/sem_wine.sh` | modificar — o cabeçalho |
| `docs/tasks/40-verificacao-final.md` | modificar — o parágrafo do Log |
| `wte/tools/test_check_nativo.py` | modificar — os dois casos (ver a CORR-WTE-119) |

## Verificação

- [ ] O cabeçalho do `sem_wine.sh` nomeia as duas cláusulas e diz qual trabalha
      nesta máquina
- [ ] Um alvo fora das máscaras faz o script recusar, com o nome do diretório
- [ ] Um `wine` falso no `PATH` faz o script recusar pela primeira cláusula
- [ ] `bash wte/tools/nativo_check.sh --imagem <cópia>` continua com 7 de 7 `ok`
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
