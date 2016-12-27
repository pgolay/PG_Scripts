import scriptcontext
import rhinoscriptsyntax as rs
import Rhino
import System

class DrawBrepEdgesConduit(Rhino.Display.DisplayConduit):
    # class members
    draw_color = System.Drawing.Color.Pink
    # class constructor
    def __init__(self, brep):
        self.brep = brep
    # DrawOverlay override
    def DrawOverlay(self, e):
        for edge in self.brep.Edges:
            e.Display.DrawCurve(edge, self.draw_color, 3)

def TestDrawBrepEdges():
    # Pick a Brep
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt('Select Brep')
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Brep
    go.Get()
    if (go.CommandResult() == Rhino.Commands.Result.Success):
        # Get some stuff...
        obj = go.Object(0).Object()    
        brep = go.Object(0).Brep()
        if obj and brep:
            # Unselect the object
            obj.Select(False)
            # Create and enable the conduit
            conduit = DrawBrepEdgesConduit(brep)
            conduit.Enabled = True
            scriptcontext.doc.Views.Redraw()
            # Wait for the user...
            rs.GetString('Press <Enter> to continue')
            # Disable the conduit
            conduit.Enabled = False
            scriptcontext.doc.Views.Redraw()
 
if __name__=="__main__":
    TestDrawBrepEdges()