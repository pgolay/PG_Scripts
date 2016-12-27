import rhinoscriptsyntax as rs

def UpdateSelected():
    insts = rs.GetObjects("Select block instnces to refresh.", 4096, preselect=True)
    
    if  insts:
    
        names  = [rs.BlockInstanceName(inst)for inst in insts]
        pass
        for name in list(set(names)):
            if not rs.IsBlockEmbedded(name):
                print "true"
                rs.Command("-BlockManager Update " + chr(34) +name+ chr(34) + " Enter")
UpdateSelected()
