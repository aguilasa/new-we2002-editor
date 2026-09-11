# PES2 no Windows: rodar o DuckStation com MCP

Este documento é **receita de máquina**, não plano de fases: ele diz o que
precisa estar no disco para dirigir o *Pro Evolution Soccer 2* por MCP depois de
bootar no Windows, o que já foi copiado para lá em 2026-09-11, e — a parte que
custa tempo se descoberta tarde — **o que do ferramental do Linux não atravessa**.

O projeto é o de [/docs/PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md); a decisão de
usar o fork com servidor MCP, e a comparação entre os dois binários, está na
§6.14 dele. Aqui só o que muda de plataforma.

---

## 1. O que já está no disco

Tudo em `C:\games\ps1` — que no Linux é
`/media/ingmar/649806ED9806BE14/games/ps1`, a mesma partição, o volume de
sistema do Windows.

```
C:\games\ps1\
  duckstation-mcp\                     o emulador, em modo portable
    duckstation-qt-x64-ReleaseLTCG.exe   1.6.58, build do fork, com MCP
    portable.txt                         (vazio, e é o que liga o modo portable)
    settings.ini                         a configuração do Linux, adaptada
    bios\                                scph1001, scph5500, scph5501, scph7502
    memcards\                            os dois cartões de trabalho
    savestates\                          os sete estados de SLES-03957 e SLPM-87056
    duckstation-windows-x64-release.zip  o pacote original, para reinstalar
  roms\
    Pro Evolution Soccer 2 (Europe) (EsIt)\      as 8 trilhas
    Pro Evolution Soccer 2 (Europe) (EnFrDe)\    as 8 trilhas
    we2002\                                      as quatro imagens de WE2002
  work\                                vazio: é onde a cópia de trabalho mora
```

**`work\` começa vazio, e nada sobe sem ele.** Copiar a release inteira para lá
é o primeiro passo, não um detalhe da regra acima. São 571 MiB, as oito
trilhas, e desde 2026-09-11 o jeito curto é o alvo:

```powershell
.\make.ps1 pes2-copy
```

Ele confere **arquivo a arquivo** e copia só o que falta, então adota uma cópia
que já exista e repõe uma trilha perdida sem recopiar as outras oito.

À mão o comando é este, com uma ressalva que custa caro:

```powershell
Copy-Item -Recurse `
  "C:\games\ps1\roms\Pro Evolution Soccer 2 (Europe) (EsIt)" `
  "C:\games\ps1\work\"
```

**Ele só é seguro na primeira vez.** `Copy-Item -Recurse` cria o destino quando
ele falta e, quando ele já existe, cria uma cópia **dentro** dele — rodar duas
vezes rende
`work\Pro Evolution Soccer 2 (Europe) (EsIt)\Pro Evolution Soccer 2 (Europe) (EsIt)\`
e mais 571 MiB. O alvo não tem esse problema.

**`roms\` são os originais.** PES2 e WE2002 gravam *in-place*, então nada que
escreva aponta para lá — copie a release inteira para `work\` antes, como no
Linux. A regra é a mesma e o motivo é o mesmo.

O repositório também já está naquele disco, em
`C:\github\new-we2002-editor`, mas **desatualizado** — estava em `647f8c9` em
2026-09-11. Um `git pull` antes de usar as ferramentas.

## 2. O binário é o do fork, e isso foi verificado

O `duckstation-qt-x64-ReleaseLTCG.exe` copiado **não** é o DuckStation oficial:
é o `duckstation-windows-x64-release.zip` da release `latest` de
`sadnescity/duckstation` (publicada em 2026-08-29), que é o que o CI do fork
solta a cada push. O oficial não tem servidor MCP nenhum.

Confirmado em 2026-09-11, no `.exe` já copiado:

```
EnableMCPServer  MCPServerPort  duckstation-mcp  memory_scan
snapshot_memory  press_button   frame_step       save_state / load_state
```

e **100 nomes de ferramenta** nos esquemas embutidos no binário. São contados
no `.exe`, não contra o servidor de pé — no Linux a contagem viva deu 95 contra
um fonte que declara 99, então espere o mesmo tipo de diferença e conte com
`mcp.py --list` quando o jogo estiver rodando.

**Isto tem de ser reconferido a cada build.** A release é reconstruída a cada
push e nada promete que a próxima ainda carregue o servidor — a conferência é
parte da receita, não enfeite. No Windows, com o mesmo pacote:

```powershell
Select-String -Path duckstation-qt-x64-ReleaseLTCG.exe -Pattern 'EnableMCPServer' -Encoding Byte
```

ou, mais simples, subir e perguntar: se `mcp.py --list` responde, tem servidor.

## 3. Modo portable, e por que ele

Sem `portable.txt` o DuckStation do Windows guarda dados em
`%USERPROFILE%\Documents\DuckStation`. Com o arquivo ao lado do `.exe` — que é
o que está lá — **tudo mora na própria pasta**: BIOS, cartão, save state e
`settings.ini` viajam junto com o emulador, e o que foi copiado do Linux é lido
sem mais nada.

Uma única linha do `settings.ini` foi adaptada, porque era a única absoluta:

```ini
[GameList]
RecursivePaths = C:\games\ps1\roms
```

O resto veio intacto, inclusive as duas que importam:

```ini
[Debug]
EnableMCPServer = true
MCPServerPort = 2346
```

`SearchDirectory = bios` em `[BIOS]` é relativo e continua valendo no portable.
Os bindings de `[Pad1]` são de um controle SDL; **`press_button` do MCP não
passa por eles**, então um controle ausente não impede dirigir o jogo por
chamada — só impede jogar à mão.

## 4. Subir

Desde 2026-09-11 o **`fork.py` roda aqui**, e o [`make.ps1`](../make.ps1) da
raiz embrulha ele — o caminho curto, que cuida da cópia e acha o `.cue`
sozinho (o nome difere entre as releases: `(Es,It)` contra `(En,Fr,De)`):

```powershell
.\make.ps1 pes2            # copia se precisar, boota, espera a porta MCP
.\make.ps1 pes2-status
.\make.ps1 pes2-kill
.\make.ps1                 # os alvos e o ambiente achado
```

`.\make.ps1 we2002-play` faz o mesmo com o **jogo WE2002** sob o mesmo fork, e
`we2002-cards` tira o option file do caminho antes. Uma sessão por vez: o
`launch` encerra todo DuckStation antes de subir, então um derruba o outro.

Direto pelo `fork.py`, que é o que o alvo chama:

```powershell
python tools\pes2\fork.py launch `
  "C:\games\ps1\work\Pro Evolution Soccer 2 (Europe) (EsIt)\Pro Evolution Soccer 2 (Europe) (Es,It).cue"
python tools\pes2\fork.py status
python tools\pes2\fork.py kill
```

Ele boota, dispensa o modal se houver e **espera a porta responder** antes de
devolver o controle — que é o que separa "subiu" de "está respondendo".

Ou o `.exe` cru:

```powershell
cd C:\games\ps1\duckstation-mcp
.\duckstation-qt-x64-ReleaseLTCG.exe `
  "C:\games\ps1\work\Pro Evolution Soccer 2 (Europe) (EsIt)\Pro Evolution Soccer 2 (Europe) (Es,It).cue"
```

**O `Automatic Updater` não sobe nesta instalação**, medido em 2026-09-11 em
cinco sondagens ao longo de quinze segundos. O motivo está no `settings.ini`:
`[AutoUpdater] LastVersion` veio junto do Linux e casa com o commit deste
build, então o atualizador não tem o que anunciar. Um build novo no CI do fork
o traz de volta — por isso o `fork.py` dispensa assim mesmo, e por
**`WM_CLOSE`**, já que um diálogo Qt desenha os próprios botões e não expõe
`HWND` filho para um `BM_CLICK` alcançar. Esse caminho é o único do módulo que
o Windows ainda não exercitou.

Vale o que a §6.14 do plano mede no Linux: a porta 2346 **abre antes** de o
diálogo ser dispensado.

Depois, de dentro do repositório:

```powershell
python tools\pes2\mcp.py --status
python tools\pes2\mcp.py --list
python tools\pes2\mcp.py --call get_status
```

Pré-requisito do emulador: **Visual C++ Redistributable 2022 (x64)**. Se faltar,
o `.exe` morre sem janela e sem mensagem útil.

## 5. O que não atravessa

Esta é a parte que economiza a tarde. O que sobrou depende de coisas que não
existem no Windows — Xvfb, `xdotool`, `import -window`, shell:

| Ferramenta | No Windows | Por quê |
|---|---|---|
| `tools/pes2/fork.py` | **roda** desde 2026-09-11 | portado: `tasklist` no lugar do `pgrep`, `taskkill /F` no do `SIGKILL`, `ctypes`/`user32` no do `xdotool`, e nenhum display |
| os alvos `pes2*` e `we2002-*` do `Makefile` | **rodam** pelo [`make.ps1`](../make.ps1) | o `Makefile` é GNU make + bash e não roda aqui; os alvos foram portados para o script da raiz. O par `-98` e o `pes2-play` não têm objeto e são **recusados com o motivo** |
| `tools/pes2/drive.py` | **não roda** | dirige por `xdotool` e captura por `import -window` |
| `tools/pes2/mcp_drive.py` | **sobe, mas as rotas não reconhecem a tela** | o `fork.launch()` de que ela depende agora funciona; o que falta são as assinaturas — ver a §7 |
| `tools/pes2/boot_check.sh`, `asset_screen.sh`, `run_duckstation.sh` | **não rodam** | shell + Xvfb |
| `tools/pes2/savestate.py` | precisa de `zstd.exe` no `PATH` | ele descomprime o estado chamando o `zstd` de linha de comando |
| `mcp.py`, `pad.py`, `iso.py`, `tables.py`, `team_map.py`, `poke.py`, `player_map.py`, `lzss.py`, `bin_archive.py`, `asset_write.py`, `memcard.py`, `ofs_map.py`, `diff_releases.py`, `strings_inventory.py`, `tname.py`, `lang_map.py`, `faq_check.py` | **rodam** | Python 3 puro, stdlib |

**A bateria golden inteira do `newWe2002` também não roda lá**, pelo mesmo
motivo — é Xvfb, `xdotool` e Wine. Já está registrado em
[/docs/PLAN-WTE-WINDOWS.md](/docs/PLAN-WTE-WINDOWS.md).

Consequência prática: o `fork.py launch` **existe aqui** desde 2026-09-11, e é
por onde o emulador sobe. O que não existe é a camada de tela — o `drive.py`
continua sendo Xvfb e `import -window`, e as rotas do `mcp_drive.py` esbarram
na §7.

E não há `:98`. A regra de display do repositório é sobre Xvfb; no Windows o
equivalente é a regra de **mover a janela para fora da tela**
(`SetWindowPos(-32000, -32000)`), que vale para o editor. Para o emulador, a
janela aparece — o jogo é para ser visto.

## 6. Reobter o pacote, se precisar

```powershell
gh release download latest --repo sadnescity/duckstation `
   --pattern 'duckstation-windows-x64-release.zip'
```

Descompactar por cima de `duckstation-mcp\` preserva `portable.txt`,
`settings.ini`, `bios\`, `memcards\` e `savestates\`, que não estão no zip.

Compilar do fonte é o segundo caminho e só vale se for para mudar o servidor;
a receita de Linux está em `tools/pes2/fork.py recipe`.

**A licença do DuckStation é CC-BY-NC-ND-4.0**, e o próprio binário diz que
build modificado não pode ser redistribuído. Nada disto entra no repositório —
mesma regra de `roms/` e do `we-team-editor.exe`, em [../NOTICE.md](../NOTICE.md).

## 7. As rotas do `mcp_drive.py` não reconhecem a tela aqui

O emulador sobe, o MCP responde e **o input funciona** — medido em 2026-09-11:
três `press_button button=Start` atravessaram o FMV de abertura, e mais um
levou do título ao *Seleziona Lingua*. Não é o controle, e não é o
`[Pad1]`: os bindings do `settings.ini` são todos `SDL-0/*`, de um controle
que nem está ligado nesta máquina, e o `press_button` do MCP não passa por
eles. O que ele precisa é que a porta tenha um pad, e `Type =
DigitalController` é o que está lá.

O que falha é o **reconhecimento de tela**. As rotas esperam por média de
quadro — `TITLE_MEAN = 0.5526 ± 0.010` no `route_title` —, e nada nesta
máquina chega perto:

| captura | média |
|---|---|
| aviso legal da adidas, t≈10..19 s, estável | 0.856 |
| FMV de abertura, quadro claro isolado | 0.595 |
| FMV de abertura, faixa típica | 0.19..0.33 |
| tela de título | 0.0045 |
| seleção de idioma | 0.048 |

O `wait_for_mean` gasta as 90 fatias de 2 s e falha dizendo a média mais
próxima. Parece laço infinito e não é — são três minutos de espera.

**A causa não é geometria de janela** — isso foi testado e descartado. A
captura sai no tamanho da janela (`ScreenshotMode = ScreenResolution`), e a
janela daqui é **864×655** contra os **800×655** em que as constantes foram
medidas, o que parecia explicação. Não é: redimensionando a janela para dar
captura de exatamente 800×655 e bootando de novo, a banda continua sem ser
alcançada em 60 s.

E o próprio `mcp_drive.py` já dizia isso, no bloco *WHY THE FRAME SIGNATURES
ARE MOSTLY GONE*, entre as coisas que a PES2-TASK-34 eliminou no Linux:
*"it is not the crop -- insetting the frame moves mean and standard deviation
**together**, and the mean did not move"*. Também não é o caminho de captura
(MCP e `import -window` concordam a 0.002245) nem a escala de resolução.

O que **está** medido aqui, e é pouco:

* a banda não aparece em **70 s de amostragem a cada segundo** sem
  fast-forward, nem em **60 s com** ele;
* existe uma tela clara e estável em t≈10..19 s, mas ela é o aviso legal da
  adidas, lendo **0.856** — não o título;
* o título propriamente dito é **escuro**, 0.0045, e o `Start` a partir dele
  leva ao *Seleziona Lingua*.

Ou seja: a sequência de boot que esta máquina percorre não passa por nenhuma
tela de média 0.55. Por que a do Linux passa **não está identificado**, e é a
mesma natureza de mistério que a PES2-TASK-34 registrou ao aposentar o desvio
padrão do critério — *"a number that cannot be reproduced or explained a day
later, on the same binary, is not a criterion"*.

**O próximo passo é medir os dois lados juntos**, não escolher um conserto: a
mesma amostragem densa rodando no Linux, para ver em que instante e em que
tela o 0.5526 aparece lá. Sem isso, qualquer mudança nas constantes é chute —
inclusive a de recortar o letterbox, que parecia óbvia e está refutada.

## 8. A armadilha 35 não é coisa de Linux

O fork **cai sozinho no Windows também**: duas mortes numa sessão em
2026-09-11, as duas dentro de um minuto da primeira chamada MCP, nenhuma
deixando linha de log. É a mesma armadilha 35 da §6.11 do plano, medida no
Linux em 2026-09-03 com quatro mortes em seis corridas.

O diagnóstico do `mcp.py` — que a
[CORR-PES2-032](/docs/tasks/CORR-PES2-032.md) construiu para separar "nunca
subiu" de "caiu agora" — estava **degradado aqui até 2026-09-11**: ele
pergunta a `fork.running_pids()`, que estourava no `pgrep` ausente e caía no
ramo genérico. Com o `fork.py` portado, a mensagem certa aparece:

```
no MCP server at http://127.0.0.1:2346/mcp -- and no DuckStation process
either. It was never started, or it died mid-run (pitfall 35 ...)
```
