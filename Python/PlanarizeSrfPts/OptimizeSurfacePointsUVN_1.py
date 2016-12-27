import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
"""
To Do:
    Allow for curves.
Options:
- smooth one point (click)- use the row for fairing but only move the one point
- smooth selected points - use the row(s) for fairing but only move the selected points
- Smooth all interior points
----
- Maintain parallel edge tangency (Force 2nd row point movement along last control polygon)
- Maintain all edge tangency (reguires at least 5 points in the smooth direction)
----
----
Also:
    Move with falloff
    Move symmetrically

"""

def get_input():
    oldDir = False
    oldIdx = 0
    oldNormal = False
    
    if sc.sticky.has_key("PlanarizeDir"):
        oldDir  = sc.sticky["PlanarizeDir"]
    if sc.sticky.has_key("PlaneStyle"):
        oldIdx  = sc.sticky["PlaneStyle"]
    if sc.sticky.has_key("blnNormal"):
        oldNormal  = sc.sticky["blnNormal"]
        
    dir = oldDir
    listIndex = oldIdx
    blnNormal = oldNormal
    
    sc.doc.Objects.UnselectAll()
    sc.doc.Views.Redraw()
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Grip
    
    optToggleDir = Rhino.Input.Custom.OptionToggle(oldDir, "U","V")
    optToggleNormal = Rhino.Input.Custom.OptionToggle(oldNormal, "No","Yes")
    optList = Rhino.Input.Custom.GetOption()
    listValues = "Auto", "WorldVertical", "CPlaneVertical"

    opList = go.AddOptionList("Plane", listValues, listIndex)
    go.AddOptionToggle("Direction",optToggleDir)
    go.AddOptionToggle("SmoothNormal", optToggleNormal)
    go.SetCommandPrompt("Select a surface control point")
    
    while True:
        get_rc = go.Get()

        if go.CommandResult() != Rhino.Commands.Result.Success:
            return go.CommandResult()
        if get_rc==Rhino.Input.GetResult.Object:
            objRef = go.Object(0)
            grip = objRef.Object()
            break
        elif get_rc==Rhino.Input.GetResult.Option:
            dir = optToggleDir.CurrentValue
            sc.sticky["PlanarizeDir"] = dir
            blnNormal = optToggleNormal.CurrentValue
            sc.sticky["blnNormal"] = blnNormal
            if go.OptionIndex()==opList:
              listIndex = go.Option().CurrentListOptionIndex
              sc.sticky["PlaneStyle"] = listIndex
            continue
            
    if grip is None:return
    sc.doc.Views.Redraw()
    return grip.OwnerId, grip.Index, grip.CurrentLocation, dir, listIndex, blnNormal


def planarize_srf_pts():

    while True:
        nextRow=None
        prevRow=None
        #aGrip = rs.GetObjectGrip("Select a control point", False, True)
        aGrip = get_input()
        if not aGrip: return
        if aGrip ==  Rhino.Commands.Result.Cancel: return
        Id = aGrip[0]
        Idx = aGrip[1]
        dir = aGrip[3]
        planeStyle = aGrip[4]
        blnNormal = aGrip[5]
        
        if dir: 
            dir = 1
        else:
             dir = 0
             
        if  rs.IsSurface(Id):
            Rows = surface_UV_idx(Id)[dir]
            Max = len(Rows)
            
            for i in range(Max):
                if Idx  in(Rows[i]):

                    Row = Rows[i]
                    if i <>0:
                        prevRow = Rows[i-1]
                    if i < Max-1:
                        nextRow = Rows[i+1]
                    break

            if planeStyle == 0:
                n = 0
            else:
                n = 5
                
            while n < 6:
                apts = []
                for idx in Row:
                    apts.append(rs.ObjectGripLocation(Id,idx))

                Plane = get_ref_plane(planeStyle, apts)
                p1 = False
                p2 = False
                
                for idx in range(1, len(Row) - 1):
                    pts = []
                    if nextRow:
                        pts.append( rs.LinePlaneIntersection([rs.ObjectGripLocation(Id,nextRow[idx]),apts[idx]], Plane) )
                        p1 = True
   
                    if prevRow:
                        pts.append( rs.LinePlaneIntersection([rs.ObjectGripLocation(Id,prevRow[idx]),apts[idx]], Plane) )
                        p2 = True
                        
                    
                    if not p1 or not p2: 
                        targ = pts[0]
                    else: targ = pts[rs.PointArrayClosestPoint(pts, apts[idx])]
                    
                    rs.ObjectGripLocation(Id,Row[idx], targ)
        

                n = n + 1
            
            if blnNormal:
                apts = []
                for idx in Row:
                    apts.append(rs.ObjectGripLocation(Id,idx))
                FairPtsNormal(Id, apts, Row, .1)

 
def FairPtsNormal(Id, apts, aIdx, factor):
    srf = sc.doc.Objects.Find(Id).Geometry.Surfaces[0]
    vec_list = []
    l = 0
    n = 0
    for idx in range(1, len(apts) - 1):
        par = rs.BrepClosestPoint(Id, apts[idx])[1]
        d = rs.EvaluateSurface(Id, par[0], par[1])
        vec =apts[idx]-d
        vec_list.append(vec)
        l = l + vec.Length
        n = n + 1
    fairTol = factor*(l/n)

    curve = Rhino.Geometry.Curve.CreateInterpolatedCurve(apts,3,0)
    #pc = Rhino.Geometry.Curve.ProjectToPlane(curve, plane)
    fc = Rhino.Geometry.Curve.Fair(curve,fairTol,.05,0,0,5)
    #ping = sc.doc.Objects.AddCurve(pc)
    if fc:
        for idx in range(1, len(apts) - 1):
            test  = apts[idx]
            #grip closest point paranmeter on the faired curve:
            par = fc.ClosestPoint(test,0.0)
            # closest 3d point:
            temp = fc.PointAt(par[1])
            #temp closest point parameter on the surface:
            par = rs.SurfaceClosestPoint(Id,temp)
            #temp's closest 3d point on the surface
            p1 = rs.EvaluateSurface(Id,par[0], par[1] )
            #Distance from temp to the surface
            d1 = rs.Distance(temp,p1)
            #grip closest point parameter on the surface:
            par = rs.SurfaceClosestPoint(Id,test)
            #Nomral at the grip closesyt point:
            vecNorm = rs.SurfaceNormal(Id, par)*d1
            #Location of the normal:
            base = rs.EvaluateSurface(Id, par[0], par[1])
            # a new grip location the same distance from the surface
            # as the faired curve at the same point
            targ = base + vecNorm

            rs.ObjectGripLocation(Id,aIdx[idx], targ)


def get_ref_plane(intStyle, pts):
    
    if intStyle > 0:
        if intStyle ==1:
            tempPlane = Rhino.Geometry.Plane.WorldXY
        elif intStyle == 2:
            tempPlane = rs.ViewCPlane()
            
        p1 = tempPlane.ClosestPoint(pts[0])
        p2 = tempPlane.ClosestPoint(pts[len(pts)-1])
        vecX = p2-p1
        n = Rhino.Geometry.Vector3d.Unitize(vecX)
        newPlane = Rhino.Geometry.Plane(p1,vecX,tempPlane.ZAxis)
            
    else:
        newPlane = rs.PlaneFitFromPoints(pts)
            

    return newPlane

    
    

def surface_UV_idx(srf):
  
    aCount = rs.SurfacePointCount(srf)
    uCount = aCount[0]
    vCount = aCount[1]
   
    uList = []
    vList = []
    
    for i in range(uCount):
        vList.append([])
    for i in range(vCount):
        uList.append([])

    for i in range (vCount):
        for j in range(uCount):
            uList[i].append (i + (j*(vCount)))
            
    for i in range (uCount):
        for j in range(vCount):
            vList[i].append (j + (i*(vCount)))
            
            
    return [uList,vList]

  
    
if __name__ == '__main__':
    planarize_srf_pts()