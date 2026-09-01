---
handler: bolaMouseMove
formulario: estrategia
endereco: 0x00408e0c
veredito: implementado
---

# estrategia.bolaMouseMove

Destaca a bola sob o ponteiro e apaga a anterior. **244 bytes**, ligado às dez
bolas `bola1`…`bola10` por `OnMouseMove`.

## Entrada

- **`Sender`**, comparado com o global `0x00434340` — a bola destacada agora;
- **`Sender.Name`**, cortado em `Copy(nome, 5, 2)`: `bola` tem quatro letras,
  então a posição 5 é o primeiro dígito e o corte de dois serve `bola1` e
  `bola10` com uma regra só.

Nada da imagem.

**Evidência:** disassembly lido

## Saída

```text
se Sender <> [0x434340] entao
    [0x434340].Brush.Color := $008000    ' verde apagado
    [0x434344].Font.Color  := $C0C0C0    ' cinza claro
[0x434340] := Sender
Sender.Brush.Color := $00FF00            ' verde vivo
[0x434344] := FindComponent('etiqjug' + sufixo)
[0x434344].Font.Color := $FFFFFF         ' branco
```

`+0x16c` é `TShape.Brush` e `+0x68` é `TControl.Font` — este último é o mesmo
deslocamento que a [`sonda_dorsal.py`](../../tools/sonda_dorsal.py) confere
contra o `vcl60.bpl` a cada rodada.

**O prefixo é `etiqjug`, não `etiqpos`.** Os dois existem no formulário, e o
`estrategia.FormCreate` usa o outro; trocar um pelo outro acharia um rótulo de
verdade, pintaria o errado e não daria erro nenhum. O literal está em
`0x00424b5e` e é o que a [`strings.tsv`](../strings.tsv) já registrava.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Todas as chamadas do corpo são VCL: `TBrush::SetColor`,
`TFont::SetColor`, `TComponent::FindComponent`, `SubString` e o par de
construção/destruição de `AnsiString`.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma. Ver o Comportamento de erro.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata, e o modo de falha é específico: **na primeira passagem do mouse os
dois globais são zero** (moram em `.bss`), e o primeiro ramo os
desreferenciaria. No `.exe` isso não acontece porque o `relojTimer` roda antes
de a janela aceitar mouse e semeia `0x00434340`.

**Evidência:** disassembly lido

## Notas

**Um global, dois papéis.** `0x00434340` é lido como "bola destacada" aqui e
como "bola sendo arrastada" no
[`bolaMouseDown`](estrategia.bolaMouseDown.md) — não há um segundo ponteiro. O
original pode fazer isso porque para apertar o botão sobre a bola o ponteiro
necessariamente passou por ela primeiro, e este handler já a registrou.

**Divergência deliberada** ([WTE-TASK-35](../../../docs/tasks/concluidos/35-divergencias-deliberadas.md)):
o port confere se os globais são `nil`. Sem o `relojTimer` portado nada os
semeia, e sem a guarda o primeiro movimento derrubaria o formulário.

Pascal em
[`../../src/impl/ep2002_estrategia.bolaMouseMove.inc`](../../src/impl/ep2002_estrategia.bolaMouseMove.inc);
o estado compartilhado, em
[`../../src/impl/ep2002_estrategia.aux.inc`](../../src/impl/ep2002_estrategia.aux.inc).
