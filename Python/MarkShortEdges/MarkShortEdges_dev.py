import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import math


def Test():
    tol = sc.doc.ModelAbsoluteTolerance
    brepId = rs.GetObject( filter = 8 + 16, preselect=True)
    if brepId is None: return
    
    brep = sc.doc.Objects.Find(brepId).Geometry
    edges = brep.Edges
    
    count = 0
    for edge in edges:

        if edge.GetLength() <= tol:
            if count == 0:
                grp = rs.AddGroup()
            temp = rs.AddTextDot("!!!", edge.PointAtStart)
            rs.AddObjectsToGroup(temp, grp)
            count = count + 1
            
    print str(count) + " edges found at or below tolerance."
    
if __name__ == "__main__":
    Test()