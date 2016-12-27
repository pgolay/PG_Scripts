import rhinoscriptsyntax as rs
import scriptcontext as sc 
import Rhino



def InsertV5():
    
    blocks = rs.BlockNames()
    
    x = sorted(blocks, key=str.lower)
    
    y = Rhino.UI.Dialogs.ShowComboListBox("Test","Test", x)
    
    if not y: return
    cmdstr = "-Insert " + chr(34) + y + chr(34) + " " + "Block " + "Pause " + "EnterEnd "
    rs.Command(cmdstr)
    pass
    
    
InsertV5()



