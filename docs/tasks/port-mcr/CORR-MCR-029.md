---
id: CORR-MCR-029
title: "Correção: \"a diferença entre c-opcao e c-opcao2 é a câmera e nada mais\" omite os 15 bytes de alta entropia"
type: correção
category: engenharia-reversa
status: concluído
depends_on: []
---

# CORR-MCR-029: são 17 bytes de diferença, não 2

## Problema identificado

[`/docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md`](/docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md):194
apresenta o par `c-opcao` / `c-opcao2` como um isolamento limpo:

> Ele foi gravado **sobre** o `c-opcao`, não a partir do zero, então a
> diferença entre os dois é a câmera e nada mais

e segue com um bloco de dois bytes (`0x02104` e `0x02102`). A diferença medida
é de **17 bytes**: os dois citados **mais** os 15 de `0x02035..0x02043`.

Não contradiz a conclusão — o mapa registra à parte que esse campo muda em toda
gravação que mudou algo, e é a mesma medição. Mas a frase, lida por quem for
escrever o gravador, sugere que trocar um enum move dois bytes, e o campo de
alta entropia é justamente o que não se sabe reproduzir.

## Evidência

```
c-opcao x c-opcao2 diferem em: 0x2035 0x2036 0x2037 0x2038 0x2039 0x203a
                               0x203b 0x203c 0x203d 0x203e 0x203f 0x2040
                               0x2041 0x2042 0x2043 0x2102 0x2104
```

`0x02104` `03` → `02` (a câmera), `0x02102` `ad` → `ac` (a soma acompanhando),
e os 15 restantes são o campo de `0x02035`.

## Causa raiz

A frase descreve a diferença **de comportamento no jogo** (só a câmera mudou) e
o bloco abaixo dela é lido como a diferença **de bytes**.

## Correção

### Arquivo: `docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md`

Dizer as duas coisas: no jogo mudou só a câmera; no cartão mudaram 17 bytes —
os dois de interesse e os 15 de alta entropia, que mudam em toda gravação. É
o par que faz do `c-opcao2` um isolamento útil **e** a segunda amostra do
comportamento do campo de `0x02035`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md` | modificar |

## Verificação

- [x] o diff byte a byte de `work/cards/c-opcao.mcr` × `c-opcao2.mcr` e a frase
      do doc dizem o mesmo número
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-10

**Resumo do que foi feito:**

A frase passou a dizer as duas coisas separadas, que é o que a medição sustenta:
**no jogo mudou só a câmera; no cartão mudaram 17 bytes.** O bloco ganhou a
terceira linha, os 15 de `0x02035..0x02043`, ao lado dos dois de interesse.

E ganhou a consequência para quem for escrever o gravador, que é o motivo de a
frase antiga importar: trocar um enum move dois bytes **que se sabe
reproduzir** e quinze **que não** — e zero é aceito num cartão de primeira
execução, que é a saída registrada. O par continua sendo o isolamento útil, e
passou a ser também, explicitamente, a segunda amostra do comportamento do
campo de alta entropia.

**Problemas encontrados:**

Nenhum. O diff deu exatamente os 17 bytes da CORR, na primeira corrida.

**Medições:**

| medida | valor |
|---|---|
| bytes diferentes entre `c-opcao` e `c-opcao2` | **17** |
| de interesse | `0x02104` (`03` → `02`, a câmera), `0x02102` (`ad` → `ac`, a soma) |
| campo de alta entropia | `0x02035..0x02043`, **15** bytes, trocados por inteiro |
| `roms/`, `mcr/` | intocados (leitura pura) |

**Arquivos criados/modificados:**

- `docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md` — a distinção entre o que
  mudou na tela e o que mudou no cartão, e a terceira linha do bloco
