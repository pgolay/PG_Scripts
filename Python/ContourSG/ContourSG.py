import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino


def ContourSG():
    
    """
    
    GetObject
        option for axis (cplaneXYZ):option list
        option for # of slices: get integer
        option for start and for end points (get points)
    
    """
    def get_inputs():
        rs.UnselectAllObjects()
        while True:
            crntAxis = 0
            
            if sc.sticky.has_key("ContourCrntAxis"):
                crntAxis = sc.sticky["ContourCrntAxis"]
            else: sc.sticky["ContourCrntAxis"] = crntAxis
            
            intSlice = 100
            if sc.sticky.has_key("ContourSlices"):
                intSlice = sc.sticky["ContourSlices"]
            else: sc.sticky["ContourSlices"] = intSlice
            
            blnCrvs = False
            if sc.sticky.has_key("ContourAddCurves"):
                blnCrvs = sc.sticky["ContourAddCurves"]
            
            go = Rhino.Input.Custom.GetObject()
            go.GeometryFilter = Rhino.DocObjects.ObjectType.Surface|Rhino.DocObjects.ObjectType.PolysrfFilter            
            
            optCrvs = Rhino.Input.Custom.OptionToggle(blnCrvs, "No", "Yes")
            go.AddOptionToggle("AddCurves", optCrvs)
            
            axesList = "X","Y", "Z"
            optListAxes = go.AddOptionList("CPlaneAxis", axesList, crntAxis)
            
            optInteger = Rhino.Input.Custom.OptionInteger(intSlice)
            optNum = go.AddOptionInteger("Slices",optInteger)
            
            rc = go.Get()
            if go.CommandResult()!=Rhino.Commands.Result.Success:
                return go.CommandResult()
                
            elif rc == Rhino.Input.GetResult.Option:
                sc.sticky["ContourSlices"] = optInteger.CurrentValue
                sc.sticky ["ContourAddCurves"] = optCrvs.CurrentValue
                if go.OptionIndex() == optListAxes:
                    sc.sticky["ContourCrntAxis"] = go.Option().CurrentListOptionIndex
                continue
            elif rc == Rhino.Input.GetResult.Object:
                sc.sticky["ContourSlices"] = optInteger.CurrentValue
                objRef =  go.Object(0)
                break
            
        pts = []
        plane = rs.ViewCPlane()
        
        axis = sc.sticky["ContourCrntAxis"]
        
        if axis == 0:
            vecDir = plane.XAxis
        elif axis == 1:
            vecDir = plane.YAxis
        else: vecDir = plane.ZAxis
        
        for i in range(2):
            gp = Rhino.Input.Custom.GetPoint()
        
            intSlice = 100
            if sc.sticky.has_key("ContourSlices"):
                intSlice = sc.sticky["ContourSlices"]
            
            if i == 0:
                gp.SetCommandPrompt("Set start point")
            else:
                gp.SetCommandPrompt("Set end point")
                
            if i == 1:
                gp.Constrain(Rhino.Geometry.Line(pts[0], pts[0]+vecDir))
                gp.DrawLineFromPoint(pts[0], True)
            optBB= gp.AddOption("BoundingBox")
            gp.Get()
            if gp.CommandResult()!=Rhino.Commands.Result.Success:
                return go.CommandResult()
                
            if Rhino.Input.GetResult.Option:
                if gp.OptionIndex() == optBB:
                    bb = objRef.Object().BrepGeometry.GetBoundingBox(plane).GetCorners()
                    crntAxis = sc.sticky["ContourCrntAxis"]
                    if crntAxis == 0:
                        pts = [bb[0], bb[1]]
                    elif crntAxis == 1:
                        pts = [bb[0], bb[3]]
                    else:
                        pts = [bb[0], bb[4]]
                    return pts, objRef
            elif Rhino.Input.GetResult.Point:
                pts.append (gp.Point())
                
            sc.sticky["ContourSlices"] = optInteger.CurrentValue
            if i == 1: return pts, objRef

    
    input = get_inputs()
    
    if input == Rhino.Commands.Result.Cancel: return
    #if len(input)!= 2: return
    pts = input[0]
    blnCrvs = sc.sticky["ContourAddCurves"]
    intDiv = sc.sticky["ContourSlices"]
    line = Rhino.Geometry.LineCurve(pts[0], pts[1])
    divPts = [line.PointAt(par) for par in line.DivideByCount(intDiv,True)]
    axis = sc.sticky["ContourCrntAxis"]
    brep = input[1].Brep()
   
    vPlane = rs.ViewCPlane()
    if axis == 0:
        plane  = Rhino.Geometry.Plane.WorldYZ
    elif axis == 1:
        plane  = Rhino.Geometry.Plane.WorldZX
        
    else: plane  = Rhino.Geometry.Plane.WorldXY
    
    tol = sc.doc.ModelAbsoluteTolerance
    
    file = rs.SaveFileName("ContourSG", "CSV file|*.csv||")
    if file:
        csv = open(file,"w")
    pass
    
    for pt in divPts:
        plane.Origin = pt
        intInfo = Rhino.Geometry.Intersect.Intersection.BrepPlane(brep, plane, tol)
        if intInfo[0]:
            if len(intInfo[1]) > 0:
                area = 0
                for crv in Rhino.Geometry.Curve.JoinCurves(intInfo[1]):
                    if blnCrvs: sc.doc.Objects.AddCurve(crv)
                    test = Rhino.Geometry.AreaMassProperties.Compute(crv, tol)
                    
                    if test is not None:
                        area = area + test.Area
                if area is not None:
                    if axis == 0:
                        strPrint =  str(round(pt.X, 4))+","+ str(round(area, 4))
                    elif axis == 1:
                        strPrint =  str(round(pt.Y, 4))+","+ str(round(area, 4))
                    else:
                        strPrint =  str(round(pt.Z, 4))+","+ str(round(area, 4))
                else:
                    strPrint =  str(round(pt.X, 4))+","+ "None"
                csv.write(strPrint+"\n")
                #print strPrint
    csv.close()
    
    
if( __name__ == '__main__' ):
    ContourSG()