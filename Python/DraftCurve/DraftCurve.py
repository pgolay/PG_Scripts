import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
from System.Collections.Generic import *



def SampleSurfaceDraftAnglePoint(surface_id, point_2d, angle):
    rs_obj = rs.GetPlugInObject("RhinoScript")
    if rs_obj:
        surface_str = str(surface_id)
        point = List[float]()
        point.Add(point_2d[0])
        point.Add(point_2d[1])
        draft = rs_obj.SurfaceDraftAnglePoint(surface_str, point.ToArray(), angle)
        return draft
    return null
    
    
def test():


    

    srfObjRef = rs.GetObject("Select a surface", 8, True, subobjects=True)
    if not srfObjRef: return
    Id = srfObjRef.ObjectId
    idx = srfObjRef.GeometryComponentIndex.Index
    brep = sc.doc.Objects.Find(Id)
    srf = brep.Geometry.Faces[0].ToNurbsSurface()
    #x = brep.Geometry.ComputeSilhouette()
    crvId = rs.GetObject("Select the silhouette curve", 4)
    if not crvId: return
    crv = sc.doc.Objects.Find(crvId).Geometry
    
    def get_draft_points():
        dAng = 5
        style = Rhino.Geometry.CurveKnotStyle.ChordSquareRoot
        
        if sc.sticky.has_key("DRAFTANGLE"):
            dAng = sc.sticky["DRAFTANGLE"]
            
        pts = []
        dPts = []
        dCrv = None
        
        while True:
            gp = Rhino.Input.Custom.GetPoint()
            gp.Constrain(crv,False)
            optAng = Rhino.Input.Custom.OptionDouble(dAng,0,90)
            gp.AddOptionDouble("DraftAngle", optAng)
            gp.SetCommandPrompt("Pick a point.")
            rc = gp.Get()
            if gp.CommandResult()!=Rhino.Commands.Result.Success:
                break
            if rc ==Rhino.Input.GetResult.Option:
                dAng = optAng.CurrentValue
                sc.sticky["DRAFTANGLE"] = dAng
            #pts.append(gp.Point())
            p3d = gp.Point()
            p2d = srf.ClosestPoint(p3d)
            
            result = SampleSurfaceDraftAnglePoint(Id, p2d, dAng)
            if len(result) ==2:
                pD = result[0]
            if pD: dPts.append(Rhino.Geometry.Point3d(pD[0],pD[1],pD[2]) )
            rs.AddPoint(Rhino.Geometry.Point3d(pD[0],pD[1],pD[2]) )
            if len(dPts) > 1:
                dCrv = Rhino.Geometry.Curve.CreateInterpolatedCurve(dPts, 3, style)
                pass
        return dPts, dCrv
    pass
    dPts, dCrv = get_draft_points()
    pass
    if dCrv: sc.doc.Objects.AddCurve(dCrv)
    
    pass
    
    
    
    
test()