################################################################################
# ArcCircleTesters.py -- June 2014
# If this code works, it was written by Dale Fugier.
# If not, I don't know who wrote it.
# Works with Rhinoceros 5.
################################################################################
import scriptcontext
import rhinoscriptsyntax as rs
import Rhino

class DrawTextDotsConduit(Rhino.Display.DisplayConduit):
    def __init__(self, points):
        self.points = points
        self.bbox = Rhino.Geometry.BoundingBox()
        for point in points:
            self.bbox.Union(point)
    def CalculateBoundingBox(self, e):
        e.IncludeBoundingBox(self.bbox)
    def DrawOverlay(self, e):
        for point in self.points:
            e.Display.DrawDot(point, point.ToString())

def DrawTextDots():
    points = rs.GetPoints()
    if points:
        conduit = DrawTextDotsConduit(points)
        conduit.Enabled = True
        scriptcontext.doc.Views.Redraw()
        rs.GetString("Press <Enter> to continue")
        conduit.Enabled = False
        scriptcontext.doc.Views.Redraw()
 
if __name__=="__main__":
    DrawTextDots()
