import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
 
 
 def InterpPoints(pts):
     
     
     
     return markers, curves
 
def InterpolatePolyline():
    
    while True:
        ratStraight = 4
        brkAng = 45
        blnDel = False
        
        if sc.sticky.has_key("DeleteInputPLine"):
            blnDel = sc.sticky[ "DeleteInputPLine" ]
        if sc.sticky.has_key("PlineBreakAngle"):
            brkAng = sc.sticky["PlineBreakAngle"]
        if sc.sticky.has_key("PlineStraightRatio"):
            ratStraight = sc.sticky["PlineStraightRatio"]
            
        go = Rhino.Input.Custom.GetObject()
        go.AcceptNumber(True, False)
        go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
        opDblStraight = Rhino.Input.Custom.OptionDouble(ratStraight)
        go.AddOptionDouble("StraightnessRatio",opDblStraight)
        opDblBreak = Rhino.Input.Custom.OptionDouble(brkAng)
        go.AddOptionDouble("BreakAngle",opDblBreak)
        opBlnDel = Rhino.Input.Custom.OptionToggle(blnDel, "No", "Yes")
        go.AddOptionToggle("DeleteInput",opBlnDel )
        
        result = go.GetMultiple(1,0)
        
        if( go.CommandResult() != Rhino.Commands.Result.Success ):
            return
            
        if result == Rhino.Input.GetResult.Object:
            ids = [go.Object(i).ObjectId for i in range(go.ObjectCount)]
            
        elif result == Rhino.Input.GetResult.Option:
            brkAng = opDblBreak.CurrentValue
            sc.sticky["PlineBreakAngle"] = brkAng
            ratStraight = opDblStraight.CurrentValue
            sc.sticky["PlineStraightRatio"] = ratStraight
            blnDel = opBlnDel.CurrentValue
            sc.sticky["DeleteInputPLine"] = blnDel
            continue
        elif result == Rhino.Input.GetResult.Number:
            brkAng = go.Number()
            sc.sticky["PlineBreakAngle"] = brkAng
            continue
        break
        
    tol= sc.doc.ModelAbsoluteTolerance
    allNew = []
    
    sc.doc.Views.RedrawEnabled = False
    for pLineId in ids:
        
        pLineObj= sc.doc.Objects.Find(pLineId)
        if type(pLineObj.Geometry) != Rhino.Geometry.PolylineCurve:continue
        
        ang = Rhino.RhinoMath.ToRadians(brkAng)
        
        rc, pLine = pLineObj.Geometry.TryGetPolyline()
        
        pts = [pt for pt in pLine]
        
        result = InterpPoints(pts)
        
        
        crntPLine = [pts[0]]
        pList = []
        sFactor = ratStraight #Straightness ratio
        """
            Add the first point to the Pline then
            Start iterating with the second point. 
            Look ahead and behind. If angle is OK (smooth), add the current point only
            if the angle is hard, add the current point to the end of the current set,
            add the set to the list, and then
            start a new set, still with the current point, move to the next point.
            
        """
        vecNull = Rhino.Geometry.Vector3d.Unset
        vecs = [vecNull, vecNull]
        vList = []#list of vector pairs for setting tangents on the interp curves if needed
        
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
            if len(pList) == 1 and rs.IsCurveClosed(pLineId):
                temp = [pt for pt in pList[0]]
                temp.append(temp[0])
                pList[0] = temp
            #just a line
            if len(pList[i]) == 2:
                crvList.append(Rhino.Geometry.Line(pList[i][0], pList[i][1]).ToNurbsCurve())
            else:
                crvList.append( Rhino.Geometry.Curve.CreateInterpolatedCurve(pList[i],3, style, startTangent = vList[i][0], endTangent= vList[i][1] ))
            
        if len(crvList)== 0: continueg 
        
        crvs = Rhino.Geometry.Curve.JoinCurves(crvList)
        newCrvs = []
        for crv in crvs:
            newCrvs.append((sc.doc.Objects.AddCurve(crv)))
            
        rs.MatchObjectAttributes(newCrvs, pLineId)
        if blnDel: sc.doc.Objects.Delete(pLineId,True)
        allNew.extend(newCrvs)
        
    sc.doc.Objects.UnselectAll()
    if not blnDel:
        for item in allNew:
            rs.RemoveObjectFromAllGroups(item)
    sc.doc.Views.RedrawEnabled = True
    sc.doc.Views.Redraw()
    rs.FlashObject(allNew)
    rs.SelectObjects(allNew)
    sc.doc.Views.Redraw()


if __name__ == "__main__":
    InterpolatePolyline()