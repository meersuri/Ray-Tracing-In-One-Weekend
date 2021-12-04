import numpy as np
pi = np.pi

def deg_to_rad(deg):
    return deg * pi/180

def rand(x_min=0, x_max=1):
    return x_min + np.random.rand()*(x_max - x_min)
