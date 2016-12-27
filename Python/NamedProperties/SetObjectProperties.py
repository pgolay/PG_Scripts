import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino
import System

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


def SetObjectProperties():
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
    attr = StringToAttr(rs.GetDocumentUserText(attrName))
    if attr is None: return
    
    for objRef in objRefs:
        obj = objRef.Object()
        obj.Attributes = attr
        obj.CommitChanges()
    
if __name__ == "__main__":
    SetObjectProperties()