import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

    
def LoftCrown():
    
    
    def get_inputs():  
    
        go = Rhino.Input.Custom.GetObject()
        #add a geometry filter for the getter
        go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
        go.SubObjectSelect = True
        #go.DeselectAllBeforePostSelect = True
        go.OneByOnePostSelect = True
        
        go.SetCommandPrompt("Select two curves.")
        
        while True:
            # perform the get operation. 
            get_rc = go.GetMultiple(2, -1)
            
            if go.CommandResult()!=Rhino.Commands.Result.Success:
                return go.CommandResult()
                
            if get_rc==Rhino.Input.GetResult.Object:
                objrefs = go.Object
                sc.doc.Views.Redraw()
            break
        return ( objrefs(0),objrefs(1))

    curves = []
    inputs = get_inputs()
    if inputs == Rhino.Commands.Result.Cancel: return
    
    pU = Rhino.Geometry.Point3d.Unset
    strt = Rhino.Geometry.LoftType.Straight 
    
    for input in inputs:
        idx = input.GeometryComponentIndex.Index
        if idx != -1:# i.e. an edge curve
            curves.append(input.Object().Geometry.Edges[idx].ToNurbsCurve())
        else:# just a curve
            curves.append(input.Object().Geometry)

    if not Rhino.Geometry.Curve.DoDirectionsMatch(curves[0],curves[1]): curves[0].Reverse()

    u = Rhino.Geometry.Point3d.Unset
    t = Rhino.Geometry.LoftType.Loose
    #EdgeSrf = Rhino.Geometry.Brep.CreateEdgeSurface(curves)
    EdgeSrf =  Rhino.Geometry.Brep.CreateFromLoft(curves, u,u, t, False)
    if EdgeSrf: 
        srfId = sc.doc.ActiveDoc.Objects.AddBrep(EdgeSrf[0])
        if not srfId: return
    rs.UnselectAllObjects()
    rs.SelectObject(srfId)
    rs.Command("ChangeDegree 2 Enter")
    rs.UnselectAllObjects()
    rs.EnableObjectGrips(srfId)
    x =rs.SurfacePointCount(srfId)
    count = rs.SurfacePointCount(srfId)[1]
    
    for pt in range (count, 2*count):
        rs.SelectObjectGrip (srfId,pt)
        
    rs.Command ("MoveUVN")
    
    
    
    pass
    sc.doc.Views.Redraw()

if __name__ == '__main__':
    LoftCrown()