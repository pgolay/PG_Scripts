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
    brep = objRef.Geometry()
    idx = objRef.GeometryComponentIndex.Index
    
    if idx != -1: 
        srf = brep.ToNurbsSurface()
    else:
        srf = brep.Faces[0].ToNurbsSurface()
    
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
    else:
        section = UIso
        source = VIso
    tol = sc.doc.ModelAbsoluteTolerance
    type_rc, x = Rhino.Geometry.NurbsSurface.TryGetCone(srf,tol)
    if type_rc:
        print "The object appears to be a cone."
        line = Rhino.Geometry.Line(x.BasePoint, x.ApexPoint)
        curve = sc.doc.Objects.AddLine(line)
        if curve: sc.doc.Objects.Select(curve)
        return
    else:
        type_rc, x = Rhino.Geometry.NurbsSurface.TryGetCylinder(srf,tol)
        
        if type_rc:
            print "The object appears to be a cylinder."
            
            line = Rhino.Geometry.Line(x.Center, x.Center + (x.Axis*x.TotalHeight))
            curve = sc.doc.Objects.AddLine(line)
            if curve: sc.doc.Objects.Select(curve)
            return
        else:
            type_rc, x = Rhino.Geometry.NurbsSurface.TryGetTorus(srf,tol)
            
            if type_rc:
                print "The object appears to be a torus."
                circle = Rhino.Geometry.Circle(x.Plane, x.MajorRadius)
                curve = sc.doc.Objects.AddCircle(circle)
                if curve: sc.doc.Objects.Select(curve)
                return
                
            else:
                type_rc, x = Rhino.Geometry.NurbsSurface.TryGetSphere(srf,tol)

                if type_rc:
                    print "The object appears to be a sphere."
                    Center_pt = sc.doc.Objects.AddPoint(x.Center)
                    if Center_pt: sc.doc.Objects.Select(Center_pt)
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
            if Curve: rs.UnselectAllObjects()
            rs.SelectObject(Curve)

    pass
    
if( __name__ == "__main__" ):
    ExtractCenterline()