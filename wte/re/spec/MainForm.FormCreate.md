---
handler: FormCreate
formulario: MainForm
endereco: 0x004107c8
veredito: implementado
---

# MainForm.FormCreate

## Entrada

O **diretório corrente do processo**, por `Sysutils::GetCurrentDir()`, e seis
literais em `0x00425046`…`0x00425071`: `\image`, `\barba`, `\pelo`,
`\banderas`, `\uniformes2d`, `\data`.

**Evidência:** disassembly lido

## Saída

Sete `AnsiString` globais, montadas nesta ordem e com este encadeamento — os
quatro do meio penduram em `image`, e `data` pendura na raiz, **não** em
`image`:

```text
0x00432e84  <cwd>
0x00432e6c  <cwd>\image
0x00432e70  <cwd>\image\barba
0x00432e74  <cwd>\image\pelo
0x00432e78  <cwd>\image\banderas
0x00432e7c  <cwd>\image\uniformes2d
0x00432e80  <cwd>\data
```

São as seis pastas de asset que a
[WTE-TASK-08](../../../docs/tasks/08-convencao-dos-assets.md) já tinha medido
pelo lado do consumo ([`../assets.md`](../assets.md) seção 2); aqui aparece o
lado da produção, e os dois batem.

Depois disso, três campos publicados vão para globais: `bandera` →
`0x00432ebc`, `home1` → `0x00432ec0`, `home2` → `0x00432ec4` — os três
`TImage` que o desenho 2D usa, resolvidos pelo [`../campos.tsv`](../campos.tsv).

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Os 683 bytes do corpo não têm uma única chamada de I/O de arquivo:
a lista de importados chamados que o [`../arranque.md`](../arranque.md)
inventaria tem um item só, `Sysutils::GetCurrentDir`.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma. Não checa se as pastas existem — quem reclama é o
[`FormShow`](MainForm.FormShow.md), e só do `dat.bin`.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Concatenação de string não falha, e a inexistência da pasta só vira
problema no primeiro `LoadFromFile` — que é fase 5.

**Evidência:** disassembly lido

## Notas

**Divergência deliberada: a raiz.** O original monta tudo a partir do
diretório corrente, e por isso o editor exige ser clicado de dentro da própria
pasta; é daí que vem a mensagem `The file "dat.bin" must be in the "data"
directory`. Reproduzir isso seria reproduzir um defeito de empacotamento. O
port resolve a raiz por `WTE_ASSETS_DIR`, depois ao lado do executável, depois
a árvore de fonte (`we2002_estado.RaizDosAssets`). **Os seis nomes, a ordem e o
encadeamento são os do original.** Registrar na
[WTE-TASK-35](../../../docs/tasks/35-divergencias-deliberadas.md).

**O que não se reproduz:** o cache dos três `TImage` em global. É detalhe de
implementação em C++ sem efeito observável — em Pascal os três se alcançam pelo
campo do formulário. Vale registrar porque o global irmão desse trio,
`0x004335e4`, é exatamente o que a
[CORR-WTE-044](../../../docs/tasks/CORR-WTE-044.md) mediu sendo sobrescrito
pela carga de time com a ROM europeia: ponteiro de controle guardado em global
é o padrão que produziu o travamento do oráculo.

O Pascal está em [`../../src/impl/ep2002_mainform.FormCreate.inc`](../../src/impl/ep2002_mainform.FormCreate.inc).
