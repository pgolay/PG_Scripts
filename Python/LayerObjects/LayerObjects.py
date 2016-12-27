import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino


def LayerObjects():
    
    sLayer = rs.GetLayer("Layer Objects")
    if not sLayer: return
    idx = sc.doc.Layers.Find(sLayer, True)
    Ids = rs.ObjectsByLayer(sLayer)
    
    if Ids is None: return
    total = len(Ids)
    report = str(total) + " objects found on layer " + sLayer + "." + "\n"+ "\n"
    dict = {}
    
    for Id in Ids:
        hidden = 1
        obj = sc.doc.Objects.Find(Id)
        if obj.Visible: hidden = 0
        temp = obj.ObjectType
        
        if temp == Rhino.DocObjects.ObjectType.Brep:
            
            if sc.doc.Objects.Find(Id).Geometry.IsSurface:
                temp = "Surface"
            else:
                temp = "Polysurface"
        if temp == Rhino.DocObjects.ObjectType.InstanceReference: temp = "Block instance"
        temp = str(temp)
        
        #temp = rs.ObjectType(Id)
        if dict.has_key(temp):
            tempVal = dict[temp] + ";" + str(Id)+ str(hidden) 
            dict[temp] = tempVal
        else:
            dict[temp] = str(Id) + str(hidden) 
            
            
    result = dict.items()
    
    for item in result:
        typeList = item[1].split(";")
        count = len(typeList)
        hideCount = 0
        for sId in typeList:
            if sId[-1:] == "1": hideCount = hideCount + 1
        oType = str(item[0])
        if count > 1:
             oType = oType + "s"
        
        reportLine = str(count)+ " " + oType 
        if hideCount > 0: reportLine = reportLine + "  (" + str(hideCount) + " hidden)"
        reportLine = reportLine +  "\n"
        report = report + reportLine
    print report
    
    Rhino.UI.Dialogs.ShowTextDialog(report, "Layer Objects")
    
if __name__ == "__main__":
    LayerObjects()