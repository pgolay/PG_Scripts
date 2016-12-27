import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino


def SelectedObjects():
    

    Ids = rs.SelectedObjects()
    
    if len(Ids) == 0:
        print "No objects are selected."
        return
    total = len(Ids)
    report = str(total) + " objects selected." + "\n"+ "\n"
    dict = {}
    
    for Id in Ids:
        temp = sc.doc.Objects.Find(Id).ObjectType
        if temp == Rhino.DocObjects.ObjectType.Brep:
            
            if sc.doc.Objects.Find(Id).Geometry.IsSurface:
                temp = "Surface"
            else:
                temp = "Polysurface"
        if temp == Rhino.DocObjects.ObjectType.InstanceReference: temp = "Block instance"
        
        temp = str(temp)
        #temp = rs.ObjectType(Id)
        if dict.has_key(temp):
            tempVal = dict[temp] + ";" + str(Id)
            dict[temp] = tempVal
        else:
            dict[temp] = str(Id)
            
            
    result = dict.items()
    for item in result:
        x = len(item[1].split(";"))
        oType = str(item[0])
        if x > 1:
             oType = oType + "s"
        
        report = report + str(x)+ " " + oType+ "\n"
    print report
    
    Rhino.UI.Dialogs.ShowTextDialog(report, "Layer Objects")

    
if __name__ == "__main__":
    SelectedObjects()