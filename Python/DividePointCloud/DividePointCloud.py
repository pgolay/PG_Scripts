import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs


def DividePoints():
    
    file  = rs.OpenFileName()
    
    if not file:return

    pts = []
    with open(file, "r") as f:
        
        max = [None, None, None]
        min = [None, None, None]
        
        for line in f:
                
            pt = rs.Str2Pt(line)
            pts.append(pt)
            for i in range(3): 
                if max[i] is None or max[i] < pt[i]: max[i] = pt[i]
                if min[i] is None or min[i] > pt[i]: min[i] = pt[i]

    max = Rhino.Geometry.Point3d(max[0], max[1], max[2])
    min = Rhino.Geometry.Point3d(min[0], min[1], min[2])
    bb = Rhino.Geometry.BoundingBox(min, max)
    
    def bb_divide(bb, x_div, y_div, z_div):
        corners = bb.GetCorners()
        vecX = (corners[1]-corners[0])/(x_div)
        vecY = (corners[3]-corners[0])/(y_div)
        vecZ = (corners[4]-corners[0])/(z_div)
        vecDiag = vecX + vecY + vecZ
        
        pt = corners[0]
        boxes = []
        for i in range (x_div+1):
            for j in range(y_div+1):
                for k in range(z_div+1):
                    pt = corners[0] + vecX*i + vecY*j + vecZ*k
                    if bb.Contains(pt + vecDiag):
                        boxes.append(Rhino.Geometry.BoundingBox(pt, pt+vecDiag))
        return boxes
        
    bbs = bb_divide(bb, 2,2,3)
    
    clouds = [Rhino.Geometry.PointCloud() for b in bbs]
    for i in range(len(bbs)):
        #rs.AddPoints(bbs[i].GetCorners())
        for pt in pts:
            if bbs[i].Contains(pt):
               clouds[i].Add(pt) 
               
               
    rs.EnableRedraw(False)
    n = 1
    
    for cloud in clouds:
        
        tempId = sc.doc.Objects.AddPointCloud(cloud)
        
        if tempId:
            layer = "Cloud " + str(n)
            if not rs.IsLayer(layer):  layer = rs.AddLayer("Cloud " + str(n))
            rs.ObjectLayer(tempId, layer)
            if n > 1: rs.LayerVisible(layer, False)
            n = n + 1
        
    sc.doc.Views.Redraw()
    pass
    
if __name__=="__main__":
    DividePoints()