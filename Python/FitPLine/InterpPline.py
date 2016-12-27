import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

def Test():
    pLineId = rs.GetObject("Select a polyline", 4, preselect=True)
    if pLineId is None: return
    pLineObj= sc.doc.Objects.Find(pLineId)
    
    rc, pLine = pLineObj.Geometry.TryGetPolyline()
    
    ang = Rhino.RhinoMath.ToRadians(30)
    x = pLine.BreakAtAngles(ang)
    for item in x:
        sc.doc.Objects.AddPolyline(item)
    pass
if __name__ == "__main__":
    Test()