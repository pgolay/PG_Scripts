def ExtendAllSides(srf,distances,style):
    
    East= Rhino.Geometry.IsoStatus.East
    West= Rhino.Geometry.IsoStatus.West
    North= Rhino.Geometry.IsoStatus.North
    South= Rhino.Geometry.IsoStatus.South
    
    X = srf.Extend(East, distances[0], style)
    Y = X.Extend(West, distances[1], style)
    X = Y.Extend(North, distances[2], style)
    Y = X.Extend(South, distances[3], style)
    return Y