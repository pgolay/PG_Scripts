import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs


"""
Select an edge point
Get the entire edge row.
Set a second point constrained to the line of the picked point to the next interior point.

Move each edge point along its control polygon the distance to the second point picked. 
Move the next row along the same lines but some propotion less - perhaps
corresponding to the points position in the move-direction row and the ratio of the length of \
each control polygon segment compared to the longest segment




Once the second points are moved, move the next row along towards the new 
position of the second row, only proportionally less, and so on moving back
Do not move the last row.
(Figure out how to dynamically draw at least the points or control polygon.)


"""
def get_grip():
    
    
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Grip
    
    
    go.SetCommandPrompt("Select a surface control point")
    
 
    get_rc = go.Get()

    if go.CommandResult() != Rhino.Commands.Result.Success:
        return go.CommandResult()
    if get_rc==Rhino.Input.GetResult.Object:
        objRef = go.Object(0)
        grip = objRef.Object()
        
        

    if grip is None:return
    sc.doc.Views.Redraw()
    return grip.OwnerId, grip.Index, grip.CurrentLocation
    
    
    
    
def get_second_point(line):
    
    
    gp = Rhino.Input.Custom.GetPoint()
    gp.Constrain (line)
    gp.EnableDrawLineFromPoint(True)
    gp.DrawLineFromPoint(line.PointAtStart)
    gp.Get()
    

def surface_UV_idx(srf):
  
    aCount = rs.SurfacePointCount(srf)
    uCount = aCount[0]
    vCount = aCount[1]
   
    uList = []
    vList = []
    
    for i in range(uCount):
        vList.append([])
    for i in range(vCount):
        uList.append([])

    for i in range (vCount):
        for j in range(uCount):
            uList[i].append (i + (j*(vCount)))
            
    for i in range (uCount):
        for j in range(vCount):
            vList[i].append (j + (i*(vCount)))
            
            
    return [uList,vList]


def expand_srf():
    
    aGrip = get_grip()
    if not aGrip: return
    if aGrip ==  Rhino.Commands.Result.Cancel: return
    #etc
    p1 = aGrip[2]
    Idx = aGrip[1]
    Id = aGrip[0]
    
    if not rs.IsSurface(Id):
        return
    rowInfo = surface_UV_idx(Id)
    uRows = rowInfo[0]
    vRows = rowInfo[1]
    
    maxU = len(uRows)
    maxV = len(vRows)
    
    for i in range(maxU-1):
        if Idx  in(uRows[i]):
            uRow = uRows[i]
            break
    if i == 0:
        pass
                
                
    if i == maxV-1:
        pass
        
        
    for j in range(maxV-1):
        if Idx  in(vRows[j]):
            vRow = vRows[j]
            break
    if j == 0:
        pass
                
                
    if j == maxU-1:
        pass
        
    
                
            
    
    """
    Look for the next grip and find its location
    ref_pt =
    """
    #dirLine = Rhino.Geometry.Line(p1, ref_pt)
    
    #move_to = get_second_point(line)


if __name__ == '__main__':
    expand_srf()