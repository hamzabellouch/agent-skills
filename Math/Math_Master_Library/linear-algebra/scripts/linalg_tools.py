#!/usr/bin/env python3
"""Linear algebra helpers (numpy/scipy)."""
import numpy as np
from scipy import linalg as la

def rank(A, tol=1e-10): return int(np.linalg.matrix_rank(A, tol))
def nullspace(A): return la.null_space(A)
def colspace(A): return la.orth(A)
def eig_report(A):
    w, V = np.linalg.eig(A)
    err = np.linalg.norm(A @ V - V @ np.diag(w))
    return w, V, err
def svd_report(A):
    U, s, Vt = np.linalg.svd(A); return U, s, Vt, np.linalg.cond(A)
def least_squares(A, b):
    x, res, rk, sv = np.linalg.lstsq(A, b, rcond=None); return x, np.linalg.norm(A @ x - b)
def project(A, b):
    Q, _ = np.linalg.qr(A); return Q @ (Q.T @ b)
def low_rank(A, k):
    U, s, Vt = np.linalg.svd(A, full_matrices=False); return (U[:, :k] * s[:k]) @ Vt[:k]

if __name__ == "__main__":
    A = np.array([[2., 1., 1.], [1., 3., 2.], [1., 0., 0.]])
    w, V, err = eig_report(A); print("eigenvalues:", np.round(w, 4), "residual:", f"{err:.1e}")
    print("rank:", rank(A), " det:", round(np.linalg.det(A), 4), " trace:", np.trace(A), " sum eig:", round(w.sum().real, 4))
    B = np.array([[1., 2.], [2., 4.], [3., 6.]]); print("nullspace dim of B^T:", nullspace(B.T).shape[1])
    X = np.c_[np.ones(5), np.arange(5)]; y = np.array([1.1, 2.9, 5.2, 7.1, 8.8])
    print("least squares fit:", np.round(least_squares(X, y)[0], 4))
    print("rank-1 approx error:", round(np.linalg.norm(A - low_rank(A, 1)), 4))
