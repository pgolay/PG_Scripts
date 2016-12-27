import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

def ProjectPtsOnce():
    
    pcId = rs.GetObject("Select point cloud to project",2, preselect=True)
    if not pcId : return
    
    targId = rs.GetObject("Select the target object.", 8+16)
    if not targId: return
    
    cloud = sc.doc.Objects.Find(pcId)
    apts = cloud.Geometry.GetPoints()
    targ = sc.doc.Objects.Find(targId).Geometry
    vecDir = rs.ViewCPlane()[3]
    tol= sc.doc.ModelAbsoluteTolerance


    #    for pt in apts:
    #        ray = Rhino.Geometry.Ray3d(pt, vecDir)
    #        Result = Rhino.Geometry.Intersect.Intersection.RayShoot(ray, [targ], 1)[0]
    #        if Result:
    #            newPts.append(Result)
    #   
    
    newPts = Rhino.Geometry.Intersect.Intersection.ProjectPointsToBreps([targ], apts, vecDir, tol)
    pass
            
    if len(newPts) > 0:
        rs.AddPoints(newPts)

    
    
    
ProjectPtsOnce()