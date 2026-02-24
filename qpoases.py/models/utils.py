def rk4(f, x, u, dt):
    k1 = dt * f(x, u)
    k2 = dt * f(x + k1/2, u)
    k3 = dt * f(x + k2/2, u)
    k4 = dt * f(x + k3, u)
    return x + (k1 + 2*k2 + 2*k3 + k4) / 6