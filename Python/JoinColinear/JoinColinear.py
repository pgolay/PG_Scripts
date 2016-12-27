import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import math

def JoinColinear():
    
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

    rs.EnableRedraw(False)
    
    while len(lineList) > 1:
        
        def process_temp(temp):
            
            #bb = temp.GetBoundingBox()
            if len(lineList) < 1: return temp, False
            start = temp.PointAtStart
            end = temp.PointAtEnd
            dom = temp.Domain
            vecStart = temp.TangentAt(dom[0])
            vecEnd = temp.TangentAt(dom[1])
            
            for line in lineList:
                length = len(lineList)
                
                p1 = line.PointAtStart
                p2 = line.PointAtEnd
                vecLine = p2-p1
                
                dists = []
                dists.append( start.DistanceTo(p1))
                dists.append(start.DistanceTo(p2))
                dists.append(end.DistanceTo(p1))
                dists.append(end.DistanceTo(p2))
                
                contiguous = False
                
                for i in range(4):
                     if dists[i] <= tol:
                         contiguous = True 
                         if i < 2:
                             vecTemp = vecStart
                             break
                         else:
                             vecTemp = vecEnd
                             break
                             
                if contiguous:
                     vAng  = Rhino.Geometry.Vector3d.VectorAngle(vecLine,vecTemp)
                     if vAng < aTol or vAng > aPi-aTol:
                         temp = Rhino.Geometry.Curve.JoinCurves([temp,lineList.pop(lineList.index(line))])[0]
                         return temp, True
                         
            return temp, False
            
        temp = lineList.pop()
        blnContinue = True
        
        while blnContinue:
            temp, blnContinue = process_temp(temp)
        
        if not blnContinue:
            sc.doc.Objects.AddCurve(temp)
            #temp = lineList.pop()
    sc.doc.Objects.AddCurve(lineList[0])
    rs.DeleteObjects(crvIds)
    rs.EnableRedraw(True)

if __name__ == "__main__":
    JoinColinear()