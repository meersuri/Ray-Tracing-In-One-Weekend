import numpy as np
import io
import os
from tqdm import tqdm
from multiprocessing import Process, Value, Manager
import time

from color import Color, write_color
from vec3 import Vec3, Point3, unit_vector, dot, random_in_unit_sphere, random_unit_vector, random_in_hemisphere
from ray import Ray
from sphere import Sphere
from hittable import Hittable, HitRecord
from hittable_list import HittableList 
from camera import Camera
from material import Lambertian, Metal, Dielectric

class PathTracer:

    def __init__(self, image_width=400, aspect_ratio=16.0/9.0, samples_per_pix=2, max_depth=10):
        self.aspect_ratio = aspect_ratio
        self.image_width = image_width
        self.image_height = int(image_width / aspect_ratio) 
        self.samples_per_pix = samples_per_pix
        self.max_depth = max_depth

        self.running_processes = Value('I', 0)
        self.completed_processes = Value('I', 0)
        self.pixel_colors = Manager().dict()
        for i in range(self.image_height):
            for j in range(self.image_width):
                self.pixel_colors[(i, j)] = 0
        
    def ray_color(self, ray, depth):
        if depth <= 0:
            return Color([0, 0, 0])

        if self.world.hit(ray, 0.001, np.inf):
            scattered = Ray()
            did_scatter, scattered = self.world.rec.material.scatter(ray, self.world.rec)
            if did_scatter:
                atten = self.world.rec.material.albedo
                return atten * self.ray_color(scattered, depth - 1)
            return Color([0, 0, 0]) 
        unit_dir = unit_vector(ray.direction)
        t = 0.5*(unit_dir.y + 1.0)
        return (1.0 - t)*Color([1.0, 1.0, 1.0]) + t*Color([0.5, 0.7, 1.0])

    def hit_sphere(self, center, radius, ray):
        co = ray.origin - center
        a = ray.direction.length_squared()
        half_b = dot(co, ray.direction)
        c = co.length_squared() - radius**2
        d = half_b**2 - a*c 
        if d > 0:
            return (-half_b - np.sqrt(d))/a
        return -1

    def create_world(self):
        self.world = HittableList()
        material_ground = Lambertian(Color([0.8, 0.8, 0.0]))
        material_center = Lambertian(Color([0.1, 0.2, 0.5]))
        material_left = Dielectric(1.5)
        material_right = Metal(Color([0.8, 0.6, 0.2]), 0.0)
        
        self.world.add(Sphere(Point3([0, -100.5 , -1]), 100, material_ground))
        self.world.add(Sphere(Point3([0, 0, -1]), 0.5, material_center))
        self.world.add(Sphere(Point3([-1, 0 , -1]), 0.5, material_left))
        self.world.add(Sphere(Point3([-1, 0 , -1]), -0.45, material_left))
        self.world.add(Sphere(Point3([1, 0 , -1]), 0.5, material_right))

    def setup_stream(self):
        self.stream = io.StringIO()
        self.stream.write("P3\n")
        self.stream.write(str(self.image_width) + ' ' + str(self.image_height) + '\n')
        self.stream.write("255\n")

    def setup_camera(self):
        self.cam = Camera(Point3([-2, 2, 1]), Point3([0, 0, -1]), Vec3([0, 1, 0]), 20.0, self.aspect_ratio)
    
    def color_row(self, j):
        np.random.seed(j)
        for i in range(self.image_width):
            pix_color = Color([0, 0, 0])
            for s in range(self.samples_per_pix):
                u = (i + np.random.rand())/(self.image_width - 1)
                v = (j + np.random.rand())/(self.image_height - 1)
                r = self.cam.get_ray(u, v)
                pix_color += self.ray_color(r, self.max_depth) 
            self.pixel_colors[(i, j)] = pix_color
        return 
    
    def create_processes(self):
        self.processes = []
        for j in reversed(range(self.image_height)):
            self.processes.append(Process(target=self.run_one_process, args=(j, )))
    
    def run_processes(self):
        for p in self.processes:
            while self.running_processes.value >= os.cpu_count():
                time.sleep(0.1)
            p.start()
            time.sleep(0.1)

        for p in self.processes:
            p.join()

    def run_one_process(self, j):
        
        with self.running_processes.get_lock():
            self.running_processes.value += 1

        self.color_row(j)

        with self.running_processes.get_lock():
            self.running_processes.value -= 1

        with self.completed_processes.get_lock():
            self.completed_processes.value += 1
            print(f'\x9B1K{self.completed_processes.value}/{len(self.processes)}', end='\r')
        
    def save_image(self):

        for j in reversed(range(self.image_height)):
            for i in range(self.image_width):
                pix_color = self.pixel_colors[(i, j)]
                write_color(self.stream, pix_color, self.samples_per_pix)

        with open('image.ppm', 'w') as f:
            f.write(self.stream.getvalue())

    def print_progress(self):
        pass

    def run(self):

        self.create_world()
        self.setup_camera()
        self.setup_stream()
        self.create_processes()
        self.run_processes()
        self.save_image()

if __name__ == '__main__':
    pt = PathTracer(samples_per_pix=5, max_depth=50)
    pt.run()



