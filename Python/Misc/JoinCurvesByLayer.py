import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino



def JoinCurvesByLayer():
    
    layers = rs.GetLayers()
    if layers is None : return
    
    for layer in layers:
        Ids = rs.ObjectsByLayer(layer)
        if len(Ids) >0:
            crvs = [Id for Id in Ids if rs.IsCurve(Id)]
            if crvs is not None: joined = rs.JoinCurves(crvs, True)   
            if joined  is not None: rs.ObjectLayer(joined, layer)
            for crv in joined:rs.FlashObject(crv)


    
if __name__ == "__main__":
    JoinCurvesByLayer()