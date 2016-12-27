import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

def increment_name(name, names):
    for num in range(999):
        test = name+("{:0>3d}".format(num))
        if not test in names: return test

def BatchBlock():
    allObj = rs.NormalObjects()
 
    if not allObj: return
    names = list(set([rs.ObjectName(Id) for Id in allObj]))
    name  = "BatchBlock_"
    if sc.sticky.has_key("BatchBlockName"):
        name = sc.sticky["BatchBlockName"]
    
    boundaries = rs.GetObjects("Select enclosing curves",4+512, preselect=True)
    
    #rs.ObjectsByLayer("1")
    if not boundaries: return
    
    contents = [Id for Id in allObj if not Id in boundaries]
    bList = []
    OUT = Rhino.Geometry.PointContainment.Outside
    
    name = rs.GetString("Set base name.",name)
    if not name:return
    sc.sticky["BatchBlockName"] = name
    
    for bId in boundaries:
        bObj = []
        pts = None
        bGeo = sc.doc.Objects.Find(bId).Geometry.ToNurbsCurve()
        for cId in contents:
            temp = sc.doc.Objects.Find (cId).Geometry
            if rs.IsCurve(cId):
                f = temp.ToNurbsCurve()
                pts = temp.ToNurbsCurve().GrevillePoints()
            elif rs.IsText(cId):
                pts = [temp.Plane[0]]
                
            inside=True
            if pts:
                for pt in pts:
                    if bGeo.Contains(pt) == OUT:
                        inside = False
                        break
                if inside:
                    bObj.append(cId)
                
        if len(bObj) >0:
           bObj.append(bId)
           bList.append(bObj)
           
    if len(bList) > 0:
        for bObjList in bList:
            iPt = rs.CurveStartPoint(bObjList[len(bObjList)-1])
            x = rs.AddBlock( bObjList, iPt, delete_input=True)
            newObj = rs.InsertBlock(x, iPt)
            if newObj:
                if name not in names:
                    newName = increment_name(name,names)
                    rs.ObjectName(newObj, newName)
                    names.append(newName)

if __name__ == '__main__':    
    BatchBlock()