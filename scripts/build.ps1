[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidatePattern('^[A-Za-z0-9_-]+$')]
    [string]$Paper,

    [Parameter(Position = 1)]
    [ValidateSet('lualatex', 'pdflatex')]
    [string]$Engine = 'lualatex'
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$paperDir = Join-Path $repoRoot "papers/$Paper"
$mainFile = Join-Path $paperDir 'main.tex'
$buildDir = Join-Path $repoRoot "build/$Paper"
$outputDir = Join-Path $repoRoot 'output/pdf'

if (-not (Test-Path -LiteralPath $mainFile -PathType Leaf)) {
    throw "Unknown paper '$Paper': $mainFile does not exist."
}
if (-not (Get-Command latexmk -ErrorAction SilentlyContinue)) {
    throw 'latexmk was not found on PATH.'
}
if (-not (Get-Command biber -ErrorAction SilentlyContinue)) {
    throw 'biber was not found on PATH.'
}

New-Item -ItemType Directory -Force -Path $buildDir, $outputDir | Out-Null
Push-Location $paperDir
$previousLcAll = $env:LC_ALL
$previousLcCtype = $env:LC_CTYPE
$previousLang = $env:LANG
Remove-Item Env:LC_ALL -ErrorAction SilentlyContinue
Remove-Item Env:LC_CTYPE -ErrorAction SilentlyContinue
Remove-Item Env:LANG -ErrorAction SilentlyContinue
try {
    $engineOption = if ($Engine -eq 'lualatex') { '-lualatex' } else { '-pdf' }
    $latexmkArgs = @(
        $engineOption,
        '-interaction=nonstopmode',
        '-halt-on-error',
        '-file-line-error',
        "-outdir=$buildDir",
        "-auxdir=$buildDir",
        'main.tex'
    )
    & latexmk @latexmkArgs
    if ($LASTEXITCODE -ne 0) {
        throw "LaTeX build failed for '$Paper'. See $buildDir/main.log."
    }
}
finally {
    $env:LC_ALL = $previousLcAll
    $env:LC_CTYPE = $previousLcCtype
    $env:LANG = $previousLang
    Pop-Location
}

$finalPdf = Join-Path $outputDir "$Paper.pdf"
Copy-Item -LiteralPath (Join-Path $buildDir 'main.pdf') -Destination $finalPdf -Force
Write-Host "Built $buildDir/main.pdf"
Write-Host "Exported $finalPdf"
