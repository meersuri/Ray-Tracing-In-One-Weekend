import numpy as np
import io
from tqdm import tqdm

from color import Color, write_color
from vec3 import Vec3, Point3, unit_vector, dot, random_in_unit_sphere, random_unit_vector, random_in_hemisphere
from ray import Ray
from sphere import Sphere
from hittable import Hittable, HitRecord
from hittable_list import HittableList 
from camera import Camera
from material import Lambertian, Metal, Dielectric

def ray_color(ray, world, depth):
	if depth <= 0:
		return Color([0, 0, 0])

	if world.hit(ray, 0.001, np.inf):
		scattered = Ray()
		did_scatter, scattered = world.rec.material.scatter(ray, world.rec)
		if did_scatter:
			atten = world.rec.material.albedo
			return atten * ray_color(scattered, world, depth - 1)
		return Color([0, 0, 0]) 
	unit_dir = unit_vector(ray.direction)
	t = 0.5*(unit_dir.y + 1.0)
	return (1.0 - t)*Color([1.0, 1.0, 1.0]) + t*Color([0.5, 0.7, 1.0])

def hit_sphere(center, radius, ray):
	co = ray.origin - center
	a = ray.direction.length_squared()
	half_b = dot(co, ray.direction)
	c = co.length_squared() - radius**2
	d = half_b**2 - a*c 
	if d > 0:
		return (-half_b - np.sqrt(d))/a
	return -1

def main():

	aspect_ratio = 16.0/9.0
	image_width = 400
	image_height = int(image_width / aspect_ratio) 
	samples_per_pix = 5
	max_depth = 20

	world = HittableList()
	material_ground = Lambertian(Color([0.8, 0.8, 0.0]))
	material_center = Lambertian(Color([0.1, 0.2, 0.5]))
	material_left = Dielectric(1.5)
	material_right = Metal(Color([0.8, 0.6, 0.2]), 0.0)

	world.add(Sphere(Point3([0, -100.5 , -1]), 100, material_ground))
	world.add(Sphere(Point3([0, 0, -1]), 0.5, material_center))
	world.add(Sphere(Point3([-1, 0 , -1]), 0.5, material_left))
	world.add(Sphere(Point3([-1, 0 , -1]), -0.45, material_left))
	world.add(Sphere(Point3([1, 0 , -1]), 0.5, material_right))

	cam = Camera(Point3([-2, 2, 1]), Point3([0, 0, -1]), Vec3([0, 1, 0]), 20.0, aspect_ratio)

	stream = io.StringIO()
	stream.write("P3\n")
	stream.write(str(image_width) + ' ' + str(image_height) + '\n')
	stream.write("255\n")

	for j in tqdm(reversed(range(image_height))):
		for i in range(image_width):
			pix_color = Color([0, 0, 0])
			for s in range(samples_per_pix):
				u = (i + np.random.rand())/(image_width - 1)
				v = (j + np.random.rand())/(image_height - 1)
				r = cam.get_ray(u, v)
				pix_color += ray_color(r, world, max_depth) 
			write_color(stream, pix_color, samples_per_pix)

	with open('image.ppm', 'w') as f:
		f.write(stream.getvalue())

if __name__ == '__main__':
	main()



