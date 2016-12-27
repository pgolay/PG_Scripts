import rhinoscript.userinterface
import rhinoscript.geometry
import Rhino
import scriptcontext
import System
import math
import time
import rhinoscriptsyntax as rs

#__commandname__ = "KyleMode"


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

def signed_angle(v1, v2, sign):
    dot = rs.VectorDotProduct(v1, v2)
    det = v1.X*v2.Y*sign.Z + v2.X*sign.Y*v1.Z + sign.X*v1.Y*v2.Z - \
        v1.Z*v2.Y*sign.X - v2.Z*sign.Y*v1.X - sign.Z*v1.Y*v2.X
    return math.atan2(det, dot)

def make_readable(angle_rad):
    return str(round(math.degrees(angle_rad)))

    
def view_plane():
    vp = scriptcontext.doc.Views.ActiveView.ActiveViewport
    vecDir = vp.CameraDirection
    crnt_plane = vp.ConstructionPlane()
    vecUp = vp.CameraUp
    cLocation = vp.CameraLocation
    tLocation = vp.CameraTarget 
    length = abs((cLocation-tLocation).Length)
    vec_new = crnt_plane.ZAxis*length
    
    #vp.ChangeToParallelProjection(True)
    vp.SetCameraLocation(tLocation + vec_new, False)
    vp.SetCameraDirection(-1*crnt_plane.ZAxis, False)
    #vp.SetCameraTarget(tLocation)
    #tLocation = vp.CameraTarget
    
    if rs.IsVectorParallelTo(crnt_plane.ZAxis, Rhino.Geometry.Vector3d.ZAxis) != 0:
        
        vi = Rhino.DocObjects.ViewportInfo(vp)
        
        angle = signed_angle(vi.CameraUp, Rhino.Geometry.Vector3d.XAxis, Rhino.Geometry.Vector3d.ZAxis)
        
        rest_of_90 = angle % (math.pi*.5)
        if rest_of_90 > (math.pi*.5/2.0):
            rest_of_90 -= math.pi*.5
        
        if math.degrees(abs(rest_of_90)) < 5:
            vp.Rotate(rest_of_90, Rhino.Geometry.Vector3d.ZAxis, tLocation)
        
#    print vec
#    vi.SetCameraUp(vec)
#    test_up = vi.CameraUp
#    vp.Rotate(ang, crnt_plane.ZAxis, tLocation)

 
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
        #vp.ChangeToPerspectiveProjection(True, 50)
        #vp.SetCameraLocation(tLocation + vecCam, False)
        
    #if X < 135:
    tempPlane = find_nearest_plane(v2, v_list, p_list)
    #print tempPlane
    #if tempPlane: vp.SetConstructionPlane(tempPlan)
    #v3 = vp.ConstructionPlane().ZAxis 
    v3 = tempPlane.ZAxis
    v4 = vp.CameraDirection
    Z = Rhino.RhinoMath.ToDegrees(Rhino.Geometry.Vector3d.VectorAngle(vecZ,v4))
    Y = Rhino.RhinoMath.ToDegrees(Rhino.Geometry.Vector3d.VectorAngle(v3,v4))
    
    if Y > 170: 
        if tempPlane: vp.SetConstructionPlane(tempPlane)
        view_plane()
        scriptcontext.doc.Views.Redraw()
    else:
        vp.SetConstructionPlane(Rhino.Geometry.Plane.WorldXY)
        #print "Pongo"
        
    if not doc:
            scriptcontext.doc.Views.Redraw()

def callback_function(sender, e):
    try:
        vp = e.Viewport
        doc = e.RhinoDoc
        CplaneSetter(vp, doc)
    except Exception, e:
        print e
    
   
def KyleMode():
    if( scriptcontext.sticky.has_key("kylemode_callback_function") ):
        Rhino.Display.DisplayPipeline.CalculateBoundingBox -= scriptcontext.sticky["kylemode_callback_function"]
        scriptcontext.sticky.Remove("kylemode_callback_function")
        print "Kyle mode is off"
    else:
        scriptcontext.sticky["kylemode_callback_function"] = callback_function
        Rhino.Display.DisplayPipeline.CalculateBoundingBox += callback_function
        print "Kyle mode is on"
    scriptcontext.doc.Views.Redraw() 
    return 0
    
KyleMode()
