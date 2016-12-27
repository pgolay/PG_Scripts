def AveragePoint3d(aPts):
    P = len(aPts)
    X = Y = Z = 0
    L = len(aPts)
    for i in range(len(aPts)):
        X = X + aPts[i].X
        Y = Y + aPts[i].Y
        Z = Z + aPts[i].Z
        
    return Rhino.Geometry.Point3d(X/L, Y/L, Z/L)