



def ArcFilter(rhino_object, geometry, component_index ):
    ret, arc = geometry.TryGetArc()
    if ret:
         return True
    else: 
        return False
        
"""
Example- 
    ga = Rhino.Input.Custom.GetObject()
    ga.SetCustomGeometryFilter(ArcFilter)

"""
