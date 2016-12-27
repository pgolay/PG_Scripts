import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import math
from System.Collections.Generic import List

def DeformSurface():
    """
    Get a surface. 
    Get curves and points and meshes and PointClouds (maybe a surface as well, use the wireframe)
    Send it all to Patch with the initial surface as a starting surface.
    
    ALSO: set density?- densify the starting surface by adding knots at mid spans
         If that works, show a preview 
         
    """
    tol = sc.doc.ModelAbsoluteTolerance
    srfId = rs.GetObject("Select a surface to deform.",8, True, True)
    if not srfId: return
    
    srf = sc.doc.Objects.Find(srfId).Geometry.Faces[0].ToNurbsSurface()
    
    input = rs.GetObjects("Select points and curves to deform", 1+2+4 + 32, preselect = False, select=True)
    if input is None: return
    
    geo = List[Rhino.Geometry.GeometryBase]()
    for Id in input:
        temp = sc.doc.Objects.Find(Id).Geometry
        if isinstance(temp, Rhino.Geometry.Mesh):
            pts = temp.Vertices
            for pt in pts:
                geo.Add(Rhino.Geometry.Point(pt))
        else:
            geo.Add(sc.doc.Objects.Find(Id).Geometry)
            
    patch = Rhino.Geometry.Brep.CreatePatch( geometry = geo, startingSurface = srf, uSpans=0, vSpans=0, trim = False, tangency=False, pointSpacing = .01, flexibility = 1, surfacePull = 0, fixEdges=(False, False, False, False), tolerance = tol)
    if patch is None: return
    sc.doc.Objects.AddSurface(patch.Faces[0])
    
    
if __name__=="__main__":
    DeformSurface()