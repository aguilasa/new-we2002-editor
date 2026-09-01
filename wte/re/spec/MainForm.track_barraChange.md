---
handler: track_barraChange
formulario: MainForm
endereco: 0x0040ca10
veredito: implementado
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
[WTE-TASK-27](../../../docs/tasks/concluidos/27-handlers-de-gravacao.md).

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

**Veredito `implementado`: a régua desta task fechou verde.**
`compara_tela.sh --edicao` leva os dois lados ao time 2, marca `sel_barra1`
("Defesa") e clica na trilha da `track_barra`. Medido em 2026-08-12, ROM
japonesa:

| | oráculo | port |
|---|---|---|
| as cinco larguras, em px | `64, 75, 75, 75, 75` | `64, 75, 75, 75, 75` |
| defesa, valor do jogo | 4 → **6** | 4 → **6** |
| as outras quatro contra o `we2002_core` | 4 de 4 exatas | 4 de 4 exatas |

As quatro não editadas continuarem ancoradas no dump é metade do resultado: ela
mostra que a edição **não respingou**. A outra metade é a barra editada ter
mudado — sem isso, "os dois lados concordam" passaria com a tela intacta, que
é o par que a [WTE-TASK-20](../../../docs/tasks/concluidos/20-round-trip-headless.md)
ensinou a exigir: concordam, **e** fizeram alguma coisa. Do lado do port o
`compara_tela.sh` ainda exige do trace 1 `sel_barraClick` e o número previsto
de `track_barraChange`.

**Um número que precisou ser medido antes de o roteiro existir: o passo do
clique.** Clique na trilha não arrasta o cursor, pagina — e o `PageSize` do
comctl32 sob Wine e o do `TTrackBar` da LCL sobre gtk2 são código diferente,
com a faixa curta (`Max = 9`). Um passo de 2 de um lado e 1 do outro daria
divergência de tela que não é do handler. **Os dois andam +2 por clique**
(4 → 6 → 8; larguras 53, 75, 97).

**O que esta régua NÃO julga, e quem julga:** que os bytes editados cheguem à
imagem certa. Isso é `boton_barras2isoClick`, da
[WTE-TASK-27](../../../docs/tasks/concluidos/27-handlers-de-gravacao.md) — e é critério de
conclusão **dela**, não exclusão silenciosa daqui. Pixel igual dos dois lados
não prova que os dois escreveram o mesmo byte do modelo.
