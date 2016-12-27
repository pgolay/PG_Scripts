import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import math




def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/n # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/n # the population variance
    return pvar**0.5
    

def DetectArcs(pts):
    print len(pts)
    angs = []
    rats = []
    for i in range(len(pts)-1):
        v2 = pts[i-1] - pts[i] #points back along the sequence
        v1 = pts[i+1] - pts[i]#points along sequence
        v2.Reverse()#reverse the vector to point along the sequence, then measure the angle
        lengthRatio = v2.Length/v1.Length
        
        v1.Unitize()
        v2.Unitize()
    
        vAng = Rhino.Geometry.Vector3d.VectorAngle(v1,v2) 
        v2.Reverse()# flip the vector back again
        angs.append(vAng)
        rats.append(lengthRatio)
        
    rats.pop(0)
    angs.pop(0)
    
    a = mean(angs)
    b = mean(rats)
    sdAng = _ss(angs)#
    x = pstdev(angs)
    sdRats = _ss(rats)#
    z = pstdev(rats)
    style = Rhino.Geometry.CurveKnotStyle.ChordSquareRoot
    if sdAng < .01 and sdRats < .01:
        crv = Rhino.Geometry.Curve.CreateInterpolatedCurve(pts,3, style)
    plane = crv.TryGetPlane()[1]
    rc, arc  = Rhino.Geometry.Curve.TryGetArc(crv, plane, .01)
    
    #if rc: sc.doc.Objects.AddArc(x)
    
    
    #print rats
    pass


def MakeCurve(pts,vecs):
    tol = sc.doc.ModelAbsoluteTolerance
    if len(pts) > 3: DetectArcs(pts)
    style = Rhino.Geometry.CurveKnotStyle.ChordSquareRoot
    if len (pts) ==2:
        return Rhino.Geometry.LineCurve(pts[0],pts[1])
        
    crv = Rhino.Geometry.Curve.CreateInterpolatedCurve(pts,3, style, startTangent = vecs[0], endTangent = vecs[1]  )
    plane = crv.TryGetPlane()[1]
    rc, arc  = Rhino.Geometry.Curve.TryGetArc(crv, plane, tol)
    if rc: crv = arc
       
    return crv
    
    pass
    
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
    crvList = []
    style = Rhino.Geometry.CurveKnotStyle.ChordSquareRoot
    colinear = False
    for i in range(1,len(pts)):
        
        if i == len(pts)-1:#take care of the last segment
            crntPLine.append(pts[i])
            crvList.append(MakeCurve(crntPLine,vecs))
            continue
            
        #segment direction vectors
        if len(crntPLine) == 1:
            v2 = crntPLine[0] - pts[i] #point back along sequence
        else:
            v2 = pts[i-1] -pts[i] #points back along the sequence
            
        v1 = pts[i+1] - pts[i]#points along sequence
        v2.Reverse()#reverse the vector to point along the sequence, then measure the angle
        lengthRatio = v2.Length/v1.Length
        
        v1.Unitize()
        v2.Unitize()

        vAng = Rhino.Geometry.Vector3d.VectorAngle(v1,v2) 
        v2.Reverse()# flip the vector back again
        
        if vAng == 0 or vAng == 1:#colinear, skip this point
            colinear = True
            #sc.doc.Objects.AddPoint(pts[i])
            if len(crntPLine)>2:
                crvList.append(MakeCurve(crntPLine,vecs))
                vList.append(vecs)
                crntPLine = [pts[i-1]]
                crntPLine.append(pts[i])
                vecs[0] = v1
            continue 
            
        if colinear: 
        #Colinear previous to this point but this point is not- ends here
        #add the colinear segment
            crntPLine.append(pts[i])
            crvList.append(MakeCurve(crntPLine,[vecNull,vecNull]))
            crntPLine = [pts[i]]
            colinear = False
            continue
            
        if  vAng < ang and 1/lengthRatio > sFactor:# Straight line before this point
            crntPLine.append(pts[i])
            crvList.append(MakeCurve(crntPLine, vecs))
            crntPLine = [pts[i]]
            continue
            
        if vAng < ang and lengthRatio > sFactor:#Straight line after this point
            crntPLine.append(pts[i])
            crvList.append(MakeCurve(crntPLine, vecs))
            crntPLine = [pts[i]]
            continue
            
        if vAng > ang: #Hard corner at this point
            crntPLine.append(pts[i])
            crvList.append(MakeCurve(crntPLine, [vecNull, vecNull]))
            crntPLine = [pts[i]]
            continue
            
        else:#Smooth corner at this point
            crntPLine.append(pts[i])
            continue
    if len(crvList) == 0: return
    
    for i in range(len(crvList)):
        if Rhino.Geometry.Curve.IsArc(crvList[i].ToNurbsCurve()):

            crv = Rhino.Geometry.ArcCurve(crvList[i])
            crvList[i] = crv
            sc.doc.Objects.AddCurve(crv)
        else:
            sc.doc.Objects.AddCurve(crvList[i])
            
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