# Baseline migration matrix

This internal regression checklist records where every substantive result of
the preserved combined baseline is carried forward.

| Original topic | Destination | Regression check |
|---|---|---|
| Quadratic forms and axes | PSM sections 3--5 | Gram matrix and spectral form |
| Conic discriminant and three determinants | PSM section 4 | Signs kept distinct |
| SVD interpretation | PSM section 5; EESM section 4 | `lambda_i = sigma_i^2` |
| PMSM voltage ellipse and center | PSM sections 2--5 | Symbolic formulas retained |
| PMSM torque, MTPA, FW, MTPV | PSM section 6 | Special cases retained |
| Fixed-excitation slices | EESM section 3 | Congruent translated ellipses |
| Voltage cylinder and null space | EESM sections 3--4 | Rank two, one zero eigenvalue |
| EESM torque surface | EESM section 5 | Hyperbolic-cylinder classification |
| Copper-loss ellipsoid | EESM section 6 | Positive-definite loss metric |
| Minimum-loss operation | EESM section 6 | Lagrange relation and ray locus |
| Generalized eigenproblem | EESM section 6 | Loss whitening retained |
| Voltage-only MTPV unboundedness | EESM section 7 | Explicit null-line proof |
| Hidden numerical constraints | EESM section 8 | Domain-expansion test retained |
| Delaunay and isosurfaces | PSM section 7; EESM section 8 | Analytic/numeric roles separated |
| Five views of the PSM ellipse | PSM section 5 | Expansion, conic, inverse image, eigendecomposition, and SVD synthesized |
| Five views of the EESM cylinder | EESM sections 2--4 | Rank, null space, signature, SVD, and stacked slices synthesized |
| Geometric constrained optimization | PSM section 6; EESM sections 6--7 | Lagrange and KKT conditions developed from touching level sets |
| Loss whitening | EESM section 6 | Ellipsoid-to-sphere transformation shown explicitly |
| Counterfactual learning checks | PSM section 7; EESM sections 2, 4, 7, and 8 | Structural assumptions separated from parameter effects |

The files under `legacy/original_combined_paper/` and its ZIP archive remain
unchanged as the read-only technical baseline.

The pedagogical expansion is governed by
`docs/didactic_contract.md`; new papers inherit its checklist from
`paper_template/DIDACTIC_GUIDE.md`.
