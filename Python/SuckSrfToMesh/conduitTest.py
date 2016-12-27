import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
from System.Drawing import *
import math
#ptobjs = rs.SelectedObjects()

class RotatePt(Rhino.Input.Custom.GetPoint):

    def __init__(self, Pts,  base_point, plane):
        self.m_points = Pts #pt3d list
        self.m_basepoint = base_point
        self.m_plane = plane
        
        self.m_xform = Rhino.Geometry.Transform.Identity
        self.m_ctr = self.m_plane.Origin

    # Calculates the transformation
    def CalculateTransform(self, crntpoint):
        xform = Rhino.Geometry.Transform.Identity
        
        def calculate_angle():
            dir1 = self.m_basepoint - self.m_ctr 
            dir2 = crntpoint - self.m_ctr
            
            dir1.Unitize()
            dir2.Unitize()

            dot = Rhino.Geometry.Vector3d.Multiply(dir2, dir1)
            #dot = (dot < -1.0 ? -1.0 : (dot > 1.0 ? 1.0 : dot));
      
            #ang = math.acos(dot)
            
            ang = Rhino.Geometry.Vector3d.VectorAngle(dir1, dir2, self.m_plane )
            ZAxis = Rhino.Geometry.Vector3d.CrossProduct(self.m_plane.XAxis, self.m_plane.YAxis)
            VertZaxis = Rhino.Geometry.Vector3d.CrossProduct(ZAxis, dir1)
            vert_plane = Rhino.Geometry.Plane(self.m_ctr, VertZaxis)
            
            #print "ang1 " , ang
            
            dist = vert_plane.DistanceTo(crntpoint)
            #print "dist ", dist
            
            if (dist < 0.0):
                ang = 2.0 * math.pi - ang
                
            #print "ang2 " , ang
            return ang
            
        ang = calculate_angle()
        xform = Rhino.Geometry.Transform.Rotation(ang, self.m_plane.ZAxis, self.m_ctr)
        return xform

    # OnMouseMove override
    def OnMouseMove(self, e):
        self.m_xform = self.CalculateTransform(e.Point)
        
        GetPoint.OnMouseMove(self, e)

    def OnDynamicDraw(self, e):
        
        temp = self.m_points
        for pt in temp:
            pt.Transform(self.m_xform)
            
        e.Display.DrawPoint( e.CurrentPoint, Color.Red )
        e.Display.DrawPoint( self.m_ctr, Color.Red )
        e.Display.DrawPoint( temp[2], Color.Blue )
        e.Display.DrawPoint( e.CurrentPoint, Color.Green)
        
        e.Display.DrawLine( temp[0], temp[1], Color.Black )
        e.Display.DrawLine( temp[1], temp[2], Color.Black )
        e.Display.DrawLine( temp[2], temp[3], Color.Black )
        e.Display.DrawLine( temp[3], temp[0], Color.Black )
        
        
        
        

class MovePt(Rhino.Input.Custom.GetPoint):

    def __init__(self, Pts, idx,  base_point):
        self.m_points = Pts #pt3d list
        self.m_idx = idx #int
        self.m_xform = Rhino.Geometry.Transform.Identity
        self.m_point = base_point
        pass

    def OnDynamicDraw(self, e):
        vecDir = e.CurrentPoint - self.m_point
      
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
        
def test():
    
    rgp = Rhino.Geometry.Point3d
    
    p1 = rgp(0.0, 0.0,0.0)
    p2 = rgp(10.0, 0.0,0.0)
    p3 = rgp(10.0, 10.0,0.0)
    p4 = rgp(0.0, 10.0,0.0)
    p5 = p1
    pts = [p1,p2,p3,p4,p5]
    
    #conduit = DrawEdgesConduit(pts)
    #conduit.Enabled = True
    #    sc.doc.Views.Redraw()
    #    lines = [sc.doc.Objects.AddLine(pts[i], pts[i+1]) for i in range(4)]
    #    sc.doc.Views.Redraw ()
    
    #    go = __CustomGetObjectEx(lines)
    #    rc = go.Get()
    #    if go.CommandResult()!= Rhino.Commands.Result.Success:
    #        #conduit = DrawEdgesConduit(pts)
    #        #conduit.Enabled = False
    #        rs.DeleteObjects(lines)
    #        return go.CommandResult() #
    #    elif rc == Rhino.Input.GetResult.Object:
    #        objRef = go.Object(0)
    #        Id = objRef.ObjectId
    #        pp = objRef.SelectionPoint()#pick point
     
    gp = Rhino.Input.Custom.GetPoint()
    gp.Get()
    pp = gp.Point()
    
    circle = Rhino.Geometry.Circle(Rhino.Geometry.Plane.WorldXY, ( pp - Rhino.Geometry.Plane.WorldXY.Origin ).Length)
    #circle = Rhino.Geometry.Circle(Rhino.Geometry.Plane.WorldXY, 10)
    
    gp1 = RotatePt( pts, pp, circle.Plane )# points and a base point and a plane
    
    gp1.Constrain(circle)
    
    x = gp1.Get()

    pass
    #rs.DeleteObjects(lines)
    sc.doc.Views.Redraw ()
    #conduit.Enabled = False
test()