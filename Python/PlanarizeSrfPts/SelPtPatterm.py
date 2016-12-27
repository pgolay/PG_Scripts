import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
import random
"""
To Do:
 -Allow for curves.
Options:
- smooth one point (click)- use the row for fairing but only move the one point
- smooth selected points - use the row(s) for fairing but only move the selected points
- smooth all interior points
----
----
Also:
    move points with falloff
    move points symmetrically

"""

def get_input():
    
    #Defaults
    blnDir = 0
    intSel = 1
    intSkip = 1

    
    #Stored values is any

    if sc.sticky.has_key("PtPatternDir"):
        oldDir  = sc.sticky["PtPatternDir"]
    if sc.sticky.has_key("SelNum"):
        intSel = sc.sticky["SelNum"]
    if sc.sticky.has_key("SkipNum"):
        intSkip  = sc.sticky["SkipNum"]
    
    sc.doc.Objects.UnselectAll()
    sc.doc.Views.Redraw()
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Grip
    
 #set up the options
    optToggleDir = Rhino.Input.Custom.OptionToggle(blnDir, "U","V")
    optIntSel = Rhino.Input.Custom.OptionInteger(intSel)
    optIntSkip = Rhino.Input.Custom.OptionInteger(intSkip)

 #add the options

    go.AddOptionToggle("Direction",optToggleDir)
    go.AddOptionInteger("Select",optIntSel)
    go.AddOptionInteger("Skip",optIntSkip)

    go.SetCommandPrompt("Select a surface control point")
    
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
            sc.sticky["PtPatternDir"] = dir
            intSel = optIntSel.CurrentValue
            intSkip = optintSkip.CurrentValue

                
            continue
            
    if grip is None:return
    sc.doc.Views.Redraw()
    return grip.OwnerId, grip.Index, blnDir, intSel, intSkip
    

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


def sel_grip_pattern():

#    while True:
        nextRow=None
        prevRow=None
        #aGrip = rs.GetObjectGrip("Select a control point", False, True)
        aGrip = get_input()
        if not aGrip: return
        if aGrip ==  Rhino.Commands.Result.Cancel: return
        Id = aGrip[0]
        Idx = aGrip[1]
        dir = aGrip[2]
        intSel = aGrip[3]
        intSkip = aGrip[4]

        if dir: 
            dir = 1
        else:
             dir = 0
             
        if  rs.IsSurface(Id):
            rowInfo = surface_UV_idx(Id)
            Rows = rowInfo[dir]
            Cols = rowInfo[abs(1-dir)]
            Max = len(Rows)#number in the smooth direction
            
        for i in range(Max):
            if Idx  in(Rows[i]):
                Row = Rows[i]
                break

        pos = Row.index(Idx)
        
        def shift(Row,intShift):
            for i in range(intShift):
                temp = Row.pop()
                Row.insert(0, temp)
        
        shift(Row, len(Row) - pos)
        selList = []

        sel = True

        n = 0
        for i in range(len(Row)):
            if sel:
                selList.append(Row[i])
            n = n + 1
            
            if sel and n == intSel:
                sel = False
                n = 0
            if not sel and n == intSkip:
                sel = True
                n = 0
            
                
        for idx in selList:
            rs.SelectObjectGrip(Id, idx)
    
            
          
  
    
if __name__ == '__main__':
    sel_grip_pattern()