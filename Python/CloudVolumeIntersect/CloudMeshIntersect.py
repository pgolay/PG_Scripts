import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc


def CloudMeshIntersect():
    
    pcId= rs.GetObject("Select a pointcloud", 2, preselect=True)
    if pcId is None:return
    volId = rs.GetObject("Select a closed volume", 8+16+32)
    if volId is None:return
    
    
    
    vol = sc.doc.Objects.Find(volId).Geometry
    pc  = sc.doc.Objects.Find(pcId).Geometry
    
    if isinstance(vol,Rhino.Geometry.Extrusion): vol = vol.ToBrep(True)

    lIn  = [pt for pt in pc.GetPoints() if vol.IsPointInside(pt, .001, True)]
    
    if lIn >0: nc = Rhino.Geometry.PointCloud(lIn)
    if nc is not None:
         newPc = sc.doc.Objects.AddPointCloud(nc)
         rs.UnselectAllObjects()
         rs.SelectObject(newPc)
    
if __name__ =="__main__":
    CloudMeshIntersect()