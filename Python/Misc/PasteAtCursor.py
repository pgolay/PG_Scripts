import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

def PasteAtCursor():
    
    rs.EnableRedraw(False)
    rs.Command("_Paste")
    if rs.LastCommandResult() != 0: return
    
    Ids = rs.LastCreatedObjects()
    if Ids is None: return
    
    pt = rs.BoundingBox(Ids)[0]
    
    targ = rs.GetCursorPos()[0]
    
    rs.MoveObjects(Ids, targ-pt)    
    rs.EnableRedraw(True)
    
        
if __name__ =="__main__":
    PasteAtCursor()   