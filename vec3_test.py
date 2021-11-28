import unittest
import numpy as np
from vec3 import Vec3

class TestVec3(unittest.TestCase):

	def test_instance_arr(self):
		self.assertEqual(Vec3([1.0, 2.0, 3.0]).x, 1.0)
		self.assertEqual(Vec3([1.0, 2.0, 3.0]).y, 2.0)
		self.assertEqual(Vec3([1.0, 2.0, 3.0]).z, 3.0)
	
	def test_add_vecs(self):
		u = Vec3([1.0, 2.0, 3.0])
		v = Vec3([2.0, 3.0, 4.0])
		self.assertEqual(u + v, Vec3([3.0, 5.0, 7.0]))

	def test_sub_vecs(self):
		u = Vec3([1.0, 2.0, 3.0])
		v = Vec3([2.0, 0.0, 1.0])
		self.assertEqual(u - v, Vec3([-1.0, 2.0, 2.0]))

	def test_iadd_const(self):
		u = Vec3([1.4, 3.4, 3.2])
		u += 3.1
		self.assertTrue(np.allclose(u.x, 4.5))

	def test_iadd_vec(self):
		u = Vec3([1.4, 3.4, 3.2])
		v = Vec3([1.4, 3.4, 3.2])
		u += v
		self.assertTrue(np.allclose(u.x, 2.8))
	
	def test_isub_const(self):
		u = Vec3([1.0, 2.0, 3.0])
		u -= 1.0
		self.assertTrue(np.allclose(u.e, np.array([0.0, 1.0, 2.0])))

	def test_imul_const(self):
		u = Vec3([1.0, 2.0, 3.0])
		u *= 2
		self.assertTrue(np.allclose(u.e, np.array([2.0, 4.0, 6.0])))


if __name__ == '__main__':
	unittest.main()
