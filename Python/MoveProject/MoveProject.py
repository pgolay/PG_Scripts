import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs


def MoveProject():
    
    objIds = rs.GetObjects("Select objects to project.", preselect=True)
    if not objIds: return
    
    basePt = rs.GetPoint("Point to move from.")
    if not basePt: return
    
    targId = rs.GetObject("Select target object.", filter = 8+16+32+4096)
    if not targId: return
    
    if rs.IsMesh(targId):
        X = rs.ProjectPointToMesh(basePt,targId, rs.ViewCPlane()[3])
    else:
        X = rs.ProjectPointToSurface(basePt, targId , rs.ViewCPlane()[3])
        
    if len(X) > 1:
        intTarg = rs.PointArrayClosestPoint(X,basePt)
    else:
        intTarg = 0
        
    targPt = X[intTarg]

    rs.MoveObjects(objIds, targPt-basePt)
    
MoveProject()
    
    