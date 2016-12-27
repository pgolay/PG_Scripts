import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

def AutoChain():
    rs.Command("_SelChain _ChainContinuity=_Position _GapTolerance=2 _Pause _Enter")
    Ids = rs.SelectedObjects()
    return Ids

def PolylineRegion():
    tol = sc.doc.ModelAbsoluteTolerance
    #crvIds= rs.GetObjects(filter=4, preselect=True)
    blnAuto=False
    while True:
        
        while True:
            blnLock = False
            blnHide = False
            #blnAuto = False
            
            if sc.sticky.has_key("PLINELOCK"):
                blnLock = sc.sticky["PLINELOCK"]
            if sc.sticky.has_key("PLINEHIDE"):
                blnHide = sc.sticky["PLINEHIDE"]
            if sc.sticky.has_key("PLINEAUTO"):
                blnAuto = sc.sticky["PLINEAUTO"]
            
            if blnAuto:
                crvIds = AutoChain()
                break
            go = Rhino.Input.Custom.GetObject()
            go.SetCommandPrompt("Select lines and polylines")
            
            optLock = Rhino.Input.Custom.OptionToggle(blnLock,"No", "Yes")
            optHide = Rhino.Input.Custom.OptionToggle(blnHide,"No", "Yes")
            optAuto = Rhino.Input.Custom.OptionToggle(blnAuto,"No", "Yes")
            
            go.AddOptionToggle("LockOutput", optLock)
            go.AddOptionToggle("HideInput", optHide)
            go.AddOptionToggle("AutoChain", optAuto)
            
            get_rc = go.GetMultiple(2,0)
            
            if go.CommandResult()!=Rhino.Commands.Result.Success:
                return go.CommandResult()
               
            if get_rc==Rhino.Input.GetResult.Object:
                 crvIds = [go.Object(n).ObjectId for n in range(go.ObjectCount)]
                 break
                 
            elif get_rc==Rhino.Input.GetResult.Option:
                #print go.OptionIndex()
                blnLock = optLock.CurrentValue
                sc.sticky["PLINELOCK"]= blnLock
                blnHide = optHide.CurrentValue
                sc.sticky["PLINEHIDE"]= blnHide
                blnAuto = optAuto.CurrentValue
                #sc.sticky["PLINEAUTO"]= blnAuto

        if not crvIds: return
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