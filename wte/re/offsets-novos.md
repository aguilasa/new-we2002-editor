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

Medido, e é o que impede esta task de fechar. Com as duas ROMs que este
repositório tem, o `wte.exe` **encerra com falha de segmentação logo
depois** de ler os dados do primeiro time selecionado:

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
time, então o gate tem em que se apoiar e o que está bloqueado aqui é
remedível refazendo a corrida com a outra imagem. Quem refizer, refaça
**as duas** — a comparação entre elas é o que sustenta o diagnóstico.

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

