import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino
import math


def LineTangent():
    ang = 30
    if sc.sticky.has_key("TAN_ANGLE"):
        ang = sc.sticky["TAN_ANGLE"]
    plane = rs.ViewCPlane()
    
    vecDir = plane.XAxis
    
    crvInfo = rs.GetCurveObject("Select a curve near the tangent point.")
    if crvInfo is None: return
    
    crvId1 = crvInfo[0]
    crv1 = sc.doc.Objects.Find(crvInfo[0]).Geometry
    p1 = crvInfo[3]
    
    bb = rs.BoundingBox(crvId1, plane)

    ang = rs.GetReal("Angle?", ang,  0, 180)
    print ang
    if ang is None: return
    sc.sticky["TAN_ANGLE"] = ang
    
    plane.Rotate(Rhino.RhinoMath.ToRadians(ang), plane.ZAxis)
    bb = crv1.GetBoundingBox(plane)
    pts = bb.GetCorners()
    
    xForm = Rhino.Geometry.Transform.PlaneToPlane( Rhino.Geometry.Plane.WorldXY, plane)
    cor1 = pts[3]
    cor2 = pts[2]
    cor3 = pts[0]
    cor4 = pts[1]
    
    cor1.Transform(xForm)
    cor2.Transform(xForm)
    cor3.Transform(xForm)
    cor4.Transform(xForm)
    
    #p1 = rs.GetPointOnCurve(crvId1, "Pick curve near tangent point")
    
    #p1 = rs.GetPoint()
    if p1 is None: return
    l1 = Rhino.Geometry.Line(cor1, cor2)
    l2 = Rhino.Geometry.Line(cor3, cor4)
    d1 = l1.ClosestPoint(p1, True).DistanceTo(p1)
    d2 = l2.ClosestPoint(p1, True).DistanceTo(p1)
    
    if d1<d2:
        lcrv = Rhino.Geometry.LineCurve(cor1, cor2)
        line = Rhino.Geometry.Line(cor1, cor2)
    else:
        lcrv = Rhino.Geometry.LineCurve(cor3, cor4)
        line = Rhino.Geometry.Line(cor3, cor4)
    
    
    rc, cp1, cp2 = lcrv.ClosestPoints(crv1)
    
    #rs.AddPoint(cp2)

    gp = Rhino.Input.Custom.GetPoint()
    
    gp.Constrain(line)
    gp.EnableDrawLineFromPoint(False)
    gp.DrawLineFromPoint(cp2, True)
    
    result = gp.Get()
    
    #if result != Rhino.Commands.Result.Point: return
    if gp.Point() is None: return
    p = gp.Point()
    pass

    #p = rs.GetPoint()
    pass
    l = Rhino.Geometry.Line(cp2,p)
    sc.doc.Objects.AddLine(l)

    sc.doc.Views.Redraw()
    if p1 is None: return
    

    
LineTangent()