import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs


def test():
    
    #srfId = rs.GetObject("Select a surface", 8, True)
    
    while True:
        normLen = 1
        if sc.sticky.has_key("XNORMLENGTH"):
            normLen = sc.sticky["XNORMLENGTH"]
            
        go = Rhino.Input.Custom.GetObject()
        go.GeometryFilter = Rhino.DocObjects.ObjectType.Surface
        go.AcceptNumber(True, False)
        opLen = Rhino.Input.Custom.OptionDouble(normLen)
        go.AddOptionDouble( "Length", opLen)
        go.SetCommandPrompt("Select a surface")
        ret = go.Get()
        
        if go.CommandResult()!=Rhino.Commands.Result.Success:
            return go.CommandResult()
        if ret == Rhino.Input.GetResult.Option:
            sc.sticky["XNORMLENGTH"] = opLen.CurrentValue
            normLen = opLen.CurrentValue
            continue
        if ret == Rhino.Input.GetResult.Number:
            sc.sticky["XNORMLENGTH"] = go.Number()
            normLen = go.Number()
            continue
        if ret==Rhino.Input.GetResult.Object:
            srfObj = go.Object(0)
            break
            
    
    #srfObj = sc.doc.Objects.Find(srfId)
    brep = srfObj.Geometry()
    flipped=False
    density  = srfObj.Object().Attributes.WireDensity
    if brep.Faces[0].OrientationIsReversed:flipped = True

    crvs = brep.GetWireframe(density)
    if not crvs: resturn
    pts = []
    tol = sc.doc.ModelAbsoluteTolerance
    
    for n in range (len(crvs)):
        for p in range(len(crvs)):
            if crvs[n] != crvs[p]:
                aInt = Rhino.Geometry.Intersect.Intersection.CurveCurve(crvs[n],crvs[p],tol, tol)
                for item in aInt:
                    if item.IsPoint:
                        pts.append(item.PointA)
                        pass
    rs.EnableRedraw(False)
    if len(pts) > 0:
        culledPts = Rhino.Geometry.Point3d.CullDuplicates(pts, tol)
        for pt in culledPts:
            rc,U,V = brep.Surfaces[0].ClosestPoint(pt)
            vecNorm = brep.Surfaces[0].NormalAt(U,V)*normLen
            if flipped: vecNorm.Reverse()
            rs.AddLine(pt, rs.PointAdd(pt,vecNorm))
            pass
    rs.EnableRedraw(True)
test()