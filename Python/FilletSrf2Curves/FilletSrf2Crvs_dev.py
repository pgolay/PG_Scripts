import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
import System
from System.Drawing import *
from math import pi

def get_curve_overlaps(crvId1, crvId2):

    test1 = sc.doc.Objects.Find(crvId1).Geometry
    test2 = sc.doc.Objects.Find(crvId2).Geometry
    tol = rs.UnitAbsoluteTolerance()
    
    if not Rhino.Geometry.Curve.DoDirectionsMatch(test1, test2): test1.Reverse()
    dom1 = test1.Domain
    
    p1 = test1.ClosestPoint(test2.PointAtStart)[1]
    p2 = test1.ClosestPoint(test2.PointAtEnd)[1]

    pars = []
    
    plane = test1.PerpendicularFrameAt(dom1.T0)[1]
    aInt = Rhino.Geometry.Intersect.Intersection.CurvePlane(test2, plane, tol)
    if aInt is None:
        pars.append(p1)
    else : pars.append (dom1.T0)
    
    plane = test1.PerpendicularFrameAt(dom1.T1)[1]
    aInt = Rhino.Geometry.Intersect.Intersection.CurvePlane(test2, plane, tol)
    if aInt is None:
        pars.append(p2)
    else : pars.append (dom1.T1)
    
    int1 = Rhino.Geometry.Interval(pars[0],pars[1])

    return test1.Trim(int1), test2
    
def check_deviations(loft, crv1, crv2):
    brep = loft.ToBrep()
    tol = rs.UnitAbsoluteTolerance()
    #    crv1 = sc.doc.Objects.Find(crvSrf).Geometry
    #    crv2 = sc.doc.Objects.Find(crvUp).Geometry
    edge1 = brep.Edges[0]
    edge2 = brep.Edges[2]
    d = Rhino.Geometry.Curve.GetDistancesBetweenCurves(crv1, edge1, tol)
    d1 = round(d[1], 4)
    p1 = d[2]
    d = Rhino.Geometry.Curve.GetDistancesBetweenCurves(crv2, edge2, tol)
    d2 = round(d[1], 4)
    p2 = d[2]
    #Return max distances and parameter location of the max distance
    return [d1,p1,d2,p2]
    
class DrawSrfConduit(Rhino.Display.DisplayConduit):
    
    def __init__(self, brep, d1, d2, p1, p2):
        # input = (brep, string, string, pt3d, pt3d)
        plane = rs.ViewCameraPlane()
        plane.Origin = p1
        t1 = Rhino.Display.Text3d(d1, plane ,12)
        self.brep = brep
        self.black = Color.Black
        self.color1 = Color.Black
        self.color2 = Color.White
        self.text1 = t1
        self.d1 = d1
        self.d2 = d2
        self.p1 = p1
        self.p2 = p2
        pass
        
    def DrawForeground(self, e):
        e.Display.DrawBrepWires(self.brep, self.black, 1)
        e.Display.DrawDot(self.p1, self.d1, self.color1, self.color2)
        e.Display.DrawDot(self.p2, self.d2, self.color1, self.color2)
        e.Display.Draw3dText(self.Text1, self.color2)
    
def refine(crv1, crv2, arc_list):
    pass
    
def build_fillet(srfId, crv1, crv2, par_list, blnRebuild):
    
    tol = rs.UnitAbsoluteTolerance()
    #    crv1 = sc.doc.Objects.Find(crvSrf).Geometry
    #    crv2 = sc.doc.Objects.Find(crvUp).Geometry
    srf = sc.doc.Objects.Find(srfId).Geometry.Faces[0]
    arc_list = []
    lType = Rhino.Geometry.LoftType.Normal
    count = 0
    angle  = 0
    for par in par_list:
        plane  = crv1.PerpendicularFrameAt(par)[1]
        aInt = Rhino.Geometry.Intersect.Intersection.CurvePlane(crv2, plane, tol*2)
        pts = []
        if len(aInt) > 1:
                
            for i in range (len(aInt)):
                pts.append(aInt[i].PointA)
                    
            crvPt = pts[ rs.PointArrayClosestPoint(pts, plane.Origin)]
            
        else:
            crvPt = aInt[0].PointA
        if crvPt:
            testPar = srf.ClosestPoint(crv1.PointAt(par))
            tPlane = srf.FrameAt(testPar[1], testPar[2])[1]
            testPar = srf.ClosestPoint(crvPt)
            pullPt = srf.PointAt(testPar[1], testPar[2])
            vecDir = pullPt-plane.Origin
            vecDir.Unitize()
            arc = Rhino.Geometry.Arc(plane.Origin, vecDir, crvPt)
            arc_list.append( arc.ToNurbsCurve())
            testAngle  = arc.Angle
            testCount = int((testAngle*12)/pi)
            if testCount > count: count = testCount
            if testAngle > angle: angle = testAngle
                
        pass
        """
        If angle < 45, deg3, 4 pt
        45 to 60 deg 4, 5
        60 - 105 deg 5, 6 pt
        add point per 15 deg
        """
                
                
    x =  Rhino.RhinoMath.ToDegrees(angle)
    if x <=45: 
        deg = 3
        count = 4
    elif 45 <=x <=60:
        deg = 4
        count = 5
    else:
 
        test = int(x/15)
        
        if test > 3:
            deg = 5
            count = 6 + (test-3)
    print "count = ", count,"deg = " , deg
    for i in range(len(arc_list)):
        arc_list[i] = arc_list[i].Rebuild( count, deg, True)
    pass
    #            print count
    #            print deg
    loft = Rhino.Geometry.Brep.CreateFromLoft(arc_list, start = Rhino.Geometry.Point3d.Unset, end = Rhino.Geometry.Point3d.Unset, loftType = lType, closed = False)
    #if loft: sc.doc.Objects.AddSurface(loft[0].Faces[0])
    return loft[0].Faces[0]

def test():
    intDiv = 10
    if sc.sticky.has_key("DivSamples"):
        intDiv = sc.sticky["DivSamples"]
        
    blnRebuild = False
    
    if sc.sticky.has_key("blnRebuild"):
        blnRebuild = sc.sticky["blnRebuild"]
    
    srfId = rs.GetObject("Select a base surface.", 8)
    if not srfId: return
    
    crvSrf = rs.GetObject("Select a curve on the base surface.", 4)
    if not crvSrf: return
    
    while True:
        crvUp = rs.GetObject("Select a curve off of the base surface.", 4)
        if crvUp == crvSrf:
            continue
        else: break
        
    crv2 = sc.doc.Objects.Find(crvUp).Geometry
    
    if not crvUp: return
    
    crv1, crv2 = get_curve_overlaps(crvSrf, crvUp)
    pass

    par_list = None
    blnInsert = False
    tol = rs.UnitAbsoluteTolerance()
    
    while True:

        if not par_list:
            par_list = list(crv1.DivideByCount(intDiv, True))
        
        loft = build_fillet(srfId, crv1, crv2, par_list, blnRebuild)

        dev = check_deviations(loft, crv1, crv2)
        p1 = crv1.PointAt(dev[1])
        p2 = crv2.PointAt(dev[3])
        d1  = str(dev[0])
        d2 = str(dev[2])

        conduit = DrawSrfConduit(loft.ToBrep(), d1, d2, p1, p2)
        conduit.Enabled = True
        sc.doc.Views.Redraw()
        
        go = Rhino.Input.Custom.GetOption()
        go.AcceptNumber(True, False)
        
        go.AddOption("InsertSamples")#idx 1
        
        optIntDiv = Rhino.Input.Custom.OptionInteger( intDiv,True, 3)
        go.AddOptionInteger("Samples", optIntDiv)
        
        optToggleRebuild = Rhino.Input.Custom.OptionToggle(blnRebuild, "No", "Yes")
        go.AddOptionToggle("Deformable", optToggleRebuild)
        
        go.SetCommandPrompt("Set the number of samples")
        rc = go.Get()
        
        if go.CommandResult()!=Rhino.Commands.Result.Success:
            if loft: sc.doc.Objects.AddSurface(loft)
            conduit.Enabled = False
            sc.doc.Views.Redraw()
            return go.CommandResult()
            
        if rc == Rhino.Input.GetResult.Number:
            intDiv = int(go.Number())
            sc.sticky["DivSamples"] = intDiv
            conduit.Enabled = False
            par_list = None
            continue
        if rc == Rhino.Input.GetResult.Option:
            blnRebuild = optToggleRebuild.CurrentValue
            sc.sticky["blnRebuild"] = blnRebuild
            #if go.OptionIndex()== optIntDiv:
            intDiv = optIntDiv.CurrentValue
            par_list = None
            sc.sticky["DivSamples"] = intDiv
            if go.OptionIndex()!= 1:conduit.Enabled = False

            if go.OptionIndex()== 1:
                gp = Rhino.Input.Custom.GetPoint()
                gp.Constrain(crv1.ToNurbsCurve(), True)
                
                while True:
                    ptRC = gp.Get()
                    if gp.CommandResult()!=Rhino.Commands.Result.Success:
                        conduit.Enabled = False
                        break
                        
                    if Rhino.Input.GetResult.Point:
                        pt = gp.Point()
                        temp = crv1.ClosestPoint(pt)
                        conduit.Enabled = False
                        
                        if not par_list: par_list = list(crv1.DivideByCount(intDiv, True))
                        if temp[0]: 
                            par_list.append(temp[1])
                            par_list = sorted(par_list)
                            
                            loft = build_fillet(srfId, crv1, crv2, par_list, blnRebuild)
                              
                            dev = check_deviations(loft, crv1, crv2)
                            p1 = crv1.PointAt(dev[1])
                            p2 = crv2.PointAt(dev[3])
                            d1  = str(dev[0])
                            d2 = str(dev[2])
                              
                            conduit = DrawSrfConduit(loft.ToBrep(), d1, d2, p1, p2)
                            conduit.Enabled = True
                            sc.doc.Views.Redraw()
                    else:
                        par_list = None
                        conduit.Enabled = False
                        continue
                blnInsert = True
    if loft: sc.doc.Objects.AddSurface(loft)
    conduit.Enabled = False
    sc.doc.Views.Redraw()
    pass
    
test()