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
    [ValidateSet('help', 'run-obocaman', 'run-lazarus', 'fresh')]
    [string]$Alvo = 'help',

    # Imagem de origem. O default e o do `Makefile` da raiz.
    [string]$Image = 'roms\golden-european-deluxe.bin',

    # Onde ficam as copias de trabalho.
    [string]$Work = 'work',

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

# ----------------------------------------------------------------- alvos ----

function Invoke-Help {
    Write-Host 'Alvos:'
    Write-Host '  run-obocaman  o we-team-editor.exe do Obocaman -- NATIVO, sem Wine'
    Write-Host '  run-lazarus   o WE2002 - Lazarus Editor, sobre a propria copia'
    Write-Host '  fresh         descarta as copias de trabalho'
    Write-Host ''
    Write-Host 'Opcoes:'
    Write-Host "  -Image <bin>  imagem de origem (atual: $Image)"
    Write-Host "  -Work <dir>   copias de trabalho (atual: $Work)"
    Write-Host '  -Subst <L>    mapeia a unidade L: para -Work enquanto o'
    Write-Host '                editor do Obocaman roda, e desfaz ao sair'
    Write-Host ''
    Write-Host 'Ambiente:'
    Write-Host "  imagem          $IMG$(if (Test-Path $IMG) { '' } else { '   <AUSENTE>' })"
    Write-Host "  Obocaman        $OBO_EXE$(if (Test-Path $OBO_EXE) { '' } else { '   <AUSENTE>' })"
    Write-Host "  Lazarus         $LAZ_BIN$(if (Test-Path $LAZ_BIN) { '' } else { '   <sera compilado>' })"
    Write-Host "  copias em       $WORK_DIR"
    Write-Host ''
    Write-Host 'O que este script NAO tem:'
    Write-Host '  run / oracle / golden -- sao do newWe2002 e do ed.exe, que'
    Write-Host '  precisam de Qt6, MSVC e (os golden) de Xvfb e Wine. Ver a'
    Write-Host '  secao 2 de docs/PLAN-WINDOWS.md e a secao 5 de'
    Write-Host '  docs/PLAN-WTE-WINDOWS.md.'
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
        return
    }
    foreach ($a in $alvos) {
        Remove-Item $a.FullName -Force
        Write-Host ">> removido $($a.Name)"
    }
}

switch ($Alvo) {
    'help'         { Invoke-Help }
    'run-obocaman' { Invoke-RunObocaman }
    'run-lazarus'  { Invoke-RunLazarus }
    'fresh'        { Invoke-Fresh }
}
