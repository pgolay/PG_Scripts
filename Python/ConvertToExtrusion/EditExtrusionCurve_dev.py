import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc


def SetExtrusionLength():
    oldLength = 10
    oldCopy = False
    while True:
        if sc.sticky.has_key("COPYEXTRUSION"):
            oldCopy = sc.sticky["COPYEXTRUSION"]
            
        if sc.sticky.has_key("OLDEXTLENGTH"):
            oldLength = sc.sticky["OLDEXTLENGTH"]
            
        tol = sc.doc.ModelAbsoluteTolerance
        go = Rhino.Input.Custom.GetObject()
        go.GeometryFilter=Rhino.DocObjects.ObjectType.Extrusion
        opCopy = Rhino.Input.Custom.OptionToggle(oldCopy, "No", "Yes")
        go.AddOptionToggle("Copy", opCopy)
        go.SetCommandPrompt("Select extrusions")
        result = go.Get()
        
        if( go.CommandResult() != Rhino.Commands.Result.Success ):
            return
        if result == Rhino.Input.GetResult.Option:
            oldCopy = opCopy.CurrentValue
            sc.sticky["COPYEXTRUSION"] = oldCopy
            continue
        if result == Rhino.Input.GetResult.Object:
            Id = go.Object(0).ObjectId 
            break

    extObj = sc.doc.Objects.Find(Id)
    geo = extObj.ExtrusionGeometry
    dirCrv = geo.PathLineCurve()


    extObj = sc.doc.Objects.Find(Id)
    geo = extObj.ExtrusionGeometry
    profs = [geo.Profile3d(i,0.0) for i in range (geo.ProfileCount)]
    basePlane = profs[0].TryGetPlane()[1]
    xform = Rhino.Geometry.Transform.PlaneToPlane(basePlane, Rhino.Geometry.Plane.WorldXY)
    profCrvs = [sc.doc.Objects.AddCurve(prof) for prof in profs]
    
    dirCrv = geo.PathLineCurve()
    vecDir = (dirCrv.PointAtEnd - dirCrv.PointAtStart)
    vecDir.Unitize()
    
    """
    Do some stuff here
    e.g. if possible add the extrsuion with History, keep the curves
    instead of deleting them, turn on curve points.
    
    """
    

    baseCrvObj = sc.doc.Objects.Find(profCrvs[0])
    sc.doc.Objects.Delete(profCrvs.pop(0), True)
    newGeo = Rhino.Geometry.Extrusion.Create(baseCrvObj.Geometry, dirCrv.GetLength()* vecDir.IsParallelTo(baseCrvObj.Geometry.TryGetPlane()[1].ZAxis),geo.IsSolid)

    if len(profCrvs) > 0:
        for Id in profCrvs:
            crv = sc.doc.Objects.Find(Id).Geometry
            crv.Transform(xform)
            newGeo.AddInnerProfile(crv)
    exId = sc.doc.Objects.AddExtrusion(newGeo)
    
    rs.MatchObjectAttributes(exId, Id)
    
    #sc.doc.Objects.Replace(Id, extObj.Geometry)
    exObj = sc.doc.Objects.Find(exId)
    exObj.Attributes.WireDensity = -1
    exObj.CommitChanges()
    
    if not oldCopy:
        rs.DeleteObject(Id)
        
    sc.doc.Objects.Select(exId)
    rs.Command("RefreshShade", False)
            
    rs.EnableRedraw(True)
    sc.doc.Views.Redraw()
    pass
    
if __name__ =="__main__":
    SetExtrusionLength()