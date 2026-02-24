import numpy as np
import pyqpoases
from utils import *
from models.quad import *
import matplotlib.pyplot as plt
import time


if __name__ == '__main__':
    N = 40
    T = 10.0
    umin = np.zeros(m)
    umax = u_hover * 1.8

    Q = np.diag([100, 1, 100, 1, 200, 1,   10, 1, 10, 1, 10, 1])
    R = np.eye(m) * 0.1
    P, K = ilqr(A, B, Q, R)
    lb_u = umin - u_hover
    ub_u = umax - u_hover
    Cx = [np.zeros((0, n)) for t in range(N)]
    lb_x = [np.zeros(0) for t in range(N)]
    ub_x = [np.zeros(0) for t in range(N)]
    Cu = [np.eye(m) for t in range(N)]
    lb_u = [lb_u.copy() for t in range(N)]
    ub_u = [ub_u.copy() for t in range(N)]
    H, G, g_x0, g_q, g_r, lu_x0, lc, uc = condense(A, B, Q, R, P, Cx, Cu, lb_x, ub_x, lb_u, ub_u, N, K)
    solver = pyqpoases.qpoases()
    g = np.zeros(N * m)
    solver.init(H, G, g, lc, uc, N, m, False)

    nsteps = int(T / Ts)
    ref_traj = generate_ref(Ts, T, N)
    solve_times = np.zeros(nsteps)

    xk = np.zeros(n)
    x_history = [xk]
    u_history = []
    t_history = [0]
    r = np.zeros(m*N)
    for k in range(nsteps):
        q = [-ref_traj[:, k+i] @ Q for i in range(1, N)] + [-ref_traj[:, k+N] @ P]
        q = np.hstack(q)
        g, lb, ub = get_parametric_qp_terms_tv(g_x0, g_q, g_r, lu_x0, lc, uc, xk, q, r)

        du, solve_time_ms, iter = solver.mpcsolve(g, lb, ub)
        solve_times[k] = solve_time_ms
        print(f"Time step {k+1}. Solve time: {solve_time_ms:.3f} ms. Iter: {iter}")

        du = - K @ xk + du
        xk = h(xk, du)
        x_history.append(xk)
        u_history.append(du + u_hover)
        t_history.append((k+1) * Ts)

    x_hist_np = np.array(x_history)
    u_hist_np = np.array(u_history)
    ref_hist_np = ref_traj[:, :nsteps+1]

    fig = plt.figure(figsize=(14, 10))

    # 3D Trajectory
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    ax1.plot(ref_hist_np[0, :], ref_hist_np[2, :], ref_hist_np[4, :], 'g--', label='Reference')
    ax1.plot(x_hist_np[:, 0], x_hist_np[:, 2], x_hist_np[:, 4], 'b-', label='MPC Path')
    ax1.set_title("3D Position Tracking (Figure 8)")
    ax1.legend()

    # Control Inputs
    ax2 = fig.add_subplot(2, 2, 2)
    for i in range(4):
        ax2.plot(t_history[:-1], u_hist_np[:, i], label=f'Motor {i}')
    ax2.axhline(umax[0], color='r', linestyle='--', label='Max Thrust')
    ax2.axhline(umin[0], color='k', linestyle='--', label='Min Thrust')
    ax2.set_title("Control Inputs vs Limits")
    ax2.legend()

    # X/Y Tracking
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(t_history, ref_hist_np[0, :], 'g--', label='X Ref')
    ax3.plot(t_history, x_hist_np[:, 0], 'b-', label='X Real')
    ax3.plot(t_history, ref_hist_np[2, :], 'r--', label='Y Ref')
    ax3.plot(t_history, x_hist_np[:, 2], 'm-', label='Y Real')
    ax3.set_title("Horizontal Tracking")
    ax3.legend()

    # Z Tracking
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.plot(t_history, ref_hist_np[4, :], 'g--', label='Z Ref')
    ax4.plot(t_history, x_hist_np[:, 4], 'b-', label='Z Real')
    ax4.set_title("Altitude Tracking")
    ax4.legend()

    plt.tight_layout()
    plt.savefig("figures/quad_tv.png")

    print()
    print(f"Maximum solve time: {np.max(solve_times)} ms")
    print(f"Average solve time: {np.mean(solve_times)} ms")