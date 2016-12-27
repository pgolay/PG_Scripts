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
        result = go.GetMultiple(1,0)
        
        if( go.CommandResult() != Rhino.Commands.Result.Success ):
            return
        if result == Rhino.Input.GetResult.Option:
            oldCopy = opCopy.CurrentValue
            sc.sticky["COPYEXTRUSION"] = oldCopy
            continue
        if result == Rhino.Input.GetResult.Object:
            Ids = [go.Object(i).ObjectId for i in range(go.ObjectCount)]
            break
            
    lengths = []
    for Id in Ids:
        extObj = sc.doc.Objects.Find(Id)
        geo = extObj.ExtrusionGeometry
        dirCrv = geo.PathLineCurve()
        lengths.append (dirCrv.GetLength())
        
    strLength = "Current length "
    maxLength = max(lengths)

    minLength = min(lengths)
    
    if maxLength == minLength:
        strLength = strLength + "is " + str(maxLength)
    else:
        strLength = strLength + "varies from " + str(minLength) + " to " + str(maxLength)
        
    newLength = rs.GetReal("Set extrusion length. " + strLength,oldLength)
    if newLength is None: return
    sc.sticky["OLDEXTLENGTH"] = abs(newLength)
    
    if Ids is not None:
        rs.EnableRedraw(False)
        for Id in Ids:
            extObj = sc.doc.Objects.Find(Id)
            geo = extObj.ExtrusionGeometry
            dirCrv = geo.PathLineCurve()
            #length = dirCrv.GetLength()
            vecDir = (dirCrv.PointAtEnd - dirCrv.PointAtStart)
            vecDir.Unitize()

            p1 = dirCrv.PointAtStart
            p2 = p1 + (vecDir*newLength)
            
            geo.SetPathAndUp(p1, p2, geo.GetProfilePlane(0.0).YAxis)
            
            exId = sc.doc.Objects.AddExtrusion(geo)
            
            rs.MatchObjectAttributes(exId, Id)
            
            #sc.doc.Objects.Replace(Id, extObj.Geometry)
            exObj = sc.doc.Objects.Find(exId)
            exObj.Attributes.WireDensity = -1
            exObj.CommitChanges()
            
            if not oldCopy:
                rs.DeleteObject(Id)
                
            sc.doc.Objects.Select(exId)
            rs.Command("RefreshShade", False)
            
            
            #sc.doc.Objects.Replace(Id,geo)
    rs.EnableRedraw(True)
    sc.doc.Views.Redraw()
    pass
    
if __name__ =="__main__":
    SetExtrusionLength()