import Rhino
import scriptcontext
import System
import math
import rhinoscriptsyntax as rs


def EllipseViewAngle():
    #line_color = System.Drawing.Color.FromArgb(255,0,0)
    pi = math.pi
    line_color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
    arc_color = scriptcontext.doc.Layers.CurrentLayer.Color
    cen_color = System.Drawing.Color.FromArgb(50,0,150)

    VA = 45
            # retrieve a previously used number if any
    if scriptcontext.sticky.has_key("oldVA"):
        VA = scriptcontext.sticky["oldVA"]
        
    crnt_axis = True
    if scriptcontext.sticky.has_key("oldAxis"):
        print "has key"
        crnt_axis = scriptcontext.sticky["oldAxis"]
    
    rc, pt_start = Rhino.Input.RhinoGet.GetPoint("Center of ellipse.", False)
    if( rc!=Rhino.Commands.Result.Success ): return
    
    view = scriptcontext.doc.Views.ActiveView
    plane = view.ActiveViewport.ConstructionPlane()
    plane.Origin = pt_start

    
    def GetPointDynamicDrawFunc( sender, args ):
        plane = scriptcontext.doc.Views.ActiveView.ActiveViewport.ConstructionPlane()
        #plane.Origin = pt_start
        #draw a line from the second picked point to the current mouse point
        pt = args.CurrentPoint
        crnt_vector  = Rhino.Geometry.Vector3d( pt.X - pt_start.X, pt.Y - pt_start.Y,  pt.Z - pt_start.Z )
        
        temp = Rhino.Geometry.Vector3d( pt.X - pt_start.X, pt.Y - pt_start.Y,  pt.Z - pt_start.Z )
        temp.Unitize()
        temp.Rotate(pi/2, plane.ZAxis)
        #temp.PerpendicularTo(crnt_vector)
        vec90 = temp*factor*crnt_vector.Length
        
        X =  pt_start + crnt_vector
        Y =  pt_start + vec90
        
        args.Display.DrawPoint(pt_start, 0, 6, line_color)
        args.Display.DrawPoint(X, 0, 5, line_color)
        args.Display.DrawPoint(Y, 0, 5, line_color)
        args.Display.DrawPolyline( [args.CurrentPoint, pt_start , Y], line_color,1)
        
        #draw an ellipse from these three points pt_start, X, Y
        ellipse = Rhino.Geometry.Ellipse(pt_start, X, Y)
        args.Display.DrawCurve(ellipse.ToNurbsCurve(), arc_color, 2)
        
    while True:
        gp = Rhino.Input.Custom.GetPoint()
        
        dblOptionAng = Rhino.Input.Custom.OptionDouble(VA)
        gp.AddOptionDouble("ViewAngle", dblOptionAng)
     
        optToggleAxis = Rhino.Input.Custom.OptionToggle(crnt_axis, "Long","Short")
        gp.AddOptionToggle("Axis", optToggleAxis)
        
        gp.SetBasePoint(pt_start, True)
        gp.ConstrainToConstructionPlane(True)
        gp.AcceptNumber(True, False)
        
        gp.DynamicDraw += GetPointDynamicDrawFunc
        
        factor = abs(math.sin(Rhino.RhinoMath.ToRadians(VA)))

        if crnt_axis: #Short
            factor = 1/factor
            
        rc = gp.Get()
        
        if gp.CommandResult() !=  Rhino.Commands.Result.Success :
            return rc
            
        if rc == Rhino.Input.GetResult.Point:
            plane = scriptcontext.doc.Views.ActiveView.ActiveViewport.ConstructionPlane()
            pt = gp.Point()
            crnt_vector = Rhino.Geometry.Vector3d( pt.X - pt_start.X, pt.Y - pt_start.Y,  pt.Z - pt_start.Z )
            temp = Rhino.Geometry.Vector3d( pt.X - pt_start.X, pt.Y - pt_start.Y,  pt.Z - pt_start.Z )
            temp.Unitize()
            temp.Rotate(pi/2, plane.ZAxis)
            #temp.PerpendicularTo(crnt_vector)
            
            vec90 = temp*factor*crnt_vector.Length
            
            X =  pt_start + crnt_vector
            Y =  pt_start + vec90
            
            ellipse = Rhino.Geometry.Ellipse(pt_start, X, Y)
            scriptcontext.doc.Objects.AddEllipse(ellipse)
            break
            
        elif rc == Rhino.Input.GetResult.Option:
            print "option"
            VA = dblOptionAng.CurrentValue
            scriptcontext.sticky["oldVA"]= VA
                
            crnt_axis = optToggleAxis.CurrentValue
            scriptcontext.sticky["oldAxis"]= crnt_axis
            continue
            
        elif rc == Rhino.Input.GetResult.Number:
            print "number"
            VA  = gp.Number()
            scriptcontext.sticky["oldVA"]= VA
            continue
            
    scriptcontext.doc.Views.Redraw()


EllipseViewAngle()