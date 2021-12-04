import numpy as np
from vec3 import Vec3, Point3, cross, unit_vector
from utils import rand, deg_to_rad
from ray import Ray

class Camera:
    def __init__(self, lookfrom, lookat, vup, vfov, aspect_ratio):
        self.vfov = vfov
        self.aspect_ratio = aspect_ratio

        theta = deg_to_rad(vfov)
        h = np.tan(theta/2)
        self.viewport_height = 2.0 * h
        self.viewport_width = self.aspect_ratio * self.viewport_height
        self.focal_length = 1.0

        w = unit_vector(lookfrom - lookat)
        u = unit_vector(cross(vup, w))
        v = cross(w, u)

        self.origin = lookfrom
        self.horizontal = self.viewport_width * u
        self.vertical = self.viewport_height * v
        self.lower_left_corner = self.origin + (-0.5)*self.horizontal + (-0.5)*self.vertical + (-1)*w

    def get_ray(self, s, t):
        direction = self.lower_left_corner + s*self.horizontal + t*self.vertical - self.origin
        return Ray(self.origin, direction)
