import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
"""

Mark discontinuities with dots
Use picks a dot, add the db to the smaller angle.
Remove the dot.

"""


def isSubCrvLine(rhObject,geometry, componentIndex):
    isSubCrvLine = False
    print componentIndex.Index
    #if componentIndex.Index < 1: return False
    c = rs.coercecurve(geometry)
    if c:
        isSubCrvLine, line  = c.TryGetLine()
    
    return isSubCrvLine

def test():
    rad = 1
    
    if sc.sticky.has_key("DOGBONE_RAD"):
        rad = sc.sticky["DOGBONE_RAD"]
        
    tol = sc.doc.ModelAbsoluteTolerance
    aTol = sc.doc.ModelAngleToleranceRadians
    #x = rs.GetCurveObject()
    while True:
        
        go = Rhino.Input.Custom.GetObject()
        #go.GeometryAttributeFilter=Rhino.Input.Custom.GeometryAttributeFilter.Sub
        go.GeometryFilter =  Rhino.DocObjects.ObjectType.Curve
        go.SubObjectSelect = True
        oprad = Rhino.Input.Custom.OptionDouble(rad,True, tol*10)
        go.AddOptionDouble("CutterRadius", oprad)
        go.AcceptNumber(True, False)
        #go.SetCustomGeometryFilter(isSubCrvLine)
        go.CustomGeometryFilter
        ret = go.Get()
        
        if( go.CommandResult() != Rhino.Commands.Result.Success ):
            return
        if ret == Rhino.Input.GetResult.Option:
            rad = oprad.CurrentValue
            sc.sticky["DOGBONE_RAD"] = rad
            continue
        if ret == Rhino.Input.GetResult.Number:
            rad = go.Number()
            sc.sticky["DOGBONE_RAD"] = rad
            continue
        if ret == Rhino.Input.GetResult.Object:
            objRef  = go.Object(0)
            point = objRef.SelectionPoint()
            crv, par = objRef.CurveParameter()
            obj = go.Object(0).Object()
            Id = objRef.ObjectId
            break
    simOp = Rhino.Geometry.CurveSimplifyOptions.All
    crv = crv.Simplify(Rhino.Geometry.CurveSimplifyOptions.All, tol, aTol)
    
    discoType= Rhino.Geometry.Continuity.G1_continuous
    disc = []
    if isinstance(crv, Rhino.Geometry.PolylineCurve):
        print "P-line"
    else:
        dom = crv.Domain
        t0 = dom.Min
        t1 = dom.Max
        points = []
        discpar = []
        indices = []
        get_next = True

        while get_next == True:
            get_next, t = crv.GetNextDiscontinuity(discoType, t0, t1)
            print get_next
            if get_next:
                disc.append(crv.PointAt(t))
                discpar.append(t)
                t0 = t
                
                
        if isinstance(crv, Rhino.Geometry.PolyCurve):
            print crv.RemoveNesting()
            print crv.SegmentCount
            for par in discpar:
                dom = Rhino.Geometry.Interval(par, par)
                indices.append(crv.SegmentIndexes(dom))
                
                
    pars = [crv.Domain.Min]
    for pt in disc:
        rs.AddPoint(pt)
        tempPar = crv.ClosestPoint(pt)[1]
        pars.append(tempPar)
        
    pars.append(crv.Domain.Max)
    pass
    

    
if __name__ == "__main__":
    test()