import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
"""
To Do:
 -Allow for curves.
Options:
- smooth one point (click)- use the row for fairing but only move the one point
- smooth selected points - use the row(s) for fairing but only move the selected points
- smooth all interior points
----
----
Also:
    move points with falloff
    move points symmetrically

"""

def get_input():
    
    #Defaults
    oldDir = False
    oldPlane = 0
    oldNormal = False
    oldTan = 1
    oldMode = 1
    
    #Stored values is any
    if sc.sticky.has_key("PreserveTangency"):
        oldTan  = sc.sticky["PreserveTangency"]
    if sc.sticky.has_key("SmoothDir"):
        oldDir  = sc.sticky["SmoothDir"]
    if sc.sticky.has_key("PlaneStyle"):
        oldPlane  = sc.sticky["PlaneStyle"]
    if sc.sticky.has_key("blnNormal"):
        oldNormal  = sc.sticky["blnNormal"]
    if sc.sticky.has_key("ModeValue"):
        oldMode  = sc.sticky["ModeValue"]
    
    #Reset defaults
    dir = oldDir
    planeListIndex = oldPlane
    blnNormal = oldNormal
    tanListIndex = oldTan
    modeListIndex = oldMode
    
    sc.doc.Objects.UnselectAll()
    sc.doc.Views.Redraw()
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Grip
    
 #set up the options
    optToggleDir = Rhino.Input.Custom.OptionToggle(oldDir, "U","V")
    optToggleNormal = Rhino.Input.Custom.OptionToggle(oldNormal, "No","Yes")
    
    planeValues = "Auto", "WorldVertical", "CPlaneVertical"
    tanValues = "None","Parallel", "All"
    modeValues = "Point", "Row", "All"

 #add the options
    optModeList = go.AddOptionList("Mode", modeValues, modeListIndex)
    go.AddOptionToggle("Direction",optToggleDir)
    optPlaneList = go.AddOptionList("Plane", planeValues, planeListIndex)
    optTanList = go.AddOptionList("PreserveEdgeTangency", tanValues, tanListIndex)
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
            #print go.Option.CurrentListOptionIndex
            dir = optToggleDir.CurrentValue
            sc.sticky["SmoothDir"] = dir
            blnNormal = optToggleNormal.CurrentValue
            sc.sticky["blnNormal"] = blnNormal
            
            if go.OptionIndex()==optPlaneList:
                planeListIndex = go.Option().CurrentListOptionIndex
                sc.sticky["PlaneStyle"] = planeListIndex
                
            if go.OptionIndex() == optTanList:
                tanListIndex = go.Option().CurrentListOptionIndex
                sc.sticky["PreserveTangency"] = tanListIndex
                
            if go.OptionIndex() == optModeList:
                modeListIndex = go.Option().CurrentListOptionIndex
                sc.sticky["ModeValue"] = modeListIndex
                
            continue
            
    if grip is None:return
    sc.doc.Views.Redraw()
    return grip.OwnerId, grip.Index, grip.CurrentLocation, dir, planeListIndex, blnNormal, tanListIndex, modeListIndex
    
def MovePoints(Idx, Rows, Id, Max, dir, tanStyle, planeStyle, blnNormal, blnPt, mode):
    
    ignore = 1
    nextRow = None
    prevRow = None
    
    if tanStyle == 2: ignore = 2
    
    for i in range(Max):
        if Idx  in(Rows[i]):
            Row = Rows[i]
            if i <>0:
                prevRow = Rows[i-1]
            if i < Max-1:
                nextRow = Rows[i+1]
            break
            
    startTan = False
    endTan = False
    
  # decide if we are on a tangent row:
    if i ==  1: startTan = True
    if i == Max - 2: endTan = True
    
    if planeStyle == 0:
        n = 0
    else:
        n = 5
        
    rs.EnableRedraw(False)
    
    for q in range(len(Row)):
        if Row[q] == Idx:
            break
    
    while n < 6:
        apts = []
        plane_pts = []
        for idx in Row:
            tempPt = rs.ObjectGripLocation(Id,idx)
            apts.append(tempPt)
            if blnPt and idx != Idx: 
                plane_pts.append(tempPt)
                #rs.AddPoint(tempPt)
            else:plane_pts.append(tempPt)
              
        Plane = get_ref_plane(planeStyle, plane_pts)
        p1 = False
        p2 = False
        
        if blnPt:
            for idx in range(len(Row)):
                if Row[idx] == Idx:
                    range_of_points = [idx]
                    break
        else: range_of_points = range(ignore,len(Row)-ignore)

        for idx in range_of_points:
            pts = []
            if nextRow:
                pts.append( rs.LinePlaneIntersection([rs.ObjectGripLocation(Id,nextRow[idx]),apts[idx]], Plane) )
                p1 = True
                
            if prevRow:
                pts.append( rs.LinePlaneIntersection([rs.ObjectGripLocation(Id,prevRow[idx]),apts[idx]], Plane) )
                p2 = True
                
            if tanStyle == 0 or Max < 4:
                if not p1 or not p2: 
                    targ = pts[0]
                else: targ = pts[rs.PointArrayClosestPoint(pts, apts[idx])]
                
            else: #if tangency is preserved and we are on a tangent row, move towards the edge only
                if startTan:
                    targ = pts[1]
                elif endTan: 
                    targ = pts[0]
                else:targ = pts[rs.PointArrayClosestPoint(pts, apts[idx])]
            
            rs.ObjectGripLocation(Id, Row[idx], targ)
        rs.EnableRedraw(True)
        n = n + 1
    
    if blnNormal:
        apts = []
        if mode == 0:
            if i > ignore-1 and i < Max - (ignore-1):
                for idx in Row:
                    apts.append(rs.ObjectGripLocation(Id,idx))  
                FairPtsNormal(Id, apts, [Idx], .1*1, tanStyle)
        else:
            for idx in Row:
                apts.append(rs.ObjectGripLocation(Id,idx))
            FairPtsNormal(Id, apts, Row, .1, tanStyle)

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
        tanStyle = aGrip[6]#0 = None, 1 = parallel edges 2 = all edges
        mode = aGrip[7]

        
        if tanStyle == 2:
            print "PreserveEdgeTangency=All: No adjustment will be made if row point count is less than 5."
        
        if dir: 
            dir = 1
        else:
             dir = 0
             
        if  rs.IsSurface(Id):
            rowInfo = surface_UV_idx(Id)
            Rows = rowInfo[dir]
            Cols = rowInfo[abs(1-dir)]
            Max = len(Rows)#number in the smooth direction
            
            if mode == 2:
                for p in range(1,len(Cols)-1):
                    MovePoints(Cols[0][p],Rows,Id, Max, dir, tanStyle, planeStyle, blnNormal, False, mode)
            elif mode == 0:
                MovePoints(Idx, Rows,Id, Max, dir, tanStyle, planeStyle, blnNormal, True, mode)
            else: MovePoints(Idx,Rows,Id, Max, dir, tanStyle, planeStyle, blnNormal, False, mode)

def FairPtsNormal(Id, apts, aIdx, factor, tanStyle):
    srf = sc.doc.Objects.Find(Id).Geometry.Surfaces[0]
    vec_list = []
    l = 0
    n = 0
    ignore = 1
    if tanStyle != 0: ignore = 2
    for idx in range(1, len(apts) - 1):
        par = rs.BrepClosestPoint(Id, apts[idx])[1]
        d = rs.EvaluateSurface(Id, par[0], par[1])
        vec =apts[idx]-d
        vec_list.append(vec)
        l = l + vec.Length
        n = n + 1
    fairTol = factor*(l/n)

    curve = Rhino.Geometry.Curve.CreateInterpolatedCurve(apts,3,0)
    fc = Rhino.Geometry.Curve.Fair(curve,fairTol,.05,0,0,5)
    #ping = sc.doc.Objects.AddCurve(pc)
    if fc:
        for idx in range(ignore, len(apts) - ignore):
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

            rs.ObjectGripLocation(Id, aIdx[idx], targ)

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