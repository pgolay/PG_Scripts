import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

    

def ShowInDetails():
    if sc.doc.Views.ModelSpaceIsActive:
        print "A layout must be active for this command."
        return
    view = sc.doc.Views.ActiveView
    detail = None
    if view != Rhino.Display.RhinoPageView:
        dets = sc.doc.Views.ActiveView.GetDetailViews()
        if len(dets) == 0:
            print "No detail views found in this layout"
            return
    
    dets = sc.doc.Views.ActiveView.GetDetailViews()
    if len(dets)>0:
        for det in dets:
            if not det.IsActive:
                det.IsActive = True
                sc.doc.Views.Redraw()
                rs.Command("_ShowInDetail")
        pass
    rs.UnselectAllObjects()    
    rs.EnableRedraw(True)
    view.SetPageAsActive()
    sc.doc.Views.ActiveView = view
    sc.doc.Views.Redraw()
        
if( __name__ == "__main__" ):
    ShowInDetails()