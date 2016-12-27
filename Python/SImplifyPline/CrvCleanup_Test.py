import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs


def CurveCleanup():
    crvId = rs.GetObject("Select curve", 4, True)
    if crvId is None: return
    

    tol = sc.doc.ModelAbsoluteTolerance*2
    crv= sc.doc.Objects.Find(crvId).Geometry
    
    if type(crv) == Rhino.Geometry.PolyCurve:
        x = crv.ToNurbsCurve()
        rc = x.RemoveShortSegments(tol)
        sc.doc.Objects.AddCurve(x)
        sc.doc.Objects.Delete(crvId, True)

    sc.doc.Objects.UnselectAll()    
    
    sc.doc.Views.Redraw()
    pass
    
if __name__ == "__main__":
    CurveCleanup()