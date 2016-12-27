import Rhino
import scriptcontext as sc

"""
Cleans up by collapsing tiny segments in a polyline.
"""
def CleanUpPolyline():
    
    while True:
        tol = sc.doc.ModelAbsoluteTolerance
        if sc.sticky.has_key("PLineSimplifyTol"):
            tol = sc.sticky["PLineSimplifyTol"]
        go = Rhino.Input.Custom.GetObject()
        go.AcceptNumber(True, False)
        go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
        opDblTol = Rhino.Input.Custom.OptionDouble(tol)
        go.AddOptionDouble("SegmentTolerance",opDblTol)
        
        result = go.Get()
        
        if( go.CommandResult() != Rhino.Commands.Result.Success ):
            return
            
        if result == Rhino.Input.GetResult.Object:
            
            if type(go.Object(0).Geometry()) == Rhino.Geometry.PolylineCurve:
                curve = go.Object(0).Geometry()
                rc, pLine = curve.TryGetPolyline()
                pLineId = go.Object(0).ObjectId
            else:
                sc.doc.Objects.UnselectAll()
                sc.doc.Views.Redraw()
                print "Sorry, that was not a polyline."
                continue
            break
            
        elif result == Rhino.Input.GetResult.Option:
            tol = opDblTol.CurrentValue
            sc.sticky["PLineSimplifyTol"] = tol
            continue
        elif result == Rhino.Input.GetResult.Number:
            tol = go.Number()
            sc.sticky["PLineSimplifyTol"] = tol
            continue
        break
        
    count = pLine.CollapseShortSegments(tol)
    if count !=0:
        sc.doc.Objects.Replace(pLineId, pLine)
        sc.doc.Views.Redraw()
        print str(count) + " short segments were collapsed."
    else:
        print "No short segments were collapsed."
    pass
if __name__ == "__main__":
    CleanUpPolyline()