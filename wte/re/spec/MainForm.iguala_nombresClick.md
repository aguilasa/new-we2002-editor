---
handler: iguala_nombresClick
formulario: MainForm
endereco: 0x0040d43c
veredito: implementado
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

**O que mantinha o veredito `aberto` era outra coisa, e ela foi medida em
2026-08-18 pela [CORR-WTE-060](../../../docs/tasks/CORR-WTE-060.md): não é
defeito do port.** A
[CORR-WTE-057](../../../docs/tasks/CORR-WTE-057.md) tinha medido que o port
**não desabilita** o `iguala_nombres` no time-modelo — 518 px de mudança no
oráculo, **0** no port — com a linha presente no `.inc` do
`lista_equiposChange` e o vizinho `boton_nombres2iso` acinzentando certo.

A causa é o **widgetset**, não o código:

- a LCL desenha o glifo desabilitado aplicando `gdeDisabled`, que é uma
  **conversão para tons de cinza**. Pixel com `R = G = B` é ponto fixo dela;
- o glifo do `iguala_nombres` tem **três cores** — `#000000` (275 px),
  `#FFFFFF` (306 px) e `#76B6FF`, que é a cor transparente. Todo pixel
  desenhado é preto ou branco puro, logo já é cinza, logo a conversão não muda
  nada. **0 px, e é o resultado correto da regra da LCL**;
- o Win32 não faz grayscale: o `comctl32` monta o glifo desabilitado de uma
  máscara monocromática. Medido no recorte do oráculo — preto vira `#A6A6A6`
  (275 px) e 123 px brancos viram fundo, o que dá exatamente os 518.

As **duas hipóteses** que a CORR-WTE-057 tinha levantado estão **refutadas**,
cada uma por uma medição isolada num harness LCL de 90×40 px:

| variável trocada | mudança ao desabilitar |
|---|---|
| nada (como está hoje) | 0 px |
| `ParentFont := True` | 0 px — a fonte não é a causa; o botão não tem `Caption` |
| glifo recolorido para fundo `C0C0C0` | 257 px — muda porque isso torna os 394 px de `#76B6FF` **opacos**, não porque a cor transparente importe |
| vizinho recolorido para fundo `FFB676` | 513 px — continua acinzentando, o que sozinho derruba a hipótese da cor |

**A prova de que a regra é o grayscale, e não outra coisa:** o
`boton_nombres2iso` tem **280 pixels não-cinza** no glifo, e muda **280 px** no
`compara_tela.sh --habilitacao` do app rodando. O mesmo número dos dois lados.

O conjunto é fechado e tem conferidor:
[`check_glifos_disabled.py`](../../tools/check_glifos_disabled.py) varre os 59
botões com glifo dos 18 formulários e acha **5** invariantes — `iguala_nombres`,
`parriba` e `pabajo` no `MainForm`, `oscurecer` e `aclarar` no `color`. Entrar
ou sair desse conjunto derruba o `make -C wte check`.

Registrado como **divergência deliberada** na
[WTE-TASK-35](../../../docs/tasks/35-divergencias-deliberadas.md): é limitação
de plataforma, atinge cinco botões, e o estado lógico está certo nos dois lados
— o que difere é só o desenho.

Pascal em
[`../../src/impl/ep2002_mainform.iguala_nombresClick.inc`](../../src/impl/ep2002_mainform.iguala_nombresClick.inc).
