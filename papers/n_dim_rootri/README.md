# N-dimensional RooTri paper

Integrated from `N_dim_RooTri.zip`. The paper uses the repository publication
framework while retaining its MATLAB listings, TikZ illustration, and local
bibliography. Build it from the repository root with:

    .\scripts\build.ps1 n_dim_rootri

The directory is self-contained. Paper text is under `sections/`, the Delaunay
figure under `figures/`, MATLAB code under `listings/`, and bibliography data
under `includes/bibliography/`.

It can also be compiled directly from this directory:

    latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex
