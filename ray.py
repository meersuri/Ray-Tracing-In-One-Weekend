from vec3 import Point3

class RayOrig:
	def __get__(self, obj, objtype=None):
		return obj.orig

class RayDir:
	def __get__(self, obj, objtype=None):
		return obj.dir

class Ray:
	origin = RayOrig()
	direction = RayDir()

	def __init__(self, origin=None, direction=None):
		self.orig = origin
		self.dir = direction
	
	def at(self, t):
		return self.orig + t*self.dir
	

