import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
import itertools
 
def Test():
    tol= sc.doc.ModelAbsoluteTolerance
    pLineId = rs.GetObject("Select a polyline", 4, preselect=True)
    if pLineId is None: return
    
    pLineObj= sc.doc.Objects.Find(pLineId)
    
    oldBreak = 45
    if sc.sticky.has_key("OldBreak"):
        oldBreak = sc.sticky["OldBreak"]
    dAng = rs.GetReal("Set break angle", oldBreak)
    if dAng is None: return
    
    sc.sticky["OldBreak"] = dAng
    ang = Rhino.RhinoMath.ToRadians(dAng)
    
    rc, pLine = pLineObj.Geometry.TryGetPolyline()
    pts = [pt for pt in pLine]
    crntPLine = [pLine[0]]
    pList = []
    sFactor = 2 #Straightness ratio
    """
        Add the first point to the Pline then
        Start iterating with the second point. 
        Look ahead and behind. If angle, Add the current point only
        if not angle, add the current point to the end of the PlIne, add the pline to the list, and then
        start a new PlIne with the current point, move to the next point
    """
    vecNull = Rhino.Geometry.Vector3d.Unset
    vecs = [vecNull, vecNull]
    vList = []
    for i in range(1,len(pts)):
        
        if i == len(pts)-1:
            crntPLine.append(pts[i])
            pList.append(Rhino.Geometry.Polyline(Rhino.Geometry.Point3d.CullDuplicates(crntPLine, tol)))
            
            vList.append(vecs)
            continue
        
        v1 = pts[i-1] - pts[i]
        v2 = pts[i]- pts[i+1]
        lengthRatio = v2.Length/v1.Length
        vAng = Rhino.Geometry.Vector3d.VectorAngle(v1,v2) 
        
        if  vAng < ang and 1/lengthRatio > sFactor:# Straight before this point
            crntPLine.append(pts[i])
            pList.append(Rhino.Geometry.Polyline(Rhino.Geometry.Point3d.CullDuplicates(crntPLine, tol)))
            vList.append(vecs)
            crntPLine = [pts[i]]
            v1.Reverse()
            vecs[0] = v1
            continue
            
        elif vAng < ang and lengthRatio > sFactor:#Straight after this point
            crntPLine.append(pts[i])
            pList.append(Rhino.Geometry.Polyline(Rhino.Geometry.Point3d.CullDuplicates(crntPLine, tol)))
            v2.Reverse()
            vecs[1] = v2
            vList.append(vecs)
            vecs = [vecNull, vecNull]
            crntPLine = [pts[i]]
            
            continue
            
        if vAng > ang: #Hard corner at this point
           
            crntPLine.append(pts[i])
            pList.append(Rhino.Geometry.Polyline(Rhino.Geometry.Point3d.CullDuplicates(crntPLine, tol)))
            vList.append([vecNull, vecNull])
            crntPLine = [pts[i]]
            vecs = [vecNull, vecNull]
            continue
            
        else:#Smooth corner at this point
            crntPLine.append(pts[i])
            continue
            
    if len(crntPLine) >1:
         pList.append(Rhino.Geometry.Polyline(Rhino.Geometry.Point3d.CullDuplicates(crntPLine, tol)))
         vList.append(vecs)
         
    style = Rhino.Geometry.CurveKnotStyle.ChordSquareRoot
    
    crvList = []
    for i in range(len(pList)):
        if len(pList[i]) == 2:
            crvList.append(Rhino.Geometry.Line(pList[i][0], pList[i][1]).ToNurbsCurve())
        else:
            crvList.append( Rhino.Geometry.Curve.CreateInterpolatedCurve(pList[i],3, style, startTangent = vList[i][0], endTangent= vList[i][1] ))
        
    if len(crvList)== 0: return
    
    crvs = Rhino.Geometry.Curve.JoinCurves(crvList)
    newCrvs = []
    for crv in crvs:
        newCrvs.append((sc.doc.Objects.AddCurve(crv)))
        
    rs.MatchObjectAttributes(newCrvs, pLineId)
    rs.SelectObjects(newCrvs)
    sc.doc.Views.Redraw()
    

    pass
if __name__ == "__main__":
    Test()