---
handler: FormCreate
formulario: ficha_about
endereco: 0x00402de4
veredito: trivial
---

# ficha_about.FormCreate

## Entrada

Nada.

**Evidência:** disassembly lido

## Saída

Nada. O corpo do original tem **um byte** — um `ret`. É a forma `vazio` do
[`../arranque.md`](../arranque.md), e é o único dos 18
`FormCreate`/`FormShow` assim.

Consequência visível: o `ficha_about` é o único formulário que fica com a cor
de projeto do DFM (`clBtnFace`) na tela, porque não há `OnCreate` para
substituí-la.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.**

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não há entrada, então não há entrada inválida.

**Evidência:** disassembly lido

## Notas

O handler **existe** e está ligado no DFM (`OnCreate = FormCreate`), e por isso
tem entrada aqui e corpo escrito no port — não stub. A diferença aparece no
trace: `REStub` diz *ainda não se sabe*, `REMark` diz *passou por aqui e não
faz nada*, e as duas frases mandam procurar em lugares diferentes.

Um handler publicado e vazio é resultado legítimo, não medição incompleta: o
compilador da Borland não emitiria o método se ele não estivesse escrito no
`.cpp`, e ele não entraria na published method table se não estivesse
declarado. Alguém escreveu o método com corpo vazio e ligou no formulário —
provavelmente clicando duas vezes no `OnCreate` do inspetor de objetos e nunca
voltando.

O Pascal está em [`../../src/impl/ep2002_about.FormCreate.inc`](../../src/impl/ep2002_about.FormCreate.inc).
