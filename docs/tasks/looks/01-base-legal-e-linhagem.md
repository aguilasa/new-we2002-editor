---
id: LOOKS-TASK-01
title: "Base legal e linhagem — `we3d` (MIT), Superpack e o fonte `en_we2000edit`"
type: documentação
category: legal
phase: 0
depends_on: []
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#2"
reviewed_on: 2026-09-14
review_commit: null
done_on: 2026-09-14
done_commit: b6c5575
---

# LOOKS-TASK-01: Base legal e linhagem

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §2.
- Este projeto se apoia em três materiais de fora, com três situações legais
  **diferentes**, e misturá-las é o erro a evitar.
- O repositório já tem o hábito: o [NOTICE.md](/NOTICE.md) registra o
  `WECompressor` e o `Easy-Mcr` do mesmo jeito.

---

## Objetivo

Registrar a linhagem **antes** de qualquer linha de código, para que nenhuma
fase seguinte precise parar para decidir se pode usar o que está usando.

---

## Critério de conclusão

- [x] `NOTICE.md` ganha a seção do projeto `looks`, distinguindo os três casos:
      **`Darkensses/we3d` é MIT** e entra com crédito; o **Superpack v6** é
      coletânea de terceiros **sem licença**; o fonte **`en_we2000edit`**
      (Haplo/polipoli) não tem licença e serve como *testemunha*, não como
      código a copiar.
- [x] Fica escrito que **nada do Superpack entra no git** — nem arquivo, nem
      transcrição longa —, na mesma regra de `roms/` e do `we-team-editor.exe`.
- [x] O `.gitignore` é conferido: nenhum caminho do Superpack e nenhum
      `work/venv-looks/` pode ser versionado por descuido.
- [x] A §2 do plano e este arquivo não se contradizem.

---

## Log de Execução

**Executado em:** 2026-09-14

### Resumo do que foi feito

O `NOTICE.md` ganhou a seção *"Lineage of the appearance viewer (the
`tools/looks/` tree)"*, com os três materiais em **linhas separadas de uma
tabela** — a forma que as seções do CARP e do Easy MCR já usam — justamente
para que as duas situações sem licença não se fundam com a que tem. Três
coisas que a execução aprendeu e que o critério da task não previa:

1. **A seção *"Copyright and license status"* do próprio `NOTICE.md`
   contradizia a seção nova.** Ela afirma que *todo* material de terceiro daqui
   é sem licença (*"everything else here is unlicensed third-party code"*), e o
   `we3d` é MIT. Escrever a linhagem sem tocar nela deixaria o arquivo se
   desmentindo em dois lugares. Ela passou a nomear Haplo, polipoli e o
   Superpack entre os sem licença, e a **nomear o `we3d` como a exceção**.
2. **A linha do `en_we2000edit` pôde dizer "nada", onde a do Easy MCR teve de
   dizer "semântica"** — e isso merecia estar escrito, porque um leitor futuro
   leria a diferença como mudança silenciosa de regra. Não é: contra o Zetaprog
   os rótulos **eram** a contribuição; aqui `kHair[32]`, `kSkin[4]` e
   `kLetters[8]` já estão no `src/app/Commands.cpp`, o `tools/mcr/domains.py`
   tem cópia própria e o `src/core/Player.cpp` já decodifica o registro. Haplo
   e polipoli são a **quarta** implementação a concordar, não a primeira a
   contar.
3. **Os números do Superpack na §2 do plano descreviam uma subpasta.** É o
   achado da task, abaixo.

### O achado: `4,2 GB, 28.720 arquivos` é do `We2002\`, não da raiz

A §2 do plano atribuía esses dois números a `C:\games\we2002\Superpackv6\`.
Remedido com `tools/looks/superpack_count.py`, criado nesta task justamente
porque a regra do repositório é que número em doc venha de ferramenta guardada,
e não de one-liner descartado:

```
Cronologia We-Pes-IssPro.htm        1 files          76552 B
Iss1                               67 files        2726085 B
Iss2                             1157 files      125924629 B
Iss98                              19 files         469474 B
Mls                                32 files       16325178 B
Pes1                               65 files        3545274 B
Pes2                              562 files       54430639 B
We2000 1st                         21 files        1067532 B
We2000 2nd                         10 files         213043 B
We2000 u23                        924 files      136294984 B
We2001                             49 files        8733973 B
We2002                          28720 files     4452185957 B
We3                                19 files         449800 B
We4                               144 files       27976934 B
--------------------------------------------------------------
TOTAL                           31790 files     4830420054 B  (4.50 GiB)
```

Os 28.720 estão lá, na linha `We2002`. A raiz tem **31.790 arquivos e
4.830.420.054 B**, em treze pastas da linha ISS/PES/WE. A diferença
importa por um motivo prático, e não de contabilidade: **todo caminho `MCR\…`
do plano é relativo a `Superpackv6\We2002\`** — `Superpackv6\MCR` **não
existe**, e quem seguir o plano ao pé da letra recebe "pasta não encontrada" e
desconfia de estar com o Superpack errado. Corrigido na §2 e na §5.4, no lugar,
como manda o perfil.

Esta frase dizia **catorze pastas de jogo**, e foi remedida pela
[`CORR-LOOKS-001`](/docs/tasks/looks/CORR-LOOKS-001.md): catorze é o número de
**linhas** da saída acima, e uma delas é o arquivo
`Cronologia We-Pes-IssPro.htm`. São treze pastas — e **onze** jogos, porque
`We2000 1st`, `We2000 2nd` e `We2000 u23` são três pastas do mesmo.

De quebra, olhando a pasta do corpus: são **50 arquivos, todos `.jpg`, mas 49
tuplas** — o quinquagésimo se chama `0.jpg`. A §5.4 dizia "50 JPGs conferidos,
nomeados pela tupla exata". A linha foi escrita **na
[`LOOKS-TASK-18`](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md)**, que é
quem vai contar cobertura, e não só aqui no Log: um parser que exija tupla
quebra no `0.jpg`, e um que o ignore em silêncio reporta 50 onde mediu 49.

### O `.gitignore`

Conferido por `git check-ignore -v`, não por leitura:

```
$ git check-ignore -v "Superpackv6/MCR/We DB - polipoli/Faces/A-I3-A-F-A.jpg"
.gitignore:182:/Superpackv6/    Superpackv6/MCR/We DB - polipoli/Faces/A-I3-A-F-A.jpg
$ git check-ignore -v work/venv-looks/pyvenv.cfg
.gitignore:48:work/     work/venv-looks/pyvenv.cfg
$ git ls-files | grep -i superpack
(vazio)
```

O `work/` já cobria o venv; a linha `work/venv-looks/` foi acrescentada com
comentário dizendo isso, no mesmo molde do `wte/build/`, que existe pela mesma
razão. A entrada `/Superpackv6/` **hoje não casa com nada**, e isso é de
propósito: a coletânea mora fora da árvore de trabalho, e a linha é a guarda
para o dia em que alguém a copiar para dentro a fim de encurtar um caminho — o
comentário diz isso, para ninguém a apagar por "não casar com nada".

### Arquivos criados/modificados

- `NOTICE.md` — seção nova do `looks` e reconciliação da *"Copyright and
  license status"*
- `.gitignore` — `/Superpackv6/` e `work/venv-looks/`, com os comentários
- `tools/looks/superpack_count.py` — **novo**, com `self_check()` e caso
  vermelho (uma repartição que não soma o total)
- `docs/PLAN-LOOKS-PY.md` — §2 (obrigação cumprida e números corrigidos) e §5.4
  (o caminho e o `0.jpg`)
- `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md` — as duas linhas
  encaminhadas, e o critério do `0.jpg`
- `docs/tasks/looks/progresso.md` — tabela e checklist da Fase 0
- `docs/tasks/looks/01-base-legal-e-linhagem.md` — este arquivo

### Problemas encontrados

Nenhum que bloqueasse. Duas observações para quem vier depois:

- **Não há gate nesta fase**, e o perfil já avisa. A verificação desta task é a
  saída de ferramenta copiada acima (`git check-ignore`, `superpack_count.py
  --check`, `check_tasks.py` e a conferência de links do
  `.claude/rules/links.md`) — não o `looks_selftest`, que só nasce na
  LOOKS-TASK-06.
- O `tools/looks/` **nasceu nesta task**, uma fase antes do previsto, por conta
  do `superpack_count.py`. Ele já traz `self_check()`, então a varredura da
  LOOKS-TASK-06 o encontra em regra, e não como exceção.
