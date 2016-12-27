import Rhino
import scriptcontext as sc
import System
import rhinoscriptsyntax as rs
from System.Drawing import *
from Rhino.Commands import *
from Rhino.Geometry import *
from System.Collections.Generic import List


class DrawSrfConduit(Rhino.Display.DisplayConduit):
    def __init__(self, srf, color1, color2, pt, dblDist, crv1, crv2):
        self.srf = srf
        self.Color1 = color1
        self.Color2 = color2
        self.pt = pt
        self.dblDist = dblDist
        self.crv1 = crv1
        self.crv2 = crv2
    def DrawForeground(self, e):
        e.Display.DrawSurface(self.srf, Color.Black, 1)
        e.Display.DrawDot(self.pt,self.dblDist)
        e.Display.DrawCurve(self.crv1,self.Color1, 3)
        e.Display.DrawCurve(self.crv2,self.Color2, 3)
        
class DrawBrepConduit(Rhino.Display.DisplayConduit):
    def __init__(self, brep, mat):
       self.brep = brep
       self.Mat = mat

    def DrawForeground(self, e):
       e.Display.DrawShadedBrepShaded(self.brep, self.Mat)

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

def edit_surfacesuck_inputs(meshId, pts):
    UDeg = 3
    VDeg = 3
    UCount = 1
    VCount = 1
    mesh = sc.doc.Objects.Find(meshId).Geometry
    test_dot = Rhino.Geometry.TextDot("Test", pts[0])
    
    
    if sc.sticky.has_key("SrfSuckUDeg"):
        UDeg = sc.sticky["SrfSuckUDeg"]
        
    if sc.sticky.has_key("SrfSuckVDeg"):
        VDeg = sc.sticky["SrfSuckVDeg"]
        
    if sc.sticky.has_key("SrfSuckUCount"):
        UCount = sc.sticky["SrfSuckUCount"]
        
    if sc.sticky.has_key("SrfSuckVCount"):
        VCount = sc.sticky["SrfSuckVCount"]
        
        
    pts = list(mesh.PullPointsToMesh(pts))
    startUDeg = UDeg
    startVDeg = VDeg
    startUCount = UCount
    startVCount = VCount

    while True :
        dot_list = []
        rs.EnableRedraw(False)
        for i in range(8): 
            dot = rs.AddTextDot(" ", pts[i])
            
            dot_list.append(dot)
            if i ==1 or i == 5:
                rs.ObjectColor(dot, Color.Red)
                if i == 1:
                    rs.TextDotHeight(dot, 11)
                    
                    rs.TextDotText(dot, str(UDeg)+ "/"+ str(UCount))
                else:
                    rs.TextDotHeight(dot, 8)
            elif i == 3 or i == 7:
                rs.ObjectColor(dot, Color.Green)
                if i == 7: 
                    rs.TextDotHeight(dot, 11)
                    rs.TextDotText(dot, str(VDeg)+ "/"+ str(VCount))
                else:
                    rs.TextDotHeight(dot, 8)
            else:
                rs.TextDotHeight(dot, 8)
                
            rs.EnableRedraw(True)
            
        if len(pts) > 8: del pts[len(pts)-1]
        go = __CustomGetObjectEx(dot_list)
        go.GeometryFilter = Rhino.DocObjects.ObjectType.TextDot
        go.AcceptNothing(True)
        int_UDeg = Rhino.Input.Custom.OptionInteger(UDeg)
        int_VDeg = Rhino.Input.Custom.OptionInteger(VDeg)
        
        int_UCount = Rhino.Input.Custom.OptionInteger(UCount)
        int_VCount = Rhino.Input.Custom.OptionInteger(VCount)
        #blnGhostMesh = Rhino.Input.Custom.OptionToggle(blnGhost, "No", "Yes")
        optIntUDeg = go.AddOptionInteger("UDegree", int_UDeg)
        optIntVDeg = go.AddOptionInteger("VDegree", int_VDeg)
        optIntUCount = go.AddOptionInteger("USpans", int_UCount)
        optIntVCount = go.AddOptionInteger("VSpans", int_VCount)
        optSwap = go.AddOption("SwapUVSettings")
        optShowMesh = go.AddOption("ToggleMesh")

        go.SetCommandPrompt("Change settings or move a handle point.")
 
        rc = go.Get()
        if go.CommandResult()!= Rhino.Commands.Result.Success:
            rs.DeleteObjects(dot_list)
            return go.CommandResult() #

        elif rc == Rhino.Input.GetResult.Object:
            dotObj= go.Object(0)
            Id = dotObj.ObjectId
            if Id in dot_list:
                idx = dot_list.index(Id)
                gp = MovePt(pts, idx, dot_list, rs.TextDotPoint(Id))
                gp.Constrain(mesh, True)
                gp_rc = gp.Get()
                if gp_rc == Rhino.Input.GetResult.Point:
                    pt = gp.Point()
                    vec = pt-pts[idx]
                    rs.MoveObject(Id, vec)
                    pts[idx] = pt
                    sc.doc.Views.Redraw()
                break
                    
        elif rc==Rhino.Input.GetResult.Option:
            UDeg = int_UDeg.CurrentValue
            VDeg = int_VDeg.CurrentValue
            UCount = int_UCount.CurrentValue
            VCount = int_VCount.CurrentValue
                
            if go.Option().Index == optShowMesh:
                if rs.IsObjectHidden(meshId):
                    rs.ShowObject(meshId)
                    sc.sticky["MeshHideFlag"] = False
                else: 
                    rs.HideObject(meshId)
                    sc.sticky["MeshHideFlag"] = True
            if go.Option().Index == optSwap:
                rs.DeleteObjects(dot_list)
                UDeg = int_VDeg.CurrentValue
                VDeg = int_UDeg.CurrentValue
                UCount = int_VCount.CurrentValue
                VCount = int_UCount.CurrentValue
                sc.sticky["SrfSuckUDeg"] = UDeg
                sc.sticky["SrfSuckVDeg"] = VDeg
                sc.sticky["SrfSuckUCount"] = UCount
                sc.sticky["SrfSuckVCount"] = VCount
                
                return  pts,  UDeg, VDeg, UCount, VCount
                
            sc.sticky["SrfSuckUDeg"] = UDeg
            sc.sticky["SrfSuckVDeg"] = VDeg
            sc.sticky["SrfSuckUCount"] = UCount
            sc.sticky["SrfSuckVCount"] = VCount
            rs.DeleteObjects(dot_list)
            return  pts,  UDeg, VDeg, UCount, VCount
            continue
            
        elif Rhino.Input.GetResult.Nothing:
            rs.DeleteObjects(dot_list)
            if UDeg == startUDeg and VDeg == startVDeg and UCount == startUCount and VCount == startVCount:
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

def get_surfacesuck_inputs(meshId):
    
    mesh = sc.doc.Objects.Find(meshId).Geometry
    
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
    optMesh = gp.AddOption("ChangeMesh")
    optShowMesh = gp.AddOption("ToggleMesh")

    
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
            if gp.Option().Index == optMesh:
                sc.sticky.Remove("MyCurrentMesh")
                return["NewMesh"]
            if gp.Option().Index == optShowMesh:
                #meshId = mesh.
                if rs.IsObjectHidden(meshId):
                    rs.ShowObject(meshId)
                    sc.sticky["MeshHideFlag"] = False
                else: 
                    rs.HideObject(meshId)
                    sc.sticky["MeshHideFlag"] = True

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
        x = sc.doc.Objects.Find( self.m_dots[self.m_idx] )
        e.Display.DrawPoint( pNow, Color.Red )
        e.Display.DrawObject( x, self.m_xform )
        #e.Display.DrawObject( obj, self.m_xform )
        for pt in self.m_points:
            if n != self.m_idx:
               e.Display.DrawPoint( pt, Color.Red )
               n = n + 1
        LineColor = Color.Black      
        for i in range(l-1):
    #           if i == 0 or i == 4 or i == 1 or i== 5:
    #               LineColor1 = Color.Red
    #               LineColor2 = Color.Green
    #           else:
    #               LineColor1 = Color.Green
    #               LineColor2 = Color.Red
           
           if i != self.m_idx:
                e.Display.DrawLine(self.m_points[i], self.m_points[i+1], LineColor, 2)
           else:
               e.Display.DrawLine(pNow, self.m_points[i+1], LineColor, 2)
               if i > 0:
                   e.Display.DrawLine(pNow, self.m_points[i-1], LineColor, 2)
           if self.m_idx == 7:
               e.Display.DrawLine(pNow, self.m_points[0], LineColor, 2)

 
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
                
                if l==1:
                    e.Display.DrawLine( self.m_points[0], pNow, Color.Red, 2 )
                    
                elif l==2:
                    e.Display.DrawLine( self.m_points[0], self.m_points[1] , Color.Red, 2 )
                    e.Display.DrawLine( self.m_points[1], pNow, Color.Green, 2 )
                    e.Display.DrawLine( self.m_points[0], pNow, Color.Green, 2 )
                    
                elif l ==3:
                    e.Display.DrawLine( self.m_points[0], self.m_points[1] , Color.Red, 2 )
                    e.Display.DrawLine( self.m_points[1], self.m_points[2] , Color.Green, 2 )
                    e.Display.DrawLine( self.m_points[0], pNow, Color.Green, 2 )
                    e.Display.DrawLine( self.m_points[2], pNow, Color.Red, 2 )
                    
def make_starting_srf_ex(crvs, UDeg, VDeg, UCount, VCount):

    EdgeSrf = Rhino.Geometry.Brep.CreateEdgeSurface(crvs)
    if not EdgeSrf: return
    newSrf = EdgeSrf.Faces[0].ToNurbsSurface().Rebuild(UDeg, VDeg, UCount, VCount)

    return newSrf #sc.doc.Objects.AddSurface(newSrf) #Id
    
def patch_starting_Srf(sSrf, meshId):

    mesh_obj = sc.doc.Objects.Find(meshId)
    crvs = []
    brep = sSrf.ToBrep()
    edges = brep.Edges
    #ToDo - pull edge curves to the mesh before getting the BB
    edgept_list = []
    pulled_edgepts = []
    intDiv = 20
    
    for f in range(len(list(edges))):
        new_crv = (edges[f].ToNurbsCurve())
        crv_pars = new_crv.DivideByCount(intDiv, True)
        for par in crv_pars:
            edgept_list.append(new_crv.PointAt(par))
    pulled_edgepts.extend(rs.PullPoints(meshId, edgept_list))

    pt_list = []
    pt_objects = []
          
    srf = brep.Faces[0].ToNurbsSurface()
    UInterval = srf.Domain(0).Length/intDiv
    VInterval = srf.Domain(1).Length/intDiv

    #Divide up the surface into a grid of points.
    #Feed the points to the Patch command
    
    for i in range(intDiv):
        for j in range(intDiv):
            pt_list.append(srf.PointAt(i*UInterval,j*VInterval))

    if len(pt_list) > 0:
        pulled_points = list(mesh_obj.Geometry.PullPointsToMesh(pt_list))

    pulled_points.extend(pulled_edgepts)
    #rs.AddPoints(pulled_points)
    geo = List[Rhino.Geometry.GeometryBase]()
    for pt in pulled_points:
        geo.Add(Rhino.Geometry.Point(pt))
    tol = sc.doc.ModelAbsoluteTolerance
    x = Rhino.Geometry.Brep.CreatePatch( geometry = geo, startingSurface = sSrf, uSpans=0, vSpans=0, trim = False, tangency=False, pointSpacing = .01, flexibility = 1, surfacePull = 0, fixEdges=(False, False, False, False), tolerance = tol)
    
    return x, pulled_points
    pass

def make_crvs(pts):
    pts.append(pts[0])
    
    crvs = []
    for n in range(4):
        i = 2*n
        temp = [pts[i],pts[i+1], pts[i+2]]
        crvs.append (Rhino.Geometry.NurbsCurve.CreateInterpolatedCurve(temp, 3))
    crvs.insert(0, crvs.pop(3))
    crvs[0].Reverse()
    return crvs

def PatchToMesh():
    meshId = None
    
    if sc.sticky.has_key("MyCurrentMesh"):
        temp = sc.sticky["MyCurrentMesh"]
        if not temp: reurn
        if rs.IsObject(temp):
            meshId = temp 
        else:
            meshId = rs.GetObject("Select mesh", filter = 32 )
    else:
        meshId = rs.GetObject("Select mesh", filter = 32 )
     
    if not meshId: return
    
    #if meshId != System.Guid(): return 
    sc.sticky["MyCurrentMesh"] = meshId
    
    #rs.HideObject(meshId)
    mesh_obj = sc.doc.Objects.Find(meshId)
    patchId = None
    while True:
        x = get_surfacesuck_inputs(meshId)
        
        if not x:
            return
            
        if x[0] == "NewMesh":
            
            meshId = rs.GetObject("Select mesh", filter=32 )
            if not meshId: return
            sc.sticky["MyCurrentMesh"] = meshId
            
            rs.EnableRedraw(True)
            mesh_obj = sc.doc.Objects.Find(meshId)
            continue
        else:
            break
            
    blnSrf = x[0]
    
    if blnSrf:
        gripOn = False
        sSrf = sc.doc.Objects.Find(x[1].ObjectId).Geometry.Surfaces[0]
        srfId = x[1].ObjectId
        if rs.ObjectGripsOn(srfId):gripOn = True
        patchSrf, pulled_points = patch_starting_Srf(sSrf, meshId)
        dev_pt = show_deviation(patchSrf.Surfaces[0], pulled_points)
        v = sc.doc.Objects.AddSurface(patchSrf.Surfaces[0])
        rs.MatchObjectAttributes(v, srfId)
        if gripOn: rs.EnableObjectGrips( v, True)
        sc.doc.Objects.Delete(srfId, True)
        rs.EnableRedraw(True)
        sc.doc.Views.Redraw()
        return
        pass
    else:
        pts = x[1]
        UDeg = x[2]
        VDeg = x[3]
        UCount = x[4]+ UDeg
        VCount = x[5]+ VDeg
        pts.append(pts[0])
        
        mids = []
        for i in range(4):
            vec = (pts[i+1]-pts[i])/2
            mids.append(pts[i] + vec)
        mids = mesh_obj.Geometry.PullPointsToMesh(mids)
        n = 1
        for i in range(4):
            
            pts.insert(n,mids[i])
            n = n + 2
        del pts[len(pts)-1]
        
        crvs = make_crvs(pts)
        
        sSrf = make_starting_srf_ex(crvs, UDeg, VDeg, UCount, VCount)

    patchSrf, pulled_points = patch_starting_Srf(sSrf, meshId)
    
    dev_pt = show_deviation(patchSrf.Surfaces[0], pulled_points)
    
    edge1 = patchSrf.Edges[0].ToNurbsCurve()
    edge2 = patchSrf.Edges[3].ToNurbsCurve()
    
    if dev_pt: 
        conduit = DrawSrfConduit(patchSrf.Surfaces[0], Color.Red, Color.Green,dev_pt[0], str(dev_pt[1]), edge1, edge2)
        conduit.Enabled = True
    sc.doc.Views.Redraw()
            
    rs.EnableRedraw(True)
        
    while True:
        new_input = edit_surfacesuck_inputs(meshId, pts)
        
        conduit.Enabled = False
        if new_input == Rhino.Commands.Result.Cancel:  
            if patchId: rs.SelectObject(patchId)
            rs.ShowObject(meshId)
            return
            
        if new_input:
            pts = new_input[0]
            
            if not pts:
               patchId = sc.doc.Objects.AddSurface(patchSrf.Surfaces[0])
               rs.EnableRedraw(False)
               rs.ShowObject(meshId)
               rs.EnableRedraw(True)
               if patchId: rs.SelectObject(patchId)
               return
               
            UDeg = new_input[1]
            VDeg = new_input[2]
            UCount = new_input[3]
            VCount = new_input[4]
            UCount = UCount + UDeg
            VCount = VCount + VDeg
            crvs = make_crvs(pts)
            
            sSrf = make_starting_srf_ex(crvs, UDeg, VDeg, UCount, VCount)
            patchSrf, pulled_points = patch_starting_Srf(sSrf, meshId)
            dev_pt = show_deviation(patchSrf.Surfaces[0], pulled_points)
            
            edge1 = patchSrf.Edges[0].ToNurbsCurve()
            edge2 = patchSrf.Edges[3].ToNurbsCurve()
            conduit = DrawSrfConduit(patchSrf.Surfaces[0], Color.Red, Color.Green, dev_pt[0], str(dev_pt[1]), edge1, edge2)
            #conduit = DrawBrepConduit(patchSrf, Rhino.Display.DisplayMaterial(Color.Red))
            conduit.Enabled= True
            sc.doc.Views.Redraw()

            pass
        else:
            if patchId: rs.SelectObject(patchId)
            return
            rs.ShowObject(MeshId)
            conduit.Enabled = False
            if patchId: rs.SelectObject(patchId)
            return


if __name__ == '__main__':
    PatchToMesh()