import numpy as np
import pyqpoases
from models.quadruped import *
from utils import *

if __name__ == '__main__':
    H = data['H']
    G = data['G']
    g = data['g']
    low = data['l']
    upp = data['u']
    g_x0 = data['g_x0']
    lu_x0 = -data['lu_x0']
    N = 15
    K = K[:nu, :]
    u_ref = data['u_ref']
    U = data['U']

    solver = pyqpoases.qpoases()
    solver.init(H, G, g, low, upp, N, m, False)

    n_steps = dX.shape[0] // n - 1
    #n_steps = 2
    solve_times = np.zeros(n_steps)
    for t in range(n_steps):
        dx0 = dX[t*n : (t+1)*n]
        u_t = U[t*m : t*m + nu]
        g_new, low_new, upp_new = get_parametric_qp_terms(g_x0, lu_x0, low, upp, dx0)
        
        du, solve_time_ms, iter = solver.mpcsolve(g_new, low_new, upp_new)
        print(f"Timestep {t+1}. Iterations: {iter}. Solve time: {solve_time_ms:.3f} ms.")
        solve_times[t] = solve_time_ms

    print()
    print(f"Maximum solve time: {np.max(solve_times)} ms")
    print(f"Average solve time: {np.mean(solve_times)} ms")
    print(f"Minimum solve time: {np.min(solve_times)} ms")
 