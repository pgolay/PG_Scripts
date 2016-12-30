import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs


def DividePointsSlow():
    
    file  = rs.OpenFileName()
    
    if not file:return
    
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
    

    def GetInput():
        while True:
            x_div = 2
            y_div = 2
            z_div = 2
            if sc.sticky.has_key("BOXDIVS"):
                temp = sc.sticky["BOXDIVS"].split(",")
                x_div = int(temp[0])
                y_div = int(temp[1])
                z_div = int(temp[2])
            go = Rhino.Input.Custom.GetOption()
            opX = Rhino.Input.Custom.OptionInteger(x_div,True, 1)
            opY = Rhino.Input.Custom.OptionInteger(y_div,True, 1)
            opZ = Rhino.Input.Custom.OptionInteger(z_div,True, 1)
            go.AddOptionInteger("XBoxes", opX)
            go.AddOptionInteger("YBoxes", opY)
            go.AddOptionInteger("ZBoxes", opZ)
            go.AcceptNothing(True)
            go.SetCommandPrompt("Set bounding box divisions")
            
            ret = go.Get()
            
            if  go.CommandResult() == Rhino.Commands.Result.Cancel:
                return
                
            if  go.CommandResult() == Rhino.Commands.Result.Nothing:
                print "Nothing"
                x_div = opX.CurrentValue
                y_div = opY.CurrentValue
                z_div = opZ.CurrentValue
                return x_div,y_div,z_div
                
            if ret == Rhino.Input.GetResult.Option:
                x_div = opX.CurrentValue
                y_div = opY.CurrentValue
                z_div = opZ.CurrentValue
                sc.sticky["BOXDIVS"] = str(x_div) + "," + str(y_div) + ","+ str(z_div)
                continue
                
            else: return x_div,y_div,z_div

    
    x_div,y_div,z_div = GetInput()
    
    max = [None, None, None]
    min = [None, None, None]
    
    
    # Get the overall bounding box<<<<<<<<<<<<<<<<<
    f = open(file, "r")
    line = f.readline().strip()
    while line != "":
        pt = rs.Str2Pt(line)
        for i in range(3): 
            if max[i] is None or max[i] < pt[i]: max[i] = pt[i]
            if min[i] is None or min[i] > pt[i]: min[i] = pt[i]
        line = f.readline().strip()
        
    f.close()
    
    max = Rhino.Geometry.Point3d(max[0], max[1], max[2])
    min = Rhino.Geometry.Point3d(min[0], min[1], min[2])
    bb = Rhino.Geometry.BoundingBox(min, max)
    
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    
    bbs = bb_divide(bb, x_div,y_div,z_div)
    
    clouds = [Rhino.Geometry.PointCloud() for b in bbs]
    
    # read the points into the sub boxes<<<<<<<<<<<<<<
    f = open(file, "r")
    line = f.readline().strip()
    while line != "":
        pt = rs.Str2Pt(line)
        for i in range(len(bbs)):
            if bbs[i].Contains(pt):
                clouds[i].Add(pt)
                break
        line = f.readline().strip()

    f.close()
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
               
               
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
    DividePointsSlow()