import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

def ArcFilter(rhino_object, geometry, component_index ):
    ret, arc = geometry.ToNurbsCurve().TryGetArc()
    if ret:
         return True
    else: 
        return False

def BarrelSrf():
    mark = False
    if sc.sticky.has_key("BARREL_AXIS_MARKER"):
        mark = sc.sticky ["BARREL_AXIS_MARKER"]
    
    #    crvId = rs.GetObject("Select a curve to define the barrel shape", 4, preselect = True)
    #    if crvId is None: return
    #    crv = sc.doc.Objects.Find(crvId).Geometry
    crv = None
    arc = None
    while True:
        go = Rhino.Input.Custom.GetObject()
        go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
        go.SetCommandPrompt("Select a curve to define the barrel shape")
        opMark = Rhino.Input.Custom.OptionToggle(mark, "No", "Yes")
        
        go.AddOptionToggle("MarkAxis", opMark)
        
        retCrv = go.Get()
        
        if (go.CommandResult() != Rhino.Commands.Result.Success ): return
        
        if retCrv == Rhino.Input.GetResult.Option:
            mark = opMark.CurrentValue
            sc.sticky ["BARREL_AXIS_MARKER"] = mark
            continue
            
        if retCrv == Rhino.Input.GetResult.Object:
            crv = go.Object(0).Geometry()
            break
    
    
    while True:
        
        ga = Rhino.Input.Custom.GetObject()
        ga.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
        ga.SetCustomGeometryFilter(ArcFilter)
        ga.EnablePreSelect(False,True)
        ga.SetCommandPrompt("Select an arc to define the barrel extents")
        opMark = Rhino.Input.Custom.OptionToggle(mark, "No", "Yes")
        
        ga.AddOptionToggle("MarkAxis", opMark)
        
        ret = ga.Get()
        
        if (ga.CommandResult() != Rhino.Commands.Result.Success ): return
        
        if ret == Rhino.Input.GetResult.Option:
            mark = opMark.CurrentValue
            sc.sticky ["BARREL_AXIS_MARKER"] = mark
            continue
            
        if ret == Rhino.Input.GetResult.Object:
            arc = ga.Object(0).Geometry().ToNurbsCurve().TryGetArc()[1]
            #arc = ga.Object(0).Geometry()
            break
    
    arcPlane = arc.Plane
    axis = Rhino.Geometry.Line(arcPlane.Origin, arcPlane.Origin + arcPlane.ZAxis)
    rc,cp1, cp2 = crv.ClosestPoints(arc.ToNurbsCurve())
    
    if not rc: return
    
    vec1 = cp1 - arcPlane.Origin 
    vec2 = arc.StartPoint - arcPlane.Origin
    
    ang = Rhino.Geometry.Vector3d.VectorAngle(vec1, vec2, arcPlane)
    
    crv.Rotate( ang, arcPlane.ZAxis, arcPlane.Origin)
    
    revSrf = Rhino.Geometry.RevSurface.Create(crv, axis)
    if revSrf is None: return
    
    pt = arc.EndPoint
    rc, par1, par2 = revSrf.ClosestPoint(pt)
    if not rc: retrurn
    
    srfs = revSrf.Split(0, par1)
    sc.doc.Objects.AddSurface(srfs[0])
    
    if mark:
        bb = arc.ToNurbsCurve().GetBoundingBox(False)
        vecDir = arcPlane.ZAxis * bb.Diagonal.Length/2
        p1 = arcPlane.Origin + vecDir
        vecDir.Reverse()
        p2 = arcPlane.Origin + vecDir
        sc.doc.Objects.AddLine(Rhino.Geometry.Line(p1, p2))
        
    sc.doc.Views.Redraw()
    pass
    
    
if __name__ == "__main__":
    BarrelSrf()