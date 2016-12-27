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
    temp = list(set(temp.Split(";")))
    temp =   list(filter(None, temp))
    temp  = ";".join(temp)
    
    
    rs.SetDocumentUserText("SavedAttrs", temp)

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

def GetObjectProperties():
    
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
    go.SetCommandPrompt("Select object with properties to save.")
    go.EnablePreSelect(True, False)
    result = go.Get()
    
    if go.CommandResult()!= Rhino.Commands.Result.Success:
        return
    if result == Rhino.Input.GetResult.Object:
        objRef = go.Objects()[0]
    if objRef is None: return
    
    obj = objRef.Object()
    attr = obj.Attributes
    
    objName = attr.Name
    
    attrNameString = rs.GetDocumentUserText("SavedAttrs")
    if attrNameString: # not None:
        attrNames = attrNameString.split(";")
    else:
        attrNames = [""]
    while True:
        attrName = rs.GetString("Set saved properties name", defaultString = objName)
        if not attrName:
            print "No name was entered. Properties saving canceled." 
            return
        
        if attrName in attrNames:
            print "IN!"
            rc = Rhino.UI.Dialogs.ShowMessageBox("The name " + attrName + " is in use. Would you like to overwrite the named properties with new object properties?", "NamedProperties error", System.Windows.Forms.MessageBoxButtons.YesNoCancel, System.Windows.Forms.MessageBoxIcon.Question, System.Windows.Forms.MessageBoxDefaultButton.Button2)
            if rc == System.Windows.Forms.DialogResult.No:
                continue
            elif rc == System.Windows.Forms.DialogResult.Cancel:
                return
                
        break
        
    AttrToString(attr, attrName)
    
    attrNameString = rs.GetDocumentUserText("SavedAttrs")
    if attrNameString:
        attrNames = attrNameString.split(";")
        if attrName in attrNames:
            return
        else:
            Rhino.UI.Dialogs.ShowMessageBox("There was an error saving the named properties.", "NamedProperties error", System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Information)
            return
    
def SetObjectProperties():
    go = Rhino.Input.Custom.GetObject()
    go.EnablePreSelect(True, False)
    go.SetCommandPrompt("Select objects")
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
    attrNames =   list(filter(None, attrNames))
    attrName = Rhino.UI.Dialogs.ShowListBox("Named Properties", "Select named properties", attrNames)
    if not attrName: return
    attr = StringToAttr(rs.GetDocumentUserText(attrName))
    if attr is None: return
    
    for objRef in objRefs:
        obj = objRef.Object()
        obj.Attributes = attr
        obj.CommitChanges()
        
def EditNamedProperties():
    while True:
        attrNameString = rs.GetDocumentUserText("SavedAttrs")
        attrNames = attrNameString.split(";")
            
        gOpt = Rhino.Input.Custom.GetOption()
        gOpt.SetCommandPrompt("Choose NamedProperties editing option")
        gOpt.AddOption("Delete")
        gOpt.AddOption("Rename")
        
        rc = gOpt.Get()
        
        if gOpt.CommandResult()!= Rhino.Commands.Result.Success:
            return
        if rc == Rhino.Input.GetResult.Option:
            idx = gOpt.OptionIndex()
            if  idx ==1:
                delNames = Rhino.UI.Dialogs.ShowMultiListBox("Named Properties", "Named proprties to delete.", attrNames)
                if delNames is None: return
                temp = rs.GetDocumentUserText("SavedAttrs").split(";")
                for name in delNames:
                    temp.remove(name)
                    rs.SetDocumentUserText(name, "")
                    tempString = ";".join(temp)
                    rs.SetDocumentUserText("SavedAttrs", tempString)
            elif idx ==2:
                
                attrName = Rhino.UI.Dialogs.ShowListBox("Named Properties", "Select named properties", attrNames)
                if attrName:
                        while True:
                            newName = rs.GetString("Set new saved properties name")
                            if newName is None: return
                            
                            if newName in attrNames:
                                rc = Rhino.UI.Dialogs.ShowMessageBox("The name " + newName + " is in use. Would you like to overwrite the named properties with new object properties?", "NamedProperties error", System.Windows.Forms.MessageBoxButtons.YesNoCancel, System.Windows.Forms.MessageBoxIcon.Question, System.Windows.Forms.MessageBoxDefaultButton.Button2)
                                if rc == System.Windows.Forms.DialogResult.No:
                                    continue
                                elif rc == System.Windows.Forms.DialogResult.Cancel:
                                    return
                            attr = rs.GetDocumentUserText(attrName)
                            rs.SetDocumentUserText(newName,attr)
                            rs.SetDocumentUserText(attrName, "")
                            
                            temp = rs.GetDocumentUserText("SavedAttrs").split(";")
                            temp.remove(attrName)
                            temp.append (newName)
                            tempString = ";".join(temp)
                            rs.SetDocumentUserText("SavedAttrs", tempString)
                            print tempString
                            break
        if not rs.GetDocumentUserText("SavedAttrs"):
            print "There are no more named properties to edit."
            return
    
def NamedProperties():
    saved  = rs.GetDocumentUserText("SavedAttrs")

    go = Rhino.Input.Custom.GetOption()
    go.SetCommandPrompt("Named properties")
    
    if not saved:
        print "No properties have been saved in this file."
        GetObjectProperties()
    else: 
        go.AddOption("ApplyToObjects")
        go.AddOption("Save")
        go.AddOption("Edit")
        rc = go.Get()
        if go.CommandResult()!= Rhino.Commands.Result.Success:
            return
        if rc == Rhino.Input.GetResult.Option:
            
            idx = go.OptionIndex()
            if saved:
                if  idx ==1:
                    SetObjectProperties()
                elif idx ==2:
                    GetObjectProperties()
                else:
                    EditNamedProperties()

            
if __name__ == "__main__":
    NamedProperties()
