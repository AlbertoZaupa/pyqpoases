import numpy as np

n = 58
m = 29
data = np.load('models/data/atlas.npz')
A = data['A']
B = data['B']
h = lambda dx, du : A @ dx + B @ du