import rhinoscriptsyntax as rs
import random


def test():
    
    Ids = rs.GetObjects("Select block instances to rotate", filter = 4096, preselect=True)
    if Ids is None: return
    vec = rs.VectorCreate([0,0,1], [0,0,0])
    
    
    for Id in Ids:
        pt = rs.BlockInstanceInsertPoint(Id)
        ang = random.randrange(-180, 180)
        rs.RotateObject(Id, pt,ang,vec)
     
    
if __name__ == "__main__":
    test()