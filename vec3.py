import numpy as np
from utils import rand

def random_in_hemisphere(normal):
    in_unit_sphere = random_in_unit_sphere()
    if dot(in_unit_sphere, normal) > 0.0:
        return in_unit_sphere
    return -in_unit_sphere
    
def random_in_unit_sphere():
    while True:
        p = Vec3.random(-1, 1)
        if p.length_squared() < 1:
            return p

def random_unit_vector():
    return unit_vector(random_in_unit_sphere())

def random_in_unit_disk():
    while True:
        vec = Vec3([rand(-1, 1), rand(-1, 1), 0])
        if vec.length_squared() > 1:
            continue
        return vec


def reflect(v, n):
    return v - 2*dot(v, n)*n

def refract(uv, n, refractive_ratio):
    cos_theta = min(dot(-uv, n), 1)
    r_perp = refractive_ratio * (uv + cos_theta*n)
    r_parallel =  -np.sqrt(abs(1 - r_perp.length_squared()))*n
    return r_perp + r_parallel

class Vec3x:
    def __get__(self, obj, objtype=None):
        return obj.e[0]
    
    def __set__(self, obj, value):
        obj.e[0] = value

class Vec3y:
    def __get__(self, obj, objtype=None):
        return obj.e[1]
    
    def __set__(self, obj, value):
        obj.e[1] = value

class Vec3z:
    def __get__(self, obj, objtype=None):
        return obj.e[2]
    
    def __set__(self, obj, value):
        obj.e[2] = value

class Vec3:

    x = Vec3x()
    y = Vec3y()
    z = Vec3z()

    def random(min_coord=0, max_coord=1):
        return Vec3([rand(min_coord, max_coord), rand(min_coord, max_coord), rand(min_coord, max_coord)])
    

    def __init__(self, vec=[0.0, 0.0, 0.0]):
        if not (isinstance(vec, list) or isinstance(vec, np.ndarray)):
            msg = 'vec must be a list or numpy.ndarray'
            raise ValueError(msg)
        if len(vec) != 3:
            msg = 'vec must have len 3'
            raise ValueError(msg)
        self.e = np.array(vec, dtype=np.float32)

    def near_zero(self):
        return np.allclose(self.e, np.array([0.0, 0.0, 0.0]))

    def __neg__(self):
        return Vec3(-self.e)
    
    def __getitem__(self, idx):
        return self.e[idx]
    
    def __add__(self, other):
        if isinstance(other, Vec3):
            return Vec3(self.e + other.e)
        else:
            return Vec3(self.e + other)

    def __radd__(self, other):
        return Vec3(self.e + other)

    def __iadd__(self, other):
        if isinstance(other, Vec3):
            self.e += other.e
        else:
            self.e += other
        return self
    
    def __sub__(self, other):
        if isinstance(other, Vec3):
            return Vec3(self.e - other.e)
        else:
            return Vec3(self.e - other)

    def __rsub__(self, other):
        return Vec3(other - self.e)

    def __isub__(self, other):
        if isinstance(other, Vec3):
            self.e -= other.e
        else:
            self.e -= other
        return self
    
    def __mul__(self, other):
        if isinstance(other, Vec3):
            return Vec3(self.e * other.e)
        else:
            return Vec3(other*self.e)
    
    def __rmul__(self, t):
        return Vec3(self.e*t)

    def __imul__(self, t):
        self.e *= t
        return self
    
    def __truediv__(self, t):
        return Vec3(self.e / t)

    def __itruediv__(self, t):
        self.e /= t
        return self
    
    def __eq__(self, other):
        return all(self.e == other.e)
    
    def __str__(self):
        return ' '.join([str(x) for x in self.e])

    def length(self):
        return np.linalg.norm(self.e, 2)
    
    def length_squared(self):
        return np.linalg.norm(self.e, 2)**2
    

def dot(u, v):
    if not isinstance(u, Vec3) or not isinstance(v, Vec3):
        raise ValueError('Expected Vec3 for both arguments')
    return np.dot(u.e, v.e)

def cross(u, v):
    if not isinstance(u, Vec3) or not isinstance(v, Vec3):
        raise ValueError('Expected Vec3 for both arguments')
    return Vec3(np.cross(u.e, v.e))

def unit_vector(v):
    return v/v.length()

        
Point3 = Vec3
Color = Vec3
