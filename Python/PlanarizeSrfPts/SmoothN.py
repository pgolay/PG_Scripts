import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
"""
To Do:
    Add tangent and Curvature constraints to smoothing.
"""    

def get_input():
    
       #Defaults
    oldDir = False
    oldFactor = 5
    oldTan = 1
    oldMode = 1

    #Stored values if any
    if sc.sticky.has_key("SmoothN_Tangency"):
        oldTan  = sc.sticky["SmoothN_Tangency"]
    if sc.sticky.has_key("SmoothN_Dir"):
        oldDir  = sc.sticky["SmoothN_Dir"]
    if sc.sticky.has_key("SmoothN_FairFactor"):
        oldFactor  = sc.sticky["SmoothN_FairFactor"]
    if sc.sticky.has_key("SmoothN_ModeValue"):
        oldMode  = sc.sticky["SmoothN_ModeValue"]

    #Reset defaults
    dir = oldDir
    tanListIndex = oldTan
    modeListIndex = oldMode
    factor = oldFactor
    
    sc.doc.Objects.UnselectAll()
    sc.doc.Views.Redraw()
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Grip
    
    optToggleDir = Rhino.Input.Custom.OptionToggle(oldDir, "U","V")
    optDblFactor = Rhino.Input.Custom.OptionDouble(oldFactor)
    modeValues = "Point", "Row", "All"
    tanValues = "None","Parallel", "All"

    optModeList = go.AddOptionList("Mode", modeValues, modeListIndex)
    go.AddOptionToggle("Direction",optToggleDir)
    go.AddOptionDouble("SmoothFactor",optDblFactor)
    optTanList = go.AddOptionList("PreserveEdgeTangency", tanValues, tanListIndex)
    
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
            sc.sticky["SmoothN_Dir"] = dir
            factor = optDblFactor.CurrentValue
            sc.sticky["SmoothN_FairFactor"] = factor
            
            if go.OptionIndex() == optModeList:
                modeListIndex = go.Option().CurrentListOptionIndex
                sc.sticky["SmoothN_ModeValue"] = modeListIndex
                
            if go.OptionIndex() == optTanList:
                tanListIndex = go.Option().CurrentListOptionIndex
                sc.sticky["SmoothN_Tangency"] = tanListIndex

            continue
            
    if grip is None:return
    sc.doc.Views.Redraw()
    return grip.OwnerId, grip.Index, grip.CurrentLocation, dir,factor, tanListIndex, modeListIndex
    
    
def SmoothN():
    
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
        factor = aGrip[4]
        tanStyle = aGrip[5]#0 = None, 1 = parallel edges 2 = all edges
        mode = aGrip[6]
        
        if dir: 
            dir = 1
        else:
             dir = 0
        if  rs.IsSurface(Id):
            rowInfo = surface_UV_idx(Id)
            Rows = rowInfo[dir]
            Cols = rowInfo[abs(1-dir)]
            Max = len(Rows)#number in the smooth direction

            
            #find the next and previous rows
            for i in range(Max):
                if Idx  in(Rows[i]):
                    Row = Rows[i]
                    if i <>0:
                        prevRow = Rows[i-1]
                    if i < Max-1:
                        nextRow = Rows[i+1]
                    break
                    
                   
        apts = []

        
        if mode == 1:
            for idx in Row:
                apts.append(rs.ObjectGripLocation(Id,idx))        
            FairPtsNormal(Id, apts, Row, Idx ,.1*factor, tanStyle,mode)

        elif mode == 0:
            ignore = 1
            if tanStyle != 0: ignore = 2
            if i > ignore-1 and i < Max - (ignore-1):
                for idx in Row:
                    apts.append(rs.ObjectGripLocation(Id,idx))  
                FairPtsNormal(Id, apts, [Idx], Idx, .1*factor, tanStyle, mode)

        else:
            for p in range(1,len(Cols)-1):
                for idx in cols[p]:
                    apts.append(rs.ObjectGripLocation(Id,idx))
                #FairPtsNormal(Id, apts, cols[p],Idx, .1*factor, tanStyle, mode)
                FairPtsUV(Id, apts, cols[p], .1*factor, tanStyle, mode)
        
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
    
def FairPtsNormal(Id, apts, aIdx, Idx, factor, tanStyle, mode):
    srf = sc.doc.Objects.Find(Id).Geometry.Surfaces[0]
    vec_list = []
    l = 0
    n = 0
    ignore = 1
    if tanStyle != 0: ignore = 2

 #get an average distance to the surface for the points in the row:
    for idx in range(1, len(apts) - 1):
        par = rs.BrepClosestPoint(Id, apts[idx])[1]
        d = rs.EvaluateSurface(Id, par[0], par[1])
        vec =apts[idx]-d
        vec_list.append(vec)
        l = l + vec.Length
        n = n + 1
    fairTol = factor*(l/n) #Factor * average distance to surface
 
 #Interpolate a curve through the points and fair the curve
    curve = Rhino.Geometry.Curve.CreateInterpolatedCurve(apts,3,0)
    fc = Rhino.Geometry.Curve.Fair(curve,fairTol,.05,0,0,5)
    
    if fc:
        if mode == 0: #Point
            apts = [rs.ObjectGripLocation(Id, Idx)]
            range_to_test = range(1)
        else:
            range_to_test = range(ignore, len(apts) - ignore)
            
        for idx in range_to_test:
            test  = apts[idx]
             #grip closest point paranmeter on the faired curve:
            par = fc.ClosestPoint(test,0.0)
             #closest 3d point:
            temp = fc.PointAt(par[1])
             #temp closest point parameter on the surface:
            par = rs.SurfaceClosestPoint(Id,temp)
             #temp's closest 3d point on the surface
            p1 = rs.EvaluateSurface(Id,par[0], par[1] )
             #Distance from temp to the surface
            d1 = rs.Distance(temp,p1)
             #grip closest point parameter on the surface:
            par = rs.SurfaceClosestPoint(Id,test)
             #Normal at the grip closesyt point:
            vecNorm = rs.SurfaceNormal(Id, par)*d1
             #Location of the normal:
            base = rs.EvaluateSurface(Id, par[0], par[1])
             #a new grip location the same distance from the surface
             #as the faired curve at the same point
            targ = base + vecNorm
        
            rs.ObjectGripLocation(Id, aIdx[idx], targ)

if __name__ == '__main__':
    SmoothN()