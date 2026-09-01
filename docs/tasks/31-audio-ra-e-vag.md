---
id: PES2-TASK-31
title: "Áudio — o banco `.RA` (VAB) e os VAG"
type: engenharia-reversa
category: formato
phase: 7
depends_on: []
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §1.14"
status: pendente
---

# PES2-TASK-31: Áudio `.RA` / VAB / VAG

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §1.14 e a ressalva da §0; a §5
  Fase 14 do [PLAN-FEATURES](/docs/PLAN-FEATURES.md).
- **É independente das outras cinco tasks da Fase 7** e fica **fora do portão
  da PES2-TASK-22**. Dá para parar antes dela sem perder nada — o navegador de
  assets gráficos já é o salto de valor.
- **Emenda uma não-objetivo.** A §0 dizia "não mexer nos `SD/*.RA`", e a razão
  escrita era correta para o objetivo de mapear o banco: dado de jogo não mora
  ali. A emenda é de **escopo**, decidida em 2026-09-01, e está registrada na
  própria §0 com data.

### O que já está medido

Os primeiros 32 bytes de `/SD/PES2000.RA` (PES2, LBA 20000) são **idênticos**
aos de `/SD/W2002J00.RA` (WE2002, LBA 20000). E são um cabeçalho **VAB** da
Sony, formato público:

```
magic "VABp"   versão 7   vabid 0   fsize 0x3D710 = 251.152
programas 4    tones 64   VAGs 29   mvol 127   pan 64
```

O `fsize` de 251 kB contra um arquivo de 20 MB diz que o `.RA` é **mais de um
banco** — concatenação, ou um VAB seguido de dado de streaming. Qual dos dois
é a primeira pergunta da task.

Isto **corrige** a §5 Fase 14 do `PLAN-FEATURES`, que registra "o índice do
`.RA` não [é documentado]": o começo dele é um VAB comum, e VAB é documentado.

---

## Objetivo

Extrair e substituir um clipe de áudio, sem realocar nada.

### Método

1. **Parsear o VAB**: cabeçalho de 32 B, atributos de programa, atributos de
   tone, tabela de tamanho dos VAG. Descobrir se o `.RA` é uma cadeia de VABs
   e, se for, indexá-la.
2. **Extrair os VAG** e decodificar o ADPCM da Sony para PCM. Formato público
   e bem documentado; é a parte barata.
3. **Codificar de volta** e conferir que o VAG regerado é aceito.
4. **Substituir in-place.** Os `.RA` do PES2 somam 118 MB em 7 arquivos, com
   padding — substituição sem realocar é viável, e a política é a mesma
   fit-or-fail da PES2-TASK-29.
5. **Ouvir no emulador.** É a mesma regra do §4.1 num sentido diferente: o
   oráculo continua sendo o jogo, e áudio se verifica ouvindo.

### O que continua fora

Os `/SD/DA/*.DA` (7 arquivos, 112 MB) são CD-XA de trilha, e a §6.5 já mede
que eles começam no LBA 198606 quando o Track 1 acaba em 198456 — **não estão
no Track 1**. Ficam fora, e a razão é estrutural, não de escopo.

---

## Critério de conclusão

- [ ] Estrutura do `.RA` medida: um VAB ou uma cadeia, com a contagem.
- [ ] Todos os clipes dos 7 `.RA` extraídos, nas duas releases.
- [ ] VAG → WAV → VAG com o regerado aceito, e a perda medida.
- [ ] Um clipe trocado e **ouvido** no emulador.
- [ ] Round-trip: reescrever sem editar devolve `cmp` zero.
- [ ] A §5 Fase 14 do `PLAN-FEATURES.md` corrigida quanto ao índice do `.RA`.
- [ ] Escrito na §1.14 do plano.

---

## Log de Execução

*(a preencher)*
