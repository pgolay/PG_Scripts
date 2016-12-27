import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino
from System import Drawing as sd

def get_end_point(apts):
    dist_list = []
    proportions = []
    total_dist = 0
    for idx in range(len(apts)-1):
        dist_list.append(apts[idx].DistanceTo(apts[idx+1]))
        

    total_dist = sum(dist_list)
    for idx in range(len(dist_list)-1):
        proportions.append(dist_list[idx]/total_dist)
    pass
 
    
    def GetPointDynamicDrawFunc( sender, args ):
        x_list = []
        rev = False
        vec_base =  apts[0] - apts[1]
        now_pt = args.CurrentPoint
        vec_move = now_pt - apts[0]
        dist = vec_move.Length  
        if vec_move.IsParallelTo(vec_base) == -1: rev = True
        ratio = dist/vec_base.Length
        
        for idx in range(1, len(apts)-1):
            
            dist2 = dist/idx
            if dist2:
                m = (apts[idx] - apts[idx+1])
                if rev:
                    m.Reverse()
                m.Unitize()
                vecdir = dist2*ratio * m
                x = apts[idx] + vecdir
                
            else: x  = apts[idx]
            
            x_list.append(x)
            
            args.Display.DrawPoint( x , point_color)
            args.Display.DrawPoint( now_pt , point_color)
            
            for i in range( len(x_list)-1):
                args.Display.DrawLine( x_list[i], x_list[i+1], line_color)
        args.Display.DrawLine( x_list[i+1], apts[bound], line_color)
        args.Display.DrawLine( x_list[0], now_pt, line_color)
        
    gp = Rhino.Input.Custom.GetPoint()
    line_color = sd.Color.FromArgb(255,0,0)
    point_color = sd.Color.FromArgb(150,0,50)
    track_color = sd.Color.FromArgb(230,230,230)
    
    bound = len(apts)- 1
    line  = Rhino.Geometry.Line(apts[0], apts[1])
    ptLoc = []
    gp  = Rhino.Input.Custom.GetPoint()
    gp.AcceptNumber(True, False)
    gp.Constrain(line)
    gp.PermitObjectSnap(True)
    gp.SetBasePoint(apts[0], True)
    gp.DynamicDraw += GetPointDynamicDrawFunc
    gp.Get()
    
    if( gp.CommandResult() == Rhino.Commands.Result.Success ):
        pt = gp.Point()
        ptLoc.append(pt)
        
        rev = False
        vec_base =  apts[0] - apts[1]
        vec_move = pt - apts[0]
        if vec_move.IsParallelTo(vec_base) == -1: rev = True
        dist = vec_move.Length
        if not dist: return
        ratio = dist/vec_base.Length

    for idx in range(1, len(apts)-1):
            
            dist2 = dist/idx
            if dist2:
                m = (apts[idx] - apts[idx+1])
                if rev:
                    m.Reverse()
                m.Unitize()
                vecdir = dist2*ratio * m
                x = apts[idx] + vecdir
                
            else: x  = apts[idx]
            
            ptLoc.append(x)
    ptLoc.append(apts[bound])
    
    

    sc.doc.Views.Redraw()
    return ptLoc

def CurveSlider():
    
    while True:
        
        #objRef = get_curve()
        arr = rs.GetCurveObject()
        if not arr: return
    
        #Id = rs.CopyObject(arr[0])
        Id = arr[0]
        pickPt = arr[3]
        pickPar = arr[4]
        
        curveObj = sc.doc.Objects.Find(Id)
        deg = curveObj.Geometry.Degree
        gripsOn = rs.ObjectGripsOn(Id)
        rs.EnableObjectGrips(Id)
        pts0 = rs.CurvePoints(Id)
        crvEnd  = 0
        crvDom = curveObj.Geometry.Domain
        
        if pickPar > crvDom.Mid:
            crvEnd = 1
            r =rs.ReverseCurve(Id)
        
        pts = rs.CurvePoints(Id)
        move_pt = get_end_point(pts)
        
        pass
        if move_pt == Rhino.Commands.Result.Cancel: return
        
        rs.ObjectGripLocations(Id,move_pt)
    

#    
#    
CurveSlider()