using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using Rhino;
using Rhino.Commands;
using Rhino.DocObjects;
using Rhino.Geometry;
using Rhino.Input.Custom;

namespace TestCsCommands
{
  [Guid("e6617215-682d-46cb-86a8-e0733d88d0a3")]
  public class TestCsCommandsCommand : Command
  {
    public TestCsCommandsCommand()
    {
    }

    public override string EnglishName
    {
      get { return "TestCsCommand"; }
    }

    protected bool PlaneThroughPoints(Point3d[] points, out Plane plane, out BoundingBox box)
    {
      box = new BoundingBox(Point3d.Unset, Point3d.Unset);
      
      var rc = Plane.FitPlaneToPoints(points, out plane);
      if (rc != PlaneFitResult.Success) 
        return false;
      
      var min = Point3d.Unset;
      var max = Point3d.Unset;

      for (var i = 0; i < points.Length; i++)
      {
        double s, t;
        if (plane.ClosestParameter(points[i], out s, out t))
        {
          var p = new Point3d(s, t, 0.0);
          if (0 == i)
          {
            min = max = p;
          }
          else
          {
            if (p.X < min.X) min.X = p.X;
            else if (max.X < p.X) max.X = p.X;
            if (p.Y < min.Y) min.Y = p.Y;
            else if (max.Y < p.Y) max.Y = p.Y;
            if (p.Z < min.Z) min.Z = p.Z;
            else if (max.Z < p.Z) max.Z = p.Z;
          }
        }
      }

      box = new BoundingBox(min, max);

      return true;
    }

    protected override Result RunCommand(RhinoDoc doc, RunMode mode)
    {
      var go = new GetObject();
      go.SetCommandPrompt("Select points");
      go.GeometryFilter = ObjectType.Point;
      go.SubObjectSelect = false;
      go.GetMultiple(1, 0);
      if (go.CommandResult() != Result.Success)
        return go.CommandResult();

      var points = new Point3d[go.ObjectCount];
      for (var i = 0; i < go.ObjectCount; i++)
      {
        var point_obj = go.Object(i).Point();
        if (null == point_obj)
          return Result.Failure;
        points[i] = point_obj.Location;
      }

      Plane plane;
      BoundingBox domain;
      if (!PlaneThroughPoints(points.ToArray(), out plane, out domain))
        return Result.Failure;

      var min = domain.Min;
      var max = domain.Max;
      var corners = new Point3d[4];
      corners[0] = plane.PointAt(min.X, min.Y);
      corners[1] = plane.PointAt(min.X, max.Y);
      corners[2] = plane.PointAt(max.X, max.Y);
      corners[3] = plane.PointAt(max.X, min.Y);

      var cen = domain.Center;
      var center = plane.PointAt(cen.X, cen.Y);
      plane.Origin = center;

      var gp = new FirstRotationPoint(plane, corners);
      gp.SetCommandPrompt("First reference point");
      gp.Get();
      if (gp.CommandResult() != Result.Success)
        return gp.CommandResult();

      var reference = gp.Point();

      var gx = new SecondRotationPoint(plane, reference, corners);
      gx.SetCommandPrompt("Second reference point");
      gx.Get();


      doc.Views.Redraw();

      return Result.Success;
    }
  }

  /// <summary>
  /// FirstRotationPoint
  /// </summary>
  class FirstRotationPoint : GetPoint
  {
    private readonly Point3d[] m_corners;
    private Circle m_circle;

    public FirstRotationPoint(Plane plane, Point3d[] corners)
    {
      if (corners.Length != 4)
        throw new ArgumentException("corners should be Point3d[4]");

      m_corners = corners;
      m_circle = new Circle(plane, 0.0);
      
      SetBasePoint(plane.Origin, true);
      DrawLineFromPoint(plane.Origin, true);
      Constrain(plane, false);
    }

    protected override void OnMouseMove(GetPointMouseEventArgs e)
    {
      m_circle.Radius = m_circle.Plane.Origin.DistanceTo(e.Point);
      base.OnMouseMove(e);
    }

    protected override void OnDynamicDraw(GetPointDrawEventArgs e)
    {
      e.Display.DrawCircle(m_circle, Rhino.ApplicationSettings.AppearanceSettings.TrackingColor);
      var color = Rhino.ApplicationSettings.AppearanceSettings.DefaultObjectColor;
      e.Display.DrawLine(m_corners[0], m_corners[1], color);
      e.Display.DrawLine(m_corners[1], m_corners[2], color);
      e.Display.DrawLine(m_corners[2], m_corners[3], color);
      e.Display.DrawLine(m_corners[3], m_corners[0], color);
      base.OnDynamicDraw(e);
    }
  }

  /// <summary>
  /// SecondRotationPoint
  /// </summary>
  class SecondRotationPoint : GetPoint
  {
    private Plane m_plane;
    private Point3d m_reference;
    private readonly Point3d[] m_corners;
    private bool m_draw;
    private double m_angle;
    private Arc m_arc;

    public SecondRotationPoint(Plane plane, Point3d reference, Point3d[] corners)
    {
      if (corners.Length != 4)
        throw new ArgumentException("corners should be Point3d[4]");

      m_plane = plane;
      m_reference = reference;
      m_corners = corners;

      SetBasePoint(plane.Origin, true);
      DrawLineFromPoint(plane.Origin, true);
      Constrain(plane, false);
    }

    public bool CalculateAngle(Point3d point)
    {
      var origin = m_plane.Origin;

      var v = point - origin;
      v.Unitize();
  
      var zerov = m_reference - origin;
      var radius = zerov.Length;
      zerov.Unitize();  
  
      // Dot product
      var dot = Vector3d.Multiply(zerov, v);
      dot = (dot < -1.0 ? -1.0 : (dot > 1.0 ? 1.0 : dot));
  
      var angle = Math.Acos(dot);
      var zaxis = Vector3d.CrossProduct(m_plane.XAxis, m_plane.YAxis);
      zaxis.Unitize();

      v = Vector3d.CrossProduct(zaxis, zerov);
      v.Unitize();

      var yplane = new Plane(origin, v );
      var dist = yplane.DistanceTo(point);
      if (dist < 0.0)
        angle = 2.0 * Math.PI - angle;

      m_angle = angle;

      var arc_plane =  new Plane(origin, zerov, v);
      m_arc = new Arc(arc_plane, radius, m_angle);
      return m_arc.IsValid;
    }

    protected override void OnMouseMove(GetPointMouseEventArgs e)
    {
      m_draw = CalculateAngle(e.Point);
      base.OnMouseMove(e);
    }

    protected override void OnDynamicDraw(GetPointDrawEventArgs e)
    {
      if (m_draw)
      {
        var color = Rhino.ApplicationSettings.AppearanceSettings.DefaultObjectColor;
        //e.Display.DrawArc(m_arc, color);

        //var v = (m_arc.StartPoint - m_arc.Center) * 1.5;
        //e.Display.DrawLine(m_arc.Center, m_arc.Center + v, color);

        //v = (m_arc.EndPoint - m_arc.Center) * 1.5;
        //var v1 = e.CurrentPoint - m_arc.Center;
        //if (v1.Length > v.Length)
        //  v = v1;

        //e.Display.DrawLine(m_arc.Center, m_arc.Center + v, color);
        //e.Display.DrawPoint(m_arc.Center, color);
        //e.Display.DrawPoint(m_arc.StartPoint, color);

        var xform = Transform.Rotation(m_angle, m_plane.ZAxis, m_plane.Origin);
        var corners = new Point3d[m_corners.Length];
        for (var i = 0; i < m_corners.Length; i++)
        {
          corners[i] = m_corners[i];
          corners[i].Transform(xform);
        }

        e.Display.DrawLine(corners[0], corners[1], color);
        e.Display.DrawLine(corners[1], corners[2], color);
        e.Display.DrawLine(corners[2], corners[3], color);
        e.Display.DrawLine(corners[3], corners[0], color);
      }
      base.OnDynamicDraw(e);
    }

  }

}

