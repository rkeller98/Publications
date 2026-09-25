"""Symbolic and numerical checks for the representation-coordinate extension."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "figures" / "data"
DATA.mkdir(parents=True, exist_ok=True)


def relerr(a: float, b: float) -> float:
    return abs(a - b) / max(1.0, abs(a), abs(b))


def symbolic_checks() -> None:
    c, s, d, dd = sp.symbols("c s d dd", real=True)
    Rm = sp.Matrix([[sp.cos(d), sp.sin(d)], [-sp.sin(d), sp.cos(d)]])
    Rp = sp.Matrix([[sp.cos(d), -sp.sin(d)], [sp.sin(d), sp.cos(d)]])
    assert sp.simplify(Rm * Rp) == sp.eye(2)

    x1, x2, dx1, dx2 = sp.symbols("x1 x2 dx1 dx2", real=True)
    x = sp.Matrix([x1, x2])
    dx = sp.Matrix([dx1, dx2])
    J = sp.Matrix([[0, -1], [1, 0]])
    direct = sp.diff(Rm, d) * dd * x + Rm * dx
    expected = Rm * dx - dd * J * Rm * x
    assert sp.simplify(direct - expected) == sp.zeros(2, 1)

    Ld, Lq, Lm, ide, iq, ie, kt = sp.symbols(
        "Ld Lq Lm id iq ie kt", real=True
    )
    psid, psiq = Ld * ide + Lm * ie, Lq * iq
    psia = psid - Lq * ide
    torque = kt * (psid * iq - psiq * ide)
    assert sp.expand(psia - ((Ld - Lq) * ide + Lm * ie)) == 0
    assert sp.expand(torque - kt * psia * iq) == 0

    iT, alpha, sign = sp.symbols("iT alpha sign", positive=True, real=True)
    zp = iT / sp.sqrt(2) * sp.exp(alpha)
    zq = sign * iT / sp.sqrt(2) * sp.exp(-alpha)
    assert sp.simplify(zp * zq - sign * iT**2 / 2) == 0
    diT, da = sp.symbols("diT da", real=True)
    dzp = sp.diff(zp, iT) * diT + sp.diff(zp, alpha) * da
    dzq = sp.diff(zq, iT) * diT + sp.diff(zq, alpha) * da
    assert sp.simplify(dzp - sp.exp(alpha) * (diT + iT * da) / sp.sqrt(2)) == 0
    assert sp.simplify(dzq - sign * sp.exp(-alpha) * (diT - iT * da) / sp.sqrt(2)) == 0


def steady_quantities(kind: str, i: np.ndarray) -> tuple[float, float, float, float]:
    rs, re, w, kt = 0.12, 0.22, 2.0, 3.0
    if kind == "SPM":
        ide, iq = i
        ld = lq = 0.32
        psid, psiq = 0.82 + ld * ide, lq * iq
        torque = kt * (psid * iq - psiq * ide)
        loss = rs * (ide**2 + iq**2)
        ud, uq = rs * ide - w * psiq, rs * iq + w * psid
        return torque, loss, math.hypot(ud, uq), math.hypot(psid, psiq)
    if kind == "IPMSM":
        ide, iq = i
        ld, lq = 0.45, 0.25
        psid, psiq = 0.78 + ld * ide, lq * iq
        torque = kt * (psid * iq - psiq * ide)
        loss = rs * (ide**2 + iq**2)
        ud, uq = rs * ide - w * psiq, rs * iq + w * psid
        return torque, loss, math.hypot(ud, uq), math.hypot(psid, psiq)
    ide, iq, ie = i
    if kind == "linear EESM":
        ld, lq, lm = 0.45, 0.25, 0.30
        psid, psiq = ld * ide + lm * ie, lq * iq
    else:
        # Smooth toy saturation/cross-saturation map.
        psid = 0.45 * ide + 0.30 * ie - 0.022 * ide**3 - 0.010 * ide * iq**2
        psiq = 0.25 * iq - 0.016 * iq**3 - 0.008 * ide**2 * iq
    torque = kt * (psid * iq - psiq * ide)
    loss = rs * (ide**2 + iq**2) + re * ie**2
    ud, uq, ue = rs * ide - w * psiq, rs * iq + w * psid, re * ie
    return torque, loss, math.sqrt(ud**2 + uq**2 + ue**2), math.hypot(psid, psiq)


def jacobian(fun, x: np.ndarray, h: float = 2e-6) -> np.ndarray:
    y0 = np.asarray(fun(x), dtype=float)
    out = np.empty((y0.size, x.size))
    for k in range(x.size):
        xp, xm = x.copy(), x.copy()
        xp[k] += h
        xm[k] -= h
        out[:, k] = (np.asarray(fun(xp)) - np.asarray(fun(xm))) / (2 * h)
    return out


def offdiag_energy(mats: list[np.ndarray], S: np.ndarray) -> float:
    total = 0.0
    for A in mats:
        T = S.T @ A @ S
        total += float(np.sum((T - np.diag(np.diag(T))) ** 2))
    return total


def approximate_joint_diagonalizer(mats: list[np.ndarray]) -> np.ndarray:
    S = np.eye(3)
    for _ in range(10):
        improved = False
        for p, q in ((0, 1), (0, 2), (1, 2)):
            best_val, best_G = offdiag_energy(mats, S), np.eye(3)
            for ang in np.linspace(-math.pi / 4, math.pi / 4, 361):
                G = np.eye(3)
                ca, sa = math.cos(ang), math.sin(ang)
                G[p, p] = G[q, q] = ca
                G[p, q], G[q, p] = -sa, sa
                val = offdiag_energy(mats, S @ G)
                if val < best_val:
                    best_val, best_G = val, G
            if not np.allclose(best_G, np.eye(3)):
                S = S @ best_G
                improved = True
        if not improved:
            break
    return S


def write_condition_maps() -> tuple[float, float]:
    ipm_rows: list[str] = []
    max_ipm = 0.0
    for ide in np.linspace(-1.6, 0.6, 45):
        for iq in np.linspace(0.08, 1.8, 42):
            x = np.array([ide, iq])
            J = jacobian(
                lambda q: np.array(
                    [steady_quantities("IPMSM", q)[0],
                     steady_quantities("IPMSM", q)[3]]
                ),
                x,
            )
            cond = float(np.linalg.cond(J))
            max_ipm = max(max_ipm, min(cond, 1e8))
            ipm_rows.append(f"{ide:.7f} {iq:.7f} {min(math.log10(cond), 5):.7f}")
    (DATA / "coordinate_condition_ipm.dat").write_text(
        "id iq logcond\n" + "\n".join(ipm_rows) + "\n", encoding="utf-8"
    )

    eesm_rows: list[str] = []
    max_eesm = 0.0
    for ide in np.linspace(-1.3, 1.0, 43):
        for iq in np.linspace(0.08, 1.8, 42):
            x = np.array([ide, iq, 0.85])
            J = jacobian(
                lambda q: np.array(steady_quantities("linear EESM", q)[:3]),
                x,
            )
            cond = float(np.linalg.cond(J))
            max_eesm = max(max_eesm, min(cond, 1e8))
            eesm_rows.append(f"{ide:.7f} {iq:.7f} {min(math.log10(cond), 5):.7f}")
    (DATA / "coordinate_condition_eesm.dat").write_text(
        "id iq logcond\n" + "\n".join(eesm_rows) + "\n", encoding="utf-8"
    )
    return max_ipm, max_eesm


def numeric_checks() -> None:
    cases = {
        "SPM": np.array([-0.25, 1.10]),
        "IPMSM": np.array([-0.45, 1.10]),
        "linear EESM": np.array([-0.35, 1.05, 0.90]),
        "saturated EESM": np.array([-0.35, 1.05, 0.90]),
    }
    print("case                    torque       loss    voltage       flux       cond")
    for name, point in cases.items():
        vals = steady_quantities(name, point)
        if point.size == 2:
            J = jacobian(
                lambda q: np.array([steady_quantities(name, q)[0],
                                    steady_quantities(name, q)[3]]),
                point,
            )
        else:
            J = jacobian(
                lambda q: np.array(steady_quantities(name, q)[:3]), point
            )
        print(
            f"{name:18s} {vals[0]:11.6f} {vals[1]:10.6f} "
            f"{vals[2]:10.6f} {vals[3]:10.6f} {np.linalg.cond(J):10.3f}"
        )

    # Linear EESM whitening, torque alignment, round trip, and invariants.
    i = cases["linear EESM"]
    rs, re, ld, lq, lm, w, kt = 0.12, 0.22, 0.45, 0.25, 0.30, 2.0, 3.0
    Rloss = np.diag([rs, rs, re])
    H = kt / 2 * np.array(
        [[0.0, ld - lq, 0.0], [ld - lq, 0.0, lm], [0.0, lm, 0.0]]
    )
    A = np.array([[rs, -w * lq, 0.0], [w * ld, rs, w * lm], [0, 0, re]])
    Q = A.T @ A
    c = np.array([(ld - lq) / math.sqrt(rs), lm / math.sqrt(re)])
    beta = np.linalg.norm(c)
    S = np.array(
        [[c[0] / beta, 0, c[1] / beta],
         [0, 1, 0],
         [-c[1] / beta, 0, c[0] / beta]]
    )
    W = np.diag(np.sqrt(np.diag(Rloss)))
    z = S @ W @ i
    i_back = np.linalg.solve(W, S.T @ z)
    assert np.linalg.norm(i - i_back) < 1e-12
    kappa = kt * beta / math.sqrt(rs)
    assert relerr(i @ H @ i, kappa * z[0] * z[1]) < 1e-12
    assert relerr(i @ Rloss @ i, z @ z) < 1e-12
    Qz = S @ np.linalg.solve(W, Q) @ np.linalg.solve(W, S.T)
    assert relerr(i @ Q @ i, z @ Qz @ z) < 1e-12

    iT = math.sqrt(2 * abs(z[0] * z[1]))
    alpha = 0.5 * math.log(abs(z[0] / z[1]))
    sign = math.copysign(1.0, z[0] * z[1])
    z_back = np.array(
        [iT / math.sqrt(2) * math.exp(alpha),
         sign * iT / math.sqrt(2) * math.exp(-alpha), z[2]]
    )
    assert np.linalg.norm(z - z_back) < 1e-12

    # Finite-difference check of the moving-frame derivative.
    x, dx, delta, ddelta, dt = np.array([0.7, -0.2]), np.array([0.3, 0.5]), .4, .8, 1e-7
    def rot(a: float) -> np.ndarray:
        return np.array([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]])
    numeric = (rot(delta + ddelta * dt) @ (x + dx * dt) - rot(delta) @ x) / dt
    J2 = np.array([[0.0, -1.0], [1.0, 0.0]])
    analytic = rot(delta) @ dx - ddelta * J2 @ rot(delta) @ x
    assert np.linalg.norm(numeric - analytic) < 2e-7

    Rhalf_inv = np.diag(1 / np.sqrt(np.diag(Rloss)))
    Ht, Qt = Rhalf_inv @ H @ Rhalf_inv, Rhalf_inv @ Q @ Rhalf_inv
    comm = Ht @ Qt - Qt @ Ht
    comm_rel = np.linalg.norm(comm, "fro") / (
        np.linalg.norm(Ht, "fro") * np.linalg.norm(Qt, "fro")
    )
    mats = [Ht / np.linalg.norm(Ht, "fro"), Qt / np.linalg.norm(Qt, "fro")]
    Sjd = approximate_joint_diagonalizer(mats)
    before, after = offdiag_energy(mats, np.eye(3)), offdiag_energy(mats, Sjd)
    assert after <= before + 1e-12
    max_ipm, max_eesm = write_condition_maps()
    print(f"round-trip current error: {np.linalg.norm(i-i_back):.3e}")
    print(f"hyperbolic inverse error: {np.linalg.norm(z-z_back):.3e}")
    print(f"moving-frame derivative error: {np.linalg.norm(numeric-analytic):.3e}")
    print(f"normalized commutator: {comm_rel:.6f}")
    print(f"AJD offdiag energy: {before:.6f} -> {after:.6f}")
    print(f"sampled max condition numbers: IPMSM={max_ipm:.3e}, EESM={max_eesm:.3e}")


if __name__ == "__main__":
    symbolic_checks()
    print("coordinate symbolic checks: PASS")
    numeric_checks()
    print("coordinate numerical checks: PASS")
