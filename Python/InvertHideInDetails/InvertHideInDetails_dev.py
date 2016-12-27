import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs



def InvertHideInDetails():
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
        for det in dets:
            if det.IsActive:
                detail= det
    objs = []
    Ids = rs.SelectedObjects()
    
    if detail is None:
        while True:
            go = Rhino.Input.Custom.GetObject()
            go.GeometryFilter = Rhino.DocObjects.ObjectType.Detail
            
            if sc.doc.Views.ActiveView.PageIsActive:
                go.SetCommandPrompt("Please select a detail view.")
                
            ret = go.Get()
            if go.CommandResult()!=Rhino.Commands.Result.Success:
                return go.CommandResult()
            if ret==Rhino.Input.GetResult.Object:
                detail =   sc.doc.Objects.Find(  go.Object(0).ObjectId)
                detail.IsActive = True
                rs.UnselectAllObjects()
                break
                
        if len(Ids) == 0:
            go2 = Rhino.Input.Custom.GetObject()
            go2.EnablePreSelect(False, True)
            if len(Ids) == 0:
                
                go2.SetCommandPrompt("Select objects to keep visible")
                rc = go2.GetMultiple(1,0)
                if go.CommandResult()!=Rhino.Commands.Result.Success:
                    return go.CommandResult()
                if ret==Rhino.Input.GetResult.Object:
                    Ids = [go2.Object(i).ObjectId for i in range(go2.ObjectCount)]

    rs.UnselectAllObjects()
    rs.SelectObjects(Ids)
    rs.EnableRedraw(False)
    rs.Command("_Invert _HideInDetail _Invert ")
    
    dets = sc.doc.Views.ActiveView.GetDetailViews()
    if len(dets)>0:
        for det in dets:
            if not det.IsActive:
                det.IsActive = True
                sc.doc.Views.Redraw()
                rs.Command("_Invert _HideInDetail _Invert ")
        pass
    rs.UnselectAllObjects()    
    rs.EnableRedraw(True)
    view.SetPageAsActive()
    sc.doc.Views.ActiveView = view
    sc.doc.Views.Redraw()
        
if( __name__ == "__main__" ):
    InvertHideInDetails()