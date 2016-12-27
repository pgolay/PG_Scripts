import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino


def convert_curve_to_nurbs():
    crvs = rs.GetObjects("Select curves", 4 , preselect=True)
    if not crvs:return

    for crv in crvs:
        y = sc.doc.Objects.Find(crv).Geometry.ToNurbsCurve()
        if y:
         sc.doc.Objects.Replace(crv,y)
         
         
convert_curve_to_nurbs()