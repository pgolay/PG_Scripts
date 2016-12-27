import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

def ExtractCenterline():
    
    go = Rhino.Input.Custom.GetObject()
    go.EnablePreSelect(True, False)
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Surface
    go.Get()
    if go.CommandResult()!= Rhino.Commands.Result.Success:
        return
        
    objRef = go.Objects()[0]
    Face = objRef.Face()
    srf = Face.UnderlyingSurface()
    idx = Face.FaceIndex
    Id = objRef.ObjectId
    test = sc.doc.Objects.Find(Id)
    v = test.Geometry.Faces[idx].DuplicateFace(False)
    v.Faces.ShrinkFaces()
    
    #sc.doc.Objects.AddBrep(v)
    srf = v.Faces[0].ToNurbsSurface()
    

    faceDomU = srf.Domain(0)
    faceDomV = srf.Domain(1)
    limitPt1 = srf.PointAt(faceDomU.Min,faceDomV.Min)
    limitPt2 = srf.PointAt(faceDomU.Max,faceDomV.Max)
    pass
    
    #    sc.doc.Objects.AddPoint(limitPt1)
    #    sc.doc.Objects.AddPoint(limitPt2)
    parU = srf.Domain(0).Mid
    parV = srf.Domain(1).Mid
    
    UIso = srf.IsoCurve( 0, parV )
    VIso = srf.IsoCurve( 1, parU )
    
    pt = Rhino.Geometry.Surface.PointAt( srf, parU, parV )
    vecNorm = Rhino.Geometry.Surface.NormalAt( srf, parU, parV )
    
    UCrv = VIso.CurvatureAt(parU)
    VCrv = UIso.CurvatureAt(parV)
    
    if UCrv.Length > VCrv.Length:
        section = VIso
        source = UIso
        UDir = True
    else:
        section = UIso
        source = VIso
        UDir = False
        
    tol = sc.doc.ModelAbsoluteTolerance
    type_rc, x = Rhino.Geometry.NurbsSurface.TryGetCone(srf,tol)
    if type_rc:
        print "The object appears to be a cone."
        line = Rhino.Geometry.Line(x.BasePoint, x.ApexPoint)
        curve = sc.doc.Objects.AddLine(line)
        if curve:
            sc.doc.Objects.UnselectAll()
            sc.doc.Objects.Select(curve)
        sc.doc.Views.Redraw()
        return
    else:
        type_rc, x = Rhino.Geometry.NurbsSurface.TryGetCylinder(srf,tol)
        if type_rc:
            print "The object appears to be a cylinder."
            brep = Face.DuplicateFace(False)
            brep.Faces.ShrinkFaces()
            tempSrf = brep.Faces[0].UnderlyingSurface()
            domU = tempSrf.Domain(0)
            domV = tempSrf.Domain(1)
            plane = Rhino.Geometry.Plane.WorldXY
            line = Rhino.Geometry.Line(x.Center, x.Center + (x.Axis*x.TotalHeight))
            bb = tempSrf.GetBoundingBox(plane)
            line.ExtendThroughBox(bb)
            p1 = line.ClosestPoint(limitPt1, tol)
            p2 = line.ClosestPoint(limitPt2, tol)
            curve = sc.doc.Objects.AddLine(Rhino.Geometry.Line(p1,p2))
            if curve:
                sc.doc.Objects.UnselectAll()
                sc.doc.Objects.Select(curve)
            sc.doc.Views.Redraw()
            return
        else:
            type_rc, x = Rhino.Geometry.NurbsSurface.TryGetTorus(srf,tol)
            if type_rc:
                print "The object appears to be a torus."
                circle = Rhino.Geometry.Circle(x.Plane, x.MajorRadius)
                plane = circle.Plane
                brep = Face.DuplicateFace(False)
                brep.Faces.ShrinkFaces()
                tempSrf = brep.Faces[0].UnderlyingSurface()
                domU = tempSrf.Domain(0)
                domV = tempSrf.Domain(1)
                
                p1 = plane.ClosestPoint(tempSrf.PointAt(domU[0],domV[0]))
                p2 = plane.ClosestPoint(tempSrf.PointAt(domU[1],domV[1]))
                p3 = circle.Center
                vec1 = p3-p1
                vec2 = p3-p2
                arc = None
                ang = Rhino.Geometry.Vector3d.VectorAngle(vec1, vec2)
                if ang > .001:
                    arc = Rhino.Geometry.Arc(circle, ang)
                if arc: 
                    curve = sc.doc.Objects.AddArc(arc)
                else:
                    curve = sc.doc.Objects.AddCircle(circle)
                if curve: 
                    sc.doc.Objects.UnselectAll()
                    sc.doc.Objects.Select(curve)
                sc.doc.Views.Redraw()
                return
                
            else:
                type_rc, x = Rhino.Geometry.NurbsSurface.TryGetSphere(srf,tol)

                if type_rc:
                    print "The object appears to be a sphere."
                    Center_pt = sc.doc.Objects.AddPoint(x.Center)
                    if Center_pt:
                        sc.doc.Objects.UnselectAll()
                        sc.doc.Objects.Select(Center_pt)
                    sc.doc.Views.Redraw()
                    return
        
    rc, circle = Rhino.Geometry.Curve.TryGetArc( section, .001 )
    
    if rc:
       
        vecTest = Rhino.Geometry.Vector3d( circle.Center - pt )
        if Rhino.Geometry.Vector3d.IsParallelTo( vecNorm, vecTest ) == -1:
            result  = Rhino.Geometry.Curve.OffsetNormalToSurface( source, srf, -1*circle.Radius )
        else:
            result  = Rhino.Geometry.Curve.OffsetNormalToSurface( source, srf, circle.Radius )
            pass
        if result: 
            Curve = sc.doc.Objects.AddCurve(result)
            if Curve:
                rs.UnselectAllObjects()
                rs.SelectObject(Curve)
    sc.doc.Views.Redraw()

    
if( __name__ == "__main__" ):
    ExtractCenterline()