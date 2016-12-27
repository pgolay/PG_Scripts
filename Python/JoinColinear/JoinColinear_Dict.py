import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import math

def test():
    
    aPi = math.pi
    tol = sc.doc.ModelAbsoluteTolerance
    aTolD = rs.GetReal("Set angle tolerance", number = sc.doc.ModelAngleToleranceDegrees)
    if aTolD is None: return
    
    aTol = Rhino.RhinoMath.ToRadians(aTolD)
    
    #print "aTol = " + str(aTol)
    simplifyOp = Rhino.Geometry.CurveSimplifyOptions.All
    crvIds = rs.GetObjects("Select lines to process", 4, preselect=True)
    if crvIds is None: return
    lineList = []
    
    for Id in crvIds:
        lineList.append(sc.doc.Objects.Find(Id).Geometry)

    d1 = {Id:sc.doc.Objects.Find(Id).Geometry.PointAtStart for Id in crvIds}
    d2 = {Id:sc.doc.Objects.Find(Id).Geometry.PointAtEnd for Id in crvIds}
    dLines = {Id:sc.doc.Objects.Find(Id).Geometry for Id in crvIds}
    usedIds = []
    

    rs.EnableRedraw(False)
    
    while True:
        
        def process_temp(temp):

            
            if len(d1) < 1: return temp, False
            start = temp.PointAtStart
            end = temp.PointAtEnd
            dom = temp.Domain
            vecStart = temp.TangentAt(dom[0])
            vecEnd = temp.TangentAt(dom[1])
            
            for item in d1:
                if d1[item] == start:
                    vecLine = d1[item]-d2[item]
                    vecTemp = vecStart
                    vAng  = Rhino.Geometry.Vector3d.VectorAngle(vecLine,vecTemp)
                    if vAng < aTol or vAng > aPi-aTol:
                         temp = Rhino.Geometry.Curve.JoinCurves([temp,dLines[item]])[0]
                         return temp, True
                         
            for item in d2:
                if d2[item] == end:
                    vecLine = d1[item]-d2[item]
                    vecTemp = vecEnd
                    vAng  = Rhino.Geometry.Vector3d.VectorAngle(vecLine,vecTemp)
                    if vAng < aTol or vAng > aPi-aTol:
                         temp = Rhino.Geometry.Curve.JoinCurves([temp,dLines[item]])[0]
                         return temp, True
                         
            return temp, False
        
        
        Id = crvIds.pop()
        temp = dLines[Id]
        

        
        usedIds.append(Id)
        
                        


        blnContinue = True
        
        while blnContinue:
            temp, blnContinue = process_temp(temp)
        
        if not blnContinue:
            sc.doc.Objects.AddCurve(temp)
            #temp = lineList.pop()
    sc.doc.Objects.AddCurve(lineList[0])
    rs.DeleteObjects(usedIds)
    rs.EnableRedraw(True)

    
test()