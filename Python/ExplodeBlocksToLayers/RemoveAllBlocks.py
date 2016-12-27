import rhinoscriptsyntax as rs

def RemoveAllBlocks():

    rs.UnselectAllObjects()
    x = rs.BlockNames()
    if not x: return
    y = rs.ObjectsByType(4096)
    if y:
        def explode_em(blocks):
            for Id in blocks:
                if rs.IsBlockInstance(Id):
                    blocks = rs.ExplodeBlockInstance(Id)
                    if blocks: explode_em(blocks)
        for z in y:
            explode_em([z])

    rs.UnselectAllObjects()
    for block in x:
        rs.DeleteBlock(block)

RemoveAllBlocks()
