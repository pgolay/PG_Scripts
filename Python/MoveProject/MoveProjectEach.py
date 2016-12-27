import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

def AveragePoint3d(aPts):
    P = len(aPts)
    X = Y = Z = 0
    L = len(aPts)
    for i in range(len(aPts)):
        X = X + aPts[i].X
        Y = Y + aPts[i].Y
        Z = Z + aPts[i].Z
        
    return Rhino.Geometry.Point3d(X/L, Y/L, Z/L)
    
def MoveProjectEach():
    
    objIds = rs.GetObjects("Select objects to project.", preselect=True)
    if not objIds: return
    
    targId = rs.GetObject("Select target object.", filter = 8+16+32+4096)
    if not targId: return
    
    blnMesh = False
    if rs.IsMesh(targId): blnMesh = True
    crnt_plane = rs.ViewCPlane()
    vecDir = crnt_plane[3]
    
    for Id in objIds:
        if rs.IsBlockInstance(Id):
            
            intTarg = 0
            pt = rs.BlockInstanceInsertPoint(Id)
            if blnMesh:
                projPts = rs.ProjectPointToMesh(pt,targId, vecDir)
            else:
                projPts = rs.ProjectPointToSurface(pt, targId,vecDir)
                
            if projPts:
                if len(projPts) > 1:
                    intTarg = rs.PointArrayClosestPoint(projPts,pt) 
                
            if projPts:
                dist  = pt.DistanceTo(projPts[intTarg])
                vecDir = projPts[intTarg]- pt
                rs.MoveObject(Id, vecDir)
            
        else:
            bb = rs.BoundingBox(Id,crnt_plane,in_world_coords=True)
            cTop = AveragePoint3d([bb[4],bb[6]])
            cBot = AveragePoint3d([bb[0],bb[2]])
            
            if blnMesh:
                pp1 = rs.ProjectPointToMesh(cTop, targId, crnt_plane[3])
               
            else:
                pp1 = rs.ProjectPointToSurface(cTop, targId, crnt_plane[3])
                
            if len(pp1)>0:
                p1 = pp1[rs.PointArrayClosestPoint(pp1,cTop)]
            
#            if pp1:
                if p1.DistanceTo(cTop) < p1.DistanceTo(cBot):
                    pts = [bb[4],bb[5],bb[6],bb[7]]
                    vecDir = rs.VectorUnitize(p1-cTop)
                else:
                    pts = [bb[0],bb[1],bb[2],bb[3]]
                    vecDir = rs.VectorUnitize(p1-cTop)
                dist = 0
                for pt in pts:
                    
                    if blnMesh:
                        projPts = rs.ProjectPointToMesh(pt,targId, vecDir)
                    else:
                        projPts = rs.ProjectPointToSurface(pt, targId,vecDir)
                    if len(projPts) > 1:
                        intTarg = rs.PointArrayClosestPoint(projPts,pt) 
                        
                    else: 
                        intTarg = 0
                    
                    temp =  pt.DistanceTo(projPts[intTarg])
                    if temp > dist:
                       dist = temp
        
                rs.MoveObject(Id, rs.VectorScale(vecDir, dist))
    
MoveProjectEach()
    
    