import rhinoscript.userinterface
import rhinoscript.geometry
import Rhino
import scriptcontext
import System
import math

__commandname__ = "KyleMode"



def find_nearest_plane(VecDir):
    pi = math.pi
    v_list = []
    p_list = []
    plane = Rhino.Geometry.Plane.WorldXY
    p_list.append(plane)
    v_list.append(plane.ZAxis)
    
    plane = Rhino.Geometry.Plane.WorldYZ
    p_list.append(plane)
    v_list.append(plane.ZAxis)
    
    plane = Rhino.Geometry.Plane.WorldZX
    p_list.append(plane)
    v_list.append(plane.ZAxis)
    
    plane = Rhino.Geometry.Plane.WorldXY
    plane.Flip()
    plane.Rotate(pi/2,plane.ZAxis)
    p_list.append(plane)
    v_list.append (plane.ZAxis)
    
    plane = Rhino.Geometry.Plane.WorldYZ
    plane.Flip()
    plane.Rotate(-pi/2,plane.ZAxis)
    p_list.append(plane)
    v_list.append (plane.ZAxis)
    
    plane = Rhino.Geometry.Plane.WorldZX
    #plane.Flip()
    #plane.Rotate(pi,plane.ZAxis)
    p_list.append(plane)
    v_list.append (plane.ZAxis)
    
    n = 0
    idx = -1
    deg = 0
    for vec in v_list:
        test = Rhino.RhinoMath.ToDegrees(Rhino.Geometry.Vector3d.VectorAngle(vec, VecDir))
        #print deg
        if test > deg:
            deg = test
            idx = n
            
        n = n + 1
    return p_list[idx]
    

def CplaneSetter(vp=None, doc=None):
    if not vp:
        vp = scriptcontext.doc.Views.ActiveView.ActiveViewport
    #vp = Rhino.Display.RhinoViewport()
    
    plane = vp.ConstructionPlane()
    plane2 = Rhino.Geometry.Plane.WorldYZ
    v1 = plane.ZAxis
    v2 = vp.CameraDirection
    X = Rhino.RhinoMath.ToDegrees(Rhino.Geometry.Vector3d.VectorAngle(v1,v2))
    #print X
    
    if X < 135:
        tempPlane = find_nearest_plane(v2)
        if tempPlane: vp.SetConstructionPlane(tempPlane)
        if X > 175: vp.SetToPlanView
        
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
    else:
        scriptcontext.sticky["hack"] = hack
        Rhino.Display.DisplayPipeline.CalculateBoundingBox += hack
        
    scriptcontext.doc.Views.Redraw() 
    return 0
