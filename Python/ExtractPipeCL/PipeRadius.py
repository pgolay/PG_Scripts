import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

def SrfRadius():
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select a surface.")
    go.EnablePreSelect(False, False)
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Surface
    go.Get()
    if go.CommandResult()!= Rhino.Commands.Result.Success:
        return
        
    objRef = go.Objects()[0]
    sp = objRef.SelectionPoint()
    brep = objRef.Geometry()
    idx = objRef.GeometryComponentIndex.Index
    
    if idx != -1: 
        srf = brep.ToNurbsSurface()
    else:
        srf = brep.Faces[0].ToNurbsSurface()
    
    par = Rhino.Geometry.NurbsSurface.ClosestPoint(srf, sp)
    parU = par[1]
    parV = par[2]
    
    VIso = srf.IsoCurve( 0, parV )
    UIso = srf.IsoCurve( 1, parU )
    
    UCrvtr = VIso.CurvatureAt(parU)
    VCrvtr = UIso.CurvatureAt(parV)
    
    if UCrvtr.Length > VCrvtr.Length:
        section = VIso
    else:
        section = UIso
    
    tol = sc.doc.ModelAbsoluteTolerance
    x = Rhino.Geometry.NurbsSurface.TryGetTorus(srf, tol)
    pass
    
    if Rhino.Geometry.NurbsSurface.TryGetCone(srf, tol)[0]:
        strType = "The object appears to be a cone. Radius at pick point is "
        
    elif Rhino.Geometry.NurbsSurface.TryGetCylinder(srf, tol)[0]:
        strType = "The object appears to be a cylinder. Radius is "
        blnCyl, cyl = Rhino.Geometry.NurbsSurface.TryGetCylinder(srf, tol)
        tempPar = cyl.ToNurbsSurface().Domain(0)[0]
        print strType + str(round(cyl.CircleAt(tempPar).Radius,3))
        return
        
    elif Rhino.Geometry.NurbsSurface.TryGetSphere(srf, tol)[0]:
        strType = "The object appears to be a sphere. Radius is "
        blnSphere, sphere = Rhino.Geometry.NurbsSurface.TryGetSphere(srf, tol)
        print strType + str(round(sphere.Radius,3))
        return
        
    elif Rhino.Geometry.NurbsSurface.TryGetTorus(srf, tol)[0]:
        strType = "The object appears to be a torus. The smallest radius at pick point is "
        blnTorus, torus = Rhino.Geometry.NurbsSurface.TryGetTorus(srf, tol)
        print strType + str(round(torus.MinorRadius,3))
        return
        
    elif Rhino.Geometry.NurbsSurface.TryGetPlane(srf, tol)[0]:
        strType = "The object appears to be a planar. No radius to report."
    else: strType = "Radius at pick point is "
        
    rc, circle = Rhino.Geometry.Curve.TryGetArc( section, .001 )
    
    if rc:
       print strType + str(round(circle.Radius, 3))
    else:
        print "No constant radius found."

    
if( __name__ == "__main__" ):
    SrfRadius()