# Publications

This repository contains two self-contained LaTeX papers and a reusable,
self-contained paper template.

## Repository layout

    papers/
      psm_voltage_geometry/       independent PSM publication
      eesm_voltage_geometry/      independent EESM publication
    paper_template/               complete basis for a new paper
    shared/                       reference source for the include bundle
    scripts/                      build, clean, and scaffolding commands
    build/                        generated intermediates
    output/pdf/                   exported final PDFs
    legacy/                       preserved original combined draft

Every directory below papers/ contains its own metadata, sections, figures,
publication framework, glossary, and bibliography. A paper can therefore be
copied out of this repository and compiled without shared/.

## Anatomy of a paper

    <paper>/
      main.tex                    document order
      metadata.tex                title, authors, date, abstract
      local.tex                   paper-only commands and styles
      includes/
        publications.sty          framework entry point
        config/                   packages and document configuration
        commands/                 mathematical and machine notation
        glossary/                 acronyms and symbols
        tikz/                     reusable TikZ and PGFPlots styles
        bibliography/             this paper's bibliography database
      sections/                   one file per section
      figures/                    source for local figures

## Create a new paper

From the repository root:

    .\scripts\new_paper.ps1 my_new_paper

This copies paper_template/ to papers/my_new_paper/. Then edit metadata.tex,
local.tex, sections/, figures/, and the local bibliography as needed. The
template itself compiles and contains a small working figure example. Its
DIDACTIC_GUIDE.md and docs/didactic_contract.md define the required learning
paper style.

## Build

Requirements:

- A current MiKTeX or TeX Live installation
- latexmk, LuaLaTeX, and Biber on PATH
- PowerShell 7 or Windows PowerShell 5.1

Build either paper from the repository root:

    .\scripts\build.ps1 psm_voltage_geometry
    .\scripts\build.ps1 eesm_voltage_geometry
    .\scripts\build_all.ps1

LuaLaTeX is the default. To use pdfLaTeX:

    .\scripts\build.ps1 psm_voltage_geometry pdflatex
    .\scripts\build_all.ps1 -Engine pdflatex

A paper can also be compiled directly from its own directory without setting
TEXINPUTS:

    cd .\papers\psm_voltage_geometry
    latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex

Intermediate files are written below build/<paper>/ by the repository scripts;
stable PDFs are exported to output/pdf/. Clean them with:

    .\scripts\clean.ps1
    .\scripts\clean.ps1 psm_voltage_geometry

## Independence and reuse

The include bundle is intentionally vendored into every paper. This gives each
publication a reproducible snapshot and removes hidden parent-directory
dependencies. Paper-specific definitions belong in local.tex, not in the
vendored framework.

The shared/ directory records the repository-level reference implementation.
The paper_template/includes/ directory is the starting snapshot used for new
papers. Existing papers remain stable when either reference is changed.

New acronyms use \newabbreviation in includes/glossary/acronyms.tex; symbols use
\newglossaryentry in includes/glossary/symbols.tex. Shared drawing styles
include axis main, constraint curve, principal axis, eigenvector, projection
line, operating point, feasible region, and coordinate vector.

The glossary uses the glossaries-extra no-index workflow. Bibliographies are
processed by Biber through Latexmk.
