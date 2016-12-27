import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs


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


def get_input():
    
    #Defaults
    oldDir = False

    #Stored values is any

    if sc.sticky.has_key("DeeGree_Dir"):
        oldDir  = sc.sticky["DeeGree_Dir"]

    #Reset defaults
    dir = oldDir
 
    
    sc.doc.Views.Redraw()
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Surface
    
 #set up the options
    optToggleDir = Rhino.Input.Custom.OptionToggle(oldDir, "U","V")


 #add the options

    go.AddOptionToggle("Direction",optToggleDir)

    
    go.SetCommandPrompt("Select a surface")
    
    while True:
        get_rc = go.Get()

        if go.CommandResult() != Rhino.Commands.Result.Success:
            return go.CommandResult()
        if get_rc==Rhino.Input.GetResult.Object:
            objRef = go.Object(0)
            grip = objRef.Object()
            break
        elif get_rc==Rhino.Input.GetResult.Option:
            #print go.Option.CurrentListOptionIndex
            dir = optToggleDir.CurrentValue
            sc.sticky["DeeGree_Dir"] = dir

          
            continue
    return objRef, dir

def DeeGree():
    
    aInput  = get_input()
    if not aInput: return
    if aInput ==  Rhino.Commands.Result.Cancel: return
    objRef = aInput[0]
    dir = aInput[1]
    dir2 = abs(dir-1)
    srf = objRef.Geometry().Surfaces[0]
    Id = objRef.ObjectId
    
    degU = srf.Degree(0)
    degV = srf.Degree(1)
    deg = srf.Degree(dir)
    gripOn = rs.ObjectGripsOn(Id)

    rs.EnableRedraw (False)
    rs.EnableObjectGrips(Id, True)

    if deg % 2 == 1: 
        print "Nope, not an even degree"
        return

    uvList  =  surface_UV_idx(srf)
    
    dirList = uvList[dir]
    dir2List = uvList[dir2]
   
    if len(dir2List) != deg + 1:
        print "Nope, not single span"
        return
        
    x = int((deg+1)/2)
    Row  = dir2List[int((deg+1)/2)]


    apt = []
    for idx in Row:
        apt.append(rs.ObjectGripLocation(Id, idx))

    sDeg =  ("Enter " + str(deg+ 2) + " Enter")
    if dir == 0: sDeg = ( " " + str(deg+ 2) + " Enter Enter")
    rs.EnableObjectGrips(Id, False)
    rs.UnselectAllObjects()
    rs.SelectObject(Id)
    rs.Command ("ChangeDegree" + sDeg)
    rs.EnableObjectGrips (Id, True)
    
    brep = sc.doc.Objects.Find(Id)
    srf =brep.Geometry.Surfaces[0]
    uvList  =  surface_UV_idx(srf)
    
    dirList = uvList[dir]
    dir2List = uvList[dir2]
    Row  = dir2List[int((deg+3)/2)]
    
    n = 0
    for idx in Row:
        rs.ObjectGripLocation(Id, idx, apt[n])
        n = n + 1
    if not gripOn:rs.EnableObjectGrips (Id, False)
    rs.EnableRedraw (True)
    
    
if __name__ == '__main__':
    DeeGree()