---
id: CORR-WTE-100
title: "Correção: a citação `{$Q-}` num comentário liga a diretiva de verdade, e o {$POP} deixa de restaurar"
type: correção
category: código
status: pendente
depends_on: []
---

# CORR-WTE-100: a diretiva citada na prosa vale como diretiva

## Problema identificado

O cabeçalho do `PrecoDaSoma`, em
[`wte/src/we2002_preco.pas`](../../wte/src/we2002_preco.pas), cita a diretiva
que vem logo abaixo:

```pascal
{ LongInt em TODOS os quatro, e transbordo e o comportamento pedido -- ver o
  item 1 do cabecalho. `{$Q-}` porque o FPC pode estar com verificacao de
  overflow ligada, e ai o transbordo viraria excecao em vez de valor. }
{$PUSH}{$Q-}{$R-}
```

As crases são enfeite de Markdown; para o compilador aquilo é um `{` dentro de
um `{ }`. Duas consequências, e a segunda é a que importa:

1. **O `Warning: (2005) Comment level 2 found`**, que é o **único** warning do
   build inteiro. Enquanto ele existir, "build limpo" não é o baseline, e o gate
   *"`lazbuild` sem warning novo"* trabalha comparando contagem em vez de exigir
   zero;
2. **A diretiva citada é processada.** O `{$Q-}` da prosa liga de verdade, e
   liga **antes** do `{$PUSH}`. O `PUSH` passa a salvar um estado que já tem
   `Q-`, e o `{$POP}` da linha 149 restaura para esse mesmo estado — ou seja,
   **não restaura nada**. O `PrecoDoJogador`, logo abaixo, roda sem verificação
   de overflow mesmo que o projeto a ligue.

## Evidência

O sítio, e o fato de ser único na árvore:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -rn '`{\$' wte/src --include='*.pas' --include='*.inc'
lazbuild -B wte/wte.lpi 2>&1 | grep -c Warning
```

```text
wte/src/we2002_preco.pas:138:    item 1 do cabecalho. `{$Q-}` porque o FPC …
1
```

**A diretiva vale dentro do comentário** — medido com um programa mínimo,
compilado com `-Co` (verificação de overflow **ligada** na linha de comando):

```pascal
{ a diretiva abaixo esta DENTRO deste comentario: {$Q-} }
a := High(LongInt);
b := a + 1;          { com -Co isto deveria dar Runtime error 215 }
```

```text
Warning: Comment level 2 found
-2147483648            <- nao levantou: o {$Q-} do comentario valeu
```

**E o `{$POP}` não restaura** — mesmo programa, agora com o par completo:

```pascal
{ comentario com diretiva embutida: {$Q-} }
{$PUSH}{$Q-}{$R-}
a := High(LongInt); b := a + 1;
{$POP}
a := High(LongInt); b := a + 1;   { depois do POP, deveria levantar }
```

```text
-2147483648            <- continua sem levantar depois do POP
```

**O modo decide entre aviso e erro fatal**, e os três foram medidos:

| Modo | O que acontece |
|---|---|
| `objfpc` (o da unidade, linha 69) | comentários aninham → fecha certo, sai o aviso |
| `fpc` | idem |
| `delphi` | não aninham → o comentário fecha no `}` do `{$Q-}`, o resto vira código, `Fatal: illegal character "'\`'" ($60)` |

Nunca silencioso, então: ou compila com o aviso, ou explode alto na hora.

## Causa raiz

Convenção de escrita levada para dentro de comentário Pascal sem lembrar que
`{` é sintaxe. A crase protege em Markdown; no scanner do FPC ela não existe.

## Impacto hoje

**Nenhum byte muda.** O projeto não compila com `-Co`, então a verificação já
está desligada globalmente e o vazamento não altera resultado; o alcance é de
uma função (diretiva de scanner é por unidade, não vaza para outras); e o que
fica desprotegido é `Result := (Result * 5) div 3`, que para estourar `LongInt`
exigiria `Result` acima de ~429 milhões — o próprio cabeçalho da unidade
registra que jogador real não chega perto.

O que se perde é o **guard**: um `{$PUSH}`/`{$POP}` que não restaura é
exatamente aquilo em que alguém confia sem reler.

## Correção

### Arquivo: `wte/src/we2002_preco.pas`

Tirar as chaves da citação na linha 138 — `` `$Q-` `` em vez de `` `{$Q-}` ``.
Dois caracteres. A frase continua dizendo a mesma coisa, o comentário deixa de
aninhar, a diretiva deixa de ser processada fora do `PUSH`, e o build fica com
**zero** warnings.

**Não** trocar o `{$PUSH}{$Q-}{$R-}` da linha 140: aquele é o guard de verdade e
está certo.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/src/we2002_preco.pas` | modificar |

## Verificação

- [ ] `grep -rn '`{\$' wte/src` sai vazio
- [ ] `lazbuild -B wte/wte.lpi` com **zero** warnings (era 1)
- [ ] `make -C wte check` verde
- [ ] `check_preco.py --check` verde — a fórmula não muda
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
