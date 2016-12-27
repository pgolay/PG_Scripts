import rhinoscriptsyntax as rs
import System
import System.Collections.Generic
#import System.Linq
import System.Runtime.InteropServices
import Rhino
import scriptcontext as sc


class FirstRotationPoint ( Rhino.Input.Custom.GetPoint ):
  
   
    def FirstRotationPoint(plane, corners):
    
    #            if (corners.Length != 4)
    #            throw new ArgumentException("corners should be Point3d[4]")
        
        self.m_corners = corners
        self.m_circle =  Circle(plane, 0.0)
        
        SetBasePoint(plane.Origin, True)
        DrawLineFromPoint(plane.Origin, True)
        Constrain(plane, False)
    
    
    def OnMouseMove(GetPointMouseEventArgs, e):
        m_circle.Radius = m_circle.Plane.Origin.DistanceTo(e.Point)
        base.OnMouseMove(e)
    
    
    def OnDynamicDraw(GetPointDrawEventArgs, e):
    
        e.Display.DrawCircle(m_circle, Rhino.ApplicationSettings.AppearanceSettings.TrackingColor)
        color = Rhino.ApplicationSettings.AppearanceSettings.DefaultObjectColor
        e.Display.DrawLine(m_corners[0], m_corners[1], color)
        e.Display.DrawLine(m_corners[1], m_corners[2], color)
        e.Display.DrawLine(m_corners[2], m_corners[3], color)
        e.Display.DrawLine(m_corners[3], m_corners[0], color)
        base.OnDynamicDraw(e)
    

class SecondRotationPoint (Rhino.Input.Custom.GetPoint):
    

    def SecondRotationPoint( plane, reference, corners):
    
    #            if (corners.Length != 4):
    #                throw new ArgumentException("corners should be Point3d[4]")
    
        self.m_plane = plane
        self.m_reference = reference
        self.m_corners = corners
        
        SetBasePoint(plane.Origin, True)
        DrawLineFromPoint(plane.Origin, True)
        Constrain(plane, False)


    def CalculateAngle( point ):
    
        origin = m_plane.Origin
    
        v = point - origin
        v.Unitize()
    
        zerov = m_reference - origin
        radius = zerov.Length
        zerov.Unitize()  
    
    
        dot = Vector3d.Multiply(zerov, v)
        if dot < -1.0:
            dot = -1.0
        elif dot > 1.0:
             dot = 1.0
            
       #dot = (dot < -1.0 ? -1.0 : (dot > 1.0 ? 1.0 : dot))
    
        angle = Math.Acos(dot)
        zaxis = m_plane.ZAxis
        zaxis.Unitize()
    
        v = Vector3d.CrossProduct(zaxis, zerov)
        v.Unitize()
    
        yplane = Plane(origin, v )
        dist = yplane.DistanceTo(point)
        if (dist < 0.0):
            angle = 2.0 * Math.PI - angle
    
    
    
        self.m_angle = angle
    
        arc_plane =  Plane(origin, zerov, v)
        self.m_arc = Arc(arc_plane, radius, self.m_angle)
        return self.m_arc.IsValid
    

        def OnMouseMove(GetPointMouseEventArgs, e):
            
                self.m_draw = CalculateAngle(e.Point)
                base.OnMouseMove(e)
            
        
        def OnDynamicDraw(GetPointDrawEventArgs, e):
        
            if (self.m_draw):
            
             color = Rhino.ApplicationSettings.AppearanceSettings.DefaultObjectColor
            #e.Display.DrawArc(m_arc, color)
            
            # v = (m_arc.StartPoint - m_arc.Center) * 1.5
            #e.Display.DrawLine(m_arc.Center, m_arc.Center + v, color)
            
            #v = (m_arc.EndPoint - m_arc.Center) * 1.5
            # v1 = e.CurrentPoint - m_arc.Center
            #if (v1.Length > v.Length)
            #  v = v1
            
            #e.Display.DrawLine(m_arc.Center, m_arc.Center + v, color)
            #e.Display.DrawPoint(m_arc.Center, color)
            #e.Display.DrawPoint(m_arc.StartPoint, color)
            
            xform = Transform.Rotation(self.m_angle, self.m_plane.ZAxis, self.m_plane.Origin)
            corners = []
            for i in range (self.m_corners.Length):
            
             corners[i] = m_corners[i]
             corners[i].Transform(xform)
            
            
            e.Display.DrawLine(corners[0], corners[1], color)
            e.Display.DrawLine(corners[1], corners[2], color)
            e.Display.DrawLine(corners[2], corners[3], color)
            e.Display.DrawLine(corners[3], corners[0], color)
            
            base.OnDynamicDraw(e)

def test():

#    objs = rs.GetObjects()
##    x = sc.doc.Objects.Find(objs[0])
#    points = [sc.doc.Objects.Find(Id).Geometry.Location for Id in objs]

    def PlaneThroughPoints( points):
    
        box = Rhino.Geometry.BoundingBox(Rhino.Geometry.Point3d.Unset, Rhino.Geometry.Point3d.Unset)
          
        rc = Rhino.Geometry.Plane.FitPlaneToPoints(points)
#        if rc != Rhino.Geometry.PlaneFitResult.Success:
#            return False
        plane = rc[1]
        
        min = Rhino.Geometry.Point3d.Unset
        max = Rhino.Geometry.Point3d.Unset
    
        for i in range(len(points)):
          
            rc,s,t  = plane.ClosestParameter(points[i])
            
            p = Rhino.Geometry.Point3d(s, t, 0.0)
            
            if (0 == i):

                min = Rhino.Geometry.Point3d(p.X, p.Y, p.Z)
                max = Rhino.Geometry.Point3d(p.X, p.Y, p.Z)
              
            else:
                
              if (p.X < min.X):
                   min.X = p.X
              if (max.X < p.X):
                   max.X = p.X
              if (p.Y < min.Y):
                   min.Y = p.Y
              if (max.Y < p.Y):
                   max.Y = p.Y
              if (p.Z < min.Z):
                   min.Z = p.Z
              if (max.Z < p.Z):
                   max.Z = p.Z
              
          
        #rs.AddPoints ([max, min])
        
        box =  Rhino.Geometry.BoundingBox(min, max)
    
        return box, plane
        

    #Result = RunCommand(RhinoDoc doc, RunMode mode)
    
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select points")
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Point
    go.SubObjectSelect = False
    go.GetMultiple(1, 0)
    if (go.CommandResult() != Rhino.Commands.Result.Success):
        return go.CommandResult()

    points = []
    for  i in range(go.ObjectCount):
  
        point_obj = go.Object(i).Point()
        if (not point_obj):
            return Result.Failure
        points.append (point_obj.Location)
  
#
#      Plane plane
#      BoundingBox domain
    bb, plane =  PlaneThroughPoints(points)
        #return Result.Failure

    min = bb.Min
    max = bb.Max
    corners =  []
    corners.append(plane.PointAt(min.X, min.Y))
    corners.append(plane.PointAt(min.X, max.Y))
    corners.append(plane.PointAt(max.X, max.Y))
    corners.append(plane.PointAt(max.X, min.Y))

    cen = bb.Center
    center = plane.PointAt(cen.X, cen.Y)
    plane.Origin = center

    gp = FirstRotationPoint(plane, corners)
    gp.SetCommandPrompt("First reference point")
    gp.Get()
    if (gp.CommandResult() != Result.Success):
        return gp.CommandResult()

    reference = gp.Point()

    gx = SecondRotationPoint(plane, reference, corners)
    gx.SetCommandPrompt("Second reference point")
    gx.Get()


    doc.Views.Redraw()

    return Result.Success
    
  


        

test()



