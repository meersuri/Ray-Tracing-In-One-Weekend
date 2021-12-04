import numpy as np
from vec3 import Vec3
Color = Vec3

def write_color(stream, pix_color, samples_per_pix):
    r, g, b = pix_color.x, pix_color.y, pix_color.z
    scale = 1.0/samples_per_pix
    r = np.sqrt(r*scale)
    g = np.sqrt(g*scale)
    b = np.sqrt(b*scale)
    stream.write(str(int(256*np.clip(r, 0, 0.999))) + ' ' +
                 str(int(256*np.clip(g, 0, 0.999))) + ' ' +
                 str(int(256*np.clip(b, 0, 0.999))) + '\n')
