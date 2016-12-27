import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import System
import collections

def SetObjectDisplayModeRendered(objref):

    viewportId = sc.doc.Views.ActiveView.ActiveViewportID
    mode = Rhino.Display.DisplayModeDescription.GetDisplayModes()[2]
    attr = objref.Object().Attributes
    if attr.HasDisplayModeOverride(viewportId):
        print "Removing display mode override from object"
        attr.RemoveDisplayModeOverride(viewportId)

    attr.SetDisplayModeOverride(mode, viewportId)
    sc.doc.Objects.ModifyAttributes(objref, attr, False)
    sc.doc.Views.Redraw()
 

def recalculate_colors( distList ,meshRef, max, min):
    
    
    mesh = meshRef.Mesh()

    meshId = meshRef.ObjectId
    meshObj = sc.doc.Objects.Find(meshId)
    #x = meshObj.Geometry
    factor = .666667
    offset = 1 - factor
    norm = normalize_values(distList, factor, max, min)
     
    crntVC = meshObj.Geometry.VertexColors.Count
    if crntVC is not None: meshObj.Geometry.VertexColors.Clear()    
    
    #    crntVC = mesh.VertexColors.Count
    #    if crntVC is not None: mesh.VertexColors.Clear()    
    #    crntVC = mesh.VertexColors.Count

    for n in norm:
        meshObj.Geometry.VertexColors.Add(Rhino.Display.ColorHSL(((n)+offset), 1, .5).ToArgbColor())
    print sc.doc.Objects.Replace(meshId, meshObj.Geometry)
    sc.doc.Views.Redraw()
    
    
def calculate_colors(meshRef, brepId, max, min):
    
    brepObj = sc.doc.Objects.Find(brepId)
    meshId = meshRef.ObjectId
    mesh = meshRef.Mesh()
    meshObj = sc.doc.Objects.Find(meshId)
    
    vList = meshObj.Geometry.Vertices
    vcList1 = meshObj.Geometry.VertexColors
    pass

    idx = 0
    
    faceList = brepObj.Geometry.Faces
    for v in vList:
        rc, p1, idx, f1, f2, vecNorm  = brepObj.Geometry.ClosestPoint(v, 0.0)
        d = Rhino.Geometry.Point3d.DistanceTo(p1, v)
        vecTest = p1- Rhino.Geometry.Point3d(v)
        mPt = mesh.ClosestPoint(v, 0)
            
    distList = [Rhino.Geometry.Point3d.DistanceTo(Rhino.Geometry.Brep.ClosestPoint(brepObj.Geometry, v), v) for v in vList]
    
    distCopy = list(distList)
    
    #x = meshObj.Geometry
    factor = .666667
    offset = 1- factor
    norm = normalize_values(distList, factor, max, min)
     
    crntVC = meshObj.Geometry.VertexColors.Count
    if crntVC is not None: meshObj.Geometry.VertexColors.Clear()    
    
    #    crntVC = mesh.VertexColors.Count
    #    if crntVC is not None: mesh.VertexColors.Clear()    
    #    crntVC = mesh.VertexColors.Count

    pass
    for n in norm:
        #print 1-(1-n)
        meshObj.Geometry.VertexColors.Add(Rhino.Display.ColorHSL(((n)+offset), 1, .5).ToArgbColor())
        #testList.append([Rhino.Display.ColorHSL(n*.75, 1, .5).ToArgbColor().R, Rhino.Display.ColorHSL(n+offSet, 1, .5).ToArgbColor().G, Rhino.Display.ColorHSL(n*.75, 1, .5).ToArgbColor().B ])
        
    vcList1 = mesh.VertexColors

    #sc.doc.Objects.Replace(meshId, mesh)
    sc.doc.Objects.Replace(meshId, meshObj.Geometry)
    sc.doc.Views.Redraw()
    return distCopy
    
def normalize_values(numList, factor, maxVal, minVal):

    tempList = []
    
    
    for n in numList:
        if n > maxVal: 
            tempList.append( maxVal )
            #print "max"
        elif n < minVal:
             tempList.append( minVal )
             #print "min"
        else: tempList.append(n)
        
    x = [(n/maxVal)*factor for n in tempList]
    return x 
    pass
    
def test():
    #    meshId = rs.GetObject("Select a mesh.",32,preselect=True)
    #    if not meshId: return
    #    rs.ObjectColor(meshId, [255,0,0])
    brepId = rs.GetObject("Select a surface or polysurface.", 8+16 ,preselect=False)
    if not brepId: return
    brep = sc.doc.Objects.Find(brepId).Geometry
    
    minValue = .05
    maxValue = .1
    
    if sc.sticky.has_key("DeviationMin"):
        minValue = sc.sticky["DeviationMin"]
    
    if sc.sticky.has_key("DeviationMax"):
        maxValue = sc.sticky["DeviationMax"]
        
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Mesh
    go.SetCommandPrompt("Select mesh")
    go.Get()
    
    if go.CommandResult() !=  Rhino.Commands.Result.Success:
        return go.CommandResult()
        
    meshRef = go.Objects()[0]
    SetObjectDisplayModeRendered(meshRef)
    
    distList = calculate_colors(meshRef, brepId, maxValue, minValue)

    while True:
        
        if sc.sticky.has_key("DeviationMin"):
            minValue = sc.sticky["DeviationMin"]
    
        if sc.sticky.has_key("DeviationMax"):
            maxValue = sc.sticky["DeviationMax"]
        
        gp = Rhino.Input.Custom.GetPoint()
        
        opMax = Rhino.Input.Custom.OptionDouble(maxValue)
        opMin = Rhino.Input.Custom.OptionDouble(minValue)
        gp.AddOption("AutoRange")
        gp.SetCommandPrompt("Click to label distance.")
        gp.AddOptionDouble("MaxDeviation", opMax)
        gp.AddOptionDouble("MinDeviation", opMin)
        gp.Constrain(meshRef.Mesh(), False)
        get_rc = gp.Get()
        
        if gp.CommandResult()!=Rhino.Commands.Result.Success:
            return gp.CommandResult()
        
        elif get_rc==Rhino.Input.GetResult.Point:
            targ = gp.Point()
            distance = round(targ.DistanceTo(Rhino.Geometry.Brep.ClosestPoint(brep, targ)), 4)
            rs.AddTextDot(str(distance), targ)
            print "Distance = " + str(distance)
        elif get_rc == Rhino.Input.GetResult.Option:
            minValue = opMin.CurrentValue
            maxValue = opMax.CurrentValue
            sc.sticky["DeviationMin"] = minValue
            sc.sticky["DeviationMax"] = maxValue
            if gp.OptionIndex()==1:
                print "Autorange"
                maxValue = max(distList)
                minValue = min(distList)
                sc.sticky["DeviationMin"] = minValue
                sc.sticky["DeviationMax"] = maxValue
                #recalculate_colors(distList, meshRef, maxVal, min)
            recalculate_colors(distList, meshRef, maxValue, minValue)
    pass

if( __name__ == "__main__" ):
    test()