---
id: PES2-TASK-28
title: "`T_NAME_I` e `T_NAME_S` — o conjunto de cópias por idioma"
type: engenharia-reversa
category: formato
phase: 7
depends_on: [PES2-TASK-27]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §6.12"
status: pendente
---

# PES2-TASK-28: As cópias de idioma dos assets

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §6.12 e §1.14; a §6.1, que é a mesma
  armadilha uma camada acima; a §5 Fase 13 do
  [PLAN-FEATURES](/docs/PLAN-FEATURES.md).

O `T_NAME.BIN` guarda o nome de time e de estádio **renderizado em bitmap**
para a tela de apresentação. É a razão de o nome editado pela tabela de texto
continuar velho ali: são dois lugares, não um.

E no PES2 são **três**. Medido em 2026-09-01:

```
/BIN/T_NAME_I.BIN   62.196 B
/BIN/T_NAME_S.BIN   62.196 B   ← byte a byte idêntico ao _I
```

Idênticos hoje, e o jogo escolhe por idioma. Gravar um e deixar o outro é
exatamente o modo de falha que a §6.1 cataloga para as tabelas de texto —
com o agravante de ser **invisível** para quem joga no idioma que ficou certo.

O mesmo vale para os outros pares de idioma que a §1.4 lista:
`DAT2D_I`/`DAT2D_S`, `DATSEL_I`/`DATSEL2I`/`DATSEL3I`, `LC_*`, `FNOTE_{G,I,S}`.

---

## Objetivo

Fechar o **conjunto de cópias por idioma** de cada asset — varrido, nunca
declarado —, e renderizar um nome novo no `T_NAME`.

### Método

1. **Varrer, não listar.** Mesmo princípio do `poke.py`: agrupar os arquivos
   de `/BIN/` por conteúdo (digest do bloco descomprimido) e por sufixo de
   idioma, e **recusar** se sobrar cópia fora do plano. Declarar a lista à mão
   é como as três cópias de nome de time ficaram para trás na Fase 2.
2. **Achar a fonte no próprio disco.** O bitmap é renderizado com a fonte do
   jogo; ela sai de um dos contêineres, não de fora. Localizar, e registrar
   qual.
3. **Renderizar e remontar** uma entrada de nome, do mesmo tamanho da
   original, e inserir nas duas cópias.
4. **Verificar na tela** do emulador — o oráculo é o jogo (§4.1). O nome novo
   tem de aparecer na apresentação, **nos dois idiomas**, e a §6.1 exige a
   segunda metade da medida: o nome velho **ausente** de toda tela.

---

### Vindo da PES2-TASK-27: os `T_NAME_*` são contêiner indexado sem paleta

Medido em 2026-09-01. `T_NAME_I.BIN` e `T_NAME_S.BIN` na `(EsIt)`,
`T_NAME_F.BIN` e `T_NAME_G.BIN` na `(EnFrDe)` **têm lista de registros e
nenhum registro de CLUT** — são 22 contêineres nessa condição na `(EsIt)`,
entre eles os `DAT2D_I`/`DAT2D_S` e os `CG<idioma>.BIN`. O
`bin_archive.py export` os pula dizendo `no CLUT in this container`, e é
comportamento correto: sem paleta no arquivo, a cor vem de outro lugar.

Duas consequências para esta task:

- **O conjunto de cópias por idioma tem forma no nome**, e o sufixo é a pista:
  `_I`/`_S` na release espanhola-italiana, `_F`/`_G` na
  inglesa-francesa-alemã. Varra por sufixo, não por lista fixa — o número de
  cópias muda de release para release, que é exatamente o que o critério
  abaixo cobra.
- **Comparar dois idiomas é comparar índice, não pixel.** Os registros dizem
  retângulo de VRAM e offset; se dois idiomas têm o mesmo retângulo e fluxos
  diferentes, a diferença é o texto desenhado. `bin_archive.py ls <img>
  --file /BIN/T_NAME_I.BIN` dá a lista.

## Critério de conclusão

- [x] Conjunto de cópias por idioma varrido por ferramenta, com a lista
      completa dos pares medidos em `/BIN/`.
- [x] A ferramenta **recusa** gravar se achar cópia fora do plano.
- [x] Fonte do jogo localizada, com arquivo e offset relativo.
- [ ] Um nome renderizado, inserido nas duas cópias, e **visto na tela** —
      nos dois idiomas. **Bloqueado na PES2-TASK-03** — ver o Log.
- [ ] O nome antigo ausente de todas as telas alcançadas. **Bloqueado na
      PES2-TASK-03**, pela mesma razão.
- [x] Round-trip de volta: `cmp` zero contra a release original.
- [x] Escrito na §6.12 do plano.

---

## Log de Execução

**Executado em:** 2026-09-01 — **parcial.** Cinco dos sete critérios fechados;
os dois de tela estão bloqueados, e a task **não** está concluída.

**Resumo do que foi feito.** `tools/pes2/lang_map.py` agrupa os arquivos do
disco por digest de conteúdo — o disco inteiro, não só `/BIN/`, porque os
`FNOTE_*` que a §6.12 lista moram na raiz —, entrega o conjunto de cópias de
um asset, grava em todas de uma vez e **recusa** gravar num arquivo que não
tenha cópia. Depois de gravar, varre o disco atrás do conteúdo antigo: é a
metade da medida que uma captura no idioma certo nunca pegaria.

**O que a varredura corrigiu na §6.12, e vale mais que a ferramenta.** A
seção dizia que os pares da §1.4 — `DAT2D_I`/`DAT2D_S`,
`DATSEL_I`/`DATSEL2I`/`DATSEL3I`, `LC_*`, `FNOTE_*` — deviam ser tratados como
o `T_NAME`. **Não são cópias**: `DAT2D_I` tem 39.820 bytes e `DAT2D_S`
37.728; os três `DATSEL*I` diferem entre si; os catorze `LC_*` também; os três
`FNOTE_*` têm 1.896, 1.884 e 1.792. São **variantes de idioma**, e gravar as
duas com o mesmo conteúdo estraga uma — o problema oposto. Os conjuntos de
cópia de verdade são três por release:

| Conjunto | `(EsIt)` | `(EnFrDe)` | tamanho |
|---|---|---|---:|
| `T_NAME` | `_I`, `_S` | `_E`, `_F`, `_G` | 62.196 B |
| `LC` | `LC_MS`, `LC_OL` | idem | 10.420 B |
| `TEX` | `TEX_99`, `TEX_A0`, `TEX_A1`, `TEX_A2` | idem | 32.752 B |

E o `T_NAME` é **o mesmo arquivo nas duas releases**, mesmo digest: cinco
cópias em dois discos, um conteúdo. Os dois conjuntos `LC` e `TEX` ninguém
tinha listado.

**O sufixo não serve de regra, e a medida mostra por quê:** a `(EsIt)` traz
`DATSEL_I`, `DATSEL2I`, `DATSEL3I` e nenhuma forma sem sufixo; a `(EnFrDe)`
traz `DATSEL`, `DATSEL2`, `DATSEL3` e nenhuma com. Agrupar por nome acha
conjuntos diferentes em cada disco. Por conteúdo, não.

**A fonte, localizada.** O `T_NAME` guarda os nomes **já rasterizados** — a
primeira entrada de `T_NAME_I.BIN` é 128×128 a 4 bpp com `Ireland`,
`Scotland`, `Wales` e `England` empilhados; são 28 entradas de 4 nomes. A face
itálica é a de dois blocos vizinhos de `/BIN/DAT2D_I.BIN`, registros nos
offsets relativos **20432** e **24768**, VRAM (640, 0) e (672, 0), com
maiúsculas, minúsculas e dígitos. Conferido a olho, renderizando os dois
blocos.

**Resultado medido.** `--check` verde nas duas releases; `--self-check` verde
nas duas: 2 cópias gravadas na `(EsIt)` e 3 na `(EnFrDe)`, disco varrido sem
sobra do conteúdo antigo, e a imagem de volta **byte a byte** ao original.
`ctest -R pes2` verde em 11,55 s.

**O que ficou de fora, e por quê.** Os dois critérios de tela — *"um nome
renderizado … visto na tela, nos dois idiomas"* e *"o nome antigo ausente de
todas as telas"*. Eles precisam chegar à tela de apresentação e trocar de
idioma no emulador, que é exatamente o roteiro da
[PES2-TASK-03](/docs/tasks/03-direcao-do-emulador.md), ainda pendente. O
`depends_on` desta task só declara a 27, e isso é um defeito do quadro: quem
o refizer deve acrescentar a 03. A linha do que a 03 precisa entregar para
desbloquear esta está escrita **no arquivo dela**.

Com o bloqueio, também não foi feita a **renderização de um nome novo a partir
da fonte** — sem tela para conferir, o resultado seria uma afirmação sem
medida. O que existe e foi exercitado é o caminho de gravação: uma alteração
de mesmo tamanho no `T_NAME`, escrita em todas as cópias e desfeita com `cmp`
zero.

**Arquivos criados/modificados**

- `tools/pes2/lang_map.py` — novo
- `tools/pes2/check_image.py` — o `--check` dos conjuntos no `pes2_image`
- `docs/PLAN-PES2-PSX.md` — a §6.12 remedida e corrigida
- `docs/tasks/03-direcao-do-emulador.md` — o que a 28 espera dela
- `docs/tasks/progresso.md`, `docs/prompts/perfil-pes2.md`, `CLAUDE.md` — o
  gate novo e a ferramenta nova

**Problemas encontrados.** Além do bloqueio: a premissa desta task dizia "no
PES2 são três" cópias de `T_NAME`; são **duas** na `(EsIt)` e três na
`(EnFrDe)`, e o texto do Contexto foi mantido como estava porque descreve o
que se sabia ao abrir a task — a correção está aqui e na §6.12.
