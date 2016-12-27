import rhinoscriptsyntax as rs

def ReadNamedPoints():
    
    sFile = rs.OpenFileName("Named point import", "Text files (*.txt)|*.txt||",  rs.WorkingFolder(),extension= ".txt")
    if not sFile: return
    rs.EnableRedraw(False)
    with open(sFile, "r") as oFile:
        l = oFile.readlines()

        for i in range(1, len(l)):
            ptStr = l[i].split(chr(9))
            name = ptStr[0]
            pt = rs.Str2Pt(ptStr[1]+","+ptStr[2]+","+ptStr[3])
            rs.ObjectName(rs.AddPoint(pt), name)
            pass
    rs.EnableRedraw(True)
    
if __name__ == "__main__":
    ReadNamedPoints()