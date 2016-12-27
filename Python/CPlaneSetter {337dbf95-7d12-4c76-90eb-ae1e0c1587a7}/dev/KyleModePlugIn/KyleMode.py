import rhinoscript.userinterface
import rhinoscript.geometry
import Rhino
import scriptcontext
import System
import math
import time

__commandname__ = "KyleMode"


def find_nearest_axis(vecDir, plane, cLocation):
    #vecDir is the camera UP vector
    #plane is the current CPlane
    #cLocation is the camera location
    
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
    vp.SetCameraTarget(tLocation)
    #tLocation = vp.CameraTarget
    vi = Rhino.DocObjects.ViewportInfo(vp)
    ang, vec = find_nearest_axis(vi.CameraUp, crnt_plane, cLocation)
    vi.SetCameraUp(vec)
    test_up = vi.CameraUp
    vp.Rotate(ang, crnt_plane.ZAxis, tLocation)

 
def CplaneSetter(vp=None, doc=None):
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
 
    if X < 170:
        cLocation = vp.CameraLocation
        tLocation = vp.CameraTarget 
        vecCam = Rhino.Geometry.Vector3d(tLocation-cLocation)
        vp.ChangeToPerspectiveProjection(True, 50)
        vp.SetCameraLocation(tLocation + vecCam, False)
        
    #if X < 135:
    tempPlane = find_nearest_plane(v2, v_list, p_list)
    #if tempPlane: vp.SetConstructionPlane(tempPlan)
    #v3 = vp.ConstructionPlane().ZAxis 
    v3 = tempPlane.ZAxis
    v4 = vp.CameraDirection
    Z = Rhino.RhinoMath.ToDegrees(Rhino.Geometry.Vector3d.VectorAngle(vecZ,v4))
    Y = Rhino.RhinoMath.ToDegrees(Rhino.Geometry.Vector3d.VectorAngle(v3,v4))
    
    if Y > 170: 
        if tempPlane: vp.SetConstructionPlane(tempPlane)
        view_plane()
        #print "PingPong"
        scriptcontext.doc.Views.Redraw()
    else:
        vp.SetConstructionPlane(Rhino.Geometry.Plane.WorldXY)
        
    if not doc:
            scriptcontext.doc.Views.Redraw()

def hack(sender, e):
    vp = e.Viewport
    doc = e.RhinoDoc
    CplaneSetter(vp, doc)
    
   
#CplaneSetter()
def RunCommand( is_interactive ):
    if( scriptcontext.sticky.has_key("hack") ):
        Rhino.Display.DisplayPipeline.CalculateBoundingBox -= scriptcontext.sticky["hack"]
        scriptcontext.sticky.Remove("hack")
        print "Kyle mode is off"
    else:
        scriptcontext.sticky["hack"] = hack
        Rhino.Display.DisplayPipeline.CalculateBoundingBox += hack
        print "Kyle mode is on"
    scriptcontext.doc.Views.Redraw() 
    return 0
    
RunCommand(True)
