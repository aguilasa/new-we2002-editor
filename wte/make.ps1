<#
.SYNOPSIS
  Build e verificacao do projeto Lazarus no WINDOWS -- o irmao do `wte/Makefile`.

.DESCRIPTION
  O `wte/Makefile` e GNU make + bash, e nenhum dos dois vem com o Windows.
  Este script cobre os alvos que fazem sentido aqui e recusa os que nao fazem,
  dizendo por que -- alvo que finge ter rodado e pior do que alvo ausente, que
  e a regra que o `check` do Makefile ja segue.

  DELIBERADAMENTE SEPARADO do `newWe2002`, como o Makefile: sao dois produtos,
  com dois ciclos de verificacao. Ver `wte/README.md`, decisao 2, e
  `/docs/PLAN-WTE-WINDOWS.md`.

  Uso:
      .\make.ps1                 lista os alvos
      .\make.ps1 build
      .\make.ps1 run  -Imagem C:\caminho\copia.bin
      .\make.ps1 test
      .\make.ps1 check
      .\make.ps1 icon
      .\make.ps1 clean

  O que o Makefile tem e este script NAO tem, por nao existir alvo aqui:

    assets     e `ln -sfn`. No Windows a pasta do Obocaman vai onde o
               `wte_datafiles.pas` procura -- ver o alvo `assets` abaixo, que
               explica os tres lugares em vez de criar link.
    run-98     e Xvfb. No Windows nao ha `:98`; a janela abre no desktop.
    install    e o layout do freedesktop (`share/applications`, `hicolor`).
               Nao ha equivalente no Windows, e empacotar ficou de fora por
               decisao (WTE-TASK-39).
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('help', 'build', 'run', 'assets', 'test', 'check', 'icon',
                 'clean', 'distclean')]
    [string]$Alvo = 'help',

    # Imagem de CD passada ao `run`. O argumento e opcional no app tambem.
    [string]$Imagem,

    # Argumentos extras repassados ao binario no `run`.
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Resto
)

$ErrorActionPreference = 'Stop'

$WTE  = $PSScriptRoot
$ROOT = Split-Path $WTE -Parent
$LPI  = Join-Path $WTE 'wte.lpi'
$BIN  = Join-Path $WTE 'build\wte.exe'

# ---------------------------------------------------------------- ambiente --
#
# As tres ferramentas externas, cada uma com um jeito proprio de nao estar la.

function Get-Lazbuild {
    # `lazbuild` raramente esta no PATH no Windows: o instalador nao o poe.
    # `WTE_LAZBUILD` ganha de tudo; depois o PATH; depois os lugares onde o
    # instalador oficial e o fpcupdeluxe costumam deixar a arvore.
    if ($env:WTE_LAZBUILD) {
        if (-not (Test-Path $env:WTE_LAZBUILD)) {
            throw "WTE_LAZBUILD aponta para $($env:WTE_LAZBUILD), que nao existe."
        }
        return $env:WTE_LAZBUILD
    }
    $noPath = Get-Command lazbuild -ErrorAction SilentlyContinue
    if ($noPath) { return $noPath.Source }
    foreach ($c in @('C:\lazarus\lazbuild.exe',
                     "$env:LOCALAPPDATA\Lazarus\lazbuild.exe",
                     'C:\fpcupdeluxe\lazarus\lazbuild.exe')) {
        if (Test-Path $c) { return $c }
    }
    throw @'
lazbuild nao encontrado. Instale o Lazarus:
    winget install --id Lazarus.Lazarus --exact
ou aponte WTE_LAZBUILD para o executavel.
'@
}

function Get-LazarusDir {
    # A ARVORE (a que contem `lcl\` e `components\lazutils\lazversion.pas`),
    # que e o que o `check_lcl_props.py` quer em `WTE_LAZARUS_DIR`.
    if ($env:WTE_LAZARUS_DIR) { return $env:WTE_LAZARUS_DIR }
    $laz = Get-Lazbuild
    return (Split-Path $laz -Parent)
}

function Get-FpcDir {
    # O DIRETORIO do `fpc.exe`, para entrar no PATH.
    #
    # NAO E DETALHE. Treze testes de `tools/` compilam Pascal de verdade --
    # `test_camada_dados.pas`, `test_render.pas`, `test_bmp.pas`,
    # `test_mcr.pas`, `test_ml.pas`, `test_preco.pas`, os offsets -- e todos
    # procuram `fpc` com `shutil.which`. O instalador do Lazarus no Windows
    # NAO poe o `fpc` no PATH, entao sem esta funcao os treze PULAM dizendo
    # "sem fpc -- ... NAO foi compilado nesta execucao". Pulo honesto, mas e
    # a camada de dados inteira deixando de ser medida.
    if ($env:WTE_FPC) { return (Split-Path $env:WTE_FPC -Parent) }
    $noPath = Get-Command fpc -ErrorAction SilentlyContinue
    if ($noPath) { return (Split-Path $noPath.Source -Parent) }
    $arvore = try { Get-LazarusDir } catch { $null }
    if ($arvore) {
        $c = Get-ChildItem (Join-Path $arvore 'fpc') -Filter 'fpc.exe' `
             -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($c) { return $c.Directory.FullName }
    }
    return $null
}

function Get-Bash {
    # NAO e `bash` sem caminho. `C:\Windows\System32\bash.exe` e o atalho do
    # WSL, e o `CreateProcess` procura em System32 ANTES do PATH -- por o Git
    # for Windows na frente do PATH nao adianta. Ver a nota em
    # `tools/test_roteiro.py`.
    if ($env:WTE_BASH) { return $env:WTE_BASH }
    foreach ($c in @('C:\Program Files\Git\bin\bash.exe',
                     'C:\Program Files (x86)\Git\bin\bash.exe')) {
        if (Test-Path $c) { return $c }
    }
    return $null
}

function Get-Python {
    foreach ($n in @('python', 'python3', 'py')) {
        $c = Get-Command $n -ErrorAction SilentlyContinue
        if ($c) { return $c.Source }
    }
    throw 'python nao encontrado no PATH.'
}

# O `WTE_BASH` vale para todo o processo filho: as ferramentas o leem sozinhas.
$bash = Get-Bash
if ($bash) {
    $env:WTE_BASH = $bash

    # `LC_ALL` NAO E ENFEITE. O bash do Git for Windows nasce sem locale
    # quando o pai e o PowerShell, e ai o `grep -P` do MSYS recusa:
    #
    #     grep: -P supports only unibyte and UTF-8 locales
    #
    # saindo 2. Os scripts usam `grep -qP` para decidir se a linha de um trio
    # (roteiro, rom, modo) ja esta no `golden.tsv`; com a recusa a condicao da
    # sempre falsa, a linha velha nunca sai, e a decisao ACRESCENTA onde
    # deveria SUBSTITUIR -- o TSV fica com a mesma corrida duas vezes e o
    # `check_golden.py` passa a ler duas datas para a mesma coisa.
    #
    # Nao se conserta no script: quem esta errado e o ambiente. Medido em
    # 2026-08-26 (grep 3.0 do Git for Windows).
    if (-not $env:LC_ALL) { $env:LC_ALL = 'C.UTF-8' }
}

# O `fpc` no PATH, pela razao que a `Get-FpcDir` explica.
$fpcDir = Get-FpcDir
if ($fpcDir -and ($env:PATH -notlike "*$fpcDir*")) {
    $env:PATH = "$fpcDir;$env:PATH"
}

# E a arvore do Lazarus, que o `check_lcl_props.py` procura.
if (-not $env:WTE_LAZARUS_DIR) {
    $d = try { Get-LazarusDir } catch { $null }
    if ($d) { $env:WTE_LAZARUS_DIR = $d }
}

# ------------------------------------------------------------------- alvos --

function Invoke-Help {
    Write-Host 'Alvos:'
    Write-Host '  build      lazbuild wte.lpi -> build\wte.exe'
    Write-Host '  run        roda o binario (-Imagem <caminho> e opcional)'
    Write-Host '  assets     diz ONDE por a pasta do Obocaman (nao cria link)'
    Write-Host '  test       unittest de tools\test_*.py'
    Write-Host '  check      test + --check de todos os geradores de tools\'
    Write-Host '  icon       redesenha os 7 PNG de packaging\icons\ (sem --check)'
    Write-Host '  clean      remove build\'
    Write-Host '  distclean  clean'
    Write-Host ''
    Write-Host "Binario: $BIN"
    Write-Host ''
    Write-Host 'Ambiente encontrado:'
    $laz = try { Get-Lazbuild } catch { '<ausente>' }
    Write-Host "  lazbuild        $laz"
    Write-Host "  arvore Lazarus  $(try { Get-LazarusDir } catch { '<ausente>' })"
    Write-Host "  fpc             $(if ($fpcDir) { Join-Path $fpcDir 'fpc.exe' } else { '<ausente -- 13 testes pulam>' })"
    $gpp = Get-Command g++ -ErrorAction SilentlyContinue
    Write-Host "  g++             $(if ($gpp) { $gpp.Source } else { '<ausente -- o confronto bilingue dos offsets pula>' })"
    Write-Host "  bash            $(if ($bash) { $bash } else { '<ausente -- instale o Git for Windows>' })"
    Write-Host "  python          $(try { Get-Python } catch { '<ausente>' })"
    Write-Host ''
    Write-Host 'O que este script nao tem, e por que: veja o cabecalho.'
}

function Invoke-Build {
    $laz = Get-Lazbuild
    Write-Host ">> $laz $LPI"
    & $laz $LPI
    if ($LASTEXITCODE -ne 0) { throw "lazbuild saiu $LASTEXITCODE" }
    Write-Host ">> $BIN"
}

function Invoke-Run {
    Invoke-Build
    $argumentos = @()
    if ($Imagem) { $argumentos += $Imagem }
    if ($Resto)  { $argumentos += $Resto }
    # `-Wait` porque o `.exe` e do subsistema GUI: sem isso o PowerShell
    # devolve o prompt na hora e a saida de `--help`/`--list` chega depois,
    # embaralhada com ele. Ver a nota de `Linha` em `src/wtemain.pas`.
    if ($argumentos.Count -gt 0) {
        Start-Process -FilePath $BIN -ArgumentList $argumentos -Wait -NoNewWindow
    } else {
        Start-Process -FilePath $BIN -Wait -NoNewWindow
    }
}

function Invoke-Assets {
    # O Makefile cria um symlink; aqui nao ha alvo a criar, ha lugar a dizer.
    # A ordem de busca e a do `src/wte_datafiles.pas`, e ela nao muda com o
    # sistema -- o que muda e que no Windows o caminho 2 e uma PASTA de
    # verdade (copiada ou juncao), nao um symlink de `make`.
    $origem = Join-Path $ROOT 'we-team-editor'
    $destino = Join-Path $WTE 'assets'
    Write-Host 'A pasta do editor do Obocaman nao e versionada (binario de'
    Write-Host 'terceiro sem licenca -- 198 .bmp e o data\dat.bin). O app a'
    Write-Host 'procura, nesta ordem:'
    Write-Host ''
    Write-Host '  1. no diretorio que WTE_ASSETS_DIR apontar'
    Write-Host "  2. em $destino"
    Write-Host "  3. em $(Join-Path $WTE 'share\we2002Lazarus')"
    Write-Host ''
    if (Test-Path (Join-Path $origem 'image')) {
        Write-Host "Ha uma copia em $origem. Para usa-la sem copiar de novo:"
        Write-Host "  cmd /c mklink /J `"$destino`" `"$origem`""
    } else {
        Write-Host "Nao ha $origem neste disco."
        Write-Host 'Traga a pasta da maquina onde o editor original roda -- a'
        Write-Host 'PASTA INTEIRA, nao so o .exe: sao os bitmaps e o dat.bin'
        Write-Host 'que a versao Lazarus desenha.'
    }
    Write-Host ''
    foreach ($c in @($env:WTE_ASSETS_DIR, $destino,
                     (Join-Path $WTE 'share\we2002Lazarus'))) {
        if ($c -and (Test-Path (Join-Path $c 'data\dat.bin'))) {
            $n = (Get-ChildItem (Join-Path $c 'image') -Recurse -Filter *.bmp `
                  -ErrorAction SilentlyContinue).Count
            Write-Host ">> achado em $c -- $n bitmap(s), data\dat.bin ok"
            return
        }
    }
    Write-Host '>> nenhum dos tres tem data\dat.bin -- o app abre e avisa.'
}

function Invoke-Test {
    $py = Get-Python
    $testes = Get-ChildItem (Join-Path $WTE 'tools\test_*.py') `
              -ErrorAction SilentlyContinue
    if (-not $testes) {
        Write-Host 'AVISO: nenhum teste de ferramenta em tools\ -- nada medido.'
        return
    }
    if (-not $bash) {
        Write-Host 'AVISO: sem bash. Os testes que dirigem roteiro.sh e'
        Write-Host '       check_golden.sh vao falhar. Instale o Git for'
        Write-Host '       Windows ou aponte WTE_BASH.'
    }
    Push-Location (Join-Path $WTE 'tools')
    try {
        & $py -m unittest discover -p 'test_*.py'
        if ($LASTEXITCODE -ne 0) { throw "unittest saiu $LASTEXITCODE" }
    } finally { Pop-Location }
}

function Invoke-Check {
    Invoke-Test
    $py = Get-Python
    # Mesma regra do Makefile: `tools\test_*.py` sao testes de ferramenta, nao
    # geradores -- nao aceitam --check e saem daqui pelo filtro.
    #
    # E MAIS UM AQUI: o `make_icon.py`. Ele NAO TEM `--check` (decisao herdada
    # do `newWe2002` -- a saida do PIL nao e byte-deterministica entre versoes
    # do Pillow, e guard que quebra a cada atualizacao e pior do que nenhum).
    # Passar `--check` a ele nao e conferir: ele ignora o argumento e
    # REDESENHA os sete PNG. Medido em 2026-08-26 -- quatro icones commitados
    # voltaram modificados de um alvo que se chama `check`. Quem quiser
    # redesenhar chama `make.ps1 icon`, e olha o resultado.
    $geradores = Get-ChildItem (Join-Path $WTE 'tools\*.py') |
                 Where-Object { $_.Name -notlike 'test_*' -and
                                $_.Name -ne 'make_icon.py' }
    if (-not $geradores) {
        Write-Host 'AVISO: nenhum gerador em tools\ ainda -- nada medido.'
        return
    }
    if (-not $env:WTE_LAZARUS_DIR) { $env:WTE_LAZARUS_DIR = Get-LazarusDir }
    # NAO ha caso especial aqui, e nao deve haver. Gerador que nao pode medir
    # diz `PULADO` e sai 0 por conta propria -- e o que o `check_lcl_combo.py`
    # sempre fez e o que o `check_lcl_props.py` passou a fazer quando a LCL do
    # disco nao e a versao pinada. Quem sabe se mediu e a ferramenta; este
    # laco so conta.
    $falhou = @()
    $pulados = @()
    foreach ($g in $geradores) {
        Write-Host ">> $($g.Name) --check"
        $saida = & $py $g.FullName --check 2>&1
        $saida | ForEach-Object { Write-Host $_ }
        if ($LASTEXITCODE -ne 0) {
            $falhou += "$($g.Name) [exit $LASTEXITCODE]"
        } elseif (($saida | Out-String) -match 'PULADO') {
            $pulados += $g.Name
        }
    }
    Write-Host ''
    if ($pulados) {
        Write-Host "PULADOS (a ferramenta disse por que): $($pulados.Count)"
        $pulados | ForEach-Object { Write-Host "  $_" }
        Write-Host ''
    }
    if ($falhou) {
        Write-Host "FALHOU: $($falhou.Count) de $($geradores.Count)"
        $falhou | ForEach-Object { Write-Host "  $_" }
        Write-Host ''
        Write-Host 'Antes de tratar como regressao, veja a secao 5 de'
        Write-Host 'docs/PLAN-WTE-WINDOWS.md: a maioria dos geradores le o'
        Write-Host '.exe do Obocaman, que nao esta versionado.'
        throw "check reprovou em $($falhou.Count) gerador(es)"
    }
    $verdes = $geradores.Count - $pulados.Count
    Write-Host ">> $verdes de $($geradores.Count) gerador(es) conferidos, nenhum divergiu"
}

function Invoke-Icon {
    $py = Get-Python
    & $py (Join-Path $WTE 'tools\make_icon.py')
    if ($LASTEXITCODE -ne 0) { throw "make_icon.py saiu $LASTEXITCODE" }
    Write-Host '>> olhe o resultado: o icone e a unica coisa gerada aqui que'
    Write-Host '   teste nenhum julga.'
}

function Invoke-Clean {
    $b = Join-Path $WTE 'build'
    if (Test-Path $b) { Remove-Item $b -Recurse -Force }
    Write-Host ">> removido $b"
}

switch ($Alvo) {
    'help'      { Invoke-Help }
    'build'     { Invoke-Build }
    'run'       { Invoke-Run }
    'assets'    { Invoke-Assets }
    'test'      { Invoke-Test }
    'check'     { Invoke-Check }
    'icon'      { Invoke-Icon }
    'clean'     { Invoke-Clean }
    'distclean' { Invoke-Clean }
}
