import Rhino
import rhinoscriptsyntax as rs

def Pt3d2Str(Pt3d):
    spt = str(Pt3d)
    spt = spt.lstrip("(")
    spt = spt.rstrip(")")
    return spt

def GBCenter():
    view = rs.CurrentView()
    plane = rs.ViewCameraPlane(view)
    plane.Origin = rs.ViewCameraTarget(view)[1]
    p1 = "w" + Pt3d2Str(plane.Origin)
    
    rs.Command("NoEcho RelocateGumball " + p1 +" Enter")
    
if( __name__ == "__main__" ):
    GBCenter()