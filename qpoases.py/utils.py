import numpy as np
import scipy as sp

# Condense an LTI OCP by elimination of state variables
# and by reparametrizing the controls as a displacement
# from the LQR: u[t] = -K @ x[t] + du[t].
# The optimization variables of the resulting QP are
# { du[t] }.
def condense(A, B, Q, R, P, Cx, Cu, lb_x, ub_x, lb_u, ub_u, N, K = None):
    nx = A.shape[1]
    nu = B.shape[1]
    if K is None:
        K = np.zeros((nu, nx))
    
    Q_bar = np.kron(np.eye(N), Q)
    Q_bar[-nx:, -nx:] = P
    R_bar = np.kron(np.eye(N), R)
    
    # Feedforwards to states map
    F = np.zeros((N*nx, N*nu))
    # Feedforwards to controls map
    F_bar = np.eye(N * nu)
    A2k_B = B
    K_A2k_B = K @ B
    for k in range(N):
        for i in range(k, N):
            F[i*nx : (i+1)*nx, (i-k)*nu : (i-k+1)*nu] = A2k_B
            if i > k:
                F_bar[i*nu : (i+1)*nu, (i-k-1)*nu : (i-k)*nu] = -K_A2k_B
        A2k_B = (A - B @ K) @ A2k_B
        K_A2k_B = K @ A2k_B

    # Hessian
    H = F_bar.T @ R_bar @ F_bar + F.T @ Q_bar @ F

    # Constraints matrix
    ncx = [Cx_t.shape[0] for Cx_t in Cx]
    ncu = [Cu_t.shape[0] for Cu_t in Cu]
    C = np.zeros((sum(ncx), N*nx))
    D = np.zeros((sum(ncu), N*nu))
    for (t, ncx_t) in enumerate(ncx): 
        offset = sum(ncx[:t])
        C[offset : offset + ncx_t, t*nx : (t+1)*nx] = Cx[t]
    for (t, ncu_t) in enumerate(ncu):
        offset = sum(ncu[:t])
        D[offset : offset + ncu_t, t*nu : (t+1)*nu] = Cu[t]

    G = np.vstack([C @ F, D @ F_bar])
    low = np.hstack([np.hstack(lb_x), np.hstack(lb_u)])
    upp = np.hstack([np.hstack(ub_x), np.hstack(ub_u)])

    # Mappings from the inital condition to the states
    # and from the initial condition to the feedforwards
    L = np.zeros((nx * N, nx))
    L_bar = np.zeros((nu * N, nx))
    A2k = np.eye(nx)
    for k in range(N):
        L_bar[k*nu : (k+1)*nu, :] = - K @ A2k
        A2k = (A - B @ K) @ A2k
        L[k*nx : (k+1)*nx, :] = A2k

    # Maps x0 to the component of the linear term dependent on the initial condition
    g_x0 = F_bar.T @ R_bar @ L_bar + F.T @ Q_bar @ L

    # Maps x0 to the component of the bounds dependent on the initial condition
    lu_x0 = np.vstack([C @ L, D @ L_bar])

    # Map from linear terms in the OCP to 
    # linear terms in the condensed, reparametrized
    # problem.
    # q.T X = q.T (L x0 + F dU) = q.T L x0 + q.T F dU
    # r.T U = r.T (L_bar x0 + F_bar dU) = r.T L_bar x0 + r.T F_bar dU
    g_q = F.T
    g_r = F_bar.T

    return H, G, g_x0, g_q, g_r, lu_x0, low, upp

# Utility for condensed QPs.
# Given x0, computes the linear term in the cost
# and the bounds for the constraints.
def get_parametric_qp_terms(g_x0, lu_x0, low, upp, x0):
    const = lu_x0 @ x0
    return g_x0 @ x0, low - const, upp - const

# Utility for condensed QPs.
# Computes the linear term in the cost and the bounds
# for the constraints as a function of x0, q, r.
# tv stands for time-varying, as this utility is 
# used for problems where q and r (the references)
# change over time.
def get_parametric_qp_terms_tv(g_x0, g_q, g_r, lu_x0, low, upp, x0, q, r):
    g = g_x0 @ x0 + g_q @ q + g_r @ r
    const = lu_x0 @ x0
    return g, low - const, upp - const

# Computes the infinite horizon LQR solution by
# solving the associated DARE.
def ilqr(A, B, Q, R, max_iter=1000, verbose=False):
    nx, nu = B.shape
    L = sp.linalg.cholesky(Q, lower=True)
    for i in range(max_iter):
        BL = B.T @ L
        AL = A.T @ L
        H = np.block([
            [R + BL @ BL.T, BL @ AL.T], 
            [AL @ BL.T, Q + AL @ AL.T]])
        cholH = sp.linalg.cholesky(H, lower=True)
        L_new = cholH[nu:, nu:]

        res = np.linalg.norm(L - L_new)
        if res < 1e-7: break
        if verbose and i > 0 and i % 50 == 0: print(f"Iteration {i+1}, residual: {res:.7f}")
        L = L_new

    if i == max_iter: print("ilqr reached maximum number of iterations.")
    return L @ L.T, sp.linalg.cho_solve((cholH[:nu, :nu], True), BL @ AL.T)