from abc import ABC
from vec3 import Vec3, Point3, dot

class HitRecord:
    def __init__(self):
        self.point = None
        self.normal = None
        self.t = None
        self.front_face = None
        self.material = None
    
    def set_face_normal(self, ray, outward_normal):
        if dot(ray.direction, outward_normal) > 0:
            self.front_face = False
            self.normal = -outward_normal
        else:
            self.front_face = True
            self.normal = outward_normal

class Hittable(ABC):
    def __init__(self):
        self.rec = HitRecord()

    def hit(ray, t_min, t_max, hit_record):
        pass
