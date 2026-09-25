# Recursive QP within a simplex

Integrated from `Recursive_QP_within_Simplex.zip`. Its single-file IEEE draft
was separated into metadata, local listing configuration, and paper content,
then connected to the global publication framework. Build it with:

    .\scripts\build.ps1 recursive_qp_within_simplex

The directory is self-contained. `metadata.tex` holds title, abstract, and
keywords; `local.tex` defines the MATLAB listing style; and
`sections/01_paper.tex` contains the body and solver listing.

It can also be compiled directly from this directory:

    latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex
