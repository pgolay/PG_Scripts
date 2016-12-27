import rhinoscriptsyntax as rs
import scriptcontext as sc


def PasteToCursor():
    
    rs.EnableRedraw(False)
    rs.Command("_Paste")
    if rs.LastCommandResult() != 0: return
    
    Ids = rs.LastCreatedObjects()
    if Ids is None: return
    
    pt = rs.BoundingBox(Ids)[0]
    rs.EnableRedraw(True)
    rs.Command("_Move W" + str(pt) )
        
if __name__ =="__main__":
    PasteToCursor()  