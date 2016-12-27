import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

def get_input():
    oldDir = False
    oldIdx = 0
    
    if sc.sticky.has_key("PlanarizeDir"):
        oldDir  = sc.sticky["PlanarizeDir"]
    if sc.sticky.has_key("PlaneStyle"):
        oldIdx  = sc.sticky["PlaneStyle"]
    dir = oldDir
    listIndex = oldIdx
    
    sc.doc.Objects.UnselectAll()
    sc.doc.Views.Redraw()
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Grip
    
    optToggleDir = Rhino.Input.Custom.OptionToggle(oldDir, "U","V")
    optList = Rhino.Input.Custom.GetOption()
    listValues = "Auto", "WorldVertical", "CPlaneVertical", "View"

    opList = go.AddOptionList("Plane", listValues, listIndex)
    go.AddOptionToggle("Direction",optToggleDir)
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
            if go.OptionIndex()==opList:
              listIndex = go.Option().CurrentListOptionIndex
              sc.sticky["PlaneStyle"] = listIndex
            continue
            
    if grip is None:return
    sc.doc.Views.Redraw()
    return grip.OwnerId, grip.Index, grip.CurrentLocation, dir, listIndex
    
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
        
        if dir: 
            dir = 1
        else:
             dir = 0
             
        x = Surface_UV_idx(Id)
        if  rs.IsSurface(Id):
            Rows = Surface_UV_idx(Id)[dir]
            Max = len(Rows)
            
            for i in range(Max):
                if Idx  in(Rows[i]):
                    rowIdx = i
                    Row = Rows[i]
                    if rowIdx<>0:
                        prevRow = Rows[i-1]
                    if rowIdx < Max-1:
                        nextRow = Rows[i+1]
                    break
            apts = []

            if planeStyle == 0:
                n = 0
            else:
                n = 4
                
            while n < 5:
                for idx in Rows[rowIdx]:
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
                    

def get_ref_plane(intStyle, pts):
    
    if intStyle > 0:
        if intStyle ==1:
            tempPlane = Rhino.Geometry.Plane.WorldXY
        elif intStyle == 2:
            tempPlane = rs.ViewCPlane()
            
        else:
            tempPlane = rs.ViewCameraPlane()
            
        p1 = tempPlane.ClosestPoint(pts[0])
        p2 = tempPlane.ClosestPoint(pts[len(pts)-1])
        vecX = p2-p1
        n = Rhino.Geometry.Vector3d.Unitize(vecX)
        newPlane = Rhino.Geometry.Plane(p1,vecX,tempPlane.ZAxis)
            
    else:
        newPlane = rs.PlaneFitFromPoints(pts)
            

    return newPlane

    
    

def Surface_UV_idx(srf):
  
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