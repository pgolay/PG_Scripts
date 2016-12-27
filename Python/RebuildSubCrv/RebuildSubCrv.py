import Rhino 
import rhinoscriptsyntax as rs
import scriptcontext as sc
from System.Drawing import *

def get_crv_input():
    
    deg = 3
    count = 4
    
    if sc.sticky.has_key("RebuildCount"):
        count = sc.sticky["RebuildCount"]
        
    if sc.sticky.has_key("RebuildDeg"):
        deg = sc.sticky["RebuildDeg"]
        
    go = Rhino.Input.Custom.GetObject()
    
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
    go.SubObjectSelect = True
    
    pt_count = Rhino.Input.Custom.OptionInteger(count)
    deg_count = Rhino.Input.Custom.OptionInteger(deg)
    optIntDeg = go.AddOptionInteger("Degree", deg_count)
    optIntCount = go.AddOptionInteger("PointCount", pt_count)
    
    go.SetCommandPrompt("Select a curve or surface edge.")
    
    while True:
        rc = go.Get()
        
        if go.CommandResult()!= Rhino.Commands.Result.Success:
            rc =  go.CommandResult()
            crv = None
                
        if rc==Rhino.Input.GetResult.Object:
            objRef = go.Object(0)
            count = pt_count.CurrentValue
            deg = deg_count.CurrentValue
            
            
        elif rc==Rhino.Input.GetResult.Option:
            count = pt_count.CurrentValue
            deg = deg_count.CurrentValue
            sc.sticky["RebuildCount"] = count
            sc.sticky["RebuildDeg"] = deg
            continue
        break
    return rc, objRef, count, deg

def get_sub_curve(crv, params):
    
    t1 = params[0]
    t2 = params[1]
    
    t_mid = t1 + ((t1+t2)/2)
    X = Rhino.Display
    X.DrawPoint(crv.PointAt(t_mid), Color.Blue)
        
   
    Nurbsy = crv.Geometry.ToNurbsCurve()
    temp = Nurbsy.Split(t1)
    if  temp is None: return
    
    dom = temp[0].Domain
    
    if dom[0] < t_mid < dom[1]:
        tempCrv = temp[0]
    else:
        tempCrv = temp[1]
        
    Nurbsy = tempCrv.ToNurbsCurve()
    temp = Nurbsy.Split(t2)
    if temp is None:return
    
    dom = temp[0].Domain
    if dom[0] < t_mid < dom[1]:
        tempCrv = temp[0]
    else:
        tempCrv = temp[1]
        
    return tempCrv
    

def get_input():
    
    deg = 3
    count = 4
    graph = False
    
    if sc.sticky.has_key("RebuildCount"):
        count = sc.sticky["RebuildCount"]
        
    if sc.sticky.has_key("RebuildDeg"):
        deg = sc.sticky["RebuildDeg"]
       
    if sc.sticky.has_key("ShowGraph"):
        graph = sc.sticky["ShowGraph"]
       
    gop = Rhino.Input.Custom.GetOption()
    
    blnGraph = Rhino.Input.Custom.OptionToggle(False, "No", "Yes")
    
    pt_count = Rhino.Input.Custom.OptionInteger(count,2, 0)
    deg_count = Rhino.Input.Custom.OptionInteger(deg,1, 11)
    optIntDeg = gop.AddOptionInteger("Degree", deg_count)
    optIntCount = gop.AddOptionInteger("PointCount",pt_count)
    deviation = gop.AddOption("Deviation")
    optToggleGraph = gop.AddOptionToggle("CurvatureGraph", blnGraph)
    ends = gop.AddOption("MoveEnds")
    
    gop.SetCommandPrompt("Set option. Press Enter when done.")
    
    while True:
        rc = gop.Get()
        if gop.CommandResult()!=Rhino.Commands.Result.Success:
            rc = gop.CommandResult()
        elif rc==Rhino.Input.GetResult.Option:
            if gop.OptionIndex == deviation:
                reportDeviation()
            elif gop.OptionIndex == ends:
                moveEnds()
            
            graph = optToggleGraph.CurrentValue
            count = pt_count.CurrentValue
            deg = deg_count.CurrentValue
            sc.sticky["RebuildCount"] = count
            sc.sticky["RebuildDeg"] = deg
            sc.sticky["ShowGraph"] = graph
            continue
    
def get_curve_region(crv):
    gp = Rhino.Input.Custom.GetPoint()
    gp.Constrain(crv.Geometry,True)
    rs.UnselectAllObjects()
    gp.SetCommandPrompt("Point on curve")
    gp.Get()
    if gp.CommandResult() == Rhino.Commands.Result.Success:
        crv, t1 = gp.PointOnCurve()
        p1 = crv.PointAt(t1)
    #    def GetPointDynamicDrawFunc( sender, args ):
    #        args.Display.DrawPoint(p1, Color.Red)
    #gcp = Rhino.Input.Custom.GetPoint()
    #gcp.DynamicDraw += GetPointDynamicDrawFunc
    gcp = GetCurvePt( p1, crv)
    gcp.Constrain(crv,True)
    gcp.SetCommandPrompt("2nd Point on curve")
    gcp.Get()
    if gcp.CommandResult() == Rhino.Commands.Result.Success:
        crv, t2 = gcp.PointOnCurve()
    sc.doc.Views.Redraw
    return t1,t2
    
class GetCurvePt (Rhino.Input.Custom.GetPoint):
    def __init__(self, Pt, crv):
        self.m_point = Pt
        self.m_crv = crv
        base = crv.Duplicate()
        par = base.ClosestPoint(Pt)
        temp1 = base.Split(par[1])
        self.m_temp0 = temp1[0]
        self.m_temp1 = temp1[1]
        pass
    def OnDynamicDraw(self, e):
        #pNow = e.CurrentPoint
        #tTemp = self.m_crv.ClosestPoint(pNow)
        #temp2 = temp0.Split(tTemp[1])
        #e.Display.DrawCurve(self.m_temp0, Color.White)
        e.Display.DrawPoint(self.m_point, Color.Red)
        e.Display.DrawPoint(e.CurrentPoint, Color.Red)
         
def test():
    rc, objRef, count, deg = get_crv_input()
    
    
    if not objRef: return
    idx =objRef.GeometryComponentIndex.Index 
    if idx == -1:
        crv = sc.doc.Objects.Find(objRef.ObjectId)
        #rs.SplitCurve(crv, .5)
    else:
        brep = sc.doc.Objects.Find(objRef.ObjectId)
        
        pass
        crv = brep.BrepGeometry.Edges[idx].ToNurbsCurve()
    pass
    
    region = get_curve_region(crv)
    if not region: return
    
    D1 = rs.AddTextDot("1", crv.Geometry.PointAt(region[0]))
    D2 = rs.AddTextDot("2", crv.Geometry.PointAt(region[1]))
    
    if region[0] < region[1]:
        params = [region[0], region[1]]
    else:
        params  = [region[1], region[0]]
        
    tempCrv  = get_sub_curve(crv, params)
    sc.doc.Objects.AddCurve(tempCrv)
    pass
    #get_input()
    
test()