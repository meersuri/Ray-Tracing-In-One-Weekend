import numpy as np
from vec3 import dot
from hittable import Hittable, HitRecord
import pdb

class Sphere(Hittable):
    def __init__(self, center, radius, material):
        super().__init__()
        self.center = center
        self.radius = radius
        self.material = material
    
    def hit(self, ray, t_min, t_max):
        co = ray.origin - self.center
        a = ray.direction.length_squared()
        half_b = dot(co, ray.direction)
        c = co.length_squared() - self.radius**2
        d = half_b**2 - a*c 
        if d < 0:
            return False

        sqrtd = np.sqrt(d)
        t = (-half_b - sqrtd)/a
        if t > t_max or t < t_min:
            t = (-half_b + sqrtd)/a
        if t > t_max or t < t_min:
            return False

        self.rec.t = t
        self.rec.point = ray.at(t)
        outward_normal = (self.rec.point - self.center)/self.radius;
        self.rec.set_face_normal(ray, outward_normal)
        self.rec.material = self.material

        return True

        
