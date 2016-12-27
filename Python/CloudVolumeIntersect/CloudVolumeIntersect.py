import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc


def CloudVolumeIntersect():
    tol = sc.doc.ModelAbsoluteTolerance
    while True:
        PCCopy = False
        if sc.sticky.has_key("PCCopy"):
            PCCopy = sc.sticky["PCCopy"]
            
        go = Rhino.Input.Custom.GetObject()
        go.EnablePreSelect(True, True)
        go.GeometryFilter = Rhino.DocObjects.ObjectType.PointSet
        go.SetCommandPrompt("Select a point cloud")
        opCopy = Rhino.Input.Custom.OptionToggle(PCCopy, "No","Yes")
        go.AddOptionToggle("Copy", opCopy)
        result =go.Get()
        
        if( go.CommandResult() != Rhino.Commands.Result.Success ):
            return
        if result == Rhino.Input.GetResult.Option:
            PCCopy = opCopy.CurrentValue
            sc.sticky["PCCopy"] = PCCopy
            continue
        if result == Rhino.Input.GetResult.Object:
            pcObj  = go.Objects()[0]
            break
            
            
    while True:
        PCCopy = False
        if sc.sticky.has_key("PCCopy"):
            PCCopy = sc.sticky["PCCopy"]
            
        go = Rhino.Input.Custom.GetObject()
        go.EnablePreSelect(False, False)
        go.GeometryFilter = Rhino.DocObjects.ObjectType.Brep|Rhino.DocObjects.ObjectType.Mesh|Rhino.DocObjects.ObjectType.Extrusion
        opCopy = Rhino.Input.Custom.OptionToggle(PCCopy, "No","Yes")
        go.AddOptionToggle("Copy", opCopy)
        go.SetCommandPrompt("Select a volume")
        
        result = go.Get()
        
        if( go.CommandResult() != Rhino.Commands.Result.Success ):
            return
            
        if result == Rhino.Input.GetResult.Option:
            PCCopy = opCopy.CurrentValue
            sc.sticky["PCCopy"] = PCCopy
            continue
        if result == Rhino.Input.GetResult.Object:
            vol  = go.Objects()[0].Geometry()
            break
            
            

    brep=True
    pc = pcObj.Geometry()
    pcId = pcObj.ObjectId
    
    #make extrusions into breps
    if isinstance(vol,Rhino.Geometry.Extrusion):
         vol = vol.ToBrep(True)
         brep=True
         
    if isinstance(vol,Rhino.Geometry.Mesh):
        brep =False
        
        
     #make sure the volume id closed   
    notSolid = "The object selected as a volume is not closed."
    if brep: 
        if not vol.IsSolid: 
            print bitSolid
            return
    else:
        if not vol.IsClosed:
            print notSolid
            return
            
    pts = pc.GetPoints()  
    
    #find out if there are colors to deal with
    blnColors = pc.ContainsColors
    if blnColors:  colors = pc.GetColors()
    
    #set up new point clouds
    nc = Rhino.Geometry.PointCloud()
    if not PCCopy: pcOuter = Rhino.Geometry.PointCloud()
    
    if blnColors:
    
        for i in range(len(pts)):
            if vol.IsPointInside(pts[i], tol, True):
                nc.Add(pts[i], colors[i])
            else:
                if not PCCopy: pcOuter.Add(pts[i],colors[i])
    else:
        
        for i in range(len(pts)):
            if vol.IsPointInside(pts[i], tol, True):
                nc.Add(pts[i])
            else:
                if not PCCopy: pcOuter.Add(pts[i])
            

    if nc is not None:
         newPc = sc.doc.Objects.AddPointCloud(nc)
         rs.UnselectAllObjects()
         rs.SelectObject(newPc)
         if not PCCopy: sc.doc.Objects.Replace(pcId, pcOuter)
         
    sc.doc.Views.Redraw()
    
    
if __name__ =="__main__":
    CloudVolumeIntersect()