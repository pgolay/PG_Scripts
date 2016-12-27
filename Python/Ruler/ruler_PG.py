import Rhino
import scriptcontext
import System
import rhinoscriptsyntax as rs



def UnitSystemName(int_sys):
    if int_sys > 11:
        return "units"
    else:
        unit_list = ["units", "u","mm","cm","m","km", "uIn", "mil", "in","ft","mile","yd"]
        return unit_list[int_sys]


def SetViewScale():
        #----------------------
    #Monitor specific.
    px_density_inch = 141.5
    px_density_cm = 55.82
    dot_pitch = 0.17912
    #----------------------
    #----------------------
    
def get_ruler_inputs():

        
    
    KEYOLDSCALE = "OldScale"
    KEYOLDLEN = "OldLength"
    KEYOLDPITCH = "OldPitch"
    KEYOLDCOLOR= "OldColor"



    res_list = [
    "Resolution Diag   Pitch(" + chr(181) +"m)",
    "960X640    3.5     77",
    "1024X600   10.1    216",
    "1024X768   9.7     192",
    "1024X768   15.0    297",
    "1024X768   17.0    337",
    "1280X720   13.3    230",
    "1280X768   15.4    262",
    "1280X800   12.1    204",
    "1280X800   13.3    224",
    "1280X800   14.1    237",
    "1280X800   15.4    259",
    "1280X800   17.0    286",
    "1280X1024  17.0    264",
    "1280X1024  18.1    280 ",
    "1280X1024  19.0    294 ",
    "1366X768   11.6    188 ",
    "1366X768   13.3    215 ",
    "1366X768   14.0    227 ",
    "1366X768   15.6    253 ",
    "1366X768   18.5    300 ",
    "1360X768   19.0    308 ",
    "1440X900   13.3    198 ",
    "1440X900   14.1    211 ",
    "1440X900   15.4    230 ",
    "1440X900   17.0    254 ",
    "1440X900   19.0    285 ",
    "1400X1050  15.0    214 ",
    "1400X1050  20.1    292 ",
    "1600X900   13.1    181 ",
    "1600X900   14.0    194 ",
    "1600X900   15.4    213 ",
    "1600X900   17.3    239 ",
    "1600X900   20.0    277 ",
    "1600X1000  22.0    296 ",
    "1680X1050  15.4    197 ",
    "1680X1050  17.0    218 ",
    "1680X1050  19.0    244 ",
    "1680X1050  20.1    258 ",
    "1680X1050  21.0    269 ",
    "1680X1050  22.0    282 ",
    "1600X1200  15.0    191 ",
    "1600X1200  20.1    255 ",
    "1600X1200  21.3    270 ",
    "1920X1080  13.1    151 ",
    "1920X1080  15.6    180 ",
    "1920X1080  16.4    189 ",
    "1920X1080  21.5    248 ",
    "1920X1080  23.0    265 ",
    "1920X1080  23.6    272 ",
    "1920X1080  24.0    277 ",
    "1920X1080  24.6    284 ",
    "1920X1080  27.0    311 ",
    "1920X1200  15.4    173 ",
    "1920X1200  17.0    191 ",
    "1920X1200  22.0    247 ",
    "1920X1200  23.0    258 ",
    "1920X1200  24.0    270 ",
    "1920X1200  25.5    287 ",
    "1920X1200  27.0    303 ",
    "2048X1152  23.0    249 ",
    "2560X1440  27.0    233 ",
    "2560X1600  30.0    250 ",
    "3840X2400  22.2    125 ",]

#    result = rs.ListBox(res_list)
#    if result: 
#        print  res_list.index(result)
#        X = result.rpartition(chr(32))
#        Y = X[2]
#        if Y.isdigit:
#            print int(Y)/1000

    def stickysetting(name, value_if_missing):
        if scriptcontext.sticky.has_key(name): return scriptcontext.sticky[name]
        return value_if_missing
    

        
        
    blnScale = stickysetting(KEYOLDSCALE, True)
    blnLen = stickysetting(KEYOLDLEN, True)
    dot_pitch = stickysetting(KEYOLDPITCH, .179)
    crnt_color = stickysetting(KEYOLDCOLOR, System.Drawing.Color.LightBlue)
    #listIndex = stickysetting(KEYSETPITCH, 1)
    #intSegs = stickysetting(KEYOLDSEGS, 6)
    def dot_pitch_options():
        
        go2 = Rhino.Input.Custom.GetOption()
        go2.SetCommandPrompt("Set Ruler options.")
        opt_list = ["List"]
        go2.Get()
        return go2.CommandResult() 
        


    go = Rhino.Input.Custom.GetOption()
    go.AcceptNothing( True )
    #go.EnablePressEnterWhenDonePrompt(False)

    go.SetCommandPrompt("Set Ruler options.")

    # set up the options
    
    ShowScaleOption = Rhino.Input.Custom.OptionToggle(blnScale, "No", "Yes")
    ShowLengthOption = Rhino.Input.Custom.OptionToggle(blnLen, "No", "Yes")
    DotPitchOption = Rhino.Input.Custom.OptionDouble(dot_pitch)
    ColorOption =  Rhino.Input.Custom.OptionColor(crnt_color)
    #boolOption = Rhino.Input.Custom.OptionToggle(True, "Off", "On")
 
    go.AddOptionToggle("ScaleDisplay",ShowScaleOption)
    go.AddOptionToggle("LengthDisplay",ShowLengthOption)
    go.AddOptionDouble("MonitorDotPitch", DotPitchOption)
   

    while True:
        # perform the get operation. This will prompt the user to
        # input a point, but also allow for command line options
        # defined above
        get_rc = go.Get()
        if go.CommandResult()!=Rhino.Commands.Result.Success:
            return go.CommandResult()

        elif get_rc==Rhino.Input.GetResult.Option:
            print go.OptionIndex()
            if go.OptionIndex()==3:
                continue
        break
        
    scriptcontext.sticky[KEYOLDSCALE] = ShowScaleOption.CurrentValue
    scriptcontext.sticky[KEYOLDLEN] = ShowLengthOption.CurrentValue
    scriptcontext.sticky[KEYOLDPITCH] = DotPitchOption.CurrentValue
    
    return  ShowScaleOption.CurrentValue, ShowLengthOption.CurrentValue, DotPitchOption.CurrentValue   

    
def CustomOverlayDraw(sender, args):
    
    blnShowScale = scriptcontext.sticky["OldScale"]
    blnShowLength = scriptcontext.sticky["OldLength"]
    dot_pitch = scriptcontext.sticky["OldPitch"] #http://pxcalc.com/
    
    color_test = Rhino.Display.ColorXYZ(.5,.5,.5,.5)
    #color_test = Rhino.Display.Color4f(.5,.5,.5,.5)
    #color_test.BlendTo(.5)
    vp = args.Viewport
    #check that the view jas a parallel projection
    if not vp.IsParallelProjection or vp.ParentView is Rhino.Display.RhinoPageView or not vp.IsPlanView:
        return
        
        #set up a screen to world transform. TO DO: sort out how this works per CPlane
        # to make it work in any view (currently Right is broken)
    s2w = vp.GetTransform(Rhino.DocObjects.CoordinateSystem.Screen, Rhino.DocObjects.CoordinateSystem.World)
    
    # get the unit system abbreviaion. TO DO: make these better.
    # int_sys = rs.UnitSystem()
    X = Rhino.UnitSystem.Millimeters

    int_sys = args.RhinoDoc.ModelUnitSystem.value__
    sys_abr = UnitSystemName(int_sys)
    
    #The viewport size
    size = vp.Size
    plane_CXY = vp.ConstructionPlane()
    if 5 > int_sys > 1: #metric
        #rect_w = px_density_cm*5
        rect_w = 40/dot_pitch
        full_scale = 40
    elif int_sys == 8: #Inch
        rect_w = 40.5/dot_pitch #px_density_inch*2
        full_scale = 40.5
    elif int_sys == 9:#Feet
        rect_w = .20/dot_pitch
        full_scale = .20
    elif int_sys == 19:#Yards
        rect_w = px_density_inch*1.7
    else:
        rect_w = px_density_inch*1.9725

    rect_h = rect_w/14
    line_w = rect_w/60
    fontheight = .9*rect_h
    rect_h = int(rect_h)
    rect_w = int(rect_w)
    line_w = int(line_w)
    
    pt0 = Rhino.Geometry.Point3d(size.Width-15, size.Height-15,0)
    pt1 = Rhino.Geometry.Point3d(pt0.X-rect_w, pt0.Y,0)
    pt2 = Rhino.Geometry.Point3d(pt1.X, pt0.Y-rect_h, 0)
    pt3 = Rhino.Geometry.Point3d(pt0.X, pt2.Y, 0)
    pts = [pt0, pt1, pt2, pt3]
    
    #Set up points for a line
    p1 = Rhino.Geometry.Point3d(pt0.X-(line_w/2), pt0.Y+(line_w/2),0)
    p2 = Rhino.Geometry.Point3d(pt1.X+(line_w/2), pt0.Y+(line_w/2),0)
    #set up points for the hash marks
    p3  = Rhino.Geometry.Point3d( p1.X , p1.Y  ,0 )
    p4 = Rhino.Geometry.Point3d( p1.X , p1.Y + 5,0 )
    p5 = Rhino.Geometry.Point3d( p2.X, p2.Y  ,0 )
    p6 = Rhino.Geometry.Point3d( p2.X , p2.Y + 5,0 )
    
    
    linePts = [p1,p2]
    polylinePts = [p4,p3,p5,p6]
    
    # the screen points to place the text
    screen_pt = Rhino.Geometry.Point2d((pt0.X+pt1.X)/2, (pt2.Y+(rect_h/2)))
    screen_pt2 = Rhino.Geometry.Point2d(80, size.Height-20)
    
    #Apply the transform to the rectangle and line points

    for pt in pts: pt.Transform(s2w)
    for pt in polylinePts: pt.Transform(s2w)

    #make the lines
    line = Rhino.Geometry.Line(linePts[0], linePts[1])
    p_line = Rhino.Geometry.Polyline(polylinePts)
    start_hash = Rhino.Geometry.Line(p3,p4)
    end_hash = Rhino.Geometry.Line(p5,p6)
    
    args.Display.PushDepthTesting(False)
    
    #draw the line and the polygon
    #args.Display.DrawPolygon(pts, System.Drawing.Color.LightBlue, True)
    if blnShowLength: args.Display.DrawPolygon(pts, System.Drawing.Color.LightBlue, True)
    if blnShowLength: args.Display.DrawPolyline(p_line, System.Drawing.Color.Black, line_w)
    #if blnShowLength: args.Display.DrawLine(line, System.Drawing.Color.Black, line_w)
    #args.Display.DrawPoint()
    
    # a new transform to allow for any Cplane:
    plane_WXY = Rhino.Geometry.Plane.WorldXY
    w2c = Rhino.Geometry.Transform.PlaneToPlane(plane_CXY, plane_WXY)
    
    # apply the transform before measuring the distance between points.
    for pt in pts: pt.Transform(w2c)
    #for pt in linePts: pt.Transform(w2c)
    
    # get the distance between the points.
    dist = abs(pts[0].X - pts[1].X)
    crnt_units = Rhino.RhinoDoc.ModelUnitSystem.GetValue(Rhino.RhinoDoc.ActiveDoc)
    mm_units = Rhino.UnitSystem.Millimeters
    #test = Rhino.RhinoMath.UnitScale(crnt_units, mm_units)
    factor = full_scale/(dist *Rhino.RhinoMath.UnitScale(crnt_units, mm_units))
    
    if round(factor,2) !=1:
        pass
     
    message_length = '%.2f' % dist + " " + sys_abr
    
    message_scale = "View scale: " + str(round(factor, 2))
    
    
    if blnShowLength: args.Display.Draw2dText(message_length, System.Drawing.Color.Black, screen_pt, True, fontheight)
    if blnShowScale: args.Display.Draw2dText(message_scale, System.Drawing.Color.Black, screen_pt2, True, fontheight)
    
    args.Display.PopDepthTesting()

def ToggleRuler():
    
    KEY = "ruler"
    KEYOLDSCALE = "OldScale"
    KEYOLDLEN = "OldLength"

    if( scriptcontext.sticky.has_key(KEY) ):# and ( scriptcontext.sticky[KEYOLDSCALE] or scriptcontext.sticky[KEYOLDLEN]):
        print "Rulers turned off."
        func = scriptcontext.sticky[KEY]
        Rhino.Display.DisplayPipeline.DrawForeground -= func
        scriptcontext.sticky.Remove(KEY)
    else:
        
        get_ruler_inputs()
        if scriptcontext.sticky[KEYOLDSCALE] or scriptcontext.sticky[KEYOLDLEN]:
            print "Rulers turned on for plan views."
            func = CustomOverlayDraw
            Rhino.Display.DisplayPipeline.DrawForeground += func
            scriptcontext.sticky["ruler"] = func
        else:
            print "No ruler options enabled. No rulers drawn."
        
    scriptcontext.doc.Views.Redraw()

if __name__=="__main__":
    ToggleRuler()