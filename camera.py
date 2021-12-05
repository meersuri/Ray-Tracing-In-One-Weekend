import numpy as np
from vec3 import Vec3, Point3, cross, unit_vector, random_in_unit_disk
from utils import rand, deg_to_rad
from ray import Ray

class Camera:
    def __init__(self, lookfrom, lookat, vup, vfov, aspect_ratio, aperture, focus_dist):
        self.vfov = vfov
        self.aspect_ratio = aspect_ratio

        theta = deg_to_rad(vfov)
        h = np.tan(theta/2)
        self.viewport_height = 2.0 * h
        self.viewport_width = self.aspect_ratio * self.viewport_height
        self.focal_length = 1.0
        self.lens_radius = aperture/2.0
        self.focus_dist = focus_dist

        self.w = unit_vector(lookfrom - lookat)
        self.u = unit_vector(cross(vup, self.w))
        self.v = cross(self.w, self.u)

        self.origin = lookfrom
        self.horizontal = self.focus_dist * self.viewport_width * self.u
        self.vertical = self.focus_dist * self.viewport_height * self.v
        self.lower_left_corner = self.origin + (-0.5)*self.horizontal + (-0.5)*self.vertical + (-focus_dist)*self.w

    def get_ray(self, s, t):
        rd = self.lens_radius * random_in_unit_disk()
        offset = rd.x*self.u + rd.y*self.v
        direction = self.lower_left_corner + s*self.horizontal + t*self.vertical - self.origin - offset
        return Ray(self.origin + offset, direction)
