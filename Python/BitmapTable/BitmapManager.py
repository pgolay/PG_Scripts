import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import os
import System.Windows.Forms as wf



def test():
 
    def GetSomeObjects():
        
        gobs = Rhino.Input.Custom.GetObject()
        gobs.SetCommandPrompt ("Select objects with bitnap textures")
        gobs.GeometryFilter = Rhino.DocObjects.ObjectType.Brep;Rhino.DocObjects.ObjectType.Mesh;Rhino.DocObjects.ObjectType.Extrusion
        gobs.GetMultiple(1,0)
        if gobs.CommandResult() != Rhino.Commands.Result.Success: return
        return[gobs.Object(i).Object() for i in range(gobs.ObjectCount)]
    go = Rhino.Input.Custom.GetOption()
    #opAll = Rhino.Input.Custom.OptionToggle(
    blnAll = False
    go.AddOption("Add")
    go.AddOption("Remove")
    go.AddOption("RemoveAll")
    
    go.SetCommandPrompt("Manage bitmap table")
    
    rc = go.Get()
    
    if go.CommandResult() != Rhino.Commands.Result.Success: return
    
    if rc == Rhino.Input.GetResult.Option:
        opIdx = go.OptionIndex()

     
    if opIdx == 1: 
        objs = GetSomeObjects()
        if objs is None: return
        mats = sc.doc.Materials
        files = []
        for obj in objs:
            idx = obj.Attributes.MaterialIndex
            temp = mats[idx].GetBitmapTexture().FileName
    
            if temp is not None:
                files.append(temp)
            if len(files) != 0:
                for file in files:
                    sc.doc.Bitmaps.AddBitmap(file, True)
        return
        
    blnAll = False
    if opIdx == 3: blnAll = True
    testPath = os.getenv("LOCALAPPDATA")
    lenLocal = len(testPath)
    bTable = sc.doc.Bitmaps

    if bTable.Count == 0:
        print "No images found in the bitmap table."
        return
    print bTable.Count
    
    def IsImage(name):
        sLen  = len(name)
        idx = name.find(".")
        
        typeList = [".jpg", "jpeg",".png", ".bmp", ".tga", ".pcx"]
        text = name[-(sLen-idx):] 
        if text.lower() in typeList: return True
        return False
    
    #fileList = [item.FileName for item in x if item.FileName[:lenLocal] != testPath]
    
    def GetBitmapTableImages(bTable):
        files = []
        for item in bTable:
            name = item.FileName
            #if name[:lenLocal] != testPath:
            if name is not None:
             if IsImage(name):
                files.append(name)
        return files
    
    fileList = GetBitmapTableImages(bTable)
    
    if len(fileList) == 0:
        print "No images found in the bitmap table"
        return
        
    buttons = wf.MessageBoxButtons.OKCancel
    defButton = wf.MessageBoxDefaultButton.Button1
    ike = wf.MessageBoxIcon.Question
    
    if Rhino.RhinoApp.ExeVersion > 5:
        rc = Rhino.UI.Dialogs.ShowMessageBox("In order to do this cleanly, Rhino needs to save and reopen the file. OK to save?","Bitmap Manager", buttons, icon=ike)
    else:
        rc = Rhino.UI.Dialogs.ShowMessageBox("In order to do this cleanly, Rhino needs to save and reopen the file. OK to save?","Bitmap Manager", buttons, icon=ike, defaultButton = defButton)
    if rc == wf.DialogResult.Cancel: return
    
    rs.Command("_Save", False)
    
    if len(fileList) == 0:return
    if blnAll:
        newStates = [True for item in fileList]
    else:
        states = [False for item in fileList]
        newStates = Rhino.UI.Dialogs.ShowCheckListBox("Bitmap Manager", "Choose images to remove from Bitmap Table", fileList, states)
    
    if newStates is None:return
    
    for i in range(len(fileList)):
        if newStates[i]:
            rc = bTable.DeleteBitmap(fileList[i])
            #print rc
            
    rs.Command("_Save", False)
    rs.Command ("_Revert") 
    
    bTable = sc.doc.Bitmaps
    fileList = GetBitmapTableImages(bTable)
    print "Current bitmap table image count = " + str(len(fileList))    
    pass
    
test()