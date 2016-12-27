import rhinoscriptsyntax as rs
import Rhino


def test():
    filter = Rhino.DocObjects.ObjectType.Surface
    while True:

        rc, objref = Rhino.Input.RhinoGet.GetOneObject("Select face", False, filter)
        if not objref:
            rs.Prompt()  
            break
        face = objref.Geometry()
        DomU = face.Domain(0)
        DomV = face.Domain(1)
        mid = [(DomU[0] + ((DomU[1] - DomU[0])/2)), ((DomV[0] + DomV[1] - DomV[0])/2)]
        apt = face.Evaluate(mid[0], mid[1], 0)[1]
        N = face.NormalAt(mid[0], mid[1])
        targ = apt+N
        x = str(apt)
        rs.Command ("_Move W" + str(apt) +" " + "Along " + "W" + str(apt) + " W" + str(targ) + " ")
    
test()