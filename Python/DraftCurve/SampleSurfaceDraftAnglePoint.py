import Rhino
import rhinoscriptsyntax as rs
from System.Collections.Generic import *

def SampleSurfaceDraftAnglePoint(surface_id, point_2d, angle):
    rs_obj = rs.GetPlugInObject("RhinoScript")
    if rs_obj:
        surface_str = surface_id.ToString()
        point = List[float]()
        point.Add(point_2d[0])
        point.Add(point_2d[1])
        draft = rs_obj.SurfaceDraftAnglePoint(surface_str, point.ToArray(), angle)
        return draft
    return null

pick = rs.GetObjectEx("Select surface", 8)
if pick:
    surface_id = pick[0]
    point_3d = pick[3]
    point_2d = rs.SurfaceClosestPoint(surface_id, point_3d)
    draft = SampleSurfaceDraftAnglePoint(surface_id, point_2d, 2.0)
    if draft:
        print draft

