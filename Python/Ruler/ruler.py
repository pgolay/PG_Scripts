import Rhino
import scriptcontext
import System

def CustomOverlayDraw(sender, args):
    vp = args.Viewport
    if not vp.IsParallelProjection or vp.ParentView is Rhino.Display.RhinoPageView:
        return
    s2w = vp.GetTransform(Rhino.DocObjects.CoordinateSystem.Screen, Rhino.DocObjects.CoordinateSystem.World)
    
    size = vp.Size
    pt0 = Rhino.Geometry.Point3d(size.Width-20, size.Height-20,0)
    pt1 = Rhino.Geometry.Point3d(pt0.X-200, pt0.Y,0)
    pt2 = Rhino.Geometry.Point3d(pt1.X, pt0.Y-30, 0)
    pt3 = Rhino.Geometry.Point3d(pt0.X, pt2.Y, 0)
    pts = [pt0, pt1, pt2, pt3]
    fontheight = 20
    screen_pt = Rhino.Geometry.Point2d((pt0.X+pt1.X)/2, (pt2.Y+15))
    for pt in pts: pt.Transform(s2w)
    args.Display.PushDepthTesting(False)
    args.Display.DrawPolygon(pts, System.Drawing.Color.LightGray, True)
    dist = abs(pts[0].X - pts[1].X)
    message = '%.2f' % dist
    args.Display.Draw2dText(message, System.Drawing.Color.Black, screen_pt,True, fontheight)
    args.Display.PopDepthTesting()

def ToggleRuler():
    KEY = "ruler"
    if( scriptcontext.sticky.has_key(KEY) ):
        print 'Turn Ruler OFF'
        func = scriptcontext.sticky[KEY]
        Rhino.Display.DisplayPipeline.DrawForeground -= func
        scriptcontext.sticky.Remove(KEY)
    else:
        print 'Turn Ruler ON'
        func = CustomOverlayDraw
        Rhino.Display.DisplayPipeline.DrawForeground += func
        scriptcontext.sticky["ruler"] = func
    scriptcontext.doc.Views.Redraw()

if __name__=="__main__":
    ToggleRuler()
