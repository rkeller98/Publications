[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidatePattern('^[A-Za-z0-9_-]+$')]
    [string]$Paper
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$buildRoot = Join-Path $repoRoot 'build'
$target = if ($Paper) { Join-Path $buildRoot $Paper } else { $buildRoot }

if (-not (Test-Path -LiteralPath $target)) {
    Write-Host "Nothing to clean: $target"
    exit 0
}

$resolvedBuild = [IO.Path]::GetFullPath($buildRoot).TrimEnd('\')
$resolvedTarget = [IO.Path]::GetFullPath($target).TrimEnd('\')
if ($resolvedTarget -ne $resolvedBuild -and -not $resolvedTarget.StartsWith("$resolvedBuild\", [StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to remove a path outside the build directory: $resolvedTarget"
}

Remove-Item -LiteralPath $resolvedTarget -Recurse -Force
Write-Host "Removed $resolvedTarget"
