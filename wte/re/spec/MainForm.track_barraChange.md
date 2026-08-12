---
handler: track_barraChange
formulario: MainForm
endereco: 0x0040ca10
veredito: aberto
---

# MainForm.track_barraChange

**O handler que edita as barras de força.** 166 bytes, e o primeiro handler de
edição deste projeto a mudar estado do jogo — os anteriores só liam.

## Entrada

- `track_barra.Position` (campo `0x0228` da instância de `TTrackBar`, lido
  direto do `Sender` e não por getter). A faixa é `0..9`: `Max = 9`,
  `Min = 0`, `Frequency = 1` no formulário.
- `0x0043459c` — qual barra está marcada, que o
  [`sel_barraClick`](MainForm.sel_barraClick.md) escreveu.

**Evidência:** disassembly lido

## Saída

```text
barra := FindComponent('barra' + IntToStr(marcada))
barra.Width := 11 * Position + 9
byte[0x00434592 + marcada] := Position
```

Duas saídas, nesta ordem: a largura na tela e o byte no buffer de edição. A
cadeia `'barra'` está em `0x00424d69`, e a busca é por **nome** — o original
monta `'barra' + IntToStr` e chama `TComponent::FindComponent`, em vez de
indexar o campo `0x0338` do formulário, que é onde `barra0` mora.

`11 * v + 9` é a **mesma** aritmética da carga (`lea` / `lea` / `add 9`,
literal do disassembly), então uma barra recém-editada e uma recém-carregada
com o mesmo valor têm a mesma largura em pixel. É o que torna a comparação de
tela capaz de julgar este handler.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum na imagem.** O que ele grava é o buffer de `0x00434592`, em memória.

Quem leva esses cinco bytes para o disco é o `boton_barras2isoClick`
(`0x0040cab8`), que carrega o mesmo `0x00434592` em `ebx` — medido em
`0x0040cb3d`. É da
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md).

**Evidência:** disassembly lido

## Pré-condições

**Nenhuma.** Não confere se há time carregado nem se o global caiu em 0..4. O
que segura o handler é a tela: a `track_barra` nasce `Enabled = False` e só a
carga de um time nacional a habilita.

O port acrescenta a faixa 0..4, pela mesma razão e com a mesma ressalva do
[`sel_barraClick`](MainForm.sel_barraClick.md).

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. `FindComponent` que devolvesse `nil` derrubaria o original no
`SetWidth` seguinte; o port testa `is TControl` antes, como já faz na carga.

**Evidência:** disassembly lido

## Notas

**O buffer de edição é o achado que organiza o grupo, e ele não é cache.** Três
rotinas tocam `0x00434592`: a carga o enche a partir da imagem, este handler
grava nele, e a gravação lê dele. Se o port desenhasse a barra a partir de
`Jogo.teams[].bar_*` — que é de onde a carga tira o valor — editar mudaria o
pixel e a gravação escreveria o valor velho, e **o golden acusaria a gravação**
por um defeito que é da edição. Por isso `BarrasEmEdicao` existe separado da
camada de dados, em
[`../../src/impl/ep2002_mainform.aux.inc`](../../src/impl/ep2002_mainform.aux.inc).

O buffer só é enchido com `nacional`: em `0x0040cefa` o original compara o
índice com 95 e pula o laço de leitura inteiro. O port reproduz.

**Veredito `aberto`, e o que falta é gravação, não medição.** A spec basta
para o corpo, e o corpo está escrito
([`../../src/impl/ep2002_mainform.track_barraChange.inc`](../../src/impl/ep2002_mainform.track_barraChange.inc)).
O que não existe ainda é como julgar:

- **por byte** — precisa do `boton_barras2isoClick`, que é da WTE-TASK-27. O
  enunciado da [WTE-TASK-26](../../../docs/tasks/26-handlers-de-edicao.md) pede
  "editar pela tela nos dois lados, então gravar nos dois"; o segundo verbo
  não tem dono nesta task;
- **por pixel** — o [`compara_tela.sh`](../../tools/compara_tela.sh) leva os
  dois lados ao mesmo time e mede as cinco larguras, mas não edita barra
  nenhuma. Estender é barato e está nomeado no Log da task.

Enquanto os dois não existirem, o corpo está escrito a partir de spec medida e
**não conferido** — que é o mesmo estado em que o `lista_equipos_2Change`
fechou a WTE-TASK-25, e pela mesma honestidade.
