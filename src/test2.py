from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Frame

from compas.geometry import Transformation

point = Point(146.00, 150.00, 161.50)
xaxis = Vector(0.9767, 0.0010, -0.214)
yaxis = Vector(0.1002, 0.8818, 0.4609)

# coordinate system F
F = Frame(point, xaxis, yaxis)

T = Transformation.from_frame(F)

print(F)
print(T)
print(T.decomposed())