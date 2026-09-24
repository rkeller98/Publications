[CmdletBinding()]
param(
    [ValidateSet('lualatex', 'pdflatex')]
    [string]$Engine = 'lualatex'
)

$ErrorActionPreference = 'Stop'
$papers = @('psm_voltage_geometry', 'eesm_voltage_geometry')
foreach ($paper in $papers) {
    & (Join-Path $PSScriptRoot 'build.ps1') -Paper $paper -Engine $Engine
}
