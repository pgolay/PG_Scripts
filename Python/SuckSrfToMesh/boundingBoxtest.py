import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
from System.Drawing import *
#ptobjs = rs.SelectedObjects()

class RotatePt(Rhino.Input.Custom.GetPoint):

    def __init__(self, Pts, idx, dots, base_point, ctr):
        self.m_points = Pts #pt3d list
        self.m_idx = idx #int
        self.m_dots = dots #ids
        self.m_xform = Rhino.Geometry.Transform.Identity
        self.m_point = base_point
        self.m_ctr = ctr
        
    # Calculates the transformation
    def CalculateTransform(self, point):
        xform = RhinoTransform.Identity
        dir1 = self.m_ctr - self.m_point
        dir1 = self.m_ctr - point
        if (not dir2.IsTiny()):
            xform = Transform.Rotation(dir1, dir2, self.m_ctr )
        return xform

    # OnMouseMove override
    def OnMouseMove(self, e):
        self.m_xform = self.CalculateTransform(e.Point)
        GetPoint.OnMouseMove(self, e)

    def OnDynamicDraw(self, e):
       
        for p in self.m_points:
            p = self.m_xform*p
        
        e.Display.DrawLine(self.m_points[0],self.m_points[1], Color.Black)
        e.Display.DrawLine(self.m_points[1],self.m_points[2], Color.Black)
        e.Display.DrawLine(self.m_points[2],self.m_points[3], Color.Black)
        e.Display.DrawLine(self.m_points[3],self.m_points[0], Color.Black)
        e.Display.DrawPoint( e.CurrentPoint, Color.Red )
        

class MovePt(Rhino.Input.Custom.GetPoint):
     
    pass
    def __init__(self, Pts, idx, dots, base_point):
        self.m_points = Pts #pt3d list
        self.m_idx = idx #int
        self.m_dots = dots #ids
        self.m_xform = Rhino.Geometry.Transform.Identity
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
        #xform = self.CalculateTransform(pNow)
        vecDir = pNow - self.m_point
        l = len(self.m_points)
        n = 0
      
        p1 = self.m_points[self.m_idx] + vecDir
        p2 = self.m_points[self.m_idx+1] + vecDir

        if self.m_idx == 0:
            p3 = self.m_points[3]
            p4 = self.m_points[2] 
        elif self.m_idx == 1:
            p3 = self.m_points[0] 
            p4 = self.m_points[3] 
        elif self.m_idx == 2:
            p3 = self.m_points[1]
            p4 = self.m_points[0] 
        else:
            p3 = self.m_points[2]
            p4 = self.m_points[1]
            
        e.Display.DrawLine(p1,p2, Color.Black)
        e.Display.DrawLine(p1,p3, Color.Black)
        e.Display.DrawLine(p2,p4, Color.Black)
        e.Display.DrawPoint( pNow, Color.Red )
        
        e.Display.DrawObject( self.m_dots[ self.m_idx ], xform )
        e.Display.DrawObject( self.m_dots[ self.m_idx + 1 ], xform )
        
class __CustomGetObjectEx(Rhino.Input.Custom.GetObject):
    def __init__(self, allowable_geometry):
        self.m_allowable = allowable_geometry
    def CustomGeometryFilter(self, rhino_object, geometry, component_index):
        for id in self.m_allowable:
            if id==rhino_object.Id: return True
        return False

class DrawEdgesConduit(Rhino.Display.DisplayConduit):
    def __init__(self,  pts):

       self.pts = pts

    def DrawForeground(self, e):
        for i in range(4):
            e.Display.DrawLine(self.pts[i], self.pts[i+1], Color.Black, 3) 
        #e.Display.DrawLines(self.lines, Color.Black, 2)
       #e.Display.DrawPoints(self.pts,Rhino.Display.PointStyle.ControlPoint, 3 ,Color.Red)
       
def bb_corners(meshObj):
    
    l = meshObj.Geometry.Vertices.Count
    pts = [Rhino.Geometry.Point3d(meshObj.Geometry.Vertices[n]) for n in range(l)]
    
    plane = Rhino.Geometry.Plane.FitPlaneToPoints(pts)[1]
    xform = Rhino.Geometry.Transform.PlaneToPlane(plane, Rhino.Geometry.Plane.WorldXY)
    
    ptXform = [xform*pt for pt in pts]
    bbXY = Rhino.Geometry.BoundingBox(ptXform)
    xform = Rhino.Geometry.Transform.PlaneToPlane( Rhino.Geometry.Plane.WorldXY, plane)
    bb2D = [xform*pt for pt in bbXY.GetCorners()[0:4]]
    
    bb2D.append(bb2D[0])
    edgeLines = [Rhino.Geometry.Line(bb2D[i], bb2D[i+1]) for i in range(4)]
    corners = [bb2D[i] for i in range(4)]
    plane.Origin = corners[1] + (corners[3]-corners[1])/2
    
    return edgeLines, corners, plane

    
def test():
    meshId = rs.SelectedObjects()[0]
    mesh = sc.doc.Objects.Find(meshId)
    x = bb_corners(mesh)
    #pt_list = [sc.doc.Objects.AddPoint(pt) for pt in x[1]]
    line_list = [sc.doc.Objects.AddLine(line) for line in x[0]]
    conduit = DrawEdgesConduit(x[1])
    conduit.Enabled = True
    pass
    
    def get_inputs(meshId, lines, pts, plane):
        ctr = plane.Origin
        line_list = lines
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
            
            
        #pts = list(mesh.PullPointsToMesh(pts))
        startUDeg = UDeg
        startVDeg = VDeg
        startUCount = UCount
        startVCount = VCount
    
        while True :
            #plane = Rhino.Geometry.Plane.FitPlaneToPoints(pts)[1]
            circle = Rhino.Geometry.Circle(plane, ((pts[3]-pts[1])/2).Length)
            dot_list = []
            rs.EnableRedraw(False)
            for i in range(4): 
                dot = rs.AddTextDot(" ", pts[i])
                dot_list.append(dot)
                rs.ObjectColor(dot, Color.Red)
                rs.EnableRedraw(True)

            go = __CustomGetObjectEx(dot_list+line_list)
            #go.GeometryFilter = Rhino.DocObjects.ObjectType.TextDot
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
                conduit = DrawEdgesConduit(pts)
                conduit.Enabled = False
                rs.DeleteObjects(dot_list)
                return go.CommandResult() #
    
            elif rc == Rhino.Input.GetResult.Object:
                objRef= go.Object(0)
                Id = objRef.ObjectId
                if Id in dot_list:
                    
                    #pt = pts[1] + ((pts[3]-pts[1])/2)
                    idx = dot_list.index(Id)
                    #sc.doc.Objects.AddCircle(circle)
                    gp = RotatePt(pts, idx, dot_list, rs.TextDotPoint(Id), ctr)
                    gp.Constrain(circle)
                    
                    gp_rc = gp.Get()
                    
                    if gp_rc == Rhino.Input.GetResult.Point:
                        pt = gp.Point()
                        vec = pt-pts[idx]
                        rs.MoveObject(Id, vec)
                        pts[idx] = pt
                        sc.doc.Views.Redraw()
                    break
                else:
                    
                    idx = line_list.index(Id)
                    print idx
                    lineGeo_list =[sc.doc.Objects.Find(i).Geometry for i in line_list]
                    #test = sc.doc.Objects.Find(line_list[1])
                    lineGeo_list.append(lineGeo_list[0])
                    basePt = objRef.SelectionPoint()
                    #rs.AddPoint(basePt)
                    rs.DeleteObjects(line_list)
                    gp = MovePt(pts, idx, dot_list, basePt)
                    vecConstrain = (lineGeo_list[idx+1].Line.From - lineGeo_list[idx+1].Line.To)
                    gp.Constrain(Rhino.Geometry.Line(basePt, basePt + vecConstrain))
                    gp_rc = gp.Get()
                    
                    if gp.CommandResult()!= Rhino.Commands.Result.Success:
                        conduit = DrawEdgesConduit(pts)
                        conduit.Enabled = False
                        return pts
                    if gp_rc == Rhino.Input.GetResult.Point:
                        pt = gp.Point()
                        vec = pt-basePt
                        #rs.MoveObject(Id, vec)
                        pts[idx] = pts[idx]+vec
                        pts[idx+1] = pts[idx+1]+vec
                        line_list = [sc.doc.Objects.AddLine(Rhino.Geometry.Line(pts[i],pts[i+1])) for i in range(4)]
                        
                        rs.DeleteObjects(dot_list)
                        for i in range(4): 
                            dot = rs.AddTextDot(" ", pts[i])
                            dot_list.append(dot)
                            rs.ObjectColor(dot, Color.Red)
                            rs.EnableRedraw(True)
                        conduit = DrawEdgesConduit(pts)
                        conduit.Enabled = False
                        conduit = DrawEdgesConduit(pts)
                        conduit.Enabled = True
                        #rs.AddPoints(pts)
                        sc.doc.Views.Redraw()
                continue
                    
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
        
    #rs.AddPoints(x[1])#corners   
    x[1].append(x[1][0])

    get_inputs(meshId, line_list, x[1], x[2])
    
    conduit.Enabled = False
    sc.doc.Views.Redraw()
    
    
    
    
    
if __name__ == '__main__':
    test()