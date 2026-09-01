---
handler: boton_dialogo_texClick
formulario: MainForm
endereco: 0x0040dfe8
veredito: divergencia deliberada
---

# MainForm.boton_dialogo_texClick

Abre o diálogo de arquivo do **uniforme** (`.tex`) e guarda o caminho
escolhido. 448 bytes.

## Entrada

- `dialogo_tex`, o `TOpenDialog` do formulário — o handler o executa e lê
  `FileName`;
- `lista_equipos.ItemIndex`, para compor o nome sugerido.

**Evidência:** disassembly lido

## Saída

```text
se dialogo_tex.Execute:
    monta o caminho a partir do FileName e do time selecionado
    texto_dialogo_tex.Caption := <nome do arquivo>
    abre o arquivo pelas rotinas de I/O da RTL (0x00417170, 0x00417210)
```

O `texto_dialogo_tex` é a etiqueta que mostra o arquivo escolhido, o irmão do
`texto_dialogo_we` do caminho da imagem.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum na imagem de CD.** O arquivo que ele abre é o `.tex` externo, não a
ROM. Quanto ao conteúdo desse arquivo, a leitura ainda não foi feita: as
rotinas `0x00417170` (159 B) e `0x0040423c` são de I/O da RTL e o que se faz
com os bytes está em `0x00417170`, não lida.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma além do diálogo ser cancelável: se `Execute` devolve falso, o corpo
sai sem tocar em nada.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Arquivo inexistente ou ilegível segue para a RTL sem checagem no
corpo do handler.

**Evidência:** disassembly lido

## Notas

## O veredito passou a `divergencia deliberada` em 2026-08-24

Ele esteve `aberto` com a razão *"é do grupo de carga por afinidade, não por
dependência — o formato `.tex` é assunto da WTE-TASK-29"*. **A 29 fechou sem
ele**, e a metade que ela deveria não é a deste handler: o que lê e grava os
bytes do `.tex` é o
[`boton_tex2isoClick`](MainForm.boton_tex2isoClick.md), portado e com gate
próprio (`golden-06-textura`). Aqui só se escolhe o arquivo.

A [CORR-WTE-093](../../../docs/tasks/concluidos/CORR-WTE-093.md) escreveu o corpo,
espelhando o irmão
[`boton_dialogo_weClick`](MainForm.boton_dialogo_weClick.md).

**A divergência que dá o veredito já estava tomada e escrita antes deste corpo
existir** — ver `TexturaEscolhida` no
[`we2002_estado`](../../src/we2002_estado.pas). O original guarda um `FILE*` em
`0x00432e60` e o tamanho em `0x00434598`, mantendo o arquivo **aberto** pela
sessão; o port guarda **caminho** e tamanho, e abre e fecha por operação.

O efeito visível: no original, apagar o `.tex` depois de escolhê-lo não impede
a gravação, porque o descritor continua válido; aqui impede. Nenhum byte de
imagem depende disso — o `boton_tex2isoClick` grava o mesmo conteúdo pelos dois
caminhos, e o `golden-06-textura` continua byte-idêntico depois deste corpo.

**E é por isso que a `0x00417170` deixou de ser pré-requisito.** A seção *Bytes
tocados* a listava como metade não lida; ela é a rotina de I/O da RTL que abre o
arquivo e lê o tamanho — exatamente o par que o port substitui pelo caminho.

Entrada da [WTE-TASK-35](../../../docs/tasks/concluidos/35-divergencias-deliberadas.md).

## Notas

O `Execute` não roda no gate, pela mesma razão do irmão: sem gerenciador de
janela o gtk2 não recebe teclado, então o lado port não digita caminho em
diálogo nenhum. Quem semeia a textura no gate é o `FormShow`, por
`WTE_TEXTURA`, e os dois caminhos terminam no **mesmo** par de globais.
