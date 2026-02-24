import pyqpoases
import numpy as np
from utils import *
from models.atlas import *

if __name__ == '__main__':
    Q = np.diag(data['Q'])
    R = np.diag(data['R'])
    P = data['P']
    K = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
    lb_u = - data['d_u'] - data['u_ref']
    ub_u = data['d_u'] - data['u_ref']
    dx0 = data['x0'] - data['x_ref']
    N = 30
    n_steps = 300

    Cx = [np.zeros((0, n)) for t in range(N)]
    Cu = [np.eye(m) for t in range(N)]
    lb_x = [np.zeros(0) for t in range(N)]
    ub_x = [np.zeros(0) for t in range(N)]
    lbu_t = [lb_u.copy() for t in range(N)]
    ubu_t = [ub_u.copy() for t in range(N)]

    H, G, g_x0, _, __, lu_x0, low, upp = condense(A, B, Q, R, P, Cx, Cu, lb_x, ub_x, lbu_t, ubu_t, N, K)
    solver = pyqpoases.qpoases()
    g = np.zeros(N * m)
    solver.init(H, G, g, low, upp, N, m, False)

    solve_times = np.zeros(n_steps)
    for t in range(n_steps):
        g_new, low_new, upp_new = get_parametric_qp_terms(g_x0, lu_x0, low, upp, dx0)
        du, solve_time_ms, iter = solver.mpcsolve(g_new, low_new, upp_new)
        print(f"Timestep {t+1}. Iterations: {iter}. Solve time: {solve_time_ms:.3f} ms.")
        solve_times[t] = solve_time_ms
        dx0 = A @ dx0 + B @ np.clip(-K @ dx0 + du, lb_u, ub_u)

    print()
    print(f"Final state norm: {np.linalg.norm(dx0)}")
    print(f"Worst case solve time: {np.max(solve_times)} ms")
    print(f"Average solve time: {np.mean(solve_times)} ms")
    print(f"Minimum solve time: {np.min(solve_times)} ms")