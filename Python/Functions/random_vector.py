import Rhino
import rhinoscriptsyntax as rs
import math
import random

def random_vector():
    'generate a random unit vector'
    pi = math.pi
    x = random.random()*pi
    if (random.random()<.5): x = -x
    
    y = random.random()*pi
    if (random.random()<.5): y = -y
    
    z = random.random()*pi
    if (random.random()<.5): z = -z
    
    rc = Rhino.Geometry.Vector3d(x,y,z)
    rc.Unitize()
    return rc
    
    
def random_vector_range(pt,vecIn, ang1, ang2):
    'generate a random unit vector in range ang1,ang2'
    if vecIn is None: vecIn = Rhino.Geometry.Vector3d(0,0,1)
    refPlane = rs.PlaneFromNormal(pt,vecIn)
    
    pi = math.pi
    ang1 = math.radians(ang1)
    ang2 = math.radians(ang2)
    plane = rs.WorldXYPlane()
    ang = random.uniform(ang1,ang2)

    vec = Rhino.Geometry.Vector3d(0,0,1)
    #if (random.random()<.5): ang = -ang
    vec.Rotate(ang,plane.XAxis)
    
    ang = random.uniform(0,2*pi)
    #if (random.random()<.5): ang = -ang
    vec.Rotate(ang,plane.ZAxis)
    xform = rs.XformRotation1(plane,refPlane)
    vec.Unitize()
    vec.Transform(xform)
    return vec 
