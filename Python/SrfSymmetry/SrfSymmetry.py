import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino

def SrfPtSymmetry():
    
    while True:
        gripInfo = rs.GetObjectGrips("Select control points from one surface.", preselect=True)
        if gripInfo is None: return
        
        Id = gripInfo[0][0]
        
        for n in range (1, len(gripInfo)):
            if gripInfo[n][0] != Id:
                print "Control points from more than one object were selected."
                sc.doc.Objects.UnselectAll()
                sc.doc.Views.Redraw()
                continue
                
        if not rs.IsSurface(Id):
            print "Currently only surface points can be made symmetrical. Please select control points from one surface."
            sc.doc.Objects.UnselectAll()
            sc.doc.Views.Redraw()
            continue
        else: break
        
        
    pts = [gripInfo[n][2] for n in range (len(gripInfo))]  
    allPts = rs.SurfacePoints(Id)
    axis = rs.GetPoints(True, True, "Set symmetry axis base point", "Set symmetry axis direction", max_points = 2)
    if axis is None: return
    if len(axis)<2: return
    crntPlane = rs.ViewCPlane()
    plane  = Rhino.Geometry.Plane(axis[0], axis[0]-axis[1],crntPlane.ZAxis) 
    
    vecTest = pts[0] - plane.ClosestPoint(pts[0]) 
    
    for n in range(1,len(gripInfo)):
        if vecTest.IsParallelTo(pts[n] - plane.ClosestPoint(pts[n])) != 1: 
            print "All selected control points must be on the same side of the symmetry plane"
            return
            
    rs.EnableRedraw(False)
    for  n in range(len(gripInfo)):
        pt = plane.ClosestPoint(pts[n])
        vec = pts[n]- pt
        vec.Reverse()
        idx = rs.PointArrayClosestPoint(allPts,pt+vec) 
        rs.ObjectGripLocation(Id,idx, pt+vec)
        
    rs.EnableRedraw(True)
    
    
if __name__ == "__main__":
    SrfPtSymmetry()