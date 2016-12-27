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
    
    attrNameString = rs.GetDocumentUserText("SavedAttrs")
    if attrNameString:
        attrNames = attrNameString.split(";")
        if attrName in attrNames:
            return
        else:
            Rhino.UI.Dialogs.ShowMessageBox("There was an error saving the named properties.", "NamedProperties error", System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Information)
            return
if __name__ == "__main__":
    GetObjectProperties()