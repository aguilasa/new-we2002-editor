---
id: CORR-WTE-117
title: "Correção: o app procura os assets em quatro lugares e a mensagem promete três, sem dizer o que é o quarto"
type: correção
category: empacotamento
status: pendente
depends_on: []
---

# CORR-WTE-117: quatro candidatos no código, três na mensagem

## Problema identificado

O `RaizDosAssets` do
[`wte_datafiles.pas`](../../wte/src/wte_datafiles.pas) percorre **quatro**
candidatos:

```pascal
candidatos[0] := GetEnvironmentVariable('WTE_ASSETS_DIR');
candidatos[1] := base + '..' + DirectorySeparator + 'assets';
candidatos[2] := base + '..' + DirectorySeparator + 'share'
                      + DirectorySeparator + SLUG;
candidatos[3] := base + '..' + DirectorySeparator + '..'
                      + DirectorySeparator + 'assets';
```

A `MensagemDeAssetsAusentes`, logo abaixo no mesmo arquivo, lista **três** — o
`[3]` não aparece. O critério de conclusão da
[WTE-TASK-39](/docs/tasks/39-empacotamento.md) repete o número da mensagem
(*"os três diretórios onde o app procura"*), e o
[`wte/README.md`](../../wte/README.md) também.

Duas consequências, e nenhuma é grave sozinha:

1. **quem puser os assets no quarto lugar é atendido e não sabia que podia** —
   a busca funciona, a mensagem nunca o ofereceu;
2. **ninguém sabe para que ele serve.** É a única linha do arquivo sem
   comentário, num módulo em que cada decisão de caminho tem o seu — inclusive
   o `ExpandFileName` da mensagem, que existe só para o caminho ficar legível.

O `[3]` resolve `<dir do executável>/../../assets`. Com o binário em
`wte/build/`, isso é `<repo>/assets`, que **nada no repositório cria**: o
`make -C wte assets` liga `wte/assets`, que é o candidato `[1]`.

## Evidência

Os quatro candidatos e as três linhas da mensagem, no mesmo arquivo:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -n "candidatos\[" wte/src/wte_datafiles.pas
grep -n "  1\.\|  2\.\|  3\." wte/src/wte_datafiles.pas
```

```text
92:  candidatos[0] := GetEnvironmentVariable('WTE_ASSETS_DIR');
93:  candidatos[1] := base + '..' + DirectorySeparator + 'assets';
94:  candidatos[2] := base + '..' + DirectorySeparator + 'share'
96:  candidatos[3] := base + '..' + DirectorySeparator + '..'
99:    if TemAssets(candidatos[i]) then
100:      Exit(IncludeTrailingPathDelimiter(candidatos[i]));

112:    + '  1. no diretorio que a variavel WTE_ASSETS_DIR apontar; ou'
117:    + '  2. em ' + ExpandFileName(DirDoExecutavel + '..' + DirectorySeparator
120:    + '  3. em ' + ExpandFileName(DirDoExecutavel + '..' + DirectorySeparator
```

A mensagem, medida em 2026-08-26 com a árvore instalada num prefixo e
**movida** de lugar — os caminhos saem resolvidos, e são três:

```text
Ponha a pasta do WE2002 Team Editor num destes lugares:

  1. no diretorio que a variavel WTE_ASSETS_DIR apontar; ou
  2. em <prefixo-movido>/assets; ou
  3. em <prefixo-movido>/share/we2002Lazarus
```

Quem popula cada um:

| Candidato | Caminho | Quem cria |
|---|---|---|
| `[0]` | `$WTE_ASSETS_DIR` | o usuário |
| `[1]` | `<exe>/../assets` | `make -C wte assets` (e o `install`, no prefixo) |
| `[2]` | `<exe>/../share/<slug>` | `make -C wte install` |
| `[3]` | `<exe>/../../assets` | **ninguém** |

```bash
ls -ld assets wte/assets
```

```text
ls: cannot access 'assets': No such file or directory
lrwxrwxrwx wte/assets -> .../we-team-editor
```

## Causa raiz

O quarto candidato entrou na lista de busca e não entrou na mensagem nem ganhou
comentário, então nada diz se ele é caso previsto ou sobra.

## Correção

Decidir o que ele é, e as duas saídas são baratas:

### Se for caso previsto — `wte/src/wte_datafiles.pas`

Comentar a linha dizendo qual layout ela atende, e **acrescentar a quarta linha
à mensagem**. A mensagem já monta cada item com `ExpandFileName`; a quarta sai
do mesmo molde.

E então corrigir o número nos dois documentos que dizem três: o critério da
[WTE-TASK-39](/docs/tasks/39-empacotamento.md) e a seção do
[`wte/README.md`](../../wte/README.md).

### Se for sobra — `wte/src/wte_datafiles.pas`

Apagar o `candidatos[3]` e reduzir o array para `0..2`. A busca fica igual ao
que a mensagem promete, os documentos ficam certos sem tocar em número, e o
módulo volta a ter uma linha por decisão.

**A segunda é a recomendada**, porque o candidato `[1]` já cobre o caso de
desenvolvimento (`wte/assets`) e o `[2]` o de instalação; um terceiro caminho
relativo sem consumidor é superfície sem uso.

### Guarda

O `test_check_bordas.py` mostra o molde: um caso que percorra `RaizDosAssets` e
exija que **todo** candidato relativo apareça na `MensagemDeAssetsAusentes`.
Assim a próxima linha de busca ou entra na mensagem, ou reprova — e o número
dos documentos deixa de ser copiado à mão.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/src/wte_datafiles.pas` | modificar |
| `docs/tasks/39-empacotamento.md` | modificar (se o número mudar) |
| `wte/README.md` | modificar (se o número mudar) |
| `wte/tools/test_check_bordas.py` ou um teste novo | modificar — a guarda |

## Verificação

- [ ] O número de candidatos relativos em `RaizDosAssets` é igual ao número de
      itens da `MensagemDeAssetsAusentes`
- [ ] A guarda reprova quando se acrescenta um candidato sem tocar na mensagem
- [ ] `lazbuild wte/wte.lpi` compila
- [ ] `make -C wte install PREFIX=<tmp>` continua com 13 arquivos, e o binário
      movido acha os assets e abre a janela 522×475
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
