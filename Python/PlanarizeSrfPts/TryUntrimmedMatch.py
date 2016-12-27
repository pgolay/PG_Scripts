import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

"""
Select an edge
Dup the  edge curve
Dup all edges.
Shrink and untrim the surface

Discard the untrimmed edges that are instersected by the duped edge curve at its ends.
Of the remaining two edges, find the one that is outside the original trimmed face 
and has the surface parameters best matching some sampled on the original edge curve.

See if you can use brep Vertices to find the correct untrimmed edge.

From each edge point, find the point on its
control polygon segment that is closest to the curve and move the
control point there.

If there is more then one control polygon segment between surface edge point and
original trim curve, slide the next point to half way 

The user can then MatchSrf to the curve for position. 

"""

def get_input():
    #    blnCrv = True
    #    blnNice = True
    #    blnLoft = False
    #    
    #    if sc.sticky.has_key("oldNice"):
    #        blnNice = sc.sticky["oldNice"]
    #    if sc.sticky.has_key("oldLoft"):
    #        blnLoft = sc.sticky["oldLoft"]
    #    if sc.sticky.has_key("oldCrv"):
    #        blnCrv = sc.sticky["oldCrv"]
        
    sc.doc.Views.Redraw()
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.EdgeFilter
    go.DisablePreSelect()
    
    go.SetCommandPrompt("Select surface edges")
    
    while True:

        #get_rc = go.GetMultiple(2, -1)
        get_rc = go.Get()

        if go.CommandResult() != Rhino.Commands.Result.Success:
            return go.CommandResult()
            
    #        if get_rc == Rhino.Input.GetResult.Option:
    #            blnNice = optToggleNice.CurrentValue
    #            sc.sticky["oldNice"] = blnNice
    #            blnLoft = optToggleLoft.CurrentValue
    #            sc.sticky["oldLoft"] = blnLoft
    #            blnCrv = optToggleCurve.CurrentValue
            #sc.sticky["oldCrv"] = blnCrv
            
            continue
        if get_rc==Rhino.Input.GetResult.Object:
            break
            
    objRef = go.Objects()[0] 

    return objRef
    
    
    
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
            
            
    return [uList,vList, uCount, vCount]


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
    
    for idx in NextB:
        ptsB.append[rs.ObjectGripLocation]
    
    for idx in range(len(BaseRow)):
        pt = rs.ObjectGripLocation(Id,BaseRow[idx])
        rc, parU, parV = srfB.ClosestPoint(pt)
        rc, plane = srfB.FrameAt(parU, parV)
        plane.Origin = pt
        rs.ObjectGripLocation(Id, Row1[idx],rs.PlaneClosestPoint(plane,rs.ObjectGripLocation(Id, Row1[idx])))
        
    for idx in range(len(LastRow)):
        pt = rs.ObjectGripLocation(Id,LastRow[idx])
        rc, parU, parV = srfA.ClosestPoint(pt)
        rc, plane = srfA.FrameAt(parU, parV)
        plane.Origin = pt
        rs.ObjectGripLocation(Id, PenRow[idx],rs.PlaneClosestPoint(plane,rs.ObjectGripLocation(Id, PenRow[idx])))
        
    if not gripOn:rs.EnableObjectGrips (Id, False)
    rs.EnableRedraw (True)
    

def TryUntrimmedMatch():
    """
    South = FirstU
    North = lastU
    West = firstV
    East = lastV
    """
    
    inputs = get_input()
    if not inputs: return
    if inputs == Rhino.Commands.Result.Cancel:return
    
    objRef = inputs

    y = objRef.Geometry()
    brep = y.Brep
    edges  = brep.Edges
    edgeCrvs = [edges[n].EdgeCurve for n in range(edges.Count)]
    idx = objRef.GeometryComponentIndex.Index
    trim = y.Brep.Trims[idx]
    isoX = trim.IsoStatus
    curve = y.EdgeCurve
    srf = brep.Faces[0].ToNurbsSurface()
    blnTrim = False
    
    

    
    #    i = 0
    #    for pt in ptsX:
    #        rs.AddTextDot(i, pt.Location)
    #        i = i + 1
    if not brep.IsSurface:
        #tempx = sc.doc.Objects.AddBrep(srfx.ToBrep)
        blnTrim = True
    
    b = a.Geometry()
    idxa = a.GeometryComponentIndex.Index
    brepa = b.Brep
    srfa = brepa.Faces[0].ToNurbsSurface()
    trima = brepa.Trims[idxa]
    isoA = trima.IsoStatus
    idxXlist = surface_UV_idx(srfx)
    idxAlist = surface_UV_idx(srfa)

    xIndices =[]
    aIndices= []
    allPoints = [aIndices,xIndices]
    isos = [isoX, isoA]
    
    ptsX = srfx.Points
    ptsA = srfa.Points
    countU, countV  = idxXlist[2:4]
    print isoX, isoA
    if isos[0] == Rhino.Geometry.IsoStatus.South:
        xIndices.append(idxXlist[0][0])
        xIndices.append (idxXlist[0][1])
        
    elif isos[0] == Rhino.Geometry.IsoStatus.North:
        print countU-1
        xIndices.append(idxXlist[0][countV-1])
        xIndices.append(idxXlist[0][countV-2])
        
    elif isos[0] == Rhino.Geometry.IsoStatus.West:
        
        xIndices.append(idxXlist[1][0])
        xIndices.append(idxXlist[1][1])
        
    else :
        xIndices.append(idxXlist[1][countU-1])
        xIndices.append(idxXlist[1][countU-2])
        

    countU, countV  = idxAlist[2:4]
    if isos[1] == Rhino.Geometry.IsoStatus.South:
        aIndices.append(idxAlist[0][0])
        aIndices.append (idxAlist[0][1])
        
    elif isos[1] == Rhino.Geometry.IsoStatus.North:
        
        aIndices.append(idxAlist[0][countV-1])
        aIndices.append(idxAlist[0][countV-2])
        
    elif isos[1] == Rhino.Geometry.IsoStatus.West:
        
        aIndices.append(idxAlist[1][0])
        aIndices.append(idxAlist[1][1])
        
    else :
        aIndices.append(idxAlist[1][countV-1])
        aIndices.append(idxAlist[1][countV-2])
        
    srfxPts = [n.Location for n in ptsX]
    srfaPts = [n.Location for n in ptsA]
    linesX = []
    linesA = []
    ptList = Rhino.Collections.Point3dList(srfaPts)
    for i in range(len(xIndices[0])):
        ptIdx = Rhino.Collections.Point3dList().ClosestIndexInList(ptList, srfxPts[xIndices [0][i]])
        print ptIdx
        pts = srfaPts[ptIdx], srfaPts[ptIdx+countV]
        rs.AddLine(pts[0], pts[1])
        linesX.append(Rhino.Geometry.Line(srfxPts[xIndices [0][i]], srfxPts[xIndices [1][i]]))
        #rs.AddLine(srfxPts[xIndices [0][i]], srfxPts[xIndices [1][i]])
    pass
    ptList = Rhino.Collections.Point3dList(srfxPts)
    for i in range(len(aIndices[0])):
        ptIdx = Rhino.Collections.Point3dList().ClosestIndexInList(ptList, srfaPts[aIndices [0][i]])
        linesA.append(Rhino.Geometry.Line(srfaPts[aIndices [0][i]], srfaPts[aIndices [1][i]]))
        pts = srfxPts[ptIdx], srfxPts[ptIdx+countV]
        rs.AddLine(pts[0], pts[1])
        #rs.AddLine(srfaPts[aIndices [0][i]], srfaPts[aIndices [1][i]])


    
    """
    PointArrayClosestpoint for each edne point with the set of opposite edge points. Find the index and 
    deal with the line from the located point to the point in the next row. LineCLosestPoint in each direction
    Average the points and stick both cv edge points at that location.
    """

    
TryUntrimmedMatch()