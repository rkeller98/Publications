[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidatePattern('^[A-Za-z0-9_-]+$')]
    [string]$Name
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$templateDir = Join-Path $repoRoot 'paper_template'
$papersDir = Join-Path $repoRoot 'papers'
$targetDir = Join-Path $papersDir $Name

if (-not (Test-Path -LiteralPath $templateDir -PathType Container)) {
    throw "Paper template not found: $templateDir"
}
if (Test-Path -LiteralPath $targetDir) {
    throw "Paper already exists: $targetDir"
}

New-Item -ItemType Directory -Path $papersDir -Force | Out-Null
Copy-Item -LiteralPath $templateDir -Destination $targetDir -Recurse
Write-Host "Created self-contained paper: $targetDir"
Write-Host "Next: edit metadata.tex, local.tex, sections/, and figures/."
