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

**O limite do segundo campo era o motivo do veredito, e deixou de ser em
2026-08-18.** O original usa `DWORD[0x00433b48] - 1`, uma global de BSS que
**nenhum `mov` direto escreve** — a busca por `mov ds:0x433b48,reg` e por
`mov DWORD PTR ds:0x433b48,imm` no `.text` inteiro não achou nada, então ela é
preenchida por outro caminho.

O mesmo número aparece uma segunda vez: em `0x0040cc48` o original faz
`edit_nombre2.MaxLength := DWORD[0x00433b48] - 1`. Os dois limites são o mesmo
valor, o que confirma a *leitura* sem revelar o *valor*.

**O valor saiu, e por confirmação cruzada.** O
[`dump_truncamento.py`](../../tools/dump_truncamento.py) mede as três chamadas a
`SetMaxLength` e cruza cada expressão com a largura do campo de destino na
camada de dados — que é o `we2002_core`, byte-idêntico ao `ed.exe`.
`mixed_case_name` tem 20 bytes, logo `[0x00433b48] = 20` e o limite é **19**,
que é o que o port já usava. O gerador **aborta** se os dois lados discordarem,
então isto deixou de ser "o mesmo número por outro caminho, sem confirmação" e
passou a ser conferência que roda a cada `make check`. Ver
[`../truncamento.md`](../truncamento.md).

**O achado que saía daqui foi corrigido na mesma passagem: o port não punha
`MaxLength` em `edit_nombre1` nem em `edit_nombre2`.** Os dois campos aceitavam
texto de qualquer tamanho. Agora o `MainForm.FormShow` os põe, e por `SizeOf` do
campo de destino em vez de literal — `raw_kanji_name` dividido por dois (o nome
kanji guarda dois bytes por caractere) e `mixed_case_name` menos um.

**O que MANTÉM o veredito `aberto` é outra coisa, e ela é um defeito do port
sem causa medida.** A
[CORR-WTE-057](../../../docs/tasks/CORR-WTE-057.md) mediu que o port **não
desabilita** o `iguala_nombres` no time-modelo: 518 px de mudança no oráculo,
**0** no port. O `.inc` do `lista_equiposChange` tem a linha
(`iguala_nombres.Enabled := nacional`), o `.lfm` traz o controle nascendo
`Enabled = False`, e o vizinho `boton_nombres2iso` — mesmo `TSpeedButton`,
mesmo `Flat = True`, mesmo grupo — acinzenta certo nos dois lados. A única
diferença entre os dois no `.lfm` é `ParentFont = False` mais as propriedades
de fonte, o que não explica glifo. **Continua sem causa medida.**

Duas hipóteses foram levantadas em 2026-08-18 e **nenhuma foi testada**, então
nenhuma entra aqui como explicação: a cor transparente do glifo (o
`iguala_nombres` começa em `FFB676`, o fundo do formulário, e o vizinho em
`C0C0C0`) e o `ParentFont = False`. Registrar hipótese não medida como causa é
o modo de a spec virar ficção.

A [CORR-WTE-057](../../../docs/tasks/CORR-WTE-057.md) já escreveu que este
defeito **pede correção própria** e que o escopo dela era o instrumento, não o
defeito. Essa correção **ainda não foi aberta**, e é o que falta para este
handler chegar a `implementado`.

Pascal em
[`../../src/impl/ep2002_mainform.iguala_nombresClick.inc`](../../src/impl/ep2002_mainform.iguala_nombresClick.inc).
