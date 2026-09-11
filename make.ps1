<#
.SYNOPSIS
  Abre os editores deste repositorio no WINDOWS -- o irmao dos alvos `run-*`
  do `Makefile` da raiz.

.DESCRIPTION
  O `Makefile` da raiz e GNU make + bash, e nenhum dos dois vem com o Windows.
  Este script cobre os dois alvos que rodam aqui hoje e **recusa os que nao
  rodam, dizendo por que** -- a mesma regra do `check`: alvo verde sem medicao
  e pior do que alvo ausente.

      .\make.ps1                      lista os alvos e o ambiente achado
      .\make.ps1 run-obocaman         o we-team-editor.exe do Obocaman
      .\make.ps1 run-lazarus          o WE2002 - Lazarus Editor
      .\make.ps1 fresh                descarta as copias de trabalho

  `-Image <caminho>` troca a imagem de origem, `-Work <dir>` o diretorio das
  copias. Ver `docs/PLAN-WTE-WINDOWS.md` para o resto da porta.

  ## SAO TRES EDITORES, e so dois abrem aqui

      newWe2002          o port Qt do `ed.exe` (Moriero, 2002)
      we-team-editor     o do Obocaman (2002), PE32
      WE2002 - Lazarus   o app Lazarus deste repositorio

  O `newWe2002` NAO tem alvo aqui: ele precisa de Qt6 e MSVC, e a secao 2 do
  `docs/PLAN-WINDOWS.md` e que descreve aquele ambiente. Este script e da
  porta do `wte/`, que nao depende de nenhum dos dois.

  ## O que muda do Linux, e e a diferenca que importa

  No Linux o editor do Obocaman roda **sob Wine**, num prefix `WINEARCH=win32`
  proprio, e o alvo confere o stack X i386 do host antes de tentar. Aqui ele e
  um PE32 num Windows x64: **roda nativo pelo WOW64**, sem Wine, sem prefix e
  sem nada para conferir. Medido em 2026-08-27 -- a janela abre e o dialogo
  "Abre" e o comum do Windows, com o filtro `ISO do W11 (.bin)`.

  ## Cada editor sobre a PROPRIA copia

  Os tres gravam **in-place**. Duas copias de ~474 MB nao e desperdicio: e o
  que impede uma corrida de um editor de aparecer como resultado do outro.
  `roms/` nunca e alvo.
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet(
        'help', 'run-obocaman', 'run-lazarus', 'fresh',
        'pes2', 'pes2-copy', 'pes2-kill', 'pes2-status',
        'we2002-play', 'we2002-play-fresh',
        'we2002-ptbr-play', 'we2002-ptbr-play-fresh',
        'we2002-cards', 'we2002-card-snap', 'we2002-card-list',
        # Recusados com explicacao -- ver Invoke-Recusa. Eles estao NESTA
        # lista de proposito: quem vem do Makefile digita o nome que conhece,
        # e a recusa do ValidateSet e uma parede de alternativas sem motivo
        # nenhum junto. A regra e a do .DESCRIPTION: dizer por que.
        'pes2-play', 'pes2-98', 'we2002-98', 'we2002-ptbr-98',
        'we2002-src-check', 'mcr', 'mcr-venv', 'mcr-98')]
    [string]$Alvo = 'help',

    # Imagem de origem dos EDITORES. O default e o do `Makefile` da raiz.
    # Nao confundir com -GameImage, que e a do jogo sob o emulador.
    [string]$Image = 'roms\golden-european-deluxe.bin',

    # Onde ficam as copias de trabalho DOS EDITORES. O par do emulador e
    # `$Games\work`, e os dois nao tem relacao -- ver Invoke-Help.
    [string]$Work = 'work',

    # ------------------------------------------------------ emulador ----
    #
    # A raiz do que o DuckStation usa nesta maquina: `roms\` e `work\` saem
    # dela. E a mesma particao que no Linux e
    # /media/ingmar/649806ED9806BE14/games/ps1 -- ver docs/PES2-WINDOWS.md.
    [string]$Games = 'C:\games\ps1',

    # Qual release de PES2. O `PES2_TAG` do Makefile.
    [ValidateSet('EsIt', 'EnFrDe')]
    [string]$Pes2Tag = 'EsIt',

    # A imagem do WE2002 que o emulador roda, e o apelido da copia dela.
    # **Nascem nulos de proposito**: o default depende de $Games, e um
    # default de parametro do PowerShell nao enxerga outro parametro. Eles
    # sao preenchidos logo abaixo, e os apelidos `we2002-ptbr-*`/`-jp-*` so
    # os tocam se o usuario nao passou -- que e a semantica do `?=` do make.
    [string]$GameImage,
    [string]$GameSlug,

    # Onde o DuckStation guarda cartao e save state. No Windows ele roda em
    # **modo portable**, entao e a pasta do proprio .exe e nao um
    # ~/.local/share. Vale tambem como PES2_FORK para o fork.py.
    [string]$DuckData,

    # Obrigatorio em `we2002-card-snap`: o rotulo da amostra.
    [string]$Label,

    # Mapeia uma letra de unidade para $Work enquanto o editor do Obocaman
    # roda, e a desfaz ao sair. E o equivalente nativo do `dosdevices/e:` que
    # o alvo `wte` do Makefile cria no prefix Wine: encurta o caminho que se
    # digita no dialogo "Abre". Sem isto o script so IMPRIME o caminho, para
    # colar -- que e o comportamento default, porque `subst` cria uma unidade
    # visivel no Explorer e isso e mudanca no sistema de quem chamou.
    [string]$Subst,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Resto
)

$ErrorActionPreference = 'Stop'

$ROOT     = $PSScriptRoot
$WTE      = Join-Path $ROOT 'wte'
$OBO_DIR  = Join-Path $ROOT 'we-team-editor'
$OBO_EXE  = Join-Path $OBO_DIR 'we-team-editor.exe'
$LAZ_MAKE = Join-Path $WTE 'make.ps1'
$LAZ_BIN  = Join-Path $WTE 'build\wte.exe'

function Resolve-Absoluto([string]$p) {
    if ([System.IO.Path]::IsPathRooted($p)) { return $p }
    return (Join-Path $ROOT $p)
}

$IMG      = Resolve-Absoluto $Image
$WORK_DIR = Resolve-Absoluto $Work

# ------------------------------------------------------------- emulador ----

$GAMES_ROOT = Resolve-Absoluto $Games
$GAMES_ROMS = Join-Path $GAMES_ROOT 'roms'
$GAMES_WORK = Join-Path $GAMES_ROOT 'work'

$DUCK_DATA = if ($DuckData) { Resolve-Absoluto $DuckData }
             else { Join-Path $GAMES_ROOT 'duckstation-mcp' }
$DUCK_CARDS  = Join-Path $DUCK_DATA 'memcards'
$DUCK_STATES = Join-Path $DUCK_DATA 'savestates'

# Um lugar so declara onde o fork mora. Sem isto o caminho ficaria repetido
# aqui e no default do `fork.py`, e `-DuckData` mudaria um sem mudar o outro.
$env:PES2_FORK = $DUCK_DATA

$FORK_PY = Join-Path $ROOT 'tools\pes2\fork.py'

$PES2_RELEASE = Join-Path $GAMES_ROMS "Pro Evolution Soccer 2 (Europe) ($Pes2Tag)"

# **O nome da copia e o da propria release, nao um apelido.** O
# `pes2-$(PES2_TAG)` do Makefile e curto porque *alvo de make nao aceita
# espaco* e nao ha como escapar isso (Makefile:441-458) -- limitacao de make,
# nao regra do projeto. Aqui o nome longo passa, e usa-lo significa ADOTAR a
# copia que docs/PES2-WINDOWS.md ja mandou fazer, em vez de criar uma
# terceira de 571 MB ao lado das duas que ja existem neste disco.
$PES2_DIR = Join-Path $GAMES_WORK ([System.IO.Path]::GetFileName($PES2_RELEASE))

$CARD_DIR = Join-Path $GAMES_WORK 'cards'

# As imagens de WE2002 que existem, e o apelido de cada uma. Todas bootam
# SLPM_870.56, entao dividem o mesmo option file -- trocar de imagem nao
# troca de cartao.
#
# **`ptbr` e a `we2002-pt-br.bin`, e nao a `ptbr-remaster.bin`.** Sao duas
# imagens PT-BR diferentes e a distincao e medida: a `we2002-pt-br.bin` tem
# 201.714 setores, **150 a menos** que a European Deluxe, que e exatamente a
# diferenca que o Makefile:506-514 registra ao proibir emprestar o .cue de
# uma para a outra; a `ptbr-remaster.bin` tem 201.864, o mesmo da Deluxe. O
# `PTBR` do Makefile (linha 466) aponta para a primeira, entao `ptbr` aqui
# aponta para a mesma coisa -- e o remaster, que e a imagem dos golden do
# `newWe2002`, ganhou apelido proprio.
#
# **O default e `english`**, como o `GAME_IMAGE` do Makefile (linha 439) --
# e a imagem em que o grupo `we2002-*` foi pensado. Ela mora num
# SUBDIRETORIO proprio; o `.cue` dela esta dentro da mesma pasta, e e de
# onde `New-CueDoJogo` o le. A `we2002-pt-br.bin` nao tem `.cue` vizinho,
# entao e ela que exercita o ramo que SINTETIZA um.
#
# **Eram cinco ate 2026-09-11.** A japonesa, o `ptbr-remaster.bin` e a
# `golden-european-deluxe.bin` sairam junto com as imagens, a pedido do
# usuario: elas continuam em `roms/` DO REPOSITORIO, que e onde os golden
# do `newWe2002` as procuram, e o que foi apagado foi a copia do disco de
# jogos. Para rodar uma delas aqui, `-GameImage` e `-GameSlug` aceitam
# qualquer caminho -- nenhuma virtude se perdeu com os apelidos.
$JOGOS = @{
    'english' = 'we2002\we2002-english\we2002-english.bin'
    'ptbr'    = 'we2002\we2002-pt-br.bin'
}

# **Capturado aqui, no escopo do script.** Dentro de uma funcao,
# $PSBoundParameters e o da funcao, nao o do script -- e a flag tem de ser
# lida ANTES de qualquer default ser aplicado, senao nao ha como distinguir
# "o usuario passou deluxe" de "ninguem passou nada".
$IMAGEM_DO_USUARIO = $PSBoundParameters.ContainsKey('GameImage')
$SLUG_DO_USUARIO   = $PSBoundParameters.ContainsKey('GameSlug')

function Set-Jogo([string]$slug) {
    <#
      Aponta $GameImage/$GameSlug para uma das tres. O que o usuario passou
      ganha -- e a semantica do `?=` do make.
    #>
    if (-not $IMAGEM_DO_USUARIO) { $script:GameImage = $JOGOS[$slug] }
    if (-not $SLUG_DO_USUARIO)   { $script:GameSlug  = $slug }
}

if (-not $GameImage) { $GameImage = $JOGOS['english'] }
if (-not $GameSlug)  { $GameSlug  = 'english' }

# ---------------------------------------------------------------- copias ----

function New-CopiaDeTrabalho([string]$prefixo) {
    <#
      A copia do editor `$prefixo`, feita se ainda nao existir.

      NAO se copia por cima de uma copia que ja existe: ela pode ter edicoes
      que o usuario quer manter entre uma sessao e outra. Quem quer comecar do
      zero chama `fresh`, que e explicito. Mesma semantica do `Makefile`, onde
      a copia e um alvo de arquivo e o `fresh` e que a apaga.
    #>
    if (-not (Test-Path $IMG)) {
        throw @"
imagem ausente: $IMG
As imagens ficam em roms/, e nao sao versionadas (~780 MB) -- o usuario as
mantem. Se a pasta estiver vazia, traga os dumps; nao baixe nada.
"@
    }
    if (-not (Test-Path $WORK_DIR)) {
        New-Item -ItemType Directory -Force $WORK_DIR | Out-Null

        # O aviso da pasta sincronizada, uma vez so, quando a pasta nasce.
        # Duas copias de ~474 MB dentro do OneDrive sao ~950 MB de upload que
        # ninguem pediu. `-Work` resolve sem mudar nada do que se roda.
        #
        # QUEM DECIDE E O `$WORK_DIR`, NAO O `$ROOT`. Testar a raiz do
        # repositorio faz o aviso sair mesmo para quem ja passou `-Work` para
        # fora do OneDrive -- ou seja, justamente para quem ja fez o que ele
        # manda fazer. Aviso que nao some quando o problema some vira ruido, e
        # ruido nao se le.
        if ($WORK_DIR -like '*OneDrive*') {
            Write-Host ''
            Write-Host 'AVISO: este repositorio esta dentro do OneDrive, e as'
            Write-Host '       copias de trabalho sao de ~474 MB cada. Para'
            Write-Host '       mante-las fora da sincronizacao:'
            Write-Host "         .\make.ps1 $Alvo -Work D:\tmp\we2002"
            Write-Host ''
        }
    }
    $destino = Join-Path $WORK_DIR "$prefixo-$([System.IO.Path]::GetFileName($IMG))"
    if (Test-Path $destino) {
        Write-Host ">> reusando $destino"
    } else {
        $mb = [math]::Round((Get-Item $IMG).Length / 1MB)
        Write-Host ">> copiando $IMG -> $destino  (~$mb MB)"
        Copy-Item $IMG $destino
    }
    return $destino
}

# ------------------------------------------------------ python e o fork ----

$script:PY = $null

function Get-Python {
    <#
      O interpretador, provado antes de ser devolvido.

      **`python3` NAO entra na lista.** No Windows ele resolve para
      `...\WindowsApps\python3.exe`, o App Execution Alias da Microsoft
      Store: um reparse point de tamanho zero que abre a loja e sai 9009.
      Medido nesta maquina -- `python` e `py` sao reais, `python3` e o stub.
    #>
    if ($script:PY) { return $script:PY }
    foreach ($nome in @('python', 'py')) {
        $cmd = Get-Command $nome -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        $exe = $cmd.Source
        # Provar que roda, em vez de confiar no PATH.
        & $exe -c 'import sys' 2>$null
        if ($LASTEXITCODE -eq 0) { $script:PY = $exe; return $exe }
    }
    throw @"
nenhum Python utilizavel no PATH.
Procurados: python, py. (`python3` e o stub da Microsoft Store e nao serve.)
"@
}

function Invoke-Fork {
    <#
      Roda o `tools/pes2/fork.py` e traduz o codigo de saida.

      Tres coisas que parecem detalhe e nao sao:

      `-u`: o `fork.py` so da flush dentro do `say()`. Sem isto o resto fica
      no buffer do pipe e quem chamou olha um terminal morto por dois
      minutos enquanto o jogo boota.

      **Nada de `2>&1`.** No PowerShell 5.1 redirecionar o stderr de um
      executavel nativo embrulha cada linha num NativeCommandError; com
      $ErrorActionPreference = 'Stop' isso ESTOURA numa corrida que deu
      certo, no exato momento em que se queria capturar a mensagem.

      `77` e o SKIP do fork.py -- "esta maquina nao pode" --, e nao falha.
    #>
    param([string[]]$ForkArgs, [switch]$Silencioso)

    $py = Get-Python
    if ($Silencioso) {
        $saida = & $py -u $FORK_PY @ForkArgs
    } else {
        & $py -u $FORK_PY @ForkArgs
        $saida = $null
    }
    $codigo = $LASTEXITCODE
    if ($codigo -eq 77) {
        throw "fork.py $($ForkArgs[0]): pulado (77) -- a mensagem acima diz por que"
    }
    if ($codigo -ne 0) {
        throw "fork.py $($ForkArgs[0]) saiu $codigo"
    }
    return $saida
}

function Test-Fork {
    <#
      A guarda do Makefile:371-374. O fork nao e versionado (CC-BY-NC-ND-4.0,
      mesma regra de roms/), entao a ausencia dele e um caso comum e merece a
      receita, nao um traceback.
    #>
    $py = Get-Python
    & $py $FORK_PY which | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw @"
fork do DuckStation ausente em $DUCK_DATA
Ele nao e versionado (CC-BY-NC-ND-4.0). Para reconstruir:
  python tools\pes2\fork.py recipe
"@
    }
}

# ---------------------------------------------------------- copias PES2 ----

function New-CopiaPes2 {
    <#
      A copia da release, conferida arquivo a arquivo.

      **Sem carimbo `.copied`.** No Makefile ele existe so para dar a `make`
      um no de arquivo de que depender (Makefile:342,353-362); portado ao pe
      da letra ele RECOPIARIA 571 MB por cima da copia boa que ja esta em
      $GAMES_WORK, que nao tem carimbo nenhum.

      **Dirigida pela origem**, nunca um espelho: o destino tambem tem o
      `duckstation-fork.log`, que o fork.py escreve ao lado da imagem, e um
      /MIR o apagaria.

      E nada de `Copy-Item -Recurse` do diretorio: com o destino ausente ele
      cria a copia, com o destino presente ele cria destino\<leaf>\ DENTRO.
      Rodar duas vezes aninha.
    #>
    if (-not (Test-Path -LiteralPath $PES2_RELEASE)) {
        throw @"
release ausente: $PES2_RELEASE
As releases ficam em $GAMES_ROMS e nao sao versionadas.
-Pes2Tag EsIt|EnFrDe escolhe qual.
"@
    }
    if (-not (Test-Path -LiteralPath $GAMES_WORK)) {
        New-Item -ItemType Directory -Force -Path $GAMES_WORK | Out-Null
    }
    if (-not (Test-Path -LiteralPath $PES2_DIR)) {
        New-Item -ItemType Directory -Force -Path $PES2_DIR | Out-Null
    }

    $origem = @(Get-ChildItem -LiteralPath $PES2_RELEASE -File)
    $n = 0
    $copiados = 0
    foreach ($f in $origem) {
        $n++
        $destino = Join-Path $PES2_DIR $f.Name
        $existe = Get-Item -LiteralPath $destino -ErrorAction SilentlyContinue
        if ($existe -and $existe.Length -eq $f.Length) { continue }
        $mb = [math]::Round($f.Length / 1MB)
        Write-Host (">> [{0}/{1}] {2}  (~{3} MB)" -f $n, $origem.Count, $f.Name, $mb)
        Copy-Item -LiteralPath $f.FullName -Destination $destino -Force
        $copiados++
    }
    if ($copiados -eq 0) {
        Write-Host ">> copia ja completa em $PES2_DIR  ($($origem.Count) arquivos)"
    }
    return $PES2_DIR
}

function Get-CueDaCopia {
    <#
      Acha o .cue DENTRO da copia (Makefile:375-378). Ele nao se monta pelo
      nome: o das duas releases difere -- "(Es,It)" contra "(En,Fr,De)".
    #>
    $cue = Get-ChildItem -LiteralPath $PES2_DIR -Filter '*.cue' -File `
             -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $cue) {
        throw "nenhum .cue em $PES2_DIR -- refaca com: .\make.ps1 pes2-copy"
    }
    return $cue.FullName
}

# ------------------------------------------------- copia e cue do WE2002 ----

function New-CopiaDoJogo {
    <#
      A copia da imagem do WE2002, com nome fixo pelo apelido, e o carimbo
      que guarda de qual origem ela veio (Makefile:494-504).

      A comparacao do carimbo e por caminho NORMALIZADO e sem diferenciar
      maiuscula: no NTFS `c:\` e `C:\` sao o mesmo arquivo e bytes
      diferentes, e um `cmp` literal recopiaria 474 MB porque alguem
      capitalizou a letra da unidade.
    #>
    $origem = Resolve-Absoluto (Join-Path $GAMES_ROMS $GameImage)
    if (-not (Test-Path -LiteralPath $origem)) {
        throw @"
imagem ausente: $origem
As imagens ficam em $GAMES_ROMS\we2002 e nao sao versionadas.
"@
    }
    if (-not (Test-Path -LiteralPath $GAMES_WORK)) {
        New-Item -ItemType Directory -Force -Path $GAMES_WORK | Out-Null
    }

    $copia   = Join-Path $GAMES_WORK "we2002-$GameSlug.bin"
    $carimbo = Join-Path $GAMES_WORK "we2002-$GameSlug.src"

    $normal = [System.IO.Path]::GetFullPath($origem)
    $antigo = if (Test-Path -LiteralPath $carimbo) {
                  [System.IO.File]::ReadAllText($carimbo)
              } else { '' }

    $precisa = -not (Test-Path -LiteralPath $copia) -or ($antigo -ine $normal)
    if ($precisa) {
        $mb = [math]::Round((Get-Item -LiteralPath $origem).Length / 1MB)
        Write-Host ">> copiando $origem"
        Write-Host "   -> $copia  (~$mb MB)"
        Copy-Item -LiteralPath $origem -Destination $copia -Force
        [System.IO.File]::WriteAllText(
            $carimbo, $normal, (New-Object System.Text.UTF8Encoding $false))
    } else {
        Write-Host ">> reusando $copia"
    }
    return $copia
}

function New-CueDoJogo([string]$copia) {
    <#
      O .cue, nas duas formas do Makefile:506-525.

      Primeiro o que estiver ao lado da imagem, com a linha FILE reescrita,
      porque ela nomeia o .bin de origem e a copia tem outro nome. Se nao
      houver, um SINTETIZADO aqui, so com a trilha de dados.

      **Copiar o .cue da imagem vizinha NAO serve**: a PT-BR e 150 setores
      menor que a European Deluxe e o audio dela nao bate em deslocamento
      nenhum.

      Nada de Get-Content/Set-Content: `Out-File` e UTF-16 no 5.1 e
      `Set-Content` e ANSI, e um BOM antes de `FILE "` e risco real num
      parser de cue. E a reescrita e de arquivo inteiro por regex, para os
      finais de linha do original sobreviverem byte a byte fora do nome.
    #>
    $origem = Resolve-Absoluto (Join-Path $GAMES_ROMS $GameImage)
    $cueVizinho = [System.IO.Path]::ChangeExtension($origem, '.cue')
    $destino = Join-Path $GAMES_WORK "we2002-$GameSlug.cue"
    $nome = [System.IO.Path]::GetFileName($copia)
    $utf8 = New-Object System.Text.UTF8Encoding $false

    if ((Test-Path -LiteralPath $cueVizinho) -and
        (Get-Item -LiteralPath $cueVizinho).Length -gt 0) {
        Write-Host '>> .cue da imagem, com o FILE apontado para a copia'
        $texto = [System.IO.File]::ReadAllText($cueVizinho)
        # MatchEvaluator e nao string de substituicao: ali `$` e referencia
        # de grupo, e um nome de arquivo com `$` viraria outra coisa.
        $avaliador = [System.Text.RegularExpressions.MatchEvaluator] {
            param($m) $m.Groups[1].Value + '"' + $nome + '"'
        }
        $novo = [regex]::Replace($texto, '(?m)^(\s*FILE\s+)"[^"]*"', $avaliador)
        [System.IO.File]::WriteAllText($destino, $novo, $utf8)
    } else {
        Write-Host '>> a imagem nao tem .cue -- sintetizando so a trilha de dados'
        Write-Host '   (o jogo boota; as trilhas de audio ficam de fora)'
        # CRLF como o `ptbr-remaster.cue`, que e a forma que isto imita.
        $texto = "FILE `"$nome`" BINARY`r`n" +
                 "  TRACK 01 MODE2/2352`r`n" +
                 "    INDEX 01 00:00:00`r`n"
        [System.IO.File]::WriteAllText($destino, $texto, $utf8)
    }
    return $destino
}

# ------------------------------------------------------------- cartoes ----

function Get-CartoesDoJogo {
    <#
      O `GAME_CARD_FIND` do Makefile:472-474, numa implementacao so -- a
      guarda que MOVE e o aviso que so olha tem de procurar exatamente a
      mesma coisa.

      Tres padroes, porque o nome depende de como o DuckStation identificou
      a imagem: pelo gamedb (o serial SLPM-87056 leva a `World Soccer
      Winning Eleven 2002 (Japan)`) ou, sem casar, pelo nome do arquivo.
      `-like` ja e insensivel a caixa, que e o `-iname` do find.
    #>
    Get-ChildItem -LiteralPath $DUCK_CARDS -File -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -like '*winning*eleven*' -or
            $_.Name -like '*slpm*870*56*'    -or
            $_.Name -like 'we2002-*'
        } | Sort-Object Name
}

function Get-SaveStatesDoJogo {
    Get-ChildItem -LiteralPath $DUCK_STATES -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like 'SLPM-87056*' } | Sort-Object Name
}

function Get-Md5([string]$caminho) {
    (Get-FileHash -LiteralPath $caminho -Algorithm MD5).Hash.ToLower()
}

# ----------------------------------------------------------------- alvos ----

function Invoke-Help {
    Write-Host 'Editores:'
    Write-Host '  run-obocaman  o we-team-editor.exe do Obocaman -- NATIVO, sem Wine'
    Write-Host '  run-lazarus   o WE2002 - Lazarus Editor, sobre a propria copia'
    Write-Host '  fresh         descarta as copias de trabalho'
    Write-Host ''
    Write-Host 'PES2 -- outro jogo, outro projeto, e nao tem editor:'
    Write-Host '  pes2          abre o JOGO sob o fork do DuckStation (com MCP)'
    Write-Host '  pes2-copy     so a copia da release (~571 MB, 8 trilhas)'
    Write-Host '  pes2-kill     encerra o emulador'
    Write-Host '  pes2-status   diz o que esta rodando, e se e o fork'
    Write-Host '                -Pes2Tag EsIt|EnFrDe escolhe a release'
    Write-Host ''
    Write-Host 'O JOGO deste repositorio, sob o mesmo fork:'
    Write-Host '  we2002-play        roda a imagem sobre o option file que houver'
    Write-Host '  we2002-play-fresh  idem, comecando com o option file zerado'
    Write-Host '                     (o default e a we2002-english.bin)'
    Write-Host '  we2002-ptbr-play   e o par -fresh: a we2002-pt-br.bin.'
    Write-Host '                     Mesmo option file -- as duas bootam'
    Write-Host '                     SLPM_870.56, entao trocar de imagem nao'
    Write-Host '                     troca de cartao.'
    Write-Host '                     Outra imagem qualquer: -GameImage <bin>'
    Write-Host '                     -GameSlug <nome>'
    Write-Host '  we2002-cards       so a guarda: tira do caminho o option file'
    Write-Host '  we2002-card-snap -Label x   guarda o cartao vivo como amostra'
    Write-Host '  we2002-card-list            lista as amostras e os md5'
    Write-Host ''
    Write-Host '  Uma sessao por vez: o `launch` encerra todo DuckStation antes'
    Write-Host '  de subir, entao `pes2` derruba um `we2002-play` em curso e'
    Write-Host '  vice-versa.'
    Write-Host ''
    Write-Host 'Opcoes:'
    Write-Host '  -- dos EDITORES --'
    Write-Host "  -Image <bin>     imagem de origem (atual: $Image)"
    Write-Host "  -Work <dir>      copias de trabalho (atual: $Work)"
    Write-Host '  -Subst <L>       mapeia a unidade L: para -Work enquanto o'
    Write-Host '                   editor do Obocaman roda, e desfaz ao sair'
    Write-Host '  -- do EMULADOR (outro diretorio de trabalho, sem relacao) --'
    Write-Host "  -Games <dir>     raiz de roms\ e work\ (atual: $Games)"
    Write-Host "  -Pes2Tag <tag>   EsIt ou EnFrDe (atual: $Pes2Tag)"
    Write-Host "  -GameImage <bin> imagem do WE2002 (atual: $GameImage)"
    Write-Host "  -GameSlug <nome> apelido da copia (atual: $GameSlug)"
    Write-Host "  -DuckData <dir>  cartoes e save states (atual: $DUCK_DATA)"
    Write-Host '  -Label <nome>    o rotulo de we2002-card-snap'
    Write-Host ''
    Write-Host 'Ambiente:'
    Write-Host "  imagem          $IMG$(if (Test-Path $IMG) { '' } else { '   <AUSENTE>' })"
    Write-Host "  Obocaman        $OBO_EXE$(if (Test-Path $OBO_EXE) { '' } else { '   <AUSENTE>' })"
    Write-Host "  Lazarus         $LAZ_BIN$(if (Test-Path $LAZ_BIN) { '' } else { '   <sera compilado>' })"
    Write-Host "  copias em       $WORK_DIR"

    $py = $null
    try { $py = Get-Python } catch { }
    Write-Host "  python          $(if ($py) { $py } else { '<AUSENTE>' })"

    $temFork = $false
    if ($py) {
        & $py $FORK_PY which | Out-Null
        $temFork = ($LASTEXITCODE -eq 0)
    }
    Write-Host "  fork            $DUCK_DATA$(if ($temFork) { '' } else { '   <AUSENTE -- fork.py recipe>' })"
    Write-Host "  release PES2    $PES2_RELEASE$(if (Test-Path -LiteralPath $PES2_RELEASE) { '' } else { '   <AUSENTE>' })"
    Write-Host "  copia PES2      $PES2_DIR$(if (Test-Path -LiteralPath $PES2_DIR) { '' } else { '   <sera copiada, ~571 MB>' })"

    $imgJogo = Join-Path $GAMES_ROMS $GameImage
    Write-Host "  imagem do jogo  $imgJogo$(if (Test-Path -LiteralPath $imgJogo) { '' } else { '   <AUSENTE>' })"
    Write-Host "  copia do jogo   $(Join-Path $GAMES_WORK "we2002-$GameSlug.bin")"

    # Os cartoes achados vao impressos de proposito: e o mesmo
    # Get-CartoesDoJogo que a guarda usa, entao o help PROVA que os tres
    # padroes casam nesta maquina antes de alguem rodar o `-fresh`.
    $cartoes = @(Get-CartoesDoJogo)
    Write-Host "  cartoes         $DUCK_CARDS   ($($cartoes.Count) do jogo)"
    foreach ($c in $cartoes) { Write-Host "                    $($c.Name)" }
    $estados = @(Get-SaveStatesDoJogo)
    Write-Host "  save states     $DUCK_STATES   ($($estados.Count) de SLPM-87056)"
    Write-Host ''
    Write-Host 'O que este script NAO tem:'
    Write-Host '  run / oracle / golden -- sao do newWe2002 e do ed.exe, que'
    Write-Host '  precisam de Qt6, MSVC e (os golden) de Xvfb e Wine. Ver a'
    Write-Host '  secao 2 de docs/PLAN-WINDOWS.md e a secao 5 de'
    Write-Host '  docs/PLAN-WTE-WINDOWS.md.'
    Write-Host '  O par -98 de cada alvo, e o pes2-play: nao ha Xvfb aqui, e a'
    Write-Host '  janela do emulador aparece na unica tela que existe.'
    Write-Host '  drive.py e mcp_drive.py -- xdotool e import -window. Ver a'
    Write-Host '  secao 5 de docs/PES2-WINDOWS.md.'
    Write-Host ''
    Write-Host 'A compilacao e a bateria do Lazarus moram em wte\make.ps1.'
}

function Invoke-RunObocaman {
    if (-not (Test-Path $OBO_EXE)) {
        throw @"
$OBO_EXE ausente.
Esse editor e de terceiro, sem fonte e sem licenca: nao e versionado, e o
usuario mantem a pasta -- como faz com roms/. Ponha `we-team-editor/` na raiz.
"@
    }
    $copia = New-CopiaDeTrabalho 'obo'

    # A ARMADILHA DA EUROPEAN DELUXE, e ela e do original, nao nossa.
    #
    # O `wte.exe` morre com `c0000005` ao TROCAR DE TIME nessa ROM: ele escreve
    # alem do fim de uma tabela em `.data` e atropela tres enderecos que a
    # japonesa nao alcanca. Medido e diagnosticado em `wte/re/crash-causa.md`,
    # e e por isso que 23 dos 24 roteiros golden saem `SEM_ORACULO` ali.
    #
    # O aviso e aqui e nao no README porque e aqui que alguem esta prestes a
    # abrir a ROM errada e achar que o problema e a porta para Windows.
    if ([System.IO.Path]::GetFileName($IMG) -eq 'golden-european-deluxe.bin') {
        Write-Host ''
        Write-Host 'AVISO: nesta ROM o editor do Obocaman TRAVA ao trocar de'
        Write-Host '       time -- c0000005, escrita alem do fim de tabela. E'
        Write-Host '       bug dele, diagnosticado em wte\re\crash-causa.md.'
        Write-Host '       Para exercitar o editor de verdade:'
        Write-Host '         .\make.ps1 run-obocaman -Image roms\japanese-shift-jis.bin'
        Write-Host ''
    }

    # O caminho que se digita no dialogo "Abre".
    #
    # O CWD tem de ser a pasta do editor -- ele monta o caminho do `dat.bin` e
    # dos 198 bitmaps a partir do diretorio corrente --, entao NAO da para
    # abrir o dialogo ja no diretorio da copia. Sobra encurtar o caminho, e e
    # o que o `-Subst` faz; sem ele, o caminho vai impresso para colar no campo
    # "File name", que o dialogo comum do Windows aceita inteiro.
    $mostrar = $copia
    $mapeou = $false
    if ($Subst) {
        $letra = $Subst.TrimEnd(':', '\')
        if ($letra.Length -ne 1) { throw "-Subst quer UMA letra, veio '$Subst'" }
        if (Test-Path "${letra}:") {
            throw "a unidade ${letra}: ja existe -- escolha outra letra"
        }
        & cmd /c "subst ${letra}: `"$WORK_DIR`"" | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "subst ${letra}: falhou" }
        $mapeou = $true
        $mostrar = Join-Path "${letra}:" ([System.IO.Path]::GetFileName($copia))
    }

    Write-Host ">> no dialogo `"Abre`", cole em File name:"
    Write-Host "   $mostrar"
    Write-Host '>> o aviso de tamanho e o mesmo do ed.exe -- responda "Sim"'
    Write-Host ">> we-team-editor.exe (PE32 nativo, WOW64 -- sem Wine)"
    try {
        # `-WorkingDirectory` na pasta do editor: os assets saem do CWD.
        # `-Wait` para que o `subst` so seja desfeito depois que ele fechar.
        Start-Process -FilePath $OBO_EXE -WorkingDirectory $OBO_DIR -Wait
    } finally {
        if ($mapeou) {
            $letra = $Subst.TrimEnd(':', '\')
            & cmd /c "subst ${letra}: /D" | Out-Null
            Write-Host ">> unidade ${letra}: desfeita"
        }
    }
}

function Invoke-RunLazarus {
    $copia = New-CopiaDeTrabalho 'laz'
    # A compilacao e a resolucao dos assets moram no `wte\make.ps1`; aqui fica
    # a copia da imagem, que e o que aquele script nao faz -- o `run` de la
    # abre o binario sem argumento, e o app entao nao tem imagem para editar.
    & powershell -ExecutionPolicy Bypass -File $LAZ_MAKE build
    if ($LASTEXITCODE -ne 0) { throw "wte\make.ps1 build saiu $LASTEXITCODE" }

    # Os 198 bitmaps e o `dat.bin` sao do editor do Obocaman e nao sao
    # versionados. O `run-lazarus` do Makefile chama `make -C wte assets`
    # sempre, porque la o alvo CRIA o symlink; aqui ele so ORIENTA, entao
    # chamar sempre seria repetir o mesmo texto a cada corrida. So quando
    # falta -- e ai o texto e exatamente o que se precisa ler.
    #
    # A ordem de busca e a do `wte/src/wte_datafiles.pas`, e o sentinela e o
    # mesmo que ele usa: `data\dat.bin`.
    $achou = @($env:WTE_ASSETS_DIR,
               (Join-Path $WTE 'assets'),
               (Join-Path $WTE 'share\we2002Lazarus')) |
             Where-Object { $_ -and (Test-Path (Join-Path $_ 'data\dat.bin')) }
    if (-not $achou) {
        Write-Host ''
        Write-Host 'AVISO: os assets do editor original nao foram achados -- o'
        Write-Host '       app vai abrir e avisar, sem desenhar camisa nem'
        Write-Host '       bandeira. Onde por:'
        Write-Host ''
        & powershell -ExecutionPolicy Bypass -File $LAZ_MAKE assets
        Write-Host ''
    }
    Write-Host ">> $LAZ_BIN $copia"
    $argumentos = @($copia)
    if ($Resto) { $argumentos += $Resto }
    Start-Process -FilePath $LAZ_BIN -ArgumentList $argumentos -Wait -NoNewWindow
}

# --------------------------------------------------- alvos do emulador ----

function Invoke-Pes2Copy { New-CopiaPes2 | Out-Null }

function Invoke-Pes2 {
    <#
      Sobe o JOGO PES2 sob o fork, e FICA rodando: o `launch` dispensa o
      modal, espera a porta MCP responder e volta com o PID. Encerre com
      `pes2-kill`.

      **Sem `--display`.** Nao ha Xvfb aqui, e o fork.py ignora a opcao no
      Windows -- passa-la faria este script prometer algo que nao acontece.

      E sem `--window ANY`: o titulo da janela do PES2 e estavel
      ("Pro Evolution Soccer 2"), entao vale o regex default. Quem precisa
      de ANY e o WE2002, cujo titulo vem do gamedb em japones.
    #>
    Test-Fork
    New-CopiaPes2 | Out-Null
    $cue = Get-CueDaCopia
    Write-Host ">> $cue"
    Write-Host '>> para parkar um save state, peca: o slot 1 e o atalho do'
    Write-Host '   menu principal e nao deve ser sobrescrito.'
    Invoke-Fork @('launch', $cue)
}

function Invoke-Pes2Kill   { Invoke-Fork @('kill') }
function Invoke-Pes2Status { Invoke-Fork @('status') }

function Invoke-We2002Cards {
    <#
      A guarda: tira do caminho o option file que houver.

      **MOVE, nunca apaga** -- e por isso o `Move-Item` vai SEM `-Force`:
      `-Force` sobrescreveria um option file ja arquivado, que e exatamente
      o que "movido, nao apagado" promete nao fazer.
    #>
    New-Item -ItemType Directory -Force -Path $DUCK_CARDS | Out-Null
    $velhos = @(Get-CartoesDoJogo)
    if (-not $velhos) {
        Write-Host ">> nenhum option file do jogo em $DUCK_CARDS"
    } else {
        # HH e nao hh: `hh` e 12 horas e colide duas vezes por dia,
        # justamente o que este carimbo existe para evitar.
        $quando = Get-Date -Format 'yyyyMMdd-HHmmss'
        $dest = Join-Path $GAMES_WORK "optionfiles-$quando"
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
        Write-Host '>> option file ja existia -- movendo para fora do caminho'
        foreach ($f in $velhos) {
            Write-Host "   $($f.FullName)"
            Move-Item -LiteralPath $f.FullName -Destination $dest
        }
        Write-Host "   -> $dest  (movido, nao apagado)"
    }

    # Save state carrega o cartao junto, entao carregar um desfaz a guarda
    # de cima. O aviso vem DEPOIS do movimento, como no Makefile.
    $estados = @(Get-SaveStatesDoJogo)
    if ($estados) {
        Write-Host '>> AVISO: ha save state deste jogo, e save state carrega o'
        Write-Host '   cartao junto -- carregar um desfaz a guarda acima:'
        foreach ($s in $estados) { Write-Host "   $($s.FullName)" }
    }
}

function Invoke-We2002Play {
    <#
      **Ele NAO zera o cartao.** Zerar a cada corrida arquivaria um option
      file por partida e faria toda sessao comecar do zero. Quem zera e
      `we2002-play-fresh`. Aqui o cartao so se anuncia.
    #>
    $cartoes = @(Get-CartoesDoJogo)
    if (-not $cartoes) {
        Write-Host ">> sem option file: o jogo vai criar um em $DUCK_CARDS\"
    } else {
        Write-Host '>> continuando sobre o option file que ja existe:'
        foreach ($c in $cartoes) { Write-Host "   $($c.FullName)" }
    }
    Test-Fork
    $copia = New-CopiaDoJogo
    $cue = New-CueDoJogo $copia
    Write-Host ">> $cue"
    # `--window ANY`: o DuckStation nomeia a janela pelo DISPLAY TITLE do
    # gamedb, e para o WE2002 esse titulo e japones -- cravar o texto aqui
    # prenderia o alvo a uma revisao do gamedb.
    Invoke-Fork @('launch', $cue, '--window', 'ANY')
    Write-Host ">> o cartao aparece em $DUCK_CARDS\ assim que o jogo gravar."
    Write-Host '   Encerre com `.\make.ps1 pes2-kill` (o mesmo fork).'
}

function Invoke-We2002PlayFresh {
    Invoke-We2002Cards
    Invoke-We2002Play
}

function Invoke-We2002CardSnap {
    <#
      Guarda o cartao vivo com um rotulo, para uma serie de amostras. O
      option file tem verificacao de integridade propria -- editar a mao e
      recusado pelo jogo (MCR-TASK-17) --, entao a unica fonte de cartao
      valido e o proprio jogo, e uma amostra e insubstituivel. Por isso
      rotulo que ja existe e RECUSADO, nunca sobrescrito.
    #>
    if (-not $Label) {
        throw 'falta o rotulo -- .\make.ps1 we2002-card-snap -Label <nome>'
    }
    $cartao = @(Get-CartoesDoJogo) | Select-Object -First 1
    if (-not $cartao) {
        throw "nenhum option file em $DUCK_CARDS para guardar."
    }
    New-Item -ItemType Directory -Force -Path $CARD_DIR | Out-Null
    $destino = Join-Path $CARD_DIR "$Label.mcr"
    if (Test-Path -LiteralPath $destino) {
        throw "$destino ja existe -- escolha outro rotulo"
    }
    Copy-Item -LiteralPath $cartao.FullName -Destination $destino
    Write-Host ">> $destino"
    Write-Host "   $(Get-Md5 $destino)  $([System.IO.Path]::GetFileName($destino))"
}

function Invoke-We2002CardList {
    if (-not (Test-Path -LiteralPath $CARD_DIR)) {
        Write-Host '(nenhuma amostra ainda)'
        return
    }
    Get-ChildItem -LiteralPath $CARD_DIR | Format-Table Mode, Length, LastWriteTime, Name | Out-Host
    foreach ($f in Get-ChildItem -LiteralPath $CARD_DIR -Filter '*.mcr' -File `
                     -ErrorAction SilentlyContinue) {
        Write-Host "   $(Get-Md5 $f.FullName)  $($f.Name)"
    }
}

function Invoke-Recusa([string]$alvo) {
    <#
      Alvo que o Makefile tem e este script nao pode ter -- dito com o
      motivo, que e a regra do .DESCRIPTION: alvo verde sem medicao e pior
      do que alvo ausente, e nome recusado sem explicacao e pior ainda.
    #>
    $porques = @{
        'pes2-play' = @(
            'Aqui `pes2` JA abre na sua tela. A excecao da secao 6.10 existia'
            'porque no Linux o default era o Xvfb :98; nao ha :98 no Windows,'
            'entao nao ha excecao a nomear.'
            'Use: .\make.ps1 pes2')
        'pes2-98' = @(
            'Nao ha Xvfb no Windows -- o par `-98` de todo alvo de GUI e do'
            'Linux.'
            'Use: .\make.ps1 pes2')
        'we2002-98' = @(
            'Nao ha Xvfb no Windows.'
            'Use: .\make.ps1 we2002-play')
        'we2002-ptbr-98' = @(
            'Nao ha Xvfb no Windows.'
            'Use: .\make.ps1 we2002-ptbr-play')
        'we2002-src-check' = @(
            'Encanamento de make: um alvo .PHONY vazio que forcava a regra do'
            'carimbo .src. Aqui o carimbo e conferido dentro de we2002-play.')
        'mcr' = @(
            'O editor de .mcr e outro projeto (PySide6, docs/PLAN-MCR-PY.md).'
            'Ele RODA no Windows -- tools/mcr/ e Python puro --, mas o venv e'
            'os alvos ainda nao foram portados para este script. Por enquanto:'
            '  python -m venv work\venv-mcr'
            '  work\venv-mcr\Scripts\pip install PySide6'
            '  work\venv-mcr\Scripts\python tools\mcr\ui\app.py <cartao>')
    }
    $porques['mcr-venv'] = $porques['mcr']
    $porques['mcr-98']   = $porques['mcr']

    Write-Host "'$alvo' nao existe neste script." -ForegroundColor Yellow
    foreach ($linha in $porques[$alvo]) { Write-Host "  $linha" }
    exit 2
}

function Invoke-Fresh {
    if (-not (Test-Path $WORK_DIR)) {
        Write-Host ">> nao ha $WORK_DIR -- nada a descartar"
        return
    }
    # So as copias que ESTE script cria. `work/` e compartilhado com as
    # ferramentas do `wte/` -- o `test_conta_ml.py` procura `ml-jp.bin` ali, e
    # apagar a pasta inteira levaria junto uma fixture que ninguem pediu para
    # apagar.
    $alvos = Get-ChildItem $WORK_DIR -Filter '*.bin' -ErrorAction SilentlyContinue |
             Where-Object { $_.Name -like 'obo-*' -or $_.Name -like 'laz-*' }
    if (-not $alvos) {
        Write-Host ">> nenhuma copia obo-*/laz-* em $WORK_DIR"
    }
    foreach ($a in $alvos) {
        Remove-Item $a.FullName -Force
        Write-Host ">> removido $($a.Name)"
    }

    # Segundo bloco: as copias do EMULADOR, que moram noutro diretorio.
    #
    # A copia de PES2 NAO entra, de proposito -- sao 571 MB para recopiar e,
    # pior, e nela que fica a partida jogada a mao de que o save state
    # depende. `optionfiles-*` e `cards` tambem ficam: sao a SAIDA da guarda
    # e do card-snap, e apaga-las faria o `fresh` destruir justamente o que
    # o "movido, nao apagado" prometeu preservar.
    if (Test-Path -LiteralPath $GAMES_WORK) {
        $doJogo = Get-ChildItem -LiteralPath $GAMES_WORK -File `
                    -ErrorAction SilentlyContinue |
                  Where-Object { $_.Name -like 'we2002-*.bin' -or
                                 $_.Name -like 'we2002-*.cue' -or
                                 $_.Name -like 'we2002-*.src' }
        foreach ($a in $doJogo) {
            Remove-Item -LiteralPath $a.FullName -Force
            Write-Host ">> removido $($a.Name)"
        }
        if (-not $doJogo) {
            Write-Host ">> nenhuma copia we2002-* em $GAMES_WORK"
        }
        if (Test-Path -LiteralPath $PES2_DIR) {
            Write-Host ''
            Write-Host '>> a copia de PES2 NAO entra no fresh: sao 571 MB e e nela'
            Write-Host '   que mora a partida jogada a mao de que o save state'
            Write-Host '   depende. Para zerar, explicitamente:'
            Write-Host "     Remove-Item -LiteralPath '$PES2_DIR' -Recurse"
        }
    }
}

switch ($Alvo) {
    'help'                   { Invoke-Help }
    'run-obocaman'           { Invoke-RunObocaman }
    'run-lazarus'            { Invoke-RunLazarus }
    'fresh'                  { Invoke-Fresh }

    'pes2'                   { Invoke-Pes2 }
    'pes2-copy'              { Invoke-Pes2Copy }
    'pes2-kill'              { Invoke-Pes2Kill }
    'pes2-status'            { Invoke-Pes2Status }

    'we2002-play'            { Invoke-We2002Play }
    'we2002-play-fresh'      { Invoke-We2002PlayFresh }
    'we2002-ptbr-play'       { Set-Jogo 'ptbr'; Invoke-We2002Play }
    'we2002-ptbr-play-fresh' { Set-Jogo 'ptbr'; Invoke-We2002PlayFresh }
    'we2002-cards'           { Invoke-We2002Cards }
    'we2002-card-snap'       { Invoke-We2002CardSnap }
    'we2002-card-list'       { Invoke-We2002CardList }

    default                  { Invoke-Recusa $Alvo }
}
