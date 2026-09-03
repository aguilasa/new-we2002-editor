---
id: CORR-PES2-021
title: "Correção: o `boot_check.sh` justifica nomear o binário com um 0,019 que a própria task mediu e desmentiu"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-PES2-021: o `boot_check.sh` afirma 0,019 entre os dois binários; medido são ~0,0015

## Problema identificado

O cabeçalho de [`tools/pes2/boot_check.sh`](../../tools/pes2/boot_check.sh),
na linha 38, justifica a decisão de o gate **dizer contra qual binário
correu** com um número:

```
# does not name its binary cannot be compared with the one before it, and
# the two binaries do not render the same picture -- the title screen's
# standard deviation differs by 0.019 between them.
```

O número é falso, e o que o desmente é a **medição da mesma task, no mesmo
commit**. A tabela "As assinaturas de quadro, medidas" da §6.14 do
[`PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md) registra, para a tela de título:

| binário | desvio medido em 2026-09-03 |
|---|---|
| fork | 0,359942 .. 0,360497 |
| AppImage | 0,358742 |

A distância entre os dois é de **0,0012 a 0,0018** — uma ordem de grandeza
abaixo do 0,019 afirmado. O 0,019 é a distância entre a leitura de hoje
(≈0,360) e a **registrada anteontem** (0,3411), e a mesma seção do plano
descarta explicitamente o binário como causa dela:

> **não é o fork:** o AppImage é o mesmo arquivo de 29 de agosto, intocado,
> e hoje ele dá 0,3587 onde deu 0,341 anteontem;

Ou seja: o comentário atribui ao binário exatamente a deriva que a task
mediu para provar que **não é do binário** — e que por isso aposentou o
desvio como critério.

## Evidência

Onde o número vive, e que ele nasceu neste commit:

```
$ grep -rn "0\.019\|0,019" tools/pes2/ docs/PLAN-PES2-PSX.md \
      docs/prompts/perfil-pes2.md CLAUDE.md
tools/pes2/boot_check.sh:38:# standard deviation differs by 0.019 between them.

$ git show HEAD -- tools/pes2/boot_check.sh | grep -n '^+.*0\.019'
84:+# standard deviation differs by 0.019 between them.
```

A medição que o contradiz, reproduzida nesta revisão contra o fork:

```
$ python3 tools/pes2/mcp_drive.py "<copia.cue>" --screen main-menu --out-dir <dir>
  shot title  mean=0.552843 sd=0.359966  .../title.png
```

0,359966 (fork, hoje) contra 0,358742 (AppImage, 2026-09-03) = **0,001224**.

## Causa raiz

O comentário foi escrito com o número que a task **esperava** encontrar — a
diferença entre binários — e não foi reconciliado quando a medição mostrou
que a diferença é entre **dias**, não entre binários.

## Correção

### Arquivo: `tools/pes2/boot_check.sh`

Trocar a justificativa por uma que a §6.14 sustente. As duas coisas
verdadeiras e úteis a dizer ali são:

1. as **médias** sobrevivem à troca de binário (título ≈0,5502..0,5551 nos
   dois), então não é a média que distingue;
2. o **desvio não se reproduz nem no mesmo binário de um dia para o outro**
   — por isso ele saiu de critério —, e é justamente por o gate não ter um
   número estável para julgar que ele precisa **dizer qual binário correu**:
   sem o nome, a corrida de hoje não se compara com a de ontem.

Sugestão de redação para as três últimas linhas do parágrafo:

```sh
# fallback. Either way the run *says which one it was*: a boot check that
# does not name its binary cannot be compared with the one before it. The
# two binaries agree on every frame *mean* measured (section 6.14), and the
# title screen's standard deviation reproduces under neither -- it moved
# 0.019 on the untouched AppImage from one day to the next, which is why it
# was retired as a criterion. A number nobody judges by is a reason to
# record the binary, not to trust the frame.
```

O que **não** fazer: substituir 0,019 por 0,0015 e manter a frase. A
diferença medida entre binários é menor que a variação do mesmo binário
entre dias, então ela não sustenta afirmação nenhuma sobre "não renderizam
a mesma imagem".

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/pes2/boot_check.sh` | modificar |

## Verificação

- [x] `grep -rn "0\.019" tools/pes2/` não devolve mais a atribuição ao binário
- [x] o parágrafo restante bate com a tabela da §6.14 do `PLAN-PES2-PSX.md`
- [x] `PES2_IMAGE=<copia.cue> tools/pes2/boot_check.sh` continua verde e
      continua nomeando o binário na linha `BOOT OK:`
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-09-03

**Resumo do que foi feito:** as três últimas linhas do parágrafo "Which
emulator this judges" do `boot_check.sh` foram reescritas com o que a §6.14
sustenta. A frase deixou de atribuir os 0,019 à troca de binário e passa a
dizer as duas coisas medidas: as **médias** de quadro concordam entre os dois
binários, e o **desvio-padrão não se reproduz nem no mesmo binário de um dia
para o outro** — os 0,019 são a deriva do AppImage intocado entre 2026-09-01
e 2026-09-03. A conclusão fica explícita: um número que ninguém julga é razão
para **registrar** o binário, não para confiar no quadro.

**Problemas encontrados:** nenhum. O `0.019` continua no arquivo, agora
atribuído ao lado certo — a deriva do mesmo AppImage entre dias —, que é
exatamente o que a CORR pede; o que sumiu é a atribuição ao par de binários
(`grep -rn "differs by 0\.019" tools/pes2/` vazio).

**Gate:** `PES2_IMAGE=<cópia EsIt no scratchpad> tools/pes2/boot_check.sh`
verde contra o fork —

```
frame 1  mean=0.154569  sd=0.202177
frame 2  mean=0.126603  sd=0.233843
changed pixels: 260000 of 524000
BOOT OK: the fork (/home/ingmar/Applications/duckstation-mcp/bin/duckstation-qt),
window 4194311, 800x655, two live frames in /tmp/pes2-boot-k9cjpI
```

A linha final nomeia o binário, que é o comportamento que o parágrafo
justifica. Os quadros ficaram no `/tmp` do `mktemp`, fora do repositório.
`roms/` intocada — o boot correu sobre cópia da release `(EsIt)` no
scratchpad, e o `duckstation-fork.log` do lançador caiu na cópia.

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `tools/pes2/boot_check.sh` | modificado (linhas 35-41 do cabeçalho) |
