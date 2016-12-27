import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

    
def LoftCrown():
    
    
    def get_inputs(): 
        oldDeg = 3
        oldPts = 4
        oldReb = False
        if sc.sticky.has_key("RebuildPointCount"):
            oldPts = sc.sticky["RebuildPointCount"]
        if sc.sticky.has_key("RebuildDegree"):
            oldDeg = sc.sticky["RebuildDegree"]
        if sc.sticky.has_key("blnRebuild"):
            oldReb = sc.sticky["blnRebuild"]
        
            
        go = Rhino.Input.Custom.GetObject()
        #add a geometry filter for the getter
        go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
        go.SubObjectSelect = True
        #go.DeselectAllBeforePostSelect = True
        go.OneByOnePostSelect = True
        
        go.SetCommandPrompt("Select two curves.")

        blnRebuild = Rhino.Input.Custom.OptionToggle(oldReb, "No", "Yes")
        intPts = Rhino.Input.Custom.OptionInteger(oldPts,True, 2)
        intDeg = Rhino.Input.Custom.OptionInteger(oldDeg,1,11)
        
        go.AddOptionToggle("RebuildCurves", blnRebuild)
        go.AddOptionInteger("PointCount",intPts)
        go.AddOptionInteger("RebuildDegree",intDeg)
        
        points = oldPts
        degree = oldDeg
        blnReb = False
        while True:
            # perform the get operation. 
            get_rc = go.GetMultiple(2, -1)
            
            if go.CommandResult()!=Rhino.Commands.Result.Success:
                return go.CommandResult()
                
            if go.CommandResult() == Rhino.Commands.Result.Cancel: return 
            
            if get_rc==Rhino.Input.GetResult.Object:
                objrefs = go.Object
                sc.doc.Views.Redraw()
                break
            elif get_rc == Rhino.Input.GetResult.Option:
               points = intPts.CurrentValue
               degree = intDeg.CurrentValue
               blnReb = blnRebuild.CurrentValue
               sc.sticky["RebuildDegree"] = degree
               sc.sticky["RebuildPointCount"] = points
               sc.sticky["blnRebuild"] = blnReb
               
               
               continue
        return ( [objrefs(0),objrefs(1)], degree, points, blnReb)

    curves = []
    objRefs, intDeg, intPts, blnReb = get_inputs()
    
    if not objRefs: return
    
    pU = Rhino.Geometry.Point3d.Unset
    strt = Rhino.Geometry.LoftType.Straight 
    
    for objRef in objRefs:
        idx = objRef.GeometryComponentIndex.Index
        if idx != -1:# i.e. an edge curve
            curves.append(objRef.Object().Geometry.Edges[idx].ToNurbsCurve())
        else:# just a curve
            curves.append(objRef.Object().Geometry)

    if not Rhino.Geometry.Curve.DoDirectionsMatch(curves[0],curves[1]): curves[0].Reverse()
    
 
    crvList = []
 
    for crv in curves:
        if blnReb: 
            crvList.append(Rhino.Geometry.Curve.Rebuild(crv,intPts, intDeg, preserveTangents=True))
        else: crvList.append (crv)
            
            
    EdgeSrf = Rhino.Geometry.Brep.CreateEdgeSurface(crvList)
    
    if EdgeSrf: 
        srfId = sc.doc.ActiveDoc.Objects.AddBrep(EdgeSrf)
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