"""Symbolic identities and randomized regression for the EESM whitepaper."""

from __future__ import annotations

import math
import random

import numpy as np
import sympy as sp


def symbolic_checks() -> None:
    Rs, Re, Ld, Lq, Le, w, kt, psi = sp.symbols(
        "Rs Re Ld Lq Le w kt psi", positive=True, finite=True
    )
    dL = Ld - Lq
    A = sp.Matrix([[Rs, -w * Lq, 0], [w * Ld, Rs, w * Le]])
    Q = sp.simplify(A.T * A)
    n = sp.Matrix([-w**2 * Lq * Le, -Rs * w * Le, Rs**2 + w**2 * Ld * Lq])
    assert sp.simplify(A * n) == sp.zeros(2, 1)
    assert Q == Q.T and sp.simplify(Q.det()) == 0

    H = kt / 2 * sp.Matrix([[0, dL, 0], [dL, 0, Le], [0, Le, 0]])
    lam = sp.symbols("lam")
    expected_char = lam * (lam**2 - kt**2 * (dL**2 + Le**2) / 4)
    assert sp.simplify(H.charpoly(lam).as_expr() - expected_char) == 0

    D = Rs**2 + w**2 * Ld * Lq
    icd = -psi * w**2 * Lq / D
    icq = -psi * Rs * w / D
    assert sp.simplify(Ld * icd**2 + Lq * icq**2 + psi * icd) == 0

    Hp = sp.Matrix(
        [[Rs**2 + w**2 * Ld**2, Rs * w * dL],
         [Rs * w * dL, Rs**2 + w**2 * Lq**2]]
    )
    b = sp.Matrix([w**2 * Ld * psi, Rs * w * psi])
    assert sp.simplify(-Hp.inv() * b - sp.Matrix([icd, icq])) == sp.zeros(2, 1)
    tan2 = sp.cancel(2 * Hp[0, 1] / (Hp[0, 0] - Hp[1, 1]))
    assert sp.simplify(tan2 - 2 * Rs / (w * (Ld + Lq))) == 0

    rs = sp.Rational(3, 2) * Rs
    ad, ae = dL / sp.sqrt(rs), Le / sp.sqrt(Re)
    beta = sp.sqrt(ad**2 + ae**2)
    S = sp.Matrix([[ad / beta, 0, ae / beta], [0, 1, 0], [-ae / beta, 0, ad / beta]])
    assert sp.simplify(S * S.T) == sp.eye(3)
    zpsi, zq, z0 = sp.symbols("zpsi zq z0", real=True)
    z = sp.Matrix([zpsi, zq, z0])
    y = sp.simplify(S.T * z)
    current = sp.diag(1 / sp.sqrt(rs), 1 / sp.sqrt(rs), 1 / sp.sqrt(Re)) * y
    loss = sp.simplify((current.T * sp.diag(rs, rs, Re) * current)[0])
    torque = sp.simplify((current.T * H * current)[0])
    kappa = sp.simplify(kt * beta / sp.sqrt(rs))
    expected_kappa = kt * sp.sqrt(dL**2 / rs**2 + Le**2 / (rs * Re))
    assert sp.simplify(kappa**2 - expected_kappa**2) == 0
    assert sp.simplify(loss - (zpsi**2 + zq**2 + z0**2)) == 0
    assert sp.simplify(torque - kappa * zpsi * zq) == 0

    Hbar = sp.diag(1 / sp.sqrt(rs), 1 / sp.sqrt(rs), 1 / sp.sqrt(Re)) * H * sp.diag(
        1 / sp.sqrt(rs), 1 / sp.sqrt(rs), 1 / sp.sqrt(Re)
    )
    spectral = Hbar.charpoly(lam).as_expr()
    expected_spectral = lam * (lam**2 - kappa**2 / 4)
    assert sp.simplify(spectral - expected_spectral) == 0
    Pmax = sp.symbols("Pmax", positive=True)
    assert sp.simplify((kappa / 2) * Pmax - expected_kappa * Pmax / 2) == 0
    xM, yM = dL / rs, Le / sp.sqrt(rs * Re)
    assert sp.simplify(kappa**2 / kt**2 - (xM**2 + yM**2)) == 0
    assert sp.limit(yM, Re, 0, dir="+") == sp.oo

    IP, Mreq = sp.symbols("IP Mreq", positive=True)
    psi_min = Mreq / (kt * IP)
    psi_max = Ld * IP
    assert sp.simplify(kt * psi_min * IP - Mreq) == 0
    assert sp.simplify(psi_max / Ld - IP) == 0
    assert sp.simplify(kt * IP * (psi_max - psi_min) - (kt * Ld * IP**2 - Mreq)) == 0

    sigma, gamma = sp.symbols("sigma gamma", real=True)
    salient_shape = sp.sin(gamma) * (1 + sigma * sp.cos(gamma))
    assert sp.simplify(sp.diff(salient_shape, gamma) - (
        sp.cos(gamma) + sigma * (2 * sp.cos(gamma) ** 2 - 1)
    )) == 0

    u, v, iT, alpha = sp.symbols("u v iT alpha", real=True)
    assert sp.expand(((u + v) / sp.sqrt(2)) * ((u - v) / sp.sqrt(2))) == (u**2 - v**2) / 2
    hyper_loss = sp.simplify((iT * sp.cosh(alpha)) ** 2 + (iT * sp.sinh(alpha)) ** 2)
    assert sp.simplify(hyper_loss - iT**2 * sp.cosh(2 * alpha)) == 0

    eta, chi, c = sp.symbols("eta chi c", positive=True, real=True)
    J = eta + (1 + chi**2) / eta
    circle = (eta - c / 2) ** 2 + chi**2 - (c**2 / 4 - 1)
    assert sp.simplify(circle.subs(c, J)) == 0

    a, b = sp.symbols("a b", real=True)
    square = sp.expand((a + sp.I * b) ** 2)
    assert sp.re(square) == a**2 - b**2
    assert sp.im(square) == 2 * a * b


def numeric_regression(trials: int = 250, seed: int = 260925) -> None:
    rng = random.Random(seed)
    worst = {"loss": 0.0, "torque": 0.0, "voltage": 0.0, "capability": 0.0,
             "salient_psm": 0.0}

    def relerr(a: float, b: float) -> float:
        return abs(a - b) / max(1.0, abs(a), abs(b))

    for _ in range(trials):
        Rs = rng.uniform(0.03, 1.2)
        Re = rng.uniform(0.05, 2.0)
        Ld = rng.uniform(0.2, 2.0)
        Lq = rng.uniform(0.2, 2.0)
        Le = rng.uniform(0.1, 1.8)
        omega = rng.uniform(-5.0, 5.0)
        if abs(omega) < 0.05:
            omega = 0.05
        poles = rng.randint(1, 6)
        kt = 1.5 * poles
        i = np.array([rng.uniform(-3, 3) for _ in range(3)], dtype=float)

        rs = 1.5 * Rs
        R = np.diag([rs, rs, Re])
        dL = Ld - Lq
        H = kt / 2 * np.array([[0, dL, 0], [dL, 0, Le], [0, Le, 0]], dtype=float)
        A = np.array([[Rs, -omega * Lq, 0], [omega * Ld, Rs, omega * Le]], dtype=float)
        Q = A.T @ A

        a = np.array([dL / math.sqrt(rs), Le / math.sqrt(Re)])
        beta = np.linalg.norm(a)
        S = np.array([[a[0] / beta, 0, a[1] / beta], [0, 1, 0], [-a[1] / beta, 0, a[0] / beta]])
        y = np.diag(np.sqrt(np.diag(R))) @ i
        z = S @ y
        kappa = kt * beta / math.sqrt(rs)

        p0, m0, u0 = i @ R @ i, i @ H @ i, i @ Q @ i
        p1 = z @ z
        m1 = kappa * z[0] * z[1]
        B = A @ np.diag(1 / np.sqrt(np.diag(R))) @ S.T
        u1 = z @ (B.T @ B) @ z
        worst["loss"] = max(worst["loss"], relerr(p0, p1))
        worst["torque"] = max(worst["torque"], relerr(m0, m1))
        worst["voltage"] = max(worst["voltage"], relerr(u0, u1))

        Hbar = np.diag(1 / np.sqrt(np.diag(R))) @ H @ np.diag(1 / np.sqrt(np.diag(R)))
        spectral_capability = np.linalg.eigvalsh(Hbar)[-1]
        worst["capability"] = max(
            worst["capability"], relerr(spectral_capability, kappa / 2)
        )

        psi_pm = rng.uniform(0.1, 2.0)
        IP = rng.uniform(0.2, 4.0)
        sigma = dL * IP / psi_pm
        if abs(sigma) < 1e-10:
            closed_factor = 1.0
        else:
            cstar = (-1 + math.sqrt(1 + 8 * sigma**2)) / (4 * sigma)
            closed_factor = math.sqrt(max(0.0, 1 - cstar**2)) * (1 + sigma * cstar)
        angles = np.linspace(0.0, math.pi, 20001)
        sampled_factor = float(np.max(np.sin(angles) * (1 + sigma * np.cos(angles))))
        worst["salient_psm"] = max(
            worst["salient_psm"], relerr(closed_factor, sampled_factor)
        )

        if p0 > 1e-12:
            x = y / math.sqrt(p0)
            Qbar = np.diag(1 / np.sqrt(np.diag(R))) @ Q @ np.diag(1 / np.sqrt(np.diag(R)))
            tau, nu = x @ Hbar @ x, x @ Qbar @ x
            assert relerr(m0, p0 * tau) < 1e-11
            assert relerr(u0, p0 * nu) < 1e-11

    assert max(value for name, value in worst.items() if name != "salient_psm") < 1e-10, worst
    assert worst["salient_psm"] < 1e-7, worst
    print(f"random trials: {trials}")
    for name, value in worst.items():
        print(f"max relative {name} error: {value:.3e}")


if __name__ == "__main__":
    symbolic_checks()
    print("symbolic checks: PASS")
    numeric_regression()
    print("numeric regression: PASS")
