import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import math

def test():
    #makes a circle with the seam point aligned to CPlane Y
    
    PT_COUNT = 12
    RAD = 1
    pi = math.pi
        
        


    p1 = None

    while True:
        gp = Rhino.Input.Custom.GetPoint()
        if sc.sticky.has_key("PT_COUNT"):
            PT_COUNT = sc.sticky["PT_COUNT"]
        
        gp.SetCommandPrompt ("Center of circle")
        optIntCount = Rhino.Input.Custom.OptionInteger( PT_COUNT, True, 4)
        gp.AddOptionInteger("PointCount", optIntCount)
        rc = gp.Get()
    
        if gp.CommandResult()!=Rhino.Commands.Result.Success:
            return gp.CommandResult()
        elif  rc==Rhino.Input.GetResult.Option:
            PT_COUNT = optIntCount.CurrentValue
            sc.sticky["PT_COUNT"] = PT_COUNT
            continue
        else:
            
            p1 =  gp.Point()
            break
      
    if not p1: return

    while True:
        
        gp = Rhino.Input.Custom.GetPoint()
        if sc.sticky.has_key("RAD"):
            RAD = sc.sticky["RAD"]
        
        if sc.sticky.has_key("PT_COUNT"):
            PT_COUNT = sc.sticky["PT_COUNT"]
        gp.SetCommandPrompt ("Radius")
        gp.AcceptNumber(True, True)
        gp.AcceptNothing(True)
        
        optRad = Rhino.Input.Custom.OptionDouble(RAD)
        optIntCount = Rhino.Input.Custom.OptionInteger( PT_COUNT, True, 4)
        gp.AddOptionInteger("PointCount", optIntCount)
        gp.AddOptionDouble("Radius", optRad)
        gp.DrawLineFromPoint(p1, True)
        rc = gp.Get()
    
        if gp.CommandResult()!=Rhino.Commands.Result.Success:
            return gp.CommandResult()
        elif  rc==Rhino.Input.GetResult.Option:
            PT_COUNT = optIntCount.CurrentValue
            sc.sticky["PT_COUNT"] = PT_COUNT
            RAD= optRad.CurrentValue
            sc.sticky["RAD"] = RAD
            if  gp.OptionIndex()== optRad:
                break
            else:
                continue
        else:
            RAD = rs.Distance (p1, gp.Point())
            sc.sticky["RAD"] = RAD
            break
            
    pass
    plane = sc.doc.Views.ActiveView.ActiveViewport.ConstructionPlane()
    p2 = p1 + (plane.YAxis * RAD)
    plane.Origin = p1
    plane.Rotate( pi/2, plane.ZAxis)
    circle = Rhino.Geometry.Circle(plane, RAD)
    sc.doc.Objects.AddCircle(circle)
    sc.doc.Views.Redraw()
    pass
    
test()