import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino


def SectionPlanes():
    
    """
    Get the curve GetObject, and then loop through GetPoint points on the curve.
    Size defaults to 12" in imperial files, 300mm in metric
    At each point find a perp frame and place a planar srf or mesh on the plane
    
    """
    
    def get_inputs():
        
        metric_sys = ["Millimeter", "Centimeter", "Meter"]
        imp_sys = ["Inch", "Foot"]
        
        sys = sc.doc.GetUnitSystemName(modelUnits=True, capitalize=True, singular=True, abbreviate=False)
        
        if sys == "Millimeter":
            XSize = 300
            YSize = 300
            
        if sys == "Centimeter":
            XSize = 30
            YSize = 30
            
        if sys == "Meter":
            XSize = .30
            YSize = .30
            
        if sys == "Foot":
            XSize = 1.0
            YSize = 1.0
            
        if sys == "Inch":
            XSize = 12
            YSize = 12
        
        go = Rhino.Input.Custom.GetObject()
        go.EnablePreSelect(True, True)
        
        if sc.sticky.has_key("OldX"):
            XSize = sc.sticky["OldX"]
        if sc.sticky.has_key("OldY"):
            YSize = sc.sticky["OldY"]
            
        dblOptionX = Rhino.Input.Custom.OptionDouble(XSize)
        dblOptionY = Rhino.Input.Custom.OptionDouble(YSize)
        
        go.AddOptionDouble("XSize", dblOptionX)
        go.AddOptionDouble("YSize", dblOptionY)
        go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve.EdgeFilter.Curve

        while True:
            
            rc = go.Get()
            
            if go.CommandResult() != Rhino.Commands.Result.Success:
                return go.CommandResult()
               
            if rc==Rhino.Input.GetResult.Object:
                objRef = go.Object(0)
                XSize = dblOptionX.CurrentValue
                YSize = dblOptionY.CurrentValue
                break
                 
            elif rc==Rhino.Input.GetResult.Option:
                XSize = dblOptionX.CurrentValue
                YSize = dblOptionY.CurrentValue
            continue
            
        sc.sticky["OldX"] = XSize
        sc.sticky["OldY"] = YSize
        return objRef, XSize, YSize

    inputs = get_inputs()
    
    if inputs == Rhino.Commands.Result.Cancel: return
    
    objRef = inputs[0]
    if objRef.GeometryComponentIndex.ComponentIndexType.BrepEdge:
        crv = objRef.Geometry().ToNurbsCurve()
    else:
        crv = objRef.Geometry
        
    XSize  = inputs[1]
    YSize = inputs[2]
    
    while True:
        PlaneTypeIdx = 0
        if sc.sticky.has_key("PlaneTypeIdx"):
            PlaneTypeIdx  = sc.sticky["PlaneTypeIdx"]
        gp = Rhino.Input.Custom.GetPoint()
        gp.Constrain(crv,True)
        dblOptionX = Rhino.Input.Custom.OptionDouble(XSize)
        dblOptionY = Rhino.Input.Custom.OptionDouble(YSize)
        optToggleType = Rhino.Input.Custom.OptionToggle(PlaneTypeIdx, "Surface","Mesh")
        gp.AddOptionToggle("PlaneType", optToggleType)
        
        gp.AddOptionDouble("XSize", dblOptionX)
        gp.AddOptionDouble("YSize", dblOptionY)
        
        rc = gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return gp.CommandResult()
           
        if rc == Rhino.Input.GetResult.Point:
            pt = gp.Point()
            XSize = dblOptionX.CurrentValue
            YSize = dblOptionY.CurrentValue
            sc.sticky["OldX"] = XSize
            sc.sticky["OldY"] = YSize
            
            par = crv.ClosestPoint(pt)[1]
            frame = crv.PerpendicularFrameAt(par)[1]

            vecX = frame.XAxis * XSize/2
            vecX.Reverse()
            vecY = frame.YAxis * YSize/2
            vecY.Reverse()
            
            frame.Translate (vecX + vecY)
            
            if PlaneTypeIdx == 0:
                rs.AddPlaneSurface(frame,XSize,YSize)
            else:
                p0 = frame.Origin
                p1 = p0 - (vecX * 2)
                p3 = p0 - ((vecX * 2) + (vecY * 2))
                p2 = p0 - (vecY * 2)
                rs.AddMesh([p0,p1,p2,p3],[(0,1,3,2)])
            
        elif rc ==  Rhino.Input.GetResult.Option:
            XSize = dblOptionX.CurrentValue
            YSize = dblOptionY.CurrentValue
            PlaneTypeIdx = optToggleType.CurrentValue
            sc.sticky["PlaneTypeIdx"]  = PlaneTypeIdx
        
    pass
SectionPlanes()