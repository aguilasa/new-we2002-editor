# Offsets medidos contra o `wte.exe` em execução — WTE-TASK-19

**GERADO por `wte/tools/analisar_io.py` — não editar à mão.**
Evidência: [`io-medido.tsv`](io-medido.tsv), produzido por
[`../tools/diff_dirigido.sh`](../tools/diff_dirigido.sh).
Regenerar: `python3 wte/tools/analisar_io.py`.

O irmão estático é [`offsets.md`](offsets.md), que lê o `.exe` parado.
Aqui o `.exe` **roda**, e o que se mede é a syscall.

---

## O método, e por que não é `cmp`

O enunciado da task pede diff dirigido: editar um campo, gravar, `cmp`.
Isso enxerga **escrita de valor diferente**, e só. O editor do Obocaman
grava, na maior parte das áreas, exatamente o que leu — ali o `cmp` sai
limpo e não distingue *não gravou* de *gravou igual*, que levam a
conclusões opostas sobre o que o app Lazarus precisa endereçar. E `cmp`
não vê **leitura** nenhuma, que é a metade da resposta que diz onde os
50 `OFS_*` ausentes moram.

Então a régua é `strace` sobre o processo Wine, e o `cmp` fica como
segunda régua independente: toda faixa que mudou no arquivo tem de estar
contida numa faixa de escrita do trace.

### As duas réguas, sessão a sessão

A conferência roda no fim de cada corrida (`analisar_io.py --conferir`),
e é ela que pegou os três defeitos de instrumento das passagens
anteriores. O resultado dela morria no diretório da sessão, em `/tmp`:
das cinco primeiras corridas, uma só teve o número registrado, em prosa
([CORR-WTE-047](../../docs/tasks/CORR-WTE-047.md)). Agora o `cmp.tsv` de
cada sessão é fundido em [`cmp-medido.tsv`](cmp-medido.tsv), e a linha
abaixo é derivada dele — como o resto deste arquivo.

| sessão | faixas do `cmp` | contidas nas escritas do trace | faixas de escrita |
|---|---:|---:|---:|
| `06-diff-dirigido` | 7 | 7 | 8 |
| `06-truncada` | 7 | 7 | 8 |
| `09-areas-com-time` | 19 | 19 | 31 |
| `10-telas-que-faltavam` | 9 | 9 | 10 |
| `11-varredura-de-times` | 9 | 9 | 9 |
| `27-gravacao-controle` | 12 | 12 | 18 |
| `27-descarga-sem` | 9 | 9 | 9 |
| `27-descarga-com` | 9 | 9 | 10 |
| `27-barras-editada` | 10 | 10 | 10 |
| `27-nomes-editados` | 19 | 19 | 19 |
| `27-textura` | 36 | 36 | 29 |
| `27-mcr` | 9 | 9 | 9 |
| `27-dorsal-editado` | 10 | 10 | 10 |
| `27-mover` | 11 | 11 | 12 |
| `27-mover-ml` | 10 | 10 | 10 |
| `27-descarte-ml` | 13 | 13 | 13 |

**As duas réguas fecham nas 16 sessões que escreveram.**
Faixa do `cmp` que sobrasse significaria syscall perdida pelo
trace, e nenhum número desta task valeria nada — é literalmente o
que já aconteceu duas vezes, e as duas foram descobertas aqui.

O contrário — faixa de escrita do trace sem par no `cmp` — **não é
erro**: é o editor gravando de volta exatamente o que leu, que é o
comportamento que motivou trocar o `cmp` pelo `strace` como régua
principal.

### Um terceiro caminho que foi tentado e **derruba o app**

Encher a cópia com um padrão (`0xA5`) depois do Load e ver o que
sobrevive à gravação. A ideia era mapear escrita sem depender de valor.
**Não funciona:** o `wte.exe` não lê tudo no Load — ele lê sob demanda,
e uma imagem de 474 MB cheia de `0xA5` o mata no primeiro clique, com a
janela sobrevivendo ao processo. Medido, e registrado aqui para que
ninguém repita.

---

## O diff de controle vem primeiro

**Abrir a imagem, sem tocar em nada, já grava 14337 bytes em 8 faixa(s).**
Não é o `Load`+`Save` não idempotente do `ed.exe`: aqui não há `Save`
nenhum — o `wte.exe` escreve durante a **carga**, antes de a janela
principal aparecer e sem clique de usuário.

| faixa | tamanho | setor | byte no setor |
|---|---:|---:|---:|
| 11784..13831 | 2048 | 5 | 24 |
| 14136..16183 | 2048 | 6 | 24 |
| 16488..18535 | 2048 | 7 | 24 |
| 18840..20887 | 2048 | 8 | 24 |
| 21192..23239 | 2048 | 9 | 24 |
| 23544..25591 | 2048 | 10 | 24 |
| 25896..27943 | 2048 | 11 | 24 |
| 1921862..1921862 | 1 | 817 | 278 |

Sete das oito faixas são contíguas em setor: `11784`..`27943`, setores 5 a 11, sempre do byte 24 ao 2071 —
a região de dados de usuário inteira de cada setor. Estão **abaixo**
do menor offset que este repositório conhece (`387792`), então nenhuma toca dado de time ou
de jogador.

A oitava é de **1 byte** em `1921862` (setor 817, byte 278). Nenhum `OFS_*` cai nela; o mais
próximo é `OFS_FLAG_SHAPE_COPY_1` = `1929004`, a 7142 bytes. Um byte solto, gravado na carga
e sem nome — é candidato a offset novo, e está na tabela de
faixas órfãs abaixo.

**Consequência para toda medição desta task:** essa faixa é ruído de
fundo e sai da conta. Sem o controle, ela apareceria em cada corrida e
pareceria efeito da edição.

---

## O que a sessão mediu

| ação | faixas de leitura | bytes lidos | faixas de escrita | bytes escritos |
|---|---:|---:|---:|---:|
| `ARRANQUE` | 5 | 4971 | 8 | 14337 |
| `GRAVA_BARRAS` | 0 | 0 | 0 | 0 |
| `IGUALA_NOMES` | 0 | 0 | 0 | 0 |
| `GRAVA_NOMES` | 0 | 0 | 0 | 0 |
| `PINTAR` | 0 | 0 | 0 | 0 |
| `GRAVA_CAMISETA` | 0 | 0 | 0 | 0 |
| `GRAVA_MEMORY` | 0 | 0 | 0 | 0 |
| `ABRE_JOGADOR` | 0 | 0 | 0 | 0 |
| `TIME_TITULAR` | 0 | 0 | 0 | 0 |
| `SELECIONA_TIME` | 16 | 18542 | 0 | 0 |
| `FIM` | 0 | 0 | 0 | 0 |

**9 das 11 ações não tocaram a imagem em byte nenhum:** `GRAVA_BARRAS`, `IGUALA_NOMES`, `GRAVA_NOMES`, `PINTAR`, `GRAVA_CAMISETA`, `GRAVA_MEMORY`, `ABRE_JOGADOR`, `TIME_TITULAR`, `FIM`.

Isso é medida, e não ausência de medida: os cliques **chegam** ao
app — o mesmo roteiro reabre o splash `Sobre...` por clique, com a
janela mapeando —, e mesmo assim os botões de gravação por área não
escrevem byte nenhum enquanto não houver time selecionado.

---

## Os `OFS_*` que a execução confirmou — 28

Confirmado aqui quer dizer: **o `wte.exe` endereçou este ponto da
imagem**. É afirmação de posição, não de semântica — a leitura vem em
bloco de 512 ou 2048 bytes, e o que a faixa prova é que o app vai ali.

A coluna "WTE-TASK-06" diz o que a análise **estática** tinha dito do
mesmo offset. `ausente` virando confirmado é o resultado que esta task
existe para produzir.

| `Offsets.hpp` | valor | WTE-TASK-06 | ação | op | faixa |
|---|---:|---|---|---|---|
| `OFS_PLAYER_NAME` | 387792 | ausente (H2) | `SELECIONA_TIME` | R | 387792..388827 |
| `OFS_SQUAD_NUMBERS_NATIONAL` | 404716 | ausente (H2) | `SELECIONA_TIME` | R | 404716..405227 |
| `OFS_TEAM_NAME_1` | 1012640 | confirmado | `SELECIONA_TIME` | R | 1012641..1013664 |
| `OFS_TEAM_NAME_1_END` | 1013431 | ausente (H1) | `SELECIONA_TIME` | R | 1012641..1013664 |
| `OFS_TEAM_NAME_1_A` | 1013736 | ausente (H1) | `SELECIONA_TIME` | R | 1013736..1014447 |
| `OFS_TEAM_NAME_2` | 1881968 | confirmado | `SELECIONA_TIME` | R | 1881969..1883407 |
| `OFS_TEAM_NAME_KANJI` | 2002316 | confirmado | `ARRANQUE` | R | 2002316..2004047 |
| `OFS_TEAM_NAME_KANJI_A` | 2003928 | ausente (H1) | `ARRANQUE` | R | 2002316..2004047 |
| `OFS_TEAM_NAME_3` | 2003996 | confirmado | `ARRANQUE` | R | 2002316..2004047 |
| `OFS_TEAM_ABBREV_1` | 2004996 | confirmado | `SELECIONA_TIME` | R | 2002317..2005883 |
| `OFS_FLAG_SHAPE_COPY_2` | 2005412 | confirmado | `SELECIONA_TIME` | R | 2002317..2005883 |
| `OFS_LINK_ML` | 2012680 | confirmado | `ARRANQUE` | R | 2012680..2014871 |
| `OFS_LINK_ML1` | 2012728 | ausente (H1) | `ARRANQUE` | R | 2012680..2014871 |
| `OFS_LINK_ML2` | 2013336 | ausente (H1) | `ARRANQUE` | R | 2012680..2014871 |
| `OFS_SQUAD_NUMBERS_ML` | 2014504 | ausente (H1) | `ARRANQUE` | R | 2012680..2014871 |
| `OFS_ML_TEAM_NAME_7` | 2028267 | confirmado | `SELECIONA_TIME` | R | 2028268..2029535 |
| `OFS_FLAG_SHAPE_COPY_3` | 2328060 | confirmado | `SELECIONA_TIME` | R | 2328060..2328695 |
| `OFS_TEAM_BARS` | 2328184 | ausente (H1) | `SELECIONA_TIME` | R | 2328060..2328695 |
| `OFS_TEAM_BARS_A` | 2328504 | ausente (H1) | `SELECIONA_TIME` | R | 2328060..2328695 |
| `OFS_KIT_PREVIEW` | 2667256 | ausente (H3) | `SELECIONA_TIME` | R | 2667258..2667801 |
| `OFS_TEAM_NAME_4` | 2830160 | confirmado | `SELECIONA_TIME` | R | 2830161..2831451 |
| `OFS_TEAM_ABBREV_3` | 4234484 | confirmado | `SELECIONA_TIME` | R | 4234485..4235371 |
| `OFS_TEAM_MIXED_CASE_NAME` | 4598596 | confirmado | `SELECIONA_TIME` | R | 4598597..4599927 |
| `OFS_TEAM_ABBREV_2` | 5651068 | confirmado | `SELECIONA_TIME` | R | 5651069..5653155 |
| `OFS_TEAM_NAME_6` | 5651448 | confirmado | `SELECIONA_TIME` | R | 5651069..5653155 |
| `OFS_TEAM_NAME_6_A` | 5651880 | ausente (H1) | `SELECIONA_TIME` | R | 5651069..5653155 |
| `OFS_TEAM_NAME_6_B` | 5652364 | ausente (H1) | `SELECIONA_TIME` | R | 5651069..5653155 |
| `OFS_FLAG_COLOURS` | 12549518 | ausente (H3) | `SELECIONA_TIME` | R | 12549518..12550029 |

**14 dos 50 `ausente`** da WTE-TASK-06 passaram a
`confirmado` por execução. Os demais continuam sem evidência dinâmica —
não porque o `wte.exe` não os alcance, mas porque a sessão medida não
exercitou a tela que os toca.

---

## Faixas que nenhum `OFS_*` explica — 13

Região que o `wte.exe` endereça e que o `Offsets.hpp` do `newWe2002`
não nomeia. É a lista que o app Lazarus vai precisar, e que este
repositório ainda não tem.

| ação | op | faixa | tamanho | setor | candidato da WTE-TASK-06 |
|---|---|---|---:|---:|---|
| `ARRANQUE` | R | 0..22 | 23 | 0 | — |
| `ARRANQUE` | R | 11796..12307 | 512 | 5 | — |
| `ARRANQUE` | R | 2736694..2737205 | 512 | 1163 | `2736690`, `2736694` |
| `ARRANQUE` | W | 11784..13831 | 2048 | 5 | — |
| `ARRANQUE` | W | 14136..16183 | 2048 | 6 | — |
| `ARRANQUE` | W | 16488..18535 | 2048 | 7 | — |
| `ARRANQUE` | W | 18840..20887 | 2048 | 8 | — |
| `ARRANQUE` | W | 21192..23239 | 2048 | 9 | — |
| `ARRANQUE` | W | 23544..25591 | 2048 | 10 | — |
| `ARRANQUE` | W | 25896..27943 | 2048 | 11 | — |
| `ARRANQUE` | W | 1921862..1921862 | 1 | 817 | `1921862` |
| `SELECIONA_TIME` | R | 12543596..12544779 | 1184 | 5333 | `12544268` |
| `SELECIONA_TIME` | R | 14368636..14369147 | 512 | 6109 | — |

### Fora da janela que o `newWe2002` conhece

O maior offset do `Offsets.hpp` é `12552648`.
As faixas abaixo estão **acima** dele — território que este
repositório nunca precisou endereçar, e o aviso que a
[`offsets.md`](offsets.md) escreveu se cumpre: a faixa do filtro
estático deriva do nosso próprio `Offsets.hpp`, então offset novo
aqui **alarga a janela** e obriga a reconferir o limite das duas
tabelas.

| ação | op | faixa | tamanho | setor | byte no setor |
|---|---|---|---:|---:|---:|
| `SELECIONA_TIME` | R | 14368636..14369147 | 512 | 6109 | 268 |

---

## O limite duro desta medição: o `wte.exe` morre ao carregar um time

Medido, e por três passagens foi o que impedia esta task de andar — a
CORR-WTE-044 desfez o bloqueio e as sessões seguintes mediram por cima
dele. Fica escrito porque explica o desenho de tudo o que veio depois.
Com a ROM **europeia**, o `wte.exe` **encerra com falha de segmentação
logo depois** de ler os dados do primeiro time selecionado:

```
--- SIGSEGV {si_signo=SIGSEGV, si_code=SEGV_MAPERR, si_addr=NULL} ---
```

A janela sobrevive ao processo — o `wineserver` a mantém mapeada —, e é
por isso que o sintoma se disfarça de *clique parou de funcionar*.
Foram gastos dois diagnósticos até separar as duas coisas; quem repetir
a medição confira `ps -o stat` procurando `Z`, e não a tela.

### A hipótese do tamanho foi testada, e está **refutada**

O editor avisa na abertura que o tamanho não corresponde: ele quer
**474.431.328** bytes exatos, e as ROMs daqui têm 474.784.128 (European
Deluxe) e 307.187.664 (japonesa). A diferença da primeira é
**352.800 bytes = exatamente 150 setores** de 2352, e toda ela está na
cauda, muito depois do maior offset conhecido.

Então a cópia foi truncada para o tamanho exato (`truncada-474431328.bin`) e a
sessão rodou de novo, mesmo roteiro, uma variável trocada. Resultado:

- o aviso de tamanho **some** — o corte é o que ele queria;
- o mapa de I/O sai **idêntico faixa a faixa**, leitura e escrita;
- **o `wte.exe` cai igual**, no mesmo ponto.

Tamanho não é a causa. O que a hipótese explicava era o aviso, e o
aviso nunca foi o problema.

### E a região vazia é pista, não causa

A causa foi medida depois, e está em [`crash.md`](crash.md): a
violação de acesso cai dentro do `vcl60.bpl`, em
`Graphics::TFont::SetSize`, com o `this` **nulo** — chamada por uma
rotina do `.exe` que procura um controle pelo nome. **A falha é de
estado de interface, não de leitura da imagem.** O que esta seção mede
continua valendo como pista da *causa da causa*, e não como a causa.

A última leitura antes do `SIGSEGV` são 512 bytes em
`14368636` — 1,8 MB **acima** do maior offset que o `newWe2002`
conhece. Amostrando os primeiros 64 bytes
dessa faixa na imagem: **4 não são zero**.

Para comparar: das outras 19 faixas lidas, a mais
vazia tem 32 bytes não-zero na mesma amostra. A região que
o editor lê por último, e logo antes de morrer, é a única
praticamente zerada.

Isso não prova a causa — prova que **nesta release não há o que ler**
onde o editor foi ler. Medida em [`io-conteudo.tsv`](io-conteudo.tsv).

**O pedido, então, deixou de ser "a release de 474.431.328 bytes":**
truncar a que temos não serve.

**E deixou de ser pedido.** A CORR-WTE-044 mediu a causa e ela não é
esta: o ponteiro que a rotina de realce usa é sobrescrito pela carga do
time, o controle procurado **existe**, e a mesma faixa em `14368636` é
lida pelas **duas** imagens do repositório — só uma trava. Com
`roms/japanese-shift-jis.bin` o `wte.exe` passa da troca de time com
zero violação de acesso. Ver [`crash-causa.md`](crash-causa.md).

### O que isso custa, e a quem

| Alcançado | Bloqueado |
|---|---|
| arranque e carga inicial | os seis grupos de campo da WTE-TASK-19 |
| seleção de time (uma vez) | qualquer gravação por área |
| o diff de controle | o diff dirigido *stricto sensu* — editar um campo e gravar |

**A coluna `Bloqueado` vale para a imagem que esta medição usou, a
europeia.** O `wte.exe` é o **oráculo comportamental** do projeto (§4.2
do plano), e a
[WTE-TASK-22](../../docs/tasks/22-harness-golden.md) monta o gate golden
em cima dele; com `roms/japanese-shift-jis.bin` ele passa da troca de
time, então o gate tem em que se apoiar. A seção seguinte é a medição
que isso destravou.

---

## As seis áreas, com um time carregado

Medido com o roteiro
[`09-areas-com-time.txt`](../tests/roteiros/09-areas-com-time.txt) sobre
cópia de `roms/japanese-shift-jis.bin`.
**A imagem não é escolha de gosto:** com a
europeia o `wte.exe` morre na troca de time, e o roteiro mediria o
travamento em vez das áreas ([`crash-causa.md`](crash-causa.md)).

O `ARRANQUE` desta sessão é o **diff de controle desta imagem** — abrir
sem tocar em nada —, e ele vem antes de toda ação medida abaixo, como
manda o método da task.

| ação | área da task | leituras | escritas | bytes escritos |
|---|---|---:|---:|---:|
| `ARRANQUE` | — | 5 | 9 | 14339 |
| `SELECIONA_TIME` | carga do time — o pre-requisito de todas as outras | 17 | 0 | 0 |
| `GRAVA_BARRAS` | barras de atributo do time (`boton_barras2iso`) | 0 | 0 | 0 |
| `IGUALA_NOMES` | nomes, sem gravar (`iguala_nombres`) | 0 | 0 | 0 |
| `GRAVA_NOMES` | nomes do time (`boton_nombres2iso`) | 0 | 8 | 57 |
| `PINTAR` | bandeira e cor de radar (`colorear` → `ficha_color`) | 0 | 11 | 385 |
| `TIME_TITULAR` | lado titular e o contador de blocos de ML livres | 0 | 0 | 0 |
| `CALCULA_PRECO` | preço derivado dos atributos (`etiqprecio`) | 3 | 2 | 24 |
| `ABRE_JOGADOR` | ficha do jogador — cabelo, barba, `careto` | 4 | 1 | 1 |
| `FIM` | — | 0 | 0 | 0 |

Depois do arranque, as ações tocaram **46 faixas** —
22 de escrita. Os `OFS_*` do `newWe2002` alcançados por
esta sessão são **33**.

**4 ação(ões) não tocou(aram) a imagem**: `GRAVA_BARRAS`, `IGUALA_NOMES`, `TIME_TITULAR`, `FIM`. Isso é resultado, não
falha de clique — o roteiro é dirigido por janela, e cada uma delas
foi resolvida pelo nome antes do clique.

**27 faixas desta sessão nenhum `OFS_*` explica**, e
2 delas ficam acima do maior offset que o
`newWe2002` conhece. São elas que a fase 4 precisa nomear.

| ação | op | início | fim | tamanho | setor |
|---|:---:|---:|---:|---:|---:|
| `ARRANQUE` | R | 0 | 22 | 23 | 0 |
| `ARRANQUE` | R | 11796 | 12307 | 512 | 5 |
| `ARRANQUE` | R | 2736694 | 2737205 | 512 | 1163 |
| `ARRANQUE` | W | 11784 | 13831 | 2048 | 5 |
| `ARRANQUE` | W | 14136 | 16183 | 2048 | 6 |
| `ARRANQUE` | W | 16488 | 18535 | 2048 | 7 |
| `ARRANQUE` | W | 18840 | 20887 | 2048 | 8 |
| `ARRANQUE` | W | 21192 | 23239 | 2048 | 9 |
| `ARRANQUE` | W | 23544 | 25591 | 2048 | 10 |
| `ARRANQUE` | W | 25896 | 27943 | 2048 | 11 |
| `ARRANQUE` | W | 1921862 | 1921862 | 1 | 817 |
| `ARRANQUE` | W | 2012984 | 2012985 | 2 | 855 |
| `SELECIONA_TIME` | R | 12543596 | 12544779 | 1184 | 5333 |
| `SELECIONA_TIME` | R | 14368636 | 14369147 | 512 | 6109 |
| `GRAVA_NOMES` | W | 1013936 | 1013943 | 8 | 431 |
| `GRAVA_NOMES` | W | 1882896 | 1882907 | 12 | 800 |
| `GRAVA_NOMES` | W | 2004988 | 2004995 | 8 | 852 |
| `GRAVA_NOMES` | W | 2005372 | 2005375 | 4 | 852 |
| `GRAVA_NOMES` | W | 2830940 | 2830947 | 8 | 1203 |
| `GRAVA_NOMES` | W | 4234860 | 4234863 | 4 | 1800 |
| `GRAVA_NOMES` | W | 5652644 | 5652651 | 8 | 2403 |
| `PINTAR` | W | 2667290 | 2667319 | 30 | 1134 |
| `PINTAR` | W | 5651444 | 5651447 | 4 | 2402 |
| `PINTAR` | W | 12543596 | 12543851 | 256 | 5333 |
| `PINTAR` | W | 12544268 | 12544297 | 30 | 5333 |
| `CALCULA_PRECO` | W | 14368636 | 14368637 | 2 | 6109 |
| `ABRE_JOGADOR` | W | 3067426 | 3067426 | 1 | 1304 |

---

## A 5ª passagem: o que faltava era tela, e o que faltava era índice

Depois da 4ª passagem sobravam 35 dos 50 `OFS_*` sem veredito dinâmico,
e eles não faltavam pelo mesmo motivo. Daí duas sessões, não uma:

- [`10-telas-que-faltavam.txt`](../tests/roteiros/10-telas-que-faltavam.txt) — a estratégia, a ficha
  do jogador, o dorsal, o outro lado da janela, a extração do uniforme
  e o diálogo de textura, que nenhum roteiro tinha aberto;
- [`11-varredura-de-times.txt`](../tests/roteiros/11-varredura-de-times.txt) — os times 60, 120 e 180
  da lista. `OFS_PLAYER_NAME_5..8` e os `OFS_ML_*` são blocos com passo
  de setor: tela nova nenhuma os alcança, e descer na lista alcança.

As duas sobre cópia de `roms/japanese-shift-jis.bin`, pela mesma razão
da 4ª passagem, e as duas com o `ARRANQUE` — o diff de controle — antes
de qualquer ação medida.

| sessão | ação | o que foi exercitado | leituras | escritas | bytes lidos |
|---|---|---|---:|---:|---:|
| `10` | `ARRANQUE` | — | 5 | 9 | 5415 |
| `10` | `SELECIONA_TIME` | — | 17 | 0 | 18467 |
| `10` | `ESTRATEGIA` | formação e posições em campo (`mostrar_estrategia_1`) | 4 | 0 | 2324 |
| `10` | `FICHA_JOGADOR` | ficha do jogador (`mostrar_jugador_1`) | 4 | 0 | 2360 |
| `10` | `DORSAL` | número da camisa (`dorsal1` → `ficha_dorsal`) | 1 | 0 | 512 |
| `10` | `TIME_FUNDO` | time 30 da lista | 15 | 1 | 29138 |
| `10` | `JOGADOR_FUNDO` | jogador 15 da lista | 17 | 0 | 17150 |
| `10` | `FICHA_FUNDO` | ficha desse jogador | 4 | 0 | 2048 |
| `10` | `TIME_2` | o time do lado direito (`lista_equipos_2`) | 3 | 0 | 3144 |
| `10` | `FICHA_2` | ficha de um jogador desse time | 4 | 0 | 2048 |
| `10` | `EXTRAI_UNI` | extrair o uniforme para arquivo (`grabar_camiseta`) | 16 | 0 | 31232 |
| `10` | `ABRE_TEX` | abrir o diálogo de textura (`boton_dialogo_tex`) | 0 | 0 | 0 |
| `10` | `FIM` | — | 0 | 0 | 0 |
| `11` | `ARRANQUE` | — | 5 | 9 | 5415 |
| `11` | `TIME_60` | time 60 da lista | 15 | 0 | 31367 |
| `11` | `FICHA_60` | ficha de um jogador dele | 23 | 0 | 29774 |
| `11` | `TIME_120` | time 120 | 25 | 0 | 43010 |
| `11` | `FICHA_120` | ficha de um jogador dele | 6 | 0 | 3292 |
| `11` | `TIME_180` | time 180 | 17 | 0 | 11280 |
| `11` | `ESTRATEGIA_180` | formação desse time | 3 | 0 | 1556 |
| `11` | `FICHA_180` | ficha de um jogador dele | 6 | 0 | 3292 |
| `11` | `TIME_2_FUNDO` | time 60 do lado direito | 5 | 0 | 20633 |
| `11` | `FICHA_2_FUNDO` | ficha de um jogador dele | 10 | 0 | 7284 |
| `11` | `FIM` | — | 0 | 0 | 0 |

**7 `OFS_*` saíram de hipótese nesta passagem** — nenhuma
sessão anterior os tinha endereçado:

| `Offsets.hpp` | valor | sessão | ação | op |
|---|---:|---|---|:---:|
| `OFS_ML_PLAYER_NAME_2` | 2008632 | `11` | `TIME_120` | R |
| `OFS_ML_PLAYER_NAME_3` | 2010984 | `11` | `TIME_120` | R |
| `OFS_FORMATIONS` | 2303700 | `10` | `ESTRATEGIA` | R |
| `OFS_KIT_PREVIEW_A` | 2669544 | `10` | `TIME_FUNDO` | R |
| `OFS_KIT_PREVIEW_B` | 2671896 | `11` | `TIME_120` | R |
| `OFS_KIT_PREVIEW_C` | 2674248 | `11` | `TIME_120` | R |
| `OFS_FLAG_COLOURS_B` | 12552648 | `11` | `TIME_120` | R |

### O achado grande: a região do uniforme

Extrair a camisa para arquivo lê **16 faixas contíguas**,
de `21168024` a `21203815` — 35792 bytes, setores 9000 a 9015.
O maior offset que o `Offsets.hpp` conhece é `12552648`: esta região
está **8 MB acima** dele, e o
`newWe2002` nunca precisou nomeá-la porque não desenha uniforme.

É a entrada da [WTE-TASK-29](../../docs/tasks/29-camisa-e-bandeira-2d.md), e é a maior região
nova que esta task achou.

---

## Os 50, um a um — o veredito de cada

O critério da WTE-TASK-19 é *resolver ou declarar irrelevante* cada um
dos 50 `OFS_*` que a WTE-TASK-06 marcou `ausente`. São três vereditos, e
dois deles vêm de régua diferente:

- **endereçado** — o `wte.exe` foi ali, medido por `strace`;
- **retomada de fronteira** — o offset não é endereço de campo: é o
  ponto onde o `Database.cpp` do `newWe2002` retoma a leitura de um
  registro que cai em cima da fronteira de setor, dentro de um
  `case N :` ou de um `if (i == N)` — o legado usa as duas formas para a
  mesma coisa, e a coluna **prova** diz qual delas casou, com a linha.
  Só o registro N o endereça, e o `wte.exe` só o
  endereçaria se o usuário escolhesse exatamente aquele jogador;
- **base de varredura** — o offset é a base de um lote que o legado
  desfila com um `for`. Só o primeiro registro do lote a endereça.

Os dois últimos saem do **fonte**, não da tela, e é isso que os torna
resposta: a ausência deles num trace é a previsão do papel que eles têm,
não buraco de cobertura. Quem varre é o Moriero; o Obocaman salta direto
para o registro que a tela mostra.

| `Offsets.hpp` | valor | veredito | prova |
|---|---:|---|---|
| `OFS_PLAYER_NAME` | 387792 | endereçado | `06`/`SELECIONA_TIME` R |
| `OFS_PLAYER_NAME_2` | 390456 | endereçado | `10`/`TIME_FUNDO` R |
| `OFS_PLAYER_NAME_3` | 392808 | endereçado | `10`/`TIME_FUNDO` R |
| `OFS_PLAYER_NAME_4` | 395160 | endereçado | `10`/`TIME_FUNDO` R |
| `OFS_PLAYER_NAME_5` | 397512 | endereçado | `11`/`FICHA_60` R |
| `OFS_PLAYER_NAME_6` | 399864 | endereçado | `11`/`FICHA_60` R |
| `OFS_PLAYER_NAME_7` | 402216 | endereçado | `11`/`FICHA_60` R |
| `OFS_PLAYER_NAME_8` | 404568 | endereçado | `11`/`TIME_120` R |
| `OFS_SQUAD_NUMBERS_NATIONAL` | 404716 | endereçado | `06`/`SELECIONA_TIME` R |
| `OFS_TEAM_NAME_1_END` | 1013431 | endereçado | `06`/`SELECIONA_TIME` R |
| `OFS_TEAM_NAME_1_A` | 1013736 | endereçado | `06`/`SELECIONA_TIME` R |
| `OFS_TEAM_NAME_KANJI_A` | 2003928 | endereçado | `06`/`ARRANQUE` R |
| `OFS_ML_PLAYER_NAME` | 2006288 | endereçado | `11`/`TIME_120` R |
| `OFS_ML_PLAYER_NAME_2` | 2008632 | endereçado | `11`/`TIME_120` R |
| `OFS_ML_PLAYER_NAME_3` | 2010984 | endereçado | `11`/`TIME_120` R |
| `OFS_LINK_ML1` | 2012728 | endereçado | `06`/`ARRANQUE` R |
| `OFS_LINK_ML2` | 2013336 | endereçado | `06`/`ARRANQUE` R |
| `OFS_SQUAD_NUMBERS_ML` | 2014504 | endereçado | `06`/`ARRANQUE` R |
| `OFS_PLAYER_ATTR` | 2179492 | endereçado | `09`/`CALCULA_PRECO` R |
| `OFS_PLAYER_ATTR_1` | 2180328 | retomada de fronteira | `case 44+PLAYERS_NC :` no `Database.cpp`, `Seek` em :639 |
| `OFS_PLAYER_ATTR_2` | 2182680 | retomada de fronteira | `case 215+PLAYERS_NC :` no `Database.cpp`, `Seek` em :645 |
| `OFS_PLAYER_ATTR_3` | 2185032 | retomada de fronteira | `case 385+PLAYERS_NC :` no `Database.cpp`, `Seek` em :650 |
| `OFS_PLAYER_ATTR_4` | 2187384 | retomada de fronteira | `case 556+PLAYERS_NC :` no `Database.cpp`, `Seek` em :657 |
| `OFS_PLAYER_ATTR_5` | 2189736 | retomada de fronteira | `case 727+PLAYERS_NC :` no `Database.cpp`, `Seek` em :663 |
| `OFS_PLAYER_ATTR_6` | 2192088 | retomada de fronteira | `case 897+PLAYERS_NC :` no `Database.cpp`, `Seek` em :668 |
| `OFS_PLAYER_ATTR_7` | 2194440 | retomada de fronteira | `case 1068+PLAYERS_NC :` no `Database.cpp`, `Seek` em :675 |
| `OFS_PLAYER_ATTR_8` | 2196792 | retomada de fronteira | `case 1239+PLAYERS_NC :` no `Database.cpp`, `Seek` em :681 |
| `OFS_PLAYER_ATTR_9` | 2199144 | retomada de fronteira | `case 1409+PLAYERS_NC :` no `Database.cpp`, `Seek` em :686 |
| `OFS_ML_PLAYER_ATTR` | 2204112 | base de varredura | `Seek` + `for` no `Database.cpp` |
| `OFS_ML_PLAYER_ATTR_1` | 2206200 | retomada de fronteira | `case 148 :` no `Database.cpp`, `Seek` em :707 |
| `OFS_ML_PLAYER_ATTR_2` | 2208552 | retomada de fronteira | `case 319 :` no `Database.cpp`, `Seek` em :714 |
| `OFS_FORMATIONS` | 2303700 | endereçado | `10`/`ESTRATEGIA` R |
| `OFS_FORMATIONS_A` | 2304984 | retomada de fronteira | `if(i == 32)` no `Database.cpp`, `Seek` em :381 |
| `OFS_TEAM_BARS` | 2328184 | endereçado | `06`/`SELECIONA_TIME` R |
| `OFS_TEAM_BARS_A` | 2328504 | endereçado | `06`/`SELECIONA_TIME` R |
| `OFS_KICKER` | 2329056 | endereçado | `10`/`ESTRATEGIA` R |
| `OFS_ML_TEAM_NAME_8` | 2476048 | base de varredura | `Seek` + `for` no `Database.cpp` |
| `OFS_ML_TEAM_NAME_8_A` | 2476680 | retomada de fronteira | `if(i == 30)` no `Database.cpp`, `Seek` em :301 |
| `OFS_KIT_PREVIEW` | 2667256 | endereçado | `06`/`SELECIONA_TIME` R |
| `OFS_KIT_PREVIEW_A` | 2669544 | endereçado | `10`/`TIME_FUNDO` R |
| `OFS_KIT_PREVIEW_B` | 2671896 | endereçado | `11`/`TIME_120` R |
| `OFS_KIT_PREVIEW_C` | 2674248 | endereçado | `11`/`TIME_120` R |
| `OFS_TEAM_NAME_5` | 4822908 | base de varredura | `Seek` + `for` no `Database.cpp` |
| `OFS_TEAM_NAME_5_A` | 4823976 | retomada de fronteira | `if(i == 57)` no `Database.cpp`, `Seek` em :209 |
| `OFS_TEAM_NAME_6_A` | 5651880 | endereçado | `06`/`SELECIONA_TIME` R |
| `OFS_TEAM_NAME_6_B` | 5652364 | endereçado | `06`/`SELECIONA_TIME` R |
| `OFS_FLAG_COLOURS_SENEGAL` | 12545758 | endereçado | `11`/`FICHA_60` R |
| `OFS_FLAG_COLOURS` | 12549518 | endereçado | `06`/`SELECIONA_TIME` R |
| `OFS_FLAG_COLOURS_A` | 12550296 | endereçado | `10`/`TIME_FUNDO` R |
| `OFS_FLAG_COLOURS_B` | 12552648 | endereçado | `11`/`TIME_120` R |

| veredito | quantos |
|---|---:|
| endereçado | 33 |
| retomada de fronteira | 14 |
| base de varredura | 3 |

**Nenhum sem veredito.** O critério da task está fechado — o que não
quer dizer que os 17 não endereçados sejam
inalcançáveis: quer dizer que alcançá-los exige escolher na tela
exatamente o registro que cai na fronteira, e que a ausência deles é
previsão do fonte, não buraco de cobertura.

---

## Geometria de setor, conferida

28 de 29 faixas começam dentro da região de dados de
usuário de um setor MODE2/2352 (bytes 24..2071).
O corte não é decorativo: é o mesmo que a WTE-TASK-06 usa para separar
offset de imagem de constante qualquer, e vê-lo valer sobre syscall
real é a confirmação de que a régua estática media a coisa certa.

A(s) exceção(ões):

- `ARRANQUE` R em `0`, 23 byte(s) — byte 0 do setor 0.

A leitura de 23 bytes no offset `0` não é dado: é o *sync* mais o
cabeçalho do setor 0, que o editor lê para reconhecer o formato — e
cabeçalho de setor fica, por definição, fora da região de dados.

