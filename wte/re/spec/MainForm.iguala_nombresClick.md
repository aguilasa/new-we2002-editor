---
handler: iguala_nombresClick
formulario: MainForm
endereco: 0x0040d43c
veredito: aberto
---

# MainForm.iguala_nombresClick

"Usar Nome1 nos 3 tipos de nomes" — a dica do próprio botão, no DFM. 248 bytes.

## Entrada

`edit_nombre1.Text` (campo `0x35c`) e a global `0x00433b48`.

**Evidência:** disassembly lido

## Saída

```text
edit_nombre2.Text := Copy(edit_nombre1.Text, 1, DWORD[0x00433b48] - 1)
edit_nombre3.Text := Copy(edit_nombre1.Text, 1, 3)
```

Duas cópias truncadas, cada uma ao que cabe no campo de destino. O `3` é
literal no original e casa com o `MaxLength = 3` que o DFM põe no
`edit_nombre3` — é a abreviatura.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Mexe só nos dois `TEdit`. Quem leva nome para a imagem é o
`boton_nombres2isoClick`, da
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md).

**Evidência:** disassembly lido

## Pré-condições

**Nenhuma.** Não confere se há time carregado nem se o campo está vazio. O que
o segura é a tela: o botão nasce `Enabled = False` e a carga de um time
nacional o habilita — e é justamente aí que mora o defeito registrado abaixo.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Com `edit_nombre1` vazio, os outros dois ficam vazios.

**Evidência:** disassembly lido

## Notas

**O limite do segundo campo não foi medido, e é por isso que o veredito é
`aberto`.** O original usa `DWORD[0x00433b48] - 1`, uma global de BSS que
**nenhum `mov` direto escreve** — a busca por `mov ds:0x433b48,reg` e por
`mov DWORD PTR ds:0x433b48,imm` no `.text` inteiro não achou nada, então ela é
preenchida por outro caminho (ponteiro, ou estrutura carregada em bloco).

O mesmo número aparece uma segunda vez: em `0x0040cc48` o original faz
`edit_nombre2.MaxLength := DWORD[0x00433b48] - 1`. Os dois limites são o mesmo
valor, o que confirma a *leitura* — é o comprimento máximo do campo — sem
revelar o *valor*.

**O port usa 19, tirado do tamanho do campo na camada de dados** (`names` é
`array[0..19] of AnsiChar`, então cabem 19 caracteres mais o terminador). É o
método da §4.2 — o mesmo número por outro caminho —, mas **desta vez sem
confirmação cruzada**: se a global valer outra coisa, o truncamento diverge.
Fechar isto é barato quando o oráculo estiver sendo dirigido com um nome longo,
e é entrada da
[WTE-TASK-36](../../../docs/tasks/36-buffers-e-truncamento.md).

**Achado que sai daqui e é maior que este handler: o port não põe `MaxLength`
em `edit_nombre1` nem em `edit_nombre2`.** O original põe, ao carregar a
imagem: `edit_nombre1.MaxLength := DWORD[0x00433a10] div 2` e
`edit_nombre2.MaxLength := DWORD[0x00433b48] - 1`. No port os dois campos
aceitam texto de qualquer tamanho. É divergência de comportamento, não de
pixel, e nenhum teste atual a pega — o `edit_nombre3` escapa por acaso, porque
o `MaxLength = 3` dele está no DFM e o `.lfm` o herda.

**E o botão tem um defeito próprio, ainda sem causa.** A
[CORR-WTE-057](../../../docs/tasks/CORR-WTE-057.md) mediu que o port **não
desabilita** o `iguala_nombres` no time-modelo: 518 px de mudança no oráculo,
**0** no port. O `.inc` do `lista_equiposChange` tem a linha
(`iguala_nombres.Enabled := nacional`), o `.lfm` traz o controle nascendo
`Enabled = False`, e o vizinho `boton_nombres2iso` — mesmo `TSpeedButton`,
mesmo `Flat = True`, mesmo grupo — acinzenta certo nos dois lados. A única
diferença entre os dois no `.lfm` é `ParentFont = False` mais as propriedades
de fonte, o que não explica glifo. **Continua sem causa medida.**

Pascal em
[`../../src/impl/ep2002_mainform.iguala_nombresClick.inc`](../../src/impl/ep2002_mainform.iguala_nombresClick.inc).
