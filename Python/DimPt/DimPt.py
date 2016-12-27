import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs


def DimPt():
    

    
    def get_input():
        
        idx = 0
        if sc.sticky.has_key("dimpt_format"):
            idx = sc.sticky["dimpt_format"]
        
        gp = Rhino.Input.Custom.GetPoint()
        gp.SetCommandPrompt("Set point to dimension.")
        gp.EnableDrawLineFromPoint( True )
        listValues = "None", "XYZ", "WLH"
        opList = gp.AddOptionList("Format", listValues, idx)
        n = 0
        rc = []
        current_point = 1
        
        def GetPointDynamicDrawFunc( sender, args ):
            if len(rc)>1:
                c = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
                args.Display.DrawPolyline(rc, c)
        gp.DynamicDraw += GetPointDynamicDrawFunc
        while True:
            if len(rc)>0:
                if n ==1:
                    gp.SetCommandPrompt("Set leader point.")
                else:gp.SetCommandPrompt("Set leader point.Press Enter to finish.")
                    
                gp.DrawLineFromPoint(prevPoint, True)
                gp.SetBasePoint(prevPoint, True)
                current_point += 1
            getres = gp.Get()
            #if gp.CommandResult()!=Rhino.Commands.Result.Success: return None
            
            if getres==Rhino.Input.GetResult.Cancel:break
                  
            
            elif getres==Rhino.Input.GetResult.Option:
               if gp.OptionIndex()==opList:
                  idx = gp.Option().CurrentListOptionIndex
                  sc.sticky["dimpt_format"] = idx
                  continue
     
            prevPoint = gp.Point()
            rc.append(prevPoint)
            n = n + 1
        return rc, idx
    
    apt, idx = get_input()
    #apt = rs.GetPoints(True, "Set point to dimension", "Set next leader point")
    if not apt: return
    if len(apt) < 2: return
    intRound = 3
    if idx ==0:
        sText  = str(round(apt[0].X,intRound))+ ", "+ str(round(apt[0].Y, intRound))+ ", "+  str(round(apt[0].Z,intRound))
    elif idx == 1:
        sText  = "X"+ str(round(apt[0].X,intRound))+ ", "+ "Y" + str(round(apt[0].Y, intRound))+ ", "+  "Z" + str(round(apt[0].Z,intRound))
    else:
        sText  = "W"+ str(round(apt[0].X,intRound))+ ", "+ "L" + str(round(apt[0].Y, intRound))+ ", "+  "H" + str(round(apt[0].Z,intRound))
    sLeader =rs.AddLeader(apt, view_or_plane=None, text = None)
    
    sDot = rs.AddTextDot(sText, apt.pop())
    
    grp = rs.AddGroup()
    rs.AddObjectsToGroup([sDot,sLeader], grp)
    
    
if __name__ == '__main__':
    DimPt()