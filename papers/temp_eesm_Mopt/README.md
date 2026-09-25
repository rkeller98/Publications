# Self-contained paper template

Copy this entire directory to papers/<paper-name> or run:

    .\scripts\new_paper.ps1 <paper-name>

The copied paper has no runtime dependency on the repository-level shared/
directory.

## Where content belongs

- main.tex: document order only
- metadata.tex: title, authors, date, abstract, and output switches
- local.tex: definitions used by this paper only
- sections/: one source file per logical section
- figures/: TikZ/PGFPlots figures and local figure data
- includes/: the paper's private LaTeX framework, glossary, and bibliography

Compile from inside the paper directory:

    latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex

Use \showglossaryfalse or \showbibliographyfalse in metadata.tex when a paper
does not need those components.
