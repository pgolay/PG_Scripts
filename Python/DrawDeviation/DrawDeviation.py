import Rhino
import scriptcontext as sc
import System
import math
import rhinoscriptsyntax as rs

def DrawDeviation(vp=None, doc=None):
    if not vp:
        vp = scriptcontext.doc.Views.ActiveView.ActiveViewport
    

def hack(sender, e):
    vp = e.Viewport
    doc = e.RhinoDoc
    DrawDeviation(vp, doc)
    
def test():

    
    
    pts1 =

    if( scriptcontext.sticky.has_key("Deviation_hack") ):
        Rhino.Display.DisplayPipeline.CalculateBoundingBox -= scriptcontext.sticky["hack"]
        scriptcontext.sticky.Remove("Deviation_hack")
        print "DrawDeviation mode is off"
    else:
        c1 = rs.GetObject(filter = 0, preselect = True)
        if not c1: return
        c2 =  rs.GetObject(filter = 0, preselect = False)
        if not c2: return
        
        scriptcontext.sticky["hack"] = hack
        Rhino.Display.DisplayPipeline.CalculateBoundingBox += hack
        print "DrawDeviation mode is on"
    scriptcontext.doc.Views.Redraw() 
    return 0    
    
    
test()