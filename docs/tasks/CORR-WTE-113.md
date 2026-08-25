---
id: CORR-WTE-113
title: "Correção: `golden_suite.sh --roteiro` trunca o `golden.tsv` inteiro — 96 corridas viram zero"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-113: `--roteiro` sem `--retomar` apaga a bateria inteira

## Problema identificado

Rodar a bateria filtrada por um roteiro **destrói o registro dos outros**. O
[`golden_suite.sh`](../../wte/tools/golden_suite.sh) reescreve o cabeçalho do
TSV sempre que `--retomar` não é passado, e faz isso **antes de qualquer
corrida**:

```sh
if [ ! -f "$SAIDA" ] || [ "$RETOMAR" != 1 ]; then
  printf 'roteiro\trom\tmodo\tveredito\tsegundos\tdata\n' > "$SAIDA"
fi
```

O `--roteiro`, portanto, **não é filtro: é substituição**. Quem quiser
acrescentar uma corrida ao registro tem de saber, sem que nada diga, que
precisa também de `--retomar`.

Não é hipótese: aconteceu na
[WTE-TASK-37](/docs/tasks/37-reconferencia-de-ui.md), com as 92 corridas da
[WTE-TASK-34](/docs/tasks/34-bateria-golden-completa.md) — **1,8 hora de
relógio** — apagadas ao registrar o `golden-25-retorno`. Foram recuperadas à
mão do `git show HEAD:`, e o Log da task fecha o assunto com *"vale um item
para quem mexer na bateria de novo"*. **Esse item não foi aberto**, nada mudou
no script, e o próximo a usar `--roteiro` repete a perda.

O que salvou a primeira vez foi o `check_golden.py --check`, que passou a
acusar 23 roteiros "com par em disco e ausentes da bateria" — ou seja, a perda
é **detectada depois**, não impedida, e a recuperação depende de o TSV já estar
commitado.

## Evidência

Reproduzido em 2026-08-25 sobre uma **cópia** do TSV, com `--saida` apontado
para ela e a corrida interrompida em 6 segundos — antes de qualquer golden
rodar:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
cp wte/re/golden.tsv /tmp/copia.tsv
wc -l < /tmp/copia.tsv
timeout 6 bash wte/tools/golden_suite.sh --saida /tmp/copia.tsv \
     --roteiro golden-25-retorno --rom japonesa >/dev/null 2>&1
wc -l < /tmp/copia.tsv
cat /tmp/copia.tsv
```

```text
97
1
roteiro	rom	modo	veredito	segundos	data
```

**97 linhas viraram 1** — o cabeçalho, e nada mais. As 96 corridas registradas
(92 da WTE-TASK-34 mais as 4 da WTE-TASK-37) desapareceram sem que uma única
corrida tivesse começado.

| Comando | O que a pessoa espera | O que acontece |
|---|---|---|
| `--roteiro X` | acrescenta ou refaz as linhas de X | **zera o TSV** e escreve só as de X |
| `--roteiro X --retomar` | idem | é o que funciona |

## Causa raiz

O truncamento do TSV foi escrito para a corrida completa, e o `--roteiro`
entrou depois sem que a condição do truncamento passasse a considerá-lo.

## Correção

### Arquivo: `wte/tools/golden_suite.sh`

O truncamento só faz sentido quando a corrida é **a bateria inteira**. Com
`--roteiro` (ou `--rom` diferente de `ambas`), a corrida é parcial e o registro
tem de ser preservado, com as linhas do que rodou substituídas em vez de o
arquivo inteiro:

```sh
PARCIAL=0
[ "${#ESCOLHIDOS[@]}" -gt 0 ] && PARCIAL=1
[ "$ROM" != ambas ] && PARCIAL=1

if [ ! -f "$SAIDA" ] || { [ "$RETOMAR" != 1 ] && [ "$PARCIAL" != 1 ]; }; then
  printf 'roteiro\trom\tmodo\tveredito\tsegundos\tdata\n' > "$SAIDA"
fi
```

E, no `registra()`, apagar a linha velha do trio `(roteiro, rom, modo)` antes de
acrescentar a nova — senão a corrida parcial duplica linhas em vez de
atualizá-las, e o `check_golden.py` passa a ler duas datas para a mesma corrida.

**Alternativa mais conservadora, se a de cima parecer muito:** recusar
`--roteiro` sem `--retomar`, com a mensagem dizendo o que aconteceria. Custa
três linhas e transforma perda silenciosa em erro na cara. É pior de usar e
melhor que hoje.

### Guarda

Um caso em `test_check_golden.py` — ou um `test_golden_suite.py` novo — que
monte um TSV com duas linhas, chame a lógica de truncamento com `--roteiro`, e
**exija** que as linhas sobrevivam. A demonstração acima já é o roteiro do
teste: 97 linhas entram, 97 (ou mais) têm de sair.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/golden_suite.sh` | modificar |
| `wte/tools/test_check_golden.py` | modificar — a guarda |
| `docs/tasks/37-reconferencia-de-ui.md` | modificar — apontar esta CORR onde o Log diz "vale um item" |

## Verificação

- [ ] A reprodução acima devolve **97** nas duas medições
- [ ] `--roteiro X` duas vezes seguidas não duplica as linhas de X
- [ ] `python3 wte/tools/check_golden.py --check` verde depois de uma corrida parcial
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
