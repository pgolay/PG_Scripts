import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
import System
from System.Drawing import *
from Rhino.Commands import *
from Rhino.Geometry import *
from System.Collections.Generic import List
"""
Sets rows of surface cointrol points to a user defined plane.
"""

class DrawSrfUVEdgesConduit(Rhino.Display.DisplayConduit):
    
    def __init__(self, crv1, crv2):
        X = crv2.TangentAtStart
        Rhino.Geometry.Vector3d.Reverse(X)
        self.crv1 = crv1
        self.crv2 = crv2
        self.vec1 = crv1.TangentAtEnd
        self.vec2 = X
        pass
        
    def DrawOverlay(self, e):
        e.Display.DrawCurve(self.crv1, Color.Red, 3)
        e.Display.DrawCurve(self.crv2, Color.Green, 3)
        e.Display.DrawArrowHead( self.crv1.PointAtEnd, self.vec1, Color.Red, 20.0, 0.0)
        e.Display.DrawArrowHead( self.crv2.PointAtStart, self.vec2, Color.Green, 20.0,0.0)
        
def get_input(srf):
    
    dir = False
    listIndex = 0
    blnTwo = False
    
    sc.doc.Objects.UnselectAll()
    sc.doc.Views.Redraw()
    
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Grip
    listValues = ["Auto", "WorldVertical", "CPlaneVertical", "View"]
    listValues2Pt = ["WorldVertical", "CPlaneVertical", "View"]
    gOpt =  Rhino.Input.Custom.GetOption()
    
    while True:
    
        if sc.sticky.has_key("PlanarizeDir"):
            dir  = sc.sticky["PlanarizeDir"]
            
        if sc.sticky.has_key("PlaneStyle"):
            listIndex  = sc.sticky["PlaneStyle"]
            
        if sc.sticky.has_key("blnTwoPoints"):
            blnTwo = sc.sticky["blnTwoPoints"]
            
        optToggleDir = Rhino.Input.Custom.OptionToggle(dir, "U","V")
        optToggleTwo = Rhino.Input.Custom.OptionToggle(blnTwo, "No", "Yes")
        
        optList = go.AddOptionList("Plane", listValues, listIndex)
        
        go.AddOptionToggle("Direction", optToggleDir)
        go.AddOptionToggle ("TwoPoints",  optToggleTwo)
        optSurface = go.AddOption("ChangeSurface")
        go.SetCommandPrompt("Select a surface control point")

        if blnTwo and  listIndex == 0:
            x = gOpt.AddOptionList("Plane", listValues2Pt, 1)
            gOpt.SetCommandPrompt("Two point plane direction cannot work with the auto plane. Please choose a plane style.")
            gOpt.Get()
            if gOpt.CommandResult() != Rhino.Commands.Result.Success:
                return gOpt.CommandResult()
            else:
                listIndex = gOpt.Option().CurrentListOptionIndex + 1
                sc.sticky["PlaneStyle"] = listIndex
                continue

        get_rc = go.Get()
        if go.CommandResult() != Rhino.Commands.Result.Success:
            return go.CommandResult()
            

        if get_rc==Rhino.Input.GetResult.Object:
            objRef = go.Object(0)
            grip = objRef.Object()
            break
            
        elif get_rc==Rhino.Input.GetResult.Option:

            dir = optToggleDir.CurrentValue
            blnTwo = optToggleTwo.CurrentValue #two points to set plane
            sc.sticky["PlanarizeDir"] = dir
            sc.sticky["blnTwoPoints"] = blnTwo
            
            if go.Option().Index==optList: #plane style
               listIndex = go.Option().CurrentListOptionIndex
               sc.sticky["PlaneStyle"] = listIndex
               
            elif go.Option().Index == optSurface:
                return ["NewSurface"]
               
            continue
            
    if grip is None:return
    sc.doc.Views.Redraw()
 
    return  grip.Index, dir, blnTwo, listIndex
    
def get_two_points():
    
    gl = Rhino.Input.Custom.GetLine()
    rc, line = gl.Get()
    pass
    if rc != Rhino.Commands.Result.Success:
        return gl.CommandResult()
    
    if line:return line.From, line.To

def planarize_srf_pts():

    while True:
        
        srfId = rs.GetObject("Select a surface.", 8)
        if not srfId:
            return
            
        if not rs.ObjectGripsOn(srfId):
            rs.EnableObjectGrips(srfId)

        while True:
            
            brep = sc.doc.Objects.Find(srfId).Geometry
            edge1 = brep.Edges[0]
            edge2 = brep.Edges[3]
            conduit = DrawSrfUVEdgesConduit(edge1, edge2)
            conduit.Enabled = True
            sc.doc.Views.Redraw()
            
            nextRow=None
            prevRow=None
            
            aGrip = get_input(sc.doc.Objects.Find(srfId))
            
            if not aGrip:
                conduit.Enabled = False
                sc.doc.Views.Redraw()
                return
            if aGrip == Rhino.Commands.Result().Cancel: 
                conduit.Enabled = False
                sc.doc.Views.Redraw()
                return
            if aGrip ==  Rhino.Commands.Result.Cancel: return
            if aGrip[0] == "NewSurface":
                srfId = None
                aGrip = None
                break
                
            Idx = aGrip[0]
            dir = aGrip[1]
            blnTwo = aGrip[2]
            planeStyle = aGrip[3]
            
            if dir: 
                dir = 1
            else:
                 dir = 0
                 
            x = Surface_UV_idx(srfId)
            if  rs.IsSurface(srfId):
                Rows = Surface_UV_idx(srfId)[dir]
                Max = len(Rows)
                
                for i in range(Max):
                    if Idx  in(Rows[i]):
                        rowIdx = i
                        Row = Rows[i]
                        if rowIdx<>0:
                            prevRow = Rows[i-1]
                        if rowIdx < Max-1:
                            nextRow = Rows[i+1]
                        break
                apts = []
    
                if planeStyle == 0:
                    n = 0
                else:
                    n = 4
                    
                while n < 5:
                    for idx in Rows[rowIdx]:
                        apts.append(rs.ObjectGripLocation(srfId,idx))
                        
                    Plane = get_ref_plane(planeStyle, apts, blnTwo)
                    p1 = False
                    p2 = False
                    
                    
                    if blnTwo:
                        ptRange = range(len(Row))
                    else:
                        ptRange  = range(1, len(Row) - 1)
                    
                    for idx in ptRange:
                        pts = []
                        if nextRow:
                            pts.append( rs.LinePlaneIntersection([rs.ObjectGripLocation(srfId,nextRow[idx]),apts[idx]], Plane) )
                            p1 = True
       
                        if prevRow:
                            pts.append( rs.LinePlaneIntersection([rs.ObjectGripLocation(srfId,prevRow[idx]),apts[idx]], Plane) )
                            p2 = True
                            
                        if not p1 or not p2: 
                            targ = pts[0]
                        else: targ = pts[rs.PointArrayClosestPoint(pts, apts[idx])]
                        
                        rs.ObjectGripLocation(srfId,Row[idx], targ)
                        
                        n = n + 1
                conduit.Enabled = False
                sc.doc.Views.Redraw()
            conduit.Enabled = False
            sc.doc.Views.Redraw()
    
def get_ref_plane(intStyle, pts, blnTwo):
    
    if intStyle > 0:
        if intStyle ==1:
            tempPlane = Rhino.Geometry.Plane.WorldXY
        elif intStyle == 2:
            tempPlane = rs.ViewCPlane()
            
        else:
            tempPlane = rs.ViewCameraPlane()
            
        if blnTwo:
            pts = get_two_points()
            if not pts:return
            p1 = pts[0]
            p2 = pts[1]
        else:
                
            p1 = tempPlane.ClosestPoint(pts[0])
            p2 = tempPlane.ClosestPoint(pts[len(pts)-1])
            
        vecX = p2-p1
        n = Rhino.Geometry.Vector3d.Unitize(vecX)
        newPlane = Rhino.Geometry.Plane(p1,vecX,tempPlane.ZAxis)
            
    else:
        newPlane = rs.PlaneFitFromPoints(pts)
            

    return newPlane
    
def Surface_UV_idx(srf):
  
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
    
if __name__ == '__main__':
    planarize_srf_pts()