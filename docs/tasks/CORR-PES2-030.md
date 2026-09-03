---
id: CORR-PES2-030
title: "Correção: o `pes2_boot` prova vida exigindo que dois quadros difiram, e falha na tela de intro que não anima"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-PES2-030: o gate de boot é intermitente — 1 falha em 3 corridas seguidas, com o emulador saudável

## Problema identificado

O `boot_check.sh` prova que o emulador está vivo com três asserções, e a
terceira é:

```sh
*) awk -v c="$CHANGED" -v t="$TOTAL" 'BEGIN{exit !(c > t*0.001)}' ||
       { echo "FAIL: the two frames are the same -- it is not running"; fail=1; } ;;
```

Os dois quadros são tirados em **relógio fixo**: um aos `PES2_WARMUP`
segundos (45 por padrão) e outro `PES2_GAP` depois (12). A asserção só é
válida se a tela em que os dois caem **animar**. O boot do PES2 atravessa
logos e telas de abertura estáticas, e o instante em que cada uma começa
varia de corrida para corrida — quando as duas amostras caem dentro da mesma
tela parada, o gate declara *"it is not running"* sobre um emulador que está
perfeitamente vivo.

É a **armadilha 32 da §6.11** — *"imobilidade exata só serve na tela
realmente parada"* — aplicada ao contrário: lá o risco é esperar por
imobilidade numa tela que anima; aqui é exigir movimento numa tela que não
anima. As duas saem do mesmo engano, que é tratar o relógio como se ele
dissesse em que tela se está.

As outras duas asserções (`sd > 0.02` em cada quadro) **não** falharam: os
quadros não são pretos, têm conteúdo, e o desvio-padrão de 0,13657 é o de uma
tela desenhada. Só a comparação entre eles falhou.

## Evidência

Três corridas seguidas do mesmo comando, mesmo binário, mesma cópia, sem
nenhuma alteração entre elas:

```
$ PES2_IMAGE="<cópia>/….cue" tools/pes2/boot_check.sh

# corrida A -- 2026-09-03 17:41, via `ctest -R pes2`
frame 1  mean=0.253503  sd=0.13657
frame 2  mean=0.253503  sd=0.13657
changed pixels: 0 of 524000
FAIL: the two frames are the same -- it is not running        exit != 0

# corrida B, minutos depois
frame 1  mean=0.102687  sd=0.154013
frame 2  mean=0.206067  sd=0.274267
changed pixels: 260000 of 524000
BOOT OK: the fork (…/duckstation-mcp/bin/duckstation-qt)

# corrida C
frame 1  mean=0.155367  sd=0.202307
frame 2  mean=0.124209  sd=0.230248
changed pixels: 260000 of 524000
BOOT OK: the fork (…/duckstation-mcp/bin/duckstation-qt)
```

Na corrida A os dois quadros são **byte a byte idênticos** — `mean` e `sd`
iguais até o último dígito, 0 de 524.000 pixels diferentes. Não é um
emulador travado: `sd=0,13657` é conteúdo desenhado, e o lançador reportou
`duckstation-mcp 1.0.0 answering`, ou seja o servidor MCP respondeu e a
janela existia.

A média das duas amostras de A, 0,253503, não é nenhuma das assinaturas
conhecidas — não é o título (0,5526 ±0,010) nem o menu principal (0,1406
±0,010) —, o que é consistente com uma tela de abertura parada entre as duas.

O emulador **não** herda estado entre corridas: o `fork.py` lança com
`-batch -fastboot -nogui`, e o `SLES-03957_resume.sav` do usuário ficou com
`mtime` de 15:07, intocado pelas três corridas.

Frequência medida: **1 falha em 3** nesta bateria, e 1 em 5 contando as duas
corridas verdes anteriores do mesmo lote.

## Causa raiz

A prova de vida está ancorada em **tempo de relógio**, não em estado. Aos
45 s + 12 s, em que tela o jogo está é uma aposta — depende da máquina, da
carga e do que o emulador fez no arranque. O gate assume que qualquer par de
instantes separados por 12 s cai em pixels diferentes, e essa premissa é
falsa em toda tela estática, que é a maior parte de uma abertura de PSX.

## Correção

O critério é: **a prova de vida não pode depender de o jogo estar animando
naquele instante.** Três formas, em ordem de preferência.

1. **Amostrar mais de duas vezes.** Trocar o par por N amostras ao longo do
   `PES2_GAP` (por exemplo uma por segundo) e exigir que **alguma** delas
   difira das outras. Uma tela estática de 12 s continua sendo atravessada
   por qualquer boot que ande; o que hoje falha é a coincidência de dois
   pontos, e ela desaparece com uma dúzia.

2. **Perguntar ao emulador em vez de olhar a tela.** O binário de trabalho é
   o fork com MCP, e a contagem de quadros dele é a resposta exata para "está
   rodando?" — `mcp.py` já fala com ele. O caminho tem de degradar para o
   olhar-a-tela quando o binário é o AppImage oficial, que não tem servidor,
   e é por isso que ele não é a primeira opção.

3. **Alongar o `PES2_GAP`.** É o remendo, não o conserto: reduz a
   probabilidade sem eliminá-la, e paga em segundos de gate.

Qualquer que seja a escolha, a **mensagem** de falha tem de deixar de afirmar
o que não sabe: *"the two frames are the same -- it is not running"* é uma
conclusão, e o que se mediu foi *"these two samples are identical"*.

### Arquivo: `tools/pes2/boot_check.sh`

A asserção de vida e a mensagem dela.

### Arquivo: `docs/PLAN-PES2-PSX.md` §3.4 e `docs/prompts/perfil-pes2.md`

O gate é descrito nos dois como a evidência de que o jogo bota. Se ele passa
a amostrar N vezes, o número entra ali; se passa a perguntar ao MCP, entra a
ressalva do AppImage.

### Caso vermelho

O gate precisa continuar sabendo ficar vermelho **quando o emulador está de
fato morto**. Um controle possível, sem emulador: alimentar a comparação com
duas cópias do mesmo quadro e exigir a recusa — que é o que a corrida A
produziu por acidente, e que hoje não tem teste.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/pes2/boot_check.sh` | modificar |
| `docs/PLAN-PES2-PSX.md` | modificar |
| `docs/prompts/perfil-pes2.md` | modificar |

## Verificação

- [ ] dez corridas seguidas de `boot_check.sh` sobre a mesma cópia, todas
      verdes — a frequência medida hoje é de 1 falha em 3
- [ ] o gate continua ficando **vermelho** com o emulador morto ou a tela
      preta, e o caso está exercitado
- [ ] a mensagem de falha diz o que foi medido, não a conclusão
- [ ] `ctest --test-dir build -R pes2` verde com a receita completa
- [ ] `roms/` intocada; nenhum quadro do jogo versionado

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
