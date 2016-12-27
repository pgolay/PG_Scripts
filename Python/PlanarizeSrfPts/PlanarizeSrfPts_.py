import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

def test():
    
    
    aGrip = rs.GetObjectGrip("Select a control point", False,True)
    
    if not aGrip: return
    
    Id = aGrip[0]
    Idx = aGrip[1]
    dir = 1
    if  rs.IsSurface(Id):
        Rows = Surface_UV_idx(Id)[dir]
        Max = len(Rows)
        
        for i in range(Max):
            if Idx  in(Rows[i]):
                rowIdx = i
                Row = Rows[i]
                if rowIdx<>0:
                    prevRow = Rows[i-1]
                if rowIdx < Max-1:
                    nextRow = Rows[i+1]
                break
                

            
        apts = []
        n = 0
        while n < 5:

            for idx in Rows[rowIdx]:
                apts.append(rs.ObjectGripLocation(Id,idx))
                
            Plane = rs.PlaneFitFromPoints(apts)
            for idx in range(1, Max-1):
                pts = []
        #            linePrev = Rhino.Geometry.Line(rs.ObjectGripLocation(Id,prevRow[idx]),aPts[idx])
                if nextRow:
                    pts.append( rs.LinePlaneIntersection([rs.ObjectGripLocation(Id,nextRow[idx]),apts[idx]], Plane) )
                    
                if prevRow:
                    pts.append( rs.LinePlaneIntersection([rs.ObjectGripLocation(Id,prevRow[idx]),apts[idx]], Plane) )
                
                if not pts[0]: 
                    targ = pts[1]
                elif not pts[1]: 
                    targ = pts[0]
                else: targ = pts[rs.PointArrayClosestPoint(pts, apts[idx])]
                
                rs.ObjectGripLocation(Id,Row[idx], targ)
                
                n = n + 1
                


def Surface_UV_idx(srf):
  
    aCount = rs.SurfacePointCount(srf)
    uCount = aCount[0]
    vCount = aCount[1]
   
    uList = []
    vList = []
    
    for U in range(uCount):
        uList.append([])
    for V in range(vCount):
        vList.append([])

    for i in range (uCount):
        for j in range(vCount):
            uList[i].append (i + (j*(vCount-1)))
            
    for i in range (vCount):
        for j in range(uCount):
            vList[i].append (j + (i*(uCount)))
    return [uList,vList]

    x = 2
    
    
test()