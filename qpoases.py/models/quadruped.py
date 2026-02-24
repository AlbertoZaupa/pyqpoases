import numpy as np

data = np.load("models/data/quadruped.npz")
A = data['Ad']
B = data['Bd']
K = data['K']
dX = data['dX']
tau_low = data['l'][-20:]
tau_upp = data['u'][-20:]
n = 52
m = 32
nu = 20
nlam = 12