import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino
import math


def LineTangent():
    ang = None
    objref = None
    """
    BETTER FLOW:
    Set up a getObject with Angle option > then get point on curve
    If Angle, use the go below, with Angle option prompt showing Angle=XXX
    
    BothSides option? Try implementing as rs.COmmand (Line) with Along osnap
    """

    while True:
        ang = 30
        if sc.sticky.has_key("TAN_ANGLE"):
            ang = sc.sticky["TAN_ANGLE"]
        go = Rhino.Input.Custom.GetObject()
        go.SetCommandPrompt("Select a curve near the tangent point.")
        go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
        go.SubObjectSelect = False
        go.GroupSelect = False
        go.AcceptNothing(True)
        go.AcceptNumber(True, True)
        optAng = Rhino.Input.Custom.OptionDouble(ang, 0, 180)
        go.AddOptionDouble("Angle",optAng)
    
        ret2 = go.Get()
        if go.CommandResult()!=Rhino.Commands.Result.Success: return
        if ret2 == Rhino.Input.GetResult.Option:
        
            if sc.sticky.has_key("TAN_ANGLE"):
                ang = sc.sticky["TAN_ANGLE"]
            ang = go.Number()
            if ang is None: return
            sc.sticky["TAN_ANGLE"] = ang
            continue
        if ret2 == Rhino.Input.GetResult.Number:
            ang = go.Number()
            if ang is None: return
            sc.sticky["TAN_ANGLE"] = ang
            continue
            
        if ret2 == Rhino.Input.GetResult.Object:
             objref = go.Object(0)
             break

        
    crvId1= objref.ObjectId
    p1 = objref.SelectionPoint()
    par = objref.CurveParameter()[1]
    viewname = go.View().ActiveViewport.Name
    obj = objref.Object()
    crv1 = objref.Geometry()
    
    spanCount = crv1.SpanCount
    spanIdx = None
    domLength= None
    
    for i in range(spanCount):
        tempDom = crv1.SpanDomain(i)
        if tempDom.Min < par < tempDom.Max:
            spanIdx = i
            domLength = tempDom.Length
            break
            
    print spanIdx
    
    plane = rs.ViewCPlane(viewname)

    ang = Rhino.RhinoMath.ToRadians(ang)
    
    vecTest = crv1.TangentAt(par)
        
    while True:
        par1 = par + domLength/10
        par2 = par - domLength/10
        tan1 = crv1.TangentAt(par1)
        tan2 = crv1.TangentAt(par2)
        ang1 = Rhino.Geometry.Vector3d.VectorAngle(plane.XAxis, tan1)
        ang2 = Rhino.Geometry.Vector3d.VectorAngle(plane.XAxis, tan2)
        
        if (ang1 < ang and ang2 > ang) or (ang1 < ang and ang2 < ang):
            
            rs.AddPoints([crv1.PointAt(par1),crv1.PointAt(par2)])
            break
    domLength = domLength/2
        
    curves = crv1.Split([par1,par2])
    crv1 = curves[1]
    plane.Rotate(ang, plane.ZAxis)

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
    gp = Rhino.Input.Custom.GetPoint()
    
    gp.Constrain(line)
    gp.EnableDrawLineFromPoint(False)
    gp.DrawLineFromPoint(cp2, True)
    
    result = gp.Get()
    if gp.CommandResult()!=Rhino.Commands.Result.Success:return
    p = gp.Point()

    newLine = Rhino.Geometry.Line(cp2,p)
    sc.doc.Objects.AddLine(newLine)
    
    sc.doc.Views.Redraw()
    

if __name__ == "__main__":
    LineTangent()