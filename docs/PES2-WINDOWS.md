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

```powershell
cd C:\games\ps1\duckstation-mcp
.\duckstation-qt-x64-ReleaseLTCG.exe `
  "C:\games\ps1\work\Pro Evolution Soccer 2 (Europe) (EsIt)\Pro Evolution Soccer 2 (Europe) (Es,It).cue"
```

Dispense o **`Automatic Updater`** que sobe junto (*Remind Me Later* — `Skip`
silencia para sempre escrevendo na configuração, e esta é a do usuário). A
porta 2346 **abre antes** de o diálogo ser dispensado, medido no Linux em
2026-09-03; o diálogo ainda assim atrapalha, porque fica por cima da janela do
jogo.

Depois, de dentro do repositório:

```powershell
python tools\pes2\mcp.py --status
python tools\pes2\mcp.py --list
python tools\pes2\mcp.py --call get_status
```

Pré-requisito do emulador: **Visual C++ Redistributable 2022 (x64)**. Se faltar,
o `.exe` morre sem janela e sem mensagem útil.

## 5. O que não atravessa

Esta é a parte que economiza a tarde. Três camadas do ferramental do Linux
dependem de coisas que não existem no Windows:

| Ferramenta | No Windows | Por quê |
|---|---|---|
| `tools/pes2/fork.py` | **não roda** | `pgrep -x`, `signal.SIGKILL`, `xdotool` para dispensar o diálogo, `DISPLAY=:98` |
| `tools/pes2/drive.py` | **não roda** | dirige por `xdotool` e captura por `import -window` |
| `tools/pes2/mcp_drive.py` | **parcial** | as rotas chamam `fork.launch()`; `--measure-menu`, que trabalha contra um jogo já de pé, é o que sobra |
| `tools/pes2/boot_check.sh`, `asset_screen.sh`, `run_duckstation.sh` | **não rodam** | shell + Xvfb |
| `tools/pes2/savestate.py` | precisa de `zstd.exe` no `PATH` | ele descomprime o estado chamando o `zstd` de linha de comando |
| `mcp.py`, `pad.py`, `iso.py`, `tables.py`, `team_map.py`, `poke.py`, `player_map.py`, `lzss.py`, `bin_archive.py`, `asset_write.py`, `memcard.py`, `ofs_map.py`, `diff_releases.py`, `strings_inventory.py`, `tname.py`, `lang_map.py`, `faq_check.py` | **rodam** | Python 3 puro, stdlib |

**A bateria golden inteira do `newWe2002` também não roda lá**, pelo mesmo
motivo — é Xvfb, `xdotool` e Wine. Já está registrado em
[/docs/PLAN-WTE-WINDOWS.md](/docs/PLAN-WTE-WINDOWS.md).

Consequência prática: no Windows **o emulador se sobe à mão** e as ferramentas
falam com ele por MCP. Não há equivalente do `fork.py launch`, e escrever um
custaria reimplementar o dispensar-diálogo com a API de janela do Windows — o
que a §"fora da tela" do [../CLAUDE.md](../CLAUDE.md) descreve para o `ed.exe`,
e que aqui ainda não foi feito.

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
