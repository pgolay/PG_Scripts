import Rhino
import scriptcontext as sc
import System
import math
import rhinoscriptsyntax as rs
from System.Drawing import *
from Rhino.Commands import *
from Rhino.Geometry import *


def show_deviation(srf, pts):
    dist = 0
    maxpt = None
    for pt in pts:
        par = srf.ClosestPoint(pt)
        temp = pt.DistanceTo(srf.PointAt(par[1], par[2]))
        
        if temp > dist:
            dist = temp
            maxpt = pt

    print "Deviation  = ", round(dist, 4)
    return maxpt, round(dist, 4)

def edit_surfacesuck_inputs(mesh, pts):
    UDeg = 3
    VDeg = 3
    UCount = 1
    VCount = 1
    
    
    test_dot = Rhino.Geometry.TextDot("Test", pts[0])
    
    if sc.sticky.has_key("SrfSuckUDeg"):
        UDeg = sc.sticky["SrfSuckUDeg"]
        
    if sc.sticky.has_key("SrfSuckVDeg"):
        VDeg = sc.sticky["SrfSuckVDeg"]
        
    if sc.sticky.has_key("SrfSuckUCount"):
        UCount = sc.sticky["SrfSuckUCount"]
        
    if sc.sticky.has_key("SrfSuckVCount"):
        VCount = sc.sticky["SrfSuckVCount"]
        
        
    startUDeg = UDeg
    startVDeg = VDeg
    startUCount = UCount
    startVCount = VCount
    
    
    dot_list = []
    
    i = 0
    for pt in pts:
        dot_list.append(rs.AddTextDot(i, pt))
        i = i + 1
    
    #go = Rhino.Input.Custom.GetObject()
    go = __CustomGetObjectEx(dot_list)
    go.GeometryFilter = Rhino.DocObjects.ObjectType.TextDot
    go.AcceptNothing(True)
    int_UDeg = Rhino.Input.Custom.OptionInteger(UDeg)
    int_VDeg = Rhino.Input.Custom.OptionInteger(VDeg)
    
    int_UCount = Rhino.Input.Custom.OptionInteger(UCount)
    int_VCount = Rhino.Input.Custom.OptionInteger(VCount)

    optIntUDeg = go.AddOptionInteger("UDegree", int_UDeg)
    optIntVDeg = go.AddOptionInteger("VDegree", int_VDeg)
    optIntUCount = go.AddOptionInteger("USpans", int_UCount)
    optIntVCount = go.AddOptionInteger("VSpans", int_VCount)
 
    
    """
    Let the user select a dot, or set an option. If the user selects a dot
    go to GetPoint, constrain to mesh, draw the other three points and this one
    with lines between.
    Repeat - let the user continue to move points. Add an Update option to recalculate the surface
    from the new point locations and degree etc.
    Show deviation
    Enter when done.
    """
    while True :
        
        go.SetCommandPrompt("Select a corner point.")
 
        rc = go.Get()
        if go.CommandResult()!= Rhino.Commands.Result.Success:
            return go.CommandResult() #

        elif rc == Rhino.Input.GetResult.Object:
            dotObj= go.Object(0)
            Id = dotObj.ObjectId
            if Id in dot_list:
                idx = dot_list.index(Id)
                gp = MovePt(pts, idx, dot_list, rs.TextDotPoint(Id))
                gp.Constrain(mesh.Geometry, True)
                gp_rc = gp.Get()
                if gp_rc == Rhino.Input.GetResult.Point:
                    pt = gp.Point()
                    vec = pt-pts[idx]
                    rs.MoveObject(Id, vec)
                    pts[idx] = pt
                    sc.doc.Views.Redraw
                break
                    
        elif rc==Rhino.Input.GetResult.Option:
            UDeg = int_UDeg.CurrentValue
            VDeg = int_VDeg.CurrentValue
            UCount = int_UCount.CurrentValue
            VCount = int_VCount.CurrentValue
                    
            sc.sticky["SrfSuckUDeg"] = UDeg
            sc.sticky["SrfSuckVDeg"] = VDeg
            sc.sticky["SrfSuckUCount"] = UCount
            sc.sticky["SrfSuckVCount"] = VCount
            continue
            
        elif Rhino.Input.GetResult.Nothing:
            if UDeg == startUDeg and VDeg == startVDeg and UCount == startUCount and VCount == startVCount:
                rs.DeleteObjects(dot_list)
                return [False]
            break
            #return pts,  UDeg, VDeg, UCount, VCount
            
    rs.DeleteObjects(dot_list)
    return  pts,  UDeg, VDeg, UCount, VCount
    
class __CustomGetObjectEx(Rhino.Input.Custom.GetObject):
    def __init__(self, allowable_geometry):
        self.m_allowable = allowable_geometry
    def CustomGeometryFilter(self, rhino_object, geometry, component_index):
        for id in self.m_allowable:
            if id==rhino_object.Id: return True
        return False

def get_surfacesuck_inputs(mesh):
    
    UDeg = 3
    VDeg = 3
    UCount = 1
    VCount = 1
    
    if sc.sticky.has_key("SrfSuckUDeg"):
        UDeg = sc.sticky["SrfSuckUDeg"]
    if sc.sticky.has_key("SrfSuckVDeg"):
        VDeg = sc.sticky["SrfSuckVDeg"]
        
    if sc.sticky.has_key("SrfSuckUCount"):
        UCount = sc.sticky["SrfSuckUCount"]
    if sc.sticky.has_key("SrfSuckVCount"):
        VCount = sc.sticky["SrfSuckVCount"]
        
    pts = []
    gp = GetPts(pts)
    gp.Constrain(mesh, True)
    
    int_UDeg = Rhino.Input.Custom.OptionInteger(UDeg)
    int_VDeg = Rhino.Input.Custom.OptionInteger(VDeg)
    
    int_UCount = Rhino.Input.Custom.OptionInteger(UCount)
    int_VCount = Rhino.Input.Custom.OptionInteger(VCount)

    optIntUDeg = gp.AddOptionInteger("UDegree", int_UDeg)
    optIntVDeg = gp.AddOptionInteger("VDegree", int_VDeg)
    optIntUCount = gp.AddOptionInteger("USpans", int_UCount)
    optIntVCount = gp.AddOptionInteger("VSpans", int_VCount)
    optSurface = gp.AddOption("Surface")
    
    objref = None
    i = 0
    while True :
        if i == 1:
            gp.SetCommandPrompt("Set corner points. The second point determines the U direction.")
        else:
            gp.SetCommandPrompt("Set corner point.")
        rc = gp.Get()
        if gp.CommandResult()!= Rhino.Commands.Result.Success:
            return
        if rc==Rhino.Input.GetResult.Point:
            pts.append(gp.Point())
            i = i + 1
        elif rc==Rhino.Input.GetResult.Option:
            UDeg = int_UDeg.CurrentValue
            VDeg = int_VDeg.CurrentValue
            UCount = int_UCount.CurrentValue
            VCount = int_VCount.CurrentValue
            if gp.Option().Index == optSurface:
                go = Rhino.Input.Custom.GetObject()
                go.GeometryFilter = Rhino.DocObjects.ObjectType.Surface
                go.SetCommandPrompt("Select a surface.")
                rc = go.Get()
                if Rhino.Input.GetResult.Object:
                    objref = go.Object(0)
                    
            sc.sticky["SrfSuckUDeg"] = UDeg
            sc.sticky["SrfSuckVDeg"] = VDeg
            sc.sticky["SrfSuckUCount"] = UCount
            sc.sticky["SrfSuckVCount"] = VCount
            
        if objref is not None:
            return True, objref, UDeg, VDeg, UCount, VCount
        else:
            if i == 4:
                return False, pts, UDeg, VDeg, UCount, VCount
                
class MovePt(Rhino.Input.Custom.GetPoint):
    
    l_color = sc.doc.Layers.CurrentLayer.Color
    pass
    def __init__(self, Pts, idx, dots, base_point):
        self.m_points = Pts
        self.m_idx = idx
        self.m_dots = dots
        self.m_xform = Transform.Identity
        self.m_point = base_point
        pass
        
    
    # Calculates the transformation
    def CalculateTransform(self, point):
        xform = RhinoTransform.Identity
        dir = point - self.m_point
        if (not dir.IsTiny()):
            xform = Transform.Translation(dir)
        return xform
        
    # OnMouseMove override
    def OnMouseMove(self, e):
        self.m_xform = self.CalculateTransform(e.Point)
        GetPoint.OnMouseMove(self, e)
        
        
    def OnDynamicDraw(self, e):
        pNow = e.CurrentPoint
        l = len(self.m_points)
        n = 0
        x = sc.doc.Objects.Find( self.m_dots[self.m_idx])
        e.Display.DrawPoint(pNow, Color.Red)
        e.Display.DrawObject( x, self.m_xform )
        #e.Display.DrawObject(obj, self.m_xform)
        for pt in self.m_points:
            if n != self.m_idx:
               e.Display.DrawPoint(pt, Color.Red)
               n = n + 1
               
        for i in range(l-1):
           if i == 0 or i == 2:
               LineColor1 = Color.Red
               LineColor2 = Color.Green
           else:
               LineColor1 = Color.Green
               LineColor2 = Color.Red
               
           if i != self.m_idx:
                e.Display.DrawLine(self.m_points[i], self.m_points[i+1], LineColor1, 2)
           else:
               e.Display.DrawLine(pNow, self.m_points[i+1], LineColor1, 2)
               e.Display.DrawLine(pNow, self.m_points[i-1], LineColor2, 2)
           if self.m_idx == 3:
               e.Display.DrawLine(pNow, self.m_points[0],Color.Green, 2)
               e.Display.DrawLine(pNow, self.m_points[2],Color.Red,  2)
 
class GetPts (Rhino.Input.Custom.GetPoint):
    
    l_color = sc.doc.Layers.CurrentLayer.Color
    pass
    def __init__(self, Pts):
        self.m_points = Pts
        pass
    def OnDynamicDraw(self, e):
        pNow = e.CurrentPoint
        e.Display.DrawPoint(pNow, Color.Red)
        l = len(self.m_points)
        for pt in self.m_points:
            e.Display.DrawPoint(pt, Color.Red)
        if l > 0:
                
            for i in range(l):
               if i == 0 or i == 2:
                   LineColor1 = Color.Red
                   LineColor2 = Color.Green
               else:
                   LineColor1 = Color.Green
                   LineColor2 = Color.Red
               if l == 1:
                   e.Display.DrawLine( pNow, self.m_points[0], LineColor1, 2 )
               e.Display.DrawLine( self.m_points[i], self.m_points[i+1], LineColor1, 2 )
               e.Display.DrawLine( pNow, self.m_points[l-1], LineColor2, 2 )
               e.Display.DrawLine( pNow,self.m_points[0], Color.Green, 2 )

def make_starting_srf(pts, UDeg, VDeg, UCount, VCount):
    ptSrf = Rhino.Geometry.NurbsSurface.CreateFromCorners(pts[0], pts[1], pts[2], pts[3])
    if not ptSrf: return
    newSrf = ptSrf.Rebuild(UDeg, VDeg, UCount, VCount)
    return sc.doc.Objects.AddSurface(newSrf) #Id
    
def patch_starting_Srf(srfId, meshId):
    mesh_obj = sc.doc.Objects.Find(meshId)
    crvs = []
    brep = sc.doc.Objects.Find(srfId)

    edges = brep.Geometry.Edges
    #ToDo - pull edge curves to the mesh before getting the BB
    edgept_list = []
    pulled_edgepts = []
    for f in range(len(list(edges))):
        new_crv = (edges[f].ToNurbsCurve())
        crv_pars = new_crv.DivideByLength(1, True)
        for par in crv_pars:
            edgept_list.append(new_crv.PointAt(par))
        rs.EnableRedraw(False)
        pulled_edgepts.extend(rs.PullPoints(meshId, edgept_list))

    pt_list = []
    pt_objects = []
          
    srf = brep.BrepGeometry.Faces[0].ToNurbsSurface()
    
    UInterval = srf.Domain(0).Length/10
    VInterval = srf.Domain(1).Length/10
    
    
    #Divide up the surface into a grid of points.
    #Feed the points to the Patch command
    intDiv = 10
    for i in range(intDiv):
        for j in range(intDiv):
            pt_list.append(srf.PointAt(i*UInterval,j*VInterval))
    for i in range(intDiv):
        pt_list.append(srf.PointAt(srf.Domain(0).Length,i*VInterval))
        pt_list.append(srf.PointAt(i*UInterval, srf.Domain(1).Length))
        
    if len(pt_list) > 0:
        pulled_points = mesh_obj.Geometry.PullPointsToMesh(pt_list)
        
    pt_objects.extend(rs.AddPoints(pulled_points))
    pt_objects.extend(rs.AddPoints(pulled_edgepts))
    list(pulled_points).extend(pulled_edgepts)

    rs.UnselectAllObjects()
    rs.SelectObjects(pt_objects)
    cmd_str = "-Patch StartingSurface SelId " + str(srfId) + " DeleteInput=Yes PreserveEdges=No Enter"
    rs.Command (cmd_str, False)
    if rs.LastCommandResult() == 0:
        rs.DeleteObjects (pt_objects)
        patchId = rs.LastCreatedObjects()[0]
        if patchId: return patchId, pulled_points
    pass
    
def PatchToMesh():
    meshId = rs.GetObject("Select mesh", filter = 32 )
    if not meshId: return
    mesh_obj = sc.doc.Objects.Find(meshId)
    #rs.HideObject(meshId)
    x = get_surfacesuck_inputs(mesh_obj.Geometry)
    if not x: return
    src = rs.AddPoint(0,0,0)
    blnSrf = x[0]
    use_srf = False
    if blnSrf:
        use_srf = True
        brep = sc.doc.Objects.Find(x[1].ObjectId)
        srfId = x[1].ObjectId
        pass
    else:
        pts = x[1]
        UDeg = x[2]
        VDeg = x[3]
        UCount = x[4]+ UDeg
        VCount = x[5]+VDeg
        srfId = make_starting_srf(pts, UDeg, VDeg, UCount, VCount)

    patchId, pulled_points = patch_starting_Srf(srfId, meshId)
    
    if patchId:
        patch_srf = sc.doc.Objects.Find(patchId).BrepGeometry.Surfaces[0]
        rs.MatchObjectAttributes(patchId,src)
        rs.DeleteObject(src)
    
    dev_pt = show_deviation(patch_srf, pulled_points)
    
    if dev_pt:
        if not use_srf:
            dev_object = rs.AddTextDot(dev_pt[1], dev_pt[0])
    rs.EnableRedraw(True)
    sc.doc.Views.Redraw()

    #dev_object = None
    if use_srf: 
        return
    while True:
        new_input = edit_surfacesuck_inputs(mesh_obj, pts)
        if new_input:

            pts = new_input[0]
            if not pts:
               if dev_object is not None: 
                   rs.DeleteObject(dev_object)
               return
               
            UDeg = new_input[1]
            VDeg = new_input[2]
            UCount = new_input[3]
            UCount = UCount + UDeg
            VCount = new_input[4]
            VCount - VCount + VDeg
            
            rs.DeleteObject(patchId)
            srfId = make_starting_srf(pts, UDeg, VDeg, UCount, VCount)
            patchId, pulled_points = patch_starting_Srf(srfId, meshId)
            patch_srf = sc.doc.Objects.Find(patchId).BrepGeometry.Surfaces[0]
            rs.DeleteObject (src)
            
            dev_pt = show_deviation(patch_srf, pulled_points)
            if dev_object is not None: 
                rs.DeleteObject(dev_object)
            if dev_pt:
                dev_object = rs.AddTextDot(dev_pt[1], dev_pt[0])
                
            rs.EnableRedraw(True)
            sc.doc.Views.Redraw()
            pass
        else:
            if dev_object is not None: 
                rs.DeleteObject(dev_object)
            return
            
PatchToMesh()