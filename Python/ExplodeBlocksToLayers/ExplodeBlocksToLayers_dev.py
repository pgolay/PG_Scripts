import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import System


def increment_name(name):

    for num in range(999):
        test = name+("{:0>3d}".format(num))
        if not rs.IsLayer(test): return test
         
def ExplodeToLayers(Id, perObject, top):
    count = 1
    if sc.sticky.has_key("BLOCKCOUNT"):
        count = sc.sticky["BLOCKCOUNT"]+1
    sc.sticky["BLOCKCOUNT"] = count
        
    name = rs.BlockInstanceName(Id)# the definition name of the instance
    num = rs.BlockObjectCount(name)
    if num == 1:
        strNum = "Working on block " + str(count) +"... it has one object."
    else:
        strNum = "Working on block " + str(count) +"... it has " + str(num) + " objects."
    rs.Prompt(strNum)
    
    blockObjs = rs.BlockObjects(name)# the IDs of the objects in a block def
    
    for i in range(len(blockObjs)): #make sure they are valid
        if not rs.IsObjectValid(blockObjs[i]):
            
            print "Invalid object encountered. Skipping this block: " + name  
            Rhino.UI.Dialogs.ShowTextDialog("Invalid object encountered. Skipping this block: " + name, "ExplodeBlockToLayers" )
            return
    
    parentLayer = rs.ObjectLayer(Id)
    layerColor = rs.LayerColor(parentLayer)
    objColor = rs.ObjectColor(Id)

    newName = name
    
    if rs.IsLayer(name):
        newName = increment_name(name)#make a unique layer name
        
    if perObject: 
        addLayer = rs.AddLayer(newName, parent=parentLayer)
        rs.ObjectLayer(Id, addLayer)
        
    if sc.sticky.has_key("MyProcessedBlocks"):# keep track of the block def names
        ProcessedBlocks = sc.sticky["MyProcessedBlocks"]
        ProcessedBlocks.append(name)
        sc.sticky["MyProcessedBlocks"] = ProcessedBlocks
    else:
        ProcessedBlocks = [name]
        sc.sticky["MyProcessedBlocks"] = ProcessedBlocks
        
    if sc.sticky.has_key("MyBlockList"):#?
        blockList = sc.sticky["MyBlockList"]
        
    # explode the instance and get the
    #Ids of the resulting objects
    #set the objects to color by layer
    Ids = []
    temp = rs.ExplodeBlockInstance(Id)
    if temp is None:
        #print "None, Id = " + str(Id)
        return
    if len(temp) == 0:
        #print "Zero, Id = " + str(Id)
        return
    NullId = System.Guid.TryParse("00000000-0000-0000-0000-000000000000")[1]

    for item in temp:
        if not item.Equals(NullId):
            Ids.append(item)
    
    if len(Ids) >0:
        rs.ObjectColorSource(Ids, 0)
        for i in range(len(Ids)):
            
            if rs.IsBlockInstance(Ids[i]):
                blockList.append(Ids[i])
            else:
                rs.ObjectColorSource(Ids[i],1)
                
        if not perObject:
            rs.ObjectLayer(Ids, parentLayer)
        else:
            rs.ObjectLayer(Ids, addLayer)
            rs.LayerColor(addLayer, rs.ObjectColor(Ids[i]))
            
    sc.sticky["MyBlockList"]= blockList
        
    
def ExplodeBlocksToLayers():
   
   
    def get_inputs():
        while True:
            blnLayers = False
            
            if sc.sticky.has_key("BLN_LAYERS"):
                blnLayers  = sc.sticky["BLN_LAYERS"]
                
            go = Rhino.Input.Custom.GetObject()
            go.SetCommandPrompt("Select block instances to explode.")
            go.GeometryFilter = Rhino.DocObjects.ObjectType.InstanceReference
            
            boolOptionLayers = Rhino.Input.Custom.OptionToggle(blnLayers, "KeepInsertionLayer", "NewLayerPerBlock")
            optLayers = go.AddOptionToggle("Layers", boolOptionLayers)
            
            rc = go.GetMultiple(1,0)
            
            if go.CommandResult()!=Rhino.Commands.Result.Success:
                return go.CommandResult()
                
            if rc==Rhino.Input.GetResult.Option:
                blnLayers = boolOptionLayers.CurrentValue
                sc.sticky["BLN_LAYERS"] = blnLayers
                continue
            if rc==Rhino.Input.GetResult.Object:
                blnLayers = boolOptionLayers.CurrentValue
                sc.sticky["BLN_LAYERS"] = blnLayers
                Ids = [go.Objects()[i].ObjectId for i in range(len(go.Objects()))]
                
                break
                
        return Ids, blnLayers
    
    result = get_inputs()
    if result == Rhino.Commands.Result.Cancel: return

    Ids, perObject = result

    
    sc.sticky["MyProcessedBlocks"] = []
    sc.sticky["MyBlockList"] = Ids
    pass
    rs.Prompt("Working...")
    
    def explode_em():
        
        while True:
            top = False
            blockList = sc.sticky["MyBlockList"]

            if len(blockList) == 0: return
            Id = blockList.pop(0)
            #print "BL Length = " + str(len(blockList))
            if Id in Ids: top = True
    #            if not isinstance(Id, Rhino.DocObjects.RhinoObject):
    #                print "Got it " + str(Id)
    #                #rs.UnselectAllObjects()
    #                #rs.Sleep(2000)
    #                rs.Command("SelID " + str(Id))
                #print "IsObject = " + str(rs.IsObject(Id))
                #continue
            
            else:
                pass
            if len(blockList) == 1: 
                pass
            ExplodeToLayers(Id, perObject, top)
           
            
    rs.EnableRedraw=False
    
    explode_em()
    
    rs.EnableRedraw=True

    if sc.sticky.has_key("MyProcessedBlocks"):
        purgeList = sc.sticky["MyProcessedBlocks"]
        
    for name in purgeList:
        if rs.IsBlock(name):
            if not rs.IsBlockInUse(name):
                rs.DeleteBlock(name)
    sc.sticky["BLOCKCOUNT"] = 1
    
if __name__ == "__main__":
    ExplodeBlocksToLayers()