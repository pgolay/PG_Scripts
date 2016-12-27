import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc



def DividePointsWithPlane(pts, plane):
    
    x = []
    
    
    for pt in pts:
        v = pt - plane.Origin
        x.append (Rhino.Geometry.Point3d(v*plane.XAxis, v*plane.YAxis, v*plane.ZAxis))
    

    lPlus = []
    lMinus = []
    
    for pt in x:
        if pt.Z >=0:
            lPlus.append(pt)
        else:
            lMinus.append(pt)
            
    return lPlus,lMinus
        
    """
    Set the point coordinates to plane coordinates
    Split the points as to + and - Z
    
    """
    
    
    
def tester():
    
    ptIds = rs.GetObjects("Select points", 1, group=True,  preselect=True)
    if not ptIds: return
    
    
    
    pts = []
    for Id in ptIds:
        pts.append(rs.PointCoordinates(Id))
        
    x =  DividePointsWithPlane(pts, rs.ViewCPlane())
    pass
tester()
    
    