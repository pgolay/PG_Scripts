import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino


def SectionPlaneDynamic():
    
    def get_inputs():
        
        go = Rhino.Input.Custom.GetObject()
        go.EnablePreSelect(True, True)
        
        go.GeometryFilter = Rhino.DocObjects.ObjectType.EdgeFilter.Curve
        go.SetCommandPrompt("Select a curve or surface edge.")
        rc = go.Get()
        
        if go.CommandResult() != Rhino.Commands.Result.Success:
            return go.CommandResult()
           
        if rc==Rhino.Input.GetResult.Object:
            objRef = go.Object(0)
            return objRef
                 
    inputs = get_inputs()
    
    if inputs == Rhino.Commands.Result.Cancel: return
    
    id = inputs.ObjectId
    idx = inputs.GeometryComponentIndex.Index
    if idx == -1:
        crv = sc.doc.Objects.Find(id).Geometry
    else :     
        Brep = sc.doc.Objects.Find(id).Geometry
        crv = Brep.Edges[idx].ToNurbsCurve()
    
    List = ["Surface", "Mesh"]
    
    while True:

        PlaneTypeIdx = 0
        #Stored values if any
        if sc.sticky.has_key("PlaneTypeIdx"):
            PlaneTypeIdx  = sc.sticky["PlaneTypeIdx"]
            
        crntPlane = rs.ViewCPlane()
        
        gp = Rhino.Input.Custom.GetPoint()
        gp.Constrain(crv,True)
        optToggleType = Rhino.Input.Custom.OptionToggle(PlaneTypeIdx, "Surface","Mesh")
        gp.AddOptionToggle("PlaneType", optToggleType)
        
        while True:
            rc = gp.Get()
            if gp.CommandResult() != Rhino.Commands.Result.Success:
                return gp.CommandResult()
               
            if rc == Rhino.Input.GetResult.Point:
                pt = gp.Point()
                par = crv.ClosestPoint(pt)[1]
                frame = crv.PerpendicularFrameAt(par)[1]
                rs.ViewCPlane(rs.CurrentView(), frame)
                center_mode = Rhino.Input.GetBoxMode.Center
                get_rc, apts = Rhino.Input.RhinoGet.GetRectangle(center_mode, frame.Origin, None)
                if get_rc != Rhino.Commands.Result.Success: 
                    return get_rc
                if not apts: return
                
                if PlaneTypeIdx == 0 :
                    rs.AddSrfPt(apts)
                else:
                    rs.AddMesh( apts, [[0,1,2,3]])
                
                rs.ViewCPlane(rs.CurrentView(),crntPlane)
                break
            elif rc == Rhino.Input.GetResult.Option:
                PlaneTypeIdx = optToggleType.CurrentValue
                sc.sticky["PlaneTypeIdx"]  = PlaneTypeIdx
                
            continue
   
 
    
SectionPlaneDynamic()