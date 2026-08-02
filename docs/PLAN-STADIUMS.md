# Plano exclusivo — estádios (TMD / malha 3D / texturas)

> **Objetivo: extrair, visualizar, remontar e reimportar os estádios do
> WE2002.**
>
> Este plano é **separado de propósito**. Ele não é uma fase do
> [PLAN-FEATURES.md](PLAN-FEATURES.md): é um projeto próprio, com dependência
> nova (renderização 3D), paradigma de UI novo e um risco de corromper disco
> que nenhuma outra feature tem.
>
> **Pré-requisito duro:** PLAN-FEATURES concluído até a Fase 12. Este plano
> consome a camada ISO9660 (Fase 8), o codec LZSS (Fase 9), a gravação com
> ECC (Fase 11) e o navegador de assets (Fase 12) já prontos e testados. Não
> começar antes — reimplementar isso aqui seria duplicar as quatro.
>
> Análise do disco feita em **2026-08-02** sobre o *European Deluxe 2002-03*.
> Todo número abaixo foi medido, não estimado.

---

## 1. Ponto de partida: o que a ferramenta do CARP faz

[WE_TMD_Tools](https://github.com/maxiducoli/WE_TMD_Tools) tem duas metades:

- **Extrator** — abre `GRDM_*.BIN` e cospe as peças TMD individuais em disco;
- **Criador** — remonta um `GRDM_*.BIN` a partir de peças, permitindo trocar
  peça de um estádio por peça de outro.

O detalhe mais útil do código dele não é o algoritmo, é uma **tabela**. Em
`clsTMDTools.cs` existe `tMDsFijos`, que lista, por estádio, as peças que
**não podem ser trocadas**:

```
A  {1,2,3,11,14}    D  {1,2,3,10,13}    J  {1,2,3,11,14}    P  {1,2,3,11,14}
B  {1,2,3,10,13}    F  {1,2,3,14,17}    M  {1,2,3,16,19}    RJ {1,2,3,12,15}
C  {1,2,3,12,15}    G  {1,2,3,11,14}    MJ {1,2,3,12,15}    S  {1,2,3,11,14}
H  {1,2,3,11,14}    I  {1,2,3,10,13}    O  {1,2,3,13,16}    T  {1,2,3,11,14}
V  {1,2,3,13,16}
```

Ou seja: peças 1, 2 e 3 são fixas em **todo** estádio (quase certamente gramado
+ linhas + arcos), e mais duas específicas por estádio. É conhecimento empírico
de 20 anos de modding que economiza meses de tentativa e erro. **Isso entra no
projeto como dado, com crédito.**

---

## 2. O que os arquivos do disco realmente são (medido)

### 2.1 `GRDM_*.BIN` — a geometria

17 arquivos, 37–47 KB, um por estádio. **Não são comprimidos** — nenhum fluxo
LZSS válido em nenhum offset dos primeiros 400 bytes.

Layout:

```
[0 .. 104|112|116)   tabela de ponteiros absolutos de RAM (0x8016xxxx)
[tabela .. fim)      N modelos TMD empacotados um atrás do outro
```

Contagem por estádio, comparada com a maior peça fixa da tabela do CARP:

| Estádio | bytes | TMDs | tabela | maior peça fixa (CARP) |
|---|---:|---:|---:|---:|
| A | 46.773 | 15 | 104 | 14 |
| B | 37.545 | 13 | 112 | 13 |
| C | 43.409 | 17 | 112 | 15 |
| D | 43.125 | 14 | 104 | 13 |
| F | 45.725 | 18 | 112 | 17 |
| GJ | 42.425 | 15 | 104 | — |
| H | 44.901 | 15 | 112 | 14 |
| I | 45.053 | 14 | 112 | 13 |
| J | 46.085 | 15 | 104 | 14 |
| M | 45.821 | 20 | 104 | 19 |
| MJ | 42.104 | 16 | 104 | 15 |
| O | 43.260 | 17 | 104 | 16 |
| P | 43.941 | 15 | 104 | 14 |
| RJ | 47.441 | 17 | 104 | 15 |
| S | 47.097 | 15 | 116 | 14 |
| T | 40.557 | 15 | 112 | 14 |
| V | 45.212 | 17 | 104 | 14…16 |

O número de TMDs bate com a tabela dele em 13 dos 16 estádios que ele lista
(`#TMD = maior_fixo + 1`); os três desvios provavelmente são falso-positivo da
minha varredura por magic, que aceita qualquer `41 00 00 00` seguido de
`nobj < 64`. **Validação cruzada suficiente**: os `GRDM_*` são exatamente o
conjunto de peças que a ferramenta dele manipula, e as peças são indexadas
`1..N`.

O formato é **TMD padrão do SDK da PlayStation**, não um formato proprietário:

```
GRDM_A.BIN, primeiro TMD @ offset 336
  id = 0x41   flags = 0   nobj = 1
  obj0: vert_top=0x11a4  n_vert=126
        norm_top=0x1594  n_norm=1
        prim_top=0x001c  n_prim=102   scale=0
```

`flags = 0` significa que **os ponteiros internos do TMD são relativos** ao
início da tabela de objetos. Confirmado aritmeticamente: `prim_top = 0x1c` = o
tamanho exato da tabela de 1 objeto, e `336+12+0x11a4 + 126*8 = 5872`, que é
exatamente onde começa o TMD seguinte. **Isso é a melhor notícia do documento
inteiro**: peça é relocável, dá para reordenar e substituir sem reescrever
ponteiro interno nenhum.

### 2.2 A tabela de ponteiros — a pior notícia

Os primeiros 104–116 bytes de cada `GRDM_*` são endereços **absolutos de RAM**
da PSX (`0x80162060`, `0x80162070`, …), espaçados de 16 em 16 bytes, com zeros
intercalados. Em `GRDM_A` são 15 não-nulos — o mesmo número de TMDs.

O mesmo padrão aparece nos `GDC_*` e no `MODEL.BIN`. Nos `GDC_*` a tabela mapeia
limpo: com base = `primeiro_ponteiro − 28`, os 5 ponteiros não-nulos de
`GDC_AD.BIN` caem em **28, 11.484, 24.240, 27.844, 32.980** — seções internas
do próprio arquivo.

Consequências:

1. O arquivo é carregado num **endereço fixo de RAM** e contém ponteiros
   absolutos para si mesmo. Mudou tamanho de peça, mudou tudo depois dela, e a
   tabela **tem que ser reconstruída**.
2. O endereço-base é diferente entre `GDC_AD` (`0x800e2df4`) e `GDC_AN`
   (`0x800e2f18`). Ou o cabeçalho tem tamanho variável, ou o base é calculado
   em runtime. **Precisa ser resolvido na fase S1** — é o item de maior
   incerteza técnica do plano.
3. Somado ao fato já estabelecido de que **o jogo não acha arquivo por nome**
   (ver PLAN-FEATURES §5a — nenhuma string de nome de arquivo existe fora do
   diretório ISO9660), a política de gravação é a mesma: **fit-or-fail**. Um
   `GRDM_*` remontado tem que caber no extent original.

### 2.3 `GDC_*.BIN` — as texturas

34 arquivos (17 estádios × dia/noite), 127–195 KB. Alta entropia (**7,32–7,37
bits/byte**), zero magic de TIM, nenhum fluxo LZSS válido nos primeiros 400
bytes. Cabeçalho de 28 bytes com 7 ponteiros (5 não-nulos) para 5 seções.

`GDC_AD` × `GDC_AN` do mesmo estádio: **89,7% dos bytes diferem**. Não é o mesmo
gráfico com paleta trocada — dia e noite são conjuntos de textura distintos.

**O codec é desconhecido.** É o segundo ponto de incerteza do plano. Hipóteses a
testar em S3, nesta ordem: dados de VRAM crus 16 bpp (entropia bate); LZSS com
cabeçalho diferente; o `BemaniLZ` que aparece em
[Winning-Eleven-tools-by-CARP](https://github.com/maxiducoli/Winning-Eleven-tools-by-CARP-TESTs-TOOLs-)
(41 KB de código, formato distinto do `WECompress`).

### 2.4 Fora de escopo mas anotado

`MODEL.BIN` (64.800 bytes) tem o mesmo padrão de tabela de ponteiros. Provável
modelo de jogador. **Não entra neste plano** — mexer em modelo de jogador é
outro projeto, com outros riscos (animação esqueletal). Fica registrado para
não ser confundido com estádio.

---

## 3. Por que isso é um projeto separado, e não uma fase

| Motivo | Detalhe |
|---|---|
| **Dependência nova** | O app não desenha nada hoje. O único `OnPaint` do legado desenha o ícone minimizado. Um visualizador 3D traz OpenGL para o repositório — confinado a um alvo próprio, §4a. |
| **Paradigma de UI novo** | Câmera orbital, seleção de peça, wireframe/sólido/texturizado. Não é formulário de campos. |
| **Sem oráculo, e agora sem nem UI de referência** | O `ed.exe` não tem estádio. A ferramenta do CARP é WinForms sem render 3D — ela lista peças, não mostra. Não dá para comparar telas. |
| **Risco alto de corromper** | Ponteiro absoluto errado = travamento em campo, e o erro só aparece depois de carregar a partida. |
| **Escopo elástico** | "Importar malha do Blender" é um subprojeto inteiro (quantização, limites do GTE, atribuição de textura). Precisa de fronteira explícita. |

---

## 4. Decisões estruturais

A **(a)** está decidida. **(b)**, **(c)** e **(d)** ficam em aberto até S1 dar
os dados.

### (a) Onde o código mora → **duas bibliotecas novas, nenhuma delas o core** — decidido

Nada de estádio entra em `we2002_core`, e nada de OpenGL entra numa biblioteca
que não seja a de render. Quatro alvos, com a seta de dependência apontando num
sentido só:

```
src/core/      we2002_core       INALTERADO — é o que o golden test julga
src/assets/    we2002_assets     PLAN-FEATURES — Iso9660, Lzss, BinArchive, Tim, Ecc
src/stadium/   we2002_stadium    NOVO — Tmd, GrdmArchive, GdcTextures.  C++ puro.
src/view3d/    we2002_view3d     NOVO — o widget de render.  Único alvo que linka GL.
src/app/       newWe2002         cola: aba de estádio, seleção de peça, comandos
```

| Alvo | Depende de | Proibido depender de |
|---|---|---|
| `we2002_stadium` | `we2002::assets` | **Qt, OpenGL**, `windows.h`, POSIX |
| `we2002_view3d` | `we2002::stadium`, Qt6::OpenGLWidgets | `newWe2002` (nada de `MainWindow`) |
| `newWe2002` | tudo acima | — |

Por que quatro e não "põe tudo no app":

- **O parser fica testável headless.** `we2002_stadium` sem Qt e sem GL roda no
  mesmo regime dos 61 checks atuais, em máquina sem display. O fuzz da §6.3
  linka só ele — alvo pequeno, rápido, sem Qt no processo, o que importa quando
  se roda sob ASan pelo `tools/run-sanitized.sh`.
- **O OpenGL fica confinado.** `we2002_view3d` é o único ponto do repositório
  que precisa de GL. Isso mantém a Fase 7 (Windows) e o CI headless livres da
  dependência, e permite `-DWE2002_VIEW3D=OFF` — que dá extrator, exportador e
  troca de peça **sem render nenhum**, exatamente o caminho de fallback da §8
  se a S3 não ceder.
- **O core não cresce.** Mesmo argumento do PLAN-FEATURES §4: `we2002_core` não
  linka nenhuma das outras, então geometria de estádio não tem como aparecer no
  caminho do `Database::Save` nem por acidente.

Opções de build: `WE2002_STADIUM` (padrão `ON`) e `WE2002_VIEW3D` (padrão `ON`
se Qt6 e GL forem achados; `OFF` desliga só o render). Alvo de teste próprio,
`we2002_stadium_tests`, com nome separado no ctest — os 61 checks do core
continuam sendo 61.

### (b) Motor de render

`QOpenGLWidget` cru com shader mínimo, ou `Qt3D`? Recomendação:
**`QOpenGLWidget`**. O Qt3D é um módulo grande, meio abandonado no Qt6 e traria
peso de empacotamento; o que precisamos é desenhar triângulo e quad texturizado
com câmera orbital — algumas centenas de linhas de GL moderno. Vive dentro de
`we2002_view3d` e em nenhum outro lugar.

### (c) Fronteira do editor

Três níveis, custo crescente:

| Nível | O que permite | Risco |
|---|---|---|
| **1 — trocar peça** | pegar peça *i* do estádio X e pôr no lugar da peça *j* do estádio Y | baixo, é o que o CARP já faz |
| **2 — editar textura** | repintar a textura do estádio, geometria intacta | médio, depende de S3 |
| **3 — importar malha** | OBJ/glTF → TMD | **alto** |

Recomendação: **entregar 1 e 2, e tratar 3 como fase final opcional**, cortável
sem perda. Nível 1 sozinho já é o que a comunidade usa hoje, com a vantagem de
ver o resultado antes de gravar.

**(d) Peças fixas.** A tabela `tMDsFijos` do CARP entra como dado, e a
troca de peça fixa é **bloqueada por padrão**, com override explícito
("sei o que estou fazendo") que registra aviso. Motivo: a tabela é empírica; se
alguém achar que ela está errada num caso, tem que poder testar — mas não por
acidente.

---

## 5. Fases

Numeradas `S1..S7` para não colidir com as fases 7–14 dos outros planos. Cada
uma fecha com `ctest` verde, incluindo `golden` e `golden_gui` — que continuam
não sabendo que estádio existe, e é assim que tem que ser.

### S1 — Mapa do formato (read-only, sem UI)

Parser TMD em `src/core/Tmd.cpp`: cabeçalho, tabela de objetos, primitivas
(os ~20 tipos do SDK: tri/quad × plano/gouraud × textura/cor), vértices,
normais. Parser da tabela de ponteiros de `GRDM_*`. Ferramenta
`we2002_tmd info|dump`.

Resolver **os dois pontos de incerteza da §2.2**: o que os 15 ponteiros de
`GRDM_A` apontam de fato, e como o endereço-base é determinado.

*Aceite:* relatório completo dos 17 estádios — por peça: nº de vértices,
normais, primitivas, e histograma de tipo de primitiva. Zero peça com tipo
desconhecido. A soma dos tamanhos das peças mais a tabela **reproduz o tamanho
do arquivo exatamente**, nos 17. Sem isso, o resto está construído em cima de
palpite.

*Risco:* médio. O TMD é documentado; a tabela de ponteiros não.

### S2 — Exportação para formato aberto

TMD → OBJ (+MTL) e/ou glTF, com UV e índice de TPage/CLUT preservados por
face. Permite abrir estádio no Blender **antes** de existir visualizador nosso —
é o caminho mais curto para ver se S1 está certo.

*Aceite:* os 17 estádios abrem no Blender com geometria plausível (gramado
plano, arquibancadas em volta, sem face invertida em massa). Verificação visual,
assumidamente subjetiva — S1 é quem dá o rigor.

*Risco:* baixo.

### S3 — Texturas (`GDC_*`)

Engenharia reversa do codec conforme §2.3, extração das 5 seções, decodificação
para PNG, e ligação com os índices de TPage/CLUT que as primitivas do TMD
carregam.

*Aceite:* texturas de um estádio extraídas e aplicadas ao OBJ da S2 batem
visualmente com um print do jogo rodando no RetroArch.

*Risco:* **o mais alto do plano.** Se o codec não ceder, S3 é adiável: S4 e S5
funcionam com render sem textura, e o nível 2 da §4c cai fora.

### S4 — Visualizador 3D no app

`we2002_view3d`: `QOpenGLWidget` com câmera orbital, wireframe/sólido/texturizado, seleção de
peça por clique, lista de peças lateral marcando as fixas.

*Aceite:* abrir os 17 estádios, orbitar, selecionar peça e ver o índice bater
com o do relatório da S1. Nada é gravado nesta fase.

*Risco:* médio, quase todo de UI.

### S5 — Montagem por peças (nível 1)

Trocar peça entre estádios, reconstruir o `GRDM_*` inteiro, recalcular a tabela
de ponteiros, gravar com a política fit-or-fail e o ECC da Fase 11.

*Aceite:* remontar um estádio **sem trocar nada** devolve o arquivo byte a byte
idêntico — mesma invariante do PLAN-FEATURES §5c, e o único teste automático
forte que esta fase tem. Trocar uma peça não-fixa e carregar partida no
emulador sem travar. Trocar uma peça fixa exige o override.

*Risco:* alto. Primeira gravação de estádio.

### S6 — Editor de textura do estádio (nível 2)

Só se S3 fechar. Reaproveita o navegador de assets da Fase 12: exporta PNG,
reimporta, recomprime, fit-or-fail.

*Aceite:* trocar a cor da arquibancada e ver no emulador.

*Risco:* médio, herdado de S3.

### S7 — Importação de malha (nível 3) — **opcional**

OBJ/glTF → TMD: triangulação, quantização para inteiro de 16 bits, geração de
normais, atribuição de TPage/CLUT, e respeito aos limites práticos do GTE
(contagem de primitiva por peça compatível com o orçamento do frame original).

*Aceite:* malha simples autoral, dentro do orçamento de vértices da peça
substituída, carrega e renderiza no emulador sem queda de framerate visível.

*Risco:* alto e **elástico**. Cortável sem prejudicar S1–S6.

---

## 6. Estratégia de teste

O golden test não alcança nada disto. O que substitui:

1. **Conservação de bytes** — desmontar e remontar sem editar devolve o arquivo
   idêntico. Vale para `GRDM_*` (S5) e `GDC_*` (S6).
2. **Invariantes estruturais** — soma das peças + tabela == tamanho do arquivo;
   todo `prim_top`/`vert_top` dentro da peça; todo índice de vértice de
   primitiva `< n_vert`; toda peça referenciada exatamente uma vez pela tabela.
3. **Fuzz de robustez** — o parser recebe arquivo truncado e lixo aleatório e
   **recusa**, sem estourar buffer. Isso vale para ASan (`tools/run-sanitized.sh`,
   por causa da Citrix) e é obrigatório: parser binário de dado de terceiro é
   onde bug de memória mora.
4. **Boot no emulador** — RetroArch com core PSX, uma vez por fase que grava,
   carregando partida **no estádio alterado** (não basta o jogo iniciar).
5. **Não-regressão** — `golden` e `golden_gui` verdes em todas as sete fases.

---

## 7. Crédito

Além do que o PLAN-FEATURES §9 já obriga, este plano acrescenta ao
[NOTICE.md](../NOTICE.md):

- **Maximiliano Ducoli (CARP)** — `WE_TMD_Tools`, e em especial a tabela
  `tMDsFijos` de peças fixas por estádio, usada como dado de partida. Condição
  declarada por ele: uso não comercial, com citação.
- **TMD** é formato do SDK oficial da PlayStation, documentado publicamente há
  décadas. Reimplementar o parser não deriva de código do CARP.

---

## 8. Ordem e critério de parada

S1 → S2 são obrigatórias e baratas: entregam extrator e exportador, e já dão
valor real (abrir estádio do WE2002 no Blender). S3 é o pivô: se o codec ceder,
o plano vai até S6; se não ceder, S4 e S5 entregam visualizador e troca de peça
sem textura, que ainda é mais do que existe hoje em qualquer ferramenta.

S7 só se alguém pedir, e depois de S5 estar rodando há tempo suficiente para se
confiar nele.
