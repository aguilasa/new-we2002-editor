---
id: CORR-WTE-100
title: "Correção: a citação `{$Q-}` num comentário abre nível 2 — o único warning do build, e um erro fatal em modo delphi"
type: correção
category: código
status: concluído
depends_on: []
---

# CORR-WTE-100: a citação com chaves abre comentário de nível 2

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

As crases são enfeite de Markdown; para o scanner do FPC aquilo é um `{` dentro
de um `{ }`. Duas consequências, as duas medidas:

1. **`Warning: (2005) Comment level 2 found`** — o **único** warning do build
   inteiro. Enquanto ele existir, "build limpo" não é o baseline, e o gate
   *"`lazbuild` sem warning novo"* trabalha comparando contagem em vez de exigir
   zero;
2. **Em `{$mode delphi}` isso deixa de compilar.** Naquele modo comentários não
   aninham: o comentário fecharia no `}` do `{$Q-}`, o resto da frase viraria
   código e o build morre com `Fatal: illegal character "'\`'" ($60)`. A
   unidade declara `{$mode objfpc}` na linha 69 e por isso passa hoje — a
   fragilidade é a troca de modo, não o estado atual.

**O que esta correção NÃO é**, e a distinção custou três instrumentos: a
diretiva citada **não** é processada, e o `{$PUSH}`/`{$POP}` da linha 140/149
**restaura corretamente**. A primeira redação desta correção afirmava o
contrário nos dois pontos — ver o Log.

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

**O modo decide entre aviso e erro fatal**, e os três foram medidos com um
programa mínimo que reproduz o padrão:

| Modo | O que acontece |
|---|---|
| `objfpc` (o da unidade, linha 69) | comentários aninham → fecha certo, sai o aviso |
| `fpc` | idem |
| `delphi` | não aninham → `Fatal: illegal character "'\`'" ($60)` |

**E o instrumento que mostra que a diretiva citada não vale.** Ele precisa
distinguir `Q+` de `Q-`, e o primeiro que se tentou **não distinguia**: soma de
`LongInt` em x86-64 não levanta nem com `-Co`, porque a conta acontece num
registrador de 64 bits. Com `Int64` a diferença aparece:

```pascal
{$mode objfpc}{$Q+}          { ou {$Q-} }
function Op(x: Int64): Int64; begin Result := x + 1; end;
...  WriteLn(Op(High(Int64)));
```

```text
{$Q+}  ->  Runtime error 215
{$Q-}  ->  -9223372036854775808
```

Com esse instrumento, a citação embutida:

```pascal
{$mode objfpc}{$Q+}
{ a diretiva abaixo esta DENTRO deste comentario: {$Q-} }
...  WriteLn(Op(High(Int64)));
```

```text
Warning: Comment level 2 found
Runtime error 215        <- Q+ seguiu LIGADO: a diretiva citada nao valeu
```

E o par completo, com a citação embutida antes dele:

```text
dentro do guard: -9223372036854775808     <- {$Q-} do PUSH valeu
depois do POP:   Runtime error 215        <- o POP restaurou
```

## Causa raiz

Convenção de escrita levada para dentro de comentário Pascal sem lembrar que
`{` é sintaxe. A crase protege em Markdown; no scanner do FPC ela não existe.

## Impacto hoje

**Nenhum byte muda, e nenhum guard está quebrado.** O que se ganha consertando
são duas coisas pequenas e reais: um build com **zero** warnings, que é um
baseline melhor do que "um warning conhecido"; e a remoção de uma mina para
quem um dia trocar o modo da unidade.

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

- [x] `grep -rn '`{\$' wte/src` sai vazio
- [x] `lazbuild -B wte/wte.lpi` com **zero** warnings (era 1)
- [x] `make -C wte check` verde
- [x] `check_preco.py --check` verde — a fórmula não muda
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-24

**Resumo do que foi feito:**

Dois caracteres: `` `{$Q-}` `` virou `` `$Q-` `` na linha 138. A frase diz a
mesma coisa, o comentário deixa de aninhar, e o build passou de **1** para
**0** warnings. O `{$PUSH}{$Q-}{$R-}` da linha 140 ficou intacto — aquele é o
guard de verdade e sempre esteve certo. O arquivo tem as mesmas **160** linhas
depois da troca, então a fração da §4.4 não se move.

**Problemas encontrados:**

1. **A primeira redação desta correção estava errada, e o instrumento é que
   estava.** Ela afirmava duas coisas: que a diretiva citada é *processada*, e
   que por isso o `{$POP}` deixa de restaurar. As duas saíram de um teste que
   usava `LongInt` e `-Co` — e esse teste **não distingue `Q+` de `Q-`**:
   em x86-64 a soma de `LongInt` acontece num registrador de 64 bits e não
   levanta em nenhum dos dois casos. O teste imprimia o mesmo número sempre, e
   eu li "imprimiu número" como "a diretiva valeu".

   Trocado para `Int64`, o instrumento passa a distinguir (`Q+` → `Runtime
   error 215`, `Q-` → o valor), e as duas afirmações **caem**: com `{$Q+}` no
   topo e a citação embutida logo abaixo, o programa **levanta** — o `Q+` seguiu
   ligado, a diretiva citada não valeu. E com o par completo, `dentro do guard`
   imprime o valor e `depois do POP` levanta: o `POP` restaura.

   Vale a lição, porque ela é geral: **um teste diferencial que não foi
   conferido contra o caso de controle não mede nada.** O controle aqui custava
   uma corrida — compilar o mesmo programa com `{$Q+}` e com `{$Q-}` e exigir
   saídas diferentes — e teria pego o erro antes de ele virar texto commitado.

2. **O corpo da correção e a linha da tabela foram reescritos** com o que ficou
   medido. O registro de abertura no fim do `correcoes-progresso.md` guarda o
   que a revisão escreveu no dia, como os outros, e ganhou uma nota apontando
   para cá.

3. **Nenhum gate de comportamento foi rodado, e não deve ser.** A troca é dentro
   de um comentário e está medido que a diretiva embutida nunca foi processada:
   o código gerado é bit a bit o mesmo. O `check_preco.py --check` continua
   verde com a mesma amostra, que é o que prova que a fórmula não mudou.

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `wte/src/we2002_preco.pas` | modificado — linha 138, dois caracteres |
