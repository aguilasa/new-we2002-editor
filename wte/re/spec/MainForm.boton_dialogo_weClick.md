---
handler: boton_dialogo_weClick
formulario: MainForm
endereco: 0x0040bd60
veredito: aberto
---

# MainForm.boton_dialogo_weClick

Abre a imagem de CD. É o primeiro handler do projeto a sair de stub, e é a
porta de entrada de todo o resto: sem imagem carregada, nenhum handler de
edição tem estado para editar.

## Entrada

O `dialogo_we`, um `TOpenDialog` do próprio `MainForm`, com `Filter = 'ISO do
W11(.bin)|*.BIN'` e `Title = 'Abre'` vindos do DFM. O caminho escolhido pelo
usuário é a entrada; o resto vem do disco.

Também lê `data/dat.bin` — o arquivo de 145.408 B que acompanha o editor. Só a
segunda metade interessa aqui (`0x20000` em diante, 14.336 B = 7 × 2048).

**Evidência:** disassembly lido

## Saída

Três coisas, nesta ordem:

1. injeta sete setores na imagem (ver *Bytes tocados*);
2. carrega o banco inteiro para a memória;
3. escreve o nome do arquivo no `texto_dialogo_we`.

**Evidência:** diff medido

## Bytes tocados

**Grava na imagem**, e este é o achado que contraria o enunciado da
[WTE-TASK-25](../../../docs/tasks/25-handlers-de-carga.md) — ele previa provar
que o grupo de carga não escreve nada.

```
0x2e08 +2048 x7  os sete setores de dat.bin[0x20000..], com salto de 0x130
                 entre um e o seguinte
```

O passo `0x130` = 304 = 2352 − 2048 é o salto sobre EDC/ECC e o cabeçalho do
setor seguinte. `0x2e08` = 11784 = 5 × 2352 + 24, o primeiro byte de dados do
setor 5.

Medido sobre `roms/japanese-shift-jis.bin`: **11.952 bytes em 7 faixas**,
`11796..13831`, `14136..16183`, `16488..18535`, `18840..20887`,
`21192..23239`, `23544..25591`, `25896..26527`. As faixas começam em 11796 e
não em 11784 porque os doze primeiros bytes já batiam.

**Duas faixas do arranque continuam sem explicação:** `1921862..1921862` (um
byte, setor 817) e `2012984..2012985` (dois bytes, setor 855). O oráculo as
grava, o port não, e elas seguem declaradas como `conhecida:` no roteiro do
gate.

**Evidência:** diff medido

## Pré-condições

`data/dat.bin` tem de existir e ser legível. O original o resolve a partir do
diretório corrente e, se não achar, mostra `O arquivo dat.bin esta fora do seu
diretorio` (literal em `0x00424cb1`).

A injeção é **idempotente por sentinela**: o byte em `0x2e14` valendo `0xFC`
significa "já injetado", e o bloco inteiro é pulado. Sem isso, reabrir a mesma
imagem regravaria os mesmos bytes.

**Evidência:** disassembly lido

## Comportamento de erro

O original não trata falha de leitura da imagem além da checagem de tamanho, e
a checagem de tamanho é **só aviso** — ele carrega assim mesmo. O port devolve
`False` de `AbreImagem` quando o arquivo não existe e escreve isso no rótulo.

**Evidência:** observação de tela

## Notas

**Este caminho não é exercitado pelo gate**, e não pode ser: sem window
manager no `:99` o GTK2 nunca considera a janela ativa, então o lado port não
recebe teclado e não digita caminho em diálogo nenhum (WTE-TASK-13). Quem
carrega no gate é o `MainForm.FormShow`, pela linha de comando — e passa pelo
mesmo `AbreImagem`, que é onde a injeção mora. O `.exe` tem os dois trechos de
injeção duplicados, um aqui e outro no `FormShow`; o port tem um só.

**Veredito ainda `aberto`** porque as duas faixas de cima não têm explicação
medida, e porque a carga da tela (nome, barras, elenco) é o resto da
WTE-TASK-25.
