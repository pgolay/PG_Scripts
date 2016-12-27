import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs



def get_input():
    blnCrv = True
    blnNice = True
    blnLoft = False
    
    if sc.sticky.has_key("oldNice"):
        blnNice = sc.sticky["oldNice"]
    if sc.sticky.has_key("oldLoft"):
        blnLoft = sc.sticky["oldLoft"]
    if sc.sticky.has_key("oldCrv"):
        blnCrv = sc.sticky["oldCrv"]
        
    sc.doc.Views.Redraw()
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.EdgeFilter
    go.DisablePreSelect()
    
    optToggleCurve = Rhino.Input.Custom.OptionToggle(blnCrv,"No","Yes")
    go.AddOptionToggle( "Curve", optToggleCurve )
    
    optToggleNice = Rhino.Input.Custom.OptionToggle(blnNice,"No","Yes")
    go.AddOptionToggle( "Nice", optToggleNice )
    
    optToggleLoft = Rhino.Input.Custom.OptionToggle(blnLoft,"No","Yes")
    go.AddOptionToggle( "BlendyLoft", optToggleLoft )

    go.SetCommandPrompt("Select a surface edge. Select the nice edge first.")
    
    while True:

        #get_rc = go.GetMultiple(2, -1)
        get_rc = go.GetMultiple(2,-1)

        if go.CommandResult() != Rhino.Commands.Result.Success:
            return go.CommandResult()
            
        if get_rc == Rhino.Input.GetResult.Option:
            blnNice = optToggleNice.CurrentValue
            sc.sticky["oldNice"] = blnNice
            blnLoft = optToggleLoft.CurrentValue
            sc.sticky["oldLoft"] = blnLoft
            blnCrv = optToggleCurve.CurrentValue
            sc.sticky["oldCrv"] = blnCrv
            
            continue
        if get_rc==Rhino.Input.GetResult.Object:
            break
            
    objRefs = [go.Object(i) for i in range(go.ObjectCount)]

    return objRefs, blnNice, blnLoft, blnCrv
    
    
    
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


def DeeGree(srfId,srfA, srfB, idxA, idxB):

    objRef = Rhino.DocObjects.ObjRef(sc.doc.Objects.Find(srfId))
    dir = 0
    dir2 = 1
    srf = objRef.Geometry().Surfaces[0]
    Id = srfId# objRef.ObjectId
    
    degU = srf.Degree(0)
    degV = srf.Degree(1)
    deg = srf.Degree(dir)
    gripOn = rs.ObjectGripsOn(Id)

    rs.EnableRedraw (False)
    rs.EnableObjectGrips(Id, True)

    if deg % 2 == 1: 
        print "Nope, not an even degree"
        return

    uvList  =  surface_UV_idx(srf)
    
    dirList = uvList[dir]
    dir2List = uvList[dir2]
   
    if len(dir2List) != deg + 1:
        print "Nope, not single span"
        return
        
    x = int((deg+1)/2)
    Row  = dir2List[int((deg+1)/2)]
    apt = []
    for idx in Row:
        apt.append(rs.ObjectGripLocation(Id, idx))

    sDeg =  ("Enter " + str(deg+ 2) + " Enter")
    if dir == 0: sDeg = ( " " + str(deg+ 2) + " Enter Enter")
    rs.EnableObjectGrips(Id, False)
    sc.doc.Objects.UnselectAll()
    sc.doc.Objects.Select(Id)
    rs.Command ("ChangeDegree" + sDeg)
    rs.EnableObjectGrips (Id, True)
    
    brep = sc.doc.Objects.Find(Id)
    srf = brep.Geometry.Surfaces[0]
    uvList  =  surface_UV_idx(srf)
    
    dirList = uvList[dir]
    dir2List = uvList[dir2]
    RowIdx = int((deg+3)/2)
    Row  = dir2List[RowIdx]
    BaseRow = dir2List[0]
    Row1 = dir2List[1]
    LastRow = dir2List[len(dir2List)-1]
    PenRow = dir2List[len(dir2List)-2]
    n = 0
    
    for idx in Row:
        rs.ObjectGripLocation(Id, idx, apt[n])
        n = n + 1
        

    #get indices for point rows of the inputs
    # that are parallel to the edges.

    uvListA  =  surface_UV_idx(srfA)
    uvListB  =  surface_UV_idx(srfB)
    
    if idxA == 1:
        BaseA = uvListA[0][0]
        NextA = uvListA[0][1]
    elif idxA ==3:
        BaseA = uvListA[0][len(uvListA)-1]
        NextA = uvListA[0][len(uvListA)-2]
    elif idxA ==0:
        BaseA = uvListA[1][0]
        NextA = uvListA[1][1]
    elif idxA ==2:
        BaseA = uvListA[1][len(uvListA)-1]
        NextA = uvListA[1][len(uvListA)-2]
        
        
    if idxB == 1:
        BaseB = uvListB[0][0]
        NextB = uvListB[0][1]
    elif idxB ==3:
        BaseB = uvListB[0][len(uvListB)-1]
        NextB = uvListB[0][len(uvListB)-2]
    elif idxB ==0:
        BaseB = uvListB[1][0]
        NextB = uvListB[1][1]
    elif idxB ==2:
        BaseB = uvListB[1][len(uvListB)-1]
        NextB = uvListB[1][len(uvListB)-2]
        
        
    pass
    cvA = rs.SurfacePoints(srfA)
    cvB = rs.SurfacePoints(srfB)
    
    ptsA = []
    ptsB = []
    
    # get the point locations for the second rows of the input surfaces
    for idx in NextA:
        ptsA.append(cvA[idx])
    pLineA = Rhino.Geometry.Polyline(ptsA)
    sc.doc.Objects.AddPolyline(pLineA)
        
    for idx in NextB:
        ptsB.append(cvB[idx])
    pLineB = Rhino.Geometry.Polyline(ptsB)
    sc.doc.Objects.AddPolyline(pLineB)
    # try to find the nearest second row point on the inputs to an edge point
    # of the loft and move the second row point on the loft to a line
    # between the edge point on the loft and the nearest second row control 
    # polygon segment on the input surface. Phew. The goal is to get close to tangency.
    
    for idx in range(len(BaseRow)):
        pt = rs.ObjectGripLocation(Id,BaseRow[idx])
        nearPt = Rhino.Geometry.Polyline.ClosestPoint(pLineA,pt)
        
    #        rc, parU, parV = srfB.ClosestPoint(pt)
    #        rc, plane = srfB.FrameAt(parU, parV)
    #        plane.Origin = pt
        rs.ObjectGripLocation(Id, Row1[idx],nearPt)
        
    for idx in range(len(LastRow)):
        pt = rs.ObjectGripLocation(Id,LastRow[idx])
        rc, parU, parV = srfA.ClosestPoint(pt)
        rc, plane = srfA.FrameAt(parU, parV)
        plane.Origin = pt
        rs.ObjectGripLocation(Id, PenRow[idx],rs.PlaneClosestPoint(plane,rs.ObjectGripLocation(Id, PenRow[idx])))
        
    if not gripOn:rs.EnableObjectGrips (Id, False)
    rs.EnableRedraw (True)
    

def GetTheoretical():
    
    inputs = get_input()
    if not inputs: return
    if inputs == Rhino.Commands.Result.Cancel:return
    
    edges = inputs[0]
    Nice = inputs[1]
    blnLoft = inputs[2]
    blnCrv = inputs[3]
    
    if not blnCrv and not blnLoft:
        print "Curve and Loft set to No. Nothing done."
        return
        
    x = edges[0]
    a = edges[1]
    
    y = x.Geometry()
    brepx = y.Brep

    idxx = x.GeometryComponentIndex.Index
    trimx = y.Brep.Trims[idxx]
    curvex = y.ToNurbsCurve()
    srfx = brepx.Faces[0].ToNurbsSurface()
    blnTrimx = False
    
    if not brepx.IsSurface:
        #tempx = sc.doc.Objects.AddBrep(srfx.ToBrep)
        blnTrimx = True
    
    b = a.Geometry()
    idxa = a.GeometryComponentIndex.Index
    brepa = b.Brep
    trima = brepa.Trims[idxa]
    curvea = b.ToNurbsCurve()
    srfa = b.Brep.Faces[0].ToNurbsSurface()
    blnTrima = False
    if not brepa.IsSurface:
        #tempx = sc.doc.Objects.AddBrep(srfx.ToBrep)
        blnTrima = True
    
    if not Rhino.Geometry.Curve.DoDirectionsMatch(curvex, curvea):
        curvea.Reverse()
        
    p1 = curvea.PointAtStart
    p2 = curvex.PointAtEnd
    dist = Rhino.Geometry.Point3d.DistanceTo(p1, p2)
    
    if blnTrima and blnTrimx:
        testInt =  Rhino.Geometry.Intersect.Intersection.SurfaceSurface(srfa,srfx, .001)
    elif blnTrima and not blnTrimx:
          ext1 = srfx.Extend(trimx.IsoStatus, dist, False)
          #sc.doc.Objects.Add(ext1)
          testInt = Rhino.Geometry.Intersect.Intersection.SurfaceSurface(ext1,srfa, .001)
    elif blnTrimx and not blnTrima:
          ext1 = srfa.Extend(trima.IsoStatus, dist, False)
          #sc.doc.Objects.Add(ext1)
          testInt = Rhino.Geometry.Intersect.Intersection.SurfaceSurface(ext1,srfx, .001)
    else: 
        ext1 = srfx.Extend(trimx.IsoStatus, dist, True)
        #sc.doc.Objects.Add(ext1)
        ext2 = srfa.Extend(trima.IsoStatus, dist, True)
        #sc.doc.Objects.Add(ext2)
        testInt = Rhino.Geometry.Intersect.Intersection.SurfaceSurface(ext1,ext2, .001)
      
    if not testInt: return
    if testInt[1][0]: intCrv = testInt[1][0]
    
    if not Rhino.Geometry.Curve.DoDirectionsMatch(curvex, intCrv):
        intCrv.Reverse()
        
    intCrv = Rhino.Geometry.Curve.Fit(intCrv, 3, 0, .05)
    crvId = sc.doc.Objects.AddCurve(intCrv)

    sc.doc.Objects.Select(crvId)

    if Nice:
        tempedge = sc.doc.Objects.AddCurve(curvex)
        strSel = " SelID " + str(tempedge)
        sc.doc.Objects.UnselectAll()
        sc.doc.Objects.Select(crvId)#Select the intersection curve to rebuild
        
        if blnLoft: 
            temp_a = sc.doc.Objects.AddCurve(curvea)
            sc.doc.Objects.Select(temp_a)#Select the second edge curve to rebuild
            
        #rebuild using the first edge, as a curve, as MasterCurve, then delete this curve
        reb = rs.Command ("-Rebuild SelectMasterCurve" + strSel + " DeleteInput=Yes Enter")
        sc.doc.Objects.Delete(tempedge, True)
        
        if reb:
            intCrv = sc.doc.Objects.Find(crvId).Geometry
            if blnLoft:
                curvea = sc.doc.Objects.Find(temp_a).Geometry
    if blnLoft:
        
        u = Rhino.Geometry.Point3d.Unset
        t = Rhino.Geometry.LoftType.Loose
        
        curves = [curvex,intCrv,curvea]
        newBrep = Rhino.Geometry.Brep.CreateFromLoft(curves, u, u, t, False)
        
        sc.doc.Objects.Delete(temp_a,True)
        
        if newBrep:
            loftId = sc.doc.Objects.AddBrep(newBrep[0])
            if loftId:
                sc.doc.Objects.UnselectAll()
                DeeGree(loftId, srfa, srfx, idxx, idxa)

    if not blnCrv: sc.doc.Objects.Delete(crvId,True)
    pass
    
    
GetTheoretical()