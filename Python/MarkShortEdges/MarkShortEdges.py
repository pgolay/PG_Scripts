import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import math

def SrfMidParam(srf):
    domU = srf.Domain(0)
    domV = srf.Domain(1)
    return [domU.T0 + ((domU.T1-domU.T0)/2) , domV.T0 + ((domV.T1-domV.T0)/2)]
    
def CrvMidParam(crv):
    dom = crv.Domain
    return dom.T0 + ((dom.T1-dom.T0)/2) 
    
def Test():
    tol = pow(sc.doc.ModelAbsoluteTolerance,2)
    brepId = rs.GetObject( filter = 8 + 16, preselect=True)
    if brepId is None: return
    
    brep = sc.doc.Objects.Find(brepId).Geometry
    faces = brep.Faces

    edges = brep.Edges
    
    count = 0
    for face in faces:
        sizeRC = False
        x = Rhino.Geometry.AreaMassProperties.Compute(face)
        #rs.AddPoint(x.Centroid)
        print x.Area, face.FaceIndex
        if x.Area < tol:
            if count ==  0:
                grp=rs.AddGroup()
            pt = x.Centroid
            bb = face.GetBoundingBox(True)
            pt = bb.Center
            temp = rs.AddTextDot("!!!", pt)
            rs.AddObjectsToGroup(temp, grp)
            count = count + 1
            
    print str(count) + " very small area faces found."
    
if __name__ == "__main__":
    Test()