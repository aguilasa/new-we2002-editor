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

- [ ] Conjunto de cópias por idioma varrido por ferramenta, com a lista
      completa dos pares medidos em `/BIN/`.
- [ ] A ferramenta **recusa** gravar se achar cópia fora do plano.
- [ ] Fonte do jogo localizada, com arquivo e offset relativo.
- [ ] Um nome renderizado, inserido nas duas cópias, e **visto na tela** —
      nos dois idiomas.
- [ ] O nome antigo ausente de todas as telas alcançadas.
- [ ] Round-trip de volta: `cmp` zero contra a release original.
- [ ] Escrito na §6.12 do plano.

---

## Log de Execução

*(a preencher)*
