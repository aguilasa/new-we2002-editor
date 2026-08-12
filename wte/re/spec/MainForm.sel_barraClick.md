---
handler: sel_barraClick
formulario: MainForm
endereco: 0x0040c9d0
veredito: aberto
---

# MainForm.sel_barraClick

Escolhe **qual** das cinco barras de força a `track_barra` edita. 61 bytes —
o menor handler de edição do `MainForm`, e o mais fácil de ler inteiro.

Ligado aos cinco rádios `sel_barra0..4` de uma vez.

## Entrada

- **`Sender.ComponentIndex`** e `sel_barra0.ComponentIndex` (o campo `0x310`
  do formulário, pelo [`campos.tsv`](../campos.tsv)). O original chama
  `TComponent::GetComponentIndex` nos dois e **subtrai** — não compara o
  `Sender` com cada um dos cinco botões. O resultado é o 0..4 que indexa tudo
  o mais.
- `BarrasEmEdicao` — o buffer de cinco bytes em `0x00434592`, que a carga de
  time encheu.

**Evidência:** disassembly lido

## Saída

```text
marcada := Sender.ComponentIndex - sel_barra0.ComponentIndex
0x0043459c := marcada                       ' o global "qual barra"
track_barra.Position := byte[0x00434592 + marcada]
```

Nada mais. Não mexe em largura de barra, não toca a lista de times, não
desenha.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Não abre a imagem.

**Evidência:** disassembly lido

## Pré-condições

**Nenhuma.** Não confere se o índice caiu em 0..4, não confere se há time
carregado, não confere `nacional`. O que segura o handler é a tela: os cinco
rádios nascem `Enabled = False` no `.dfm` e só a carga de um time nacional os
habilita — e ela, sim, confere o `< 95`.

O port **acrescenta** a faixa (`Exit` fora de 0..4). É divergência de robustez
sobre entrada que a tela não produz, e está registrada nas Notas.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Com um `Sender` que não fosse um dos cinco rádios, o original
indexaria `0x00434592` fora dos cinco bytes e leria o vizinho — os dois
handlers do binário compartilham `.data` sem separador.

**Evidência:** disassembly lido

## Notas

**A aritmética de índice de componente vale nos dois lados, e isso foi
conferido.** Os cinco `object sel_barra*` são consecutivos no formulário
(posições 44 a 48 do [`ep2002_mainform.lfm`](../../forms/ep2002_mainform.lfm),
na ordem do `.dfm`), e a LCL cria na ordem do arquivo como a VCL criava. Isso
é a ordem de **criação**, não a de campo — a distinção que a
[WTE-TASK-25](../../../docs/tasks/25-handlers-de-carga.md) pagou para aprender
(`.dfm` acerta 73 de 440 deslocamentos de campo). Aqui a ordem certa é
justamente a do `.dfm`, porque `ComponentIndex` é posição na lista
`Components` do dono, que a criação preenche.

**Duas divergências deliberadas do port**, as duas de robustez e nenhuma
alcançável pela tela — entrada para a
[WTE-TASK-35](../../../docs/tasks/35-divergencias-deliberadas.md):

1. `Sender` que não seja `TComponent` sai sem fazer nada;
2. índice fora de 0..4 sai sem fazer nada, em vez de ler o byte vizinho.

**Veredito `aberto`: escrito e não conferido contra o original.** O efeito
visível deste handler é a posição do cursor da `track_barra`, e o
[`compara_tela.py`](../../tools/compara_tela.py) mede largura de barra, não
posição de cursor de trackbar. Quem o julga de verdade é o par
`track_barraChange` + `boton_barras2isoClick`, e o segundo é da
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md).

Pascal em
[`../../src/impl/ep2002_mainform.sel_barraClick.inc`](../../src/impl/ep2002_mainform.sel_barraClick.inc).
