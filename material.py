import numpy as np
from hittable import HitRecord
from abc import ABC
from vec3 import reflect, refract, unit_vector, random_unit_vector, dot, random_in_unit_sphere, Color
from ray import Ray
from utils import rand

class Material(ABC):
    def scatter(ray_in, rec, attenuation, ray_scattered):
        pass

class Lambertian(Material):
    def __init__(self, a):
        self.albedo = a
    
    def scatter(self, ray_in, rec):
        scatter_dir = rec.normal + random_unit_vector()
        if scatter_dir.near_zero():
            scatter_dir = rec.normal
        scattered = Ray(rec.point, scatter_dir)
        return True, scattered

class Metal(Material):
    def __init__(self, a, fuzz):
        self.albedo = a
        self.fuzz = min(1, fuzz)
    
    def scatter(self, ray_in, rec):
        reflected = reflect(unit_vector(ray_in.direction), rec.normal)
        scattered = Ray(rec.point, reflected + self.fuzz*random_in_unit_sphere())
        return dot(scattered.direction, rec.normal) > 0, scattered

class Dielectric(Material):
    def __init__(self, refractive_idx):
        self.ri = refractive_idx
        self.albedo = Color([1, 1, 1])
    
    def scatter(self, ray_in, rec):
        refraction_ratio = 1/self.ri if rec.front_face else self.ri
        unit_direction = unit_vector(ray_in.direction)
        cos_theta = min(dot(-unit_direction, rec.normal), 1.0)
        sin_theta = np.sqrt(1.0 - cos_theta**2)
        cannot_refract = refraction_ratio * sin_theta > 1.0 
        if cannot_refract or self.reflectance(cos_theta, refraction_ratio) > rand():
            direction = reflect(unit_direction, rec.normal)
        else:
            direction = refract(unit_direction, rec.normal, refraction_ratio) 
        scattered = Ray(rec.point, direction)
        return True, scattered
    
    def reflectance(self, cosine, ref_idx):
        r0 = (1 - ref_idx)/( 1 + ref_idx)
        r0 = r0**2
        return r0 + (1 - r0)*pow((1 - cosine), 5)
