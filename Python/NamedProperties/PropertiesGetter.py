import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino
import System


def AttrToString(attr, attrName):
    
    a = ""

    a = a + str(attr.ColorSource)
    a = a + ";" + str(attr.LayerIndex)
    a = a + ";" + str(attr.MaterialSource)
    a = a + ";" + str(attr.Name)
    a = a + ";" + str(int(attr.ObjectColor.A)) +"," + str(int(attr.ObjectColor.R))+"," + str( int(attr.ObjectColor.G))+"," + str( int(attr.ObjectColor.B))
    a = a + ";" + str(int(attr.PlotColor.A)) + "," + str(int(attr.PlotColor.R)) + "," + str(int(attr.PlotColor.G)) + "," + str(int(attr.PlotColor.B))
    a = a + ";" + str(attr.Mode)
    a = a + ";" + str(attr.ObjectDecoration)
    a = a + ";" + str(attr.WireDensity)
    a = a + ";" + str(attr.PlotColorSource)
    a = a + ";" + str(attr.PlotWeight)
    a = a + ";" + str(attr.PlotWeightSource)
    a = a + ";" + str(attr.MaterialIndex)
    #rs.SetDocumentData("NamedProperties", attrName, attr)
    rs.SetDocumentUserText(attrName, a)
    temp = rs.GetDocumentUserText("SavedAttrs")
    temp = temp + ";" + attrName
    rs.SetDocumentUserText("SavedAttrs", temp)
    #Rhino.UI.Dialogs.ShowTextDialog(a, "Test")
    pass
    
def StringToAttr(str):
    a = str.split(";")
    attr = Rhino.DocObjects.ObjectAttributes()
    
    colorSources = ["ColorFromLayer", "ColorFromMaterial", "ColorFromObject",  "ColorFromParent"]
    rhColorSources = [Rhino.DocObjects.ObjectColorSource.ColorFromLayer, Rhino.DocObjects.ObjectColorSource.ColorFromMaterial, Rhino.DocObjects.ObjectColorSource.ColorFromObject, Rhino.DocObjects.ObjectColorSource.ColorFromParent]
    attr.ColorSource = rhColorSources[colorSources.index(a[0])]
    
    attr.LayerIndex = int(a[1])
    
    matSources = ["MaterialFromLayer", "MaterialFromObject", "MaterialFromParent"]
    rhMatSources = [Rhino.DocObjects.ObjectMaterialSource.MaterialFromLayer, Rhino.DocObjects.ObjectMaterialSource.MaterialFromObject, Rhino.DocObjects.ObjectMaterialSource.MaterialFromParent]
    attr.MaterialSource = rhMatSources[matSources.index(a[2])]
    
    attr.Name =  a[3]
    
    rgbaList = a[4].split(",")
    color = System.Drawing.Color.FromArgb(int(rgbaList[0]),int(rgbaList[1]), int(rgbaList[2]),int(rgbaList[3]))

    attr.ObjectColor =   color
    pltColorList = a[5].split(",")
    color = System.Drawing.Color.FromArgb(int(pltColorList[0]),int(pltColorList[1]), int(pltColorList[2]),int(pltColorList[3]))
    attr.PlotColor = color
    
    modes = ["Normal","Hidden", "Locked"]
    rhModes = [Rhino.DocObjects.ObjectMode.Normal,Rhino.DocObjects.ObjectMode.Hidden, Rhino.DocObjects.ObjectMode.Locked]
    attr.Mode = rhModes[modes.index(a[6])]
    
    decos = ["None", "StartArrowhead", "EndArrowhead","BothArrowhead"]
    rhDecos = [Rhino.DocObjects.ObjectDecoration.None,Rhino.DocObjects.ObjectDecoration.StartArrowhead, Rhino.DocObjects.ObjectDecoration.EndArrowhead, Rhino.DocObjects.ObjectDecoration.BothArrowhead]
    attr.ObjectDecoration = rhDecos[decos.index(a[7])]
    
    attr.WireDensity = int(a[8])
    
    
    
    plotColorSources = ["PlotColorFromLayer", "PlotColorFromObject", "PlotColorFromDisplay", "PlotColorFromParent"]
    rhPlotColorSources = [Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromLayer, Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject, Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromDisplay, Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromParent]
    attr.PlotColorSource = rhPlotColorSources[plotColorSources.index(a[9])]
    
    
    attr.PlotWeight = float(a[10])
    
    plotWeightSources = ["PlotWeightFromLayer", "PlotWeightFromObject", "PlotWeightFromParent"]
    rhPlotWeightSources = [Rhino.DocObjects.ObjectPlotWeightSource.PlotWeightFromLayer, Rhino.DocObjects.ObjectPlotWeightSource.PlotWeightFromObject, Rhino.DocObjects.ObjectPlotWeightSource.PlotWeightFromParent]
    attr.PlotWeightSource = rhPlotWeightSources[plotWeightSources.index( a[11])]
    attr.MaterialIndex = int(a[12])
    return attr

def GetProperties():
    
    """
    I. Get and save properties
    Get object
    record properties, and prompt for a name for the properties
    save as doc user text
    
    II. Retrieve and apply properties
    Get objects
    Pop up list of properties to apply(from doc data) Use dictionary?
    Allow selection? 
    
    """
    
    go = Rhino.Input.Custom.GetObject()
    go.EnablePreSelect(True, False)
    result = go.Get()
    
    if go.CommandResult()!= Rhino.Commands.Result.Success:
        return
    if result == Rhino.Input.GetResult.Object:
        objRef = go.Objects()[0]
    if objRef is None: return
    
    obj = objRef.Object()
    attr = obj.Attributes
    
    attrNameString = rs.GetDocumentUserText("SavedAttrs")
    if attrNameString: # not None:
        attrNames = attrNameString.split(";")
    while True:
        attrName = rs.GetString("Set saved properties name")
        if attrName is None: return
        
        if attrName in attrNames:
            rc = Rhino.UI.Dialogs.ShowMessageBox("The name " + attrName + " is in use. Would you like to overwrite the named properties with new object properties?", "NamedProperties error", System.Windows.Forms.MessageBoxButtons.YesNoCancel, System.Windows.Forms.MessageBoxIcon.Question, System.Windows.Forms.MessageBoxDefaultButton.Button2)
            if rc == System.Windows.Forms.DialogResult.No:
                continue
            elif rc == System.Windows.Forms.DialogResult.Cancel:
                return
        break
        
    AttrToString(attr, attrName)
    
    pass
    
    
    
def SetProperties():
    go = Rhino.Input.Custom.GetObject()
    go.EnablePreSelect(True, False)
    result = go.GetMultiple(1,0)
    
    if go.CommandResult()!= Rhino.Commands.Result.Success:
        return
    if result == Rhino.Input.GetResult.Object:
        objRefs = [go.Objects()[n] for n in range (go.Objects().Count)]
        
    if objRefs is None: return
    
    attrNameString = rs.GetDocumentUserText("SavedAttrs")
    if attrNameString: # not None:
        attrNames = attrNameString.split(";")
    else:
        Rhino.UI.Dialogs.ShowMessageBox("No named properties were found.", "NamedProperties error", System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Information)
        return
        
    attrName = Rhino.UI.Dialogs.ShowListBox("Named Properties", "Select named properties", attrNames)
    
    for objRef in objRefs:
        obj = objRef.Object()
        obj.Attributes = StringToAttr(rs.GetDocumentUserText(attrName))
        
        #attrDict["testAttr"]
        obj.CommitChanges()

    
if __name__ == "__main__":
    SetProperties()
