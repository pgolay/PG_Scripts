import rhinoscriptsyntax as rs
import Rhino
import scriptcontext

def pascaltest():
    int = 5
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Curve")
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
    option = Rhino.Input.Custom.OptionInteger(int)
    go.AcceptNumber(True, True)
    i, option = go.AddOptionInteger("Points", option)
    items = []
    
    while(True):
        rc = go.Get()
        if rc==Rhino.Input.GetResult.Option:
            x = 2
            continue
        if rc == Rhino.Input.GetResult.Number:
            int = go.Number()
            continue
        if rc==Rhino.Input.GetResult.Object:
            id = go.Object(0).ObjectId
            val = option.CurrentValue
            items.append((id,val))
            scriptcontext.doc.Objects.UnselectAll()
            scriptcontext.doc.Views.Redraw()
            continue
        break
    return items

input = pascaltest()
for curve, value in input:
    print "curve", curve, "value", value