from System.Collections.Generic import List



#e.g. if a function complains it needs 'IEnumerable(GeometryBase)':
    geometry = List[Rhino.Geometry.GeometryBase]()
    for pt in pulled_points:
        geometry.Add(Rhino.Geometry.Point(pt))
 
    x = Rhino.Geometry.Brep.CreatePatch( geometry, sSrf, .001)