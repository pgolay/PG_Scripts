import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc


def PolylineRegion():
    tol = sc.doc.ModelAbsoluteTolerance
    crvIds= rs.GetObjects(filter=4, preselect=True)
    
    if not crvIds:return
    
    #lineIds = rs.ExplodeCurves(crvIds)
    lines = []
    for Id in crvIds:
        crvGeo = sc.doc.Objects.Find(Id).Geometry
        if isinstance(crvGeo, Rhino.Geometry.LineCurve):
            lines.append(crvGeo)
        else:
            pieces = crvGeo.DuplicateSegments()
            for piece in pieces:
                lines.append(piece)
            
    testLine = lines.pop()
    firstLine = testLine
    pts = []
    lastRun = False
    
    while True:
        if lastRun:
            rc, t1, t2 = Rhino.Geometry.Intersect.Intersection.LineLine(testLine.Line, firstLine.Line)
            pt = testLine.Line.PointAt(t1)
            pts.insert(0,pt)
            pts.append(pt)
            break
            
        testPts = []

        for line in lines:
            testPts.append(line.Line.From)
            testPts.append(line.Line.To)

        idx1 = rs.PointArrayClosestPoint(testPts, testLine.Line.From)
        d1 = testLine.Line.From.DistanceTo(testPts[idx1])
        
        idx2 = rs.PointArrayClosestPoint(testPts, testLine.Line.To)
        d2 = testLine.Line.To.DistanceTo(testPts[idx2])

        if d1 <= d2:
            idx = idx1
        else:
            idx = idx2
        
        crvIdx = int(idx/2)
        
        targetLine = lines.pop(crvIdx)
        
        line1 = testLine.Line
        
        rc, t1, t2 = Rhino.Geometry.Intersect.Intersection.LineLine(line1, targetLine.Line)
        
        if rc:
            p3 = line1.PointAt(t1)
            pts.append(p3)
            testLine = targetLine
        if len(lines) == 0:
            lastRun=True
            
    pLine = Rhino.Geometry.Polyline(pts)
    if not pLine.IsClosed:
        pts.append(pts[0])
        pLine = Rhino.Geometry.Polyline(pts)
    if pLine is not None: pLineId = sc.doc.Objects.AddPolyline(pLine)
    if pLineId is not None:
        sc.doc.Objects.UnselectAll()
        sc.doc.Objects.Lock(pLineId, False)
        
        rs.HideObjects(crvIds)
    sc.doc.Views.Redraw()

    pass
    
if __name__ == "__main__":
    PolylineRegion()