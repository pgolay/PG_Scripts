import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc


def increment_name(name):

    for num in range(999):
        test = name+("{:0>3d}".format(num))
        if not rs.IsLayer(test): return test
         
    
def ExplodeToLayers(Id, perObject):

    name = rs.BlockInstanceName(Id)# the definition name of the instance
    
    blockObjs = rs.BlockObjects(name)# the IDs of the objects in a block def
    for BId in blockObjs: #make sure they are valid
        if not rs.IsObjectValid(BId):
            print BId
            print "Invalid object encountered. Skipping this block."
            
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
    Ids = [n for n in rs.ExplodeBlockInstance(Id)]
    rs.ObjectColorSource(Ids, 0)
    
    
    objCount = 0
    objNames = []
    multiples = []
    
    if Ids:
        for Id in Ids:
            if rs.IsBlockInstance(Id):
                blockList.append(Id)
                
            else:
                rs.ObjectColorSource(Id,1)
                objCount = objCount + 1
                x = rs.ObjectName(Id)
                if x:
                     objNames.append(x)
                else:
                    rs.ObjectName(Id, "Object")
                    objNames.append("Object")
                
        for name in objNames:
           if objNames.count(name) > 1:
               multiples.append(name)
        if not perObject:
            rs.ObjectLayer(Ids, parentLayer)
        else:
            if not rs.IsBlockInstance(Id):
                
                objName = rs.ObjectName(Id)
                if objName: 
                    if objName in multiples:
                        objName  = increment_name(objName)                
                    
                objLayer = rs.AddLayer(objName, parent=addLayer)
                rs.ObjectLayer(Id,objLayer)
            else:
                rs.ObjectLayer(Ids, addLayer)
                rs.LayerColor(addLayer, rs.ObjectColor(Ids[0]))
            
    sc.sticky["MyBlockList"]= blockList
        
    
def ExplodeBlocksToLayers():
   
    def get_inputs():
        while True:
            blnLayers = False
            
            if sc.sticky.has_key("BLN_LAYERS"):
                blnLayers  = sc.sticky["BLN_LAYERS"]
                
            go = Rhino.Input.Custom.GetObject()
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

    blockList, perObject = result
    if not blockList: return
    
    Ids = [Id for Id in blockList]
    
    sc.sticky["MyProcessedBlocks"] = []
    sc.sticky["MyBlockList"] = blockList
    
    
    def explode_em(n):
        
        while True:

            blockList = sc.sticky["MyBlockList"]
            if len(blockList) == 0: return
            Id = blockList.pop(0)
            
            x = ExplodeToLayers(Id, perObject)
           
            
    rs.EnableRedraw=False
    
    explode_em(0)
    
    rs.EnableRedraw=True

    if sc.sticky.has_key("MyProcessedBlocks"):
        purgeList = sc.sticky["MyProcessedBlocks"]
        
    for name in purgeList:
        if rs.IsBlock(name):
            if not rs.IsBlockInUse(name):
                rs.DeleteBlock(name)
    
    
if( __name__ == "__main__" ):
    ExplodeBlocksToLayers()