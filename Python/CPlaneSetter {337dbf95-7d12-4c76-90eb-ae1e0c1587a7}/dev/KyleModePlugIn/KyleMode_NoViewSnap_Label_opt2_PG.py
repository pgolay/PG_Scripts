import rhinoscript.userinterface
import rhinoscript.geometry
import Rhino
import scriptcontext
import System
import math
import time
import rhinoscriptsyntax as rs

__commandname__ = "AutoCPlane"

def GetConstructionPlaneName(plane):
    vec = Rhino.Geometry.Vector3d
    
    dirs = [vec(0,0,1), vec(0,0,-1), vec(0,1,0), vec(0,-1,0), vec(1,0,0), vec(-1,0,0)]
    names = [ "Top", "Bottom", "Back", "Front", "Right", "Left"]
    zippy = zip(dirs,names)
    
    Z = plane.ZAxis
    for item in zippy:
        if Z == item[0]:
            return item[1]
    
    

def CustomOverlayDraw(sender, args):
    try:
        vp = args.Viewport
        
        #check that the view is not a layout
        if  vp.ParentView is Rhino.Display.RhinoPageView:
            return
            
        #The viewport size
        size = vp.Size
        
        # get the current cplane name
        plane_CXY = vp.ConstructionPlane()
        cpName = GetConstructionPlaneName(plane_CXY)
        rect_color = System.Drawing.Color.Pink
        font_color = System.Drawing.Color.Black
        
        if cpName == "Top":
            rect_color = System.Drawing.Color.Blue
            font_color = System.Drawing.Color.White
        elif cpName == "Bottom":
            rect_color = System.Drawing.Color.LightBlue
            font_color = System.Drawing.Color.Black
        elif cpName == "Left":
            rect_color = System.Drawing.Color.Pink
            font_color = System.Drawing.Color.Black
        elif cpName == "Right":
            rect_color = System.Drawing.Color.DarkRed
            font_color = System.Drawing.Color.White
        elif cpName == "Back":
            rect_color = System.Drawing.Color.LightGreen
            font_color = System.Drawing.Color.Black
        else:
            rect_color = System.Drawing.Color.DarkGreen
            font_color = System.Drawing.Color.White
            
            
        #set the dimesnions of the label and text- (TO DO:figure this out better)
        rect_h = 14
        rect_w = 48
        fontheight = .9*rect_h
        
        # the screen points to place the text
        screen_pt = Rhino.Geometry.Point2d(size.Width-5-(rect_w/2), rect_h-1)
        
        r = System.Drawing.Rectangle(size.Width-5-rect_w, rect_h-7, rect_w, rect_h)
        
        args.Display.Draw2dRectangle(r, rect_color, 0, rect_color)
        args.Display.Draw2dText(cpName, font_color, screen_pt, True, fontheight)
        
    except Exception as e:
        print 'Error: ' + str(e)
    

def find_nearest_axis(vecDir, plane, cLocation):
    #vecDir is the camera UP vector
    #plane is the current CPlane
    #cLocation is the camera location
    pi = math.pi
    testPt1 = rs.PlaneClosestPoint(plane,cLocation)
    testPt2 = rs.PlaneClosestPoint(plane,cLocation+vecDir)
    
    testVec = (testPt2-testPt1)
    testVec.Unitize()
    
    v_list = [plane.XAxis, -1*plane.XAxis, plane.YAxis, -1*plane.YAxis]
    ang = pi
    n = 0
    anglist = []
    
    for v in v_list:
        test = Rhino.Geometry.Vector3d.VectorAngle(v, testVec)
        anglist.append(test)
        if test < ang: 
            ang = test
            idx = n
        n = n + 1
 #    scriptcontext.doc.Views.Redraw()
    
    #test to see if the vector angle is clockwise or counter-clockwise
    XVec = Rhino.Geometry.Vector3d.CrossProduct(v_list[idx],testVec)
    dir = Rhino.Geometry.Vector3d.IsParallelTo(plane.ZAxis, XVec)
    
    #print "dir = " ,dir
    if dir != -1:
        ang = -ang
    X = Rhino.RhinoMath.ToDegrees(ang)
    
    return ang, v_list[idx]


def find_nearest_plane(VecDir, v_list,p_list):
    n = 0
    idx = -1
    ang = 90
    for vec in v_list:
        test = Rhino.RhinoMath.ToDegrees( Rhino.Geometry.Vector3d.VectorAngle(vec, VecDir))
        #print deg
        if test > ang:
            ang = test
            idx = n
            
        n = n + 1
    return p_list[idx]
    
def view_plane():
    vp = scriptcontext.doc.Views.ActiveView.ActiveViewport
    vecDir = vp.CameraDirection
    crnt_plane = vp.ConstructionPlane()
    vecUp = vp.CameraUp
    cLocation = vp.CameraLocation
    tLocation = vp.CameraTarget 
    length = abs((cLocation-tLocation).Length)
    vec_new = crnt_plane.ZAxis*length
    vp.ChangeToParallelProjection(True)
    vp.SetCameraLocation(tLocation + vec_new, False)
    vp.SetCameraDirection(-1*crnt_plane.ZAxis, False)
    vp.SetCameraTarget(tLocation,  True)
    #tLocation = vp.CameraTarget
    vi = Rhino.DocObjects.ViewportInfo(vp)
    ang, vec = find_nearest_axis(vi.CameraUp, crnt_plane, cLocation)
    vi.SetCameraUp(vec)
    test_up = vi.CameraUp
    vp.Rotate(ang, crnt_plane.ZAxis, tLocation)

 
def CplaneSetter(vp=None, doc=None, angle=10):
    
    if not vp:
        vp = scriptcontext.doc.Views.ActiveView.ActiveViewport

    v_list = []
    p_list = []
    pO = Rhino.Geometry.Point3d(0,0,0)
    
    vecX = Rhino.Geometry.Vector3d(1,0,0)
    vecY = Rhino.Geometry.Vector3d(0,1,0)
    vecZ = Rhino.Geometry.Vector3d(0,0,1)
    negX = Rhino.Geometry.Vector3d(-1,0,0)
    negY = Rhino.Geometry.Vector3d(0,-1,0)
    negZ = Rhino.Geometry.Vector3d(0,0,-1)

    plane = Rhino.Geometry.Plane(pO,vecX, vecY)
    p_list.append(plane)
    v_list.append(vecZ)
    
    plane = Rhino.Geometry.Plane(pO,vecX, negY)
    p_list.append(plane)
    v_list.append(negZ)
    
    plane = Rhino.Geometry.Plane(pO,vecY, vecZ)
    p_list.append(plane)
    v_list.append(vecX)
    
    plane = Rhino.Geometry.Plane(pO,negY, vecZ)
    p_list.append(plane)
    v_list.append(negX)
    
    plane = Rhino.Geometry.Plane(pO, vecX, vecZ)
    p_list.append(plane)
    v_list.append(negY)
    
    plane = Rhino.Geometry.Plane(pO, negX, vecZ)
    p_list.append(plane)
    v_list.append(vecY)
    
    vp = scriptcontext.doc.Views.ActiveView.ActiveViewport
    crnt_plane = vp.ConstructionPlane()
    
    v1 = crnt_plane.ZAxis
    v2 = vp.CameraDirection
    
    X = Rhino.RhinoMath.ToDegrees(Rhino.Geometry.Vector3d.VectorAngle(v1,v2))
    vi = Rhino.DocObjects.ViewportInfo(vp)
 
    #    if X < 170:
    #        cLocation = vp.CameraLocation
    #        tLocation = vp.CameraTarget 
    #        vecCam = Rhino.Geometry.Vector3d(tLocation-cLocation)
    #        vp.ChangeToPerspectiveProjection(True, 50)
    #        vp.SetCameraLocation(tLocation + vecCam, False)
        
       #if X < 135:
           
    tempPlane = find_nearest_plane(v2, v_list, p_list)
    #if tempPlane: vp.SetConstructionPlane(tempPlan)
    #v3 = vp.ConstructionPlane().ZAxis 
    v3 = tempPlane.ZAxis
    v4 = vp.CameraDirection
    Z = Rhino.RhinoMath.ToDegrees(Rhino.Geometry.Vector3d.VectorAngle(vecZ,v4))
    Y = Rhino.RhinoMath.ToDegrees(Rhino.Geometry.Vector3d.VectorAngle(v3,v4))
    
    if Y > 180-angle: 
        if tempPlane: 
            vp.SetConstructionPlane(tempPlane)
        #view_plane()
        #print "PingPong"
            scriptcontext.doc.Views.Redraw()
    else:
        vp.SetConstructionPlane(Rhino.Geometry.Plane.WorldXY)
        
    if not doc:
            scriptcontext.doc.Views.Redraw()

def hack(sender, e):
    vp = e.Viewport
    doc = e.RhinoDoc
    angle = int(scriptcontext.sticky["KyleAngle"])
    MouseDownCallback = True
    MouseUpCallback.rotated = True

class MouseUpCallback(Rhino.UI.MouseCallback):
    
    rotated = False
    
    def __init__(self):
        if scriptcontext.sticky.has_key("KyleMouseUpCallback") and (scriptcontext.sticky["KyleMouseUpCallback"] is not None):
            scriptcontext.sticky["KyleMouseUpCallback"].Enabled = False
        scriptcontext.sticky["KyleMouseUpCallback"] = self
        self.Enabled = True
    
    def OnMouseUp(self, e): #Rhino.UI.MouseCallbackEventArgs
        try:
            if e.Button == System.Windows.Forms.MouseButtons.Right:
                CplaneSetter(e.View.ActiveViewport, e.View.Document, int(scriptcontext.sticky["KyleAngle"]))
        
            MouseUpCallback.rotated = False
            
        except Exception, e:
            print "Error: " + str(e)
            
            
class MouseDownCallback(Rhino.UI.MouseCallback):
    
    rotated = True
    
    def __init__(self):
        if scriptcontext.sticky.has_key("KyleMouseDownCallback") and (scriptcontext.sticky["KyleMouseDownCallback"] is not None):
            scriptcontext.sticky["KyleMouseDownCallback"].Enabled = False
        scriptcontext.sticky["KyleMouseDownCallback"] = self
        self.Enabled = True
    
    def OnMouseDown(self, e): #Rhino.UI.MouseCallbackEventArgs
        try:
            if e.Button == System.Windows.Forms.MouseButtons.Right:
                #CplaneSetter(e.View.ActiveViewport, e.View.Document, int(scriptcontext.sticky["KyleAngle"]))
                func = CustomOverlayDraw
                Rhino.Display.DisplayPipeline.DrawForeground += func
                scriptcontext.sticky["Label"] = func
                CustomOverlayDraw
            
            MouseUpCallback.rotated = False
            
        except Exception, e:
            print "Error: " + str(e)


#CplaneSetter()
def RunCommand( is_interactive ):
    if( scriptcontext.sticky.has_key("hack") ):
        Rhino.Display.DisplayPipeline.CalculateBoundingBox -= scriptcontext.sticky["hack"]
        scriptcontext.sticky.Remove("hack")

        if( scriptcontext.sticky.has_key("Label") ):# and ( scriptcontext.sticky[KEYOLDSCALE] or scriptcontext.sticky[KEYOLDLEN]):
            func = scriptcontext.sticky["Label"]
            Rhino.Display.DisplayPipeline.DrawForeground -= func
            scriptcontext.sticky.Remove("Label")
        
        if scriptcontext.sticky.has_key("KyleMouseUpCallback") and (scriptcontext.sticky["KyleMouseUpCallback"] is not None):
            scriptcontext.sticky["KyleMouseUpCallback"].Enabled = False
            del scriptcontext.sticky["KyleMouseUpCallback"]
        print "AutoCPlane mode is off."
    else:
        if scriptcontext.sticky.has_key("KyleAngle"):
            defAngle = scriptcontext.sticky["KyleAngle"]
        else: defAngle = 10
        
        angle = rs.GetInteger("Set CPlane swap angle", defAngle, 1, 44)
        scriptcontext.sticky["KyleAngle"] = angle
        
        scriptcontext.sticky["hack"] = hack
        Rhino.Display.DisplayPipeline.CalculateBoundingBox += hack
        
        MouseDownCallback()
        MouseUpCallback()
        
        print "AutoCPlane mode is on."
    scriptcontext.doc.Views.Redraw() 

RunCommand(True)