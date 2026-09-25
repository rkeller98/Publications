[CmdletBinding()]
param(
    [ValidateSet('lualatex', 'pdflatex')]
    [string]$Engine = 'lualatex'
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$papersDir = Join-Path $repoRoot 'papers'
$papers = Get-ChildItem -LiteralPath $papersDir -Directory |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'main.tex') -PathType Leaf } |
    Sort-Object Name |
    ForEach-Object { $_.Name }

foreach ($paper in $papers) {
    & (Join-Path $PSScriptRoot 'build.ps1') -Paper $paper -Engine $Engine
}
