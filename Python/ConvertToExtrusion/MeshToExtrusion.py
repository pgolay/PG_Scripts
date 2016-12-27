import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import math

def InterpolatePolyline(pLine):
   
    ratStraight = 4
    brkAng = 45
    blnDel = False
        
    tol= sc.doc.ModelAbsoluteTolerance
    allNew = []
    
    ang = Rhino.RhinoMath.ToRadians(brkAng)
    
    pts = [pt for pt in pLine]
    crntPLine = [pts[0]]
    pList = []
    sFactor = ratStraight #Straightness ratio

    vecNull = Rhino.Geometry.Vector3d.Unset
    vecs = [vecNull, vecNull]
    vList = []
    
    for i in range(1,len(pts)):
        
        if i == len(pts)-1:#take care of the last segment
            crntPLine.append(pts[i])
            pList.append(Rhino.Geometry.Point3d.CullDuplicates(crntPLine, tol))
            vList.append(vecs)
            continue
        
        #segment direction vectors
        v1 = pts[i-1] - pts[i]
        v2 = pts[i]- pts[i+1]

        lengthRatio = v2.Length/v1.Length
        
        v1.Unitize()
        v2.Unitize()

        vAng = Rhino.Geometry.Vector3d.VectorAngle(v1,v2) 
        if vAng == 0 or vAng == 1: continue
        if  vAng < ang and 1/lengthRatio > sFactor:# Straight line before this point
            crntPLine.append(pts[i])
            pList.append(Rhino.Geometry.Point3d.CullDuplicates(crntPLine, tol))
            vList.append(vecs)
            crntPLine = [pts[i]]
            v1.Reverse()
            vecs[0] = v1
            continue
            
        elif vAng < ang and lengthRatio > sFactor:#Straight line after this point
            crntPLine.append(pts[i])
            pList.append(Rhino.Geometry.Point3d.CullDuplicates(crntPLine, tol))
            v2.Reverse()
            vecs[1] = v2
            vList.append(vecs)
            vecs = [vecNull, vecNull]
            crntPLine = [pts[i]]
            continue
            
        if vAng > ang: #Hard corner at this point
           
            crntPLine.append(pts[i])
            pList.append(Rhino.Geometry.Point3d.CullDuplicates(crntPLine, tol))
            vList.append([vecNull, vecNull])
            crntPLine = [pts[i]]
            vecs = [vecNull, vecNull]
            continue
            
        else:#Smooth corner at this point
            crntPLine.append(pts[i])
            continue
            
    style = Rhino.Geometry.CurveKnotStyle.ChordSquareRoot
    crvList = []
    
    for i in range(len(pList)):
        #single closed curve-
        if len(pList) == 1 and pLine.IsClosed:
            temp = [pt for pt in pList[0]]
            temp.append(temp[0])
            pList[0] = temp
        #just a line
        if len(pList[i]) == 2:
            crvList.append(Rhino.Geometry.Line(pList[i][0], pList[i][1]).ToNurbsCurve())
        else:
            tempCrv = Rhino.Geometry.Curve.CreateInterpolatedCurve(pList[i],3, style, startTangent = vList[i][0], endTangent= vList[i][1] )
            crvList.append(tempCrv)
            #crvList.append(Rhino.Geometry.NurbsCurve.Fit(tempCrv, 3, .01,0) )
        
    if len(crvList)== 0: return
    
    crvs = Rhino.Geometry.Curve.JoinCurves(crvList)
    return crvs[0]

def FindOuterCurve(curves, plane):
    inside = Rhino.Geometry.RegionContainment.AInsideB
    outside = Rhino.Geometry.RegionContainment.BInsideA
    tol = sc.doc.ModelAbsoluteTolerance
    outer = curves[0]
    inner = []
    temp = [crv for crv in curves]
    
    while len(temp) > 0:
        test = temp.pop()
        for crv in temp:
            crvState = Rhino.Geometry.Curve.PlanarClosedCurveRelationship(test, crv,plane, tol)
            if  crvState == inside:
                outer = crv
                if not test in inner: inner.append(test)
            elif crvState == outside:
                outer = test
                if not crv in inner: inner.append(crv)
            else:
                if not crv in inner: inner.append(crv)
                if not test in inner: inner.append(test)

    result = [outer]
    result.extend(inner)
    return result
    
def MeshToExtrusion():
    tol = sc.doc.ModelAbsoluteTolerance

    #go.DisablePreSelect()
    
    while True:
        go = Rhino.Input.Custom.GetObject()
        go.GeometryFilter = Rhino.DocObjects.ObjectType.Mesh
        fitTol = tol
        oldDel = False
        retCurves = False
        if sc.sticky.has_key("OLDDELETEMESH"):
            oldDel = sc.sticky["OLDDELETEMESH"]
        if sc.sticky.has_key("OLDRETURNCRVS"):
            retCurves = sc.sticky["OLDRETURNCRVS"]
        if sc.sticky.has_key("PLINEFITTOL"):
            fitTol = sc.sticky["PLINEFITTOL"]
        
        go.SetCommandPrompt("Select an extrusion shaped mesh")
        
        opDelete = Rhino.Input.Custom.OptionToggle(oldDel,"No", "Yes")
        go.AddOptionToggle("DeleteInput", opDelete)
        
        opReturnCrvs = Rhino.Input.Custom.OptionToggle(retCurves,"No", "Yes")
        go.AddOptionToggle("ReturnCurves", opReturnCrvs)
        
        opTol = Rhino.Input.Custom.OptionDouble(fitTol)
        go.AddOptionDouble("FittingTolerance", opTol)
        
        go.AcceptNumber(True, False) 
        result = go.Get()
        
        if( go.CommandResult() != Rhino.Commands.Result.Success ):
            return
        if result == Rhino.Input.GetResult.Number:
            fitTol = go.Number()
            sc.sticky["PLINEFITTOL"] = fitTol
            continue
        if result == Rhino.Input.GetResult.Option:
            oldDel = opDelete.CurrentValue
            sc.sticky["OLDDELETEMESH"] = oldDel
            retCurves = opReturnCrvs.CurrentValue
            sc.sticky["OLDRETURNCRVS"] = retCurves
            fitTol = opTol.CurrentValue
            sc.sticky["PLINEFITTOL"] = fitTol
            continue
        if result == Rhino.Input.GetResult.Object:
            
            objref = go.Object(0)
            break
    meshId = objref.ObjectId
    obj = sc.doc.Objects.Find(meshId)
    mesh = objref.Mesh()

    pts = rs.GetPoints(True,False,"Set direction base point", "Set direction",2)
    if len(pts) !=2:return
    
    vecDir = pts[1]- pts[0] 
    
    bPlane = Rhino.Geometry.Plane(pts[0], vecDir)

    bb = rs.BoundingBox(meshId, bPlane)
    height = bb[0].DistanceTo(bb[4])
    
    plane1 = Rhino.Geometry.Plane(bb[0], bb[1], bb[3])
    vecDir = bb[4]-bb[0]
    tempPlane = Rhino.Geometry.Plane(bb[0], vecDir)
    
    bases = []
    
    #for each linrear edge returned with the maesh sides and caps
    #move the base pane to the mid of each edge and intersect
    # with the corresponding brep face. The resuly should be one curve
    #and most lilely a simple iso.
    
    tempPlane.Origin = bb[0] + (vecDir/2)
    intx = Rhino.Geometry.Intersect.Intersection.MeshPlane(mesh,tempPlane)
    if len(intx) > 0 :
        bases =[Rhino.Geometry.Curve.ProjectToPlane(crv.ToNurbsCurve(),plane1)for crv in intx]
            
    if len(bases) == 0:return
    
    baseCurves = Rhino.Geometry.Curve.JoinCurves(bases,tol, False)
    x = baseCurves[0].TryGetPolyline()
    for i in range(len(baseCurves)):
        baseCurves[i] = InterpolatePolyline(baseCurves[i].TryGetPolyline()[1])
    if retCurves: 
        for crv in baseCurves: sc.doc.Objects.AddCurve(crv)
    

    if len(baseCurves) > 1: 
        sortedCurves = FindOuterCurve(baseCurves, plane1)
    else:
        sortedCurves = [baseCurves[0]]
        
    rc,crvPlane = sortedCurves[0].TryGetPlane()
    
    xform = Rhino.Geometry.Transform.PlaneToPlane(crvPlane, Rhino.Geometry.Plane.WorldXY)
    
    if crvPlane.ZAxis.IsParallelTo(plane1.ZAxis)== -1: height = -height
    
    ex = Rhino.Geometry.Extrusion.Create(sortedCurves.pop(0), height, mesh.IsClosed)
    
    if len(sortedCurves) > 0:
        for crv in sortedCurves:
            crv.Transform(xform)
            ex.AddInnerProfile(crv)
    
    exId = sc.doc.Objects.AddExtrusion(ex)
    if exId is not None:
        sc.doc.Objects.Select(exId)
        rs.MatchObjectAttributes(exId, meshId)
        exObj = sc.doc.Objects.Find(exId)
        exObj.Attributes.WireDensity = -1
        exObj.CommitChanges()
        pass
        
        if oldDel: sc.doc.Objects.Delete(obj,True)
    sc.doc.Objects.UnselectAll()
    sc.doc.Objects.Select(exId)
    sc.doc.Views.Redraw()
    pass
    
if __name__ =="__main__":
    MeshToExtrusion()