#pts is a list of Rhino.Geometry.Point3d()

def round_points(pts, intRnd):
    result  = []
    for pt in pts:
        x = round(pt.X,intRnd)
        y  = round(pt.Y, intRnd)
        z = round(pt.Z, intRnd)
        result.append(Rhino.Geometry.Point3d(x, y, z))
    return result