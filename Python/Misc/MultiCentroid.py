import rhinoscriptsyntax as rs


def MultiCentroid():
    
    ids = rs.GetObjects("Select objects", 8+16+4096,True, True)
    if not ids: return
    obj_list = []
    block_obj_list = []
    
    rs.EnableRedraw(False)
    
    for id in ids:
        if rs.IsBlockInstance(id):
            object_ids = rs.ExplodeBlockInstance(rs.CopyObject(id))
            for obj_id in object_ids:
                block_obj_list.append(obj_id)
            
            
        else:
            obj_list.append(id)
            
    if len(obj_list) >0: rs.SelectObjects(obj_list)
    if len(block_obj_list) >0: rs.SelectObjects(block_obj_list)
    rs.Command("_-VolumeCentroid ")
    rs.UnselectAllObjects()
    if rs.LastCommandResult() ==0:
        rs.SelectObject(rs.LastCreatedObjects()[0])

    if len(block_obj_list)>0: rs.DeleteObjects(block_obj_list)
    rs.EnableRedraw(True)
 
        
        
MultiCentroid()