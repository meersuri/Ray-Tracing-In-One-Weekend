from hittable import Hittable, HitRecord
from copy import deepcopy

class HittableList(Hittable):
	def __init__(self):
		self.objects = []
	
	def add(self, obj):
		self.objects.append(obj)
	
	def clear(self):
		self.objects = []
	
	def hit(self, ray, t_min, t_max):
		hit_anything = False
		closest_so_far = t_max
		for obj in self.objects:
			if obj.hit(ray, t_min, closest_so_far):
				hit_anything = True
				closest_so_far = obj.rec.t
				self.rec = obj.rec
		return hit_anything


