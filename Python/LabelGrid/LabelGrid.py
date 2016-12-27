import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import operator

def round_points(pts, intRnd):
    result  = []
    for pt in pts:
        x = round(pt.X,intRnd)
        y  = round(pt.Y, intRnd)
        z = round(pt.Z, intRnd)
        result.append(Rhino.Geometry.Point3d(x, y, z))
    return result

def test():

    def get_objects():
        
        if sc.sticky.has_key("oldCount"):
            oldCount = sc.sticky["oldCount"]
        else:
            oldCount = 1
            
        if sc.sticky.has_key("oldPlaces"):
            oldPlaces = sc.sticky["oldPlaces"]
        else:
            oldPlaces = 4

        filter = Rhino.DocObjects.ObjectType.Annotation
        
        go = Rhino.Input.Custom.GetObject()
        go.GroupSelect = True
        count = Rhino.Input.Custom.OptionInteger(oldCount)
        digits = Rhino.Input.Custom.OptionInteger(oldPlaces)
        
        go.AddOptionInteger("StartingCount", count)
        go.AddOptionInteger("NumberOfDigits", digits)
        go.EnablePreSelect(True, True)
        go.SetCommandPrompt("Select labels to order")
        
        start_count = oldCount
        places = oldPlaces
        
        while True:
            rc = go.GetMultiple(1,0)
            if go.CommandResult()!=Rhino.Commands.Result.Success:
                return go.CommandResult(), None, oldCount, oldPlaces
                
            if rc==Rhino.Input.GetResult.Object:
                ids = [go.Object(i).ObjectId for i in range(go.ObjectCount)]
                sc.doc.Views.Redraw()
                break
            elif rc==Rhino.Input.GetResult.Option:
                places = digits.CurrentValue
                start_count = count.CurrentValue
                sc.sticky["oldPlaces"] = places
                sc.sticky["oldCount"] = start_count
                
        return [rc,ids,start_count, places]
        
    rc,aObj, count, places = get_objects()
    if rc == Rhino.Commands.Result.Cancel: return
        
    if not aObj: return
    aBB = rs.BoundingBox(aObj, rs.ViewCPlane())
    CPlane = rs.ViewCPlane()
    plane  = Rhino.Geometry.Plane(aBB[3], CPlane[1], -1*CPlane[2])
    loc = []
    Ids = []
    for Id in aObj:
        temp = sc.doc.ActiveDoc.Objects.Find(Id)
        X = temp.Geometry
#        loc.append(X.GetBoundingBox(True).Center)
        loc.append(rs.TextObjectPoint(Id))
        Ids.append(Id)
    if len(loc) < 1 : return

    sInt = len(str(len(aObj)))
    xform = rs.XformRotation1(plane,rs.WorldXYPlane())
    xform_inverse = rs.XformInverse(xform)
    trans_loc = []
    
    #round off the points
    locRound = round_points(loc,3)
    #  make a dictionary of the rounded points and corresponding IDs
    dictionary = dict(zip(locRound, Ids))
    
    X = dictionary.get(locRound[0])
    for pt in locRound:
        trans_loc.append(rs.PointTransform(pt,xform))
    xsort = sorted(trans_loc, key = operator.itemgetter(0,1))

    crnt_int = count
    for pt in xsort:
        sInt = (places-len(str(crnt_int)))*"0"+str(crnt_int)
        #sc.doc.ActiveDoc.Objects.AddTextDot(sInt,pt)
        pt = rs.PointTransform(pt,xform_inverse)
        X  = dictionary.get(pt)
        rs.TextObjectText(dictionary.get(pt),sInt)
        crnt_int = crnt_int + 1
    
    sc.doc.ActiveDoc.Views.Redraw()
    
test()