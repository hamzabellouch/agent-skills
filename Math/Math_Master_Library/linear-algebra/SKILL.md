---
name: linear-algebra
description: "Solve linear algebra problems: matrices, determinants, systems, vector spaces, eigenvalues, diagonalization, SVD, orthogonality, least squares, inner products, linear transformations. Includes a Python helper script. Use for any matrix, vector space, or eigenvalue question."
---

# Linear Algebra

## Core computations
- Gaussian elimination -> RREF; rank = number of pivots; nullity = n - rank (rank-nullity theorem).
- Determinant: det(AB) = det A det B; det = product of eigenvalues; zero iff singular; cofactor expansion; 2x2 ad - bc.
- Inverse: A^{-1} = adj(A)/det A, or row-reduce [A | I]. Solve Ax = b with LU rather than inverting numerically.
- Eigen: det(A - lambda I) = 0; trace = sum of eigenvalues; A = P D P^{-1} if n independent eigenvectors; symmetric matrices have real eigenvalues and orthogonal eigenvectors (spectral theorem). Jordan form for defective cases. Cayley-Hamilton p(A) = 0.
- Orthogonality: Gram-Schmidt, QR; projection onto subspace P = A(A^T A)^{-1} A^T; least squares x = (A^T A)^{-1} A^T b (use QR/SVD for stability).
- SVD A = U S V^T: singular values sqrt(eig(A^T A)); low-rank approximation (Eckart-Young); pseudoinverse; condition number kappa = sigma_max/sigma_min.
- Positive definite: all eigenvalues > 0 <=> Cholesky exists <=> x^T A x > 0.
- Vector spaces: basis, dimension, span, linear independence, subspaces (column space, null space, row space, left null space - four fundamental subspaces).
- Linear maps: matrix w.r.t. basis, change of basis P^{-1} A P, kernel and image, similarity.
- Inner product spaces: Cauchy-Schwarz |<u,v>| <= ||u|| ||v||, triangle inequality, orthogonal complement.
- Advanced: tensor products, dual spaces, bilinear forms, Sylvester's law of inertia, matrix exponential e^{At} for ODEs, Perron-Frobenius, Krylov methods, PCA = SVD of centered data.

## Workflow
1. Identify the structure (square? symmetric? sparse?). 2. Choose the decomposition. 3. Verify with numeric computation. 4. Interpret geometrically.

## Script
`scripts/linalg_tools.py` - rank, nullspace, eigen decomposition with checks, SVD, least squares, projections. Run for a demo.
