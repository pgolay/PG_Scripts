import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import math
import System

"""
    to automate:
    find all linear edges
    find the longest linear edge that ends on an aligned bb(?)
    Section the brep through the middle of this edge.
    If all other edges the section plane crosses are linear and parallel, 
    then use the edge as the extrusion direction.
    Work down through the linear edges by length. Pop edges that have been
    crossed by previous unsuccessful section planes from the edge list.

    From the selected edge:
    find side faces
    section each in the middle.
    Project all results to the bb aligned base plane and
    use the joined result as the extrusion inputs.
    
"""

def FindBestEdge(brep):
    tol = sc.doc.ModelAbsoluteTolerance
    brepEdges = brep.Edges
    faces = brep.Faces
    
    edgeCurves = [item.EdgeCurve for item in brepEdges]
    
    #make a dictionary and then sort linear edges by edge length
    tempD= {item:item.GetLength() for item in edgeCurves if item.IsLinear()}
    
    le = []
    for w in sorted(tempD, key=tempD.get, reverse=False):
        le.append ( w )

    """
    for each edge, make a normal plane at its mid point
    
    Return the first edge for which all other edges hit by its plane are
    both linear and parallel to the test edge
    
    """
    j = -1
    for edge  in le:
        j = j + 1
        edgeOK = True
        p1 = edge.PointAtStart
        p2 = edge.PointAtEnd
        
        vecDir = p2 - p1 
        mid = p1 +(vecDir/2)
        if j == 0:rs.AddTextDot( j, mid)
        plane = Rhino.Geometry.Plane(mid, vecDir) #Mid plane of edge
        base = Rhino.Geometry.Plane(plane)
        top = Rhino.Geometry.Plane(plane)
        top.Origin = p2
        base.Origin = p1
        
        xform = Rhino.Geometry.Transform.ChangeBasis(Rhino.Geometry.Plane.WorldXY, plane)
        
        rc, xrev = xform.TryGetInverse()
        brepBB = brep.GetBoundingBox(xform)
        #rs.AddPoint(brepBB.Min)
        #rs.AddPoint(brepBB.Max)
        ping = brepBB.Min
        pong = brepBB.Max
        plane.RemapToPlaneSpace(ping)
        plane.RemapToPlaneSpace(ping)
        ping.Transform(xrev)
        pong.Transform(xrev)
        if j == 0:
            sc.doc.Objects.AddPoint(ping)
            sc.doc.Objects.AddPoint(pong)
            sc.doc.Objects.AddPoint(p1)
            sc.doc.Objects.AddPoint(p2)
            sc.doc.Objects.AddPoint(p1+plane.XAxis)
            sc.doc.Objects.AddPoint(p1+plane.YAxis)
            sc.doc.Objects.AddPoint(p2+plane.YAxis)
            sc.doc.Objects.AddPoint(p2+plane.XAxis)
            rs.ViewCPlane(plane = plane)
        #break
        print j
        #print "Cope1 " + str(Rhino.Geometry.Point3d.ArePointsCoplanar([p1,p1+plane.XAxis,p1+ plane.YAxis, ping], tol ))
        #print "Cope2 " + str(Rhino.Geometry.Point3d.ArePointsCoplanar([p2,p2+plane.XAxis,p2+plane.YAxis,pong], tol ))
        if not Rhino.Geometry.Point3d.ArePointsCoplanar([p1,p1+plane.XAxis,p1+ plane.YAxis, ping], tol ) or not Rhino.Geometry.Point3d.ArePointsCoplanar([p2,p2+plane.XAxis,p2+plane.YAxis,pong], tol ):
            edgeOK = False
            #print edgeOK
            continue
        sc.doc.Views.Redraw()
        pass
        print "midway " + str(edgeOK)
        for bEdge in edgeCurves:
            bb = bEdge.GetBoundingBox(xform)
            corners = bb.GetCorners()
            #if j == 0:rs.AddPoints(corners)
            up=False
            down=False
            if j == 0:
                rs.ObjectColor(rs.AddPoint(bb.Min), System.Drawing.Color.Red)
                rs.ObjectColor(rs.AddPoint(bb.Max), System.Drawing.Color.Blue)
            
            #for pt in corners: 
                #pt.Transform(xrev)
                #plane.RemapToPlaneSpace(pt)
            #if j == 0:rs.AddPoint(pt)
            pass
            if bb.Max.Z > 0:
                up = True
                if down:
                    break
                else:
                    continue
            elif bb.Min.Z < 0:
                down = True
                if up:
                    break
                else:
                    continue
        print up , down
        if up and down:
            if not bEdge.IsLinear():
               edgeOK = False
               break
            vecTemp = bEdge.PointAtEnd - bEdge.PointAtStart
            parallel = vectemp.IsParallelTo(vecDir)
            if parallel != 1 and parallel != -1:
               edgeOK = False
               break 
    print "EDGEOK = " + str(edgeOK)
    if edgeOK: return edge

def FindSides(brep, vecTest):
    rhVersion = rs.ExeVersion()
    faces = brep.Faces
    caps = []
    sides = []
    edges = []
    for face in faces:
        endCap=True
        line = None
        pass
        for trim in face.OuterLoop.Trims:
            if rhVersion == 5:
                temp = trim.Edge.ToNurbsCurve()
            else:
                temp = trim.Edge.EdgeCurve 
            if temp.IsLinear:
                vec = temp.PointAtEnd-temp.PointAtStart
                parallel =vec.IsParallelTo(vecTest) 
                if parallel == 1 or parallel == -1:
                    line = temp
                    endCap=False
                    break
                    
        if endCap:
             caps.append(face)
        else:
            sides.append(face)
            edges.append(line)
    
    return  sides, edges

def FindOuterCurve(curves, plane):
    inside = Rhino.Geometry.RegionContainment.AInsideB
    outside = Rhino.Geometry.RegionContainment.BInsideA
    tol = sc.doc.ModelAbsoluteTolerance
    outer = curves[0]
    inner = []
    temp = [crv for crv in curves]
    
    while len(temp) > 0:
        test = temp.pop()
        for crv in temp:
            crvState = Rhino.Geometry.Curve.PlanarClosedCurveRelationship(test, crv,plane, tol)
            if  crvState == inside:
                outer = crv
                if not test in inner: inner.append(test)
            elif crvState == outside:
                outer = test
                if not crv in inner: inner.append(crv)
            else:
                if not crv in inner: inner.append(crv)
                if not test in inner: inner.append(test)

    result = [outer]
    result.extend(inner)
    return result
    
def ConvertToExtrusion():
    tol = sc.doc.ModelAbsoluteTolerance
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Brep
    #go.DisablePreSelect()
    
    while True:
        oldDel = False
        retCurves = False
        if sc.sticky.has_key("OLDDELETEBREP"):
            oldDel = sc.sticky["OLDDELETEBREP"]
        if sc.sticky.has_key("OLDRETURNCRVS"):
            retCurves = sc.sticky["OLDRETURNCRVS"]
        
        go.SetCommandPrompt("Select polysurfaces to convert")
        opDelete = Rhino.Input.Custom.OptionToggle(oldDel,"No", "Yes")
        go.AddOptionToggle("DeleteInput", opDelete)
        
        opReturnCrvs = Rhino.Input.Custom.OptionToggle(retCurves,"No", "Yes")
        go.AddOptionToggle("ReturnCurves", opReturnCrvs)
        
        result = go.GetMultiple(1,0)
        
        if( go.CommandResult() != Rhino.Commands.Result.Success ):
            return
            
        if result == Rhino.Input.GetResult.Option:
            oldDel = opDelete.CurrentValue
            sc.sticky["OLDDELETEBREP"] = oldDel
            retCurves = opReturnCrvs.CurrentValue
            sc.sticky["OLDRETURNCRVS"] = retCurves
            pass
        if result == Rhino.Input.GetResult.Object:
            objs = [go.Object(i) for i in range(go.ObjectCount)]
            objref = go.Object(0)
            pass
            #idx = objref.GeometryComponentIndex.Index
            
            break
            #edge = brep.Trims[idx].Edge
            #edgeCrv = edge.ToNurbsCurve()
            
            #if  edgeCrv.IsLinear():
               # break
            #else:
                #print "The selected edge is not linear"
                #continue
    Ids = []
    for item in objs:
        Id = (item.ObjectId)
        Ids.append (Id)
        obj = sc.doc.Objects.Find(Id)
        brep = objref.Brep()
        pass
        brep.Faces.ShrinkFaces()
        
        edgeCrv = FindBestEdge(brep)
        pass
        vecDir = edgeCrv.PointAtEnd - edgeCrv.PointAtStart 
        sides, lines = FindSides(brep, vecDir)
        bPlane = Rhino.Geometry.Plane(edgeCrv.PointAtStart, vecDir)
    
        bb = rs.BoundingBox(Id, bPlane)
        height = bb[0].DistanceTo(bb[4])
        
        plane1 = Rhino.Geometry.Plane(bb[0], bb[1], bb[3])
        plane2 = Rhino.Geometry.Plane(bb[4], bb[5], bb[7])
        tempPlane = Rhino.Geometry.Plane(edgeCrv.PointAtStart, vecDir)
        
        bases = []
        
        # for each linear edge returned with the sides
        # move the base pane to the mid of each edge and intersect
        # with the corresponding brep face. The result should be one curve
        # and most likely a simple iso.
        
        for i in range(len(sides)):
            tempPlane.Origin = lines[i].PointAtStart + ((lines[i].PointAtEnd-lines[i].PointAtStart)/2)
            intx = Rhino.Geometry.Intersect.Intersection.BrepPlane(sides[i].ToBrep(),tempPlane, tol)
            if len(intx[1]) > 0 : crv = intx[1][0]
            if crv is not None:
                bases.append(Rhino.Geometry.Curve.ProjectToPlane(crv,plane1))
            
        if len(bases) == 0:return
        
        baseCurves = Rhino.Geometry.Curve.JoinCurves(bases,tol, False)
        if retCurves: 
            for crv in baseCurves: sc.doc.Objects.AddCurve(crv)
        
        if len(baseCurves) > 1: 
            sortedCurves = FindOuterCurve(baseCurves, plane1)
        else:
            sortedCurves = [baseCurves[0]]
            
        rc,crvPlane = sortedCurves[0].TryGetPlane()
        
        #find the xform for the interior loops- they need to be added in the XY plane
        xform = Rhino.Geometry.Transform.PlaneToPlane(crvPlane, Rhino.Geometry.Plane.WorldXY)
        
        # flip the direction if the base-curve plane is antiparallel to the bb base plane
        if crvPlane.ZAxis.IsParallelTo(plane1.ZAxis)== -1: height = -height
        
        #create the extrusion from the first curve in the list (outer curve)
        ex = Rhino.Geometry.Extrusion.Create(sortedCurves.pop(0), height, brep.IsSolid)
        
        # add any interior curves
        if len(sortedCurves) > 0:
            for crv in sortedCurves:
                crv.Transform(xform)
                ex.AddInnerProfile(crv)
        
        # add the new extrusion to the document
        exId = sc.doc.Objects.AddExtrusion(ex)
        
        
        #clean up
        if exId is not None:
            sc.doc.Objects.Select(exId)
            rs.MatchObjectAttributes(exId, Id)
            exObj = sc.doc.Objects.Find(exId)
            exObj.Attributes.WireDensity = 1
            exObj.CommitChanges()
            pass
            if oldDel: sc.doc.Objects.Delete(obj,True)
        
    sc.doc.Views.Redraw()
    pass
    
if __name__ =="__main__":
    ConvertToExtrusion()