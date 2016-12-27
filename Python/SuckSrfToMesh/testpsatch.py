import rhinoscriptsyntax as rs

pts = rs.GetPoints()
x = rs.PointArrayBoundingBox(pts)
rs.AddPoints(x)
pass

def test():
    #make a few points then PlaneThroughtPt to test with
    x = rs.GetObject(filter=8)
    y = rs.GetObjects(filter = 1)
    
    rs.AddPatch( y, x)
    
test()

