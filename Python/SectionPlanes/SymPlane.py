import Rhino
import scriptcontext as sc
import System
import math
import rhinoscriptsyntax as rs


def AveragePoint3d(aPts):
    P = len(aPts)
    X = Y = Z = 0
    L = len(aPts)
    for i in range(len(aPts)):
        X = X + aPts[i].X
        Y = Y + aPts[i].Y
        Z = Z + aPts[i].Z
        
    return Rhino.Geometry.Point3d(X/L, Y/L, Z/L)

def SymPlane():
    
    pts1 = rs.GetObjectGrips("Select the first set of points.", preselect=True)
    
    if not pts1: return
    
    pts2 = rs.GetObjectGrips("Select the second set of points.")
    
    if not pts2: return
    
    loc1 = []
    loc2 = []
    for info in pts1:
        loc1.append(info[2])
        
    for info in pts2:
        loc2.append(info[2])
        
    
    p1 = AveragePoint3d(loc1)
    p2 = AveragePoint3d(loc2)
    vec = (p1-p2)/2
    p = p2 + vec
    #rs.AddPoint (p)
    
    cp = rs.ViewCPlane()
    vecZ = cp.ZAxis
    
    dirPt = rs.GetPoint(message = "Set plane direction.", base_point = p)
    if not dirPt: return
    vecDir = dirPt-p
    rs.ViewCPlane( plane = rs.PlaneFromFrame( p,vecDir, vecZ))
    rs.Command ("Plane Center 0")
    
    rs.ViewCPlane(plane = cp)
    
SymPlane()