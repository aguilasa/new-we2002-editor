# `re/dfm/` — os 18 formulários em texto

Produto da **WTE-TASK-03**. Os 18 formulários do `we-team-editor.exe` vivem em
`.rsrc` como recursos `RT_RCDATA` cujo conteúdo é um stream DFM binário
começando por `TPF0`; o [`../../tools/dfm_extract.py`](../../tools/dfm_extract.py)
os decodifica e escreve aqui, em DFM textual padrão.

O censo de classes por formulário está em [`censo.md`](censo.md).

Saída de gerador: **não editar à mão.** Correção entra no `dfm_extract.py` e o
diretório é regerado:

```sh
python3 wte/tools/dfm_extract.py
python3 wte/tools/dfm_extract.py --check   # o que `make -C wte check` roda
```

## Os blobs binários ficam fora do `.dfm`

As 118 propriedades `vaBinary` — `Icon.Data`, o `Picture.Data` dos 45 `TImage`,
o `Glyph.Data` dos 28 `TSpeedButton` — somam 798 KiB. Em vez de hex inline,
cada uma virou um arquivo em `blobs/<formulário>/<dono>.<propriedade>.bin`,
referenciado no `.dfm` assim:

```
Glyph.Data = {blob SpeedButton1.Glyph.Data.bin 778 sha256:2e1dc715...}
```

A razão é a §2 do plano: esses blobs são a arte do Obocaman, da mesma natureza
dos 198 `.bmp` de `we-team-editor/` — pasta que o repositório ignora por ser
binário de terceiro sem licença. Hex é só uma codificação; colar os bytes aqui
reintroduziria no versionamento o que o `.gitignore` mantém fora dele. O que a
fase 2 precisa versionado é a **estrutura** dos formulários, e é ela que fica.

Consequências:

- `blobs/` é **ignorado pelo git** e renasce do `.exe` a cada execução, como
  `wte/assets`;
- o SHA-256 no `.dfm` versionado é o que substitui versionar os bytes: o
  `--check` confere os 798 KiB byte a byte contra ele;
- `{...}` com texto não-hexadecimal faz um leitor de DFM padrão **falhar** ao
  encontrar a referência, em vez de aceitar lixo em silêncio.

O `dfm2lfm.py` da **WTE-TASK-10** resolve a referência lendo o `.bin` ao lado.
