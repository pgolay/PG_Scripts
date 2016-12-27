import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc


def MarkCVWeights():
    
    Id = rs.GetObject("Select a curve or surface.",4 + 8, preselect=True)
    if Id is None: retrurn
    
    uText = rs.GetUserText(Id)
    if len(uText) != 0:
        dotIdList = rs.GetUserText (Id,"WeightMarkers")
        if dotIdList is not None:
            dotList = dotIdList.split(",")
            for dotId in dotList:
                if rs.IsObject(dotId):
                    rs.DeleteObject(dotId)
                    
                    
    geo = sc.doc.Objects.Find(Id).Geometry
    layer = rs.ObjectLayer(Id)
    dots =[]
    if rs.IsSurface(Id):
        geo = geo.Faces[0].ToNurbsSurface()
        
        
    rs.EnableRedraw(False)
    
    strMessage = " weighted control points found."
    count = 0
    strNum = "No "
    grp = rs.AddGroup()
    for pt in geo.Points:
        wt = pt.Weight
        if wt != 1.0:
            count = count +1
            dot = rs.AddTextDot(str(wt), pt.Location)
            rs.ObjectLayer(dot, layer)
            dots.append(str(dot))
            
    if len(dots)>0:
        rs.AddObjectsToGroup(dots,grp)
        rs.SetUserText(Id,"WeightMarkers", ','.join(dots))
    if count > 0: strNum = str(count)
    print strNum + strMessage
    
    rs.EnableRedraw(True)
    
if __name__ == "__main__":
    MarkCVWeights()