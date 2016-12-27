import Rhino
import scriptcontext
import System
import math
import rhinoscriptsyntax as rs


__commandname__ = "EllipseViewAngle"

# RunCommand is the called when the user enters the command name in Rhino.
# The command name is defined by the filname minus "_cmd.py"

def RunCommand( is_interactive ):
    #line_color = System.Drawing.Color.FromArgb(255,0,0)
    
    line_color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
    arc_color = scriptcontext.doc.Layers.CurrentLayer.Color
    cen_color = System.Drawing.Color.FromArgb(50,0,150)

    oldVA = 45
            # retrieve a previously used number if any
    if scriptcontext.sticky.has_key("oldVA"):
        oldVA = scriptcontext.sticky["oldVA"]
    
    VA = rs.GetReal("View angle?", number = oldVA)
    if not VA: return
    scriptcontext.sticky["oldVA"] = VA
    
    rc, pt_start = Rhino.Input.RhinoGet.GetPoint("Center of ellipse.", False)
    if( rc!=Rhino.Commands.Result.Success ): return
    
    view = scriptcontext.doc.Views.ActiveView
    plane = view.ActiveViewport.ConstructionPlane()
    plane.Origin = pt_start
    factor = abs(math.sin(Rhino.RhinoMath.ToRadians(VA)))
    
    def GetPointDynamicDrawFunc( sender, args ):
        plane = scriptcontext.doc.Views.ActiveView.ActiveViewport.ConstructionPlane()
        #plane.Origin = pt_start
        #draw a line from the second picked point to the current mouse point
        pt = args.CurrentPoint
        crnt_vector  = Rhino.Geometry.Vector3d( pt.X - pt_start.X, pt.Y - pt_start.Y,  pt.Z - pt_start.Z )
        
        temp = Rhino.Geometry.Vector3d( pt.X - pt_start.X, pt.Y - pt_start.Y,  pt.Z - pt_start.Z )
        temp.Unitize()
        temp.PerpendicularTo(crnt_vector)
        vec90 = temp*factor
        
        X =  pt_start + crnt_vector
        Y =  pt_start + vec90
        
        args.Display.DrawPoint(pt_start, 0, 6, line_color)
        args.Display.DrawPoint(X, 0, 5, line_color)
        args.Display.DrawPoint(Y, 0, 5, line_color)
        args.Display.DrawPolyline( [args.CurrentPoint, pt_start , Y], line_color,1)
        
        #draw an ellipse from these three points pt_start, X, Y
        ellipse = Rhino.Geometry.Ellipse(pt_start, X, Y)
        args.Display.DrawCurve(ellipse.ToNurbsCurve(), arc_color, 2)
        
    gp = Rhino.Input.Custom.GetPoint()
    gp.SetBasePoint(pt_start, True)
    gp.ConstrainToConstructionPlane(True)
    gp.DynamicDraw += GetPointDynamicDrawFunc
    gp.Get()
    
    if( gp.CommandResult() == Rhino.Commands.Result.Success ):
        plane = scriptcontext.doc.Views.ActiveView.ActiveViewport.ConstructionPlane()
        pt = gp.Point()
        crnt_vector = Rhino.Geometry.Vector3d( pt.X - pt_start.X, pt.Y - pt_start.Y,  pt.Z - pt_start.Z )
        temp = Rhino.Geometry.Vector3d( pt.X - pt_start.X, pt.Y - pt_start.Y,  pt.Z - pt_start.Z )
        temp.Unitize()
        temp.PerpendicularTo(crnt_vector)
        
        vec90 = temp*factor
        
        X =  pt_start + crnt_vector
        Y =  pt_start + vec90
        
        ellipse = Rhino.Geometry.Ellipse(pt_start, X, Y)
        scriptcontext.doc.Objects.AddEllipse(ellipse)
        scriptcontext.doc.Views.Redraw()


