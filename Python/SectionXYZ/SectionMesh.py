import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import System



def XYZSections():
    
    red = System.Drawing.Color.Red
    blue = System.Drawing.Color.Blue
    green = System.Drawing.Color.Green
    
    def getSectionInputs():
        
        X = True
        Y = True
        Z = True
        XSpace = 1
        YSpace = 1
        ZSpace = 1
        
        if sc.sticky.has_key("SectionX"):
            X = sc.sticky["SectionX"]
        if sc.sticky.has_key("SectionY"):
            Y = sc.sticky["SectionY"]
        if sc.sticky.has_key("SectionZ"):
            Z = sc.sticky["SectionZ"]
        
        if sc.sticky.has_key("XSpace"):
            XSpace = sc.sticky["XSpace"]
        if sc.sticky.has_key("YSpace"):
            YSpace = sc.sticky["YSpace"]
        if sc.sticky.has_key("ZSpace"):
            ZSpace = sc.sticky["ZSpace"]
        
        go = Rhino.Input.Custom.GetObject()
        go.GeometryFilter = Rhino.DocObjects.ObjectType.Mesh
        go.SetCommandPrompt("Select a mesh to section")
        
        while True:
            go.ClearCommandOptions()
            
            boolOptionX = Rhino.Input.Custom.OptionToggle(X, "No", "Yes")
            boolOptionY = Rhino.Input.Custom.OptionToggle(Y, "No", "Yes")
            boolOptionZ = Rhino.Input.Custom.OptionToggle(Z, "No", "Yes")
        
            
            dblOptionX = Rhino.Input.Custom.OptionDouble(XSpace)
            dblOptionY = Rhino.Input.Custom.OptionDouble(YSpace)
            dblOptionZ = Rhino.Input.Custom.OptionDouble(ZSpace)        
            
            go.AddOptionToggle("XSection", boolOptionX)
            go.AddOptionToggle("YSection", boolOptionY)
            go.AddOptionToggle("ZSection", boolOptionZ)
            
            x_opt = go.AddOptionDouble("XSpacing", dblOptionX)
            y_opt = go.AddOptionDouble("YSpacing", dblOptionY)
            z_opt = go.AddOptionDouble("ZSpacing", dblOptionZ)
            all_opt = go.AddOption("SetAllSpacingToX") 
            
            rc = go.Get()
            
            if go.CommandResult() != Rhino.Commands.Result.Success:
                return go.CommandResult()
               
            if rc==Rhino.Input.GetResult.Object:
                 objRef = go.Object(0)
                 
                 
                 XSpace = dblOptionX.CurrentValue
                 YSpace = dblOptionY.CurrentValue
                 ZSpace = dblOptionZ.CurrentValue
                
                 sc.sticky["SectionX"] = X
                 sc.sticky["SectionY"] = Y
                 sc.sticky["SectionZ"] = Z
                
                 sc.sticky["XSpace"] = XSpace
                 sc.sticky["YSpace"] = YSpace
                 sc.sticky["ZSpace"] = ZSpace
                
                 break
                
            elif rc==Rhino.Input.GetResult.Option:
                XSpace = dblOptionX.CurrentValue
                YSpace = dblOptionY.CurrentValue
                ZSpace = dblOptionZ.CurrentValue
                X = boolOptionX.CurrentValue
                Y = boolOptionY.CurrentValue
                Z = boolOptionZ.CurrentValue
                
                if go.OptionIndex()==all_opt:
                    YSpace = XSpace
                    ZSpace = XSpace
                    X = boolOptionX.CurrentValue
                    Y = boolOptionY.CurrentValue
                    Z = boolOptionZ.CurrentValue
                continue
           
        return objRef, X, Y, Z, XSpace, YSpace, ZSpace
        
        
        
    inputs = getSectionInputs()
    if inputs == Rhino.Commands.Result.Cancel: return
    
    sMesh, blnX, blnY, blnZ, xS, yS, zS  = inputs
    if not blnX and not blnY and not blnZ:
        print "No section directions were set to Yes. At least one must be Yes." 
        return
        
    meshObj = sc.doc.Objects.Find(sMesh.ObjectId)
    bBox = meshObj.Geometry.GetBoundingBox(Rhino.Geometry.Plane.WorldXY)
    corners  = bBox.GetCorners()

    planeX = Rhino.Geometry.Plane.WorldYZ
    planeY = Rhino.Geometry.Plane.WorldZX
    planeZ = Rhino.Geometry.Plane.WorldXY
    
    vecX = Rhino.Geometry.Vector3d(1,0,0)* xS
    vecY = Rhino.Geometry.Vector3d(0,1,0)* yS
    vecZ = Rhino.Geometry.Vector3d(0,0,1)* zS
    
    baseX = corners[0][0]-(corners[0][0] % xS)
    baseY = corners[0][1]-(corners[0][1] % yS)
    baseZ = corners[0][2]-(corners[0][2] % zS)
    
    basePt = Rhino.Geometry.Point3d(baseX, baseY, baseZ)
    
    endX = corners[6][0]-(corners[6][0] % xS) + xS
    endY = corners[6][1]-(corners[6][1] % yS) + yS
    endZ = corners[6][2]-(corners[6][2] % zS) + zS
    
    endPt = Rhino.Geometry.Point3d(endX, endY, endZ)
    
    if not rs.IsLayer("Sections"):
        rs.AddLayer("Sections")
         
    rs.EnableRedraw(False)
    
    if blnX:
        if not rs.IsLayer("Sections::XSections"):
            rs.AddLayer("XSections", red, True, False, "Sections")

        planeX.Origin = basePt
        while planeX.Origin[0] < endPt[0]:
            pLine = Rhino.Geometry.Intersect.Intersection.MeshPlane(meshObj.Geometry, planeX)
            if pLine:
                for obj in pLine:
                    addPline = sc.doc.Objects.AddPolyline(obj)
                    rs.ObjectLayer(addPline, "Sections::XSections")
            planeX.Origin = planeX.Origin + vecX
         
    if blnY:
        if not rs.IsLayer("Sections::YSections"):
           rs.AddLayer("YSections", green, True, False, "Sections")
        
        planeY.Origin = basePt
        while planeY.Origin[1] < endPt[1]:
            
            pLine = Rhino.Geometry.Intersect.Intersection.MeshPlane(meshObj.Geometry, planeY)
            if pLine:
                for obj in pLine:
                    addPline = sc.doc.Objects.AddPolyline(obj)
                    rs.ObjectLayer(addPline, "Sections::YSections")
            planeY.Origin = planeY.Origin + vecY
    
    if blnZ:
        if not rs.IsLayer("Sections::ZSections"):
           rs.AddLayer("ZSections", blue, True, False, "Sections")
        
        planeZ.Origin = basePt
        while planeZ.Origin[2] < endPt[2]:
            
            pLine = Rhino.Geometry.Intersect.Intersection.MeshPlane(meshObj.Geometry, planeZ)
            if pLine:
                for obj in pLine:
                    addPline = sc.doc.Objects.AddPolyline(obj)
                    rs.ObjectLayer(addPline, "Sections::ZSections")
    
            planeZ.Origin = planeZ.Origin + vecZ
        
        rs.EnableRedraw(True)
    
    
XYZSections()