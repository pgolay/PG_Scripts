import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
"""
Start with the first curve in the group. Locate the nearest start or end point from all the other curves.
extend each with a line to a point where the tangents meet.
Join and simplify the result, remove the second curve from the list,
Repeat until only one curve is left - if it is open, extand the ends as before.
Co-linear curves might need special treatment (add a line between the ends or something, so detect those.

"""

def CloseCurve(crv):
    pass
def test():
    tol = sc.doc.ModelAbsoluteTolerance
    crvIds= rs.GetObjects(filter=4, preselect=True)
    
    if not crvIds:return
    plane = Rhino.Geometry.Plane.WorldXY
    count = 0
    #bb = Rhino.Geometry.BoundingBox()
    for Id in crvIds:
        
        tempBB = sc.doc.Objects.Find(Id).Geometry.GetBoundingBox(plane)
        
        if count > 0:
            bb.Union (tempBB)
            #sc.doc.Objects.AddPoints(bb.GetCorners())
        else:
            bb = tempBB
            #sc.doc.Objects.AddPoints(bb.GetCorners())
        count = count + 1
        
        
    bbPts = bb.GetCorners()
    
    dist = (bbPts[0]-bbPts[6]).Length
    lines = []
    crvs = []
    
    copyIds = []
    for Id in crvIds:
        copyIds.append(Id)
        crvObj = sc.doc.Objects.Find(Id)
        crvGeo = sc.doc.Objects.Find(Id).Geometry
        crvs.append(crvGeo)
        #pts.append([crvGeo.PointAtStart, crvGeo.PointAtEnd])
    n = 0
    while True:
        
        if len(crvIds) > 1:
            tempId = crvIds.pop()
        else: 
            sc.doc.Objects.AddCurve(tempCrv)
            tempCrv = CloseCurve(tempCrv)
            sc.doc.Objects.AddCurve(tempCrv)
            break
        if n == 0:
             tempCrv = crvs.pop()
             n = n + 1
             print n
             
        IsLine = False
        tempCrv = tempCrv.TryGetPolyline()[1]
        
        pts = []
        for crv in crvs:
            pts.append(crv.PointAtStart)
            pts.append(crv.PointAtEnd)
            
        start = False #nearest target end is the end point
        
        idx1 = rs.PointArrayClosestPoint(pts, tempCrv.Last)
        d1 = tempCrv.Last.DistanceTo(pts[idx1])
        idx2 = rs.PointArrayClosestPoint(pts, tempCrv.First)
        d2 = tempCrv.First.DistanceTo(pts[idx2])
        #sc.doc.Objects.AddPoint(tempCrv.Last)
        if d1 <= d2:
            idx = idx1
            print "d1"
        else:
            print "d2"
            idx = idx2
    #        if idx == idx1:
    #            sc.doc.Objects.AddLine(Rhino.Geometry.Line(pts[idx], tempCrv.Last))
    #        else:
    #            sc.doc.Objects.AddLine(Rhino.Geometry.Line(pts[idx], tempCrv.First))
            #tempCrv.Reverse()
        #sc.doc.Objects.AddPoint(tempCrv.Last)
        sc.doc.Views.Redraw()
        pass
        
        crvIdx = int(idx/2)
        targetCrv = crvs.pop(crvIdx)
        
        print "idx = " + str(idx)
        if (idx/2)%2 == 0:#index is even
            print "crvIdx = " + str(crvIdx)
            print "idx/2%2 = " + str((idx/2)%2)
            start = True #nearest target end is the startpoint
            
        #sc.doc.Objects.AddPoint(pts[idx])
        #targId = crvIds.pop(crvIdx)
        
        
        if start:#the direction to extend the target curve
            vecTarg = targetCrv.TangentAtStart
            vecTarg.Reverse()
        else:
            vecTarg = targetCrv.TangentAtEnd
            
        p1 = pts[idx]#the start or end point of the target
        #sc.doc.Objects.AddPoint(p1)
        p2 = p1+(vecTarg)
        
        if idx == idx1:#working from the end point of the current curve
            vecEx = tempCrv.ToNurbsCurve().TangentAtEnd
            line1 = Rhino.Geometry.Line(tempCrv.Last, tempCrv.Last + vecEx )
        else:#working from the start point of the current curve.
            vecEx = tempCrv.ToNurbsCurve().TangentAtStart
            vecEx.Reverse()
            line1 = Rhino.Geometry.Line(tempCrv.First, tempCrv.First + vecEx)

        line2 = Rhino.Geometry.Line(p1,p2)
        #sc.doc.Objects.AddLine(line1)
        #sc.doc.Objects.AddLine(line2)
        
        rc, t1, t2 = Rhino.Geometry.Intersect.Intersection.LineLine(line1, line2)
        
        if rc:
            p3 = line1.PointAt(t1)
            #sc.doc.Objects.AddPoint(p3)
            sc.doc.Views.Redraw()
            
            if IsLine:
                if idx == idx1:
                    tempCrv = Rhino.Geometry.Line(tempCrv.PointAtStart, p3)
                else:
                    tempCrv = Rhino.Geometry.Line(tempCrv.PointAtEnd, p3)
                if start:
                    targetCurve.SetPoint(0,p3)
                else:
                    targetCurve.SetPoint(targetCrv.PointCount-1,p3)
                #sc.doc.Objects.AddLine(tempCrv)
            else:
                print "start = " + str(start)
                tempCrv = Rhino.Geometry.PolylineCurve(tempCrv)
                if idx == idx1:
                    tempCrv.SetPoint(tempCrv.PointCount - 1, p3) 
                else:
                    tempCrv.SetPoint(0, p3) 
                #sc.doc.Objects.AddPoint(p3)
                
                if start:
                    if isinstance(targetCrv,Rhino.Geometry.LineCurve):
                        c = targetCrv.Line
                        targetCrv.Line = Rhino.Geometry.Line(c.From,p3)
                    else:
                        targetCrv.SetPoint(0,p3)
                else:
                    if isinstance(targetCrv,Rhino.Geometry.LineCurve):
                        c = targetCrv.Line
                        targetCrv.Line = Rhino.Geometry.Line(c.To,p3)
                    else:
                        targetCrv.SetPoint(targetCrv.PointCount-1,p3)
                        
                #sc.doc.Objects.Replace(targId, targetCrv)
                #sc.doc.Objects.Replace(tempId, tempCrv)
        tempCrv = Rhino.Geometry.Curve.JoinCurves([targetCrv, tempCrv.ToNurbsCurve()])[0]
            
    sc.doc.Views.Redraw()

    pass
        
    
    #        sc.doc.Objects.Delete(Id, True)
    #    result =Rhino.Geometry.Curve.JoinCurves(crvs, .5)
    #    for crv in result:
    #        sc.doc.Objects.AddCurve(crv)
    #        tempPts = crvGeo.ToNurbsCurve().Points
    #        for pt in tempPts:
    #            pts.append(pt.Location)
    #        tan1 = crvGeo.TangentAtStart
    #        tan1.Reverse()
    #        tan1 = tan1*dist
    #        tan2 =crvGeo.TangentAtEnd * dist
    #        lines.append( Rhino.Geometry.Line(crvGeo.PointAtStart, crvGeo.PointAtStart + tan1))
    #        lines.append( Rhino.Geometry.Line(crvGeo.PointAtEnd, crvGeo.PointAtEnd + tan2))
    #    
    #    x = Rhino.Geometry.Point3d.SortAndCullPointList(pts, .1)
    #    pline = Rhino.Geometry.Polyline(x)
    #    sc.doc.Objects.AddPolyline(pline)
    #    for line in lines:
    #        
    #        sc.doc.Objects.AddLine(line)
    
    
    pass
test()