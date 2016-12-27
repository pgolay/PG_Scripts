import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs


def CurveCleanup():
    crvIds = rs.GetObjects("Select curves", 4, True, True)
    if crvIds is None: return
    
    newIds = []
    tol = sc.doc.ModelAbsoluteTolerance
    aTol= sc.doc.ModelAngleToleranceRadians
    opSim = Rhino.Geometry.CurveSimplifyOptions.All
    for crvId in crvIds:
        crv= sc.doc.Objects.Find(crvId).Geometry
        
        if type(crv) == Rhino.Geometry.PolylineCurve:
            rc, pLine = crv.TryGetPolyline()
            count = pLine.CollapseShortSegments(tol*2)
            if count !=0:
                sc.doc.Objects.Replace(crvId, pLine)
                newIds.append(crvId)
        else:
            if type(crv) == Rhino.Geometry.PolyCurve:
                nCrv = crv.ToNurbsCurve()
                rc = nCrv.RemoveShortSegments(tol*2)
#                   :
    #                    bits = crv.Explode()
    #                    newBits = Rhino.Geometry.Curve.JoinCurves(bits)
    #                    
    #                    temp = [sc.doc.Objects.AddCurve(bit)for bit in newBits]
    #                    newIds.extend(temp)
    
    #            
            temp = sc.doc.Objects.AddCurve(nCrv.Simplify( opSim,tol, aTol))
            newIds.append(temp)
            
            rs.MatchObjectAttributes(temp, crvId)
            sc.doc.Objects.Delete(crvId, True)
        
    sc.doc.Objects.UnselectAll()    
    if len(newIds) >0: rs.SelectObjects(newIds)
    
    sc.doc.Views.Redraw()
    pass
    
if __name__ == "__main__":
    CurveCleanup()