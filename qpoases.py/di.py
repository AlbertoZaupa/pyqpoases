import pyqpoases
from utils import *

nx = 2
nu = 1
N = 10
A = np.array([[1, 1], [0, 1]])
B = np.array([[0], [1]])
Q = np.eye(nx)
R = np.eye(nu)
P, _ = ilqr(A, B, Q, R)
Cx = [np.zeros((0, nx)) for t in range(N-3)] + [np.array([[1, 0]]), np.array([[1, 0]]), np.eye(nx)]
Cu = [np.eye(nu), np.zeros((0, nu)), np.eye(nu)] + [np.zeros((0, nu)) for t in range(N-3)]
lb_x = [np.zeros(0) for t in range(N-3)] + [np.zeros(1), np.zeros(1), np.zeros(nx)]
ub_x = [np.zeros(0) for t in range(N-3)] + [np.zeros(1), np.zeros(1), np.zeros(nx)]
lb_u = [np.ones(nu), np.zeros(0), np.ones(nu)] + [np.zeros(0) for t in range(N-3)]
ub_u = [np.ones(nu), np.zeros(0), np.ones(nu)] + [np.zeros(0) for t in range(N-3)]
x0 = np.array([10, 5])

if __name__ == '__main__':
    H, G, g_x0, _, _, lu_x0, lc, uc = condense(A, B, Q, R, P, Cx, Cu, lb_x, ub_x, lb_u, ub_u, N)
    g = np.zeros(N*nu)
    solver = pyqpoases.qpoases()
    solver.init(H, G, g, lc, uc, N, nu, True)
    g, low, upp = get_parametric_qp_terms(g_x0, lu_x0, lc, uc, x0)
    solver.mpcsolve(g, low, upp)

    u = solver.get_sol()
    for t in range(N): print(u[t*nu : (t+1)*nu])
