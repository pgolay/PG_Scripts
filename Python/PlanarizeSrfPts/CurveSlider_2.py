import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino
from System import Drawing as sd

def get_end_point(apts):
    old_x_list = apts
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
        #x_list.append(apts[0])
        x_list = apts
        n = 0
        for idx in range(1, len(apts)-1):
            n = n  + 1
            if n > 20:return
            dist2 = dist/idx
            print idx, str(x_list[2])
            if dist2:
 #                m = (apts[idx] - apts[idx+1])
                m = (x_list[idx] - x_list[idx+1])
                if rev:
                    m.Reverse()
                m.Unitize()
                vecdir = dist2*ratio * m
                x = x_list[idx] + vecdir
 #                x = apts[idx] + vecdir
            else: x  = apts[idx]

            x_list.insert(idx,x)
            
            
            args.Display.DrawPoint( x , point_color)
            args.Display.DrawPoint( now_pt , point_color)

            for i in range( len(x_list)-1):
                args.Display.DrawLine( x_list[i], x_list[i+1], line_color)
                
        #old_x_list = x_list
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
        ratio = dist/vec_base.Length
        if not dist: return
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