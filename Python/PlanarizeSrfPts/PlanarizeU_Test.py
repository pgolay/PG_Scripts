import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

def planarize_u():
    planarize()
   
def get_input():
    oldDir = False
    if sc.sticky.has_key("PlanarizeDir"):
        oldDir  = sc.sticky["PlanarizeDir"]
    dir = oldDir
    sc.doc.Objects.UnselectAll()
    sc.doc.Views.Redraw()
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Grip
    optToggleDir = Rhino.Input.Custom.OptionToggle(oldDir, "V","U")
    go.AddOptionToggle("Direction",optToggleDir)
    go.ChooseOneQuestion
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
            continue
            
    if grip is None:return
    sc.doc.Views.Redraw()
    return grip.OwnerId, grip.Index, grip.CurrentLocation, dir
    
def planarize():

    while True:
        
        #aGrip = rs.GetObjectGrip("Select a control point", False, True)
        aGrip = get_input()
        if not aGrip: return
        if aGrip ==  Rhino.Commands.Result.Cancel: return
        Id = aGrip[0]
        Idx = aGrip[1]
        dir = aGrip[3]
        
        if dir: 
            dir = 0
        else:
             dir = 1
             
             
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
            n = 0
            while n < 5:
                for idx in Rows[rowIdx]:
                    apts.append(rs.ObjectGripLocation(Id,idx))
                    
                Plane = rs.PlaneFitFromPoints(apts)
                for idx in range(1, Max-1):
                    pts = []
            #            linePrev = Rhino.Geometry.Line(rs.ObjectGripLocation(Id,prevRow[idx]),aPts[idx])
                    if nextRow:
                        pts.append( rs.LinePlaneIntersection([rs.ObjectGripLocation(Id,nextRow[idx]),apts[idx]], Plane) )
                        c = rs.ObjectGripLocation(Id,nextRow[idx])
                    if prevRow:
                        pts.append( rs.LinePlaneIntersection([rs.ObjectGripLocation(Id,prevRow[idx]),apts[idx]], Plane) )
                        b =rs.ObjectGripLocation(Id,prevRow[idx])
                        
                    
                    if not pts[0]: 
                        targ = pts[1]
                    elif not pts[1]: 
                        targ = pts[0]
                    else: targ = pts[rs.PointArrayClosestPoint(pts, apts[idx])]
                    
                    rs.ObjectGripLocation(Id,Row[idx], targ)
                    
                    n = n + 1
                    


def Surface_UV_idx(srf):
  
    aCount = rs.SurfacePointCount(srf)
    uCount = aCount[0]
    vCount = aCount[1]
   
    uList = []
    vList = []
    
    for U in range(uCount):
        uList.append([])
    for V in range(vCount):
        vList.append([])

    for i in range (uCount):
        for j in range(vCount):
            uList[i].append (i + (j*(vCount)))
            
    for i in range (vCount):
        for j in range(uCount):
            vList[i].append (j + (i*(uCount)))
    return [uList,vList]

    x = 2
    
if __name__ == '__main__':
    planarize_u()