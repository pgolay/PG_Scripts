import Rhino
import rhinoscriptsyntax as rs

def Pt3d2Str(Pt3d):
    spt = str(Pt3d)
    spt = spt.lstrip("(")
    spt = spt.rstrip(")")
    return spt
    
def GBToVP():
    view = rs.CurrentView()
    plane = rs.ViewCameraPlane(view)
    plane.Origin = rs.ViewCameraTarget(view)[1]
    p1 = "w" + Pt3d2Str(plane.Origin)
    p2 = "w" + Pt3d2Str(plane.Origin + plane.XAxis)
    p3 = "w" + Pt3d2Str(plane.Origin + plane.YAxis)
    
    rs.Command("NoEcho RelocateGumball " + p1 +" " + p2 +" "+ p3 +" ")
    
if( __name__ == "__main__" ):
    GBToVP()
    
