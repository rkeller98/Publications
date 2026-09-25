"""Reproducible dynamic-geometry checks and toy EESM trajectory data.

The waypoint searches are deliberately small and deterministic.  They verify
the paper's geometric hypotheses; they are not claimed as globally optimal
control solvers.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "figures" / "data"
DATA.mkdir(parents=True, exist_ok=True)

LD, LQ, LM, LF = 0.42, 0.24, 0.12, 1.05
RS, RF, OMEGA = 0.16, 0.12, 0.75
US, UF, KT = 1.30, 0.32, 3.0
L = np.array([[LD, 0.0, LM], [0.0, LQ, 0.0], [LM, 0.0, LF]])
R = np.diag([RS, RS, RF])
C = np.array([[0.0, -OMEGA, 0.0], [OMEGA, 0.0, 0.0], [0.0, 0.0, 0.0]])
A_SYS = -np.linalg.solve(L, R + C @ L)
B_SYS = np.linalg.inv(L)
S = np.diag([US * US, US * US, UF * UF])
D = np.diag([1.0 / US, 1.0 / US, 1.0 / UF]) @ L
G = L.T @ np.linalg.inv(S) @ L

IA = np.array([0.05, 0.45, 0.55])
IB = np.array([0.35, 1.25, 1.10])


def torque(i: np.ndarray) -> float:
    return KT * i[1] * ((LD - LQ) * i[0] + LM * i[2])


def drift_voltage(i: np.ndarray) -> np.ndarray:
    return (R + C @ L) @ i


def voltage(i: np.ndarray, di: np.ndarray) -> np.ndarray:
    return L @ di + drift_voltage(i)


def utilization(u: np.ndarray) -> float:
    return max(float(np.linalg.norm(u[:2]) / US), float(abs(u[2]) / UF))


def segment_feasible(a: np.ndarray, b: np.ndarray, duration: float) -> bool:
    if duration <= 0.0:
        return False
    di = (b - a) / duration
    # Voltage is affine along a linear-current segment.  A norm and an
    # absolute value are convex, so their maxima occur at an endpoint.
    for s in (0.0, 1.0):
        if utilization(voltage((1.0 - s) * a + s * b, di)) > 1.0 + 2e-10:
            return False
    return True


def min_segment_time(a: np.ndarray, b: np.ndarray) -> float:
    if np.linalg.norm(b - a) < 1e-12:
        return 0.0
    grid = np.geomspace(1e-4, 80.0, 150)
    feasible = [t for t in grid if segment_feasible(a, b, float(t))]
    if not feasible:
        return math.inf
    hi = float(feasible[0])
    lo = hi / (grid[1] / grid[0])
    for _ in range(55):
        mid = 0.5 * (lo + hi)
        if segment_feasible(a, b, mid):
            hi = mid
        else:
            lo = mid
    return hi * 1.000002


def path_metrics(points: np.ndarray) -> tuple[float, float, float, list[float]]:
    total_t = total_e = peak_u = 0.0
    durations: list[float] = []
    for a, b in zip(points[:-1], points[1:]):
        dt = min_segment_time(a, b)
        if not np.isfinite(dt):
            return math.inf, math.inf, math.inf, []
        durations.append(dt)
        total_t += dt
        total_e += dt / 3.0 * (
            float(a @ R @ a) + float(a @ R @ b) + float(b @ R @ b)
        )
        di = (b - a) / dt if dt else np.zeros(3)
        for s in np.linspace(0.0, 1.0, 81):
            peak_u = max(peak_u, utilization(voltage((1 - s) * a + s * b, di)))
    return total_t, total_e, peak_u, durations


def monotone_torque(points: np.ndarray) -> bool:
    ma, mb = torque(IA), torque(IB)
    last = ma
    for a, b in zip(points[:-1], points[1:]):
        for s in np.linspace(0.0, 1.0, 25)[1:]:
            m = torque((1 - s) * a + s * b)
            if m < last - 3e-3 or m < ma - 1e-6 or m > mb + 1e-6:
                return False
            last = m
    return True


def search(seed: np.ndarray, objective: str, time_cap: float | None = None) -> np.ndarray:
    rng = np.random.default_rng(20260925 if objective == "time" else 20260926)
    best = seed.copy()

    def score(p: np.ndarray) -> float:
        if np.max(np.abs(p[1:-1])) > 2.35 or not monotone_torque(p):
            return math.inf
        t, e, _, _ = path_metrics(p)
        if time_cap is not None and t > time_cap:
            return math.inf
        return t if objective == "time" else e

    best_score = score(best)
    for scale, trials in [(0.36, 600), (0.18, 800), (0.08, 1000), (0.035, 1200)]:
        for _ in range(trials):
            candidate = best.copy()
            candidate[1:-1] += rng.normal(0.0, scale, candidate[1:-1].shape)
            value = score(candidate)
            if value < best_score:
                best, best_score = candidate, value
    return best


def target_surface_point(field_current: float) -> np.ndarray:
    target = torque(IB)
    best = None
    best_d = math.inf
    for id_ in np.linspace(-0.35, 1.15, 2401):
        active = (LD - LQ) * id_ + LM * field_current
        if active <= 0.02:
            continue
        iq = target / (KT * active)
        p = np.array([id_, iq, field_current])
        if np.max(np.abs(p)) > 2.35:
            continue
        d = float((p - IA) @ G @ (p - IA))
        if d < best_d:
            best, best_d = p, d
    assert best is not None
    return best


def sample_path(name: str, points: np.ndarray, durations: list[float]) -> None:
    rows = []
    elapsed = 0.0
    for index, (a, b, dt) in enumerate(zip(points[:-1], points[1:], durations)):
        count = 45
        for j, s in enumerate(np.linspace(0.0, 1.0, count)):
            if index and j == 0:
                continue
            i = (1 - s) * a + s * b
            di = (b - a) / dt
            u = voltage(i, di)
            rows.append([
                elapsed + s * dt,
                *(i.tolist()),
                torque(i),
                float(i @ R @ i),
                utilization(u),
            ])
        elapsed += dt
    np.savetxt(
        DATA / f"dynamic_{name}.dat",
        np.asarray(rows),
        header="t id iq if torque pcu uutil",
        fmt="%.9f",
    )


def main() -> None:
    eig = np.linalg.eigvalsh(L)
    assert np.all(eig > 0.0)
    assert np.allclose(L, L.T)
    assert np.allclose(D.T @ D, G)
    assert np.allclose(D @ B_SYS @ np.diag([US, US, UF]), np.eye(3))

    c_geom = target_surface_point(IA[2])
    active_naive = (LD - LQ) * IB[0] + LM * IA[2]
    c_stator = np.array([IB[0], torque(IB) / (KT * active_naive), IA[2]])
    c_excite = np.array([IA[0], IA[1], IB[2]])
    strategies: dict[str, np.ndarray] = {
        "straight": np.vstack([IA, IB]),
        "stator_first": np.vstack([IA, c_stator, IB]),
        "excitation_first": np.vstack([IA, c_excite, IB]),
        "geometric": np.vstack([IA, c_geom, IB]),
    }

    seed = np.vstack([IA, IA + (IB - IA) / 3.0, IA + 2.0 * (IB - IA) / 3.0, IB])
    time_path = search(seed, "time")
    strategies["time"] = time_path
    t_time = path_metrics(time_path)[0]
    energy_seed = time_path.copy()
    energy_path = search(energy_seed, "energy", time_cap=1.55 * t_time)
    strategies["energy"] = energy_path

    summary_rows = []
    for name, points in strategies.items():
        t, e, peak_u, durations = path_metrics(points)
        assert np.isfinite(t) and peak_u <= 1.00001
        sample_path(name, points, durations)
        summary_rows.append((name, t, e, peak_u, len(points) - 2))

    with (DATA / "dynamic_summary.dat").open("w", encoding="ascii") as stream:
        stream.write("# strategy time energy peak_u internal_waypoints\n")
        for row in summary_rows:
            stream.write(f"{row[0]} {row[1]:.7f} {row[2]:.7f} {row[3]:.7f} {row[4]}\n")

    # Projector identity at a representative point.
    i = 0.5 * (IA + IB)
    grad = KT * np.array([(LD - LQ) * i[1], (LD - LQ) * i[0] + LM * i[2], LM * i[1]])
    ginv = np.linalg.inv(G)
    pg = np.eye(3) - np.outer(ginv @ grad, grad) / float(grad @ ginv @ grad)
    assert np.allclose(grad @ pg, np.zeros(3), atol=2e-12)
    assert np.allclose(pg @ pg, pg, atol=2e-12)

    # Finite-horizon Gramian positivity through deterministic quadrature.
    horizon = 1.5
    vals, vecs = np.linalg.eig(A_SYS)
    def expm(t: float) -> np.ndarray:
        return np.real_if_close(vecs @ np.diag(np.exp(vals * t)) @ np.linalg.inv(vecs)).astype(float)
    grid = np.linspace(0.0, horizon, 2001)
    wc = np.zeros((3, 3))
    for left, right in zip(grid[:-1], grid[1:]):
        mid = 0.5 * (left + right)
        em = expm(mid)
        wc += (right - left) * em @ B_SYS @ B_SYS.T @ em.T
    wc_eigs = np.linalg.eigvalsh(wc)
    assert np.all(wc_eigs > 0.0)

    tau_s = math.sqrt((LD / RS) * (LQ / RS))
    tau_f = LF / RF
    print("dynamic symbolic/matrix checks: PASS")
    print(f"inductance eigenvalues: {eig}")
    print(f"tau_s={tau_s:.6f}, tau_f={tau_f:.6f}, epsilon={tau_s/tau_f:.6f}")
    print(f"torque step: {torque(IA):.6f} -> {torque(IB):.6f}")
    for name, t, e, peak_u, _ in summary_rows:
        print(f"{name:16s} time={t:.6f} energy={e:.6f} peak_u={peak_u:.6f}")
    print(f"Gramian eigenvalues at T={horizon}: {wc_eigs}")
    print("dynamic numeric checks: PASS")


if __name__ == "__main__":
    main()
